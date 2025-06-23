
#!/usr/bin/env python3
from __future__ import annotations
from bs4 import BeautifulSoup
from pathlib import Path
import sys, json, datetime, time, requests
from procore_scraper.utils import slugify, canonicalize, sha1_text, log_json
from readability import Document
import markdownify

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR/"raw_html"
MD_DIR = DATA_DIR/"clean_md"
META_DIR = DATA_DIR/"meta"
for p in (RAW_DIR, MD_DIR, META_DIR): p.mkdir(parents=True, exist_ok=True)

HEADERS={"User-Agent":"Mozilla/5.0"}

def fetch(url:str, retry:int=3):
    for i in range(retry):
        try:
            return requests.get(url, headers=HEADERS, timeout=30)
        except requests.RequestException:
            time.sleep(2**i)
    raise RuntimeError(f"Failed fetch {url}")

def strip_tags(html:str)->str:
    soup=BeautifulSoup(html,"lxml")
    for bad in soup(["script","style","noscript","iframe","canvas","svg","nav","header","footer","form","aside"]):
        bad.decompose()
    return str(soup)

def one_line(md:str,n:int=160)->str:
    return " ".join(md.split())[:n]

def main():
    if len(sys.argv)!=2:
        sys.exit("Usage: python scrape_procore.py url_list_clean.txt")
    urls=[u.strip() for u in Path(sys.argv[1]).read_text().splitlines() if u.strip()]
    from tqdm.auto import tqdm
    for url in tqdm(urls):
        canon=canonicalize(url)
        slug=slugify(canon)
        md_path=MD_DIR/f"{slug}.md"
        if md_path.exists(): continue
        resp=fetch(canon)
        if resp.status_code!=200:
            log_json("fetch_error",url=canon,code=resp.status_code)
            continue
        html=resp.text
        (RAW_DIR/f"{slug}.html").write_text(html,"utf-8",errors="ignore")
        main_html=Document(strip_tags(html)).summary(html_partial=True)
        if len(main_html)<180: main_html=html
        md=markdownify.markdownify(main_html, heading_style="ATX")
        md_path.write_text(md,"utf-8")
        meta=dict(
            url=canon,
            slug=slug,
            sha1=sha1_text(md),
            title=BeautifulSoup(html,"lxml").title.string if BeautifulSoup(html,"lxml").title else "",
            last_scraped=datetime.datetime.utcnow().isoformat()+"Z",
            summary=one_line(md)
        )
        (META_DIR/f"{slug}.json").write_text(json.dumps(meta,indent=2))
if __name__=="__main__":
    main()
