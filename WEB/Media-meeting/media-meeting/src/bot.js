const puppeteer = require('puppeteer-core');
const db = require('./db');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || "dev_secret";
const TIMEOUT = 8000;
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const adminToken = jwt.sign({ 
    id: 999999, 
    username: 'Bot',
    role: 'admin'
}, JWT_SECRET);

async function browse(url, user, token){
    let browser;
    let result;
    try{
        browser = await puppeteer.launch({
            headless: true,
            pipe: true,
            executablePath: '/usr/bin/chromium',
            ignoreHTTPSErrors: true, 
            acceptInsecureCerts: true,
            args: [
                '--ignore-certificate-errors',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-wasm',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-crash-reporter',
                '--no-crashpad',
                '--jitless'
            ]
        });
        result = await Promise.race([
            visit(browser, url, user, token),
            sleep(TIMEOUT).then(() => {
                throw new Error('Bot timeout');
            })
        ]);

    }catch(e){
        result = `Bot encountered an error: ${e.message}`;
    }finally{
        if(browser){
            try{
                await browser.close();
            }catch(e){
                console.error('Failed to close browser:', e);
            }
        }
    }
    return result;
}

async function visit(browser, url, user, token){
    const page = await browser.newPage();
    let adminPlayResponse = null;

    await page.setCookie({
        name: 'adminToken',
        value: adminToken,
        domain: '127.0.0.1',
        path: '/',
        httpOnly: true,
        sameSite: 'Lax'
    });
    await page.setCookie({
        name: 'token',
        value: token,
        domain: '127.0.0.1',
        path: '/',
        httpOnly: true,
        sameSite: 'Lax'
    });

    page.on('response', async (response) => {
        try {
            const url = response.url();
            if (url.endsWith('/api/adminPlay')) {
                if (response.status() === 200) { // Admin didn't die!
                    rawJsonResponse = await response.json(); // still just want to be sure
                    adminPlayResponse = rawJsonResponse.status;
                }
                else {
                    adminPlayResponse = "fail";
                }
            }
        } catch (e) {
            console.log('BOT: Failed to parse response', e);
        }
    });
    
    try{
        const now = Date.now();
        await page.goto(url);
        await sleep(2000 - (Date.now() - now)); // no timing attack casino is safe!

        const finalUrl = page.url();

        if (!finalUrl.startsWith('http://127.0.0.1:6969')) {
            await page.close();
            return "Are you a Hacker, little Orange?";
        }

        if (!adminPlayResponse) {
            await page.close();
            return "Admin play was never executed.";
        }

        const action = (adminPlayResponse === 'safe') ? 'cross' : 'wait';

        if (user.hints <= 0) {
            await page.close();
            return "This is not the house of Joana. If you want more hints, send 5€ MBWay to 962401457";
        }
        db.useHint(user.id);
        await page.close();
        return `Lizzy says '${action.toUpperCase()}'..."`;
    }
    catch(e){
        console.error('Error during visit:', e);
        return 'Error during visit: ' + e.message;
    }
}

module.exports = {browse};
