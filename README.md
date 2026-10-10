# CentrAlign Autonomous Company Operator (`CentraOperator`)
### Founding Engineer Prototype & Core Runtime Architecture

> **Transforming high-level enterprise intent into verified, auditable outcomes across browsers, documents, internal APIs, and SaaS tools.**

---

## 1. Executive Summary & Founding Vision

Modern enterprises suffer from extreme fragmentation: business workflows are scattered across SaaS portals (BambooHR, Stripe, Zendesk, Okta), files, communication channels, and internal systems. Human workers spend hours finding unstated context, cross-checking policies, clicking through interfaces, and compiling reports.

Chatbots produce text advice without executing actions. Brittle RPA scripts break when selectors or schemas shift.

**CentrAlign Operator** is built from first principles as an **Autonomous Company Operator**:
1. **Institutional Grounding**: Resolves ambiguous, short requests (*"Onboard Alex to Engineering"*) into specific steps by querying an Organizational Memory & SOP Graph.
2. **Deterministic-to-Stochastic Task Graph (DAG)**: Compiles goals into a Directed Acyclic Graph where every node contains preconditions, parameters, blast radius assessments, and **Invariant Verification Contracts**.
3. **Adaptive Self-Healing Runtime**: Automatically diagnoses runtime anomalies (DOM changes, API rate limits, schema drift) via Root Cause Analysis (RCA) and executes fallback strategies.
4. **Policy-Enforced Human-in-the-Loop (HITL)**: High-risk or financial actions crossing policy limits (e.g., refunds > $50.00 USD, external emails, access revocation) pause statefully with interactive blast-radius inspection cards.
5. **Cryptographic & Invariant Audit Proofs**: Validates actual system state mutations (not just process return codes) and compiles an audit package with timestamped SHA256 hashes and diffs.

---

## 2. The Core Autonomous Loop

```
  Goal
   ?
   ?
[ Understand & Ground ] ??? Queries Org Memory & SOP Graph (SOP-HR-001, SOP-FIN-004)
   ?
   ?
[ Compile Task DAG ]    ??? Generates discrete task nodes with Invariant Contracts
   ?
   ?
[ Guardrail & HITL ]    ??? Checks Risk: If High / Policy limit -> Pause for Human Signoff
   ?
   ?
[ Heterogeneous Exec ]  ??? Dispatches Browser, File, SaaS API, or Shell tools
   ?
   ?
[ Observe & Adapt ]     ??? Analyzes outputs; Self-heals on errors with RCA fallback
   ?
   ?
[ Invariant Verify ]    ??? Queries target systems directly for proof of state mutation
   ?
   ?
[ Complete & Audit ]    ??? Generates cryptographic audit bundle & updates corporate learnings
```

---

## 3. Architecture & Codebase Map

```
centra_operator/
??? config.py                 # System configuration, API keys, thresholds, sandbox paths
??? memory/
?   ??? org_graph.py          # Corporate Hierarchy, Role permissions, Tool policies, Endpoints
?   ??? default_knowledge.py  # Executable Enterprise SOPs (HR Onboarding, Stripe Refund, SOC2)
?   ??? store.py              # Semantic & keyword memory repository + learning feedback loop
??? planner/
?   ??? intent_parser.py      # Goal disambiguation & entity extraction
?   ??? guardrails.py         # Risk classification (LOW/MED/HIGH) & policy threshold evaluator
?   ??? dag_planner.py        # Compiles intent + SOP into executable verified Task DAG
??? engine/
?   ??? state.py              # ExecutionState, TaskNode, ApprovalRequest, TraceLog models
?   ??? recovery.py           # Self-healing engine with Root Cause Analysis (RCA)
?   ??? hitl.py               # Human-in-the-Loop manager (Approval queues, feedback injection)
?   ??? runtime.py            # Master Execution Runtime orchestrating the loop
??? tools/
?   ??? base.py               # BaseTool contract, ToolResult schema, telemetry
?   ??? browser_tool.py       # Browser operator with resilient multi-locator fallbacks
?   ??? file_tool.py          # Sandbox file operator, diff generator, SHA256 checksum verifier
?   ??? internal_api_tool.py  # Connectors for BambooHR, Stripe, Okta/GitHub IAM, Zendesk
?   ??? communication_tool.py # Outbound email dispatcher and Slack channel notifier
?   ??? cli_tool.py           # Sandboxed script & command executor
?   ??? registry.py           # Dynamic tool discovery and dispatcher
??? verification/
?   ??? verifier.py           # Invariant & post-condition verification engine
?   ??? audit_evidence.py     # Cryptographic audit package & Markdown summary compiler
??? llm/
?   ??? provider.py           # Pluggable LLM interface (Gemini/OpenAI + SmartDeterministicEngine)
?   ??? prompts.py            # System prompts for reasoning, planning, and self-healing
??? web/
    ??? app.py                # FastAPI REST API + Server-Sent Events backend
    ??? static/               # Sleek Dark Mode Mission Control SPA (Tailwind CSS, Lucide icons)
```

