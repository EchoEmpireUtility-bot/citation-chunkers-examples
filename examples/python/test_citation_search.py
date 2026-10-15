"""Offline tests for the downstream citation-search recipe."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from citation_search import ACTOR_ID, SearchError, build_index, digest, search


def fixture_delivery(text="Govern risks with documented evidence."):
    sha = hashlib.sha256(text.encode()).hexdigest()
    document_sha = "a" * 64
    row = {
        "text": text, "sha256": sha, "characterCount": len(text),
        "documentSha256": document_sha, "documentId": "sha256:" + document_sha,
        "sourceUrl": "https://example.org/public.pdf", "pageStart": 7, "pageEnd": 7,
        "pageChunkIndex": 1, "chunking": {"chunkSize": 3000, "overlap": 300},
        "documentTitle": "Public example",
    }
    row["chunkId"] = "sha256:" + digest({
        "version": "pdf-citation-chunker:chunk:v1", "documentSha256": document_sha,
        "pageNumber": 7, "pageChunkIndex": 1, "chunkSha256": sha,
        "chunkSize": 3000, "overlap": 300,
    })
    rows = [row]
    return {"chunks": rows, "receipt": {"actorId": ACTOR_ID, "status": "DELIVERED",
                                      "deliveredChunks": 1, "chunksSha256": digest(rows)}}


class CitationSearchTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.delivery = self.root / "delivery.json"
        self.db = self.root / "index.sqlite3"

    def write_delivery(self, payload):
        self.delivery.write_text(json.dumps(payload), encoding="utf-8")

    def test_verified_delivery_indexes_and_queries_with_provenance(self):
        self.write_delivery(fixture_delivery())
        self.assertEqual(build_index(self.delivery, self.db),
                         (1, "LOCAL_RECEIPT_AND_CHUNK_INTEGRITY"))
        matches = search(self.db, "govern evidence")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["pageStart"], 7)
        self.assertEqual(matches[0]["sourceUrl"], "https://example.org/public.pdf")
        self.assertEqual(search(self.db, "unrelated"), [])

    def test_replay_does_not_overwrite_existing_index(self):
        self.write_delivery(fixture_delivery())
        build_index(self.delivery, self.db)
        before = self.db.read_bytes()
        with self.assertRaisesRegex(SearchError, "already exists"):
            build_index(self.delivery, self.db)
        self.assertEqual(self.db.read_bytes(), before)

    def test_tampered_text_and_receipt_cannot_create_index(self):
        payload = fixture_delivery()
        payload["chunks"][0]["text"] = "altered"
        self.write_delivery(payload)
        with self.assertRaises(SearchError):
            build_index(self.delivery, self.db)
        self.assertFalse(self.db.exists())
        payload = fixture_delivery()
        payload["receipt"]["status"] = "PARTIAL"
        self.write_delivery(payload)
        with self.assertRaises(SearchError):
            build_index(self.delivery, self.db)

    def test_query_is_bounded_and_not_raw_fts_syntax(self):
        self.write_delivery(fixture_delivery())
        build_index(self.delivery, self.db)
        self.assertEqual(search(self.db, 'govern" OR unrelated'), [])
        with self.assertRaises(SearchError):
            search(self.db, "govern", limit=1000)

    def test_duplicate_chunk_ids_rejected(self):
        payload = fixture_delivery()
        payload["chunks"].append(dict(payload["chunks"][0]))
        payload["receipt"]["deliveredChunks"] = 2
        payload["receipt"]["chunksSha256"] = digest(payload["chunks"])
        self.write_delivery(payload)
        with self.assertRaisesRegex(SearchError, "duplicate"):
            build_index(self.delivery, self.db)

    def test_plain_dataset_is_supported_without_provenance_claim(self):
        self.write_delivery(fixture_delivery()["chunks"])
        self.assertEqual(build_index(self.delivery, self.db), (1, "CHUNK_INTEGRITY_ONLY"))
        self.assertEqual(len(search(self.db, "documented evidence")), 1)


if __name__ == "__main__":
    unittest.main()
