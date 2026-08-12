const CACHE_VERSION = 'quiz-learning-v1';
const CORE_CACHE = `${CACHE_VERSION}-core`;
const CORE_ASSETS = [
  './',
  './index.html',
  './quiz.html',
  './questions.js',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CORE_CACHE)
      .then(cache => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(key => key.startsWith('quiz-learning-') && key !== CORE_CACHE)
          .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

async function networkFirst(request) {
  const cache = await caches.open(CORE_CACHE);
  try {
    const response = await fetch(request);
    if (response && response.ok) cache.put(request, response.clone());
    return response;
  } catch (error) {
    const cached = await cache.match(request, { ignoreSearch: true });
    if (cached) return cached;
    if (request.mode === 'navigate') {
      return (await cache.match('./index.html')) || (await cache.match('./quiz.html'));
    }
    throw error;
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CORE_CACHE);
  const cached = await cache.match(request, { ignoreSearch: true });
  if (cached) return cached;
  const response = await fetch(request);
  if (response && response.ok) cache.put(request, response.clone());
  return response;
}

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  const isFreshAsset = request.mode === 'navigate' ||
    url.pathname.endsWith('/quiz.html') ||
    url.pathname.endsWith('/index.html') ||
    url.pathname.endsWith('/questions.js') ||
    url.pathname.endsWith('/manifest.webmanifest');

  event.respondWith(isFreshAsset ? networkFirst(request) : cacheFirst(request));
});