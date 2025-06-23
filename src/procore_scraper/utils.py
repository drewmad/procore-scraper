
"""
procore_scraper.utils – misc helpers
"""
from __future__ import annotations
import hashlib, re, json, datetime, sys
from typing import Any

_SLUG_RE = re.compile(r"[^a-z0-9]+")

def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", "ignore")).hexdigest()

def canonicalize(url: str) -> str:
    url = url.strip().replace("http://", "https://").rstrip("/").lower()
    return url

def slugify(url: str, max_len: int = 240) -> str:
    body = canonicalize(url).split("://",1)[-1]
    slug = _SLUG_RE.sub("-", body).strip("-")
    return slug[:max_len]

def log_json(event: str, **data: Any) -> None:
    payload = {"ts": datetime.datetime.utcnow().isoformat(timespec="seconds")+"Z",
               "event": event, **data}
    sys.stdout.write(json.dumps(payload)+"\n")
    sys.stdout.flush()
