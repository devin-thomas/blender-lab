import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const scenarios = [
  ['BL-001', 'Mesh modelling'], ['BL-002', 'Pixel UV and vertex colour'],
  ['BL-003', 'Geometry nodes'], ['BL-004', 'Keyframe animation'],
  ['BL-005', 'Rigid body simulation'], ['BL-006', 'glTF roundtrip'],
  ['BL-007', 'Modular environment kit'], ['BL-008', 'Vertex shade composition'],
  ['BL-009', 'Gradient-card atmosphere'],
  ['BL-010', 'Rig and deformation desk'],
  ['BL-011', 'Action and NLA bench'],
  ['BL-012', 'Camera and staging lab'],
  ['BL-013', 'Geometry Nodes scatter'],
  ['BL-014', 'Geometry Nodes field inspector'],
  ['BL-015', 'UV and texel audit'],
  ['BL-019', 'Compositor bench'],
  ['BL-020', 'Lighting observatory'],
  ['BL-021', 'Asset-browser kit'],
  ['BL-022', 'Sprite-sheet camera'],
  ['BL-025', 'Topology surgery'],
  ['BL-026', 'Boolean assembly'],
  ['BL-027', 'Retopology projection desk'],
  ['BL-028', 'Mesh attribute contracts'],
  ['BL-029', 'Shape-key expression desk'],
  ['BL-030', 'Curve path and profile forge'],
  ['BL-031', 'Typography geometry desk'],
].map(([id, name]) => ({ id: id.toLowerCase(), name, parameters: { value: { type: 'number', minimum: 0.1, maximum: 2, default: 1 } }, requiredCapabilities: ['scenarios'] }));

export function validateRecipe(recipe) {
  if (!recipe || recipe.format !== 'blender-lab-recipe-v1' || !scenarios.some(s => s.id.toUpperCase() === recipe.lab)) {
    throw new Error('Replay must contain a supported Blender Lab recipe');
  }
  if (typeof recipe.value !== 'number' || !Number.isFinite(recipe.value) || recipe.value < 0.1 || recipe.value > 2) {
    throw new Error('value must be a finite number from 0.1 to 2');
  }
  return { format: recipe.format, lab: recipe.lab, value: recipe.value };
}

export async function decodeReplay(handoff) {
  if (handoff.kind !== 'inline' || handoff.encoding !== 'base64' || handoff.format !== 'blender-lab-recipe-v1') {
    throw new Error('Only inline Blender Lab recipe replays are supported');
  }
  const bytes = Buffer.from(handoff.data, 'base64');
  if (bytes.length > 1024 * 1024 || createHash('sha256').update(bytes).digest('hex') !== handoff.sha256) {
    throw new Error('Replay payload digest or size is invalid');
  }
  return validateRecipe(JSON.parse(bytes.toString('utf8')));
}

export function encodeReplay(recipe) {
  const bytes = Buffer.from(JSON.stringify(validateRecipe(recipe)));
  return { kind: 'inline', encoding: 'base64', data: bytes.toString('base64'), sha256: createHash('sha256').update(bytes).digest('hex'), format: recipe.format };
}

