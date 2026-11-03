# Source inspection — ScriptHammer

Ngày đọc 03/11/2026. Commit `a2dd31ae25ea30c678d990432c7e2b60b4faeda7`; working tree sạch. Chỉ đọc source, không build/start/test ứng dụng. SHA-256 tính toàn bộ bytes; trích đoạn giữ số dòng gốc.

Package manager `pnpm@10.16.1`, package version `0.0.1`.

Phiên bản khai báo: `{"@supabase/ssr": "^0.12.7", "@supabase/supabase-js": "^2.117.2", "next": "15.5.9", "react": "19.1.0"}`. Đây là package.json, không phải xác nhận version runtime.

## `LICENSE`

SHA-256: `f69d5a9022505a239e772f1d1c1a8bc322861b0be7284a0f7821d7421a76082d`.

```text
1: MIT License
2:
3: Copyright (c) 2025 Jonathan Pohlner and ScriptHammer contributors
4:
5: Permission is hereby granted, free of charge, to any person obtaining a copy
6: of this software and associated documentation files (the "Software"), to deal
7: in the Software without restriction, including without limitation the rights
8: to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
9: copies of the Software, and to permit persons to whom the Software is
10: furnished to do so, subject to the following conditions:
11:
12: The above copyright notice and this permission notice shall be included in all
13: copies or substantial portions of the Software.
14:
15: THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
16: IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
17: FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
18: AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
19: LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
20: OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
21: SOFTWARE.
```

## `package.json`

SHA-256: `7b81eb8f28135d254745037d6dcc2913b168b627b70b0dd0ee4bf5759977c006`.

```text
50:     "generate:sitemap": "node scripts/generate-sitemap.js",
51:     "generate:rss": "node scripts/generate-rss.js",
52:     "sync:wireframes": "bash scripts/sync-wireframes.sh",
53:     "sync:cesium": "bash scripts/sync-cesium.sh",
54:     "prebuild": "node scripts/detect-project.js && node scripts/generate-author-config.js && node scripts/generate-manifest.js && node scripts/generate-sitemap.js && node scripts/generate-rss.js && bash scripts/sync-wireframes.sh && bash scripts/sync-cesium.sh",
55:     "build": "NODE_ENV=production next build && node scripts/strip-css-script-tags.mjs && node scripts/stamp-sw-version.mjs",
56:     "start": "next start",
57:     "lint": "eslint",
```

```text
77:     "analyze": "ANALYZE=true pnpm run build",
78:     "migrate:components": "node scripts/migrate-components.js",
79:     "validate:structure": "node scripts/validate-structure.js --strict",
80:     "generate:component": "plop component",
81:     "generate:blog": "node scripts/generate-blog-data.js",
82:     "generate:icons": "node scripts/generate-icons.js",
83:     "check:icons": "node scripts/generate-icons.js --check",
```

## `next.config.ts`

SHA-256: `ea94a8da9df20b8ad7640e69854b7f2e50b8ab10c0deb4e70a5f71a3cb395056`.

