#!/usr/bin/env python3
"""Build gumroad/landing.html from the template + repo assets.

Reads gumroad/landing-template.html, converts the site's own PNG assets to
compact WebP data URIs and injects them, writing the final self-contained
gumroad/landing.html that the Gumroad CLI previews/publishes.
"""
import base64
import io
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JOBS = [
    ("__B64_ICON__", "assets/icon-256.png", 256, 90),
    ("__B64_STRATA__", "assets/stratigrafia.png", 1400, 82),
    ("__B64_DETAIL__", "assets/item-detail.png", 1200, 82),
]


def webp_b64(path, max_w, quality):
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    tpl_path = os.path.join(ROOT, "gumroad", "landing-template.html")
    with open(tpl_path, encoding="utf-8") as f:
        html = f.read()
    for placeholder, rel, max_w, q in JOBS:
        html = html.replace(placeholder, webp_b64(os.path.join(ROOT, rel), max_w, q))
    leftover = [p for p, _, _, _ in JOBS if p in html]
    if leftover:
        sys.exit(f"Placeholders not replaced: {leftover}")
    out = os.path.join(ROOT, "gumroad", "landing.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(out)
    buys = html.count('data-gumroad-action="buy"')
    print(f"Wrote {out} ({size/1024:.0f} KB), buy elements: {buys}")
    if buys < 1:
        sys.exit("No data-gumroad-action=\"buy\" element found!")


if __name__ == "__main__":
    main()
