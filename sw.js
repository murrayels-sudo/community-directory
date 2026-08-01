// Community Directory - Service Worker
// Caches the app shell so it opens with zero connectivity, and serves
// directory.json from cache when offline (network is tried first so
// updates come through whenever there IS a connection).

const CACHE_NAME = "community-directory-v1";
const SHELL_FILES = [
  "./",
  "./index.html",
  "./manifest.json",
  "./directory.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-512-maskable.png",
  "./icons/apple-touch-icon.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_FILES))
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

  // directory.json: network-first so updates are picked up the moment
  // there's a connection, falling back to cache when offline.
  if (req.url.endsWith("directory.json")) {
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

  // everything else (app shell): cache-first for instant, offline-safe loads.
  event.respondWith(
    caches.match(req).then((cached) => cached || fetch(req))
  );
});
