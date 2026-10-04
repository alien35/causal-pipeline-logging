---
name: causal-pipeline-tracing
description: >-
  Instruments asynchronous pipelines, event queues, state machines, and cross-tier boundaries
  with Causal Numbered Pipeline Traces. Achieves 14% faster diagnostic latency and 50-57% token
  reduction on concurrency defects by providing deterministic formal proofs of failure. Use when
  the user asks to improve logging, add AI-friendly diagnostic tracing, instrument async/outbox
  pipelines, resolve race conditions or state desyncs, or make a codebase easily debuggable by AI agents.
---

# Causal Pipeline Tracing (`causal-pipeline-tracing`)

A high-density diagnostic instrumentation pattern designed specifically for AI coding agents. 
By replacing ad-hoc strings and verbose JSON dumps with **Causal Numbered Pipeline Traces**, this skill enables AI agents to pinpoint cross-tier root causes with **100% first-pass accuracy and zero exploratory detours**.

---

## 🧭 When to Apply This Skill

Activate this workflow whenever:
1. **The user asks to enhance, standardize, or refactor logging** across the application.
2. **The codebase contains stateful asynchronous pipelines**:
   - Client-side outbox queues, retry buffers, debounced event handlers.
   - Optimistic UI updates with asynchronous acknowledgement reconciliation.
   - Cross-process boundaries (e.g., `postMessage` bridges, WebSockets, gRPC, REST).
   - Event-driven workers, distributed jobs, or message brokers.
3. **The user wants the codebase to be easily debugged by AI coding assistants**.
4. **Reproducing intermittent race conditions, queue deadlocks, or state synchronization bugs**.

---

## 📋 The 5-Step Implementation Procedure

### Step 1: Identify Asynchronous Pipelines & Boundaries

Scan the target codebase for asynchronous state machines and cross-tier boundaries:
- **Client Outbox / Queue**: Look for queues holding in-flight actions, pending sync items, or retry loops.
- **Optimistic Reconciliation**: Look for state caches updated optimistically before server ACK.
- **Bridge Boundaries**: Look for IPC, `postMessage`, WebWorker, or network transport layers.
- **Worker Queues**: Look for background tasks processing jobs asynchronously.

### Step 2: Formulate the Causal Numbered Step Map

For each pipeline, define a monotonic sequence of pipeline numbers. Every phase must have an explicit integer step, and conditional branches receive letter suffixes:

```text
[1] Intake/Enqueue ──> [2] Debounce/Batch ──> [3] Dispatch
                                                    │
                                  ┌─────────────────┴─────────────────┐
                                  ▼                                   ▼
                       [3a] Local Cache Commit             [3b] Remote Dispatch
                                  │                                   │
                                  ▼                                   ▼
                       [4a] Sync Complete                  [4] Await ACK
                                                                      │
                                                    ┌─────────────────┴─────────────────┐
                                                    ▼                                   ▼
                                           [5a] ACK Confirmed                 [5b] ACK Timeout/Error
                                                    │                                   │
                                                    ▼                                   ▼
                                           [6] Pipeline Closed                [5c] Deadlock / Eviction
```

### Step 3: Implement Causal Numbered Trace Emission

Format emitted logs to match the standardized causal trace grammar:

```
[<SUBSYSTEM>-TRACE] <step-sequence> [<STATUS>] reason=<failure-code> | <key>=<value> ...
```

#### Grammar Rules:
1. **Prefix Tag**: `[<NAME>-TRACE]` (e.g., `[OUTBOX-TRACE]`, `[CMD-PIPELINE-TRACE]`).
2. **Step Sequence**: Linear arrows showing actual execution history (e.g., `1 -> 2 -> 3b -> 4`).
3. **Status Indicator**: `[OK]` for successful completion, `[FAIL]` or `[ABORT]` for terminal failures.
4. **Machine-Readable Failure Flag**: `reason=<kebab-case-identifier>` on failures (e.g., `reason=stale-snapshot-leaked`, `reason=unhandled-4xx-inFlight-not-cleared`).
5. **State Summary**: Exactly 2 to 4 high-signal primitive values (`id=...`, `queueDepth=...`, `inFlight=...`).
6. **Zero Payload Dumps**: Never print multi-kilobyte JSON payloads, large arrays, or binary blobs.

---

### Step 4: Enforce Bounded Reproduction Windows (<300 Lines)

> [!IMPORTANT]
> **The Bounded Window Rule**: LLMs achieve the highest diagnostic signal when reproduction logs are concise. Verbose or unbounded traces dilute context.
>
> 1. Implement a **Clear-and-Reproduce** mechanism (e.g., `logger.clearHistory()` or resetting the log buffer on test run).
> 2. Ensure each reproduction capture emits **fewer than 300 lines**.
> 3. Store the active trace in memory and only flush to console/file when an anomalous boundary or terminal failure occurs.

---

### Step 5: Validate Tracing Conformance

Run the included verification script to check your newly instrumented traces:

```bash
python3 scripts/verify_traces.py <path_to_reproduction_log>
```

