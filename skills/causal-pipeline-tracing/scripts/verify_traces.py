#!/usr/bin/env python3
"""
verify_traces.py - Linter and validator for Causal Numbered Pipeline Traces.

Usage:
    python3 verify_traces.py <path_to_log_file>
"""

import sys
import re
from pathlib import Path

TRACE_REGEX = re.compile(
    r"^\[(?P<tag>[A-Z0-9_-]+)-TRACE\]\s+"
    r"(?P<sequence>[0-9a-z]+(?:\s*->\s*[0-9a-z]+)*)\s+"
    r"(?P<status>\[OK\]|\[FAIL\]|\[ABORT\]|\[RETRY\])"
    r"(?:\s+reason=(?P<reason>[a-zA-Z0-9_-]+))?"
    r"(?:\s*\|\s*(?P<context>.*))?$"
)

def lint_trace_file(file_path: Path):
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    lines = file_path.read_text(encoding="utf-8").splitlines()
    total_lines = len(lines)
    trace_count = 0
    errors = []
    warnings = []

    print(f"🔍 Auditing trace file: {file_path}")
    print(f"📊 Total lines in log: {total_lines}")

    if total_lines > 300:
        warnings.append(
            f"Reproduction window contains {total_lines} lines (>300 line budget). "
            f"Consider bounding reproduction to maximize LLM signal density."
        )

    for idx, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "-TRACE]" not in line:
            # Unstructured or non-trace line
            continue

        trace_count += 1
        match = TRACE_REGEX.match(line)
        if not match:
            errors.append(f"Line {idx}: Malformed trace grammar. Got: '{line}'")
            continue

        tag = match.group("tag")
        sequence = match.group("sequence")
        status = match.group("status")
        reason = match.group("reason")
        context = match.group("context")

        # Check line length
        if len(line) > 200:
            warnings.append(f"Line {idx}: Line length ({len(line)} chars) exceeds 200 char recommendation.")

        # Check reason presence on failure
        if status in ("[FAIL]", "[ABORT]") and not reason:
            errors.append(f"Line {idx}: Status {status} is missing mandatory 'reason=<identifier>' tag.")

        # Check sequence progression
        steps = [s.strip() for s in sequence.split("->")]
        if len(steps) < 1:
            errors.append(f"Line {idx}: Empty step sequence.")

        # Check context pairs
        if context:
            for pair in context.split("|"):
                pair = pair.strip()
                if pair and "=" not in pair:
                    warnings.append(f"Line {idx}: Context item '{pair}' does not follow key=value format.")

    print(f"✅ Analyzed {trace_count} causal pipeline traces.")
    print("-" * 60)

    if errors:
        print(f"❌ Found {len(errors)} error(s):")
        for err in errors:
            print(f"   • {err}")
    else:
        print("🎉 Zero formatting errors! All traces conform to specification.")

    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warning(s):")
        for warn in warnings:
            print(f"   • {warn}")

    print("-" * 60)
    if errors:
        sys.exit(1)
    else:
        print("✨ Trace verification passed successfully.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify_traces.py <path_to_log_file>")
        sys.exit(1)
    lint_trace_file(Path(sys.argv[1]))
