self.addEventListener('install', (e) => {
    self.skipWaiting();
    self.importScripts('pyodide_config.js');
    console.log('[sw] installing');
    console.log(pyodideapp_www_files);
    e.waitUntil(
        caches.open('nutrition').then((cache) => {
            return cache.addAll(pyodideapp_www_files);
        }).catch(e => console.info('already cached?'))
    );
});

self.addEventListener('activate', function() {
    console.log('[sw] activated');
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request, {ignoreVary: true}).then(function(response) {
            let fresh = fetch(event.request);
            if (response === undefined) {
                return fresh;
            }
            else {
                fresh.then(function(response) {
                    caches.open('nutrition').then(cache => {
                        cache.put(event.request, response.clone());
                    }).catch(e => console.log(e));
                })
                return response;
            }
        })
    )
});