import {randomUUID} from 'node:crypto';
import {z} from 'zod';
import type {RowDataPacket} from 'mysql2';
import {pool,bootstrap} from './db.js';
import {makeApp,finishApp,HttpError} from './http.js';
import {orderInput,keyInput,requestHash,priceOrder} from './domain.js';
await bootstrap(async()=>{
 await pool.query(`CREATE TABLE IF NOT EXISTS orders(id CHAR(36) PRIMARY KEY,customer_name VARCHAR(100) NOT NULL,customer_email VARCHAR(254) NOT NULL,total_vnd BIGINT UNSIGNED NOT NULL,status VARCHAR(20) NOT NULL DEFAULT 'CREATED',idempotency_key VARCHAR(100) CHARACTER SET ascii COLLATE ascii_bin NOT NULL UNIQUE,request_hash CHAR(64) NOT NULL,created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)) ENGINE=InnoDB`);
 await pool.query(`CREATE TABLE IF NOT EXISTS order_items(id CHAR(36) PRIMARY KEY,order_id CHAR(36) NOT NULL,product_id CHAR(36) NOT NULL,product_name VARCHAR(150) NOT NULL,unit_price_vnd BIGINT UNSIGNED NOT NULL,quantity INT NOT NULL,subtotal_vnd BIGINT UNSIGNED NOT NULL,FOREIGN KEY(order_id) REFERENCES orders(id)) ENGINE=InnoDB`);
});
const map=(r:any)=>({id:r.id,customerName:r.customer_name,customerEmail:r.customer_email,totalVnd:Number(r.total_vnd),status:r.status,createdAt:r.created_at});
async function get(id:string) {
 const [rows]=await pool.execute<RowDataPacket[]>('SELECT * FROM orders WHERE id=?',[id]);if(!rows[0])throw new HttpError(404,'Không tìm thấy đơn hàng.','ORDER_NOT_FOUND');
 const [items]=await pool.execute<RowDataPacket[]>('SELECT * FROM order_items WHERE order_id=? ORDER BY product_id',[id]);
 return {...map(rows[0]),items:items.map(i=>({productId:i.product_id,productName:i.product_name,unitPriceVnd:Number(i.unit_price_vnd),quantity:i.quantity,subtotalVnd:Number(i.subtotal_vnd)}))};
}
async function replay(key:string,hash:string) {
 const [rows]=await pool.execute<RowDataPacket[]>('SELECT id,request_hash FROM orders WHERE idempotency_key=?',[key]);
 if(!rows[0])return null;
 if(rows[0].request_hash!==hash)throw new HttpError(409,'Khóa yêu cầu đã được dùng cho một nội dung khác.','IDEMPOTENCY_CONFLICT');
 return get(rows[0].id);
}
const app=makeApp('orders');
app.get('/health/ready',async(_req,res)=>{await pool.query('SELECT 1');res.json({status:'ok'});});
app.get('/orders',async(req,res)=>{
 const q=z.object({page:z.coerce.number().int().min(1).max(100000).default(1),pageSize:z.coerce.number().int().min(1).max(50).default(10)}).parse(req.query);
 const [rows]=await pool.query<RowDataPacket[]>('SELECT * FROM orders ORDER BY created_at DESC,id DESC LIMIT ? OFFSET ?',[q.pageSize,(q.page-1)*q.pageSize]);
 const [count]=await pool.query<RowDataPacket[]>('SELECT COUNT(*) AS total FROM orders');res.json({items:rows.map(map),total:Number(count[0].total),...q});
});
app.get('/orders/:id',async(req,res)=>res.json(await get(z.string().uuid().parse(req.params.id))));
app.post('/orders',async(req,res)=>{
 const input=orderInput.parse(req.body),key=keyInput.parse(req.get('idempotency-key')),hash=requestHash(input);
 const old=await replay(key,hash);if(old){res.json(old);return;}
 let response: globalThis.Response;
 try {response=await fetch((process.env.PRODUCTS_URL||'http://127.0.0.1:3001')+'/internal/products/resolve',{method:'POST',headers:{'Content-Type':'application/json','X-Request-Id':res.locals.requestId},body:JSON.stringify({ids:input.items.map(i=>i.productId)}),signal:AbortSignal.timeout(3000)});}
 catch {throw new HttpError(503,'Dịch vụ sản phẩm chưa sẵn sàng. Vui lòng thử lại.','PRODUCTS_UNAVAILABLE');}
 if(response.status===404)throw new HttpError(404,'Có sản phẩm không tồn tại.','PRODUCT_NOT_FOUND');
 if(!response.ok)throw new HttpError(503,'Dịch vụ sản phẩm chưa sẵn sàng.','PRODUCTS_UNAVAILABLE');
 const data=await response.json() as {items:{id:string;name:string;priceVnd:number;isActive:boolean}[]};
 if(data.items.some(p=>!p.isActive))throw new HttpError(409,'Có sản phẩm đã ngừng bán. Vui lòng cập nhật giỏ hàng.','PRODUCT_INACTIVE');
 const priced=priceOrder(input,data.items),id=randomUUID(),conn=await pool.getConnection();
 let duplicate=false;
 try {
  await conn.beginTransaction();
  await conn.execute('INSERT INTO orders(id,customer_name,customer_email,total_vnd,idempotency_key,request_hash) VALUES(?,?,?,?,?,?)',[id,input.customerName,input.customerEmail,priced.totalVnd,key,hash]);
  for(const i of priced.items)await conn.execute('INSERT INTO order_items(id,order_id,product_id,product_name,unit_price_vnd,quantity,subtotal_vnd) VALUES(?,?,?,?,?,?,?)',[randomUUID(),id,i.productId,i.productName,i.unitPriceVnd,i.quantity,i.subtotalVnd]);
  await conn.commit();
 } catch(err:any) {
  await conn.rollback();
  if(err.code==='ER_DUP_ENTRY') duplicate=true; else throw err;
 } finally { conn.release(); }
 if(duplicate){const saved=await replay(key,hash);if(saved){res.json(saved);return;}throw new HttpError(503,'Vui lòng gửi lại yêu cầu.');}
 res.status(201).json(await get(id));
});
finishApp(app);
const server=app.listen(Number(process.env.PORT||3002),'0.0.0.0',()=>console.log('Orders ready'));
process.on('SIGTERM',()=>server.close(()=>{void pool.end().then(()=>process.exit(0));}));
