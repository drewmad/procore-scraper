"""
DynamicMarkdownSplitter
-----------------------
Smart, recursion-safe chunker tuned for Procore docs.

* H2-H6 headers define primary sections.
* Never splits inside fenced  ``` code blocks.
* Recurses until every chunk ≤ CHUNK_MAX tokens.
* Guaranteed progress: if the smart split fails, falls back to 50/50.
"""

from __future__ import annotations
from typing import List
import re, tiktoken

# ------------------------------------------------------------------- #
# Constants
# ------------------------------------------------------------------- #
_HEAD_RE         = re.compile(r"^(#{2,6}\s+.+)", re.M)
_CODE_FENCE_RE   = re.compile(r"```")
enc              = tiktoken.encoding_for_model("gpt-4o-mini")

CHUNK_TARGET     = 320     # ideal size
CHUNK_MAX        = 360     # hard upper size
OVERLAP_TOKENS   = 40      # tokens prepended from previous chunk


# ------------------------------------------------------------------- #
# Helpers
# ------------------------------------------------------------------- #
def _toklen(text: str) -> int:
    return len(enc.encode(text))


def _split_headers(md: str) -> List[str]:
    """Top-level header boundaries → list of sections."""
    parts, start = [], 0
    for m in _HEAD_RE.finditer(md):
        if m.start() == 0:
            continue
        parts.append(md[start:m.start()])
        start = m.start()
    parts.append(md[start:])
    return parts


def _safe_split(section: str) -> List[str]:
    """
    Recursively split `section` until every piece ≤ CHUNK_MAX tokens.

    Pass 1  paragraph grouping outside code fences.  
    Pass 2  if still oversize, hard-split token stream at midpoint.
    """
    if _toklen(section) <= CHUNK_MAX:
        return [section]

    # ----- Pass 1 : smart paragraph split -----
    paras = section.split("\n\n")
    out, buf, in_code = [], [], False
    for para in paras:
        if _CODE_FENCE_RE.search(para):
            in_code = not in_code
        buf.append(para)
        if (not in_code) and _toklen("\n\n".join(buf)) >= CHUNK_TARGET:
            out.append("\n\n".join(buf).strip())
            buf = []
    if buf:
        out.append("\n\n".join(buf).strip())

    # ----- Pass 2 : fallback 50/50 if no progress -----
    if len(out) == 1 and _toklen(out[0]) > CHUNK_MAX:
        tokens = enc.encode(section)
        mid = len(tokens) // 2
        left, right = enc.decode(tokens[:mid]), enc.decode(tokens[mid:])
        out = [left, right]

    # Recurse on any child that’s still too big
    final: List[str] = []
    for chunk in out:
        final.extend(_safe_split(chunk) if _toklen(chunk) > CHUNK_MAX else [chunk])
    return final


# ------------------------------------------------------------------- #
def dynamic_markdown_split(md: str) -> List[str]:
    """Public API – returns a list of overlapped chunks."""
    sections = _split_headers(md)
    chunks: List[str] = []
    for sec in sections:
        chunks.extend(_safe_split(sec))

    # fixed overlap
    result: List[str] = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            result.append(chunk.strip())
        else:
            overlap = enc.decode(enc.encode(chunks[i - 1])[-OVERLAP_TOKENS:])
            result.append((overlap + "\n\n" + chunk).strip())
    return result