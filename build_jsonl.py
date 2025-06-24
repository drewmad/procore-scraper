# build_jsonl.py
import json, pathlib, hashlib, tiktoken, sys

enc = tiktoken.encoding_for_model("gpt-4o-mini")
MD_DIR = pathlib.Path("data/clean_md")
OUT    = pathlib.Path("openai_payload.json")

# Build list of documents
documents = []
for md in MD_DIR.glob("*.md"):
    text = md.read_text()
    documents.append({
        "text": text,
        "metadata": {
            "sha1": hashlib.sha1(text.encode()).hexdigest(),
            "filename": md.name,
            "tokens": len(enc.encode(text))
        }
    })

# Write as JSON file
with OUT.open("w", encoding="utf-8") as fh:
    json.dump(documents, fh, indent=2, ensure_ascii=False)

print("✓ wrote", OUT, f"({OUT.stat().st_size/1e6:.1f} MB)")
print(f"✓ processed {len(documents)} documents") 