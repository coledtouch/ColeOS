#!/usr/bin/env node
/* ci-deploy.js — runs inside GitHub Actions (.github/workflows/deploy.yml).
 *
 * On a console "Deploy" (workflow_dispatch) it pulls the Adviser's staged edits
 * from the worker, applies them to this checkout, stamps sw.js, publishes to the
 * "coleos" Worker, clears the queue, and commits the applied edits back to main
 * so the repo stays the source of truth. On a plain push it just deploys HEAD.
 *
 * The Cloudflare token lives in the repo's Actions secrets — never on the worker.
 * Env: CLOUDFLARE_API_TOKEN, COLEOS_ADMIN_TOKEN, APPLY_PENDING ("true" on dispatch) */
const fs = require("fs"), path = require("path"), crypto = require("crypto"), { execSync } = require("child_process");
const SITE = path.resolve(__dirname, "..");
const API = "https://coleos-api.coleciprari.workers.dev";
const ACCOUNT = "ba46412ff1f79be9aef72d7f1895fd78";
const CF = (process.env.CLOUDFLARE_API_TOKEN || "").trim();
const ADMIN = (process.env.COLEOS_ADMIN_TOKEN || "").trim();
const APPLY = process.env.APPLY_PENDING === "true";
if (!CF) {
  // Not configured yet — say so loudly on the run, but don't paint the repo red for a setup step.
  console.log("::warning::CLOUDFLARE_API_TOKEN isn't set on this repo, so the deploy was skipped. "
    + "Add it (and COLEOS_ADMIN_TOKEN) under Settings → Secrets and variables → Actions, e.g. "
    + "gh secret set CLOUDFLARE_API_TOKEN --repo coledtouch/ColeOS < ~/.coleos/cf-api-token.txt");
  process.exit(0);
}

const MIME = { html: "text/html; charset=utf-8", js: "text/javascript; charset=utf-8", xml: "application/xml",
  txt: "text/plain; charset=utf-8", webmanifest: "application/manifest+json", png: "image/png",
  jpg: "image/jpeg", ico: "image/x-icon", pdf: "application/pdf", svg: "image/svg+xml" };

