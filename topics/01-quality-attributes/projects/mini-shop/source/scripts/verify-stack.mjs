import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const base=process.env.BASE_URL||'http://127.0.0.1:8080';
function docker(args){return execFileSync(process.env.DOCKER_PRIVILEGE||'docker',process.env.DOCKER_PRIVILEGE?['docker',...args]:args,{encoding:'utf8',timeout:240000,maxBuffer:5*1024*1024});}
function compose(...args){return docker(['compose','--project-directory',root,...args]);}
async function api(path,method='GET',body,key){const r=await fetch(base+'/api'+path,{method,headers:{'Content-Type':'application/json',...(key?{'Idempotency-Key':key}:{})},body:body?JSON.stringify(body):undefined,signal:AbortSignal.timeout(10000)});return {status:r.status,data:await r.json()};}
async function wait(path){for(let i=0;i<40;i++){try{if((await api(path)).status===200)return;}catch{}await new Promise(r=>setTimeout(r,1000));}throw Error('Not recovered: '+path);}
function pass(id){console.log('PASS '+id);}
async function verifyDeployment(){
 const orderContainer=compose('ps','-q','orders').trim();const before=docker(['inspect','--format','{{.Id}} {{.State.StartedAt}}',orderContainer]).trim();
 const productsBefore=compose('ps','-q','products').trim();
 compose('up','-d','--build','--force-recreate','--no-deps','--wait','products');assert.notEqual(compose('ps','-q','products').trim(),productsBefore);const after=docker(['inspect','--format','{{.Id}} {{.State.StartedAt}}',orderContainer]).trim();assert.equal(after,before);await wait('/products');pass('D06 independent Products build/deploy');
}
if(process.argv.includes('--deployment-only')){await verifyDeployment();}else{
try{
 compose('config','--quiet');
 const ps=compose('ps','--format','json').trim().split('\n').map(l=>JSON.parse(l));assert.equal(ps.length,6);assert.ok(ps.every(p=>p.Health==='healthy'));pass('D01 six healthy containers');
 const key=randomUUID();const body={customerName:'Test Chaos',customerEmail:'chaos@example.com',items:[{productId:'10000000-0000-4000-8000-000000000001',quantity:1}]};
 const created=await api('/orders','POST',body,key);assert.equal(created.status,201);const order=created.data;
 compose('stop','products');
 const start=Date.now();const failed=await api('/orders','POST',body,randomUUID());assert.equal(failed.status,503);assert.ok(Date.now()-start<8000);assert.equal((await api('/orders/'+order.id)).status,200);pass('D02 Products outage isolates existing orders');
 const replay=await api('/orders','POST',body,key);assert.equal(replay.status,200);assert.equal(replay.data.id,order.id);pass('D08 replay while Products offline');
 compose('start','products');await wait('/products');assert.equal((await api('/orders','POST',body,randomUUID())).status,201);pass('D03 recovery');
 compose('restart','orders-db');await wait('/orders');assert.equal((await api('/orders','POST',body,randomUUID())).status,201);pass('D04 database reconnect');
 compose('down');compose('up','-d','--wait');await wait('/orders');assert.equal((await api('/orders/'+order.id)).data.totalVnd,order.totalVnd);pass('D05 persistence down/up without deleting volumes');
 await verifyDeployment();
 for(const service of ['products','orders']){
  const id=compose('ps','-q',service).trim();const nets=JSON.parse(docker(['inspect','--format','{{json .NetworkSettings.Networks}}',id]));assert.ok(Object.keys(nets).includes('lab01-mini-shop_'+service+'-data'));assert.ok(!Object.keys(nets).includes('lab01-mini-shop_'+(service==='products'?'orders':'products')+'-data'));
  const dbId=compose('ps','-q',service+'-db').trim();const ports=docker(['inspect','--format','{{json .HostConfig.PortBindings}}',dbId]).trim();assert.ok(ports==='{}'||ports==='null');
  const code="const mysql=require('mysql2/promise');(async()=>{const c=await mysql.createConnection({host:process.env.DB_HOST,user:process.env.DB_USER,password:process.env.DB_PASSWORD,database:process.env.DB_NAME});const [rows]=await c.query('SHOW GRANTS');const s=JSON.stringify(rows);if(!s.includes('`'+process.env.DB_NAME+'`.*'))process.exitCode=1;try{await c.query('SELECT * FROM mysql.user');process.exitCode=1;}catch(e){if(e.code!=='ER_TABLEACCESS_DENIED_ERROR'&&e.code!=='ER_DBACCESS_DENIED_ERROR')throw e;}await c.end();})().catch(e=>{console.error(e.code);process.exit(1)});";
  compose('exec','-T',service,'node','-e',code);
 }
 pass('D07 network isolation, private DB ports, restricted grants');
 console.log('All Docker verification scenarios passed.');
}finally{compose('up','-d','--wait');}

}
