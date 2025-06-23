# 🏗️ Procore Scraper → RAG Pipeline

End-to-end toolkit that turns [Procore] docs & site pages into a production-ready
vector index for Retrieval-Augmented Generation (RAG).

URL list → scrape → clean-md → chunk → embed → FAISS/Qdrant

---

## Features
| Stage | Highlights |
|-------|------------|
| **Crawl** | Async `httpx` + Readability extraction, language filter, heuristic prune. |
| **Chunk** | _DynamicMarkdownSplitter_ keeps headers & code blocks intact; 320-token targets. |
| **Embed** | OpenAI `text-embedding-3-large` (or smaller, via `config/settings.yaml`). |
| **Vector DB** | Local **FAISS** flat-IP index _or_ remote **Qdrant** (HNSW). |
| **Eval** | 20-question YAML ground-truth → Ragas metrics (`context_precision`, `answer_relevance`). |
| **CI / CD** | GitHub Action refreshes weekly, pushes new index artefact, Slack alert on failure. |

---

## Quick start

```bash
# 1. clone & enter repo
git clone https://github.com/<you>/procore_scraper.git
cd procore_scraper

# 2. create venv + deps
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .          # editable package

# 3. scrape & build index
python generate_url_list.py
python fetch_sitemap_urls.py --domains developers.procore.com support.procore.com procore.com --out url_list_site.txt
cat url_list.txt url_list_site.txt | sort -u > url_list_full.txt
python prune_urls.py url_list_full.txt
python scrape_procore.py url_list_clean.txt
python chunk_and_embed.py
python ingest_vector_db.py --db faiss

# 4. ask a question
python -m procore_scraper.cli_ask "How do I refresh an OAuth token?"

Requires: OpenAI API key (export OPENAI_API_KEY=sk-…).

Configuration
# config/settings.yaml
vector_db: faiss                  # or qdrant
emb_model: text-embedding-3-large # OpenAI model
chunk_size: 320
chunk_overlap: 40
hnsw_m: 16
hnsw_ef_construct: 256

Change → rerun chunk_and_embed.py (only new chunks embed).

⸻

GitHub Actions

.github/workflows/refresh.yml re-crawls, embeds delta, and uploads the fresh
faiss.index artefact every Monday 06:00 UTC or on manual dispatch.

Add repository secrets:

Name
Value
OPENAI_API_KEY
your key
SLACK_BOT_TOKEN
(optional)

Production use
	•	Local FAISS
Copy faiss.index & faiss.index.meta.pkl; load with faiss.read_index.
	•	Remote Qdrant
docker run -p 6333:6333 qdrant/qdrant then
python ingest_vector_db.py --db qdrant --host localhost.

At inference:
vec = embed(question)                # same OpenAI model
scores, ids = index.search(vec, k=8)
context = "\n\n".join(meta[i]["text"] for i in ids[0])
answer = chat_complete(question, context)
Troubleshooting
Issue
Fix
ModuleNotFoundError: faiss
newer wheel exposes faiss_cpu; import fallback already present.
No module named pip in venv
python -m ensurepip --upgrade && python -m pip install -U pip.
OpenAI quota hit
set OPENAI_MAX_TOKENS env or lower chunk_size.

License

MIT – do whatever you want, no warranty.  Contributions welcome!

© 2025 Drew / madengineering
Everything you need—ignore files, complete README, and you’re CI-ready.