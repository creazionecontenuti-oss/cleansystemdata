#!/usr/bin/env python3
"""Pipeline Gumroad landing: preview | publish | clear.

Legge gumroad/landing.html (costruito da build_landing.py) e:
  preview  → DRY-RUN: report di dimensioni/elementi, NESSUNA pubblicazione
  publish  → backup della description attuale (una tantum) + PUT della landing
             + round-trip di verifica
  clear    → ripristina la description originale dal backup

Ambiente: GUMROAD_ACCESS_TOKEN (segreto GitHub), PIPELINE_ACTION.
Output: report su stdout (il workflow lo pubblica in un issue).
"""
import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request

PRODUCT_ID = "yhcldt"
API = "https://api.gumroad.com/v2"
TOKEN = os.environ.get("GUMROAD_ACCESS_TOKEN", "")
ACTION = os.environ.get("PIPELINE_ACTION", "preview")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANDING = os.path.join(ROOT, "gumroad", "landing.html")
BACKUP = os.path.join(ROOT, "gumroad", "original-description.txt")


def call(path, params=None, method="GET"):
    params = dict(params or {})
    params["access_token"] = TOKEN
    if method == "GET":
        url = API + path + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, method="GET")
        body = None
    else:
        url = API + path
        body = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=body, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


lines = []


def report(s):
    lines.append(s)


def main():
    html = open(LANDING, encoding="utf-8").read()
    report(f"landing.html: {len(html)} char, buy elements: {html.count('data-gumroad-action=')}")
    report(f"sha256: {hashlib.sha256(html.encode()).hexdigest()[:12]}")

    if ACTION == "preview":
        report("DRY-RUN: niente è stato pubblicato, il prodotto non è stato toccato.")
        report("Inizio landing: " + html[:220].replace("\n", " "))

    elif ACTION == "publish":
        if not os.path.exists(BACKUP):
            cur = call(f"/products/{PRODUCT_ID}")["product"]["description"]
            with open(BACKUP, "w", encoding="utf-8") as f:
                f.write(cur)
            report(f"backup description attuale salvato ({len(cur)} char) in gumroad/original-description.txt")
        else:
            report("backup description già presente (non sovrascritto).")
        res = call(f"/products/{PRODUCT_ID}", {"description": html}, method="PUT")
        ok = res.get("success")
        report(f"PUT description: success={ok}")
        cur = call(f"/products/{PRODUCT_ID}")["product"]["description"]
        report(f"round-trip: description ora {len(cur)} char (attese ~{len(html)})")
        report("PUBLISHED ✅" if ok else "PUBLISH FALLITO ❌")

    elif ACTION == "clear":
        if not os.path.exists(BACKUP):
            sys.exit("backup mancante: niente da ripristinare")
        backup = open(BACKUP, encoding="utf-8").read()
        res = call(f"/products/{PRODUCT_ID}", {"description": backup}, method="PUT")
        report(f"ripristinata la description originale: success={res.get('success')}")

    else:
        sys.exit(f"azione sconosciuta: {ACTION}")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
