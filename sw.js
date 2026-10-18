/* Service Worker: app shell offline, audio cache-first with Range support (iOS Safari needs 206 responses). */
var SHELL = 'hmbsg-shell-v1';
var AUDIO = 'hmbsg-audio-v1';
var SHELL_FILES = ['./', './index.html', './info.html', './manifest.webmanifest', './icon-192.png', './icon-512.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(SHELL).then(function (c) { return c.addAll(SHELL_FILES); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== SHELL && k !== AUDIO; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

function rangeResponse(cached, rangeHeader) {
  return cached.blob().then(function (blob) {
    var size = blob.size;
    var m = /bytes=(\d*)-(\d*)/.exec(rangeHeader || '');
    if (!m) return new Response(blob, { status: 200, headers: { 'Content-Type': 'audio/mpeg', 'Content-Length': String(size), 'Accept-Ranges': 'bytes' } });
    var start = m[1] ? parseInt(m[1], 10) : 0;
    var end = m[2] ? Math.min(parseInt(m[2], 10), size - 1) : size - 1;
    if (start >= size) return new Response(null, { status: 416, headers: { 'Content-Range': 'bytes */' + size } });
    var part = blob.slice(start, end + 1);
    return new Response(part, { status: 206, headers: {
      'Content-Type': 'audio/mpeg', 'Content-Length': String(end - start + 1),
      'Content-Range': 'bytes ' + start + '-' + end + '/' + size, 'Accept-Ranges': 'bytes' } });
  });
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (url.pathname.indexOf('/audio/') !== -1 && /\.mp3$/i.test(url.pathname)) {
    e.respondWith(caches.open(AUDIO).then(function (c) { return c.match(url.href); }).then(function (cached) {
      if (cached) return rangeResponse(cached, req.headers.get('range'));
      return fetch(req);
    }));
    return;
  }
  // app shell: network first, cache fallback
  e.respondWith(fetch(req).then(function (resp) {
    if (resp && resp.ok && url.pathname.indexOf('/audio/') === -1) {
      var copy = resp.clone(); caches.open(SHELL).then(function (c) { c.put(req, copy); });
    }
    return resp;
  }).catch(function () { return caches.match(req, { ignoreSearch: true }).then(function (r) { return r || caches.match('./index.html'); }); }));
});
