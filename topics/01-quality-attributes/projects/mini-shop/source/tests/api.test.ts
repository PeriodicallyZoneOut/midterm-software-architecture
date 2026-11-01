import {test} from 'node:test';
import assert from 'node:assert/strict';
import {randomUUID} from 'node:crypto';
const base=process.env.BASE_URL||'http://127.0.0.1:8080';
async function call(path:string,method='GET',body?:unknown,key?:string){const res=await fetch(base+'/api'+path,{method,headers:{'Content-Type':'application/json',...(key?{'Idempotency-Key':key}:{})},body:body===undefined?undefined:JSON.stringify(body)});return {status:res.status,data:await res.json() as any};}
const productBody={name:'Test API '+Date.now(),description:'Automated test',priceVnd:15000,isActive:true};
let product:any,order:any;
const key=randomUUID();
const makeBody=(id=product.id)=>({customerName:'Test Buyer',customerEmail:'buyer@example.com',items:[{productId:id,quantity:2}]});
test('API integration',async t=>{
 await t.test('A01 seed và contract',async()=>{const r=await call('/products');assert.equal(r.status,200);assert.ok(r.data.items.length>=5);});
 await t.test('A02 create/get/patch product',async()=>{const r=await call('/products','POST',productBody);assert.equal(r.status,201);product=r.data;assert.equal((await call('/products/'+product.id)).data.priceVnd,15000);assert.equal((await call('/products/'+product.id,'PATCH',{description:'Edited'})).status,200);});
 await t.test('A03 validation product',async()=>{for(const patch of [{priceVnd:-1},{priceVnd:1.2},{extra:'x'},{}])assert.equal((await call('/products/'+product.id,'PATCH',patch)).status,400,JSON.stringify(patch));});
 await t.test('A03b PATCH giữ các trường không gửi',async()=>{await call('/products/'+product.id,'PATCH',{isActive:false,description:'Keep me'});const r=await call('/products/'+product.id,'PATCH',{name:productBody.name});assert.equal(r.data.isActive,false);assert.equal(r.data.description,'Keep me');await call('/products/'+product.id,'PATCH',{isActive:true});});
 await t.test('A04 tạo đơn dùng giá server',async()=>{const r=await call('/orders','POST',makeBody(),key);assert.equal(r.status,201);order=r.data;assert.equal(order.totalVnd,30000);assert.equal(order.items[0].unitPriceVnd,15000);});
 await t.test('A05 snapshot sau sửa giá/tên',async()=>{await call('/products/'+product.id,'PATCH',{priceVnd:99000,name:'Test changed'});const r=await call('/orders/'+order.id);assert.equal(r.data.totalVnd,30000);assert.equal(r.data.items[0].productName,productBody.name);});
 await t.test('A06 replay và A07 conflict',async()=>{const r=await call('/orders','POST',makeBody(),key);assert.equal(r.status,200);assert.equal(r.data.id,order.id);assert.equal((await call('/orders','POST',{...makeBody(),customerName:'Different'},key)).status,409);});
 await t.test('A08 concurrent replay không trùng đơn',async()=>{const key=randomUUID();const rs=await Promise.all(Array.from({length:6},()=>call('/orders','POST',makeBody(),key)));assert.equal(rs.filter(r=>r.status===201).length,1);assert.equal(rs.filter(r=>r.status===200).length,5);assert.equal(new Set(rs.map(r=>r.data.id)).size,1);});
 await t.test('A09 absent/inactive không tạo đơn',async()=>{const before=(await call('/orders')).data.total;assert.equal((await call('/orders','POST',makeBody(randomUUID()),randomUUID())).status,404);await call('/products/'+product.id,'PATCH',{isActive:false});assert.equal((await call('/orders','POST',makeBody(),randomUUID())).status,409);assert.equal((await call('/orders')).data.total,before);await call('/products/'+product.id,'PATCH',{isActive:true});});
 await t.test('A10 input sai/malformed/oversized',async()=>{assert.equal((await call('/orders','POST',makeBody())).status,400);assert.equal((await call('/orders','POST',{...makeBody(),items:[...makeBody().items,...makeBody().items]},randomUUID())).status,400);for(const quantity of [0,100,1.5])assert.equal((await call('/orders','POST',{...makeBody(),items:[{productId:product.id,quantity}]},randomUUID())).status,400);const raw=await fetch(base+'/api/orders',{method:'POST',headers:{'Content-Type':'application/json'},body:'{broken'});assert.equal(raw.status,400);const large=await call('/orders','POST',{text:'x'.repeat(40000)},randomUUID());assert.equal(large.status,413);});
 await t.test('A11 pagination et 404',async()=>{const r=await call('/orders?page=1&pageSize=1');assert.equal(r.status,200);assert.equal(r.data.items.length,1);assert.equal(r.data.pageSize,1);assert.equal((await call('/orders?pageSize=51')).status,400);assert.equal((await call('/orders/'+randomUUID())).status,404);});
 await t.test('A12 routes internes inaccessibles',async()=>{assert.equal((await call('/internal/products/resolve','POST',{ids:[product.id]})).status,404);assert.equal((await call('/unknown')).status,404);});
 await t.test('A13 propagation request ID',async()=>{const r=await fetch(base+'/api/products',{headers:{'X-Request-Id':'test-trace-123'}});assert.equal(r.headers.get('x-request-id'),'test-trace-123');});
 await t.test('A14 không nhận giá client',async()=>assert.equal((await call('/orders','POST',{...makeBody(),items:[{productId:product.id,quantity:1,priceVnd:1}]},randomUUID())).status,400));
 await call('/products/'+product.id,'PATCH',{isActive:false});
});
