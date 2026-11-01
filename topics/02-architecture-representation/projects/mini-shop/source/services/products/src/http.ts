import express, { type Request, type Response, type NextFunction } from 'express';
import { randomUUID } from 'node:crypto';
import { ZodError } from 'zod';
export class HttpError extends Error { constructor(public status: number, message: string, public code = 'REQUEST_FAILED') { super(message); } }
export function makeApp(service: string) {
 const app = express(); app.disable('x-powered-by');
 app.use((req, res, next) => {
  const supplied = req.get('x-request-id');
  const id = supplied && /^[a-zA-Z0-9_-]{1,100}$/.test(supplied) ? supplied : randomUUID();
  res.locals.requestId = id; res.set('X-Request-Id', id);
  const start = performance.now();
  res.on('finish', () => console.log(JSON.stringify({service, requestId:id, method:req.method, path:req.path, status:res.statusCode, durationMs:Math.round(performance.now()-start)})));
  next();
 });
 app.use(express.json({limit:'32kb'}));
 app.get('/health/live', (_req,res) => res.json({status:'ok',service}));
 return app;
}
export function finishApp(app: ReturnType<typeof express>) {
 app.use((_req,res) => res.status(404).json({error:{code:'NOT_FOUND',message:'Không tìm thấy đường dẫn.'},requestId:res.locals.requestId}));
 app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
  let status = 500, code = 'INTERNAL_ERROR', message = 'Có lỗi hệ thống. Vui lòng thử lại.';
  if(err instanceof HttpError) { status=err.status; code=err.code; message=err.message; }
  else if(err instanceof ZodError) { status=400; code='VALIDATION_ERROR'; message='Dữ liệu không hợp lệ: '+err.issues.map(i=>i.path.join('.')+': '+i.message).join('; '); }
  else if(err.type==='entity.parse.failed') { status=400; code='INVALID_JSON'; message='JSON không hợp lệ.'; }
  else if(err.type==='entity.too.large') { status=413; code='BODY_TOO_LARGE'; message='Nội dung yêu cầu quá lớn.'; }
  else if(['ECONNREFUSED','ECONNRESET','ETIMEDOUT','PROTOCOL_CONNECTION_LOST','ER_CON_COUNT_ERROR'].includes(err.code)) {status=503;code='DATABASE_UNAVAILABLE';message='Database chưa sẵn sàng. Vui lòng thử lại.';}
  if(status===500) console.error(JSON.stringify({requestId:res.locals.requestId,code:err.code||'UNEXPECTED',message:err.message}));
  res.status(status).json({error:{code,message},requestId:res.locals.requestId});
 });
}
