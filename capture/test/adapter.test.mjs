import assert from 'node:assert/strict';
import { once } from 'node:events';
import { EventEmitter } from 'node:events';
import { mkdtemp, readdir, readFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { WebSocketServer } from 'ws';
import { connectAdapter, decodeReplay, encodeReplay, runBlender, scenarios, validateRecipe } from '../adapter.mjs';

const recipe = { format: 'blender-lab-recipe-v1', lab: 'BL-001', value: 1.25 };

test('six supported recipes, numeric parameter validation and digest verification', async () => {
  assert.equal(scenarios.length, 6);
  for (const lab of scenarios) assert.equal(validateRecipe({ ...recipe, lab: lab.id.toUpperCase() }).lab, lab.id.toUpperCase());
  for (const value of [NaN, Infinity, '1', 0, 2.1, 4]) assert.throws(() => validateRecipe({ ...recipe, value }));
  for (const value of [0.1, 2]) assert.equal(validateRecipe({ ...recipe, value }).value, value);
  assert.equal(scenarios.every(s => s.parameters.value.maximum === 2), true);
  assert.throws(() => validateRecipe({ ...recipe, lab: '../not-a-lab' }));
  assert.deepEqual(await decodeReplay(encodeReplay(recipe)), recipe);
  await assert.rejects(decodeReplay({ ...encodeReplay(recipe), sha256: '0'.repeat(64) }));
  await assert.rejects(decodeReplay({ kind: 'file', path: '/tmp/other' }));
  assert.throws(() => connectAdapter({ endpoint: 'ws://example.com:47100', token: 'a'.repeat(32) }));
});

test('Blender runner rejects invalid recipes and already cancelled work before launch', async () => {
  let launches = 0;
  const spawnProcess = () => { launches++; throw new Error('Should not launch'); };
  await assert.rejects(runBlender({ ...recipe, value: 2.1 }, { spawnProcess }), /0.1 to 2/);
  await assert.rejects(runBlender({ ...recipe, lab: '../escape' }, { spawnProcess }), /supported/);
  const abort = new AbortController(); abort.abort();
  await assert.rejects(runBlender(recipe, { signal: abort.signal, spawnProcess }));
  assert.equal(launches, 0);
});

test('Blender cancellation waits for process close and writes its final output', async t => {
  const outputRoot = await mkdtemp(path.join(os.tmpdir(), 'blender-lab-cappy-test-'));
  t.after(() => rm(outputRoot, { recursive: true, force: true }));
  const child = new EventEmitter(); child.stdout = new EventEmitter(); child.stderr = new EventEmitter();
  const abort = new AbortController();
  let killed = false, settled = false;
  child.kill = () => { killed = true; return true; };
  const launched = new Promise(resolve => { child.launched = resolve; });
  const task = runBlender(recipe, { outputRoot, signal: abort.signal, spawnProcess: () => { child.launched(); return child; } });
  task.then(() => { settled = true; }, () => { settled = true; });
  await launched;
  abort.abort();
  assert.equal(killed, true);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(settled, false);
  child.stdout.emit('data', Buffer.from('Final Blender output\n'));
  child.emit('close', null, 'SIGTERM');
  await assert.rejects(task, /cancelled/);
  const [id] = await readdir(path.join(outputRoot, recipe.lab));
  assert.equal(await readFile(path.join(outputRoot, recipe.lab, id, 'blender.log'), 'utf8'), 'Final Blender output\n');
});

test('Blender timeout requests termination and rejects after process close', async t => {
  const outputRoot = await mkdtemp(path.join(os.tmpdir(), 'blender-lab-cappy-timeout-'));
  t.after(() => rm(outputRoot, { recursive: true, force: true }));
  const child = new EventEmitter(); child.stdout = new EventEmitter(); child.stderr = new EventEmitter();
  let kills = 0;
  child.kill = () => { kills++; setImmediate(() => child.emit('close', null, 'SIGTERM')); return true; };
  await assert.rejects(runBlender(recipe, { outputRoot, timeoutMs: 10, spawnProcess: () => child }), /exceeded/);
  assert.equal(kills, 1);
});

async function fixture(t, runner) {
  const server = new WebSocketServer({ host: '127.0.0.1', port: 0 });
  await once(server, 'listening');
  const socket = connectAdapter({ endpoint: `ws://127.0.0.1:${server.address().port}`, token: 't'.repeat(32), runner });
  const [peer] = await once(server, 'connection');
  const messages = [], waiters = [];
  peer.on('message', bytes => {
    const message = JSON.parse(bytes.toString());
    messages.push(message);
    for (const waiter of [...waiters]) if (waiter.match(message)) { waiters.splice(waiters.indexOf(waiter), 1); clearTimeout(waiter.timer); waiter.resolve(message); }
  });
  const wait = match => {
    const prior = messages.find(match);
    if (prior) return Promise.resolve(prior);
    return new Promise((resolve, reject) => {
      const waiter = { match, resolve, timer: undefined };
      waiter.timer = setTimeout(() => { waiters.splice(waiters.indexOf(waiter), 1); reject(new Error(`Timed out; received ${messages.map(m => m.type).join(', ')}`)); }, 3000);
      waiters.push(waiter);
    });
  };
  const send = message => peer.send(JSON.stringify(message));
  t.after(async () => { socket.close(); await once(peer, 'close'); await new Promise(resolve => server.close(resolve)); });
  const hello = await wait(m => m.type === 'hello');
  assert.equal(hello.token, 't'.repeat(32));
  assert.deepEqual(hello.capabilities, ['scenarios', 'freeform_recording', 'replay']);
  send({ type: 'welcome', protocol: 1, controller: { name: 'test', version: '0.1.0' } });
  return { send, wait, messages };
}

test('immediate post-welcome preparation, heartbeat, scenario and hashed replay', async t => {
  const recipes = [];
  const { send, wait } = await fixture(t, async received => { recipes.push(received); return { output: 'test-only', evidence: { lab: received.lab, passed: true } }; });
  send({ type: 'prepare_scenario', op: 'op1', scenario: recipe.lab.toLowerCase(), parameters: { value: recipe.value } });
  await wait(m => m.type === 'ready' && m.op === 'op1');
  send({ type: 'ping', nonce: 'alive' });
  await wait(m => m.type === 'pong' && m.nonce === 'alive');
  send({ type: 'start', op: 'op1' });
  const completed = await wait(m => m.type === 'completed' && m.op === 'op1');
  assert.deepEqual(await decodeReplay(completed.replay), recipe);
  assert.equal(completed.result.captured, false);
  send({ type: 'prepare_replay', op: 'op2', replay: completed.replay });
  await wait(m => m.type === 'ready' && m.op === 'op2');
  send({ type: 'start', op: 'op2' });
  await wait(m => m.type === 'completed' && m.op === 'op2');
  assert.deepEqual(recipes, [recipe, recipe]);
});

test('unknown parameter and failed Blender runner cannot count as success', async t => {
  const { send, wait, messages } = await fixture(t, async () => { throw new Error('Blender check failed'); });
  send({ type: 'prepare_scenario', op: 'bad', scenario: 'bl-001', parameters: { secretPath: 'no' } });
  const rejected = await wait(m => m.type === 'failed' && m.op === 'bad');
  assert.equal(rejected.code, 'INVALID_PARAMETERS');
  send({ type: 'prepare_scenario', op: 'fail', scenario: 'bl-001', parameters: {} });
  await wait(m => m.type === 'ready' && m.op === 'fail');
  send({ type: 'start', op: 'fail' });
  assert.equal((await wait(m => m.type === 'failed' && m.op === 'fail')).code, 'BLENDER_SCENARIO_FAILED');
  assert.equal(messages.some(m => m.type === 'completed'), false);
});

test('scripted recording completes with recipe and cancellation suppresses completion', async t => {
  let resolve;
  const { send, wait, messages } = await fixture(t, () => new Promise(done => { resolve = done; }));
  send({ type: 'record_start', op: 'record' });
  await wait(m => m.type === 'started' && m.op === 'record');
  resolve({ output: 'test-only', evidence: { passed: true } });
  const recording = await wait(m => m.type === 'completed' && m.op === 'record');
  assert.equal((await decodeReplay(recording.replay)).lab, 'BL-001');
  send({ type: 'prepare_scenario', op: 'cancelled', scenario: 'bl-002', parameters: {} });
  await wait(m => m.type === 'ready' && m.op === 'cancelled');
  send({ type: 'start', op: 'cancelled' });
  await wait(m => m.type === 'started' && m.op === 'cancelled');
  send({ type: 'cancel', op: 'cancelled' });
  send({ type: 'ping', nonce: 'after-cancel' });
  await wait(m => m.type === 'pong' && m.nonce === 'after-cancel');
  resolve({ output: 'test-only', evidence: { passed: true } });
  await new Promise(done => setTimeout(done, 20));
  assert.equal(messages.some(m => m.type === 'completed' && m.op === 'cancelled'), false);
});
