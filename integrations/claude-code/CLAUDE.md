# Claude Code Guidelines: Causal Pipeline Tracing

Add the following section to your repository's root `CLAUDE.md` to instruct Anthropic's Claude Code CLI to automatically format, refactor, and diagnose asynchronous code using Causal Numbered Pipeline Tracing:

```markdown
## Logging & Diagnostics: Causal Pipeline Tracing

When implementing, modifying, or debugging asynchronous pipelines, event queues, state machines, or cross-tier communication:

1. **Format Specification**:
   - Always use Causal Numbered Pipeline Traces instead of ad-hoc console strings or deeply nested JSON dumps:
     `[<SUBSYSTEM>-TRACE] <sequence> [<STATUS>] reason=<kebab-case-reason> | <key>=<value>`
   - Example happy path: `[OUTBOX-TRACE] 1 -> 2 -> 3 -> 4 [OK] | entityId=doc-123 | rev=2`
   - Example failure path: `[OUTBOX-TRACE] 1 -> 2 -> 3b -> 4 [FAIL] reason=unhandled-4xx-inFlight-not-cleared | entityId=doc-123 | inFlight=true`

2. **Causal Progression Rules**:
   - Primary forward execution path uses integers: `1 -> 2 -> 3 -> 4`.
   - Branching, retries, and error recovery use letter suffixes: `3a` (cache hit), `3b` (network fallback).
   - Any `[FAIL]` or `[ABORT]` status MUST specify an explicit machine-readable `reason=<flag>` identifier.
   - Limit state context to 2–4 critical scalar variables (e.g., `queueDepth=1 | inFlight=true`). Never dump multi-kilobyte JSON payloads.

3. **Reproduction Bounds**:
   - Scope all test reproduction logs to `< 300 lines` via clear-and-reproduce sessions.

4. **Reference Implementation**:
   - Full specification: `.agents/skills/causal-pipeline-tracing/references/spec.md`
   - Verification tool: Run `python3 .agents/skills/causal-pipeline-tracing/scripts/verify_traces.py <log_file>` to validate trace syntax.
```

### Prompting Claude Code

Once added, you can prompt Claude Code:
```bash
claude "Review our outbox queue in src/queue/ and instrument it with Causal Numbered Pipeline Traces per CLAUDE.md"
```
Or for diagnosing an issue from a log:
```bash
claude "Here is our reproduction log: $(cat reproduction.log). Identify the root cause file and fix the bug."
```
