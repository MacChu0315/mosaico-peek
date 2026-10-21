/* Pure deterministic animation reference. No wall clock, timers, DOM, detector,
 * target confirmation, state transition policy, or navigation rules.
 * All durations below are REFERENCE SUGGESTIONS, not ESP-Mosaico project policy.
 */
(function (root) {
  'use strict';

  var STATES = Object.freeze(['IDLE', 'NOTICE', 'TRACKING', 'HOLD', 'LEAVE', 'sleeping', 'waking']);
  var THEMES = Object.freeze({
    night_owl: Object.freeze({ maxGazeX: 18, maxGazeY: 12 }),
    deep_sea: Object.freeze({ maxGazeX: 20, maxGazeY: 12 }),
    mechanical: Object.freeze({ maxGazeX: 10, maxGazeY: 8 })
  });
  var REFERENCE = Object.freeze({
    fixedDtMs: 1000 / 60,
    seed: 0x4d4f5341,
    gazeTauMs: 135,
    holdTauMs: 260,
    invalidHoldMs: 250,
    invalidNeutralMs: 450,
    leaveNeutralMs: 600,
    sleepCloseMs: 700,
    wakeOpenMs: 650,
    blinkCycleMs: 4600,
    simulated: true
  });

  function finite(value) { return typeof value === 'number' && Number.isFinite(value); }
  function clamp(value, low, high) { return Math.min(high, Math.max(low, value)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function smoothstep(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }

  function normalizeSample(raw, fallbackNowMs) {
    raw = raw && typeof raw === 'object' ? raw : {};
    var now = finite(raw.now_ms) && raw.now_ms >= 0 ? raw.now_ms : (finite(fallbackNowMs) ? Math.max(0, fallbackNowMs) : 0);
    var coordFinite = finite(raw.target_x) && finite(raw.target_y);
    var entered = finite(raw.state_entered_ms) && raw.state_entered_ms >= 0 ? Math.min(raw.state_entered_ms, now) : now;
    var roleValid = STATES.indexOf(raw.role_state) >= 0;
    var theme = Object.prototype.hasOwnProperty.call(THEMES, raw.theme) ? raw.theme : 'night_owl';
    return {
      now_ms: now,
      data_valid: raw.data_valid === true,
      target_confirmed: raw.target_confirmed === true,
      candidate_present: raw.candidate_present === true,
      target_x: coordFinite ? clamp(raw.target_x, -1, 1) : 0,
      target_y: coordFinite ? clamp(raw.target_y, -1, 1) : 0,
      coordinates_valid: coordFinite,
      coordinates_clamped: coordFinite && (Math.abs(raw.target_x) > 1 || Math.abs(raw.target_y) > 1),
      target_usable: raw.data_valid === true && raw.target_confirmed === true && coordFinite,
      role_state: roleValid ? raw.role_state : 'IDLE',
      role_fallback: !roleValid,
      state_entered_ms: entered,
      ui_visible: raw.ui_visible !== false,
      theme: theme
    };
  }

  /* Integer hash provides a reproducible variation schedule. It is not input
   * arbitration, a detector, or a runtime random-number source. */
  function seededUnit(index) {
    var n = (REFERENCE.seed ^ Math.imul((index + 1) | 0, 0x45d9f3b)) >>> 0;
    n = Math.imul(n ^ (n >>> 16), 0x45d9f3b) >>> 0;
    n = Math.imul(n ^ (n >>> 16), 0x45d9f3b) >>> 0;
    return ((n ^ (n >>> 16)) >>> 0) / 4294967295;
  }

  function blinkPulse(t) {
    if (t < 0 || t >= 240) return 0;
    if (t < 75) return smoothstep(t / 75);
    if (t < 110) return 1;
    return 1 - smoothstep((t - 110) / 130);
  }

  function blinkAt(ageMs) {
    var age = Math.max(0, ageMs), cycle = Math.floor(age / REFERENCE.blinkCycleMs);
    var phase = age - cycle * REFERENCE.blinkCycleMs;
    var start = 2600 + seededUnit(cycle) * 750;
    var first = blinkPulse(phase - start);
    var second = seededUnit(cycle + 101) > 0.76 ? blinkPulse(phase - start - 350) * 0.88 : 0;
    return Math.max(first, second);
  }

  function idleGaze(ageMs) {
    var t = Math.max(0, ageMs) / 1000;
    return { x: 0.085 * Math.sin(t * 0.51) + 0.025 * Math.sin(t * 1.13),
      y: 0.055 * Math.sin(t * 0.39) + 0.015 * Math.sin(t * 0.91) };
  }

  function targetRole(role) { return role === 'NOTICE' || role === 'TRACKING' || role === 'HOLD' || role === 'waking'; }

  function makePose(state, sample, lid, fallbackMode, reentered) {
    var theme = THEMES[sample.theme];
    return {
      gazeX: clamp(state.gazeX, -1, 1),
      gazeY: clamp(state.gazeY, -1, 1),
      gazePxX: clamp(state.gazeX, -1, 1) * theme.maxGazeX,
      gazePxY: clamp(state.gazeY, -1, 1) * theme.maxGazeY,
      lid: clamp(lid, 0, 1),
      roleState: sample.role_state,
      stateEnteredMs: sample.state_entered_ms,
      phaseMs: Math.max(0, sample.now_ms - sample.state_entered_ms),
      visible: sample.ui_visible,
      nowMs: sample.now_ms,
      theme: sample.theme,
      fallbackMode: fallbackMode || 'none',
      targetUsable: sample.target_usable,
      inputClamped: sample.coordinates_clamped,
      reentered: reentered === true
    };
  }

  function lidFor(state, sample) {
    var age = Math.max(0, sample.now_ms - sample.state_entered_ms);
    if (sample.role_state === 'sleeping') {
      if (state.sleepEnteredVisible) return lerp(state.sleepStartLid, 1, smoothstep(age / REFERENCE.sleepCloseMs));
      return 1;
    }
    if (sample.role_state === 'waking') return 1 - smoothstep(age / REFERENCE.wakeOpenMs);
    if (sample.role_state === 'NOTICE') return 0.12 * (1 - smoothstep(age / 220));
    if (sample.role_state === 'LEAVE') return blinkPulse(age - 280) * 0.95;
    return blinkAt(sample.now_ms - state.visibleEpochMs);
  }

  function initialize(sample, reentered) {
    var initial = { x: 0, y: 0 };
    if (sample.role_state === 'IDLE') initial = idleGaze(sample.now_ms - sample.state_entered_ms);
    if (targetRole(sample.role_state) && sample.target_usable) {
      initial = { x: sample.target_x, y: sample.target_y };
      if (sample.role_state === 'waking') {
        var wake = smoothstep((sample.now_ms - sample.state_entered_ms) / REFERENCE.wakeOpenMs);
        initial.x *= wake;
        initial.y *= wake;
      }
    }
    var state = {
      lastNowMs: sample.now_ms,
      visible: sample.ui_visible,
      suspended: !sample.ui_visible,
      currentRole: sample.role_state,
      stateEnteredMs: sample.state_entered_ms,
      visibleEpochMs: sample.now_ms,
      gazeX: initial.x,
      gazeY: initial.y,
      invalidSinceMs: targetRole(sample.role_state) && !sample.target_usable ? sample.now_ms : null,
      fallbackOriginX: initial.x,
      fallbackOriginY: initial.y,
      leaveOriginX: initial.x,
      leaveOriginY: initial.y,
      sleepEnteredVisible: false,
      sleepStartLid: 1,
      pose: null
    };
    state.pose = makePose(state, sample, lidFor(state, sample),
      targetRole(sample.role_state) && !sample.target_usable ? 'hold' : 'none', reentered);
    return state;
  }

  function createState(raw, reentered) {
    return initialize(normalizeSample(raw), reentered);
  }

  function step(previous, raw) {
    if (!previous || !previous.pose) return createState(raw);
    var sample = normalizeSample(raw, previous.lastNowMs);
    if (!sample.ui_visible) {
      if (previous.suspended) return previous;
      return Object.assign({}, previous, { visible: false, suspended: true,
        pose: Object.assign({}, previous.pose, { visible: false, reentered: false }) });
    }
    if (previous.suspended || !previous.visible) return initialize(sample, true);
    if (sample.now_ms < previous.lastNowMs) return initialize(sample, true);

    var state = Object.assign({}, previous);
    var changed = sample.role_state !== previous.currentRole || sample.state_entered_ms !== previous.stateEnteredMs;
    var dt = Math.max(0, sample.now_ms - previous.lastNowMs);
    var age = Math.max(0, sample.now_ms - sample.state_entered_ms);
    var fallbackMode = 'none';
    state.lastNowMs = sample.now_ms;
    state.visible = true;
    state.suspended = false;
    state.currentRole = sample.role_state;
    state.stateEnteredMs = sample.state_entered_ms;

    if (changed) {
      state.leaveOriginX = previous.gazeX;
      state.leaveOriginY = previous.gazeY;
      state.sleepEnteredVisible = sample.role_state === 'sleeping';
      state.sleepStartLid = previous.pose.lid;
      state.invalidSinceMs = null;
    }

    if (sample.role_state === 'sleeping') {
      var rest = smoothstep(age / REFERENCE.sleepCloseMs);
      state.gazeX = state.sleepEnteredVisible ? lerp(state.leaveOriginX, 0, rest) : 0;
      state.gazeY = state.sleepEnteredVisible ? lerp(state.leaveOriginY, 0, rest) : 0;
      state.invalidSinceMs = null;
    } else if (sample.role_state === 'LEAVE') {
      var release = smoothstep(age / REFERENCE.leaveNeutralMs);
      state.gazeX = lerp(state.leaveOriginX, 0, release);
      state.gazeY = lerp(state.leaveOriginY, 0, release);
      state.invalidSinceMs = null;
    } else if (sample.role_state === 'IDLE') {
      var idle = idleGaze(age);
      var idleBlend = changed ? 0 : 1 - Math.exp(-dt / 220);
      state.gazeX = lerp(previous.gazeX, idle.x, idleBlend);
      state.gazeY = lerp(previous.gazeY, idle.y, idleBlend);
      state.invalidSinceMs = null;
    } else if (sample.target_usable) {
      state.invalidSinceMs = null;
      var tau = sample.role_state === 'HOLD' ? REFERENCE.holdTauMs : REFERENCE.gazeTauMs;
      var blend = 1 - Math.exp(-dt / tau);
      var desiredX = sample.target_x, desiredY = sample.target_y;
      if (sample.role_state === 'waking') {
        var opening = smoothstep(age / REFERENCE.wakeOpenMs);
        desiredX *= opening;
        desiredY *= opening;
      }
      state.gazeX = lerp(previous.gazeX, desiredX, blend);
      state.gazeY = lerp(previous.gazeY, desiredY, blend);
    } else {
      if (previous.invalidSinceMs === null || changed) {
        state.invalidSinceMs = sample.now_ms;
        state.fallbackOriginX = previous.gazeX;
        state.fallbackOriginY = previous.gazeY;
      }
      var invalidAge = Math.max(0, sample.now_ms - state.invalidSinceMs);
      var neutralProgress = smoothstep((invalidAge - REFERENCE.invalidHoldMs) / REFERENCE.invalidNeutralMs);
      state.gazeX = state.fallbackOriginX * (1 - neutralProgress);
      state.gazeY = state.fallbackOriginY * (1 - neutralProgress);
      fallbackMode = invalidAge < REFERENCE.invalidHoldMs ? 'hold' :
        invalidAge < REFERENCE.invalidHoldMs + REFERENCE.invalidNeutralMs ? 'neutralizing' : 'neutral';
    }

    state.pose = makePose(state, sample, lidFor(state, sample), fallbackMode, false);
    return state;
  }

  function sampleAt(ms, scenario, theme) {
    if (!root.PreviewTimeline) throw new Error('Load timeline.js before requesting an injected sample.');
    return root.PreviewTimeline.sampleAt(ms, scenario, theme);
  }

  /* Seek/replay re-simulates from t0 on the same 60 Hz grid. The final partial
   * step is evaluated at the exact requested timestamp; no render history or
   * wall clock enters the result. Hidden intervals are sampled by the reference
   * transport but never tick the suspended character model. */
  function advanceTo(cursor, ms, scenario, theme) {
    var sample = sampleAt(ms, scenario, theme);
    var end = sample.now_ms;
    var steps = Math.floor(end * 60 / 1000);
    var reuse = cursor && cursor.scenario === sample.scenario && cursor.theme === sample.theme && cursor.index <= steps;
    var state = reuse ? cursor.state : createState(sampleAt(0, sample.scenario, sample.theme));
    var first = reuse ? cursor.index + 1 : 1;
    for (var i = first; i <= steps; i += 1) {
      /* A grid timestamp must not depend on a previous seek endpoint. Divide
       * the integer numerator last so exact second boundaries stay exact. */
      var time = i * 1000 / 60;
      var at = sampleAt(time, sample.scenario, sample.theme);
      if (!at.ui_visible && state.suspended) continue;
      state = step(state, at);
    }
    var nextCursor = { index: steps, state: state, scenario: sample.scenario, theme: sample.theme };
    if (end > steps * 1000 / 60) state = step(state, sample);
    return { timeMs: end, scenario: sample.scenario, sample: sample, pose: state.pose, state: state, cursor: nextCursor };
  }

  function simulateAt(ms, scenario, theme) {
    var result = advanceTo(null, ms, scenario, theme);
    delete result.cursor;
    return result;
  }

  root.PreviewModel = Object.freeze({
    STATES: STATES,
    THEMES: THEMES,
    REFERENCE: REFERENCE,
    normalizeSample: normalizeSample,
    seededUnit: seededUnit,
    blinkAt: blinkAt,
    idleGaze: idleGaze,
    createState: createState,
    step: step,
    sampleAt: sampleAt,
    advanceTo: advanceTo,
    simulateAt: simulateAt
  });
})(typeof window !== 'undefined' ? window : globalThis);
