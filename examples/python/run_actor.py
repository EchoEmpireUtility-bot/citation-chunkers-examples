"""Start an EchoEmpire Actor and print its Apify run metadata."""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen


ACTORS = {
    "pdf": "H1c9OyB0AnRf8Sy4y",
    "ocr": "50meJWqJ27Aw2QYZD",
}


def main() -> None:
    product = sys.argv[1] if len(sys.argv) > 1 else "pdf"
    if product not in ACTORS:
        raise SystemExit("Usage: python run_actor.py [pdf|ocr]")
    token = os.environ["APIFY_TOKEN"]
    root = Path(__file__).resolve().parents[2]
    payload = (root / "inputs" / f"{product}-citation-chunker.json").read_bytes()
    request = Request(
        f"https://api.apify.com/v2/acts/{ACTORS[product]}/runs",
        data=payload,
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urlopen(request) as response:
        print(json.dumps(json.load(response), indent=2))


if __name__ == "__main__":
    main()
