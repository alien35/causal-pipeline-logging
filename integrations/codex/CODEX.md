# OpenAI Codex & Assistant Guidelines: Causal Pipeline Tracing

This document provides configuration snippets and prompt instructions for using **Causal Numbered Pipeline Traces** with **OpenAI Codex**, GPT-4/GPT-5 coding workflows, OpenAI Assistants API, and GitHub Copilot.

---

## 1. Project Instruction File (`AGENTS.md` / `CODEX.md`)

Place this instruction block in your project root as `AGENTS.md` or `CODEX.md` (or `.github/copilot-instructions.md` for GitHub Copilot):

```markdown
# Agent Instructions: Causal Pipeline Tracing Standard

When generating, refactoring, or diagnosing code involving asynchronous pipelines, state machines, queues, or cross-tier communication:

1. **Instrumentation Standard**:
   - Do NOT emit unstructured console logs (`"Processing item..."`) or dump full JSON objects (`{"data": {...}}`).
   - Emit deterministic Causal Numbered Pipeline Traces following this grammar:
     `[<SUBSYSTEM>-TRACE] <step_sequence> [<STATUS>] reason=<kebab-case-reason> | <key>=<value>`

2. **Step Sequence Grammar**:
   - Monotonic integers represent forward progression: `1 -> 2 -> 3 -> 4`.
   - Letter suffixes indicate conditional branches or error paths: `2a` (offline), `2b` (dispatching), `3b` (network retry).
   - Arrows (`->`) strictly assert causal execution order.

3. **Terminal Reason Tags**:
   - Any terminal status `[FAIL]` or `[ABORT]` must include `reason=<machine-readable-tag>`.
   - Examples: `reason=stale-snapshot-leaked`, `reason=unhandled-4xx-inFlight-not-cleared`, `reason=revision-inversion-detected`.

4. **Context Constraints**:
   - Include only 2–4 high-signal scalar variables: `| id=123 | queueDepth=1 | inFlight=false`.
   - Keep reproduction logs strictly bounded to `< 300 lines`.
```

---

## 2. OpenAI API / Assistant System Prompt

If you are using OpenAI Codex or the OpenAI Responses / Chat API directly, include this in the `developer` or `system` message:

```text
You are an expert software engineer specialized in resilient asynchronous systems. 
When writing or refactoring asynchronous logic, queues, and state machines, you MUST instrument all operations with Causal Numbered Pipeline Traces:
- Format: [<SUBSYSTEM>-TRACE] 1 -> 2 -> 3b -> 4 [STATUS] reason=<reason-code> | key=value
- Successful runs terminate with [OK].
- Failed runs terminate with [FAIL] reason=<kebab-case-code>.
- Log only 2-4 scalar context variables (no raw payload dumps).
- Ensure logs are bounded (<300 lines reproduction budget).
```

---

## 3. Direct Prompting Examples for Codex

### Refactoring an existing queue:
> *"Rewrite `src/queue/outbox.py` to use Causal Numbered Pipeline Tracing. Map out the sequential stages as monotonic step numbers (1, 2, 3...) with branch suffixes (3a, 3b) and machine-readable failure reason flags."*

### Zero-Detour Root-Cause Diagnosis:
> *"Here is the reproduction log from our distributed sync test:*
> ```text
> [SYNC-PIPELINE-TRACE] 1 -> 2b -> 3 -> 3b -> 4 [FAIL] reason=revision-inversion-detected | entityId=ent-42 | incomingRev=4 | currentRev=5
> ```
> *Analyze the trace, identify the exact failing function in `syncService.ts`, and provide the fix."*
