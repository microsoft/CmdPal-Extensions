import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const astroRoot = join(root, 'node_modules', 'astro');
const astroPackage = JSON.parse(readFileSync(join(astroRoot, 'package.json'), 'utf8'));
const astroCli = join(astroRoot, astroPackage.bin.astro);
const child = spawn(process.execPath, [astroCli, ...process.argv.slice(2)], {
  cwd: root,
  env: { ...process.env, ASTRO_TELEMETRY_DISABLED: '1' },
  stdio: 'inherit',
});

child.on('exit', (code) => process.exit(code ?? 1));
