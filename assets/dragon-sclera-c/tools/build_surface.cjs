#!/usr/bin/env node
/* Art-only rebuild. Requires an existing sharp installation; installs nothing. */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '..');
let sharp;
try { sharp = require('sharp'); }
catch (error) {
  const modules = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
  if (!modules) throw new Error('Use an existing sharp installation; see preview/DEPENDENCIES.md.');
  sharp = require(path.join(modules, 'sharp'));
}
const input = path.join(root, 'source/layers/01-ai-original.png');
const output = path.resolve(process.argv[2] || path.join(root, 'build/sclera-rebuilt.png'));
if (output === path.join(root, 'submission/sclera.png')) {
  throw new Error('Refusing to overwrite the selected submission. Rebuild to a separate path for comparison.');
}
async function main() {
  fs.mkdirSync(path.dirname(output), { recursive: true });
  await sharp(input).resize(480, 480, {fit:'fill', kernel:'lanczos3'})
    .removeAlpha().png().toFile(output);
  const selected = fs.readFileSync(path.join(root, 'submission/sclera.png'));
  const rebuilt = fs.readFileSync(output);
  console.log(JSON.stringify({
    output,
    sharp: sharp.versions.sharp,
    libvips: sharp.versions.vips,
    sha256: crypto.createHash('sha256').update(rebuilt).digest('hex'),
    byte_identical_to_selected: rebuilt.equals(selected)
  }, null, 2));
}
main().catch(error => { console.error(error.message); process.exitCode=1; });
