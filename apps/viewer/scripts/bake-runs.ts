// Bake the repo's runs/ into dist/runs/ for the static Cloudflare Pages deploy.
// Run after `vite build` (it is the second half of `pnpm build:pages`):
//
//   vite-node scripts/bake-runs.ts
//
// The logic and its byte-parity test live in vite/bakeRuns.ts; this only wires the repo paths
// (the same runs/ the dev server's serveRuns plugin mounts) and fails loudly on a dist that
// Pages would reject.

import path from "node:path";
import { fileURLToPath } from "node:url";
import { assertPagesReady, bakeRuns } from "../vite/bakeRuns";

const viewerDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const runsDir = path.resolve(viewerDir, "../../runs");
const distDir = path.join(viewerDir, "dist");

const result = bakeRuns(runsDir, path.join(distDir, "runs"));
if (!result.baked.includes("/_index") || result.baked.length <= 2) {
  throw new Error(`no runs found under ${runsDir}; refusing to bake an empty viewer`);
}
const runs = new Set(result.baked.filter((u) => !u.startsWith("/_")).map((u) => u.split("/")[1]));
console.log(`baked ${result.baked.length} URLs for ${runs.size} runs from ${runsDir} into dist/runs/`);
for (const s of result.sharded) {
  console.log(`  sharded /runs${s.url}: ${(s.bytes / 1048576).toFixed(2)} MiB in ${s.parts} parts`);
}
for (const u of result.notFound) console.log(`  absent (the dev endpoint 404s it too): /runs${u}`);
assertPagesReady(distDir);
console.log("dist/ is ready for Cloudflare Pages");
