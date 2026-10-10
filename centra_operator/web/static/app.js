// CentrAlign Operator - Mission Control Frontend Controller
let currentSessionId = null;
let pollTimer = null;

const scenarios = {
  onboarding: "Onboard Alex Morgan as Senior Frontend Engineer starting Monday, set up BambooHR, provision GitHub & Okta SSO, generate compliance checklist, and send welcome email.",
  refund: "Process customer refund request for Zendesk Ticket #8841 ($75.00) from billing-support@cloudscale.tech, verify Stripe charge, obtain manager approval, and reconcile Q3 ledger.",
  offboarding: "Execute SOC2 access revocation and offboarding for Alex Morgan, audit permissions, de-provision Okta SSO & GitHub organization access, and output cryptographic audit certificate.",
  recovery: "Navigate to internal HR onboarding portal with updated selector fallback, submit form, and verify submission state."
};

function loadScenario(key) {
  const input = document.getElementById("goal-input");
  input.value = scenarios[key] || "";
  dispatchGoal();
}

async function dispatchGoal() {
  const input = document.getElementById("goal-input");
  const goal = input.value.trim();
  if (!goal) return;

  const btn = document.getElementById("dispatch-btn");
  btn.disabled = true;
  btn.innerHTML = `<span class="animate-spin">?</span><span>Planning...</span>`;

  try {
    const res = await fetch("/api/goals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal, auto_approve: false })
    });
    const state = await res.json();
    currentSessionId = state.session_id;
    renderState(state);
    startPolling();
  } catch (err) {
    console.error("Error dispatching goal:", err);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="play" class="w-4 h-4 fill-white"></i><span>Execute Goal</span>`;
    lucide.createIcons();
  }
}

function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(async () => {
    if (!currentSessionId) return;
    try {
      const res = await fetch(`/api/session/${currentSessionId}`);
      if (res.ok) {
        const state = await res.json();
        renderState(state);
        if (state.status === "COMPLETED" || state.status === "FAILED") {
          clearInterval(pollTimer);
        }
      }
    } catch (e) {
      console.error(e);
    }
  }, 1000);
}

function renderState(state) {
  // Update status badge
  const badge = document.getElementById("system-status-badge");
  if (state.status === "AWAITING_APPROVAL") {
    badge.className = "px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold flex items-center space-x-1.5";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span><span class="pl-2">AWAITING HITL APPROVAL</span>`;
  } else if (state.status === "RUNNING" || state.status === "PLANNING") {
    badge.className = "px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold flex items-center space-x-1.5";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span><span class="pl-2">AUTONOMOUS EXECUTION</span>`;
  } else if (state.status === "COMPLETED") {
    badge.className = "px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center space-x-1.5";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400"></span><span class="pl-2">GOAL VERIFIED &amp; COMPLETED</span>`;
  }

  // Disambiguated intent
  if (state.disambiguated_intent) {
    document.getElementById("intent-summary-box").classList.remove("hidden");
    document.getElementById("disambiguated-intent-text").textContent = state.disambiguated_intent;
  }
  if (state.matched_sop_id) {
    const sopTag = document.getElementById("sop-tag");
    sopTag.classList.remove("hidden");
    sopTag.textContent = state.matched_sop_id;
  }

  // Render DAG Nodes
  const dagContainer = document.getElementById("dag-container");
  if (state.tasks && state.tasks.length > 0) {
    dagContainer.innerHTML = state.tasks.map((task, idx) => {
      let statusColor = "border-slate-800 bg-slate-900/60 text-slate-400";
      let badgeHtml = `<span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 uppercase font-mono">${task.status}</span>`;
      let extraClass = "";

      if (task.status === "RUNNING" || task.status === "VERIFYING") {
        statusColor = "border-cyan-500 bg-cyan-950/20 text-cyan-300";
        badgeHtml = `<span class="text-[10px] px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 uppercase font-mono animate-pulse">RUNNING</span>`;
        extraClass = "pulse-running";
      } else if (task.status === "AWAITING_APPROVAL") {
        statusColor = "border-amber-500 bg-amber-950/20 text-amber-300";
        badgeHtml = `<button onclick="openHitlModal('${task.id}')" class="text-[10px] px-2.5 py-1 rounded bg-amber-500 text-slate-950 font-bold uppercase hover:bg-amber-400 transition animate-bounce">Review Required</button>`;
      } else if (task.status === "COMPLETED") {
        statusColor = "border-emerald-500/40 bg-emerald-950/10 text-emerald-300";
        badgeHtml = `<span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 uppercase font-mono">? VERIFIED</span>`;
      } else if (task.status === "FAILED") {
        statusColor = "border-rose-500/50 bg-rose-950/20 text-rose-300";
        badgeHtml = `<span class="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 uppercase font-mono">FAILED</span>`;
      }

      const riskTag = task.risk_level === "HIGH" ? `<span class="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">HIGH RISK</span>` : "";

      return `
        <div class="p-3.5 rounded-xl border ${statusColor} ${extraClass} transition-all space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="font-mono text-slate-500">#${idx + 1}</span>
              <h4 class="font-semibold text-slate-100">${task.title}</h4>
              ${riskTag}
            </div>
            <div>${badgeHtml}</div>
          </div>
          <p class="text-slate-400 text-[11px] font-sans">${task.description}</p>
          <div class="flex items-center justify-between text-[11px] text-slate-500 font-mono pt-1">
            <span class="flex items-center space-x-1">
              <i data-lucide="wrench" class="w-3 h-3 text-cyan-400"></i>
              <span>tool: <b>${task.tool_name}</b></span>
            </span>
            ${task.verification_contract ? `<span class="text-slate-400 italic">Invariant: ${task.verification_contract.verification_query.slice(0, 40)}...</span>` : ""}
          </div>
          ${task.recovery_notes ? `<div class="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[10px] font-mono">?? ${task.recovery_notes}</div>` : ""}
        </div>
      `;
    }).join("");
  }

  // Render Trace Logs
  const logConsole = document.getElementById("log-console");
  if (state.trace_logs && state.trace_logs.length > 0) {
    document.getElementById("log-count").textContent = `${state.trace_logs.length} events`;
    logConsole.innerHTML = state.trace_logs.map(log => {
      let stageBadge = `<span class="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">[${log.stage}]</span>`;
      let msgColor = "text-slate-300";

      if (log.level === "SUCCESS") msgColor = "text-emerald-400 font-semibold";
      if (log.level === "WARNING") msgColor = "text-amber-400";
      if (log.level === "ERROR") msgColor = "text-rose-400 font-bold";
      if (log.level === "HITL") msgColor = "text-amber-300 font-bold";

      return `
        <div class="leading-relaxed border-b border-slate-900 pb-1">
          <span class="text-slate-600 text-[10px]">${new Date(log.timestamp * 1000).toLocaleTimeString()}</span>
          ${stageBadge}
          <span class="${msgColor}">${log.message}</span>
        </div>
      `;
    }).join("");
    logConsole.scrollTop = logConsole.scrollHeight;
  }

  // Check for active HITL
  if (state.pending_approvals && state.pending_approvals.length > 0) {
    openHitlModal(state.pending_approvals[0].task_id);
  } else {
    closeHitlModal();
  }

  // Evidence section
  if (state.status === "COMPLETED" && state.evidence_summary) {
    document.getElementById("evidence-section").classList.remove("hidden");
  }

  lucide.createIcons();
}

