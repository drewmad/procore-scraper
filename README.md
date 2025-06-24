# 🏗️ Procore Scraper → RAG Pipeline

End-to-end toolkit that turns [Procore] docs & site pages into a production-ready
vector index for Retrieval-Augmented Generation (RAG).

URL list → scrape → clean-md → chunk → embed → FAISS/Qdrant

---

## ✅ Current Status

**OpenAI Assistant Successfully Created and Working!**
- Assistant ID: `asst_ueLOB0oOsC8ZQkymnJ3nBkSj`
- File ID: `file-T8SNWWqVN4As6Nrvx2VXm2`
- 6,081 documents processed (21.1 MB)
- Ready for Q&A about Procore documentation

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

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp config/secrets.env.example config/secrets.env
# Edit config/secrets.env with your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### Option 1: Local FAISS Index

```bash
# 1. Scrape and process content
python scrape_procore.py

# 2. Generate embeddings
python chunk_and_embed.py

# 3. Create FAISS index
python ingest_vector_db.py --db faiss
```

### Option 2: OpenAI Vector Store (Recommended) ✅

```bash
# 1. Scrape and process content (same as above)
python scrape_procore.py
python chunk_and_embed.py

# 2. Build JSON payload for OpenAI
python build_jsonl.py

# 3. Create OpenAI Assistant (already done!)
python create_assistant.py

# 4. Query the Assistant
python test_query.py
# or for interactive mode:
python interactive_query.py
```

## Usage Examples

### Test the Assistant
```bash
# Ask about Procore API authentication
python test_query.py
```

### Interactive Q&A
```bash
# Start interactive session
python interactive_query.py

# Example questions:
# - "How do I authenticate with the Procore API?"
# - "What are the main features of Procore?"
# - "How do I refresh an OAuth token?"
# - "What is the project management workflow?"
```

## File Structure

```
├── data/
│   ├── clean_md/          # Processed markdown files
│   ├── embeddings/        # Vector embeddings
│   └── raw_html/          # Raw scraped HTML
├── config/
│   ├── settings.yaml      # Configuration
│   └── secrets.env        # API keys (not in git)
├── scripts/
│   ├── scrape_procore.py  # Main scraping script
│   ├── chunk_and_embed.py # Embedding generation
│   ├── ingest_vector_db.py # FAISS/Qdrant ingestion
│   ├── build_jsonl.py     # OpenAI payload builder
│   ├── create_store.py    # OpenAI vector store
│   ├── create_assistant.py # OpenAI Assistant
│   ├── query_assistant.py # Query interface
│   ├── test_query.py      # Test script
│   └── interactive_query.py # Interactive Q&A
└── requirements.txt       # Python dependencies
```

## OpenAI Vector Store Workflow

The OpenAI approach is recommended for production use:

1. **Build JSON**: Convert markdown files to JSON format with metadata
2. **Upload**: Upload to OpenAI with `purpose="assistants"`
3. **Create Assistant**: Attach file to Assistant with `code_interpreter` tool
4. **Query**: Single API call handles embedding, search, and response generation

### Advantages

- ✅ No large files to manage (GitHub rejected 400MB FAISS files)
- ✅ Automatic embedding and indexing
- ✅ Built-in citations and metadata
- ✅ Scalable and managed by OpenAI
- ✅ Simple API for queries
- ✅ Working Assistant ready for use

## Configuration

Edit `config/settings.yaml` to customize:
- Scraping URLs and patterns
- Chunking parameters
- Vector store settings
- Model configurations

## Troubleshooting

### OpenAI API Issues
- Ensure your API key is set: `export OPENAI_API_KEY="your-key"`
- Check API credits and rate limits
- Verify file upload was successful

### Assistant Issues
- Use the correct Assistant ID: `asst_ueLOB0oOsC8ZQkymnJ3nBkSj`
- Ensure the file is properly attached
- Check for deprecation warnings (normal, API still works)

## License

MIT License

© 2025 Drew / madengineering
Everything you need—ignore files, complete README, and you're CI-ready.