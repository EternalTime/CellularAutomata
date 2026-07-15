/* Cellular automata — interactive applet for the pyCA documentation.
 *
 * The dynamics are a direct port of the library: applyRule mirrors
 * ECA._apply_rule, the noisy and asynchronous variants mirror
 * stochastic.NoisyECA.evolve and stochastic.AsyncECA.evolve, the Ising
 * automaton mirrors ica.ICA.evolve (per-site energy, heat-bath flips,
 * clipped exponent and all), and the 2d rule mirrors ca2d.CA2D.evolve.
 * The live measures are measures.block_entropy (k = 1),
 * measures.entropy_rate (k = 2), and measures.lz_complexity, computed on
 * the current state each step. No dependencies, no build step.
 */
(function () {
    'use strict';

    /* ── Geometry and palette ───────────────────────────────────────────── */
    const N = 320;                  // 1d lattice size
    const ROWS = 180;               // 1d spacetime rows shown
    let GR = 128, GC = 128;         // 2d lattice shape; GC refit to the frame at seed time
    const TRACE = 900;              // meter history length

    const NAVY = [7, 34, 63];       // #07223f — dead cells, stage
    const GOLD = [253, 181, 21];    // #FDB515 — live cells

    /* ── ECA core (ports eca.ECA) ───────────────────────────────────────── */

    /* Bit n of the rule is the output for neighborhood number n. */
    function buildRuleArray(rule) {
        const a = new Uint8Array(8);
        for (let n = 0; n < 8; n++) a[n] = (rule >> n) & 1;
        return a;
    }

    /* One synchronous update: neighborhood number, then table lookup.
     * idx = 4*s[i-1] + 2*s[i] + s[i+1], periodic in space. */
    function applyRule(state, ra) {
        const n = state.length, out = new Uint8Array(n);
        for (let i = 0; i < n; i++) {
            const l = state[(i - 1 + n) % n], r = state[(i + 1) % n];
            out[i] = ra[4 * l + 2 * state[i] + r];
        }
        return out;
    }

    /* ── Stochastic variants (port stochastic.py) ───────────────────────── */

    /* NoisyECA: apply the rule, then flip each output with probability
     * `noise`. */
    function noisyEvolve(state, ra, noise) {
        const out = applyRule(state, ra);
        for (let i = 0; i < out.length; i++) {
            if (Math.random() < noise) out[i] = 1 - out[i];
        }
        return out;
    }

    /* AsyncECA: update a random fraction of the cells; the rest stand
     * still. The rule sees the *current* state everywhere. */
    function asyncEvolve(state, ra, q) {
        const ruled = applyRule(state, ra);
        const out = Uint8Array.from(state);
        for (let i = 0; i < out.length; i++) {
            if (Math.random() < q) out[i] = ruled[i];
        }
        return out;
    }

    /* ── Ising automaton (ports ica.ICA) ────────────────────────────────── */

    /* Thermal flips where chosen, the rule elsewhere. Stochastic cells keep
     * their previous value, flipped with the heat-bath probability
     * 1/(1 + e^(-2 E_i / T)) where E_i = -s_i (s_{i-1} + s_{i+1})/2 in
     * spin variables s = 2c - 1. The exponent is clipped to +-700 as in
     * ICA._stoch_evolve. */
    function icaEvolve(state, ra, temperature, stochfrac) {
        const n = state.length;
        const invT = 1 / (Number.EPSILON + temperature);
        const out = applyRule(state, ra);
        for (let i = 0; i < n; i++) {
            if (Math.random() < stochfrac) {
                const s = 2 * state[i] - 1;
                const l = 2 * state[(i - 1 + n) % n] - 1;
                const r = 2 * state[(i + 1) % n] - 1;
                const E = -s * 0.5 * (l + r);
                let x = 2 * invT * E;
                if (x > 700) x = 700; else if (x < -700) x = -700;
                const flip = Math.random() < 1 / (1 + Math.exp(-x));
                out[i] = flip ? 1 - state[i] : state[i];
            }
        }
        return out;
    }

    /* ── Outer-totalistic 2d (ports ca2d.CA2D) ──────────────────────────── */

    function countMask(counts) {
        const mask = new Uint8Array(9);
        for (const c of counts) if (c >= 0 && c <= 8) mask[c] = 1;
        return mask;
    }

    /* Moore-neighborhood sums with periodic wrapping, then
     * born = ~alive & births[counts], survive = alive & survivals[counts]. */
    function ca2dEvolve(grid, B, S) {
        const out = new Uint8Array(GR * GC);
        for (let r = 0; r < GR; r++) {
            const rm = ((r - 1 + GR) % GR) * GC;
            const r0 = r * GC;
            const rp = ((r + 1) % GR) * GC;
            for (let c = 0; c < GC; c++) {
                const cm = (c - 1 + GC) % GC, cp = (c + 1) % GC;
                const cnt = grid[rm + cm] + grid[rm + c] + grid[rm + cp]
                          + grid[r0 + cm] + grid[r0 + cp]
                          + grid[rp + cm] + grid[rp + c] + grid[rp + cp];
                out[r0 + c] = grid[r0 + c] ? S[cnt] : B[cnt];
            }
        }
        return out;
    }

    /* ── Measures (port measures.py) ────────────────────────────────────── */

    /* Shannon entropy of the length-k block distribution, in bits. Circular
     * windows, pooled over all supplied rows, exactly as
     * measures._block_distribution builds its histogram. */
    function blockEntropy(rows, width, k) {
        const counts = new Float64Array(1 << k);
        let total = 0;
        for (const row of rows) {
            for (let i = 0; i < width; i++) {
                let w = 0;
                for (let j = 0; j < k; j++) w = 2 * w + row[(i + j) % width];
                counts[w]++; total++;
            }
        }
        let H = 0;
        for (let a = 0; a < counts.length; a++) {
            if (counts[a] > 0) {
                const p = counts[a] / total;
                H -= p * Math.log2(p);
            }
        }
        return H;
    }

    /* Spatial entropy rate estimate, H_k - H_{k-1} (here k = 2). */
    function entropyRate2(rows, width) {
        return blockEntropy(rows, width, 2) - blockEntropy(rows, width, 1);
    }

    /* LZ76 phrase count by the Kaspar-Schuster scan (ports
     * measures._lz76_phrases line for line). */
    function lz76Phrases(s) {
        const n = s.length;
        let i = 0, k = 1, l = 1;
        let kMax = 1, c = 1;
        while (true) {
            if (s[i + k - 1] === s[l + k - 1]) {
                k += 1;
                if (l + k > n) { c += 1; break; }
            } else {
                if (k > kMax) kMax = k;
                i += 1;
                if (i === l) {
                    c += 1;
                    l += kMax;
                    if (l + 1 > n) break;
                    i = 0; k = 1; kMax = 1;
                } else {
                    k = 1;
                }
            }
        }
        return c;
    }

    /* Normalized Lempel-Ziv complexity (ports measures.lz_complexity):
     * phrase count over n / log2(n), averaged over rows. */
    function lzComplexity(rows, width) {
        const norm = Math.log2(width) / width;
        let sum = 0;
        for (const row of rows) sum += lz76Phrases(row) * norm;
        return sum / rows.length;
    }

    /* ── Parameters and state ───────────────────────────────────────────── */
    const P = {
        kind: 'eca',        // eca | noisy | async | ica | ca2d
        rule: 110,
        noise: 0.02,        // NoisyECA
        q: 0.75,            // AsyncECA update_fraction
        temperature: 1.0,   // ICA
        stochfrac: 0.5,     // ICA
        births: [3],        // CA2D
        survivals: [2, 3]
    };

    let ruleArr = buildRuleArray(P.rule);
    let Bmask = countMask(P.births);
    let Smask = countMask(P.survivals);

    let state = null;       // Uint8Array(N), the 1d state
    let grid = null;        // Uint8Array(GR*GC), the 2d state
    let running = true;

    const traceH2 = [], traceLZ = [];

    function randomRow() {
        const s = new Uint8Array(N);
        for (let i = 0; i < N; i++) s[i] = Math.random() < 0.5 ? 1 : 0;
        return s;
    }

    function seed() {
        state = randomRow();
        // Fit the 2d lattice to the frame: square cells, no letterboxing.
        // Columns are set from the stage's aspect ratio; Reset refits after
        // a window resize.
        if (canvas && off2d && canvas.width && canvas.height) {
            GC = Math.max(16, Math.round(GR * canvas.width / canvas.height));
            off2d.width = GC;
            off2d.height = GR;
            gridImg = off2dCtx.createImageData(GC, GR);
        }
        grid = new Uint8Array(GR * GC);
        for (let i = 0; i < grid.length; i++) grid[i] = Math.random() < 0.5 ? 1 : 0;
        traceH2.length = 0;
        traceLZ.length = 0;
        if (off1d) {
            const c = off1d.getContext('2d');
            c.fillStyle = 'rgb(' + NAVY.join(',') + ')';
            c.fillRect(0, 0, N, ROWS);
        }
    }

    function step() {
        if (P.kind === 'ca2d') {
            grid = ca2dEvolve(grid, Bmask, Smask);
        } else if (P.kind === 'noisy') {
            state = noisyEvolve(state, ruleArr, P.noise);
        } else if (P.kind === 'async') {
            state = asyncEvolve(state, ruleArr, P.q);
        } else if (P.kind === 'ica') {
            state = icaEvolve(state, ruleArr, P.temperature, P.stochfrac);
        } else {
            state = applyRule(state, ruleArr);
        }
    }

    /* The meters watch the current state: the single row for the 1d
     * automata, all rows of the grid pooled for the 2d one — the same
     * pooling measures._as_rows applies to 2d input. */
    function measure() {
        let rows, width;
        if (P.kind === 'ca2d') {
            rows = [];
            for (let r = 0; r < GR; r++) rows.push(grid.subarray(r * GC, (r + 1) * GC));
            width = GC;
        } else {
            rows = [state];
            width = N;
        }
        // LZ76 is the costliest measure; for the 2d lattice, every 8th row
        // estimates the same row-mean at an eighth of the cost.
        traceLZ.push(P.kind === 'ca2d'
            ? lzComplexity(rows.filter((_, r) => r % 8 === 0), width)
            : lzComplexity(rows, width));
        traceH2.push(entropyRate2(rows, width));
        if (traceLZ.length > TRACE) { traceH2.shift(); traceLZ.shift(); }
    }

    /* ── Rendering ──────────────────────────────────────────────────────── */
    let canvas, ctx, off1d, off1dCtx, off2d, off2dCtx, rowImg, gridImg;
    let phaseCv;

    function paintRow() {
        const d = rowImg.data;
        for (let i = 0; i < N; i++) {
            const c = state[i] ? GOLD : NAVY;
            d[4 * i] = c[0]; d[4 * i + 1] = c[1]; d[4 * i + 2] = c[2]; d[4 * i + 3] = 255;
        }
        // Scroll the spacetime diagram up one row, new state at the bottom.
        off1dCtx.drawImage(off1d, 0, 1, N, ROWS - 1, 0, 0, N, ROWS - 1);
        off1dCtx.putImageData(rowImg, 0, ROWS - 1);
    }

    function paintGrid() {
        const d = gridImg.data;
        for (let i = 0; i < grid.length; i++) {
            const c = grid[i] ? GOLD : NAVY;
            d[4 * i] = c[0]; d[4 * i + 1] = c[1]; d[4 * i + 2] = c[2]; d[4 * i + 3] = 255;
        }
        off2dCtx.putImageData(gridImg, 0, 0);
    }

    function draw() {
        const W = canvas.width, H = canvas.height;
        ctx.imageSmoothingEnabled = false;
        ctx.fillStyle = 'rgb(' + NAVY.join(',') + ')';
        ctx.fillRect(0, 0, W, H);
        if (P.kind === 'ca2d') {
            // Square cells: scale uniformly, centre any sliver of slack.
            const s = Math.min(W / GC, H / GR);
            const dw = GC * s, dh = GR * s;
            ctx.drawImage(off2d, (W - dw) / 2, (H - dh) / 2, dw, dh);
        } else {
            ctx.drawImage(off1d, 0, 0, W, H);
        }
    }

    /* Phase plot: C_LZ against h_2, equal axes on [0, 1]. Both estimate
     * the entropy rate — h_2 sees only pair correlations, C_LZ regularity
     * at every length — so the diagonal C_LZ = h_2 is the reference: a
     * history sags below it when it carries structure longer than two
     * cells that only the parse can see. (Finite-size bias pushes C_LZ up;
     * a fair coin at these widths sits somewhat above 1, clamped here.) */
    function drawPhase(cv) {
        const c = cv.getContext('2d');
        const W = cv.width, H = cv.height;
        const px = v => 2 + Math.min(v, 1) * (W - 4);
        const py = v => H - 2 - Math.min(v, 1) * (H - 4);
        c.clearRect(0, 0, W, H);
        c.strokeStyle = 'rgba(255,255,255,0.18)';
        c.lineWidth = 1;
        c.strokeRect(0.5, 0.5, W - 1, H - 1);
        c.setLineDash([2, 3]);
        c.beginPath(); c.moveTo(px(0), py(0)); c.lineTo(px(1), py(1)); c.stroke();
        c.setLineDash([]);
        // Trail, then the live point.
        const n = traceLZ.length;
        c.strokeStyle = 'rgba(253,181,21,0.45)';
        c.lineWidth = 1.2;
        c.beginPath();
        for (let i = 0; i < n; i++) {
            i ? c.lineTo(px(traceH2[i]), py(traceLZ[i]))
              : c.moveTo(px(traceH2[i]), py(traceLZ[i]));
        }
        c.stroke();
        if (n) {
            c.fillStyle = '#FDB515';
            c.beginPath();
            c.arc(px(traceH2[n - 1]), py(traceLZ[n - 1]), 3, 0, 6.283);
            c.fill();
        }
    }

    /* ── Loop ───────────────────────────────────────────────────────────── */
    function frame() {
        if (running) {
            const substeps = P.kind === 'ca2d' ? 1 : 2;
            for (let i = 0; i < substeps; i++) {
                step();
                if (P.kind !== 'ca2d') paintRow();
            }
            if (P.kind === 'ca2d') paintGrid();
            measure();
        }
        // Painted even when paused, so a window resize cannot blank the card.
        draw();
        drawPhase(phaseCv);
        requestAnimationFrame(frame);
    }

    /* ── UI ─────────────────────────────────────────────────────────────── */
    const UI = `
      <div id="ca-head">
        <span class="ca-title">pyCA</span>
        <select id="ca-kind">
          <option value="eca">ECA — elementary</option>
          <option value="noisy">NoisyECA — flipped outputs</option>
          <option value="async">AsyncECA — broken clock</option>
          <option value="ica">ICA — rule vs. heat bath</option>
          <option value="ca2d">CA2D — outer-totalistic 2d</option>
        </select>
        <button class="ca-hbtn" id="ca-reset">Reset</button>
        <button class="ca-hbtn" id="ca-pause">Pause</button>
      </div>
      <div id="ca-stage">
        <canvas id="ca-canvas" width="640" height="420"></canvas>
        <div id="ca-controls" class="ca-ov">
        <div class="ca-ctl" data-kinds="eca noisy async ica">
          <label for="ca-rule">rule</label>
          <button type="button" id="ca-rule">110</button>
          <div id="ca-rulemenu"></div>
        </div>
        <div class="ca-ctl ca-slider" data-kinds="noisy">
          <label for="ca-noise">noise <span class="val" id="ca-noise-val">0.02</span></label>
          <input type="range" id="ca-noise" min="0" max="1" step="0.005" value="0.02">
        </div>
        <div class="ca-ctl ca-slider" data-kinds="async">
          <label for="ca-q">update fraction <span class="val" id="ca-q-val">0.75</span></label>
          <input type="range" id="ca-q" min="0" max="1" step="0.01" value="0.75">
        </div>
        <div class="ca-ctl ca-slider" data-kinds="ica">
          <label for="ca-temp">temperature <span class="val" id="ca-temp-val">1.00</span></label>
          <input type="range" id="ca-temp" min="0" max="4" step="0.02" value="1">
        </div>
        <div class="ca-ctl ca-slider" data-kinds="ica">
          <label for="ca-sf">stochastic fraction <span class="val" id="ca-sf-val">0.50</span></label>
          <input type="range" id="ca-sf" min="0" max="1" step="0.01" value="0.5">
        </div>
        <div class="ca-ctl" data-kinds="ca2d">
          <label for="ca-b">born with neighbors (B)</label>
          <input type="text" id="ca-b" value="3" size="5">
        </div>
        <div class="ca-ctl" data-kinds="ca2d">
          <label for="ca-s">survives with neighbors (S)</label>
          <input type="text" id="ca-s" value="23" size="5">
        </div>
        </div>
        <div id="ca-meters" class="ca-ov">
          <div id="ca-plotrow">
            <div id="ca-ylab"><span>\\(C_{LZ}\\)</span></div>
            <canvas id="ca-phase" width="160" height="160"></canvas>
          </div>
          <div id="ca-xlab">\\(h_2\\)</div>
        </div>
      </div>
    `;

    /* The docs load MathJax (sphinx.ext.mathjax), but it has already swept
     * the page by the time we inject this markup, so typeset by hand. */
    function typesetMath(el) {
        const M = window.MathJax;
        if (!M) return;
        if (M.startup && M.startup.promise) {
            M.startup.promise.then(() => M.typesetPromise([el])).catch(() => {});
        } else if (M.typesetPromise) {
            M.typesetPromise([el]).catch(() => {});
        }
    }

    function showControls() {
        document.querySelectorAll('#ca-controls .ca-ctl').forEach(el => {
            const kinds = el.getAttribute('data-kinds').split(' ');
            el.style.display = kinds.indexOf(P.kind) >= 0 ? '' : 'none';
        });
    }

    function parseCounts(text) {
        const out = [];
        for (const ch of text) {
            const d = ch.charCodeAt(0) - 48;
            if (d >= 0 && d <= 8) out.push(d);
        }
        return out;
    }

    function on(id, event, fn) {
        document.getElementById(id).addEventListener(event, fn);
    }

    function boot() {
        const root = document.getElementById('ca-app');
        if (!root) return;
        root.innerHTML = UI;
        typesetMath(root);

        canvas = document.getElementById('ca-canvas');
        ctx = canvas.getContext('2d');
        // The canvas fills the card; keep its buffer at display size so the
        // 2d grid's letterbox stays square.
        function resizeCanvas() {
            const w = canvas.clientWidth, h = canvas.clientHeight;
            if (w && h && (canvas.width !== w || canvas.height !== h)) {
                canvas.width = w;
                canvas.height = h;
            }
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        off1d = document.createElement('canvas');
        off1d.width = N; off1d.height = ROWS;
        off1dCtx = off1d.getContext('2d');
        off2d = document.createElement('canvas');
        off2d.width = GC; off2d.height = GR;
        off2dCtx = off2d.getContext('2d');
        rowImg = off1dCtx.createImageData(N, 1);
        gridImg = off2dCtx.createImageData(GC, GR);

        phaseCv = document.getElementById('ca-phase');

        seed();
        showControls();

        on('ca-kind', 'change', function () {
            P.kind = this.value;
            showControls();
            seed();
        });
        // All 256 rules in a custom drop-up: a native select's menu is
        // OS-drawn and spills out of the applet, so the options live in a
        // scrollable grid that opens above the panel, inside the stage.
        const ruleBtn = document.getElementById('ca-rule');
        const ruleMenu = document.getElementById('ca-rulemenu');
        for (let r = 0; r < 256; r++) {
            const o = document.createElement('button');
            o.type = 'button';
            o.className = 'ca-ruleopt' + (r === P.rule ? ' sel' : '');
            o.textContent = r;
            o.addEventListener('click', function (e) {
                e.stopPropagation();
                P.rule = r;
                ruleArr = buildRuleArray(r);
                ruleBtn.textContent = r;
                ruleMenu.querySelectorAll('.sel').forEach(
                    el => el.classList.remove('sel'));
                this.classList.add('sel');
                ruleMenu.style.display = 'none';
            });
            ruleMenu.appendChild(o);
        }
        ruleBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            const open = ruleMenu.style.display === 'grid';
            ruleMenu.style.display = open ? 'none' : 'grid';
            if (!open) {
                // Centre the selected rule; scrollTop, not scrollIntoView,
                // so the page itself never jumps.
                const sel = ruleMenu.querySelector('.sel');
                if (sel) {
                    ruleMenu.scrollTop = sel.offsetTop
                        - ruleMenu.clientHeight / 2 + sel.offsetHeight / 2;
                }
            }
        });
        document.addEventListener('click', function () {
            ruleMenu.style.display = 'none';
        });
        on('ca-noise', 'input', function () {
            P.noise = parseFloat(this.value);
            document.getElementById('ca-noise-val').textContent = P.noise.toFixed(3);
        });
        on('ca-q', 'input', function () {
            P.q = parseFloat(this.value);
            document.getElementById('ca-q-val').textContent = P.q.toFixed(2);
        });
        on('ca-temp', 'input', function () {
            P.temperature = parseFloat(this.value);
            document.getElementById('ca-temp-val').textContent = P.temperature.toFixed(2);
        });
        on('ca-sf', 'input', function () {
            P.stochfrac = parseFloat(this.value);
            document.getElementById('ca-sf-val').textContent = P.stochfrac.toFixed(2);
        });
        on('ca-b', 'change', function () {
            P.births = parseCounts(this.value);
            Bmask = countMask(P.births);
        });
        on('ca-s', 'change', function () {
            P.survivals = parseCounts(this.value);
            Smask = countMask(P.survivals);
        });
        on('ca-reset', 'click', seed);
        on('ca-pause', 'click', function () {
            running = !running;
            this.textContent = running ? 'Pause' : 'Resume';
        });

        requestAnimationFrame(frame);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
