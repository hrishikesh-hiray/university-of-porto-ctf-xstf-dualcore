const http = require('http');
const crypto = require('crypto');

const BASE = 'http://127.0.0.1:6969';
const GAME_SEED = 'WHAT_HAPPENS_IN_M3DIA_STAYS_IN_M3DIA';

function req(method, path, body, cookie='') {
  return new Promise((resolve, reject) => {
    const data = body ? new URLSearchParams(body).toString() : null;
    const u = new URL(BASE + path);
    const opts = {
      hostname: u.hostname, port: u.port, path: u.pathname + u.search, method,
      headers: {
        ...(data ? {'Content-Type':'application/x-www-form-urlencoded','Content-Length': Buffer.byteLength(data)} : {}),
        ...(cookie ? {Cookie: cookie} : {})
      }
    };
    const r = http.request(opts, (res) => {
      let out=''; res.on('data', d => out += d.toString());
      res.on('end', () => resolve({status:res.statusCode, headers:res.headers, body:out}));
    });
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}

function decodeJwtPayload(jwt){
  const p = jwt.split('.')[1];
  return JSON.parse(Buffer.from(p, 'base64url').toString());
}

function correctMove(userId, plays){
  const input = `${userId}:${plays}:${GAME_SEED}`;
  const hash = crypto.createHmac('sha256', GAME_SEED).update(input).digest('hex');
  const lastChar = parseInt(hash.slice(-1),16);
  return (lastChar % 2 === 0) ? 'cross' : 'wait';
}

(async()=>{
  const username = 'local_' + Math.random().toString(16).slice(2,8);
  const password = 'pw123456';
  await req('POST','/api/register',{username,password});
  const login = await req('POST','/api/login',{username,password});
  const tokenCookie = (login.headers['set-cookie']||[]).find(x => x.startsWith('token='));
  if (!tokenCookie) throw new Error('No auth token');
  const cookie = tokenCookie.split(';')[0];
  const token = cookie.slice('token='.length);
  const payload = decodeJwtPayload(token);

  let plays = 0;
  let score = 0;
  while (score < 777) {
    const action = correctMove(payload.id, plays);
    const pr = await req('POST','/api/play',{action},cookie);
    const data = JSON.parse(pr.body);
    if (data.status !== 'safe') throw new Error(`Unexpected fail at play ${plays}`);
    score += data.gained;
    plays += 1;
  }

  const me = await req('GET','/api/me',null,cookie);
  console.log(me.body);
})();
