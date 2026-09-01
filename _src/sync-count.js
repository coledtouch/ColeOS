#!/usr/bin/env node
/* sync-count.js — ONE source of truth for "how many platforms".
 *
 * N is derived from the PRODUCTS array in index.html (the My Projects catalog).
 * Every hand-written copy of that number elsewhere — meta tags, JSON-LD, the
 * noscript block, terminal copy, ColeAI answers, boot lines, ask/ pages,
 * resume.html, status.html (and the worker, if you pass it) — is rewritten to N,
 * keeping each spot's own form: numeric "12" stays numeric, "Twelve"/"twelve"
 * stays a word. Anything still carrying a different number in a "platforms"
 * phrase is listed for review at the end.
 *
 *   node _src/sync-count.js                               # sync the site
 *   node _src/sync-count.js ../coleos-api/src/worker.js   # ...and the worker
 *   node _src/sync-count.js --check                       # report only
 *
 * Add a project to PRODUCTS, run this, review the diff, deploy. That's it. */
const fs = require("fs"), path = require("path");
const ROOT = path.resolve(__dirname, "..");
const args = process.argv.slice(2), CHECK = args.includes("--check");
const extra = args.filter(a => !a.startsWith("--")).map(a => path.resolve(a));

const idx = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const block = idx.match(/const PRODUCTS=\[([\s\S]*?)\n\];/);
if (!block) throw new Error("PRODUCTS array not found in index.html");
const N = (block[1].match(/^\s*\{n:"/gm) || []).length;
if (!N) throw new Error("could not count PRODUCTS entries");

const WORDS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split(" ");
const w = WORDS[N] || String(N), W = w[0].toUpperCase() + w.slice(1);
const cap = x => x[0].toUpperCase() + x.slice(1);
const NUM = "(\\d+|" + WORDS.slice(1).map(x => cap(x) + "|" + x).join("|") + ")";
const form = tok => /^\d+$/.test(tok) ? String(N) : (/^[A-Z]/.test(tok) ? W : w);

const RULES = [
  [new RegExp(`\\b${NUM} production platforms`, "g"),        (m, t) => `${form(t)} production platforms`],
  [new RegExp(`\\b${NUM} other production platforms`, "g"),  (m, t) => `${form(t)} other production platforms`],
  [new RegExp(`\\b${NUM} live platforms`, "g"),              (m, t) => `${form(t)} live platforms`],
  [new RegExp(`\\b${NUM} platforms\\b`, "g"),                (m, t) => `${form(t)} platforms`],
  [new RegExp(`\\b${NUM} volumes (ready|mounted)`, "g"),     (m, t, k) => `${form(t)} volumes ${k}`],
  [new RegExp(`\\b${NUM}, all live`, "g"),                   (m, t) => `${form(t)}, all live`],
  [/\["\d+","platforms shipped"\]/g,                          () => `["${N}","platforms shipped"]`],
  [/· \+\d+ more/g,                                           () => `· +${N - 3} more`],   // boot screen lists 3, counts the rest
];

const files = ["index.html", "resume.html", "status.html",
  ...fs.readdirSync(path.join(ROOT, "ask")).filter(f => f.endsWith(".html")).map(f => "ask/" + f)]
  .map(f => path.join(ROOT, f)).concat(extra);

let total = 0;
for (const f of files) {
  const before = fs.readFileSync(f, "utf8"); let after = before, n = 0;
  for (const [re, rep] of RULES) after = after.replace(re, (...a) => { const out = rep(...a); if (out !== a[0]) n++; return out; });
  if (n) { total += n; console.log(`${CHECK ? "would update" : "updated"} ${path.relative(ROOT, f)}: ${n} spot(s)`); if (!CHECK) fs.writeFileSync(f, after); }
}
console.log(`platform count = ${N} (${w}) — ${total} change(s)${CHECK ? " pending" : ""}`);

const stale = new RegExp(`\\b(\\d+|${WORDS.slice(1).map(x => cap(x) + "|" + x).join("|")})\\s+(?:production |live |other production )?platforms\\b`, "g");
for (const f of files) {
  const s = fs.readFileSync(f, "utf8"); let m;
  while ((m = stale.exec(s))) {
    const v = m[1], asN = /^\d+$/.test(v) ? +v : WORDS.indexOf(v.toLowerCase());
    if (asN !== N) console.log(`  review ${path.relative(ROOT, f)}: "${m[0]}"`);
  }
}
