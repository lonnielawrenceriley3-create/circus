#!/usr/bin/env node

/**
 * Flea Circus - Simple State Server
 *
 * Enables multi-device synchronization over network/WiFi
 *
 * Usage:
 *   node server.js [port]
 *
 * Defaults to port 8000
 *
 * Then access:
 *   Operator: http://localhost:8000/control.html
 *   Display:  http://localhost:8000/display.html
 *
 * Or on network:
 *   http://<your-ip>:8000/control.html
 *   http://<your-ip>:8000/display.html
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.argv[2] || 8000;

let sharedState = {
    displayMode: 'intro',
    currentCue: null,
    videoUrl: null,
    videoPlaying: false,
    audioUrl: null,
    audioPlaying: false,
    audioVolume: 1,
    overlayText: '',
    overlayType: null,
    timerDuration: 0,
    timerActive: false,
    messageText: '',
    lastUpdate: 0,
    connectionStatus: 'connected'
};

const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.ogv': 'video/ogg',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.ogg': 'audio/ogg',
    '.m4a': 'audio/m4a',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.query;

    // Enable CORS for all requests
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // API Routes
    if (pathname === '/api/state' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(sharedState));
        return;
    }

    if (pathname === '/api/state' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                const updates = JSON.parse(body);
                sharedState = {
                    ...sharedState,
                    ...updates,
                    lastUpdate: Date.now()
                };
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(sharedState));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Invalid JSON' }));
            }
        });
        return;
    }

    // Serve static files
    let filePath = pathname === '/' ? '/index.html' : pathname;
    filePath = path.join(__dirname, filePath);

    // Security: prevent path traversal
    if (!filePath.startsWith(__dirname)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }

    fs.stat(filePath, (err, stats) => {
        if (err || !stats.isFile()) {
            res.writeHead(404);
            res.end('Not Found');
            return;
        }

        const ext = path.extname(filePath).toLowerCase();
        const contentType = mimeTypes[ext] || 'application/octet-stream';

        res.writeHead(200, { 'Content-Type': contentType });
        fs.createReadStream(filePath).pipe(res);
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`
🎪 Flea Circus Show Control System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Server running on port ${PORT}

Access from:
  Local:       http://localhost:${PORT}
  This device: http://127.0.0.1:${PORT}

Find your IP address:
  Linux/Mac:   ifconfig | grep "inet " | grep -v 127
  Windows:     ipconfig

On your network:
  Operator:    http://<YOUR-IP>:${PORT}/control.html
  Display:     http://<YOUR-IP>:${PORT}/display.html

Then:
  1. Open Display on projector/TV in fullscreen
  2. Open Operator on tablet
  3. Both will sync automatically

Press Ctrl+C to stop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    `);
});

process.on('SIGINT', () => {
    console.log('\n\nServer stopped.');
    process.exit(0);
});
