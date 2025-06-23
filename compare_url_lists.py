#!/usr/bin/env python3
"""
Output URLs that are new or missing compared to the previous crawl.
"""
from __future__ import annotations
import argparse, pathlib, difflib

def load(fp: pathlib.Path) -> list[str]:
    return [l.strip() for l in fp.read_text().splitlines() if l.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--out", default="url_list_delta.txt")
    args = ap.parse_args()

    old, new = map(pathlib.Path, (args.old, args.new))
    before, after = load(old), load(new)

    delta = sorted(set(after) ^ set(before))  # symmetric diff
    pathlib.Path(args.out).write_text("\n".join(delta))
    print(f"Wrote {len(delta)} delta URLs → {args.out}")

if __name__ == "__main__":
    main()