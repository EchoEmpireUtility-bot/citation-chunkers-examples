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

Invoke-RestMethod `
    -Uri "https://api.apify.com/v2/acts/$($actorIds[$Product])/runs" `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -InFile $inputPath | ConvertTo-Json -Depth 10
