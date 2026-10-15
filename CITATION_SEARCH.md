# Public PDF → page-linked search, without an AI key

This example turns output from the existing [PDF Citation Chunker](https://apify.com/skilled_glee/pdf-citation-chunker) into a searchable local SQLite index. It does not create a new Actor, bill separately, call a model, or upload your documents to another service. It demonstrates keyword retrieval with page provenance—not semantic ranking or a complete hosted RAG system.

1. Inspect the [NIST AI RMF public task and quickstart](NIST_QUICKSTART.md). Viewing them is free. Running the Actor may be billable; check current pricing and use an enforced charge cap in your Apify client. A timeout is not a cancellation—inspect the run before any retry.
2. Save a successful Actor default-dataset response as a JSON array named `dataset.json`. The quickstart's `run-sync-get-dataset-items` endpoint returns this form on success. Keep your token in the request header or private client configuration, not in the saved file, URL, or index.
3. Run Python 3.10+ with SQLite FTS5 from this repository root:

```sh
python3 examples/python/citation_search.py index dataset.json --db nist.sqlite3
python3 examples/python/citation_search.py query --db nist.sqlite3 --terms "risk management" --limit 1
```

The result includes a short excerpt, original PDF URL, page number, stable document ID and chunk ID. The script checks content hashes and the chunk-ID contract, rejects duplicate/invalid records, caps input at 20 MiB and 10,000 chunks, and never overwrites an existing index. It supports a raw dataset array (`CHUNK_INTEGRITY_ONLY`) or the bounded workflow's saved `DELIVERED` artifact (`LOCAL_RECEIPT_AND_CHUNK_INTEGRITY`). These labels do not verify buyer identity or payment.

An October 4, 2026 **owner-account technical run** of the public NIST AI RMF PDF produced 55 validated chunks. A local replay indexed all 55 and returned a page-27 match for “risk management.” This is a format and downstream-use proof, not an independent customer result. The [public automation release](https://github.com/EchoEmpireUtility-bot/citation-chunkers-examples/releases/tag/pdf-automation-v0.1) preserves the saved proof and checksums without requiring a new run to inspect it.

Limits: embedded-text PDFs only; scanned PDFs require the separate OCR Actor. Search is lexical, so synonyms may not match. The local SQLite file contains document text and has no encryption or multiuser authorization. Use only public PDFs or documents you are authorized to process, and store private indexes accordingly. Useful output is not evidence of creator earnings, repeat demand, or profit.
