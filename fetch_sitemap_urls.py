
#!/usr/bin/env python3
from __future__ import annotations
import argparse, pathlib, requests, xml.etree.ElementTree as ET

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def parse(url: str, seen: set[str]) -> set[str]:
    if url in seen: return set()
    seen.add(url)
    root = ET.fromstring(fetch(url))
    ns = {"sm":"http://www.sitemaps.org/schemas/sitemap/0.9"}
    out = set()
    for loc in root.findall("sm:sitemap/sm:loc",ns):
        out |= parse(loc.text.strip(), seen)
    for loc in root.findall("sm:url/sm:loc",ns):
        out.add(loc.text.strip())
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domains", nargs="+", required=True)
    ap.add_argument("--out", default="url_list_site.txt")
    args = ap.parse_args()
    urls = set()
    for dom in args.domains:
        try:
            urls |= parse(f"https://{dom}/sitemap.xml", set())
        except Exception as e:
            print(f"[WARN] {dom}: {e}")
    pathlib.Path(args.out).write_text("\n".join(sorted(urls)))
    print(f"Wrote {len(urls):,} URLs → {args.out}")
if __name__ == "__main__":
    main()
