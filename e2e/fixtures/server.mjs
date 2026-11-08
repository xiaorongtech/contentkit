import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const dir = dirname(fileURLToPath(import.meta.url));
const port = Number(process.env.PORT || 8901);
http.createServer(async (req, res) => {
  const body = await readFile(join(dir, 'compose.html'));
  res.writeHead(200, {'content-type': 'text/html; charset=utf-8'});
  res.end(body);
}).listen(port, '127.0.0.1', () => console.log(`fixture http://127.0.0.1:${port}/`));
