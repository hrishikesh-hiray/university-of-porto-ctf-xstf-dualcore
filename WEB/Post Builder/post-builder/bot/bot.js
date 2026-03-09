const express = require('express');
const puppeteer = require('puppeteer-core');

const app = express();
app.use(express.json());

const FLAG = process.env.FLAG || 'FLAG{test_flag}';
const WEB_URL = process.env.WEB_URL || 'http://127.0.0.1:5001';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

const rateLimitStore = new Map();
const RATE_LIMIT = 3;
const RATE_WINDOW = 60000; // 60 seconds in ms

function checkRateLimit(ip) {
    const now = Date.now();
    const windowStart = now - RATE_WINDOW;
    
    let timestamps = rateLimitStore.get(ip) || [];
    timestamps = timestamps.filter(t => t > windowStart);
    
    if (timestamps.length >= RATE_LIMIT) {
        return false;
    }
    
    timestamps.push(now);
    rateLimitStore.set(ip, timestamps);
    return true;
}

async function visitUrl(urlToVisit) {
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: 'new',
            executablePath: '/usr/bin/chromium', // Uses the apt-get installed Chromium
	    pipe: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox', // Crucial for running as root
                '--disable-dev-shm-usage',
                '--disable-gpu',
		'--single-process'
            ]
        });
        
        const page = await browser.newPage();
        
        // Go to login page
        await page.goto(`${WEB_URL}/login`, { waitUntil: 'networkidle2' });
        
        // Execute login script and inject variables safely
        await page.evaluate(async (password, flag, targetUrl, webUrl) => {
            const loginData = { username: 'admin', password: password };
            await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(loginData),
                credentials: 'include'
            });
            sessionStorage.setItem('adminFlag', flag);
            window.location.href = targetUrl.replace(webUrl, '');
        }, ADMIN_PASSWORD, FLAG, urlToVisit, WEB_URL);

        // Wait for 6 seconds to let any XSS payloads trigger
        await new Promise(r => setTimeout(r, 6000));

    } catch (error) {
        console.error(`Error visiting URL: ${error.message}`);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

app.post('/visit', (req, res) => {
    const clientIp = req.ip;
    if (!checkRateLimit(clientIp)) {
        return res.status(429).json({ error: 'Rate limit exceeded. Please try again later.' });
    }

    const { url } = req.body;
    if (!url) {
        return res.status(400).json({ error: 'Missing url parameter' });
    }

    if (!url.startsWith(WEB_URL)) {
        return res.status(400).json({ error: 'Invalid URL' });
    }

    // Fire and forget (don't await) so the API responds immediately
    visitUrl(url);

    return res.status(200).json({ message: 'Bot will visit your URL shortly' });
});

app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok' });
});

app.listen(8000, '0.0.0.0', () => {
    console.log('Puppeteer Bot listening on port 8000');
});
