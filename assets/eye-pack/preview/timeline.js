/* Offline reference input script. Every state and confirmation is SIMULATED.
 * No detector, classifier, distance logic, or project-level input policy lives here.
 * Coordinates: x points right; y points down; normalized to [-1, 1].
 */
(function (root) {
  'use strict';

  var SCENARIOS = Object.freeze({
    full: Object.freeze({ id: 'full', name: '完整参考演示', durationMs: 48000,
      description: '七种状态、候选忽略、四向跟随、失效回退，以及三种切出／重入。所有输入由时间线注入。' }),
    enter_target: Object.freeze({ id: 'enter_target', name: '进入页面 · 已确认目标', durationMs: 6000,
      description: '首次可见即注入 TRACKING 与有效目标。直接使用当前目标，不重放 NOTICE。' }),
    enter_empty: Object.freeze({ id: 'enter_empty', name: '进入页面 · 无目标', durationMs: 6000,
      description: '首次可见即注入 IDLE。中途候选输入仅展示在面板中，不改变角色状态或目光。' }),
    enter_asleep: Object.freeze({ id: 'enter_asleep', name: '进入页面 · 已睡眠', durationMs: 6000,
      description: '首次可见即注入 sleeping，眼睑保持闭合。未确认候选不唤醒。' })
  });

  var MARKERS = Object.freeze([
    { timeMs: 0, label: '空闲', group: 'IDLE' },
    { timeMs: 3000, label: '未确认候选', group: 'IDLE' },
    { timeMs: 6000, label: '确认到来', group: 'NOTICE' },
    { timeMs: 6900, label: '四向跟随', group: 'TRACKING' },
    { timeMs: 12500, label: '停留', group: 'HOLD' },
    { timeMs: 14400, label: '离开', group: 'LEAVE' },
    { timeMs: 15500, label: '回到空闲', group: 'IDLE' },
    { timeMs: 19000, label: '进入睡眠', group: 'sleeping' },
    { timeMs: 20400, label: '睡眠中候选', group: 'sleeping' },
    { timeMs: 22400, label: '确认后唤醒', group: 'waking' },
    { timeMs: 26700, label: '动作中切出', group: 'NOTICE' },
    { timeMs: 28400, label: '重入 · 跟随', group: 'TRACKING' },
    { timeMs: 30600, label: '输入失效', group: 'TRACKING' },
    { timeMs: 31600, label: '有效输入恢复', group: 'TRACKING' },
    { timeMs: 32600, label: '动作中再切出', group: 'NOTICE' },
    { timeMs: 34200, label: '重入 · 无目标', group: 'IDLE' },
    { timeMs: 36600, label: '切出期间睡眠', group: 'IDLE' },
    { timeMs: 38200, label: '重入 · 已睡眠', group: 'sleeping' },
    { timeMs: 40400, label: '再次唤醒', group: 'waking' },
    { timeMs: 42500, label: '坐标失效', group: 'TRACKING' },
    { timeMs: 43250, label: '坐标恢复', group: 'TRACKING' },
    { timeMs: 44200, label: '稳定停留', group: 'HOLD' },
    { timeMs: 45500, label: '离开回中', group: 'LEAVE' },
    { timeMs: 46400, label: '结束于空闲', group: 'IDLE' }
  ].map(Object.freeze));

  function clamp(value, lo, hi) { return Math.min(hi, Math.max(lo, value)); }
  function lerp(a, b, u) { return a + (b - a) * u; }
  function between(t, a, b) { return t >= a && t < b; }

  function pointAlong(t, points) {
    if (t <= points[0][0]) return { x: points[0][1], y: points[0][2] };
    for (var i = 1; i < points.length; i += 1) {
      if (t <= points[i][0]) {
        var p = points[i - 1], q = points[i];
        var u = (t - p[0]) / (q[0] - p[0]);
        return { x: lerp(p[1], q[1], u), y: lerp(p[2], q[2], u) };
      }
    }
    var last = points[points.length - 1];
    return { x: last[1], y: last[2] };
  }

  function sampleAt(ms, scenario, theme) {
    var id = Object.prototype.hasOwnProperty.call(SCENARIOS, scenario) ? scenario : 'full';
    var t = clamp(typeof ms === 'number' && Number.isFinite(ms) ? ms : 0, 0, SCENARIOS[id].durationMs);
    var chosenTheme = ['night_owl', 'deep_sea', 'mechanical'].indexOf(theme) >= 0 ? theme : 'night_owl';
    var sample = {
      now_ms: t,
      data_valid: true,
      target_confirmed: false,
      candidate_present: false,
      target_x: null,
      target_y: null,
      role_state: 'IDLE',
      state_entered_ms: 0,
      ui_visible: true,
      theme: chosenTheme,
      scenario: id,
      simulated: true,
      note: '无目标：由注入的 IDLE 显示轻微游移与眨眼。'
    };

    function state(name, at, note) {
      sample.role_state = name;
      sample.state_entered_ms = at;
      if (note) sample.note = note;
    }
    function target(x, y) {
      sample.target_confirmed = true;
      sample.target_x = x;
      sample.target_y = y;
    }
    function candidate(x, y) {
      sample.candidate_present = true;
      sample.target_x = x;
      sample.target_y = y;
    }

    if (id === 'enter_target') {
      state('TRACKING', 0, '直接进入：当前已确认目标。当前角色由外部注入，不补播到来动作。');
      var direct = pointAlong(t, [[0, 0.65, -0.25], [1800, 0.65, -0.25], [3600, -0.55, 0.35], [6000, 0.15, -0.2]]);
      target(direct.x, direct.y);
      return sample;
    }
    if (id === 'enter_empty') {
      sample.note = '直接进入：当前无目标。保持注入的 IDLE。';
      if (between(t, 1800, 4200)) {
        candidate(0.9, -0.7);
        sample.note = '只有候选：不读取候选坐标，不切到 NOTICE／TRACKING。';
      }
      return sample;
    }
    if (id === 'enter_asleep') {
      state('sleeping', 0, '直接进入：当前已睡眠，闭眼稳定显示，不重播入睡动作。');
      if (between(t, 1400, 4600)) {
        candidate(-0.85, 0.65);
        sample.note = '睡眠中只有候选：保持 sleeping，不自行唤醒。';
      }
      return sample;
    }

    if (t < 6000) {
      if (between(t, 3000, 5000)) {
        candidate(0.85, -0.7);
        sample.note = '候选尚未确认：面板展示候选，角色维持同一条 IDLE 动画。';
      }
    } else if (t < 6900) {
      state('NOTICE', 6000, '确认到来：外部脚本同时注入有效目标与 NOTICE。');
      target(-0.55, -0.15);
    } else if (t < 12500) {
      state('TRACKING', 6900, '四向跟随：x 向右为正，y 向下为正；位置经过低通平滑。');
      var p = pointAlong(t, [
        [6900, -0.55, -0.15], [8200, -0.95, 0], [8700, -0.95, 0],
        [9900, 0.95, 0], [10300, 0.95, 0], [11100, 0, 0.9],
        [11400, 0, 0.9], [12200, 0, -0.9], [12500, 0.55, -0.15]
      ]);
      target(p.x, p.y);
    } else if (t < 14400) {
      state('HOLD', 12500, '停留：外部注入 HOLD，保持有效目标上的安静注视。');
      target(0.55, -0.15);
    } else if (t < 15500) {
      state('LEAVE', 14400, '离开：由外部明确注入 LEAVE；参考动作柔和回中。');
    } else if (t < 19000) {
      state('IDLE', 15500, '回到空闲：是否及何时入睡完全由主项目决定。');
    } else if (t < 22400) {
      state('sleeping', 19000, '外部脚本注入 sleeping；参考闭眼过渡 700 ms。');
      if (between(t, 20400, 21600)) {
        candidate(0.9, -0.8);
        sample.note = '睡眠中未确认候选：不移动目光、不唤醒。';
      }
    } else if (t < 23200) {
      state('waking', 22400, '外部脚本在确认后注入 waking；预览本身不决定唤醒。');
      target(-0.4, -0.15);
    } else if (t < 26700) {
      state('TRACKING', 23200, '唤醒后的有效目标跟随。');
      var afterWake = pointAlong(t, [[23200, -0.4, -0.15], [24900, 0.55, 0.3], [26700, -0.2, -0.35]]);
      target(afterWake.x, afterWake.y);
    } else if (t < 28400) {
      state(t < 27600 ? 'NOTICE' : 'TRACKING', t < 27600 ? 26700 : 27600,
        'NOTICE 动作中切出；切出期间角色模型冻结，输入脚本仍代表外部当前状态。');
      target(0.75, 0.1);
    } else if (t < 32600) {
      state('TRACKING', 27600, '按当前 TRACKING 与目标重入，不重播切出前的 NOTICE。');
      var reentry = pointAlong(t, [[28400, 0.75, 0.1], [30200, -0.65, 0.25], [32600, 0.5, -0.35]]);
      target(reentry.x, reentry.y);
      if (between(t, 30600, 31600)) {
        sample.data_valid = false;
        sample.note = '输入失效：参考策略先保持 250 ms，再用 450 ms 回中；角色仍是 TRACKING。';
      }
    } else if (t < 33800) {
      if (t < 33300) {
        state('NOTICE', 32600, '另一次 NOTICE 中切出；随后外部输入变为无目标。');
        target(-0.75, -0.35);
      } else {
        state('LEAVE', 33300, '页面不可见期间，外部脚本已进入 LEAVE。角色模型没有更新。');
      }
    } else if (t < 36800) {
      state('IDLE', 33800, '按当前无目标 IDLE 重入；没有旧的到来或离开动画补播。');
    } else if (t < 40400) {
      state('sleeping', 36800, '切出期间外部已进入 sleeping；重入直接显示闭眼状态。');
      if (between(t, 39000, 40000)) {
        candidate(-0.8, 0.7);
        sample.note = '重入后的睡眠候选仍被忽略。只有外部状态注入才能启动 waking。';
      }
    } else if (t < 41200) {
      state('waking', 40400, '外部脚本再次注入 waking 与已确认目标。');
      target(0.2, -0.2);
    } else if (t < 44200) {
      state('TRACKING', 41200, '有效目标持续跟随；接下来单独演示无效坐标保护。');
      var finalTrack = pointAlong(t, [[41200, 0.2, -0.2], [42300, 0.8, 0.45], [44200, -0.45, -0.25]]);
      target(finalTrack.x, finalTrack.y);
      if (between(t, 42500, 43250)) {
        sample.target_y = NaN;
        sample.note = 'target_y = NaN：拒绝非有限坐标并执行同一安全回退，不改变注入状态。';
      }
    } else if (t < 45500) {
      state('HOLD', 44200, '再次停留：三种角色共用同一份输入语义与动作时间。');
      target(-0.45, -0.25);
    } else if (t < 46400) {
      state('LEAVE', 45500, '外部注入 LEAVE，柔和回中。');
    } else {
      state('IDLE', 46400, '参考演示结束。所有状态判定、时间门槛和导航规则仍由主项目接管。');
    }

    sample.ui_visible = !(
      between(t, 27000, 28400) || between(t, 32900, 34200) || between(t, 36600, 38200)
    );
    return sample;
  }

  root.PreviewTimeline = Object.freeze({
    SCENARIOS: SCENARIOS,
    MARKERS: MARKERS,
    DURATION_MS: 48000,
    sampleAt: sampleAt,
    pointAlong: pointAlong
  });
})(typeof window !== 'undefined' ? window : globalThis);
