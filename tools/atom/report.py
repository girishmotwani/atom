"""Render a CheckReport as human-readable text or machine-readable JSON."""

from __future__ import annotations

import json

from atom.check import CheckReport
from atom.gates import GateStatus

# Bump when the JSON shape changes incompatibly, so consumers can branch on it
# instead of guessing from the presence of fields.
SCHEMA_VERSION = 1

_RESET = "\x1b[0m"
_COLOURS = {
    GateStatus.PASSED: "\x1b[32m",
    GateStatus.FAILED: "\x1b[31m",
    GateStatus.SKIPPED: "\x1b[90m",
    GateStatus.WARNING: "\x1b[33m",
}
_SYMBOLS = {
    GateStatus.PASSED: "PASS",
    GateStatus.FAILED: "FAIL",
    GateStatus.SKIPPED: "SKIP",
    GateStatus.WARNING: "WARN",
}


def render_text(report: CheckReport, use_colour: bool = True) -> str:
    """Render a report for a human reading a terminal.

    Passing gates show one line. Failing gates additionally show their verbatim
    output, because that is the only part a developer needs to act on.
    """

    lines = [f"atom check {report.directory}", ""]

    for result in report.gate_results:
        label = _paint(_SYMBOLS[result.status], result.status, use_colour)
        lines.append(f"  {label}  {result.name:<6} {result.summary} ({result.duration_seconds:.1f}s)")

        if result.status is GateStatus.FAILED and result.details.strip():
            lines.append("")
            lines.extend(f"        {detail_line}" for detail_line in result.details.splitlines())
            lines.append("")

    if report.warnings:
        lines.append("")
        lines.append("  Warnings:")
        lines.extend(f"    - {warning}" for warning in report.warnings)

    verdict_status = GateStatus.PASSED if report.passed else GateStatus.FAILED
    verdict_text = "PASSED" if report.passed else "FAILED"
    lines.append("")
    lines.append(f"  {_paint(verdict_text, verdict_status, use_colour)} in {report.total_duration_seconds:.1f}s")

    return "\n".join(lines)


def render_json(report: CheckReport) -> str:
    """Render a report as stable, versioned JSON for programmatic consumers."""

    payload = {
        "schema_version": SCHEMA_VERSION,
        "directory": str(report.directory),
        "passed": report.passed,
        "exit_code": report.exit_code,
        "total_duration_seconds": round(report.total_duration_seconds, 3),
        "warnings": list(report.warnings),
        "gates": [
            {
                "name": result.name,
                "status": result.status.value,
                "summary": result.summary,
                "details": result.details,
                "required": result.required,
                "duration_seconds": round(result.duration_seconds, 3),
            }
            for result in report.gate_results
        ],
    }

    return json.dumps(payload, indent=2)


def _paint(text: str, status: GateStatus, use_colour: bool) -> str:
    if not use_colour:
        return text

    return f"{_COLOURS[status]}{text}{_RESET}"