let activeApprovalTaskId = null;
let activeApprovalId = null;

async function openHitlModal(taskId) {
  if (!currentSessionId) return;
  const res = await fetch(`/api/session/${currentSessionId}`);
  const state = await res.json();
  const task = state.tasks.find(t => t.id === taskId);
  if (!task || !task.approval_request) return;

  activeApprovalTaskId = taskId;
  activeApprovalId = task.approval_request.id;

  document.getElementById("hitl-task-title").textContent = task.title;
  document.getElementById("hitl-reason").textContent = task.approval_request.reason;
  document.getElementById("hitl-blast").textContent = task.approval_request.blast_radius;
  document.getElementById("hitl-params").textContent = JSON.stringify(task.params, null, 2);
  document.getElementById("hitl-risk-tag").textContent = task.risk_level + " RISK";

  document.getElementById("hitl-modal").classList.remove("hidden");
  lucide.createIcons();
}

function closeHitlModal() {
  document.getElementById("hitl-modal").classList.add("hidden");
}

async function submitApproval(decision) {
  if (!currentSessionId || !activeApprovalId) return;
  const feedback = document.getElementById("hitl-feedback-input").value;

  try {
    const res = await fetch(`/api/session/${currentSessionId}/approvals/${activeApprovalId}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision, feedback })
    });
    const state = await res.json();
    closeHitlModal();
    renderState(state);
  } catch (e) {
    console.error(e);
  }
}

async function openMemoryModal() {
  const modal = document.getElementById("memory-modal");
  const content = document.getElementById("memory-content");
  modal.classList.remove("hidden");

  try {
    const res = await fetch("/api/memory");
    const mem = await res.json();

    content.innerHTML = `
      <div class="space-y-4">
        <div>
          <h4 class="font-bold text-cyan-400 uppercase tracking-wide text-xs mb-2">Standard Operating Procedures (SOPs)</h4>
          <div class="space-y-2">
            ${mem.sops.map(s => `
              <div class="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                <div class="flex items-center justify-between">
                  <span class="font-mono text-cyan-400 font-bold">${s.id}</span>
                  <span class="text-slate-500">${s.department}</span>
                </div>
                <div class="font-semibold text-slate-200">${s.title}</div>
                <p class="text-slate-400 text-[11px]">${s.description}</p>
                <div class="text-amber-400/90 text-[10px] font-mono mt-1">Policy: ${s.policy_notes}</div>
              </div>
            `).join("")}
          </div>
        </div>

        <div>
          <h4 class="font-bold text-indigo-400 uppercase tracking-wide text-xs mb-2">Company Personnel &amp; Roles</h4>
          <div class="grid grid-cols-2 gap-2">
            ${mem.employees.map(e => `
              <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <div class="font-semibold text-slate-200">${e.name}</div>
                <div class="text-slate-400 text-[11px]">${e.role} &middot; ${e.department}</div>
                <div class="text-slate-500 text-[10px] font-mono">${e.email}</div>
              </div>
            `).join("")}
          </div>
        </div>
      </div>
    `;
  } catch (e) {
    content.innerHTML = `<div class="text-rose-400">Failed to load memory graph.</div>`;
  }
  lucide.createIcons();
}

function closeMemoryModal() {
  document.getElementById("memory-modal").classList.add("hidden");
}

async function viewEvidenceModal() {
  if (!currentSessionId) return;
  const res = await fetch(`/api/evidence/${currentSessionId}`);
  if (!res.ok) return;
  const ev = await res.json();

  document.getElementById("evidence-content").textContent = JSON.stringify(ev, null, 2);
  document.getElementById("evidence-modal").classList.remove("hidden");
  lucide.createIcons();
}

function closeEvidenceModal() {
  document.getElementById("evidence-modal").classList.add("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
});
