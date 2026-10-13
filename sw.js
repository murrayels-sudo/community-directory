// Community Directory - Service Worker
// Caches the app shell so it opens with zero connectivity, and serves
// directory.json from cache when offline (network is tried first so
// updates come through whenever there IS a connection).

const CACHE_NAME = "community-directory-v10";
const SHELL_FILES = [
  "./",
  "./index.html",
  "./manifest.json",
  "./directory.json",
  "./suburb-coordinates.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-512-maskable.png",
  "./icons/apple-touch-icon.png",
  "./qr-code.png"
];

self.addEventListener("install", (event) => {
  // Fetch every shell file fresh from the network (bypassing the browser's
  // HTTP cache) so a new version is never filled with an older copy.
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      Promise.all(
        SHELL_FILES.map((file) =>
          fetch(new Request(file, { cache: "reload" })).then((res) => {
            if (!res.ok) throw new Error("Could not fetch " + file);
            return cache.put(file, res);
          })
        )
      )
    )
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;

  // directory.json and suburb-coordinates.json: network-first so updates
  // are picked up the moment there's a connection, falling back to cache
  // when offline.
  if (req.url.endsWith("directory.json") || req.url.endsWith("suburb-coordinates.json")) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // The app page itself: network-first so fixes and new versions arrive
  // straight away, falling back to the saved copy when offline.
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(new Request(req, { cache: "no-cache" }))
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put("./index.html", copy));
          return res;
        })
        .catch(() => caches.match("./index.html").then((c) => c || caches.match(req)))
    );
    return;
  }

  // everything else (app shell): cache-first for instant, offline-safe loads.
  event.respondWith(
    caches.match(req).then((cached) => cached || fetch(req))
  );
});
