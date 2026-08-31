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

## Quick start

Set a token in your shell, then run one of the examples:

```sh
export APIFY_TOKEN="your_apify_token"
curl -X POST \
  "https://api.apify.com/v2/acts/H1c9OyB0AnRf8Sy4y/runs" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  --data @inputs/pdf-citation-chunker.json
```

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
openapi/        minimal invocation contract for the two Apify Actors
```
