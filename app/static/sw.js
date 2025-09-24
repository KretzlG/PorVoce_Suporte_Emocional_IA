// Service Worker for PWA functionality
const CACHE_NAME = 'porvocesaude-v1.0.0';
const STATIC_CACHE = 'static-v1.0.0';

// Files to cache for offline functionality
const CACHE_FILES = [
    '/',
    '/static/manifest.json',
    '/static/css/base.css',
    '/static/js/base.js',
    '/static/img/logo.png',
    '/static/img/favicon.ico',
    
    // Vuetify and Vue files (CDN)
    'https://cdn.jsdelivr.net/npm/vuetify@3.4.0/dist/vuetify.min.css',
    'https://cdn.jsdelivr.net/npm/vuetify@3.4.0/dist/vuetify.min.js',
    'https://unpkg.com/vue@3.3.8/dist/vue.global.js',
    'https://cdn.jsdelivr.net/npm/@mdi/font@7.3.67/css/materialdesignicons.min.css',
    
    // Google Fonts
    'https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&display=swap',
    
    // Offline pages
    '/offline',
    '/emergency'
];

// Installation event
self.addEventListener('install', event => {
    console.log('[SW] Installing service worker...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching app shell...');
                return cache.addAll(CACHE_FILES);
            })
            .then(() => {
                console.log('[SW] App shell cached successfully');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('[SW] Error caching app shell:', error);
            })
    );
});

// Activation event
self.addEventListener('activate', event => {
    console.log('[SW] Activating service worker...');
    
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME && cacheName !== STATIC_CACHE) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('[SW] Service worker activated');
            return self.clients.claim();
        })
    );
});

// Fetch event - Network first, then cache strategy for API calls
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);
    
    // Skip non-GET requests and chrome-extension requests
    if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
        return;
    }
    
    // Handle API requests - Network first strategy
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // If successful, clone and cache the response
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // If network fails, try to serve from cache
                    return caches.match(request)
                        .then(cachedResponse => {
                            if (cachedResponse) {
                                return cachedResponse;
                            }
                            // Return offline response for critical API calls
                            return new Response(
                                JSON.stringify({
                                    success: false,
                                    error: 'Você está offline. Verifique sua conexão.',
                                    offline: true
                                }),
                                {
                                    status: 200,
                                    headers: { 'Content-Type': 'application/json' }
                                }
                            );
                        });
                })
        );
        return;
    }
    
    // Handle static assets and pages - Cache first strategy
    event.respondWith(
        caches.match(request)
            .then(cachedResponse => {
                // Return cached version if available
                if (cachedResponse) {
                    return cachedResponse;
                }
                
                // Otherwise fetch from network
                return fetch(request)
                    .then(response => {
                        // Don't cache non-success responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response
                        const responseToCache = response.clone();
                        
                        // Cache the fetched response
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(() => {
                        // If both cache and network fail, show offline page
                        if (request.destination === 'document') {
                            return caches.match('/offline');
                        }
                        
                        // For other resources, return a generic offline response
                        return new Response('Offline', { status: 503 });
                    });
            })
    );
});

// Background sync for offline chat messages
self.addEventListener('sync', event => {
    console.log('[SW] Background sync event:', event.tag);
    
    if (event.tag === 'chat-message-sync') {
        event.waitUntil(syncChatMessages());
    }
});

// Push notifications for emergency alerts
self.addEventListener('push', event => {
    console.log('[SW] Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'Você tem uma nova mensagem',
        icon: '/static/img/icon-192x192.png',
        badge: '/static/img/icon-72x72.png',
        vibrate: [200, 100, 200],
        tag: 'chat-notification',
        actions: [
            {
                action: 'open',
                title: 'Abrir Chat',
                icon: '/static/img/icon-192x192.png'
            },
            {
                action: 'dismiss',
                title: 'Dispensar'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Por Você - Suporte Emocional', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'open' || !event.action) {
        event.waitUntil(
            clients.openWindow('/chat')
        );
    }
});

// Helper function to sync chat messages
async function syncChatMessages() {
    try {
        // Get pending messages from IndexedDB
        const pendingMessages = await getPendingMessages();
        
        for (const message of pendingMessages) {
            try {
                const response = await fetch('/api/chat/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(message)
                });
                
                if (response.ok) {
                    // Remove from pending messages
                    await removePendingMessage(message.id);
                    console.log('[SW] Message synced successfully');
                }
            } catch (error) {
                console.error('[SW] Error syncing message:', error);
            }
        }
    } catch (error) {
        console.error('[SW] Error during background sync:', error);
    }
}

// Helper function to get pending messages (would use IndexedDB)
async function getPendingMessages() {
    // This would integrate with IndexedDB to store offline messages
    return [];
}

// Helper function to remove pending message (would use IndexedDB)
async function removePendingMessage(messageId) {
    // This would integrate with IndexedDB
    console.log('[SW] Removing pending message:', messageId);
}

// Error handling
self.addEventListener('error', event => {
    console.error('[SW] Service worker error:', event.error);
});

// Install prompt handling
let deferredPrompt;

self.addEventListener('beforeinstallprompt', event => {
    console.log('[SW] Before install prompt fired');
    event.preventDefault();
    deferredPrompt = event;
    
    // Notify the main thread that the PWA can be installed
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage({
                type: 'PWA_INSTALLABLE'
            });
        });
    });
});

// App installed event
self.addEventListener('appinstalled', event => {
    console.log('[SW] PWA was installed');
    deferredPrompt = null;
    
    // Track installation
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage({
                type: 'PWA_INSTALLED'
            });
        });
    });
});

// Message handling from main thread
self.addEventListener('message', event => {
    console.log('[SW] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME });
    }
});

console.log('[SW] Service worker script loaded');