```text
40: const basePath = detectProjectConfig();
41:
42: const nextConfig: NextConfig = {
43:   output: 'export',
44:   basePath: basePath,
45:   assetPrefix: basePath ? `${basePath}/` : '',
46:   trailingSlash: true,
47:   images: {
48:     unoptimized: true,
49:   },
50:   // Overridable so a build can put its output somewhere other than .next.
51:   // ONE live caller: scripts/serve-basepath.sh sets NEXT_DIST_DIR=out-basepath
52:   // so the basePath-prefixed export (#157) lands ready to symlink-serve —
53:   // under `output: 'export'` Next 15.5 replaces the distDir with the finished
54:   // static site and never creates out/, so distDir IS the export dir.
55:   //
56:   // It is NOT the answer to "a build racing the dev server". That was
57:   // scripts/e2e-live-acceptance.sh's use, and an isolated distDir did not stop
58:   // the corruption — six failures in two days (#508). Builds belong in the
59:   // `builder` service, which has its own .next volume and no dev server in it.
60:   // If you are reaching for this to dodge a race, reach for that instead.
61:   distDir: process.env.NEXT_DIST_DIR || '.next',
62:   cleanDistDir: true,
63:   env: {
64:     NEXT_PUBLIC_PAGESPEED_API_KEY: process.env.NEXT_PUBLIC_PAGESPEED_API_KEY,
65:     // Deploy workflows omit NEXT_PUBLIC_BASE_PATH and rely on detect-project.js,
66:     // so the resolved basePath must be injected here or client code that builds
67:     // URLs (auth redirects) sees '' in production (issue #154).
68:     NEXT_PUBLIC_BASE_PATH: basePath,
69:   },
70:   webpack: (config, { isServer, dev }) => {
71:     // Emit which MODULES ended up in which chunk, so the first-load gate can ask
72:     // the build a question instead of grepping minified output for a class name.
73:     //
```

## `scripts/generate-blog-data.js`

SHA-256: `384530bbb02b0c2f49e726c564b9cf119e9d77a71ccf8e3bb2d83a0f3566643d`.

```text
7:
8: const fs = require('fs').promises;
9: const path = require('path');
10: const matter = require('gray-matter');
11: const crypto = require('crypto');
12:
13: const BLOG_DIR = path.join(process.cwd(), 'public', 'blog');
14: const OUTPUT_DIR = path.join(process.cwd(), 'src', 'lib', 'blog');
15: const OUTPUT_FILE = path.join(OUTPUT_DIR, 'blog-data.json');
16:
17: /**
```

```text
94: async function processMarkdownFile(filePath) {
95:   const content = await fs.readFile(filePath, 'utf-8');
96:   const { data: frontMatter, content: markdownContent } = matter(content);
97:
98:   const fileName = path.basename(filePath, '.md');
99:   const title = frontMatter.title || fileName;
100:   const slug = frontMatter.slug || generateSlug(title);
101:   const publishedAt = normalizeFrontMatterDate(
102:     frontMatter.date,
103:     'date',
104:     filePath
105:   );
106:   const updatedAt = normalizeFrontMatterDate(
107:     frontMatter.updatedAt || frontMatter.date,
108:     frontMatter.updatedAt ? 'updatedAt' : 'date',
109:     filePath
110:   );
111:   const excerpt = frontMatter.excerpt || extractExcerpt(markdownContent);
112:   const wordCount = markdownContent.trim().split(/\s+/).length;
113:   const readingTime = calculateReadingTime(markdownContent);
114:
115:   return {
116:     id: generateId(slug, publishedAt),
117:     slug,
118:     title,
119:     content: markdownContent,
120:     excerpt,
121:     publishedAt,
122:     updatedAt,
123:     status: frontMatter.draft ? 'draft' : 'published',
124:     author: {
125:       id: frontMatter.authorId || 'default',
126:       name: frontMatter.author || 'Anonymous',
127:       avatar: frontMatter.authorAvatar,
```

```text
222:     console.log('💡 Add .md files to public/blog/ directory');
223:     return;
224:   }
225:
226:   console.log(`📚 Found ${markdownFiles.length} markdown files`);
227:
228:   // Process all markdown files
229:   const posts = [];
230:   for (const file of markdownFiles) {
231:     const filePath = path.join(blogDir, file);
232:     const post = await processMarkdownFile(filePath);
233:
234:     posts.push(post);
235:     console.log(`✅ Processed: ${file}`);
236:   }
237:
238:   // Sort posts by date (newest first), then slug as a deterministic tie-breaker.
239:   posts.sort(
240:     (a, b) =>
```

## `src/app/blog/page.tsx`

SHA-256: `79d88aed900ba4e882be5c304b4d52ba6bdc688b4ee837a2ba79de641f50ed12`.

