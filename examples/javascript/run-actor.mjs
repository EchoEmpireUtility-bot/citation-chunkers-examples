import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const actors = { pdf: "H1c9OyB0AnRf8Sy4y", ocr: "50meJWqJ27Aw2QYZD" };
const product = process.argv[2] ?? "pdf";
if (!(product in actors)) throw new Error("Usage: node run-actor.mjs [pdf|ocr]");
if (!process.env.APIFY_TOKEN) throw new Error("Set APIFY_TOKEN to an Apify API token.");

const here = dirname(fileURLToPath(import.meta.url));
const input = await readFile(join(here, "..", "..", "inputs", `${product}-citation-chunker.json`));
const response = await fetch(`https://api.apify.com/v2/acts/${actors[product]}/runs`, {
  method: "POST",
  headers: { Authorization: `Bearer ${process.env.APIFY_TOKEN}`, "Content-Type": "application/json" },
  body: input,
});
if (!response.ok) throw new Error(await response.text());
console.log(JSON.stringify(await response.json(), null, 2));
