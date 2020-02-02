self.importScripts('pyodide_config.js');

self.addEventListener('install', (e) => {
    console.log('[sw] installing');
    console.log(pyodideapp_www_files);
    e.waitUntil(
        caches.open('nutrition').then((cache) => {
            return cache.addAll(pyodideapp_www_files);
        })
    );
});

self.addEventListener('activate', function() {
    console.log('[sw] activated');
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request, {ignoreVary: true}).then(function(response) {
            if (response === undefined) {
                return fetch(event.request).then(function(response) {
                    return caches.open('nutrition').then(cache => {
                        cache.put(event.request, response.clone());
                        return response;
                    })
                })
            }
            else {
                return response;
            }
        })
    )
});