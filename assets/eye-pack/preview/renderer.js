/* Shared browser / Node Canvas renderer. It contains no animation clock.
 * Browser: PreviewRenderer.createRenderer((w,h) => a new DOM canvas).
 * Node: PreviewRenderer.createRenderer(require('@napi-rs/canvas').createCanvas).
 * Pass decoded Image objects as themeAssets.eye, .lids[0..8], and .frame.
 */
(function (root) {
  'use strict';

  function clamp(x, lo, hi) { return Math.min(hi, Math.max(lo, x)); }
  function numberOr(x, fallback) { return typeof x === 'number' && Number.isFinite(x) ? x : fallback; }
  function originOf(pair) {
    return Array.isArray(pair) ? [numberOr(pair[0], 0), numberOr(pair[1], 0)] : [0, 0];
  }

  function createRenderer(createCanvas) {
    if (typeof createCanvas !== 'function') throw new TypeError('createRenderer needs createCanvas(width, height).');
    var scratch = null, blendCtx = null;

    function ensureScratch(width, height) {
      if (!scratch || scratch.width !== width || scratch.height !== height) {
        scratch = createCanvas(width, height);
        scratch.width = width;
        scratch.height = height;
        blendCtx = scratch.getContext('2d');
      }
      return blendCtx;
    }

    function render(ctx, themeAssets, pose, options) {
      options = options || {};
      if (!ctx || !ctx.canvas) throw new TypeError('render needs a 2D Canvas context.');
      if (!themeAssets || !themeAssets.eye || !themeAssets.frame || !Array.isArray(themeAssets.lids) || themeAssets.lids.length !== 9) {
        throw new TypeError('themeAssets must include eye, frame and exactly nine decoded lid images.');
      }
      var visible = !pose || pose.visible !== false;
      var gazeX = clamp(numberOr(pose && pose.gazeX, 0), -1, 1);
      var gazeY = clamp(numberOr(pose && pose.gazeY, 0), -1, 1);
      var maxX = Math.max(0, numberOr(themeAssets.maxGazeX, 18));
      var maxY = Math.max(0, numberOr(themeAssets.maxGazeY, 12));
      var eyeOrigin = originOf(themeAssets.eyeOrigin), lidOrigin = originOf(themeAssets.lidOrigin);
      var lid = clamp(numberOr(pose && pose.lid, 0), 0, 1);
      var position = lid * 8;
      var low = Math.floor(position), high = Math.min(8, low + 1), weight = position - low;
      var pxX = gazeX * maxX, pxY = gazeY * maxY;
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
      if (visible) {
        ctx.scale(ctx.canvas.width / 480, ctx.canvas.height / 480);
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(themeAssets.eye, eyeOrigin[0] + pxX, eyeOrigin[1] + pxY);
        if (options.lowMode === true) {
          low = Math.round(position);
          high = low;
          weight = 0;
          ctx.drawImage(themeAssets.lids[low], lidOrigin[0], lidOrigin[1]);
        } else if (weight <= 1e-8 || low === high) {
          ctx.drawImage(themeAssets.lids[low], lidOrigin[0], lidOrigin[1]);
        } else {
          var a = themeAssets.lids[low], b = themeAssets.lids[high];
          if (a.width !== b.width || a.height !== b.height) throw new Error('All lid images for one theme must share dimensions.');
          var mix = ensureScratch(a.width, a.height);
          mix.setTransform(1, 0, 0, 1, 0, 0);
          mix.clearRect(0, 0, scratch.width, scratch.height);
          mix.globalCompositeOperation = 'source-over';
          mix.globalAlpha = 1 - weight;
          mix.drawImage(a, 0, 0);
          /* Add premultiplied color + alpha contributions. Ordinary source-over
           * blending for the second sprite would darken overlapping coverage. */
          mix.globalCompositeOperation = 'lighter';
          mix.globalAlpha = weight;
          mix.drawImage(b, 0, 0);
          mix.globalAlpha = 1;
          mix.globalCompositeOperation = 'source-over';
          ctx.drawImage(scratch, lidOrigin[0], lidOrigin[1]);
        }
        ctx.drawImage(themeAssets.frame, 0, 0);
      }
      ctx.restore();
      return { drawn: visible, gazePxX: pxX, gazePxY: pxY, lidLow: low, lidHigh: high,
        lidMix: weight, eyeOrigin: eyeOrigin, lidOrigin: lidOrigin };
    }

    return Object.freeze({ render: render });
  }

  root.PreviewRenderer = Object.freeze({ createRenderer: createRenderer });
})(typeof window !== 'undefined' ? window : globalThis);
