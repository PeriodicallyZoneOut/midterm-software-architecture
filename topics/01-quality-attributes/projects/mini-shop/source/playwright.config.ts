import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests',testMatch:'browser.spec.ts',workers:1,timeout:30000,use:{baseURL:process.env.BASE_URL||'http://127.0.0.1:8080',headless:true,launchOptions:{executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']},screenshot:'only-on-failure'},reporter:[['list'],['html',{open:'never'}]]});
