import { createHash } from "node:crypto";
import { readdir, readFile, writeFile } from "node:fs/promises";
import { relative, resolve, sep } from "node:path";
import { getDeploymentConfig, withDeploymentBase } from "./deployment-paths.mjs";

const root = resolve("dist");
const { base } = getDeploymentConfig();

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map(async (entry) => {
    const path = resolve(directory, entry.name);
    return entry.isDirectory() ? walk(path) : [path];
  }));
  return nested.flat();
}

const files = (await walk(root))
  .filter((path) => !path.endsWith(`${sep}sw.js`))
  .sort();

const digest = createHash("sha256");
for (const file of files) {
  digest.update(relative(root, file));
  digest.update(await readFile(file));
}

const fileUrls = files.map((file) => withDeploymentBase(relative(root, file).split(sep).join("/"), base));
const routeUrls = ["/", "/data", "/presentasi"].map((route) => withDeploymentBase(route, base));
const precache = [...new Set([...routeUrls, ...fileUrls])];
const cacheScope = base.replace(/^\/+|\/+$/g, "").replace(/[^a-z\d]+/gi, "-").toLowerCase() || "root";
const cachePrefix = `lima-tahun-fmipa-${cacheScope}-`;
const cacheName = `${cachePrefix}${digest.digest("hex").slice(0, 12)}`;
const appRoot = withDeploymentBase("/", base);

const source = `const CACHE_PREFIX = ${JSON.stringify(cachePrefix)};
const CACHE_NAME = ${JSON.stringify(cacheName)};
const APP_ROOT = ${JSON.stringify(appRoot)};
const PRECACHE = ${JSON.stringify(precache, null, 2)};

const scopePath = new URL(self.registration.scope).pathname;
const isWithinScope = (url) => url.origin === self.location.origin && url.pathname.startsWith(scopePath);

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => Promise.all(PRECACHE.map((url) => cache.add(url))))
      .then(() => self.skipWaiting())
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
  if (event.request.method !== "GET" || !isWithinScope(requestUrl)) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(event.request);

    if (event.request.mode !== "navigate" && cached) return cached;

    try {
      const response = await fetch(event.request);
      if (response.ok) await cache.put(event.request, response.clone());
      return response;
    } catch (_) {
      if (cached) return cached;
      const path = requestUrl.pathname;
      const indexPath = path.endsWith("/") ? path + "index.html" : path + "/index.html";
      return (await cache.match(indexPath)) || (await cache.match(APP_ROOT));
    }
  })());
});
`;

await writeFile(resolve(root, "sw.js"), source);
console.log(`Service worker: ${precache.length} berkas, cache ${cacheName}`);
