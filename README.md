> **Canonical source migrated on 2026-10-08:** development now belongs in [EchoEmpire-Machine-Foundry/examples/citation-chunkers](https://github.com/EchoEmpireUtility-bot/EchoEmpire-Machine-Foundry/tree/master/examples/citation-chunkers). This repository is retained for source history and existing consumer/deployment compatibility. The documentation below is its pre-cutover baseline, not a current Empire status or operating-authority source. Use the canonical repository's [STATUS.md](https://github.com/EchoEmpireUtility-bot/EchoEmpire-Machine-Foundry/blob/master/STATUS.md) and [authority map](https://github.com/EchoEmpireUtility-bot/EchoEmpire-Machine-Foundry/blob/master/empire/authority-map.json).

# EchoEmpire Citation Chunkers — Integration Examples

Machine-readable PDF ingestion for RAG, retrieval, search, and agents.

| Product | Give it | It returns | Store page |
| --- | --- | --- | --- |
| PDF Citation Chunker | A public embedded-text PDF URL | Deterministic, page-aware citation-ready JSON chunks | https://apify.com/skilled_glee/pdf-citation-chunker |
| OCR Citation Chunker | A public scanned or image-only PDF URL | OCR-backed, page-aware citation-ready JSON chunks with quality metadata | https://apify.com/skilled_glee/ocr-citation-chunker |

Both Actors are public, use Apify pay-per-event billing, and are eligible for agentic payments. An Apify API token is required to run either Actor programmatically. Do not include your token in source control.

## Choose the right Actor

- Use **PDF Citation Chunker** when a PDF has an embedded text layer.
- Use **OCR Citation Chunker** when the PDF is scanned, image-only, or has no useful embedded text layer.

Each output record carries page provenance, a stable SHA-256-based identifier, normalized text, and source-document metadata. OCR records also carry confidence and quality fields.

## Quick start: input URL → JSON chunks

Set an Apify token, then run the PDF Actor. This request waits for the Actor and prints its dataset items directly—no run polling or second dataset request.

```sh
export APIFY_TOKEN="your_apify_token"
curl --fail-with-body -X POST \
  "https://api.apify.com/v2/actors/H1c9OyB0AnRf8Sy4y/run-sync-get-dataset-items?clean=true&maxTotalChargeUsd=0.05" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  --data @inputs/pdf-citation-chunker.json
```

The example caps total run charges at **$0.05**. Raise the cap only when you intentionally submit larger work.

Apify's synchronous endpoint waits for up to five minutes. Use the asynchronous `/runs` workflow for large OCR documents or any job that may exceed that limit; a synchronous HTTP timeout does not abort the underlying Actor run.

See language-specific examples in [examples](examples), ready-to-copy inputs in [inputs](inputs), and representative excerpts from genuine output records in [sample-output](sample-output).

## For AI agents / MCP

Useful discovery terms:

- **PDF:** PDF chunking, RAG ingestion, citation chunks, page provenance, stable chunk IDs.
- **OCR:** scanned PDF OCR, image-only PDF, OCR to JSON, citation-ready OCR, scanned documents for RAG.

Apify agents can discover, inspect, and run these Actors through the Apify Store and MCP integration. The direct x402 discovery surface is also available at:

- Catalog: https://echoempire-x402-apify-gateway.d7682413.workers.dev/
- OpenAPI: https://echoempire-x402-apify-gateway.d7682413.workers.dev/openapi.json
- MCP manifest: https://echoempire-x402-apify-gateway.d7682413.workers.dev/.well-known/mcp.json
- Agent guidance: https://echoempire-x402-apify-gateway.d7682413.workers.dev/llms.txt

The direct x402 PDF flow requires a quote first; see the gateway OpenAPI for its payment workflow. The examples in this repository use the standard Apify API so developers can choose their own Apify billing or agentic-payment mechanism.

## Important behavior

- Billing is tied to successful useful work, not to the number of JSON chunks.
- OCR blank pages may be scanned but emit no useful record and are not charged as `page-processed` events.
- Use only public PDFs you are authorized to process.

## Repository layout

```text
examples/       curl, Python, JavaScript, and PowerShell invocation examples
inputs/         ready-to-run Actor inputs
sample-output/  representative excerpts from genuine output records
openapi/        synchronous invocation contract for the two Apify Actors
```
