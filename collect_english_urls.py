
#!/usr/bin/env python3
from __future__ import annotations
import argparse, pathlib, concurrent.futures, requests
from langdetect import detect, LangDetectException
HEADERS={"User-Agent":"Mozilla/5.0"}
def is_en(url:str)->bool:
    try:
        text = requests.get(url, headers=HEADERS, timeout=15).text[:4000]
        return detect(text)=="en"
    except (requests.RequestException,LangDetectException):
        return False
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("infile", type=pathlib.Path)
    ap.add_argument("-o","--out", default="url_list_english.txt")
    ap.add_argument("-j","--jobs",type=int, default=8)
    args=ap.parse_args()
    urls=[u.strip() for u in args.infile.read_text().splitlines() if u.strip()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        english=[u for u,ok in zip(urls, ex.map(is_en, urls)) if ok]
    pathlib.Path(args.out).write_text("\n".join(sorted(english)))
    print(f"Kept {len(english)}/{len(urls)} English URLs")
if __name__=="__main__":
    main()
