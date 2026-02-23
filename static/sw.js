const CACHE_NAME = 'museum-exhibits-v3';
const PRECACHE_URLS = [
  '/',
  '/static/style.css?v=3',
  '/static/manifest.webmanifest?v=3',
  '/static/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => (k === CACHE_NAME ? null : caches.delete(k))))
    )
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;

  if (req.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) {
        return cached;
      }
      return fetch(req)
        .then((resp) => {
          const url = new URL(req.url);
          if (url.origin === self.location.origin) {
            const copy = resp.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          }
          return resp;
        })
        .catch(() => cached || caches.match('/'));
    })
  );
});
