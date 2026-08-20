const SCOPE_URL = new URL(self.registration.scope);
const SCOPE_PATH = SCOPE_URL.pathname;
const SCOPE_KEY = SCOPE_PATH.replace(/^\/+|\/+$/g, "").replace(/[^a-z\d]+/gi, "-").toLowerCase() || "root";
const CACHE_PREFIX = `lima-tahun-fmipa-${SCOPE_KEY}-`;
const CACHE_NAME = `${CACHE_PREFIX}v1`;
const APP_SHELL = [
  "./",
  "./data",
  "./presentasi",
  "./manifest.webmanifest",
  "./brand/favicon.svg",
  "./brand/logo-horizontal.png",
  "./brand/logo-horizontal-white.png",
  "./brand/supergraphic-lines.png",
  "./fonts/GamaSans-Regular.otf",
  "./fonts/GamaSans-Bold.otf",
  "./fonts/GamaSerif-Regular.otf",
  "./fonts/GamaSerif-Bold.otf"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      Promise.allSettled(APP_SHELL.map((path) => cache.add(new URL(path, SCOPE_URL))))
    ).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys
        .filter((key) => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
        .map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const requestUrl = new URL(event.request.url);
  if (event.request.method !== "GET" || requestUrl.origin !== SCOPE_URL.origin || !requestUrl.pathname.startsWith(SCOPE_PATH)) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(event.request);

    if (event.request.mode !== "navigate" && cached) return cached;

    try {
      const response = await fetch(event.request);
      if (response.ok) await cache.put(event.request, response.clone());
      return response;
    } catch (_) {
      return cached ?? cache.match(new URL("./", SCOPE_URL));
    }
  })());
});
