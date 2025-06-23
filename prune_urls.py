
#!/usr/bin/env python3
from __future__ import annotations
import argparse, pathlib, re, urllib.parse

BAD = [
    re.compile(r"/blog/"),
    re.compile(r"\.(jpg|jpeg|png|gif|svg|pdf)$"),
    re.compile(r"login"),
    re.compile(r"signup"),
]

def keep(url: str) -> bool:
    if any(p.search(url) for p in BAD):
        return False
    parsed = urllib.parse.urlparse(url)
    return not parsed.fragment

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("infile", type=pathlib.Path)
    ap.add_argument("-o","--out", default="url_list_clean.txt")
    args = ap.parse_args()
    urls = [u.strip() for u in args.infile.read_text().splitlines() if u.strip()]
    kept = [u for u in urls if keep(u)]
    pathlib.Path(args.out).write_text("\n".join(sorted(set(kept))))
    print(f"Pruned {len(urls)-len(kept)} → wrote {len(kept)}")
if __name__ == "__main__":
    main()
