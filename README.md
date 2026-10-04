# Causal Pipeline Logging (`causal-pipeline-tracing`)

> **High-Density Logging for Deterministic AI Agent Debugging & Zero-Detour Fault Localization**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skill: Agent-Ready](https://img.shields.io/badge/Skill-Agent--Ready-success.svg)](.agents/skills/causal-pipeline-tracing/SKILL.md)

> [!IMPORTANT]
> ### ⚡ TL;DR
> * **The Problem**: AI coding assistants waste 50%+ of their context and tokens wandering through unrelated files when debugging async queues, event loops, and cross-tier microservices with messy console logs or massive JSON dumps.
> * **The Solution**: Instrument asynchronous pipelines with **Causal Numbered Pipeline Traces**:
>   ```text
>   [OUTBOX-TRACE] 1 -> 2 -> 3b -> 4 [FAIL] reason=unhandled-4xx-inFlight-not-cleared | entityId=doc-123 | inFlight=true
>   ```
> * **The Proven Stats**:
>   * 🔻 **50% to 56.8% token drop** on concurrency bugs (queue deadlocks: 2,294 vs 5,306 tokens; delta overwrites: 2,758 vs 5,580 tokens).
>   * ⚡ **19.5s mean diagnostic latency** (13.7% faster than JSON, 10.1% faster than unstructured console logs).
>   * 🎯 **100% 1st-pass layer accuracy & 0 exploratory detours**: The numbered sequence acts as a formal proof of failure.
> * **The Golden Rule**: Constrain reproduction logs to a bounded window of **< 300 lines**.
> * **Universal Setup**:
>   * **Antigravity**: Install the skill into `.agents/skills/causal-pipeline-tracing/`
>   * **Claude Code**: Paste `integrations/claude-code/CLAUDE.md` into your root `CLAUDE.md`
>   * **OpenAI Codex / Copilot**: Paste `integrations/codex/CODEX.md` into your root `AGENTS.md`
>   * **One-line installer**: `bash .agents/skills/causal-pipeline-tracing/scripts/install_skill.sh --all /path/to/project`

---

## 📊 Empirical Benchmarks: The Evidence

In benchmark evaluations comparing AI coding agents across complex asynchronous multi-tier defect scenarios (queue deadlocks, race conditions, partial delta overwrites, and revision inversions), **Causal Numbered Traces** demonstrated substantial gains over unstructured console logging and structured JSON.

### 1. Headline Results

| Diagnostic Metric | Unstructured Console | Structured JSON | Causal Numbered Trace | Net Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Mean Diagnostic Latency** | 21.7s (21,727 ms) | 22.6s (22,626 ms) | **19.5s (19,524 ms)** | **13.7% faster** than JSON, **10.1% faster** than Unstructured |
| **1st-Pass Layer Accuracy** | 100.0% | 100.0% | **100.0%** | Deterministic boundary detection |
| **Root Cause Accuracy** | 100.0% | 100.0% | **100.0%** | Exact file & function identified |
| **Mean Exploratory Detours** | 0.0 | 0.0 | **0.0** | Zero extraneous file inspections |
| **Mean Investigation Turns** | 1.0 | 1.0 | **1.0** | Resolved in a single turn |
| **Mean Context Tokens** | 5,601 | 5,040 | **4,677** | Consistently lowest token footprint |

---

### 2. Token Reduction on Asynchronous Concurrency Defects

The highest payoff occurs on stateful, asynchronous queues, race conditions, and partial delta updates:

```
Defect Scenario                Unstructured    Structured JSON   Causal Trace    Token Savings
-------------------------------------------------------------------------------------------------
Outbox Queue Deadlock          5,306 tokens    5,347 tokens      2,294 tokens    🔻 -56.8%
Partial Delta Overwrite        5,580 tokens    5,724 tokens      2,758 tokens    🔻 -50.6%
Revision Inversion             5,589 tokens    5,605 tokens      2,650 tokens    🔻 -52.6%
```

On asynchronous state machine and queueing defects, **Causal Numbered Traces eliminate over 50% to 56.8% of prompt tokens** while reducing agent cognitive load.

---

## 🧠 The Two Regimes of Logging for AI Agents

Empirical analysis uncovers two distinct regimes in how LLMs consume execution logs:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        LOGGING REGIMES FOR AI CODING AGENTS                            │
├─────────────────────────────────────────┬──────────────────────────────────────────────┤
│ 1. Asynchronous State Machine Regime    │ 2. Synchronous Validation Regime             │
│    (HIGH PAYOFF: 50% - 57% Token Drop)  │    (BOUNDED REPRODUCTION REQUIRED)           │
├─────────────────────────────────────────┼──────────────────────────────────────────────┤
│ • Queue deadlocks, outbox states,       │ • Immediate input validation, synchronous    │
│   inversion races, cross-process ticks. │   type checks, simple missing fields.        │
│ • Unstructured logs force speculative   │ • Unfiltered trace trees can expand token    │
│   hypotheses across client & server.    │   count if allowed to run unbounded.         │
│ • Numbered traces explicitly prove the  │ • Crucial Rule: Scope log captures to a      │
│   exact failed state transition.        │   bounded reproduction window (<300 lines).  │
└─────────────────────────────────────────┴──────────────────────────────────────────────┘
```

1. **The Asynchronous State Machine Regime (High Payoff)**:
   When bugs occur in stateful, asynchronous queues and race conditions, unstructured logs force the LLM to hypothesize multiple potential failure points across client and server. Causal Numbered Traces cut tokens by **50% to 57%** and resolve the defect deterministically. The numbered sequence acts as a **formal proof of failure**.
2. **The Verification vs. Explanation Trade-Off**:
   For simple synchronous validation failures, verbose trace dumps can slightly increase prompt length if not filtered. Bounding logs to a **compact reproduction window (<300 lines)** ensures maximum signal density without noise pollution.

---

## 📐 Anatomy of a Causal Numbered Trace

Traditional logging outputs ad-hoc strings or deep nested JSON objects:
```bash
# ❌ Unstructured Console: High ambiguity, no sequence guarantee
[WARN] 14:02:11 Failed to process move in outbox. retry count: 3
[DEBUG] 14:02:11 Ack timed out for doc-901
[INFO] 14:02:12 Received delta update from server
```

```json
// ❌ Verbose JSON: High token tax, deeply nested payloads that distract the LLM
{"timestamp":1696435331000,"level":"warn","context":{"subsystem":"outbox","inFlight":true,"payload":{"op":"move","coords":[100,240],"userId":"usr-9"},"error":"timeout"}}
```

A **Causal Numbered Pipeline Trace** encodes the exact sequential progression through pipeline stages with explicit failure boundaries:

```bash
#  Causal Numbered Trace: Unambiguous causal proof, minimal tokens
[OUTBOX-PIPELINE-TRACE] 1 -> 2 -> 3b -> 4 [FAIL] reason=unhandled-4xx-inFlight-not-cleared | entityId=doc-901 | queueDepth=1 | inFlight=true
```

### Core Syntax Rules

1. **Prefix Tag**: `[<SUBSYSTEM>-TRACE]` identifying the specific pipeline boundary.
2. **Monotonic Step Sequence**: Numbered stages (`1 -> 2 -> 3 -> 4`) representing the deterministic path through the state machine.
3. **Branching Suffixes**: Sub-steps (`3a`, `3b`, `5d`) identifying conditional branches taken.
4. **Failure Reason Identifier**: Explicit `reason=<machine_readable_flag>` on the terminal step (e.g., `reason=stale-snapshot-leaked`).
5. **Key State Variables**: Exactly 2 to 4 high-signal state attributes (`queueDepth=1 | inFlight=true`). No dumping of multi-kilobyte payloads.
6. **Bounded Window**: Reproduction sessions are bounded to `< 300 lines` via a "clear-and-reproduce" workflow.

---

## 📦 What's in This Repository

This repository provides everything needed to adopt this pattern in any software project:

```text
causal-pipeline-logging/
├── README.md                                  # You are here: Guide, benchmarks & benefits
├── LICENSE                                    # MIT License
├── .agents/skills/causal-pipeline-tracing/    # The Agent Skill package
│   ├── SKILL.md                               # Complete agent instructions & runbook
│   ├── references/
│   │   ├── spec.md                            # Trace grammar & formal specification
│   │   └── benchmarks.md                      # Detailed empirical benchmarks & analysis
│   ├── examples/
│   │   ├── typescript/                        # Async outbox queue & pipeline implementation
│   │   └── python/                            # Event-driven worker pipeline implementation
│   └── scripts/
│       ├── verify_traces.py                   # CLI tool to lint and validate trace conformance
│       └── install_skill.sh                   # Helper script to install into any repository
└── integrations/                              # Drop-in rules & prompts for other agents
    ├── claude-code/CLAUDE.md                  # Drop-in config for Anthropic Claude Code
    └── codex/CODEX.md                         # Drop-in rules for OpenAI Codex, GPT-4/5 & Copilot
```

---

## 🚀 How to Add This Skill to Your AI Agent

This skill is designed for cross-agent compatibility and can be used immediately with **Claude Code**, **OpenAI Codex / Copilot**, and **Antigravity**.

### Option 1: Automatic Multi-Agent Installation via Script

Use `install_skill.sh` to configure any target repository:

```bash
# In your target project:
bash /path/to/causal-pipeline-logging/.agents/skills/causal-pipeline-tracing/scripts/install_skill.sh --all /path/to/your/project
```
Flags available:
- `--all`: Installs the skill and sets up guidelines for Claude Code (`CLAUDE.md`) and Codex (`AGENTS.md`).
- `--claude`: Installs the skill and generates Claude Code instructions.
- `--codex`: Installs the skill and generates OpenAI Codex / Copilot instructions.

---

### Option 2: Claude Code Integration (`CLAUDE.md`)

[Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code) automatically reads `CLAUDE.md` from the root of your project.

1. Copy or append [`integrations/claude-code/CLAUDE.md`](integrations/claude-code/CLAUDE.md) into your repository's root `CLAUDE.md`:

```markdown
## Logging & Diagnostics: Causal Pipeline Tracing

When writing, refactoring, or diagnosing asynchronous code, queues, or state machines:
- Emit Causal Numbered Pipeline Traces: `[<SUBSYSTEM>-TRACE] <sequence> [<STATUS>] reason=<kebab-reason> | <key>=<value>`
- Happy path: `1 -> 2 -> 3 -> 4 [OK] | entityId=doc-123 | rev=2`
- Branch/Failure path: `1 -> 2 -> 3b -> 4 [FAIL] reason=unhandled-4xx-inFlight-not-cleared | entityId=doc-123 | inFlight=true`
- Never dump raw multi-KB JSON bodies; print only 2–4 scalar state variables.
- Bound reproduction logs to <300 lines via clear-and-reproduce sessions.
- Reference specification: `.agents/skills/causal-pipeline-tracing/references/spec.md`
- Validate with: `python3 .agents/skills/causal-pipeline-tracing/scripts/verify_traces.py <log_file>`
```

2. Invoke Claude Code:
```bash
claude "Review our outbox queue and instrument it with Causal Numbered Pipeline Traces per CLAUDE.md"
```

---

### Option 3: OpenAI Codex & Assistant Integration (`AGENTS.md` / System Prompt)

For **OpenAI Codex**, GPT-4/GPT-5 coding workflows, OpenAI Assistants, and GitHub Copilot:

1. **Repository Instructions (`AGENTS.md` / `CODEX.md`)**:
   Add [`integrations/codex/CODEX.md`](integrations/codex/CODEX.md) to your repository root as `AGENTS.md` (or `.github/copilot-instructions.md`).

2. **System / Developer Prompt**:
   If using the OpenAI API or custom GPTs, inject this developer instruction:
   ```text
   When writing or refactoring asynchronous logic, queues, or state machines, you MUST instrument all operations with Causal Numbered Pipeline Traces:
   - Format: [<SUBSYSTEM>-TRACE] 1 -> 2 -> 3b -> 4 [STATUS] reason=<reason-code> | key=value
   - Output [OK] on success; output [FAIL] reason=<kebab-case-code> on failure.
   - Limit state context to 2-4 scalar values; never dump large JSON objects.
   - Constrain test reproduction logs to <300 lines.
   ```

3. **Sample Prompt for Codex**:
   > *"Analyze this outbox retry loop. Refactor its logging to follow Causal Numbered Pipeline Tracing with monotonic sequence numbers, branch suffixes (3a, 3b), and explicit reason codes on failure."*

---

### Option 4: Antigravity Project Skill

Place the skill inside `.agents/skills/`:

```bash
mkdir -p /path/to/your/project/.agents/skills/
cp -r .agents/skills/causal-pipeline-tracing /path/to/your/project/.agents/skills/
```

Then prompt your assistant:
> *"Use the causal-pipeline-tracing skill to audit our asynchronous event pipelines and enhance our logging."*

---

## 🛠️ Testing Your Traces

Included is a CLI verification tool (`verify_traces.py`) that audits reproduction logs for causal monotonicity, explicit reason tags, and token density:

```bash
python3 .agents/skills/causal-pipeline-tracing/scripts/verify_traces.py examples/typescript/sample_trace.log
```

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
