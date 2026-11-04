#!/usr/bin/env python3
"""Install the shared outline on local reading pages containing <main>.

Run after Site assembly. --dry-run reports planned entrypoints without writing.
Nested reading pages use relative asset URLs; vendor/data exports are excluded.
"""
import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

REV = "20261018-outline-pages"
ASSETS = ("page-outline.js", "page-outline.css")
EXCLUDED = {"vendor", "fonts", "data", "context-study", "study-atlas", "boundary-atlas", "portfolio"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.has_main = False
        self.has_head = False
        self.has_body = False

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.has_main = True
        elif tag == "head":
            self.has_head = True
        elif tag == "body":
            self.has_body = True


def supported(text):
    page = Page()
    page.feed(text)
    return page.has_main and page.has_head and page.has_body and bool(
        re.search(r"</head\s*>", text, re.I) and re.search(r"</body\s*>", text, re.I))


def outline_asset(tag, name):
    """Recognize only this component's local asset, including old query versions."""
    match = re.search(r"\b(?:src|href)\s*=\s*(['\"])(.*?)\1", tag, re.I | re.S)
    if not match:
        return False
    url = urlsplit(match.group(2))
    return not url.scheme and not url.netloc and Path(url.path).name == name


def render_html(text, asset_prefix=""):
    if not supported(text):
        return text
    # Keep unrelated script bodies and inline modules untouched.
    text = re.sub(r"<link\b[^>]*>", lambda m: "" if outline_asset(m.group(), "page-outline.css") else m.group(), text, flags=re.I)
    text = re.sub(r"<script\b[^>]*>\s*</script\s*>",
                  lambda m: "" if outline_asset(m.group(), "page-outline.js") else m.group(),
                  text, flags=re.I | re.S)
    css = f'<link rel="stylesheet" href="{asset_prefix}page-outline.css?v={REV}">'
    js = f'<script type="module" src="{asset_prefix}page-outline.js?v={REV}"></script>'
    text = re.sub(r"</head\s*>", lambda m: css + m.group(), text, count=1, flags=re.I)
    return re.sub(r"</body\s*>", lambda m: js + m.group(), text, count=1, flags=re.I)


def discover_pages(dist):
    for path in sorted(dist.rglob("*.html")):
        relative = path.relative_to(dist)
        if any(part.startswith(".") or part in EXCLUDED for part in relative.parts[:-1]):
            continue
        text = path.read_text()
        if supported(text):
            yield path, text


def apply(task_root, dry_run=False):
    root = Path(task_root)
    dist = root / "site/dist"
    modules = root / "team/08_Scripts/site_modules"
    if not dist.is_dir():
        raise FileNotFoundError(dist)
    for name in ASSETS:
        if not (modules/name).is_file():
            raise FileNotFoundError(modules/name)
    pages, changed = [], []
    for path, text in discover_pages(dist):
        prefix = os.path.relpath(dist,path.parent).replace(os.sep,"/")
        prefix = "" if prefix == "." else prefix + "/"
        updated = render_html(text,prefix)
        pages.append(path.relative_to(dist).as_posix())
        if updated != text:
            changed.append(path.relative_to(dist).as_posix())
            if not dry_run:
                path.write_text(updated)
    if not dry_run:
        for name in ASSETS:
            shutil.copy2(modules/name,dist/name)
    return {"dry_run":dry_run,"pages":pages,"changed_pages":changed,"assets":list(ASSETS)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-root",required=True,type=Path)
    parser.add_argument("--dry-run",action="store_true")
    args = parser.parse_args()
    print(json.dumps(apply(args.task_root,args.dry_run),indent=2))
