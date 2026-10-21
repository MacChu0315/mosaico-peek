#!/usr/bin/env node
'use strict';

// Independent behavioral checks for the JavaScript reference preview.
// These checks do not validate the C/GSP port, hardware, or a main-project API.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
let jsonPath = null;
for (let i = 0; i < argv.length; i += 1) {
  if (argv[i] === '--json' && argv[i + 1]) jsonPath = path.resolve(argv[++i]);
  else throw new Error('Usage: node tools/verify_preview.js [--json PATH]');
}

const THEMES = ['night_owl', 'deep_sea', 'mechanical'];
const PIXEL_BOUNDS = { night_owl: [18, 12], deep_sea: [20, 12], mechanical: [10, 8] };
const ROLES = ['IDLE', 'NOTICE', 'TRACKING', 'HOLD', 'LEAVE', 'sleeping', 'waking'];
const SCENARIOS = ['full', 'enter_target', 'enter_empty', 'enter_asleep'];
const DT = 1000 / 60;
const EPS = 1e-9;
const checks = [];
const sourceFiles = ['preview/timeline.js', 'preview/model.js'];
const sources = [];

function deny(name) {
  return function () { throw new Error(`Reference model attempted forbidden ${name}`); };
}

// The transport may use browser time. The loaded model and scenario generator may not.
const guardedMath = Object.create(Math);
Object.defineProperty(guardedMath, 'random', { value: deny('Math.random()') });
const blockedDate = deny('Date construction');
blockedDate.now = deny('Date.now()');
const sandbox = {
  Math: guardedMath,
  Date: blockedDate,
  performance: { now: deny('performance.now()') },
  setTimeout: deny('setTimeout()'),
  setInterval: deny('setInterval()'),
  requestAnimationFrame: deny('requestAnimationFrame()'),
  console: { log() {}, warn() {}, error() {} }
};
sandbox.window = sandbox;
vm.createContext(sandbox);

function check(id, name, run) {
  try {
    const details = run() || {};
    checks.push({ id, name, status: 'passed', details });
    process.stdout.write(`PASS ${id} ${name}\n`);
  } catch (error) {
    checks.push({ id, name, status: 'failed', error: error.message });
    process.stdout.write(`FAIL ${id} ${name}: ${error.message}\n`);
  }
}

function near(actual, expected, message, epsilon = EPS) {
  assert.ok(Number.isFinite(actual), `${message}: non-finite actual ${actual}`);
  assert.ok(Math.abs(actual - expected) <= epsilon,
    `${message}: expected ${expected}, received ${actual}`);
}

function plain(value) {
  return JSON.parse(JSON.stringify(value));
}

function sample(now, overrides = {}) {
  return {
    now_ms: now,
    data_valid: true,
    target_confirmed: false,
    candidate_present: false,
    target_x: 0,
    target_y: 0,
    role_state: 'IDLE',
    state_entered_ms: 0,
    ui_visible: true,
    theme: 'night_owl',
    ...overrides
  };
}

function assertFinitePose(pose, context) {
  assert.ok(pose && typeof pose === 'object', `${context}: pose missing`);
  for (const key of ['gazeX', 'gazeY', 'gazePxX', 'gazePxY', 'lid',
    'stateEnteredMs', 'phaseMs', 'nowMs']) {
    assert.ok(Number.isFinite(pose[key]), `${context}: ${key} must be finite; got ${pose[key]}`);
  }
  assert.ok(Math.abs(pose.gazeX) <= 1 + EPS, `${context}: gazeX outside [-1,1]`);
  assert.ok(Math.abs(pose.gazeY) <= 1 + EPS, `${context}: gazeY outside [-1,1]`);
  assert.ok(pose.lid >= -EPS && pose.lid <= 1 + EPS, `${context}: lid outside [0,1]`);
  assert.ok(ROLES.includes(pose.roleState), `${context}: unknown roleState ${pose.roleState}`);
  assert.equal(typeof pose.visible, 'boolean', `${context}: visible must be boolean`);
  assert.equal(typeof pose.targetUsable, 'boolean', `${context}: targetUsable must be boolean`);
  assert.ok(PIXEL_BOUNDS[pose.theme], `${context}: unknown theme ${pose.theme}`);
  const [maxX, maxY] = PIXEL_BOUNDS[pose.theme];
  assert.ok(Math.abs(pose.gazePxX) <= maxX + EPS, `${context}: horizontal asset limit exceeded`);
  assert.ok(Math.abs(pose.gazePxY) <= maxY + EPS, `${context}: vertical asset limit exceeded`);
}

