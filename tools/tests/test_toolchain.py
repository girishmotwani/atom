"""Behaviour tests for toolchain evidence included in review prompts."""

from __future__ import annotations

from atom.gates import GateResult, GateStatus
from atom.toolchain import ToolchainEvidence


def gate_result(
    name: str,
    status: GateStatus = GateStatus.PASSED,
    summary: str | None = None,
    details: str = "",
    required: bool = True,
) -> GateResult:
    """Create compact gate results so each test can focus on review semantics."""

    return GateResult(
        name=name,
        status=status,
        summary=summary or f"{name} passed",
        details=details,
        required=required,
        duration_seconds=0.1,
    )


def all_passing_evidence() -> ToolchainEvidence:
    """Build the green toolchain result that should exclude mechanical findings."""

    return ToolchainEvidence(
        gate_results=(
            gate_result("build"),
            gate_result("vet"),
            gate_result("fmt"),
            gate_result("test"),
            gate_result("race"),
            gate_result("staticcheck", required=False),
            gate_result("errcheck", required=False),
            gate_result("govulncheck", required=False),
        ),
        was_run=True,
        skip_reason="",
    )


def test_prompt_block_excludes_everything_the_passing_toolchain_proved():
    """A clean run should redirect models away from mechanically settled issues."""
    block = all_passing_evidence().as_prompt_block()

    assert "mechanical proof, not opinion" in block
    assert "go build ./..." in block
    assert "staticcheck ./..." in block
    assert "govulncheck ./..." in block
    assert "build errors" in block
    assert "failing tests" in block
    assert "formatting" in block
    assert "vet diagnostics" in block
    assert "ignored error returns" in block
    assert "data race on a path the tests execute" in block
    assert "known vulnerabilities in dependencies" in block
    assert "untested concurrent code is unchecked" in block
    assert "errors caught and handled wrongly" in block
    assert "unsafe handling of input in this code" in block
    assert "name misleads a reader" in block
    assert "not evidence a problem is absent" in block


def test_prompt_block_does_not_exclude_ignored_errors_when_errcheck_was_skipped():
    """Unchecked properties must stay in the model's search space."""
    evidence = ToolchainEvidence(
        gate_results=(
            gate_result("build"),
            gate_result("vet"),
            gate_result("fmt"),
            gate_result("test"),
            gate_result("race"),
            gate_result("staticcheck", required=False),
            gate_result(
                "errcheck",
                GateStatus.SKIPPED,
                summary="errcheck is not installed",
                required=False,
            ),
            gate_result("govulncheck", required=False),
        ),
        was_run=True,
        skip_reason="",
    )

    block = evidence.as_prompt_block()

    assert "errcheck ./..." in block
    assert "not installed - not checked" in block
    assert "ignored error returns" not in block


def test_prompt_block_says_nothing_is_excluded_when_toolchain_did_not_run():
    """The most dangerous bug would be suppressing findings after a skipped run."""
    evidence = ToolchainEvidence(
        gate_results=(),
        was_run=False,
        skip_reason="No go.mod found in this directory.",
    )

    block = evidence.as_prompt_block()

    assert "toolchain did not run" in block
    assert "No go.mod found" in block
    assert "nothing is excluded" in block.lower()
