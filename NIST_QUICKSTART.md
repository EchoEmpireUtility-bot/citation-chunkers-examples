# NIST AI RMF PDF → citation-ready JSON

Give the [PDF Citation Chunker](https://apify.com/skilled_glee/pdf-citation-chunker) a public embedded-text PDF. It returns page-aware JSON text chunks with stable document and chunk IDs, hashes, and source provenance for RAG or search ingestion. Scanned or image-only PDFs need the [OCR Citation Chunker](https://apify.com/skilled_glee/ocr-citation-chunker) instead.

1. [View the existing public NIST example task](https://apify.com/skilled_glee/pdf-citation-chunker/examples/pdf-citation-chunker-task). Its input and output fields are visible without a paid run. This task was already public before this guide; it is not a newly launched product.
2. The [PDF automation v0.1 public release](https://github.com/EchoEmpireUtility-bot/citation-chunkers-examples/releases/tag/pdf-automation-v0.1) contains a bounded Python workflow, `proof-input.json`, and a checksum manifest. An October 4, 2026 owner-account run with that exact NIST input delivered 55 validated chunks. This is technical proof, not independent customer use, payment, or profit.
3. To invoke the Actor yourself, check its [current pricing](https://apify.com/skilled_glee/pdf-citation-chunker/pricing), use your own Apify account, and set a charge cap you can afford. The command below **starts a billable run**; viewing the task or this page does not.

```sh
export APIFY_TOKEN="your_apify_token"
curl --fail-with-body -X POST \
  "https://api.apify.com/v2/actors/H1c9OyB0AnRf8Sy4y/run-sync-get-dataset-items?clean=true&maxTotalChargeUsd=0.05" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"url":"https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf","mode":"chunk","chunkSize":3000,"overlap":300}'
```

Keep the token private. A synchronous HTTP timeout does not prove the Actor stopped; inspect the run before retrying. For asynchronous collection and output-integrity checks, use the public release rather than resubmitting an ambiguous job.

Use only successful, nonempty records. Check `text`, `sourceUrl`, `pageStart`, `pageEnd`, `documentId`, and `chunkId` before indexing. A useful output is not evidence of a customer charge or creator earnings; billing receipts must be reconciled separately.

This page is a consumer-facing mirror of the reviewed canonical quickstart in private EchoEmpire source, published for self-serve discovery. It does not change Actor code, build, pricing, or example-task configuration.
