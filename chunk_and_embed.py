#!/usr/bin/env python3
"""
Chunk + embed Procore Markdown corpus using DynamicMarkdownSplitter and
OpenAI text-embedding-3-large (configurable via settings.yaml or $EMB_MODEL).

Skips embeddings already on disk (checks doc_sha1 + chunk_id).
"""
from __future__ import annotations
import os, json, argparse, pathlib, numpy as np, openai, yaml
from procore_scraper.utils import log_json, sha1_text
from procore_scraper.splitters import dynamic_markdown_split

# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #
CFG_PATH = pathlib.Path("config/settings.yaml")
if CFG_PATH.exists():
    cfg = yaml.safe_load(CFG_PATH.read_text())
    DEFAULT_MODEL = cfg.get("emb_model", "text-embedding-3-large")
else:
    DEFAULT_MODEL = "text-embedding-3-large"

EMB_MODEL = os.getenv("EMB_MODEL", DEFAULT_MODEL)
DATA      = pathlib.Path("data")
MD_DIR    = DATA / "clean_md"
EMB_DIR   = DATA / "embeddings"
EMB_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- #
def embed_texts(batch: list[str]) -> list[list[float]]:
    resp = openai.embeddings.create(model=EMB_MODEL, input=batch)
    return [d.embedding for d in resp.data]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--batch", type=int, default=96)
    args = ap.parse_args()

    # existing vector cache
    existing = {}
    jsonl_path = EMB_DIR / "chunks.jsonl"
    if jsonl_path.exists():
        for line in jsonl_path.read_text().splitlines():
            j = json.loads(line)
            existing[(j["doc_sha1"], j["chunk_id"])] = True

    metas, texts = [], []
    for md_path in MD_DIR.glob("*.md"):
        raw = md_path.read_text()
        sha1 = md_path.stem
        chunks = dynamic_markdown_split(raw)
        for idx, chunk in enumerate(chunks):
            key = (sha1, idx)
            if key in existing:
                continue
            metas.append({"doc_sha1": sha1, "chunk_id": idx, "text": chunk})
            texts.append(chunk)

    if not texts:
        print("No new chunks to embed.")
        return

    # allocate / extend memmap
    dim = 3072 if EMB_MODEL.endswith("large") else 1536
    mmap_path = EMB_DIR / "vecs.fp16"
    offset = 0
    if mmap_path.exists():
        offset = (mmap_path.stat().st_size // 2) // dim
    fp = np.memmap(
        mmap_path,
        dtype="float16",
        mode="r+" if mmap_path.exists() else "w+",
        shape=(offset + len(texts), dim),
    )

    # embed in batches
    with open(jsonl_path, "a") as jf:
        for i in range(0, len(texts), args.batch):
            batch = texts[i : i + args.batch]
            vecs = embed_texts(batch)
            start = offset + i
            fp[start : start + len(batch)] = np.array(vecs, dtype="float16")
            for meta in metas[i : i + args.batch]:
                jf.write(json.dumps(meta) + "\n")

    log_json("embed_complete", new_chunks=len(texts), model=EMB_MODEL)
    print(f"Embedded {len(texts):,} new chunks → {mmap_path}")


if __name__ == "__main__":
    main()