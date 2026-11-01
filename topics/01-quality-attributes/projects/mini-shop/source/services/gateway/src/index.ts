import {makeApp,finishApp,HttpError} from './http.js';
const app=makeApp('gateway');
app.get('/health/ready',(_req,res)=>res.json({status:'ok'}));
app.use(async(req,res,next)=>{
 const match=req.path.match(/^\/api\/(products|orders)(?:\/[a-fA-F0-9-]+)?$/);
 if(!match || !['GET','POST','PATCH'].includes(req.method)){next();return;}
 const target=match[1]==='products'?(process.env.PRODUCTS_URL||'http://127.0.0.1:3001'):(process.env.ORDERS_URL||'http://127.0.0.1:3002');
 try {
  const headers:Record<string,string>={'Content-Type':'application/json','X-Request-Id':res.locals.requestId};
  if(req.get('idempotency-key'))headers['Idempotency-Key']=req.get('idempotency-key')!;
  const upstream=await fetch(target+req.originalUrl.replace(/^\/api/,''),{method:req.method,headers,body:req.method==='GET'?undefined:JSON.stringify(req.body),signal:AbortSignal.timeout(8000)});
  res.status(upstream.status).type('application/json').send(await upstream.text());
 } catch {throw new HttpError(503,'Dịch vụ tạm thời không khả dụng. Vui lòng thử lại.','SERVICE_UNAVAILABLE');}
});
finishApp(app);
const server=app.listen(Number(process.env.PORT||3000),'0.0.0.0',()=>console.log('Gateway ready'));
process.on('SIGTERM',()=>server.close(()=>process.exit(0)));
