/* ColeOS service worker — ciprari.ai
 *
 * Strategy is deliberately split:
 *
 *   HTML  → network first, cache as fallback.
 *     The whole app is one ~475 KB index.html that changes on every deploy. If it
 *     were served cache-first, visitors would sit on a stale build until the cache
 *     expired — which is exactly the sort of bug that wastes an afternoon. Network
 *     first means an update always lands the moment you are online, and the cached
 *     copy only appears when there is no connection at all.
 *
 *   Everything else → cache first, refreshed in the background.
 *     Icons, the PDF and the OG image are content-addressed by deploy, so serving
 *     them from cache instantly is safe.
 */
const VERSION = "3566a14935aa";
const SHELL = "coleos-shell-" + VERSION;
const ASSETS = "coleos-assets-" + VERSION;

/* Enough to boot offline. Deliberately small — the HTML carries the whole app. */
const PRECACHE = [
  "/",
  "/manifest.webmanifest",
  "/favicon-192.png",
  "/favicon-512.png",
  "/apple-touch-icon.png",
  // Photos moved out of the HTML into real files; cached here so About and
  // Blue.jpg still work offline without bloating the initial download.
  "/headshot.png",
  "/blue.jpg",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches
      .open(SHELL)
      .then((c) => c.addAll(PRECACHE))
      // A single missing file must not abort the whole install.
      .catch(() => {})
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((k) => k.startsWith("coleos-") && k !== SHELL && k !== ASSETS)
            .map((k) => caches.delete(k))
        )
      )
      .then(() => self.clients.claim())
  );
});

const isHTML = (req) =>
  req.mode === "navigate" ||
  (req.headers.get("accept") || "").includes("text/html");

self.addEventListener("fetch", (e) => {
  const req = e.request;

  // Never touch anything that isn't a plain GET on our own origin: the ColeAI and
  // ColeMail calls go to the Worker on a different host and must not be cached.
  if (req.method !== "GET") return;
  let url;
  try { url = new URL(req.url); } catch (_) { return; }
  if (url.origin !== self.location.origin) return;

  if (isHTML(req)) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(SHELL).then((c) => c.put("/", copy)).catch(() => {});
          return res;
        })
        .catch(() =>
          caches.match("/", { ignoreSearch: true }).then(
            (hit) =>
              hit ||
              new Response(
                "<!doctype html><meta charset=utf-8><title>ColeOS — offline</title>" +
                  "<body style='font-family:system-ui;background:#0d7d7d;color:#fff;padding:40px'>" +
                  "<h1>ColeOS is offline</h1><p>Reconnect and reload to boot.</p>",
                { headers: { "Content-Type": "text/html" } }
              )
          )
        )
    );
    return;
  }

  e.respondWith(
    caches.match(req).then((hit) => {
      if (hit) {
        // refresh in the background so the next load is current
        fetch(req)
          .then((res) => {
            if (res && res.ok) caches.open(ASSETS).then((c) => c.put(req, res)).catch(() => {});
          })
          .catch(() => {});
        return hit;
      }
      return fetch(req)
        .then((res) => {
          if (res && res.ok && res.status === 200) {
            const copy = res.clone();
            caches.open(ASSETS).then((c) => c.put(req, copy)).catch(() => {});
          }
          return res;
        })
        .catch(() => caches.match(req));
    })
  );
});

/* The page asks for this after an update so it can prompt for a reload. */
self.addEventListener("message", (e) => {
  if (e.data === "version") {
    e.source && e.source.postMessage({ swVersion: VERSION });
  }
  if (e.data === "skipWaiting") self.skipWaiting();
});
