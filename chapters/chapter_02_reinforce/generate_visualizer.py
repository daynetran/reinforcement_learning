import json

try:
    from .visualize import ARTIFACTS_DIR, DEFAULT_DATA_FILENAME
except ImportError:
    from visualize import ARTIFACTS_DIR, DEFAULT_DATA_FILENAME

with open(DEFAULT_DATA_FILENAME, "r", encoding="utf-8") as f:
    data = json.load(f)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CartPole REINFORCE Visualizer</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      --background: #0f172a;
      --card: #1e293b;
      --border: #334155;
      --foreground: #f8fafc;
      --muted-foreground: #94a3b8;
      --primary: #38bdf8;
      --primary-foreground: #0f172a;
      --accent: #22c55e;
      --danger: #ef4444;
    }}
    body {{
      background: var(--background);
      color: var(--foreground);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
  </style>
</head>
<body class="p-4 md:p-6 antialiased">
  <div class="max-w-4xl mx-auto space-y-4">
    <!-- Header -->
    <header class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[var(--border)] pb-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-[var(--foreground)] flex items-center gap-2">
          <span>CartPole REINFORCE Visualizer</span>
          <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Chapter 2</span>
        </h1>
        <p class="text-sm text-[var(--muted-foreground)]">
          Interactive policy inspection and physics simulation for REINFORCE on CartPole-v1
        </p>
      </div>
      <div id="statusBadge" class="self-start sm:self-auto px-3 py-1 rounded-lg text-xs font-medium bg-sky-500/10 text-sky-400 border border-sky-500/30">
        AI Policy: Active
      </div>
    </header>

    <!-- Visualizer & Controls Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Main Canvas Card (2 Cols) -->
      <div class="lg:col-span-2 bg-[var(--card)] border border-[var(--border)] rounded-2xl p-4 flex flex-col items-center justify-between shadow-lg">
        <div class="w-full flex items-center justify-between text-xs text-[var(--muted-foreground)] mb-2 px-1">
          <div class="flex items-center gap-4">
            <span>Step: <b id="stepCounter" class="text-[var(--foreground)] text-sm font-mono">0</b> / 500</span>
            <span>Reward: <b id="rewardCounter" class="text-emerald-400 text-sm font-mono">0.0</b></span>
          </div>
          <div class="flex items-center gap-2">
            <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span id="stateStatus" class="font-mono text-emerald-400">Balancing</span>
          </div>
        </div>

        <!-- Canvas Container -->
        <div class="relative w-full aspect-[2/1] bg-slate-950/60 rounded-xl overflow-hidden border border-slate-800/80 shadow-inner flex items-center justify-center">
          <canvas id="cartpoleCanvas" class="w-full h-full block"></canvas>
          <div id="failureOverlay" class="hidden absolute inset-0 bg-red-950/70 backdrop-blur-xs flex flex-col items-center justify-center text-center p-4">
            <span class="text-red-400 text-lg font-bold">CartPole Fell!</span>
            <span id="failReason" class="text-xs text-red-200 mt-1">Pole angle exceeded limits</span>
            <button onclick="resetSim()" class="mt-3 px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-semibold shadow transition">Restart</button>
          </div>
        </div>

        <!-- Playback Controls -->
        <div class="w-full mt-4 pt-3 border-t border-[var(--border)] flex flex-wrap items-center justify-between gap-3 text-xs">
          <div class="flex items-center gap-2">
            <button id="btnPlayPause" onclick="togglePlay()" class="px-3 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold transition flex items-center gap-1">
              <span id="playIcon">⏸️</span> <span id="playText">Pause</span>
            </button>
            <button onclick="resetSim()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition">
              🔄 Reset
            </button>
          </div>

          <!-- Nudge / Perturbation buttons -->
          <div class="flex items-center gap-2">
            <span class="text-[var(--muted-foreground)]">Perturb:</span>
            <button onclick="nudge(-0.06)" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-300 transition font-mono active:scale-95">💨 Left</button>
            <button onclick="nudge(0.06)" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-300 transition font-mono active:scale-95">Right 💨</button>
          </div>

          <div class="flex items-center gap-2 text-[var(--muted-foreground)]">
            <span>Speed:</span>
            <select id="speedSelect" onchange="setSpeed(this.value)" class="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs">
              <option value="0.5">0.5x</option>
              <option value="1" selected>1.0x</option>
              <option value="2">2.0x</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Telemetry & Policy Info (1 Col) -->
      <div class="space-y-4">
        <!-- Mode Card -->
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl p-4 shadow-lg space-y-3">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">Simulation Mode</h2>
          <div class="grid grid-cols-2 gap-2">
            <button onclick="setMode('live')" id="mode-live" class="mode-btn p-2 rounded-xl text-left border border-sky-500/50 bg-sky-500/10 text-sky-400 text-xs font-medium transition">
              <div class="font-semibold">🤖 Live AI</div>
              <div class="text-[10px] text-[var(--muted-foreground)]">PyTorch Policy</div>
            </button>
            <button onclick="setMode('trained_replay')" id="mode-trained_replay" class="mode-btn p-2 rounded-xl text-left border border-[var(--border)] bg-slate-800/40 text-slate-300 text-xs font-medium transition hover:bg-slate-800">
              <div class="font-semibold">📈 Trained Run</div>
              <div class="text-[10px] text-[var(--muted-foreground)]">500-step replay</div>
            </button>
            <button onclick="setMode('untrained_replay')" id="mode-untrained_replay" class="mode-btn p-2 rounded-xl text-left border border-[var(--border)] bg-slate-800/40 text-slate-300 text-xs font-medium transition hover:bg-slate-800">
              <div class="font-semibold">📉 Untrained</div>
              <div class="text-[10px] text-[var(--muted-foreground)]">18-step failure</div>
            </button>
            <button onclick="setMode('manual')" id="mode-manual" class="mode-btn p-2 rounded-xl text-left border border-[var(--border)] bg-slate-800/40 text-slate-300 text-xs font-medium transition hover:bg-slate-800">
              <div class="font-semibold">🎮 Manual</div>
              <div class="text-[10px] text-[var(--muted-foreground)]">Keys: ← / →</div>
            </button>
          </div>

          <!-- Manual Controls Banner (shown in manual mode) -->
          <div id="manualControls" class="hidden pt-2 border-t border-[var(--border)] flex gap-2">
            <button onclick="manualAction(0)" class="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-100 rounded-lg text-xs font-bold active:bg-sky-600 transition">◀ Push Left</button>
            <button onclick="manualAction(1)" class="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-100 rounded-lg text-xs font-bold active:bg-sky-600 transition">Push Right ▶</button>
          </div>
        </div>

        <!-- Policy Probability Distribution -->
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl p-4 shadow-lg space-y-3">
          <div class="flex items-center justify-between">
            <h2 class="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">Policy Output π(a|s)</h2>
            <span id="chosenActionText" class="text-xs font-mono font-bold text-sky-400">Action: -</span>
          </div>

          <div class="space-y-2 text-xs">
            <div>
              <div class="flex justify-between text-slate-300 mb-1">
                <span>◀ Action 0 (Left)</span>
                <span id="probLeftText" class="font-mono font-semibold">50.0%</span>
              </div>
              <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div id="probLeftBar" class="bg-sky-400 h-full rounded-full transition-all duration-75" style="width: 50%"></div>
              </div>
            </div>

            <div>
              <div class="flex justify-between text-slate-300 mb-1">
                <span>Action 1 (Right) ▶</span>
                <span id="probRightText" class="font-mono font-semibold">50.0%</span>
              </div>
              <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div id="probRightBar" class="bg-emerald-400 h-full rounded-full transition-all duration-75" style="width: 50%"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- State Vector Readouts -->
        <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl p-4 shadow-lg space-y-2">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-[var(--muted-foreground)]">State Telemetry [s_t]</h2>
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="bg-slate-950/40 p-2 rounded-lg border border-slate-800/80">
              <span class="text-[var(--muted-foreground)] block text-[10px]">Position x</span>
              <span id="valX" class="font-mono font-bold text-slate-200">0.00 m</span>
            </div>
            <div class="bg-slate-950/40 p-2 rounded-lg border border-slate-800/80">
              <span class="text-[var(--muted-foreground)] block text-[10px]">Velocity ẋ</span>
              <span id="valXDot" class="font-mono font-bold text-slate-200">0.00 m/s</span>
            </div>
            <div class="bg-slate-950/40 p-2 rounded-lg border border-slate-800/80">
              <span class="text-[var(--muted-foreground)] block text-[10px]">Pole Angle θ</span>
              <span id="valTheta" class="font-mono font-bold text-emerald-400">0.00°</span>
            </div>
            <div class="bg-slate-950/40 p-2 rounded-lg border border-slate-800/80">
              <span class="text-[var(--muted-foreground)] block text-[10px]">Angular Vel θ̇</span>
              <span id="valThetaDot" class="font-mono font-bold text-slate-200">0.00°/s</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const DATA = {json.dumps(data)};

    // Gymnasium CartPole physics constants
    const GRAVITY = 9.8;
    const MASSCART = 1.0;
    const MASSPOLE = 0.1;
    const TOTAL_MASS = MASSCART + MASSPOLE;
    const LENGTH = 0.5; // half-pole length
    const POLEMASS_LENGTH = MASSPOLE * LENGTH;
    const FORCE_MAG = 10.0;
    const TAU = 0.02; // seconds per time step
    const THETA_THRESHOLD = 12 * 2 * Math.PI / 360; // 12 degrees
    const X_THRESHOLD = 2.4;

    // Canvas setup
    const canvas = document.getElementById("cartpoleCanvas");
    const ctx = canvas.getContext("2d");

    let currentMode = "live";
    let isPlaying = true;
    let speed = 1.0;
    let replayIndex = 0;
    let stepCount = 0;
    let totalReward = 0.0;
    let lastAction = null;

    // State: [x, x_dot, theta, theta_dot]
    let state = [0.0, 0.0, 0.01, 0.0];

    // Resize canvas for sharp rendering
    function resizeCanvas() {{
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.resetTransform();
      ctx.scale(dpr, dpr);
    }}
    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();

    // Forward pass for trained PyTorch MLP (4 -> 64 -> 2)
    function evaluatePolicy(s) {{
      const w1 = DATA.weights.fc1_weight; // [64, 4]
      const b1 = DATA.weights.fc1_bias;   // [64]
      const w2 = DATA.weights.fc2_weight; // [2, 64]
      const b2 = DATA.weights.fc2_bias;   // [2]

      // Hidden layer with ReLU
      const h = new Array(64);
      for (let i = 0; i < 64; i++) {{
        let sum = b1[i];
        sum += w1[i][0] * s[0];
        sum += w1[i][1] * s[1];
        sum += w1[i][2] * s[2];
        sum += w1[i][3] * s[3];
        h[i] = Math.max(0, sum); // ReLU
      }}

      // Output layer (logits)
      const logits = [b2[0], b2[1]];
      for (let j = 0; j < 64; j++) {{
        logits[0] += w2[0][j] * h[j];
        logits[1] += w2[1][j] * h[j];
      }}

      // Softmax
      const maxLogit = Math.max(logits[0], logits[1]);
      const exp0 = Math.exp(logits[0] - maxLogit);
      const exp1 = Math.exp(logits[1] - maxLogit);
      const sumExp = exp0 + exp1;
      const probs = [exp0 / sumExp, exp1 / sumExp];
      const action = logits[1] > logits[0] ? 1 : 0;
      return {{ action, probs }};
    }}

    // Step physics (CartPole-v1 Euler dynamics)
    function stepPhysics(action) {{
      let [x, x_dot, theta, theta_dot] = state;
      const force = action === 1 ? FORCE_MAG : -FORCE_MAG;

      const costheta = Math.cos(theta);
      const sintheta = Math.sin(theta);

      const temp = (force + POLEMASS_LENGTH * theta_dot * theta_dot * sintheta) / TOTAL_MASS;
      const thetaacc = (GRAVITY * sintheta - costheta * temp) / (LENGTH * (4.0 / 3.0 - MASSPOLE * costheta * costheta / TOTAL_MASS));
      const xacc = temp - POLEMASS_LENGTH * thetaacc * costheta / TOTAL_MASS;

      // Euler integration
      x = x + TAU * x_dot;
      x_dot = x_dot + TAU * xacc;
      theta = theta + TAU * theta_dot;
      theta_dot = theta_dot + TAU * thetaacc;

      state = [x, x_dot, theta, theta_dot];

      const terminated = (x < -X_THRESHOLD || x > X_THRESHOLD || theta < -THETA_THRESHOLD || theta > THETA_THRESHOLD);
      const truncated = stepCount >= 500;
      return {{ terminated, truncated }};
    }}

    function nudge(dTheta) {{
      state[2] += dTheta;
      state[3] += dTheta * 2.0;
    }}

    function manualAction(a) {{
      if (currentMode !== "manual") return;
      lastAction = a;
      executeStep(a, [a === 0 ? 1.0 : 0.0, a === 1 ? 1.0 : 0.0]);
    }}

    window.addEventListener("keydown", (e) => {{
      if (currentMode === "manual") {{
        if (e.key === "ArrowLeft") manualAction(0);
        if (e.key === "ArrowRight") manualAction(1);
      }}
    }});

    function resetSim() {{
      document.getElementById("failureOverlay").classList.add("hidden");
      stepCount = 0;
      totalReward = 0.0;
      replayIndex = 0;
      lastAction = null;

      if (currentMode === "live" || currentMode === "manual") {{
        state = [(Math.random() - 0.5) * 0.05, 0.0, (Math.random() - 0.5) * 0.05, 0.0];
      }} else if (currentMode === "trained_replay") {{
        const traj = DATA.trained_trajectory;
        state = [...traj[0].state];
      }} else if (currentMode === "untrained_replay") {{
        const traj = DATA.untrained_trajectory;
        state = [...traj[0].state];
      }}
      updateHUD([0.5, 0.5], null);
    }}

    function setMode(mode) {{
      currentMode = mode;
      document.querySelectorAll(".mode-btn").forEach(btn => {{
        btn.classList.remove("border-sky-500/50", "bg-sky-500/10", "text-sky-400");
        btn.classList.add("border-[var(--border)]", "bg-slate-800/40", "text-slate-300");
      }});
      const activeBtn = document.getElementById("mode-" + mode);
      if (activeBtn) {{
        activeBtn.classList.remove("border-[var(--border)]", "bg-slate-800/40", "text-slate-300");
        activeBtn.classList.add("border-sky-500/50", "bg-sky-500/10", "text-sky-400");
      }}

      const badge = document.getElementById("statusBadge");
      const manualControls = document.getElementById("manualControls");

      if (mode === "live") {{
        badge.textContent = "AI Policy: Active (Live PyTorch)";
        badge.className = "px-3 py-1 rounded-lg text-xs font-medium bg-sky-500/10 text-sky-400 border border-sky-500/30";
        manualControls.classList.add("hidden");
      }} else if (mode === "trained_replay") {{
        badge.textContent = "Replay: Trained (500 Steps)";
        badge.className = "px-3 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30";
        manualControls.classList.add("hidden");
      }} else if (mode === "untrained_replay") {{
        badge.textContent = "Replay: Untrained (18 Steps)";
        badge.className = "px-3 py-1 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30";
        manualControls.classList.add("hidden");
      }} else if (mode === "manual") {{
        badge.textContent = "Control: Manual (Arrow Keys)";
        badge.className = "px-3 py-1 rounded-lg text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/30";
        manualControls.classList.remove("hidden");
      }}

      resetSim();
    }}

    function togglePlay() {{
      isPlaying = !isPlaying;
      document.getElementById("playIcon").textContent = isPlaying ? "⏸️" : "▶️";
      document.getElementById("playText").textContent = isPlaying ? "Pause" : "Play";
    }}

    function setSpeed(v) {{
      speed = parseFloat(v);
    }}

    function updateHUD(probs, action) {{
      document.getElementById("stepCounter").textContent = stepCount;
      document.getElementById("rewardCounter").textContent = totalReward.toFixed(1);

      const [x, x_dot, theta, theta_dot] = state;
      document.getElementById("valX").textContent = x.toFixed(2) + " m";
      document.getElementById("valXDot").textContent = x_dot.toFixed(2) + " m/s";
      const deg = theta * 180 / Math.PI;
      const thetaEl = document.getElementById("valTheta");
      thetaEl.textContent = deg.toFixed(2) + "°";
      thetaEl.className = "font-mono font-bold " + (Math.abs(deg) > 9 ? "text-amber-400" : "text-emerald-400");
      document.getElementById("valThetaDot").textContent = (theta_dot * 180 / Math.PI).toFixed(1) + "°/s";

      if (probs) {{
        const p0 = (probs[0] * 100).toFixed(1);
        const p1 = (probs[1] * 100).toFixed(1);
        document.getElementById("probLeftText").textContent = p0 + "%";
        document.getElementById("probLeftBar").style.width = p0 + "%";
        document.getElementById("probRightText").textContent = p1 + "%";
        document.getElementById("probRightBar").style.width = p1 + "%";
      }}

      const actText = document.getElementById("chosenActionText");
      if (action !== null) {{
        actText.textContent = action === 0 ? "Action: ◀ Left" : "Action: Right ▶";
        actText.className = "text-xs font-mono font-bold " + (action === 0 ? "text-sky-400" : "text-emerald-400");
      }}
    }}

    function executeStep(action, probs) {{
      lastAction = action;
      stepCount++;
      totalReward += 1.0;
      const {{ terminated, truncated }} = stepPhysics(action);
      updateHUD(probs, action);

      if (terminated || truncated) {{
        document.getElementById("failureOverlay").classList.remove("hidden");
        document.getElementById("failReason").textContent =
          terminated ? (Math.abs(state[0]) > X_THRESHOLD ? "Cart went off track (|x| > 2.4m)" : "Pole tilted too far (|θ| > 12°)")
                     : "Episode reached max limit (500 steps)!";
        return false;
      }}
      return true;
    }}

    function draw() {{
      const rect = canvas.getBoundingClientRect();
      const w = rect.width;
      const h = rect.height;

      ctx.clearRect(0, 0, w, h);

      // Coordinate scaling
      // World limits: x from -2.4 to +2.4
      const scale = w / (2 * X_THRESHOLD * 1.15);
      const originX = w / 2;
      const originY = h * 0.72;

      const [x, x_dot, theta, theta_dot] = state;

      // Draw track
      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(w * 0.05, originY + 18);
      ctx.lineTo(w * 0.95, originY + 18);
      ctx.stroke();

      // Track limits indicators
      ctx.strokeStyle = "#ef444466";
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      const leftLimit = originX - X_THRESHOLD * scale;
      const rightLimit = originX + X_THRESHOLD * scale;
      ctx.beginPath();
      ctx.moveTo(leftLimit, originY - 60);
      ctx.lineTo(leftLimit, originY + 25);
      ctx.moveTo(rightLimit, originY - 60);
      ctx.lineTo(rightLimit, originY + 25);
      ctx.stroke();
      ctx.setLineDash([]);

      // Cart position
      const cartW = 70;
      const cartH = 34;
      const cartX = originX + x * scale;
      const cartY = originY;

      // Draw Cart shadow
      ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
      ctx.beginPath();
      ctx.ellipse(cartX, originY + 16, cartW * 0.55, 6, 0, 0, Math.PI * 2);
      ctx.fill();

      // Cart body
      const gradient = ctx.createLinearGradient(cartX - cartW/2, cartY - cartH/2, cartX + cartW/2, cartY + cartH/2);
      gradient.addColorStop(0, "#0284c7");
      gradient.addColorStop(1, "#0369a1");
      ctx.fillStyle = gradient;
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 1.5;

      ctx.beginPath();
      ctx.roundRect(cartX - cartW / 2, cartY - cartH / 2, cartW, cartH, 6);
      ctx.fill();
      ctx.stroke();

      // Cart wheels
      ctx.fillStyle = "#0f172a";
      ctx.strokeStyle = "#64748b";
      ctx.lineWidth = 2;
      [-cartW * 0.3, cartW * 0.3].forEach(offset => {{
        ctx.beginPath();
        ctx.arc(cartX + offset, cartY + cartH / 2, 7, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
      }});

      // Force indicator arrow
      if (lastAction !== null) {{
        ctx.fillStyle = lastAction === 1 ? "#22c55e" : "#38bdf8";
        ctx.beginPath();
        const arrowX = lastAction === 1 ? cartX + cartW / 2 + 8 : cartX - cartW / 2 - 8;
        const arrowDir = lastAction === 1 ? 1 : -1;
        ctx.moveTo(arrowX, cartY);
        ctx.lineTo(arrowX + arrowDir * 14, cartY - 7);
        ctx.lineTo(arrowX + arrowDir * 14, cartY + 7);
        ctx.closePath();
        ctx.fill();
      }}

      // Pole
      const poleLen = LENGTH * 2 * scale * 1.8; // visible length
      const poleThickness = 8;
      const axleX = cartX;
      const axleY = cartY - 6;

      const tipX = axleX + poleLen * Math.sin(theta);
      const tipY = axleY - poleLen * Math.cos(theta);

      // Pole stroke
      const poleGrad = ctx.createLinearGradient(axleX, axleY, tipX, tipY);
      poleGrad.addColorStop(0, "#fbbf24");
      poleGrad.addColorStop(1, "#f59e0b");
      ctx.strokeStyle = poleGrad;
      ctx.lineWidth = poleThickness;
      ctx.lineCap = "round";
      ctx.beginPath();
      ctx.moveTo(axleX, axleY);
      ctx.lineTo(tipX, tipY);
      ctx.stroke();

      // Axle center pin
      ctx.fillStyle = "#f8fafc";
      ctx.beginPath();
      ctx.arc(axleX, axleY, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#0284c7";
      ctx.beginPath();
      ctx.arc(axleX, axleY, 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Pole tip mass
      ctx.fillStyle = "#ef4444";
      ctx.beginPath();
      ctx.arc(tipX, tipY, 6, 0, Math.PI * 2);
      ctx.fill();
    }}

    let lastTime = 0;
    let accumulatedTime = 0;

    function loop(timestamp) {{
      if (!lastTime) lastTime = timestamp;
      const dt = (timestamp - lastTime) / 1000;
      lastTime = timestamp;

      if (isPlaying) {{
        accumulatedTime += dt * speed;
        while (accumulatedTime >= TAU) {{
          accumulatedTime -= TAU;

          if (currentMode === "live") {{
            const {{ action, probs }} = evaluatePolicy(state);
            const ok = executeStep(action, probs);
            if (!ok) break;
          }} else if (currentMode === "trained_replay") {{
            const traj = DATA.trained_trajectory;
            if (replayIndex < traj.length) {{
              const item = traj[replayIndex];
              state = [...item.state];
              lastAction = item.action;
              stepCount = replayIndex + 1;
              totalReward = stepCount;
              updateHUD(item.probs, item.action);
              replayIndex++;
            }} else {{
              replayIndex = 0; // loop replay
            }}
          }} else if (currentMode === "untrained_replay") {{
            const traj = DATA.untrained_trajectory;
            if (replayIndex < traj.length) {{
              const item = traj[replayIndex];
              state = [...item.state];
              lastAction = item.action;
              stepCount = replayIndex + 1;
              totalReward = stepCount;
              updateHUD([0.5, 0.5], item.action);
              replayIndex++;
            }} else {{
              document.getElementById("failureOverlay").classList.remove("hidden");
              document.getElementById("failReason").textContent = "Untrained policy fell after " + traj.length + " steps!";
              break;
            }}
          }}
        }}
      }}

      draw();
      requestAnimationFrame(loop);
    }}

    resetSim();
    requestAnimationFrame(loop);
  </script>
</body>
</html>
"""

output_path = ARTIFACTS_DIR / "cartpole_visualizer.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated visualizer HTML at {output_path}")