---

## 4. Pre-built Realistic Enterprise Scenarios

| Scenario | Trigger Prompt | Systems Involved | Key Autonomy / HITL Features |
|---|---|---|---|
| **HR Onboarding & Identity** | *"Onboard Alex Morgan as Senior Frontend Engineer..."* | BambooHR, Okta SSO, GitHub, Sandbox Docs, Email | Disambiguates vague prompt, registers HRIS, provisions IAM, generates SOC2 checklist, pauses for HITL signoff on external welcome email, verifies all states. |
| **Finance Refund & Reconciliation** | *"Process customer refund for Zendesk #8841 ($75.00)..."* | Zendesk, Stripe API, Sandbox CSV Ledger | Detects $75.00 exceeds $50.00 policy threshold (`FIN-POL-04`), pauses with blast-radius card, executes Stripe refund, reconciles Q3 ledger CSV, resolves Zendesk ticket. |
| **SOC2 Access Revocation** | *"Execute SOC2 access revocation for Alex Morgan..."* | Okta SSO, GitHub IAM, Audit Sandbox | Audits active tokens, pauses for security signoff, de-provisions access across all platforms, generates cryptographic certificate proof. |
| **Self-Healing Recovery** | *"Navigate to portal and submit with selector fallback..."* | Browser Operator, Recovery Engine | Simulates broken UI selector, executes Root Cause Analysis, self-heals with resilient text fallback, and verifies state. |

---

## 5. Quickstart & How to Run

### Prerequisites
Python 3.10+ with `fastapi`, `uvicorn`, `pydantic`, `httpx` installed.

### 1. Launch Interactive Web Mission Control Dashboard
```bash
python main.py --web
```
Open **`http://localhost:8000`** in your browser to experience the live DAG visualization, real-time ReAct logs, interactive HITL approval dialogs, Org Memory browser, and downloadable audit evidence bundles.

### 2. Run via Interactive CLI
```bash
# Interactive mode (prompts for approvals in terminal)
python cli.py "Onboard Alex Morgan as Senior Frontend Engineer starting Monday"

# Automated mode (auto-approves HITL gates for CI/CD testing)
python cli.py "Process customer refund for Zendesk Ticket #8841 ($75.00)" --auto-approve
```

### 3. Run Automated Unit & Integration Test Suite
```bash
python -m unittest discover tests
```

---

## 6. Founding Engineer Technical Strategy & Production Roadmap

1. **Computer Use & Desktop Automation**:
   - Integrate OS-level computer use models (Anthropic Computer Use / OSWorld style) with visual grounding for legacy desktop software (SAP, proprietary desktop tools).
2. **Dynamic Knowledge Synthesis from Screen Recordings**:
   - Capture video of human experts performing workflows, automatically transcribing actions into machine-executable SOP graphs.
3. **Multi-Tenant Org Partitioning & Key Vault**:
   - Zero-trust credential isolation using HashiCorp Vault or AWS Secrets Manager, with ephemeral OAuth token exchange per task execution.
4. **Resilient Distributed Execution Worker Mesh**:
   - Decouple runtime into Celery/Temporal workflow orchestrator with stateless containerized worker execution environments.
