import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const apiUrl = (process.env.REVA_API_URL ?? '').replace(/\/$/, '');

if (!apiUrl.startsWith('https://')) {
  throw new Error('REVA_API_URL debe ser una URL HTTPS del backend, por ejemplo https://reva-api.onrender.com');
}

const indexPath = resolve('dist/reva-frontend/browser/index.html');
const index = await readFile(indexPath, 'utf8');
const actualizado = index.replace('__REVA_API_URL__', apiUrl);

if (actualizado === index) {
  throw new Error('No se encontró el marcador de URL de API en el HTML generado.');
}

await writeFile(indexPath, actualizado, 'utf8');
console.log(`Frontend configurado para ${apiUrl}`);
