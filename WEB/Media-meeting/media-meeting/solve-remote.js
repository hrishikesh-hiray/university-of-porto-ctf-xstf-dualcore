const http = require('http');
const crypto = require('crypto');

const BASE = 'http://46.225.117.62:30009';
const GAME_SEED = 'WHAT_HAPPENS_IN_M3DIA_STAYS_IN_M3DIA';

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
        'Content-Type': 'application/x-www-form-urlencoded',
        ...(data ? {'Content-Length': Buffer.byteLength(data)} : {}),
        ...(cookie ? {Cookie: cookie} : {}),
      },
    };
    const r = http.request(opts, (res) => {
      let out='';
      res.on('data', d => out += d.toString());
      res.on('end', () => resolve({status: res.statusCode, headers: res.headers, body: out}));
    });
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}

function parseSetCookie(setCookie) {
  if (!setCookie) return '';
  const arr = Array.isArray(setCookie) ? setCookie : [setCookie];
  return arr.map(s => s.split(';')[0]).join('; ');
}

function decodePayload(jwt) {
  const p = jwt.split('.')[1];
  return JSON.parse(Buffer.from(p.replace(/-/g,'+').replace(/_/g,'/'), 'base64').toString());
}

function getMove(userId, plays) {
  const input = `${userId}:${plays}:${GAME_SEED}`;
  const hash = crypto.createHmac('sha256', GAME_SEED).update(input).digest('hex');
  const last = parseInt(hash.slice(-1), 16);
  return last % 2 === 0 ? 'cross' : 'wait';
}

(async () => {
  const user = 'u' + Math.random().toString(16).slice(2,10);
  const pass = 'pw123456';
  await req('POST','/api/register',{username:user,password:pass});
  const login = await req('POST','/api/login',{username:user,password:pass});
  const cookie = parseSetCookie(login.headers['set-cookie']);
  const token = cookie.split(';').find(x=>x.trim().startsWith('token='))?.trim().slice(6) || cookie.replace('token=','');
  const payload = decodePayload(token);
  const uid = payload.id;

  let score = 0;
  let plays = 0;
  while (score < 777 && plays < 5000) {
    const action = getMove(uid, plays);
    const pr = await req('POST','/api/play',{action}, cookie);
    const data = JSON.parse(pr.body || '{}');
    if (data.status !== 'safe') {
      console.log('desync at plays', plays, data);
      break;
    }
    score += data.gained;
    plays += 1;
  }

  const me = await req('GET','/api/me',null,cookie);
  console.log('USER', user, 'UID', uid, 'PLAYS', plays, 'ME', me.body);
})();
