import mysql from 'mysql2/promise';
export const pool = mysql.createPool({host:process.env.DB_HOST||'127.0.0.1',port:Number(process.env.DB_PORT||3306),user:process.env.DB_USER,password:process.env.DB_PASSWORD,database:process.env.DB_NAME,connectionLimit:5,connectTimeout:2000,decimalNumbers:true,timezone:'Z',charset:'utf8mb4'});
export async function bootstrap(migrate:()=>Promise<void>) {
 for(let attempt=1;attempt<=30;attempt++) {
  try {await pool.query('SELECT 1'); await migrate(); return;}
  catch(e) { if(attempt===30) throw e; console.log(JSON.stringify({event:'database_retry',attempt})); await new Promise(r=>setTimeout(r,2000)); }
 }
}
