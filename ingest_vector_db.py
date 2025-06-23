#!/usr/bin/env python3
"""
ingest_vector_db.py
===================
Stream the embeddings produced by `chunk_and_embed.py` into either:

• **FAISS**  – fast, in-RAM flat index (default)  
• **Qdrant** – HNSW vector DB with filtering & persistence

The script is idempotent: you can run it after every embed pass; it appends
new vectors and keeps existing ones.

---------------------------------------------------------------------------
CLI examples
---------------------------------------------------------------------------

# local FAISS (faiss.index + faiss.index.meta.pkl)
python ingest_vector_db.py --db faiss

# Qdrant running on localhost:6333
python ingest_vector_db.py --db qdrant --collection procore

# custom HNSW parameters
python ingest_vector_db.py --db qdrant --hnsw_m 32 --hnsw_ef_construct 512
"""

from __future__ import annotations
import argparse
import json
import pickle
import pathlib
import yaml
import numpy as np
from typing import List, Tuple

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
CFG = pathlib.Path("config/settings.yaml")
cfg = yaml.safe_load(CFG.read_text()) if CFG.exists() else {}

DATA_DIR = pathlib.Path("data/embeddings")
VECS_BIN = DATA_DIR / "vecs.fp16"     # memmap float16 matrix
META_JL  = DATA_DIR / "chunks.jsonl"  # one JSON per chunk


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def load_embeddings() -> Tuple[np.ndarray, List[dict]]:
    """Return (vecs[n,d] as float32, meta list)."""
    vecs = np.memmap(VECS_BIN, dtype="float16", mode="r")
    meta = [json.loads(l) for l in META_JL.read_text().splitlines()]
    dim  = vecs.size // len(meta)
    return np.asarray(vecs, dtype="float32").reshape(len(meta), dim), meta


# --------------------------------------------------------------------------- #
# FAISS ingest
# --------------------------------------------------------------------------- #
def ingest_faiss(vecs: np.ndarray, meta: List[dict], index_path: str = "faiss.index"):
    try:
        import faiss                         # standard
    except ModuleNotFoundError:
        import importlib
        faiss = importlib.import_module("faiss_cpu")  # fallback for 1.11 wheels
    import os

    if pathlib.Path(index_path).exists():
        idx = faiss.read_index(index_path)
        idx.add(vecs)
        old_meta = pickle.loads(open(f"{index_path}.meta.pkl", "rb").read())
        meta = old_meta + meta
    else:
        idx = faiss.IndexFlatIP(vecs.shape[1])
        idx.add(vecs)

    faiss.write_index(idx, index_path)
    pickle.dump(meta, open(f"{index_path}.meta.pkl", "wb"))
    print(f"[FAISS] {idx.ntotal:,} vectors stored in {index_path}")


# --------------------------------------------------------------------------- #
# Qdrant ingest
# --------------------------------------------------------------------------- #
def ingest_qdrant(
    vecs: np.ndarray,
    meta: List[dict],
    host: str,
    port: int,
    collection: str,
    m: int,
    ef_construct: int,
    ef_search: int,
):
    from qdrant_client import QdrantClient

    client = QdrantClient(host=host, port=port)

    client.recreate_collection(
        collection,
        vectors_config=dict(size=vecs.shape[1], distance="Cosine"),
        hnsw_config=dict(m=m, ef_construct=ef_construct, ef_search=ef_search),
    )

    ids = [f"{m['doc_sha1']}_{m['chunk_id']}" for m in meta]
    client.upload_collection(
        collection_name=collection,
        vectors=vecs,
        payload=meta,
        ids=ids,
        batch_size=256,
    )
    print(f"[Qdrant] Upserted {len(meta):,} vectors to {host}:{port}/{collection}")


# --------------------------------------------------------------------------- #
# CLI / main
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", choices=["faiss", "qdrant"], default=cfg.get("vector_db", "faiss"))
    ap.add_argument("--index_path", default="faiss.index")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=6333)
    ap.add_argument("--collection", default="procore")
    ap.add_argument("--hnsw_m", type=int, default=cfg.get("hnsw_m", 16))
    ap.add_argument("--hnsw_ef_construct", type=int, default=cfg.get("hnsw_ef_construct", 256))
    ap.add_argument("--hnsw_ef_search", type=int, default=cfg.get("hnsw_ef_search", 64))
    args = ap.parse_args()

    vecs, meta = load_embeddings()

    if args.db == "faiss":
        ingest_faiss(vecs, meta, index_path=args.index_path)
    else:
        ingest_qdrant(
            vecs,
            meta,
            host=args.host,
            port=args.port,
            collection=args.collection,
            m=args.hnsw_m,
            ef_construct=args.hnsw_ef_construct,
            ef_search=args.hnsw_ef_search,
        )


if __name__ == "__main__":
    main()