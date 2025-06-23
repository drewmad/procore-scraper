
#!/usr/bin/env python3
from __future__ import annotations
import subprocess, tempfile, pathlib, urllib.parse

DOCS_GH = "https://github.com/procore/documentation.git"

def main():
    out = pathlib.Path("url_list.txt")
    with tempfile.TemporaryDirectory() as td:
        subprocess.check_call(["git","clone","--depth","1",DOCS_GH,td])
        md_files = list(pathlib.Path(td).rglob("*.md"))
        urls = []
        base = "https://github.com/procore/documentation/blob/main/"
        for p in md_files:
            urls.append(urllib.parse.urljoin(base, str(p.relative_to(td))))
    out.write_text("\n".join(sorted(set(urls))))
    print(f"Wrote {len(urls):,} URLs to {out}")
if __name__ == "__main__":
    main()