// Deliberately omit input diagnostics and transition bookkeeping from visual equality.
function visibleProjection(pose) {
  const result = {};
  for (const key of ['gazeX', 'gazeY', 'gazePxX', 'gazePxY', 'lid', 'roleState',
    'stateEnteredMs', 'phaseMs', 'visible', 'nowMs', 'theme', 'fallbackMode']) {
    result[key] = pose[key];
  }
  return result;
}

function equivalentPose(a, b, context, epsilon = 0) {
  const left = visibleProjection(a);
  const right = visibleProjection(b);
  if (epsilon === 0) {
    assert.deepEqual(plain(left), plain(right), context);
    return;
  }
  for (const key of Object.keys(left)) {
    if (typeof left[key] === 'number') near(left[key], right[key], `${context}: ${key}`, epsilon);
    else assert.equal(left[key], right[key], `${context}: ${key}`);
  }
}

let model;
let timeline;
check('V00', 'load standalone modules in a clock/random/timer-guarded VM', () => {
  for (const relative of sourceFiles) {
    const bytes = fs.readFileSync(path.join(root, relative));
    sources.push({ path: relative, sha256: crypto.createHash('sha256').update(bytes).digest('hex') });
    vm.runInContext(bytes.toString('utf8'), sandbox, { filename: relative, timeout: 5000 });
  }
  model = sandbox.PreviewModel;
  timeline = sandbox.PreviewTimeline;
  assert.ok(model, 'window.PreviewModel missing');
  assert.ok(timeline, 'window.PreviewTimeline missing');
  for (const method of ['createState', 'normalizeSample', 'step', 'simulateAt', 'advanceTo', 'sampleAt']) {
    assert.equal(typeof model[method], 'function', `PreviewModel.${method} missing`);
  }
  assert.equal(typeof timeline.sampleAt, 'function', 'PreviewTimeline.sampleAt missing');
  return { exports: ['PreviewModel', 'PreviewTimeline'], dependencies: 'Node standard library only' };
});

