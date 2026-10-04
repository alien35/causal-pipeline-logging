"""
causal_trace.py - High-Density Causal Numbered Pipeline Tracing for Python.
"""
from typing import Any, List, Optional

class CausalPipelineTrace:
    def __init__(self, tag: str):
        self.tag = tag.upper()
        self.steps: List[str] = []

    def step(self, step_id: Any) -> "CausalPipelineTrace":
        self.steps.append(str(step_id))
        return self

    def success(self, **context: Any) -> str:
        line = f"[{self.tag}-TRACE] {self._render_steps()} [OK]{self._format_context(context)}"
        print(line)
        return line

    def fail(self, reason: str, **context: Any) -> str:
        line = f"[{self.tag}-TRACE] {self._render_steps()} [FAIL] reason={reason}{self._format_context(context)}"
        print(line)
        return line

    def abort(self, reason: str, **context: Any) -> str:
        line = f"[{self.tag}-TRACE] {self._render_steps()} [ABORT] reason={reason}{self._format_context(context)}"
        print(line)
        return line

    def _render_steps(self) -> str:
        return " -> ".join(self.steps)

    def _format_context(self, context: dict) -> str:
        entries = [f"{k}={v}" for k, v in context.items() if v is not None]
        if not entries:
            return ""
        return " | " + " | ".join(entries)