export async function runBlender(recipe, { outputRoot, signal, executable = process.env.BLENDER_BIN || 'blender', timeoutMs = 120_000, spawnProcess = spawn } = {}) {
  recipe = validateRecipe(recipe);
  signal?.throwIfAborted();
  if (typeof executable !== 'string' || !executable.trim()) throw new Error('BLENDER_BIN must name an executable');
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) throw new Error('Blender timeout must be positive');
  const output = path.join(outputRoot || path.join(root, 'build', 'cappy'), recipe.lab, crypto.randomUUID());
  await mkdir(output, { recursive: true });
  signal?.throwIfAborted();
  const args = ['--background', '--factory-startup', '--disable-autoexec', '--python-exit-code', '1', '--python', path.join(root, 'scripts', 'entry.py'), '--', '--action', 'scenario', '--lab', recipe.lab, '--output', output, '--value', String(recipe.value)];
  const child = spawnProcess(executable, args, { cwd: root, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
  const log = [];
  child.stdout.on('data', chunk => log.push(chunk));
  child.stderr.on('data', chunk => log.push(chunk));
  let timer;
  let forceTimer;
  let abort;
  try {
    await new Promise((resolve, reject) => {
      let failure;
      const terminate = error => {
        if (failure) return;
        failure = error;
        child.kill();
        forceTimer = setTimeout(() => child.kill('SIGKILL'), 2000);
      };
      abort = () => terminate(new Error('Blender scenario cancelled'));
      signal?.addEventListener('abort', abort, { once: true });
      timer = setTimeout(() => terminate(new Error(`Blender scenario exceeded ${timeoutMs / 1000} seconds`)), timeoutMs);
      child.once('error', error => { failure ||= error; });
      // Wait for process exit and closed output pipes before publishing its log.
      child.once('close', (code, killedBy) => failure ? reject(failure) : code === 0 ? resolve() : reject(new Error(`Blender failed (exit ${code}, signal ${killedBy}); see ${output}/blender.log`)));
      if (signal?.aborted) abort();
    });
    const evidence = JSON.parse(await readFile(path.join(output, 'evidence.json'), 'utf8'));
    if (evidence.labs?.length !== 1 || evidence.labs[0].id !== recipe.lab || evidence.labs[0].status !== 'passed' || evidence.labs[0].value !== recipe.value) throw new Error('Blender evidence did not confirm this lab and parameter passed');
    return { output, evidence };
  } finally {
    clearTimeout(timer);
    clearTimeout(forceTimer);
    signal?.removeEventListener('abort', abort);
    await writeFile(path.join(output, 'blender.log'), Buffer.concat(log));
  }
}

export function connectAdapter({ endpoint, token, runner = runBlender, recordingLab = process.env.BLENDER_LAB_SCENARIO || 'BL-001', recordingValue = Number(process.env.BLENDER_LAB_VALUE || 1) }) {
  const url = new URL(endpoint);
  if (url.protocol !== 'ws:' || !['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname) || url.username || url.password) throw new Error('Cappy endpoint must be a loopback ws:// URL');
  if (typeof token !== 'string' || token.length < 16) throw new Error('CAPPY_SESSION_TOKEN is required');
  const socket = new WebSocket(endpoint);
  let active;
  let welcomed = false;
  const send = message => { if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify(message)); };
  const fail = (op, code, error) => send({ type: 'failed', op, code, message: String(error.message || error).slice(0, 2000) });
  const clear = () => { active?.abort.abort(); active = undefined; };
  const execute = async operation => {
    send({ type: 'started', op: operation.op });
    const start = performance.now();
    send({ type: 'event', op: operation.op, t: 0, event: 'SCENARIO_STARTED', payload: operation.recipe });
    try {
      const result = await runner(operation.recipe, { signal: operation.abort.signal });
      if (active !== operation) return;
      send({ type: 'event', op: operation.op, t: performance.now() - start, event: 'SCENARIO_VERIFIED', payload: { lab: operation.recipe.lab, value: operation.recipe.value } });
      send({ type: 'completed', op: operation.op, result: { lab: operation.recipe.lab, value: operation.recipe.value, evidence: result.evidence, output: result.output, captured: false }, replay: encodeReplay(operation.recipe) });
    } catch (error) {
      if (active === operation) fail(operation.op, 'BLENDER_SCENARIO_FAILED', error);
    } finally {
      if (active === operation) active = undefined;
    }
  };
  const prepare = (op, recipe, kind) => {
    if (active) throw new Error('An operation is already active');
    active = { op, recipe, kind, state: 'ready', abort: new AbortController() };
    send({ type: 'ready', op });
  };
  socket.addEventListener('open', () => send({ type: 'hello', protocol: { min: 1, max: 1 }, token,
    adapter: { name: 'blender-lab-cappy', version: '0.1.0' }, game: { id: 'blender-lab', name: 'Blender Lab' }, build: 'recipe-v1', capabilities: ['scenarios', 'freeform_recording', 'replay'] }));
  // Keep this listener installed before welcome; the controller can prepare immediately.
  socket.addEventListener('message', async event => {
    let message;
    try {
      if (typeof event.data !== 'string' || Buffer.byteLength(event.data) > 4 * 1024 * 1024) throw new Error('Invalid frame');
      message = JSON.parse(event.data);
      if (message.type === 'welcome') { welcomed = true; send({ type: 'scenarios', scenarios }); return; }
      if (message.type === 'reject' || message.type === 'error') { console.error(`Cappy ${message.code}: ${message.message}`); clear(); socket.close(); return; }
      if (!welcomed) throw new Error('Controller sent a request before welcome');
      if (message.type === 'ping') { send({ type: 'pong', nonce: message.nonce }); return; }
      if (message.type === 'list_scenarios') { send({ type: 'scenarios', scenarios }); return; }
      if (message.type === 'prepare_scenario') {
        if (Object.keys(message.presentation || {}).length) throw new Error('Presentation overrides are not supported by this background adapter');
        if (Object.keys(message.parameters || {}).some(key => key !== 'value')) throw new Error('Unknown scenario parameter');
        if (!scenarios.some(s => s.id === message.scenario)) throw new Error('Unknown scenario');
        prepare(message.op, validateRecipe({ format: 'blender-lab-recipe-v1', lab: message.scenario.toUpperCase(), value: message.parameters?.value ?? 1 }), 'scenario');
      } else if (message.type === 'prepare_replay') {
        if (Object.keys(message.presentation || {}).length) throw new Error('Presentation overrides are not supported');
        prepare(message.op, await decodeReplay(message.replay), 'replay');
      } else if (message.type === 'record_start') {
        if (active) throw new Error('An operation is already active');
        active = { op: message.op, recipe: validateRecipe({ format: 'blender-lab-recipe-v1', lab: recordingLab, value: recordingValue }), kind: 'record', state: 'running', abort: new AbortController() };
        void execute(active);
      } else if (message.type === 'start') {
        if (active?.op !== message.op || active.state !== 'ready') throw new Error('start requires the prepared operation');
        active.state = 'running'; void execute(active);
      } else if (message.type === 'cancel') {
        if (active?.op === message.op) clear();
      } else if (message.type === 'stop') {
        if (active?.op !== message.op || active.state !== 'running') throw new Error('stop requires a running operation');
        fail(message.op, 'EARLY_STOP', new Error('Scenario stopped before Blender verification completed')); clear();
      } else throw new Error(`Unsupported controller message: ${message.type}`);
    } catch (error) {
      if (typeof message?.op === 'string') fail(message.op, 'INVALID_PARAMETERS', error);
      else { console.error(error.message); socket.close(1008, 'invalid controller message'); }
    }
  });
  socket.addEventListener('close', clear);
  socket.addEventListener('error', () => { console.error('Cappy WebSocket connection failed'); clear(); });
  return socket;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { connectAdapter({ endpoint: process.env.CAPPY_ENDPOINT, token: process.env.CAPPY_SESSION_TOKEN }); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