if (model && timeline) {
  check('V01', 'unconfirmed candidates are visually equivalent to no target in all seven states', () => {
    let comparisons = 0;
    for (const theme of THEMES) for (const role of ROLES) {
      const base = { theme, role_state: role, target_x: 0.91, target_y: -0.83 };
      let empty = model.createState(sample(0, base));
      let candidate = model.createState(sample(0, { ...base, candidate_present: true }));
      for (const time of [0, DT, 100, 500, 1200, 4000]) {
        if (time > 0) {
          empty = model.step(empty, sample(time, base));
          candidate = model.step(candidate, sample(time, { ...base, candidate_present: true }));
        }
        const label = `${theme}/${role} at ${time}ms`;
        assertFinitePose(candidate.pose, label);
        equivalentPose(candidate.pose, empty.pose, `${label}: candidate changed visual output`);
        assert.equal(candidate.pose.targetUsable, false, `${label}: candidate became usable target`);
        assert.equal(candidate.pose.roleState, role, `${label}: candidate changed supplied state`);
        if (role === 'sleeping') near(candidate.pose.lid, 1, `${label}: candidate opened sleeping eye`);
        comparisons += 1;
      }
    }
    return { comparisons, themes: THEMES, states: ROLES };
  });

  check('V02', 'confirmed coordinates actually drive tracking', () => {
    for (const theme of THEMES) {
      const incoming = sample(0, { theme, role_state: 'TRACKING', target_confirmed: true,
        target_x: 0.8, target_y: -0.6 });
      let state = model.createState(incoming);
      state = model.step(state, { ...incoming, now_ms: 1500 });
      assertFinitePose(state.pose, theme);
      assert.equal(state.pose.targetUsable, true, `${theme}: confirmed target not accepted`);
      assert.ok(state.pose.gazeX > 0.05 && state.pose.gazeY < -0.05,
        `${theme}: confirmed off-center target did not drive signed gaze`);
    }
    return { themes: THEMES, target: { x: 0.8, y: -0.6 } };
  });

  check('V03', 'invalid target data freezes gaze, returns to neutral, and recovers', () => {
    const defects = [
      ['NaN x', (value) => { value.target_x = NaN; }],
      ['infinite y', (value) => { value.target_y = Infinity; }],
      ['missing x', (value) => { delete value.target_x; }],
      ['missing y', (value) => { delete value.target_y; }],
      ['null coordinate', (value) => { value.target_x = null; }],
      ['invalid data flag', (value) => { value.data_valid = false; }],
      ['confirmation lost with candidate', (value) => {
        value.target_confirmed = false;
        value.candidate_present = true;
      }]
    ];
    let sequences = 0;
    for (const theme of THEMES) for (const [name, inject] of defects) {
      const good = sample(0, { theme, role_state: 'TRACKING', target_confirmed: true,
        target_x: 0.8, target_y: -0.6 });
      let state = model.createState(good);
      state = model.step(state, { ...good, now_ms: 1000 });
      const origin = { x: state.pose.gazeX, y: state.pose.gazeY };
      assert.ok(Math.hypot(origin.x, origin.y) > 0.05, `${theme}/${name}: setup not off-center`);
      const invalidAt = 1000 + DT;
      for (const age of [0, 100, 249, 250, 475, 700, 900]) {
        const raw = { ...good, now_ms: invalidAt + age, target_x: -0.9, target_y: 0.9 };
        inject(raw);
        state = model.step(state, raw);
        const label = `${theme}/${name}, invalid age ${age}ms`;
        assertFinitePose(state.pose, label);
        assert.equal(state.pose.targetUsable, false, `${label}: invalid sample accepted`);
        assert.equal(state.pose.roleState, 'TRACKING', `${label}: fallback changed main role state`);
        if (age < 250) {
          near(state.pose.gazeX, origin.x, `${label}: gazeX did not hold`);
          near(state.pose.gazeY, origin.y, `${label}: gazeY did not hold`);
        }
        if (age === 475) {
          assert.ok(Math.hypot(state.pose.gazeX, state.pose.gazeY) < Math.hypot(origin.x, origin.y),
            `${label}: gaze did not begin returning to neutral`);
        }
        if (age >= 700) {
          near(state.pose.gazeX, 0, `${label}: gazeX did not reach neutral`);
          near(state.pose.gazeY, 0, `${label}: gazeY did not reach neutral`);
        }
      }
      const recovered = { ...good, now_ms: invalidAt + 1200, target_x: -0.7, target_y: 0.6 };
      state = model.step(state, recovered);
      state = model.step(state, { ...recovered, now_ms: invalidAt + 3000 });
      assertFinitePose(state.pose, `${theme}/${name}: recovery`);
      assert.equal(state.pose.targetUsable, true, `${theme}/${name}: valid recovery rejected`);
      assert.ok(state.pose.gazeX < -0.05 && state.pose.gazeY > 0.05,
        `${theme}/${name}: recovery did not follow the current target`);
      sequences += 1;
    }
    return { sequences, fallbackSuggestionMs: { hold: 250, neutralize: 450 },
      invalidInputs: defects.map(([name]) => name) };
  });

  check('V04', 'finite out-of-range coordinates equal clamped boundary coordinates', () => {
    let comparisons = 0;
    for (const theme of THEMES) for (const [x, y] of [[9, -12], [-99, 6], [5, 7], [-4, -8]]) {
      const base = { theme, role_state: 'TRACKING', target_confirmed: true };
      const outside = { ...base, target_x: x, target_y: y };
      const boundary = { ...base, target_x: Math.sign(x), target_y: Math.sign(y) };
      let a = model.createState(sample(0, outside));
      let b = model.createState(sample(0, boundary));
      for (const time of [0, DT, 300, 1600]) {
        if (time > 0) {
          a = model.step(a, sample(time, outside));
          b = model.step(b, sample(time, boundary));
        }
        assertFinitePose(a.pose, `${theme} clamped at ${time}ms`);
        equivalentPose(a.pose, b.pose, `${theme}: clamped output differs from boundary output`);
        assert.equal(a.pose.inputClamped, true, `${theme}: clamp diagnostic missing`);
        comparisons += 1;
      }
    }
    return { comparisons, normalizedBounds: [-1, 1], pixelBounds: PIXEL_BOUNDS };
  });

  check('V05', 'main project retains ownership of every supplied role state', () => {
    let comparisons = 0;
    const variants = [
      { target_confirmed: false, candidate_present: false },
      { target_confirmed: false, candidate_present: true },
      { target_confirmed: true, candidate_present: false },
      { target_confirmed: true, candidate_present: true, data_valid: false }
    ];
    for (const role of ROLES) for (const flags of variants) {
      const base = { role_state: role, state_entered_ms: 0, target_x: -0.6, target_y: 0.4, ...flags };
      let state = model.createState(sample(0, base));
      for (const time of [0, 100, 2000, 10000, 500000]) {
        if (time > 0) state = model.step(state, sample(time, base));
        assertFinitePose(state.pose, `${role} at ${time}ms`);
        assert.equal(state.pose.roleState, role, `${role}: autonomously changed state at ${time}ms`);
        near(state.pose.stateEnteredMs, 0, `${role}: changed supplied state time`);
        if (role === 'sleeping') near(state.pose.lid, 1, 'confirmed input cannot independently wake sleeping');
        comparisons += 1;
      }
    }
    return { comparisons, states: ROLES, elapsedTimeTestedMs: 500000 };
  });

  check('V06', 'hidden updates freeze; re-entry uses current state and current state time', () => {
    let comparisons = 0;
    for (const theme of THEMES) for (const role of ['TRACKING', 'IDLE', 'sleeping', 'NOTICE']) {
      const notice = { theme, role_state: 'NOTICE', target_confirmed: true, target_x: -0.8, target_y: 0.2 };
      let state = model.createState(sample(0, notice));
      state = model.step(state, sample(100, notice));
      const hidden = model.step(state, sample(120, { ...notice, ui_visible: false }));
      assert.equal(hidden.pose.visible, false, `${theme}/${role}: hidden pose still visible`);
      const frozen = plain(hidden);
      for (const time of [1000, 2500, 4500]) {
        const result = model.step(hidden, sample(time, { theme, ui_visible: false,
          role_state: 'waking', state_entered_ms: time - 100,
          target_confirmed: true, target_x: 0.95, target_y: -0.95 }));
        assert.equal(result, hidden, `${theme}/${role}: repeated hidden update returned new state`);
        assert.deepEqual(plain(result), frozen, `${theme}/${role}: hidden update changed suspended state`);
      }
      const current = sample(5000, { theme, role_state: role, state_entered_ms: 4800,
        target_confirmed: role === 'TRACKING' || role === 'NOTICE', target_x: 0.7, target_y: -0.5 });
      const reentered = model.step(hidden, current);
      const fresh = model.createState(current);
      assertFinitePose(reentered.pose, `${theme}/${role}: re-entry`);
      assert.equal(reentered.pose.roleState, role, `${theme}: stale NOTICE replayed on ${role} re-entry`);
      near(reentered.pose.stateEnteredMs, 4800, `${theme}/${role}: current state time ignored`);
      near(reentered.pose.phaseMs, 200, `${theme}/${role}: phase restarted on re-entry`);
      equivalentPose(reentered.pose, fresh.pose, `${theme}/${role}: re-entry retained stale animation`);
      if (role === 'sleeping') near(reentered.pose.lid, 1, `${theme}: sleeping re-entry opened eye`);
      comparisons += 1;
    }
    return { reentries: comparisons, statesOnReturn: ['TRACKING', 'IDLE', 'sleeping', 'NOTICE'] };
  });

  check('V07', 'scenario timeline explicitly covers seven states and important boundaries', () => {
    const declaration = timeline.SCENARIOS;
    assert.ok(declaration, 'PreviewTimeline.SCENARIOS missing');
    const ids = Array.isArray(declaration)
      ? declaration.map((entry) => typeof entry === 'string' ? entry : entry.id)
      : Object.keys(declaration);
    for (const id of SCENARIOS) assert.ok(ids.includes(id), `scenario ${id} missing`);
    const roles = new Set();
    const coverage = { candidateAwake: false, candidateAsleep: false, confirmed: false,
      left: false, right: false, up: false, down: false, invalid: false,
      recovered: false, hidden: false, reentry: false };
    let sawInvalid = false;
    let previous = null;
    for (let time = 0; time <= 50000; time += 100) {
      const input = model.sampleAt(time, 'full', 'night_owl');
      const direct = timeline.sampleAt(time, 'full', 'night_owl');
      assert.deepEqual(plain(input), plain(direct), `sampleAt exports disagree at ${time}ms`);
      assert.ok(ROLES.includes(input.role_state), `timeline supplied unknown role ${input.role_state}`);
      roles.add(input.role_state);
      const candidate = input.candidate_present && !input.target_confirmed;
      coverage.candidateAwake ||= candidate && input.role_state !== 'sleeping';
      coverage.candidateAsleep ||= candidate && input.role_state === 'sleeping';
      const usable = input.data_valid && input.target_confirmed
        && Number.isFinite(input.target_x) && Number.isFinite(input.target_y);
      coverage.confirmed ||= !!usable;
      if (usable && input.role_state === 'TRACKING') {
        coverage.left ||= input.target_x < -0.3;
        coverage.right ||= input.target_x > 0.3;
        coverage.up ||= input.target_y < -0.3;
        coverage.down ||= input.target_y > 0.3;
      }
      const invalid = input.target_confirmed && (!input.data_valid
        || !Number.isFinite(input.target_x) || !Number.isFinite(input.target_y));
      sawInvalid ||= !!invalid;
      coverage.invalid ||= !!invalid;
      coverage.recovered ||= sawInvalid && !!usable;
      coverage.hidden ||= input.ui_visible === false;
      coverage.reentry ||= previous?.ui_visible === false && input.ui_visible === true;
      previous = input;
    }
    for (const role of ROLES) assert.ok(roles.has(role), `full timeline never supplies ${role}`);
    for (const [name, covered] of Object.entries(coverage)) assert.ok(covered, `missing scenario coverage: ${name}`);
    const directEntries = [
      ['enter_target', 'TRACKING', true], ['enter_empty', 'IDLE', false], ['enter_asleep', 'sleeping', false]
    ];
    for (const [id, role, confirmed] of directEntries) {
      const input = model.sampleAt(0, id, 'mechanical');
      assert.equal(input.role_state, role, `${id}: wrong initial role`);
      assert.equal(input.target_confirmed, confirmed, `${id}: wrong target confirmation`);
      assert.equal(input.ui_visible, true, `${id}: direct entry must be visible`);
    }
    return { states: [...roles], scenarios: SCENARIOS, coverage, samplingIntervalMs: 100 };
  });

  check('V08', 'fixed-time results survive non-sequential seek and theme/scenario changes', () => {
    const times = [0, 17, 2100, 8250, 15900, 24750, 31500, 39999, 45000];
    const records = [];
    for (const theme of THEMES) for (const scenario of SCENARIOS) for (const time of times) {
      const result = model.simulateAt(time, scenario, theme);
      assertFinitePose(result.pose, `${theme}/${scenario} seek ${time}ms`);
      records.push({ theme, scenario, time, sample: plain(result.sample), pose: plain(result.pose) });
    }
    for (const record of [...records].reverse()) {
      const again = model.simulateAt(record.time, record.scenario, record.theme);
      assert.deepEqual(plain(again.sample), record.sample,
        `${record.theme}/${record.scenario}: sample changed after non-sequential seek at ${record.time}ms`);
      assert.deepEqual(plain(again.pose), record.pose,
        `${record.theme}/${record.scenario}: pose changed after non-sequential seek at ${record.time}ms`);
    }
    return { repeatedFixedPoints: records.length, timesMs: times, fixedStepMs: DT };
  });

  check('V09', 'seek agrees with explicit fixed-step replay of the public input stream', () => {
    const times = [1234, 8321, 19543, 32777, 44999];
    let comparisons = 0;
    for (const time of times) {
      let state = model.createState(model.sampleAt(0, 'full', 'deep_sea'));
      for (let tick = 1; tick * 1000 / 60 < time; tick += 1) {
        state = model.step(state, model.sampleAt(tick * 1000 / 60, 'full', 'deep_sea'));
      }
      state = model.step(state, model.sampleAt(time, 'full', 'deep_sea'));
      const sought = model.simulateAt(time, 'full', 'deep_sea');
      equivalentPose(state.pose, sought.pose, `seek differs from replay at ${time}ms`, 1e-7);
      comparisons += 1;
    }
    return { comparisons, timesMs: times, fixedStepMs: DT };
  });

  check('V10', 'invalid coordinates remain unusable during initialization, re-entry, and time reset', () => {
    const defects = [
      ['NaN x', (value) => { value.target_x = NaN; }],
      ['missing x', (value) => { delete value.target_x; }],
      ['infinite y', (value) => { value.target_y = Infinity; }],
      ['null x', (value) => { value.target_x = null; }]
    ];
    let comparisons = 0;
    for (const theme of THEMES) for (const [name, inject] of defects) {
      const base = { theme, role_state: 'TRACKING', target_confirmed: true,
        target_x: 0.8, target_y: -0.6 };
      const invalid = sample(2000, base);
      inject(invalid);
      const initialized = model.createState(invalid);
      let beforeHidden = model.createState(sample(0, base));
      beforeHidden = model.step(beforeHidden, sample(1000, { ...base, ui_visible: false }));
      const reentered = model.step(beforeHidden, invalid);
      const later = model.createState(sample(5000, base));
      const reset = model.step(later, invalid);
      for (const [operation, state] of [['initialization', initialized], ['re-entry', reentered], ['time reset', reset]]) {
        const label = `${theme}/${name}/${operation}`;
        assertFinitePose(state.pose, label);
        assert.equal(state.pose.targetUsable, false, `${label}: invalid coordinates became a confirmed usable target`);
        assert.equal(state.pose.roleState, 'TRACKING', `${label}: current supplied state changed`);
        comparisons += 1;
      }
    }
    return { comparisons, resetPaths: ['initialization', 're-entry', 'time reset'],
      invalidInputs: defects.map(([name]) => name) };
  });

  check('V11', 'incremental cursor agrees exactly with replay across playback, seek, and context changes', () => {
    let comparisons = 0;
    const categories = {};
    function advanceAndCompare(cursor, time, scenario, theme, category) {
      const before = cursor ? plain(cursor) : null;
      const incremental = model.advanceTo(cursor, time, scenario, theme);
      const replayed = model.simulateAt(time, scenario, theme);
      const label = `${category}/${theme}/${scenario} at ${time}ms`;
      assertFinitePose(incremental.pose, label);
      assert.ok(incremental.cursor && typeof incremental.cursor === 'object', `${label}: cursor missing`);
      assert.equal(incremental.timeMs, replayed.timeMs, `${label}: time differs from replay`);
      assert.equal(incremental.scenario, replayed.scenario, `${label}: scenario differs from replay`);
      assert.deepEqual(plain(incremental.sample), plain(replayed.sample), `${label}: input differs from replay`);
      assert.deepEqual(plain(incremental.pose), plain(replayed.pose), `${label}: pose differs from replay`);
      if (cursor) assert.deepEqual(plain(cursor), before, `${label}: input cursor was mutated`);
      comparisons += 1;
      categories[category] = (categories[category] || 0) + 1;
      return incremental.cursor;
    }

    // Include full-scenario transition boundaries and off-grid transport times.
    const forwardTimes = [0, 17, 33, 50, 83, 100, 999, 1000, 2999, 3000,
      5017, 5999, 6000, 6001, 6899, 6900, 6917, 12500, 14400, 15500,
      19000, 20400, 22400, 23200, 26700, 27000, 27600, 28400, 30000,
      30600, 30600.01, 30616.666666666668, 30700, 30850, 31075, 31300,
      31600, 32600, 32900, 33800, 34200, 36600, 36800, 38200, 40400,
      41200, 42500, 43250, 44200, 45500, 46400, 48000];
    for (const theme of THEMES) {
      let cursor = null;
      for (const time of forwardTimes) {
        cursor = advanceAndCompare(cursor, time, 'full', theme, 'forward playback');
      }
    }

    const irregularTimes = [31000, 30600, 30610, 0, 27001, 28400, 123.25,
      42555.5, 42500, 43250, 5999.9, 6000.1, 48000, 48000, 2351, 35000];
    let cursor = null;
    for (const time of irregularTimes) {
      cursor = advanceAndCompare(cursor, time, 'full', 'deep_sea', 'irregular seek and rollback');
    }

    const contextChanges = [
      [30599.5, 'full', 'night_owl'], [30600, 'full', 'night_owl'],
      [30617, 'full', 'deep_sea'], [31600, 'full', 'deep_sea'],
      [3000, 'enter_target', 'deep_sea'], [0, 'enter_empty', 'night_owl'],
      [1400, 'enter_asleep', 'mechanical'], [6000, 'enter_asleep', 'mechanical'],
      [30600, 'full', 'mechanical'], [31600, 'full', 'mechanical'],
      [30600, 'full', 'night_owl'], [45000, 'enter_target', 'night_owl'],
      [5000, 'full', 'night_owl'], [0, 'full', 'night_owl'], [45000, 'full', 'deep_sea']
    ];
    cursor = null;
    for (const [time, scenario, theme] of contextChanges) {
      cursor = advanceAndCompare(cursor, time, scenario, theme, 'theme and scenario changes');
    }

    const branch = model.advanceTo(null, 30600, 'full', 'night_owl').cursor;
    for (const time of [31700, 31000, 30600, 42550]) {
      advanceAndCompare(branch, time, 'full', 'night_owl', 'reuse an earlier cursor');
    }
    return { comparisons, categories, comparison: 'exact sample and pose equality; input cursor unchanged',
      floatingPointBoundaryIncludedMs: 30600, pixelBounds: PIXEL_BOUNDS };
  });
}

const passed = checks.filter((item) => item.status === 'passed').length;
const failed = checks.length - passed;
const report = {
  schema: 'mosaico-eye-ui-preview-verification-v1',
  scope: 'JavaScript reference model and explicitly injected scenario timeline only',
  checkedAt: new Date().toISOString(),
  command: 'node tools/verify_preview.js [--json PATH]',
  nodeVersion: process.version,
  sources,
  assertionsNotMade: ['C/GSP implementation', 'hardware rendering/performance/memory',
    'main-project integration/API/timing policy', 'detector accuracy', 'visual asset quality'],
  summary: { total: checks.length, passed, failed },
  checks
};
if (jsonPath) {
  fs.mkdirSync(path.dirname(jsonPath), { recursive: true });
  fs.writeFileSync(jsonPath, `${JSON.stringify(report, null, 2)}\n`);
}
process.stdout.write(`\nJavaScript reference verification: ${passed}/${checks.length} passed; ${failed} failed.\n`);
if (jsonPath) process.stdout.write(`Evidence: ${jsonPath}\n`);
process.exitCode = failed ? 1 : 0;