```text
10: const logger = createLogger('app:blog:page');
11:
12: async function getPosts(
13:   page = 1,
14:   pageSize = 12
15: ): Promise<BlogPostListResponse> {
16:   try {
17:     // Read directly from generated JSON for static export
18:     const jsonPath = path.join(process.cwd(), 'src/lib/blog/blog-data.json');
19:     const jsonData = await fs.readFile(jsonPath, 'utf-8');
20:     const data = JSON.parse(jsonData);
21:
22:     // Filter published posts
23:     const posts = (data.posts || []).filter(
24:       (p: any) => p.status === 'published'
25:     );
26:
27:     // Calculate pagination
28:     const total = posts.length;
29:     const offset = (page - 1) * pageSize;
30:     const paginatedPosts = posts.slice(offset, offset + pageSize);
31:
32:     // Transform to match BlogPost type
33:     const transformedPosts = paginatedPosts.map((p: any) => ({
34:       ...p,
35:       version: 1,
```

## `src/app/blog/[slug]/page.tsx`

SHA-256: `d66d208cff75e7ab5342066e553a1606795987e2dfd4fafc38e7abfd7d862837`.

```text
40: }
41:
42: async function getPost(slug: string): Promise<BlogPost | null> {
43:   try {
44:     // Read directly from generated JSON for static export
45:     const jsonPath = path.join(process.cwd(), 'src/lib/blog/blog-data.json');
46:     const jsonData = await fs.readFile(jsonPath, 'utf-8');
47:     const data = JSON.parse(jsonData);
48:     const posts = data.posts || [];
49:
50:     // Find by slug
51:     const post = posts.find((p: any) => p.slug === slug);
52:
53:     return post || null;
```

```text
170:
171:   if (!post) {
172:     notFound();
173:   }
174:
175:   // Process markdown content
176:   const processed = markdownProcessor.process(post.content);
177:   const toc = tocGenerator.generate(post.content);
178:
179:   // Get SEO score
180:   const seoAnalysis = seoAnalyzer.analyze(post);
181:   const seoScore = seoAnalysis.score.overall;
```

```text
253: export async function generateStaticParams() {
254:   try {
255:     const jsonPath = path.join(process.cwd(), 'src/lib/blog/blog-data.json');
256:     const jsonData = await fs.readFile(jsonPath, 'utf-8');
257:     const data = JSON.parse(jsonData);
258:     const posts = data.posts || [];
259:
260:     return posts.map((post: any) => ({
261:       slug: post.slug,
262:     }));
263:   } catch (error) {
264:     logger.error('Error generating static params', { error });
265:     return [];
266:   }
267: }
268:
```

## `src/lib/blog/markdown-processor.ts`

SHA-256: `23148f76a7220ecd13463f6c2312fc0adceedfd1785bc79fe1ef77a89c1377c9`.

```text
34:   }
35:
36:   /**
37:    * Process markdown content and extract metadata
38:    */
39:   process(markdown: string): ProcessedContent {
40:     // Parse frontmatter
41:     const { data: frontMatter, content } = matter(markdown);
42:
43:     // Extract metadata
44:     const toc = this.options.enableToc ? this.extractTOC(content) : [];
45:     const images = this.extractImages(content);
46:     const links = this.extractLinks(content);
47:     const codeBlocks = this.extractCodeBlocks(content);
48:
49:     // Calculate reading time and word count
50:     const wordCount = this.calculateWordCount(content);
51:     const readingTime = Math.ceil(wordCount / 200); // Assume 200 words per minute
52:
53:     // Generate excerpt if not provided
54:     const excerpt = frontMatter.excerpt || this.generateExcerpt(content);
55:
56:     // Process markdown to HTML
57:     const html = this.renderMarkdown(content);
58:
59:     return {
60:       html,
61:       toc,
62:       metadata: {
```

## `.github/workflows/deploy.yml`

