// Inject an item-write failure in the lab database to verify transaction rollback.
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const base=process.env.BASE_URL||'http://127.0.0.1:8080';
async function api(path,method='GET',body,key){const r=await fetch(base+'/api'+path,{method,headers:{'Content-Type':'application/json',...(key?{'Idempotency-Key':key}:{})},body:body?JSON.stringify(body):undefined});return {status:r.status,data:await r.json()};}
function sql(query){const code="const mysql=require('mysql2/promise');(async()=>{const c=await mysql.createConnection({host:process.env.DB_HOST,user:process.env.DB_USER,password:process.env.DB_PASSWORD,database:process.env.DB_NAME});const [rows]=await c.query(process.argv[1]);console.log(JSON.stringify(rows));await c.end();})().catch(e=>{console.error(e.code);process.exit(1)});";const args=['compose','--project-directory',root,'exec','-T','orders','node','-e',code,query];return JSON.parse(execFileSync(process.env.DOCKER_PRIVILEGE||'docker',process.env.DOCKER_PRIVILEGE?['docker',...args]:args,{encoding:'utf8',timeout:120000}));}
const created=await api('/products','POST',{name:'Test Rollback '+Date.now(),description:'Failure injection',priceVnd:5000,isActive:true});assert.equal(created.status,201);const id=created.data.id;
const trigger='lab01_verify_'+randomUUID().replaceAll('-','');let installed=false;
const body={customerName:'Test Rollback',customerEmail:'rollback@example.com',items:[{productId:'10000000-0000-4000-8000-000000000001',quantity:1},{productId:id,quantity:1}]};
const key=randomUUID();
try{
 const before=sql('SELECT (SELECT COUNT(*) FROM orders) AS orders_count,(SELECT COUNT(*) FROM order_items) AS items_count')[0];
 sql(`CREATE TRIGGER ${trigger} BEFORE INSERT ON order_items FOR EACH ROW BEGIN IF NEW.product_id='${id}' THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Lab rollback injection'; END IF; END`);installed=true;
 const failed=await api('/orders','POST',body,key);assert.equal(failed.status,500);
 const after=sql('SELECT (SELECT COUNT(*) FROM orders) AS orders_count,(SELECT COUNT(*) FROM order_items) AS items_count')[0];assert.deepEqual(after,before);console.log('PASS A15 injected second-item failure rolls back order and first item');
}finally{if(installed)sql(`DROP TRIGGER ${trigger}`);}
const retry=await api('/orders','POST',body,key);assert.equal(retry.status,201);assert.equal(retry.data.items.length,2);console.log('PASS A16 same-key retry succeeds after rollback');
await api('/products/'+id,'PATCH',{isActive:false});
