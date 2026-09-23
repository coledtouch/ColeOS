#!/usr/bin/env node
/* security-headers.js — builds the `_headers` rules ciprari.ai is served with.
 *
 * Generated at deploy time, not committed, because the Content-Security-Policy pins
 * each page's own inline <script> by its SHA-256, and index.html's script changes on
 * every deploy (Adviser edits, sync-count). Both deploy paths call buildHeaders()
 * after every edit to the files and pass the result to Cloudflare as the assets
 * `_headers` config: _src/ci-deploy.js (GitHub Actions) and deploy/lib.js (local).
 *
 *   node _src/security-headers.js            print the rules
 *   node _src/security-headers.js --write    also write ./_headers (for wrangler dev)
 *
 * Why the policy is shaped this way:
 *  - script-src has no 'unsafe-inline': an injected <script> or onX= attribute does not
 *    run, which is the whole point after the esc() quote bug.
 *  - Documents the page creates (iframe srcdoc, blob: and about:blank popups) inherit
 *    this policy, so the App Builder cannot run user code in them. It runs apps in
 *    /sandbox.html instead, which gets its own permissive policy plus the CSP
 *    `sandbox` directive, so its code has an opaque origin even when opened top-level.
 *  - connect-src names the API worker, so a script that did slip through cannot post
 *    the admin session to another host with fetch/sendBeacon.
 */
const fs = require("fs"), path = require("path"), crypto = require("crypto"), vm = require("vm");

const API = "https://coleos-api.coleciprari.workers.dev";
const PDFJS = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/";
const SKIP_DIRS = new Set([".git", ".github", ".claude", ".wrangler", "_src", "node_modules"]);
const MAX_LINE = 2000;   // Cloudflare's per-line limit for _headers

/** Every .html file that will be published. */
function htmlFiles(dir, rel = "") {
  const out = [];
  for (const name of fs.readdirSync(path.join(dir, rel))) {
    if (SKIP_DIRS.has(name)) continue;
    const r = rel ? rel + "/" + name : name, full = path.join(dir, r);
    if (fs.statSync(full).isDirectory()) out.push(...htmlFiles(dir, r));
    else if (/\.html?$/i.test(name)) out.push(r);
  }
  return out;
}

/** Inline scripts a browser would execute, with their CSP hashes. */
function inlineScripts(html, file) {
  const out = [];
  // The HTML parser normalizes newlines before the script's text exists, so hash that.
  const src = html.replace(/\r\n?/g, "\n");
  for (const m of src.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script[\s\/>]/gi)) {
    const attrs = m[1], body = m[2];
    if (/\bsrc\s*=/i.test(attrs)) continue;
    const type = (attrs.match(/\btype\s*=\s*["']?([^"'\s>]+)/i) || [])[1] || "";
    if (type && !/^(text\/javascript|application\/javascript|module)$/i.test(type)) continue;   // JSON-LD etc. never runs
    if (!body.trim()) continue;
    // A wrong boundary would pin a hash the browser never sees and take the page down,
    // so insist the extracted text is a complete script before trusting it.
    try { new vm.Script(body, { filename: file }); }
    catch (e) {
      if (type !== "module") throw new Error(`${file}: inline script does not parse on its own (${e.message}); refusing to pin a hash for it`);
    }
    out.push("'sha256-" + crypto.createHash("sha256").update(body, "utf8").digest("base64") + "'");
  }
  return out;
}

function sitePolicy(hashes) {
  return [
    "default-src 'self'",
    // The pdf.js path covers pdf.min.js and the worker it imports from a blob: wrapper.
    `script-src 'self' ${hashes.join(" ")} ${PDFJS}`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    // 'self' is load-bearing twice: the résumé PDF viewer, and the service worker, whose
    // own fetches follow the policy served with /sw.js.
    `connect-src 'self' ${API}`,
    // https: because the ColeScape browser opens any site you type; 'self' for /sandbox.
    "frame-src 'self' https:",
    "worker-src 'self' blob:",
    "manifest-src 'self'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'self'",
    "frame-ancestors 'self'",
    // No upgrade-insecure-requests: nothing here loads over http, and while http:// is
    // still served it would upgrade /sandbox to https, which then refuses an http parent.
  ].join("; ");
}

/* The App Builder's runner. Opaque origin via the sandbox directive, so apps can use
   inline script and CDN libraries without being able to read ciprari.ai's storage. */
const SANDBOX_POLICY = [
  "sandbox allow-scripts allow-modals allow-forms allow-popups",
  "default-src * data: blob: 'unsafe-inline' 'unsafe-eval'",
  "frame-ancestors 'self'",
].join("; ");

function buildHeaders(siteDir) {
  const hashes = new Set();
  for (const f of htmlFiles(siteDir)) {
    if (f === "sandbox.html") continue;   // governed by its own policy below
    for (const h of inlineScripts(fs.readFileSync(path.join(siteDir, f), "utf8"), f)) hashes.add(h);
  }
  const common = [
    "Strict-Transport-Security: max-age=31536000; includeSubDomains",
    "X-Content-Type-Options: nosniff",
    "Referrer-Policy: strict-origin-when-cross-origin",
    "Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), serial=(), bluetooth=(), hid=(), midi=()",
    "Cross-Origin-Opener-Policy: same-origin-allow-popups",
  ];
  /* Order matters: Cloudflare applies rules top to bottom and APPENDS a header a later
     rule sets again. The sandbox rules must come last, and must detach the site's CSP
     first, or /sandbox would carry both policies and no app script could run. COOP is
     detached too: a top-level page with CSP sandbox flags and any COOP but unsafe-none
     is a network error, which would break "open in new tab". */
  const sandbox = (p) => [p,
    "  ! Content-Security-Policy",
    "  ! Cross-Origin-Opener-Policy",
    "  ! X-Frame-Options",
    "  Content-Security-Policy: " + SANDBOX_POLICY,
    ""];
  const text = [
    "/*",
    ...common.map((l) => "  " + l),
    "  X-Frame-Options: SAMEORIGIN",
    "  Content-Security-Policy: " + sitePolicy([...hashes].sort()),
    "",
    ...sandbox("/sandbox"),
    ...sandbox("/sandbox.html"),
  ].join("\n");
  const long = text.split("\n").find((l) => l.length > MAX_LINE);
  if (long) throw new Error(`_headers line is ${long.length} chars (Cloudflare's limit is ${MAX_LINE}): ${long.slice(0, 80)}…`);
  return text;
}

module.exports = { buildHeaders, inlineScripts, htmlFiles };

if (require.main === module) {
  const site = path.resolve(__dirname, "..");
  const text = buildHeaders(site);
  process.stdout.write(text);
  if (process.argv.includes("--write")) fs.writeFileSync(path.join(site, "_headers"), text);
}
