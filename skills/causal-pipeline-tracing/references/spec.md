# Causal Numbered Pipeline Trace Specification (v1.0)

This document formalizes the grammar, structure, and operational constraints for **Causal Numbered Pipeline Traces**, engineered specifically to optimize fault localization for LLM coding agents.

---

## 1. Trace Format Grammar (EBNF)

```ebnf
TraceLine        ::= Tag " " StepSequence " " Status [ " " Reason ] [ " | " ContextList ]
Tag              ::= "[" Identifier "-TRACE]"
StepSequence     ::= StepId ( " -> " StepId )*
StepId           ::= Integer [ Suffix ]
Suffix           ::= [a-z]
Status           ::= "[OK]" | "[FAIL]" | "[ABORT]" | "[RETRY]"
Reason           ::= "reason=" KebabCaseIdentifier
ContextList      ::= KeyValue ( " | " KeyValue )*
KeyValue         ::= Key "=" Value
Key              ::= [a-zA-Z0-9_]+
Value            ::= [a-zA-Z0-9_.-]+
Integer          ::= [0-9]+
KebabCaseIdentifier ::= [a-z0-9]+ ( "-" [a-z0-9]+ )*
```

---

## 2. Structural Components

### 2.1 The Tag (`[<SUBSYSTEM>-TRACE]`)
- Identifies the specific process, state machine, or asynchronous pipeline.
- Examples: `[OUTBOX-TRACE]`, `[ACK-GUARD-TRACE]`, `[DISPATCH-TRACE]`, `[STATE-SYNC-TRACE]`.
- Avoid generic tags like `[DEBUG]` or `[INFO]` that provide zero subsystem context.

### 2.2 Monotonic Step Sequences (`1 -> 2 -> 3b -> 4`)
- Each integer represents a sequential stage in the pipeline lifecycle.
- **Integers**: Represent forward progression along the primary execution happy path (1, 2, 3, 4, 5).
- **Suffixes**: Represent conditional branches, retry attempts, or error exits (e.g., `3a` = cache hit, `3b` = remote call fallback).
- **Rule of Causality**: Steps must be emitted in true execution order. The arrow `->` asserts causal precedence.

### 2.3 Status & Reason Tokens
- Successful executions conclude with `[OK]`.
- Non-successful executions MUST conclude with `[FAIL]` or `[ABORT]` immediately accompanied by `reason=<identifier>`.
- The `reason` flag must be an explicit, machine-readable kebab-case identifier that maps directly to a discrete code branch or guard clause.
- Examples:
  - `reason=stale-snapshot-leaked`
  - `reason=unhandled-4xx-inFlight-not-cleared`
  - `reason=revision-inversion-detected`
  - `reason=outbox-deadlock-timeout`

### 2.4 State Summary Context (`key=value`)
- Separated from the trace by ` | `.
- Must contain **only 2 to 4 scalar values** necessary to disambiguate the state.
- **Allowed**: `entityId=doc-123 | queueDepth=1 | inFlight=true | rev=4`
- **Disallowed**: Entire serialized JSON payloads, base64 data, stack traces, nested objects.

---

## 3. Token Budget & Density Guidelines

1. **Max Line Length**: A single trace line should never exceed 180 characters (~40 tokens).
2. **Signal-to-Token Ratio**: 
   - Traditional JSON logs: 80–90% syntax boilerplate (`"","":{}`), 10–20% diagnostic signal.
   - Causal Numbered Traces: >80% diagnostic signal per token.
3. **Reproduction Window Budget**:
   - The total reproduction log submitted to an AI assistant should be strictly **< 300 lines** (target: 50–150 lines).
   - This ensures the LLM's attention mechanism focuses entirely on the causal delta rather than scrolling through noise.
