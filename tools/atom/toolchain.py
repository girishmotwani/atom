"""Summarise mechanical Go toolchain evidence for model review prompts."""

from __future__ import annotations

from dataclasses import dataclass

from atom.gates import GateResult, GateStatus
from atom.go_selection import GoToolchainSelection


_COMMAND_BY_GATE = {
    "build": "go build ./...",
    "vet": "go vet ./...",
    "fmt": "gofmt -l .",
    "test": "go test ./...",
    "race": "go test -race ./...",
    "staticcheck": "staticcheck ./...",
    "errcheck": "errcheck ./...",
    "govulncheck": "govulncheck ./...",
}

_EXCLUSIONS_BY_GATE = {
    "build": "build errors",
    "vet": "vet diagnostics (printf verb mismatches, lost cancel, copied locks)",
    "fmt": "formatting",
    "test": "failing tests",
    "race": "a data race on a path the tests execute",
    "staticcheck": "staticcheck diagnostics",
    "errcheck": "ignored error returns",
    "govulncheck": "known vulnerabilities in dependencies",
}


@dataclass(frozen=True)
class ToolchainEvidence:
    """What the Go toolchain proved about this tree before any model saw it."""

    gate_results: tuple[GateResult, ...]
    was_run: bool
    skip_reason: str
    formatting_is_scoped: bool = False
    selection: GoToolchainSelection | None = None

    @property
    def blocking_failures(self) -> tuple[GateResult, ...]:
        """Return required gate failures that make model review premature."""

        return tuple(
            result
            for result in self.gate_results
            if result.required and result.status is GateStatus.FAILED
        )

    def as_prompt_block(self) -> str:
        """Explain which mechanical findings models should not spend time on."""

        selection_text = "\n".join(_go_selection_lines(self.selection))
        prefix = selection_text + "\n\n" if selection_text else ""
        if not self.was_run:
            reason = self.skip_reason or "no reason was recorded"
            return prefix + (
                "The Go toolchain did not run before this review.\n"
                f"Reason: {reason}\n\n"
                "Nothing is excluded from your attention. Look for "
                "everything: build errors, failing tests, formatting, vet "
                "diagnostics, ignored errors, races, vulnerabilities, and "
                "readability or extensibility problems."
            )

        lines = [
            "A Go toolchain ran over this code before review. These results are "
            "mechanical proof, not opinion.",
            "",
        ]
        lines.extend(self._command_verdict_lines())
        lines.append("")
        lines.append(self._exclusion_paragraph())
        lines.append("")
        lines.append(
            "What these tools cannot see: the race detector only observes paths "
            "the tests actually executed, so untested concurrent code is "
            "unchecked. errcheck finds discarded errors, not errors caught and "
            "handled wrongly. govulncheck finds known vulnerabilities in "
            "dependencies, not unsafe handling of input in this code. No tool "
            "here judges whether a name misleads a reader, whether a function "
            "has grown too long to follow, or whether this change will be easy "
            "to extend without editing existing behaviour."
        )
        lines.append("")
        lines.append(
            "A clean tool run is not evidence a problem is absent; it is "
            "evidence that one specific tool did not see it."
        )
        return prefix + "\n".join(lines)

    def _command_verdict_lines(self) -> list[str]:
        """Render every gate so clean, dirty, and unchecked signals stay distinct."""

        rows = []
        for result in self.gate_results:
            if result.name == "fmt" and self.formatting_is_scoped:
                rows.append((
                    "gofmt (changed Go files)",
                    f"{_verdict_for_prompt(result)} - {result.summary}\n{result.details}",
                ))
            else:
                rows.append((_command_for_gate(result.name), _verdict_for_prompt(result)))
        width = max((len(command) for command, _ in rows), default=0)
        return [f"  {command:<{width}}  {verdict}" for command, verdict in rows]

    def _exclusion_paragraph(self) -> str:
        """Name only categories whose proving tool actually passed."""

        exclusions = [
            (
                "formatting in the checked files only"
                if result.name == "fmt" and self.formatting_is_scoped
                else _EXCLUSIONS_BY_GATE[result.name]
            )
            for result in self.gate_results
            if result.status is GateStatus.PASSED and result.name in _EXCLUSIONS_BY_GATE
        ]
        if not exclusions:
            return (
                "Do not exclude any mechanical category based on this run; no "
                "tool reported a passing proof."
            )

        return (
            "Do not report these mechanically checked categories: "
            f"{_join_human_list(exclusions)}."
        )


def _go_selection_lines(selection: GoToolchainSelection | None) -> list[str]:
    if selection is None:
        return []
    request = selection.request
    lines = [
        f"Requested Go: {request.version} (source: {request.source}; "
        f"project version: {request.project_version or 'not configured'}).",
        f"Go selection: {selection.status}; observed Go: "
        f"{selection.observed_version or 'not observed'}.",
    ]
    if selection.status == "not_run":
        lines.append(f"Reason: {selection.reason}")
    else:
        lines.extend([
            f"Executable: {selection.executable} (source: {selection.selection_source}).",
            f"Go SHA-256: before={selection.executable_sha256}, "
            f"after={selection.executable_sha256_after}.",
            f"GOROOT: {selection.goroot}",
            f"Selected-root formatter: {selection.gofmt_executable}.",
            f"gofmt SHA-256: before={selection.gofmt_sha256}, "
            f"after={selection.gofmt_sha256_after or 'not used'}.",
        ])
    lines.append(
        "Selection scope: direct Go/gofmt gates only. Advisory analyzer internals "
        "and arbitrary descendants are not independently attested."
    )
    return lines


def _command_for_gate(name: str) -> str:
    """Return the command readers know for a gate name."""

    return _COMMAND_BY_GATE.get(name, name)


def _verdict_for_prompt(result: GateResult) -> str:
    """Keep prompt verdicts stable and explicit across gate statuses."""

    if result.status is GateStatus.SKIPPED and "not installed" in result.summary.lower():
        return "not installed - not checked"
    if result.status is GateStatus.SKIPPED:
        return f"SKIPPED - {result.summary}"
    if result.status is GateStatus.WARNING:
        return f"WARNING - {result.summary}"
    if result.status is GateStatus.FAILED:
        return f"FAILED - {result.summary}"
    return result.status.name


def _join_human_list(items: list[str]) -> str:
    """Join a list without hiding the boundary between the final two items."""

    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"
