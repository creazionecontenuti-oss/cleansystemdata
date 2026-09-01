#!/usr/bin/env python3
"""Build gumroad/landing.html from the template + repo assets.

Reads gumroad/landing-template.html, converts the site's own PNG assets to
compact WebP data URIs and injects them, writing the final self-contained
gumroad/landing.html that the Gumroad CLI previews/publishes.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Le immagini sono servite dal SITO (https://cleansystemdata.site/assets/...):
# la description Gumroad ha un limite ~50 KB e i data-URI WebP la gonfiano a
# 151 KB → API rifiuta. URL esterni = description leggera e sempre aggiornata.
URLS = {
    "__B64_ICON__": "https://cleansystemdata.site/assets/icon-256.png",
    "__B64_STRATA__": "https://cleansystemdata.site/assets/stratigrafia.png",
    "__B64_DETAIL__": "https://cleansystemdata.site/assets/item-detail.png",
}


def main():
    tpl_path = os.path.join(ROOT, "gumroad", "landing-template.html")
    with open(tpl_path, encoding="utf-8") as f:
        html = f.read()
    for placeholder, url in URLS.items():
        html = html.replace(placeholder, url)
    leftover = [p for p in URLS if p in html]
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
