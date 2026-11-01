import { randomUUID } from 'node:crypto';
import { z } from 'zod';
import type { RowDataPacket } from 'mysql2';
import {pool,bootstrap} from './db.js';
import {makeApp,finishApp,HttpError} from './http.js';
const productInput=z.object({name:z.string().trim().min(1).max(150),description:z.string().trim().max(2000),priceVnd:z.number().int().min(1).max(1_000_000_000),isActive:z.boolean()}).strict();
const createInput=productInput.extend({description:productInput.shape.description.default(''),isActive:productInput.shape.isActive.default(true)});
const patchInput=productInput.partial().refine(v=>Object.keys(v).length>0,'Cần ít nhất một trường.');
const idInput=z.string().uuid();
const map=(r:any)=>({id:r.id,name:r.name,description:r.description,priceVnd:Number(r.price_vnd),isActive:Boolean(r.is_active),createdAt:r.created_at,updatedAt:r.updated_at});
async function get(id:string) { const [rows]=await pool.execute<RowDataPacket[]>('SELECT * FROM products WHERE id=?',[id]); if(!rows[0]) throw new HttpError(404,'Không tìm thấy sản phẩm.','PRODUCT_NOT_FOUND'); return map(rows[0]); }
await bootstrap(async()=>{
 await pool.query(`CREATE TABLE IF NOT EXISTS products(id CHAR(36) PRIMARY KEY,name VARCHAR(150) NOT NULL,description TEXT NOT NULL,price_vnd BIGINT UNSIGNED NOT NULL,is_active BOOLEAN NOT NULL DEFAULT TRUE,created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)) ENGINE=InnoDB`);
 const seeds=[['Sổ tay Everyday','Giấy kem, bìa mềm. Cho những ý tưởng mỗi ngày.',89000],['Bình giữ nhiệt Studio','Dung tích 500ml, đồng hành cùng ngày làm việc.',249000],['Túi canvas Weekend','Gọn nhẹ, bền bỉ, mang theo mọi điều cần thiết.',159000],['Bút bi Essential','Nét viết mượt và thiết kế tối giản.',35000],['Đèn bàn Focus','Ánh sáng dịu cho góc làm việc của bạn.',399000]];
 for(let i=0;i<seeds.length;i++) await pool.execute('INSERT INTO products(id,name,description,price_vnd) VALUES(?,?,?,?) ON DUPLICATE KEY UPDATE id=id',[`10000000-0000-4000-8000-${String(i+1).padStart(12,'0')}`,...seeds[i]]);
});
const app=makeApp('products');
app.get('/health/ready',async(_req,res)=>{await pool.query('SELECT 1');res.json({status:'ok'});});
app.get('/products',async(_req,res)=>{const [rows]=await pool.query<RowDataPacket[]>('SELECT * FROM products ORDER BY created_at,id');res.json({items:rows.map(map)});});
app.get('/products/:id',async(req,res)=>res.json(await get(idInput.parse(req.params.id))));
app.post('/products',async(req,res)=>{const p=createInput.parse(req.body),id=randomUUID();await pool.execute('INSERT INTO products(id,name,description,price_vnd,is_active) VALUES(?,?,?,?,?)',[id,p.name,p.description,p.priceVnd,p.isActive]);res.status(201).json(await get(id));});
app.patch('/products/:id',async(req,res)=>{
 const id=idInput.parse(req.params.id),p=patchInput.parse(req.body);await get(id);
 const columns:Record<string,string>={name:'name',description:'description',priceVnd:'price_vnd',isActive:'is_active'};
 const entries=Object.entries(p).filter(([,v])=>v!==undefined);
 await pool.execute(`UPDATE products SET ${entries.map(([k])=>columns[k]+'=?').join(',')} WHERE id=?`,[...entries.map(([,v])=>v),id]);res.json(await get(id));
});
app.post('/internal/products/resolve',async(req,res)=>{
 const {ids}=z.object({ids:z.array(idInput).min(1).max(20)}).strict().parse(req.body);
 const [rows]=await pool.query<RowDataPacket[]>(`SELECT * FROM products WHERE id IN (${ids.map(()=>'?').join(',')})`,ids);
 if(rows.length!==new Set(ids).size) throw new HttpError(404,'Có sản phẩm không tồn tại.','PRODUCT_NOT_FOUND');
 res.json({items:rows.map(map)});
});
finishApp(app);
const server=app.listen(Number(process.env.PORT||3001),'0.0.0.0',()=>console.log('Products ready'));
process.on('SIGTERM',()=>server.close(()=>{void pool.end().then(()=>process.exit(0));}));
