import { spawn } from 'node:child_process';
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { scenarios } from './adapter.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const cli = path.join(here, 'node_modules', '@uppercut-labs', 'cappy', 'dist', 'cappy.js');
async function command(args, env = {}) {
  const child = spawn(process.execPath, [cli, ...args, '-C', here, '--config', 'cappy.config.example.json', '--json'], {
    cwd: here, env: { ...process.env, ...env }, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true,
  });
  let stdout = '', stderr = '';
  child.stdout.on('data', chunk => { stdout += chunk; });
  child.stderr.on('data', chunk => { stderr += chunk; });
  const code = await new Promise((resolve, reject) => { child.once('error', reject); child.once('close', resolve); });
  let report;
  try { report = JSON.parse(stdout); } catch { throw new Error(`Cappy did not return JSON: ${stderr}`); }
  if (code !== 0 || !report.ok) throw new Error(`${args[0]} failed: ${JSON.stringify(report.error)}`);
  return report;
}

const report = { host: process.platform, node: process.version, cappy: '@uppercut-labs/cappy@0.1.0', captured: false, checkedAt: new Date().toISOString(), labs: [] };
const requested = process.argv.slice(2);
if (new Set(requested).size !== requested.length || requested.some(id => !scenarios.some(s => s.id === id.toLowerCase()))) {
  throw new Error('Arguments must be distinct implemented lab IDs');
}
const selected = requested.length ? scenarios.filter(s => requested.includes(s.id.toUpperCase())) : scenarios;
const listed = await command(['scenarios']);
if (listed.data.scenarios.length !== scenarios.length) throw new Error('Expected every implemented lab scenario');
for (const { id: scenarioId } of selected) {
  const id = scenarioId.toUpperCase();
  console.error(`Verifying ${id} through Cappy record and replay --no-capture`);
  const recorded = await command(['record'], { BLENDER_LAB_SCENARIO: id, BLENDER_LAB_VALUE: '1.25' });
  const session = recorded.data.session;
  if (session.status !== 'completed' || recorded.data.replayable !== true) throw new Error(`${id} did not produce a replayable completed session`);
  const replay = await command(['replay', session.id, '--no-capture']);
  if (replay.data.captured !== false || replay.data.result?.lab !== id || replay.data.result?.evidence?.labs?.[0]?.status !== 'passed') throw new Error(`${id} replay was not verified by Blender`);
  report.labs.push({ lab: id, sessionId: session.id, state: session.status, value: 1.25, events: replay.data.events.length, replayEvidence: replay.data.result.evidence });
}
await writeFile(path.join(here, 'verification.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
