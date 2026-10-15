"""Index an existing validated PDF delivery for local, citation-aware search.

This is a downstream example, not an Actor or a network client. It cannot
submit runs, charge users, or establish that a delivery came from a buyer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

ACTOR_ID = "H1c9OyB0AnRf8Sy4y"
MAX_BYTES = 20 * 1024 * 1024
MAX_ITEMS = 10000
HASH = re.compile(r"^[a-f0-9]{64}$")


class SearchError(ValueError):
    pass


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def valid_chunk(row: object) -> bool:
    """Recheck the public PDF chunk contract before indexing untrusted text."""
    if not isinstance(row, dict):
        return False
    text, text_sha = row.get("text"), row.get("sha256")
    doc_sha, chunk_id = row.get("documentSha256"), row.get("chunkId")
    if (not isinstance(text, str) or not text.strip() or not isinstance(text_sha, str)
            or not HASH.fullmatch(text_sha)
            or hashlib.sha256(text.encode()).hexdigest() != text_sha
            or row.get("characterCount") != len(text)
            or not isinstance(doc_sha, str) or not HASH.fullmatch(doc_sha)
            or row.get("documentId") != "sha256:" + doc_sha
            or not isinstance(chunk_id, str) or not chunk_id.startswith("sha256:")
            or not HASH.fullmatch(chunk_id[7:])):
        return False
    start, end = row.get("pageStart"), row.get("pageEnd")
    page_chunk, config = row.get("pageChunkIndex"), row.get("chunking")
    if (type(start) is not int or type(end) is not int or start < 1 or start != end
            or type(page_chunk) is not int or page_chunk < 1 or not isinstance(config, dict)):
        return False
    size, overlap = config.get("chunkSize"), config.get("overlap")
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
        return False
    expected = digest({
        "version": "pdf-citation-chunker:chunk:v1", "documentSha256": doc_sha,
        "pageNumber": start, "pageChunkIndex": page_chunk, "chunkSha256": text_sha,
        "chunkSize": size, "overlap": overlap,
    })
    source = row.get("sourceUrl")
    try:
        parsed = urlsplit(source) if isinstance(source, str) else None
        return bool(chunk_id == "sha256:" + expected and parsed
                    and parsed.scheme in {"http", "https"} and parsed.hostname
                    and parsed.username is None and parsed.password is None)
    except ValueError:
        return False


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SearchError("Delivery contains a duplicate JSON key.")
        result[key] = value
    return result


def _read_chunks(path: Path) -> tuple[list[dict], str]:
    if path.stat().st_size > MAX_BYTES:
        raise SearchError("Delivery exceeds the 20 MiB limit.")
    try:
        delivery = json.loads(path.read_text(encoding="utf-8"),
                              object_pairs_hook=_unique_object)
    except (UnicodeError, ValueError) as exc:
        raise SearchError("Delivery is not valid UTF-8 JSON.") from exc
    if isinstance(delivery, list):
        chunks, scope = delivery, "CHUNK_INTEGRITY_ONLY"
    elif isinstance(delivery, dict) and isinstance(delivery.get("receipt"), dict):
        receipt = delivery["receipt"]
        chunks, scope = delivery.get("chunks"), "LOCAL_RECEIPT_AND_CHUNK_INTEGRITY"
        if (receipt.get("actorId") != ACTOR_ID or receipt.get("status") != "DELIVERED"
                or not isinstance(chunks, list) or receipt.get("deliveredChunks") != len(chunks)
                or receipt.get("chunksSha256") != digest(chunks)):
            raise SearchError("Delivery receipt or chunk digest does not match.")
    else:
        raise SearchError("Expected a PDF dataset array or workflow delivery.")
    if not 0 < len(chunks) <= MAX_ITEMS:
        raise SearchError("Chunk count is out of range.")
    seen: set[str] = set()
    for record in chunks:
        if not valid_chunk(record) or record["chunkId"] in seen:
            raise SearchError("Delivery contains an invalid or duplicate chunk.")
        seen.add(record["chunkId"])
    return chunks, scope


def build_index(delivery_path: Path, db_path: Path) -> tuple[int, str]:
    """Build a new database atomically; never replace an existing index."""
    chunks, scope = _read_chunks(delivery_path)
    if db_path.exists():
        raise SearchError("Index already exists; choose a new path.")
    if not db_path.parent.is_dir():
        raise SearchError("Index parent directory does not exist.")
    descriptor, temporary = tempfile.mkstemp(prefix=".citation-index-", suffix=".sqlite3",
                                             dir=db_path.parent)
    os.close(descriptor)
    try:
        with sqlite3.connect(temporary) as connection:
            connection.execute("""CREATE VIRTUAL TABLE chunks USING fts5(
                text, chunk_id UNINDEXED, document_id UNINDEXED,
                source_url UNINDEXED, page_start UNINDEXED,
                page_end UNINDEXED, document_title UNINDEXED
            )""")
            connection.executemany(
                "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?)",
                [(row["text"], row["chunkId"], row["documentId"], row["sourceUrl"],
                  row["pageStart"], row["pageEnd"], row.get("documentTitle", ""))
                 for row in chunks],
            )
        os.link(temporary, db_path)  # exclusive: cannot overwrite another index
    except FileExistsError as exc:
        raise SearchError("Index already exists; choose a new path.") from exc
    finally:
        Path(temporary).unlink(missing_ok=True)
    return len(chunks), scope


def search(db_path: Path, terms: str, limit: int = 5) -> list[dict]:
    if not 1 <= limit <= 20 or len(terms) > 200:
        raise SearchError("Query or result limit is out of range.")
    tokens = re.findall(r"[A-Za-z0-9]{2,}", terms.lower())
    if not 1 <= len(tokens) <= 8:
        raise SearchError("Use one to eight alphanumeric search terms.")
    expression = " AND ".join('"' + token + '"' for token in tokens)
    if not db_path.is_file():
        raise SearchError("Index does not exist.")
    uri = db_path.resolve().as_uri() + "?mode=ro"
    try:
        with sqlite3.connect(uri, uri=True) as connection:
            rows = connection.execute(
                """SELECT text, chunk_id, document_id, source_url,
                          page_start, page_end, document_title
                   FROM chunks WHERE chunks MATCH ?
                   ORDER BY bm25(chunks), chunk_id LIMIT ?""",
                (expression, limit),
            ).fetchall()
    except sqlite3.DatabaseError as exc:
        raise SearchError("Index is invalid or unavailable.") from exc
    return [{"excerpt": row[0][:240], "chunkId": row[1], "documentId": row[2],
             "sourceUrl": row[3], "pageStart": int(row[4]), "pageEnd": int(row[5]),
             "documentTitle": row[6]} for row in rows]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    index = commands.add_parser("index", help="Build a new local index from a delivery")
    index.add_argument("delivery", type=Path)
    index.add_argument("--db", type=Path, required=True)
    query = commands.add_parser("query", help="Find source-bound chunks")
    query.add_argument("--db", type=Path, required=True)
    query.add_argument("--terms", required=True)
    query.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)
    try:
        if args.command == "index":
            count, scope = build_index(args.delivery, args.db)
            result = {"indexedChunks": count, "verificationScope": scope,
                      "index": str(args.db)}
        else:
            result = {"query": args.terms, "matches": search(args.db, args.terms, args.limit)}
    except (OSError, SearchError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