function collect(dir) {
  const ignore = new Set([".git", ".gitignore", ".assetsignore", ".github", "_src", "node_modules", ".DS_Store", "Thumbs.db", "desktop.ini"]);
  const ai = path.join(dir, ".assetsignore");
  if (fs.existsSync(ai)) for (let line of fs.readFileSync(ai, "utf8").split(/\r?\n/)) {
    line = line.trim(); if (!line || line.startsWith("#")) continue;
    ignore.add(line.replace(/^\*\*\//, "").replace(/\/$/, ""));
  }
  const globs = [...ignore].filter(x => x.includes("*"))
    .map(x => new RegExp("^" + x.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*") + "$"));
  const out = [];
  (function walk(d, rel) {
    for (const name of fs.readdirSync(d)) {
      if (ignore.has(name) || globs.some(g => g.test(name))) continue;
      const full = path.join(d, name), r = rel + "/" + name;
      if (fs.statSync(full).isDirectory()) walk(full, r); else out.push({ rel: r, full });
    }
  })(dir, "");
  return out;
}
const h32 = b => crypto.createHash("sha256").update(b).digest("hex").slice(0, 32);

function stampSW(dir) {
  const files = collect(dir).filter(f => f.rel !== "/sw.js").sort((a, b) => a.rel.localeCompare(b.rel));
  const h = crypto.createHash("sha256");
  for (const f of files) h.update(f.rel).update(fs.readFileSync(f.full));
  const ver = h.digest("hex").slice(0, 12), sw = path.join(dir, "sw.js");
  const src = fs.readFileSync(sw, "utf8"), out = src.replace(/const VERSION = "[0-9a-f]+";/, `const VERSION = "${ver}";`);
  if (out !== src) fs.writeFileSync(sw, out);
  return ver;
}

async function deployAssets(dir) {
  const files = collect(dir), manifest = {}, byHash = {};
  for (const f of files) {
    const buf = fs.readFileSync(f.full), hash = h32(buf);
    manifest[f.rel] = { hash, size: buf.length };
    byHash[hash] = { buf, ext: f.rel.split(".").pop().toLowerCase() };
  }
  const base = `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT}`, auth = { authorization: "Bearer " + CF };
  const sess = await (await fetch(`${base}/workers/scripts/coleos/assets-upload-session`, {
    method: "POST", headers: { ...auth, "content-type": "application/json" }, body: JSON.stringify({ manifest }) })).json();
  if (!sess.success) throw new Error("upload session: " + JSON.stringify(sess.errors));
  let completion = sess.result.jwt, uploaded = 0;
  for (const bucket of sess.result.buckets || []) {
    const fd = new FormData();
    for (const hash of bucket) { const { buf, ext } = byHash[hash];
      fd.append(hash, new Blob([buf.toString("base64")], { type: MIME[ext] || "application/octet-stream" }), hash); uploaded++; }
    const up = await (await fetch(`${base}/workers/assets/upload?base64=true`, {
      method: "POST", headers: { authorization: "Bearer " + sess.result.jwt }, body: fd })).json();
    if (!up.success) throw new Error("asset upload: " + JSON.stringify(up.errors));
    if (up.result && up.result.jwt) completion = up.result.jwt;
  }
  const fd2 = new FormData();
  fd2.append("metadata", JSON.stringify({ assets: { jwt: completion }, compatibility_date: "2026-08-12" }));
  const put = await (await fetch(`${base}/workers/scripts/coleos`, { method: "PUT", headers: auth, body: fd2 })).json();
  if (!put.success) throw new Error("deploy: " + JSON.stringify(put.errors));
  console.log(`deployed coleos: ${files.length} files, ${uploaded} uploaded`);
}

(async () => {
  let edits = [];
  if (APPLY && ADMIN) {
    const r = await fetch(`${API}/pending`, { headers: { authorization: "Bearer " + ADMIN } });
    if (r.ok) edits = (await r.json()).pending || [];
    console.log(`${edits.length} staged edit(s) from the Adviser`);
  } else console.log(APPLY ? "COLEOS_ADMIN_TOKEN not set — deploying HEAD only" : "push build — deploying HEAD");

  for (const e of edits) {
    const local = path.join(SITE, e.path.replace(/^\//, ""));
    if (e.kind === "write") { fs.mkdirSync(path.dirname(local), { recursive: true }); fs.writeFileSync(local, e.new); console.log(`  write  ${e.path}`); continue; }
    const cur = fs.readFileSync(local, "utf8"), i = cur.indexOf(e.old);
    if (i < 0 || cur.indexOf(e.old, i + 1) >= 0) { console.error(`  FAIL   ${e.path}: edit #${e.id} ${i < 0 ? "no longer matches" : "matches twice"} — aborting, nothing deployed`); process.exit(1); }
    fs.writeFileSync(local, cur.slice(0, i) + e.new + cur.slice(i + e.old.length));
    console.log(`  edit   ${e.path} — ${e.note || ""}`);
  }

  console.log("sw.js VERSION", stampSW(SITE));
  await deployAssets(SITE);
  if (edits.length) await fetch(`${API}/deployed`, { method: "POST", headers: { authorization: "Bearer " + ADMIN } });

  const status = execSync("git status --porcelain", { cwd: SITE, encoding: "utf8" }).trim();
  if (!status) { console.log("nothing to commit"); return; }
  execSync('git config user.name "coleos-deploy"', { cwd: SITE });
  execSync('git config user.email "info@coenconstruction.com"', { cwd: SITE });
  execSync("git add -A", { cwd: SITE });
  const msg = edits.length
    ? `Apply ${edits.length} staged edit(s) from the Adviser\n\n` + edits.map(e => `- ${e.kind} ${e.path}${e.note ? " — " + e.note : ""}`).join("\n")
    : "Stamp service-worker version";
  execSync("git commit -q -F -", { cwd: SITE, input: msg });
  execSync("git push", { cwd: SITE, stdio: "inherit" });
  console.log("committed + pushed the applied changes");
})().catch(e => { console.error(e.message); process.exit(1); });
