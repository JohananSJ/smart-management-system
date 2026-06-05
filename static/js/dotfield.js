function initDotField(canvasId, options = {}) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext('2d', { alpha: true });
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const TWO_PI = Math.PI * 2;

  const cfg = {
    dotRadius:     options.dotRadius     ?? 1.5,
    dotSpacing:    options.dotSpacing    ?? 14,
    cursorRadius:  options.cursorRadius  ?? 500,
    bulgeOnly:     options.bulgeOnly     ?? true,
    bulgeStrength: options.bulgeStrength ?? 67,
    sparkle:       options.sparkle       ?? false,
    waveAmplitude: options.waveAmplitude ?? 0,
    gradientFrom:  options.gradientFrom  ?? 'rgba(139, 92, 246, 0.35)',
    gradientTo:    options.gradientTo    ?? 'rgba(180, 151, 207, 0.25)',
  };

  let dots = [];
  let frameCount = 0;
  let rafId = null;
  let resizeTimer = null;
  let engagement = 0;
  const mouse = { x: -9999, y: -9999, prevX: -9999, prevY: -9999, speed: 0 };
  let size = { w: 0, h: 0, offsetX: 0, offsetY: 0 };

  // Resize
  function doResize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    const w = rect.width;
    const h = rect.height;

    canvas.width  = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width  = w + 'px';
    canvas.style.height = h + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    size = {
      w,
      h,
      offsetX: rect.left + window.scrollX,
      offsetY: rect.top  + window.scrollY,
    };

    buildDots(w, h);
  }

  // Build dot grid 
  function buildDots(w, h) {
    const step = cfg.dotRadius + cfg.dotSpacing;
    const cols = Math.floor(w / step);
    const rows = Math.floor(h / step);
    const padX = (w % step) / 2;
    const padY = (h % step) / 2;
    dots = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const ax = padX + c * step + step / 2;
        const ay = padY + r * step + step / 2;
        dots.push({ ax, ay, sx: ax, sy: ay, vx: 0, vy: 0, x: ax, y: ay });
      }
    }
  }

  // Mouse tracking 
  function onMouseMove(e) {
    mouse.x = e.pageX - size.offsetX;
    mouse.y = e.pageY - size.offsetY;
  }

  function updateMouseSpeed() {
    const dx   = mouse.prevX - mouse.x;
    const dy   = mouse.prevY - mouse.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    mouse.speed += (dist - mouse.speed) * 0.5;
    if (mouse.speed < 0.001) mouse.speed = 0;
    mouse.prevX = mouse.x;
    mouse.prevY = mouse.y;
  }

  // Main animation loop 
  function tick() {
    frameCount++;
    const { w, h } = size;
    const t = frameCount * 0.02;

    const targetEngagement = Math.min(mouse.speed / 5, 1);
    engagement += (targetEngagement - engagement) * 0.06;
    if (engagement < 0.001) engagement = 0;

    ctx.clearRect(0, 0, w, h);

    const grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, cfg.gradientFrom);
    grad.addColorStop(1, cfg.gradientTo);
    ctx.fillStyle = grad;

    const crSq = cfg.cursorRadius * cfg.cursorRadius;
    const rad  = cfg.dotRadius / 2;

    ctx.beginPath();

    for (let i = 0; i < dots.length; i++) {
      const d      = dots[i];
      const dx     = mouse.x - d.ax;
      const dy     = mouse.y - d.ay;
      const distSq = dx * dx + dy * dy;

      if (distSq < crSq && engagement > 0.01) {
        const dist  = Math.sqrt(distSq);
        const tVal  = 1 - dist / cfg.cursorRadius;
        const push  = tVal * tVal * cfg.bulgeStrength * engagement;
        const angle = Math.atan2(dy, dx);
        d.sx += (d.ax - Math.cos(angle) * push - d.sx) * 0.15;
        d.sy += (d.ay - Math.sin(angle) * push - d.sy) * 0.15;
      } else {
        d.sx += (d.ax - d.sx) * 0.1;
        d.sy += (d.ay - d.sy) * 0.1;
      }

      let drawX = d.sx;
      let drawY = d.sy;

      if (cfg.waveAmplitude > 0) {
        drawY += Math.sin(d.ax * 0.03 + t) * cfg.waveAmplitude;
        drawX += Math.cos(d.ay * 0.03 + t * 0.7) * cfg.waveAmplitude * 0.5;
      }

      if (cfg.sparkle) {
        const hash = (((i * 2654435761) ^ (frameCount >> 3)) >>> 0);
        const r    = (hash % 100) < 3 ? rad * 1.8 : rad;
        ctx.moveTo(drawX + r, drawY);
        ctx.arc(drawX, drawY, r, 0, TWO_PI);
      } else {
        ctx.moveTo(drawX + rad, drawY);
        ctx.arc(drawX, drawY, rad, 0, TWO_PI);
      }
    }

    ctx.fill();
    rafId = requestAnimationFrame(tick);
  }

  // Event listeners
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(doResize, 100);
  });

  window.addEventListener('mousemove', onMouseMove, { passive: true });
  setInterval(updateMouseSpeed, 20);

  // Start
  doResize();
  tick();

  // Return destroy function
  return function destroy() {
    cancelAnimationFrame(rafId);
    clearTimeout(resizeTimer);
    window.removeEventListener('resize', doResize);
    window.removeEventListener('mousemove', onMouseMove);
  };
}