Verify that:
- [x] Trace steps follow monotonic numbering (`1 -> 2 -> 3...`).
- [x] Failing traces terminate with an explicit `reason=...` tag.
- [x] No giant object dumps pollute the output.
- [x] Total reproduction log lines are $< 300$.

---

## 💻 Code Patterns & Recipes

### 1. TypeScript / JavaScript Implementation

```typescript
// logger/causalTrace.ts
export class CausalPipelineTrace {
  private steps: string[] = [];
  constructor(private readonly tag: string) {}

  step(stepId: string | number): this {
    this.steps.push(String(stepId));
    return this;
  }

  success(context: Record<string, string | number | boolean> = {}): void {
    const ctx = Object.entries(context).map(([k, v]) => `${k}=${v}`).join(' | ');
    console.log(`[${this.tag}-TRACE] ${this.steps.join(' -> ')} [OK]${ctx ? ' | ' + ctx : ''}`);
  }

  fail(reason: string, context: Record<string, string | number | boolean> = {}): void {
    const ctx = Object.entries(context).map(([k, v]) => `${k}=${v}`).join(' | ');
    console.error(
      `[${this.tag}-TRACE] ${this.steps.join(' -> ')} [FAIL] reason=${reason}${ctx ? ' | ' + ctx : ''}`
    );
  }
}

// Usage in an Outbox Queue:
async function processOutboxQueue(item: QueueItem, state: OutboxState) {
  const trace = new CausalPipelineTrace('OUTBOX');
  trace.step(1); // Dequeue

  if (!state.isOnline) {
    trace.step('2a').fail('offline-queue-paused', { queueDepth: state.queue.length });
    return;
  }

  trace.step(2); // Prepare transport
  try {
    state.inFlight = true;
    trace.step(3); // Dispatch
    const ack = await sendWithTimeout(item, 5000);
    state.inFlight = false;
    trace.step(4).step('5a').success({ id: item.id, queueDepth: state.queue.length });
  } catch (err: any) {
    // BUG FIX / RESILIENT PATTERN: explicitly clean up inFlight state and log causal terminal reason
    const isTimeout = err.name === 'TimeoutError';
    const reason = isTimeout ? 'ack-timeout-inFlight-cleared' : 'transport-error';
    state.inFlight = false;
    trace.step(4).step('5b').fail(reason, { id: item.id, retryCount: item.retries });
  }
}
```

---

### 2. Python / Asyncio Implementation

```python
# causal_trace.py
from typing import Any, Dict, List

class CausalPipelineTrace:
    def __init__(self, tag: str):
        self.tag = tag
        self.steps: List[str] = []

    def step(self, step_id: str | int) -> "CausalPipelineTrace":
        self.steps.append(str(step_id))
        return self

    def success(self, **context: Any) -> None:
        ctx_str = " | ".join(f"{k}={v}" for k, v in context.items())
        line = f"[{self.tag}-TRACE] {' -> '.join(self.steps)} [OK]"
        if ctx_str:
            line += f" | {ctx_str}"
        print(line)

    def fail(self, reason: str, **context: Any) -> None:
        ctx_str = " | ".join(f"{k}={v}" for k, v in context.items())
        line = f"[{self.tag}-TRACE] {' -> '.join(self.steps)} [FAIL] reason={reason}"
        if ctx_str:
            line += f" | {ctx_str}"
        print(line)

# Usage in a background job processor:
async def execute_task(task_id: str, queue_state: dict):
    trace = CausalPipelineTrace("WORKER-TASK")
    trace.step(1)  # Acquired lock
    
    trace.step(2)  # Validate schema
    if not is_valid(task_id):
        trace.step("2b").fail("invalid-schema", task_id=task_id)
        return

    trace.step(3)  # Fetch state
    snapshot = await fetch_snapshot(task_id)
    if snapshot.is_stale:
        trace.step("3b").step(4).fail("stale-snapshot-leaked", task_id=task_id, rev=snapshot.rev)
        return
        
    trace.step(4).step(5).success(task_id=task_id)
```

---

## ⚠️ Anti-Patterns Checklist

When implementing this skill, strictly avoid these mistakes:

| Anti-Pattern | Why It Hurts AI Debugging | Correct Pattern |
| :--- | :--- | :--- |
| **Dumping full request/response JSON** | Consumes 5,000+ tokens with irrelevant payload noise; obscures causal sequence. | Print only 2–4 critical scalar state variables (`id`, `queueDepth`, `inFlight`). |
| **Vague string messages** (`"Something went wrong"`) | Requires LLM to read 10+ source files to guess what condition produced the string. | Use explicit `reason=<machine-readable-tag>` pointing directly to the branch. |
| **Unnumbered log sequences** | Non-deterministic under concurrency; LLM cannot tell if step 3 happened before step 2. | Use monotonic causal progression: `1 -> 2 -> 3b -> 4`. |
| **Unbounded reproduction captures** | Long logs (>1,000 lines) overflow context and trigger hallucinated file paths. | Enforce clear-and-reproduce sessions bounded to `< 300 lines`. |

---

## 🔗 Reference Documentation

- [Detailed Specification & Grammar](./references/spec.md)
- [Empirical Benchmark Results & Multi-Tier Analysis](./references/benchmarks.md)
