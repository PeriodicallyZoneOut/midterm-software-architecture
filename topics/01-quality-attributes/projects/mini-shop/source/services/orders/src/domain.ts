import {createHash} from 'node:crypto';
import {z} from 'zod';
export const orderInput=z.object({customerName:z.string().trim().min(1).max(100),customerEmail:z.string().trim().toLowerCase().email().max(254),items:z.array(z.object({productId:z.string().uuid(),quantity:z.number().int().min(1).max(99)}).strict()).min(1).max(20)}).strict().refine(v=>new Set(v.items.map(i=>i.productId)).size===v.items.length,'Sản phẩm không được trùng.');
export type OrderInput=z.infer<typeof orderInput>;
export type Product={id:string;name:string;priceVnd:number;isActive:boolean};
export const keyInput=z.string().regex(/^[A-Za-z0-9_-]{8,100}$/);
export function requestHash(body:OrderInput) {return createHash('sha256').update(JSON.stringify({...body,items:[...body.items].sort((a,b)=>a.productId.localeCompare(b.productId))})).digest('hex');}
export function priceOrder(input:OrderInput,products:Product[]) {
 const items=input.items.map(item=>{const p=products.find(p=>p.id===item.productId);if(!p) throw new Error('Missing product');return {...item,productName:p.name,unitPriceVnd:p.priceVnd,subtotalVnd:p.priceVnd*item.quantity};});
 return {items,totalVnd:items.reduce((sum,i)=>sum+i.subtotalVnd,0)};
}
