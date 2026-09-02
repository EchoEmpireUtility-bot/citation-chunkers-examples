param(
    [ValidateSet("pdf", "ocr")]
    [string]$Product = "pdf"
)

if ([string]::IsNullOrWhiteSpace($env:APIFY_TOKEN)) {
    throw "Set APIFY_TOKEN to an Apify API token."
}

$actorIds = @{ pdf = "H1c9OyB0AnRf8Sy4y"; ocr = "50meJWqJ27Aw2QYZD" }
$root = Split-Path $PSScriptRoot -Parent | Split-Path -Parent
$inputPath = Join-Path $root "inputs\$Product-citation-chunker.json"
$headers = @{ Authorization = "Bearer $env:APIFY_TOKEN" }
$uri = "https://api.apify.com/v2/actors/$($actorIds[$Product])/run-sync-get-dataset-items?clean=true&maxTotalChargeUsd=0.05"

Invoke-RestMethod `
    -Uri $uri `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -InFile $inputPath `
    -TimeoutSec 310 | ConvertTo-Json -Depth 10