SHA-256: `4c95cbcbcb5f8d685da9694190f4e2884202545a9c45c39d9f4be12c6484240f`.

```text
64:         env:
65:           # (#917) Search Console ownership token. Rendered as a <meta> tag for anyone to
66:           # read, so it is a var. Without this line the tag is skipped and verification
67:           # never ships, with no error anywhere.
68:           NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION: ${{ vars.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION }}
69:           NEXT_PUBLIC_PAGESPEED_API_KEY: ${{ secrets.NEXT_PUBLIC_PAGESPEED_API_KEY }}
70:
71:       - name: Build Next.js app
72:         run: pnpm run build
73:         env:
74:           NEXT_PUBLIC_AUTHOR_AVATAR: ${{ vars.NEXT_PUBLIC_AUTHOR_AVATAR }}
```

```text
174:
175:       - name: Add cache busting and merge outputs
176:         run: |
177:           # Create merged output directory
178:           mkdir -p merged-output
179:
180:           # Check if Next.js build output exists and copy it
181:           if [ -d "out" ]; then
182:             echo "Copying Next.js build from 'out' directory..."
183:             cp -r out/* merged-output/
184:           else
185:             echo "Warning: 'out' directory not found. The Next.js build may have failed."
186:             # Create a minimal index.html to prevent complete failure
187:             echo "<html><body><h1>Build Error</h1><p>The Next.js build did not complete successfully.</p></body></html>" > merged-output/index.html
188:           fi
189:
190:           # Check if Storybook build exists and copy it
191:           if [ -d "storybook-static" ]; then
192:             echo "Copying Storybook build..."
193:             cp -r storybook-static merged-output/storybook
194:             # Add build timestamp to force cache refresh
```

```text
321:           # ~300-500 small files against a 131-page export (17 files bought the old
322:           # 5 generations, ~100 bought 30). RETAIN_MAX_FILES backstops a runaway.
323:           #
324:           # `check-retained-assets.mjs` in smoke.yml FAILS if the live window is
325:           # narrower than this. That assertion is the part that was missing — nothing
326:           # ever compared the promise against its intended width.
327:           #
328:           # This is a MITIGATION. The recovery that does not depend on any number is
329:           # the self-heal in src/app/layout.tsx; the actual fix is #635 — a CDN
330:           # serving HTML `no-cache`, which GitHub Pages cannot be configured to do.
331:           RETAIN_DAYS: '14'
332:
333:       - name: Upload artifact
334:         uses: actions/upload-pages-artifact@v3
335:         with:
336:           path: ./merged-output
337:
338:   deploy:
339:     environment:
340:       name: github-pages
341:       url: ${{ steps.deployment.outputs.page_url }}
342:     runs-on: ubuntu-latest
343:     # Cap: observed max 1.9 min. Uncapped, a hung job runs to the 360-minute default (#1119).
344:     timeout-minutes: 10
345:     needs: build-and-deploy
346:     steps:
347:       - name: Deploy to GitHub Pages
348:         id: deployment
349:         uses: actions/deploy-pages@v5
```

## `src/lib/supabase/client.ts`

SHA-256: `dd1ecf97f3fd7c14a4e1df18b174eed1d042fac12e0bfbc309449cf542f3bd59`.

