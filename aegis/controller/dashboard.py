"""
Aegis AI Gateway - Built-in Live Web Dashboard
Served at /dashboard to provide real-time telemetry, cache hit ratios,
and an interactive semantic testing playground.
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aegis AI Gateway • Control Plane</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #090d16; }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .glow-blue { box-shadow: 0 0 25px -5px rgba(59, 130, 246, 0.2); }
    .glow-green { box-shadow: 0 0 25px -5px rgba(16, 185, 129, 0.25); }
  </style>
</head>
<body class="text-slate-100 min-h-screen antialiased flex flex-col">
  <!-- Top Navigation -->
  <header class="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-bold font-mono text-white text-lg shadow-lg shadow-blue-500/30">
          Æ
        </div>
        <div>
          <h1 class="text-base font-bold tracking-tight text-white flex items-center gap-2">
            AEGIS GATEWAY
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-semibold">ACTIVE</span>
          </h1>
          <p class="text-xs text-slate-400">High-Throughput Reverse Proxy & Semantic Cache</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a href="/docs" target="_blank" class="text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition flex items-center gap-1.5">
          <span>API Docs</span>
          <span class="text-[10px]">↗</span>
        </a>
        <button onclick="flushCache()" class="text-xs font-mono px-3 py-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/50 text-rose-300 border border-rose-800/50 transition">
          Flush Cache
        </button>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-8">
    
    <!-- 4 Key Metrics Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Card 1 -->
      <div class="p-5 rounded-xl bg-slate-900/50 border border-slate-800/80 glow-green flex flex-col justify-between">
        <div class="flex items-center justify-between text-slate-400 text-xs font-mono">
          <span>ESTIMATED SAVINGS</span>
          <span class="text-emerald-400">USD</span>
        </div>
        <div class="mt-3">
          <div id="stat-savings" class="text-3xl font-bold font-mono text-emerald-400">$0.0000</div>
          <p class="text-xs text-slate-400 mt-1">Avoided OpenAI / Gemini inference spend</p>
        </div>
      </div>

      <!-- Card 2 -->
      <div class="p-5 rounded-xl bg-slate-900/50 border border-slate-800/80 glow-blue flex flex-col justify-between">
        <div class="flex items-center justify-between text-slate-400 text-xs font-mono">
          <span>CACHE HIT RATIO</span>
          <span id="stat-hits" class="text-blue-400">0 / 0</span>
        </div>
        <div class="mt-3">
          <div id="stat-ratio" class="text-3xl font-bold font-mono text-blue-400">0.0%</div>
          <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
            <div id="stat-bar" class="bg-blue-500 h-full transition-all duration-500" style="width: 0%"></div>
          </div>
        </div>
      </div>

      <!-- Card 3 -->
      <div class="p-5 rounded-xl bg-slate-900/50 border border-slate-800/80 flex flex-col justify-between">
        <div class="flex items-center justify-between text-slate-400 text-xs font-mono">
          <span>TOKENS SAVED</span>
          <span class="text-indigo-400">INTERCEPTED</span>
        </div>
        <div class="mt-3">
          <div id="stat-tokens" class="text-3xl font-bold font-mono text-indigo-400">0</div>
          <p class="text-xs text-slate-400 mt-1">Zero tokens billed upstream</p>
        </div>
      </div>

      <!-- Card 4 -->
      <div class="p-5 rounded-xl bg-slate-900/50 border border-slate-800/80 flex flex-col justify-between">
        <div class="flex items-center justify-between text-slate-400 text-xs font-mono">
          <span>CIRCUIT BREAKERS</span>
          <span class="text-emerald-400">CASCADE</span>
        </div>
        <div class="mt-3 space-y-1.5" id="circuit-list">
          <div class="flex items-center justify-between text-xs font-mono">
            <span class="text-slate-300">Gemini 3.5:</span>
            <span class="text-emerald-400 font-bold">HEALTHY</span>
          </div>
          <div class="flex items-center justify-between text-xs font-mono">
            <span class="text-slate-300">Mock Fallback:</span>
            <span class="text-blue-400 font-bold">READY</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Playground & Real-Time Test Console -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- Left Column: Interactive Query Sandbox -->
      <div class="lg:col-span-7 bg-slate-900/60 rounded-xl border border-slate-800 p-6 flex flex-col">
        <div class="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
          <div>
            <h2 class="text-sm font-bold text-white uppercase tracking-wider font-mono">Semantic Interception Sandbox</h2>
            <p class="text-xs text-slate-400">Test how Aegis detects semantically similar prompts</p>
          </div>
          <span class="text-xs font-mono px-2 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">Live Gateway</span>
        </div>

        <!-- Preset buttons -->
        <div class="mb-4">
          <span class="text-[11px] font-mono text-slate-400 block mb-2">QUICK TEST CLUSTERS:</span>
          <div class="flex flex-wrap gap-2 text-xs">
            <button onclick="setPrompt('How do I reset my password?')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/80 transition font-mono text-[11px]">
              1. Reset Password (Original)
            </button>
            <button onclick="setPrompt('Forgot my password, how to change it?')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/80 transition font-mono text-[11px]">
              2. Forgot Password (Rephrased)
            </button>
            <button onclick="setPrompt('What is recursion in computer programming?')" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/80 transition font-mono text-[11px]">
              3. Recursion Concept
            </button>
          </div>
        </div>

        <!-- Input Area -->
        <div class="space-y-3 flex-1 flex flex-col">
          <textarea id="test-input" rows="3" placeholder="Enter a prompt to send through Aegis Gateway..." class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm font-mono text-slate-200 focus:outline-none focus:border-blue-500 transition resize-none"></textarea>
          
          <div class="flex items-center justify-between">
            <span class="text-xs text-slate-500 font-mono">Target: /v1/chat/completions</span>
            <button id="send-btn" onclick="sendTestQuery()" class="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold font-mono tracking-wide shadow-lg shadow-blue-500/20 transition flex items-center gap-2">
              <span>Execute Query</span>
              <span>→</span>
            </button>
          </div>

          <!-- Result View -->
          <div id="test-result-box" class="hidden mt-4 p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-3 font-mono text-xs">
            <div class="flex items-center justify-between pb-2 border-b border-slate-800">
              <div class="flex items-center gap-2">
                <span id="res-badge" class="px-2 py-0.5 rounded font-bold uppercase text-[10px]">HIT</span>
                <span id="res-provider" class="text-slate-400">provider</span>
              </div>
              <div class="text-slate-400 flex items-center gap-3">
                <span>Latency: <strong id="res-latency" class="text-white">0ms</strong></span>
              </div>
            </div>
            <div id="res-content" class="text-slate-300 whitespace-pre-wrap max-h-48 overflow-y-auto leading-relaxed"></div>
          </div>
        </div>
      </div>

      <!-- Right Column: Recent Query Activity Feed -->
      <div class="lg:col-span-5 bg-slate-900/60 rounded-xl border border-slate-800 p-6 flex flex-col">
        <div class="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
          <div>
            <h2 class="text-sm font-bold text-white uppercase tracking-wider font-mono">Live Traffic Stream</h2>
            <p class="text-xs text-slate-400">Incoming inference calls intercepted by Aegis</p>
          </div>
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        </div>

        <div class="flex-1 overflow-y-auto max-h-[380px] space-y-2.5" id="recent-feed">
          <div class="text-center py-12 text-slate-500 text-xs font-mono">
            No queries logged yet.<br>Send a prompt from the sandbox or via API.
          </div>
        </div>
      </div>

    </div>
  </main>

  <footer class="border-t border-slate-800 py-4 text-center text-xs text-slate-500 font-mono">
    Aegis AI Gateway • 100% OpenAI Wire-Compatible • Open Source on <a href="https://github.com/TechTonicShift/aegis" target="_blank" class="text-blue-400 underline">GitHub</a>
  </footer>

  <script>
    function setPrompt(txt) {
      document.getElementById('test-input').value = txt;
    }

    async function fetchMetrics() {
      try {
        const resp = await fetch('/metrics');
        const data = await resp.json();
        const cache = data.cache || {};

        document.getElementById('stat-savings').innerText = '$' + (cache.estimated_cost_saved_usd || 0).toFixed(4);
        document.getElementById('stat-hits').innerText = (cache.total_hits || 0) + ' / ' + (cache.total_queries || 0);
        document.getElementById('stat-ratio').innerText = (cache.hit_ratio_percent || 0).toFixed(1) + '%';
        document.getElementById('stat-bar').style.width = (cache.hit_ratio_percent || 0) + '%';
        document.getElementById('stat-tokens').innerText = (cache.total_tokens_saved || 0).toLocaleString();

        // Update circuit breakers
        const circuits = data.circuit_breakers || {};
        let circuitHtml = '';
        for (const [name, c] of Object.entries(circuits)) {
          const isHealthy = c.state === 'CLOSED';
          const color = isHealthy ? 'text-emerald-400' : 'text-rose-400';
          circuitHtml += `
            <div class="flex items-center justify-between text-xs font-mono">
              <span class="text-slate-300">${name}:</span>
              <span class="${color} font-bold">${c.state}</span>
            </div>
          `;
        }
        if (circuitHtml) {
          document.getElementById('circuit-list').innerHTML = circuitHtml;
        }

        // Update recent queries
        const queries = cache.recent_queries || [];
        if (queries.length > 0) {
          let qHtml = '';
          queries.forEach(q => {
            const isHit = q.cached;
            const badgeClass = isHit 
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' 
              : 'bg-amber-500/10 text-amber-400 border border-amber-500/30';
            const badgeText = isHit ? 'CACHE HIT' : 'LIVE MISS';

            qHtml += `
              <div class="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-xs font-mono space-y-1 hover:border-slate-700 transition">
                <div class="flex items-center justify-between">
                  <span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${badgeClass}">${badgeText}</span>
                  <span class="text-slate-500 text-[11px]">${q.time}</span>
                </div>
                <div class="text-slate-200 text-xs truncate">"${q.prompt}"</div>
                <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                  <span>${q.provider}</span>
                  <span class="text-white font-semibold">${q.latency_ms} ms</span>
                </div>
              </div>
            `;
          });
          document.getElementById('recent-feed').innerHTML = qHtml;
        }
      } catch (err) {
        console.error('Failed to fetch metrics:', err);
      }
    }

    async function sendTestQuery() {
      const input = document.getElementById('test-input');
      const btn = document.getElementById('send-btn');
      const prompt = input.value.trim();
      if (!prompt) return;

      btn.disabled = true;
      btn.innerText = 'Routing...';

      try {
        const t0 = performance.now();
        const resp = await fetch('/v1/chat/completions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: [{ role: 'user', content: prompt }]
          })
        });
        const elapsed = (performance.now() - t0).toFixed(1);
        const data = await resp.json();

        const isHit = data.cached || false;
        const resultBox = document.getElementById('test-result-box');
        const badge = document.getElementById('res-badge');
        
        resultBox.classList.remove('hidden');
        badge.innerText = isHit ? 'CACHE HIT' : 'CACHE MISS';
        badge.className = isHit 
          ? 'px-2 py-0.5 rounded font-bold uppercase text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
          : 'px-2 py-0.5 rounded font-bold uppercase text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/30';

        document.getElementById('res-provider').innerText = data.provider_used || 'gateway';
        document.getElementById('res-latency').innerText = (data.latency_ms || elapsed) + ' ms';
        document.getElementById('res-content').innerText = data.choices[0].message.content;

        fetchMetrics();
      } catch (err) {
        alert('Query failed: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>Execute Query</span><span>→</span>';
      }
    }

    async function flushCache() {
      if (confirm('Clear the entire in-memory vector cache?')) {
        await fetch('/cache/clear', { method: 'POST' });
        fetchMetrics();
      }
    }

    // Auto poll metrics every 2.5 seconds
    fetchMetrics();
    setInterval(fetchMetrics, 2500);
  </script>
</body>
</html>
"""
