var staticCacheName = "django-pwa-v" + new Date().getTime();
var filesToCache = [
    '/customer_panel/customer_login_page/',
    '/static/customer_panel/css/bootstrap.min.css',
    // Add other common CSS/JS files here to make them load instantly
    '/static/customer_panel/js/bootstrap.bundle.min.js'
];

// Cache on install
self.addEventListener("install", event => {
    this.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                return cache.addAll(filesToCache);
            })
    );
});

// Serve from cache
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});