```text
1: /**
2:  * Supabase Client for Browser (Client-side)
3:  *
4:  * Creates a Supabase client for use in browser/client components.
5:  * Sign-in links use PKCE, whose code exchange is a request from the browser, so
6:  * the static export needs no server for it (#1255).
7:  *
8:  * @module lib/supabase/client
9:  */
10:
11: import { createClient as createSupabaseClient } from '@supabase/supabase-js';
12: import type { Database } from '@/lib/supabase/types';
13: import type { SupabaseClient } from '@supabase/supabase-js';
14: import { shouldDetectSessionInUrl } from '@/lib/auth/url-session';
15:
16: /**
17:  * Creates a disabled mock client for when Supabase is not configured.
18:  * Returns a client that won't crash but all operations return errors.
19:  */
20: function createDisabledClient(): SupabaseClient<Database> {
21:   const notConfiguredError = {
22:     message: 'Supabase not configured',
23:     status: 503,
24:   };
25:
26:   const errorResponse = Promise.resolve({
27:     data: null,
28:     error: notConfiguredError,
29:   });
30:
31:   const chainableMock = () => ({
32:     select: chainableMock,
33:     eq: chainableMock,
34:     neq: chainableMock,
35:     in: chainableMock,
36:     order: chainableMock,
37:     limit: chainableMock,
38:     range: chainableMock,
39:     single: () => errorResponse,
40:     maybeSingle: () => errorResponse,
41:     insert: chainableMock,
42:     update: chainableMock,
```

## `public/sw.js`

SHA-256: `02e2732313eb60cd09467c2be8a2a850cbbacb44f773f58c148dbf45612b02e1`.

```text
30: // second copy instead of re-synchronising it.
31: const CACHE_VERSION = 'scripthammer-v1.0.0';
32:
33: // The brand segment, e.g. `scripthammer-`. Strips the `-v<semver>` tail and anything
34: // the stamp script appends after it, so it holds for the authored
35: // `scripthammer-v1.0.0` and a stamped `scripthammer-v0.0.1-<sha>` alike.
36: const CACHE_PREFIX = CACHE_VERSION.replace(/-v[\d.].*$/, '') + '-';
37: const STATIC_CACHE = `${CACHE_VERSION}-static`;
38: const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
39:
40: // Images are versioned SEPARATELY from the build, and that is the whole point
41: // (#438).
42: //
43: // This used to be `${CACHE_VERSION}-images`. Because CACHE_VERSION is stamped
44: // with the commit SHA, every deploy renamed it and `activate` deleted the
45: // previous one — throwing away every cached image on a code change that had
46: // nothing to do with images. Combined with `skipWaiting()` + `clients.claim()`
47: // below, an open page had its image cache deleted mid-session and was then
48: // claimed by the new worker, so its not-yet-requested lazy images all faulted
```

## `docker-compose.yml`

SHA-256: `7886966cc1bbc909c0360ed52f56e1b112f8d68635cab5276a984b6763e54ee6`.

```text
59:     # Discover where you landed:
60:     #   docker compose port scripthammer 3000   → 127.0.0.1:49171 (or wherever)
61:     ports:
62:       - '127.0.0.1:${SH_PORT:-0}:3000'
63:       - '127.0.0.1:${SH_STORYBOOK_PORT:-0}:6006'
64:       - '127.0.0.1:${SH_HMR_PORT:-0}:24678'
65:     # Lets in-container Chromium (Playwright) reach the HOST's published local
66:     # Supabase Kong port via http://host.docker.internal:54321 when using
67:     # `pnpm run use:local`. Docker Desktop/WSL provide this automatically;
```

```text
138:     profiles: ['build']
139:     # PID1 init (#275 SIGNAL_HANDLING). Compose's `init: true` is the
140:     # `docker run --init` route the audit named as the alternative to adding
141:     # tini to the Dockerfile. One-shot service, but without it a Ctrl-C
142:     # mid-build orphans the child processes `pnpm build` spawned.
143:     init: true
144:     build:
145:       context: .
146:       dockerfile: docker/Dockerfile
147:       target: dev
148:     volumes:
149:       - .:/app
150:       - node_modules:/app/node_modules
151:       # NOT next_cache — that volume is the dev server's. This is the whole
152:       # point of the service. /app/.next is pre-created node-owned in the image
153:       # (docker/Dockerfile, the chown -R node:node step), so this volume
154:       # inherits that ownership.
155:       - builder_next:/app/.next
156:     env_file:
157:       - .env
158:     environment:
```
