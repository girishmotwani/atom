"""Behaviour tests for report rendering."""

from __future__ import annotations

import json
from pathlib import Path

from atom.check import CheckReport
from atom.gates import GateResult, GateStatus
from atom.report import render_json, render_text


def make_report(*gate_results: GateResult, warnings: tuple[str, ...] = ()) -> CheckReport:
    """Build a CheckReport directly so rendering is tested in isolation from gates."""
    return CheckReport(
        directory=Path("/repo"),
        gate_results=tuple(gate_results),
        warnings=warnings,
        total_duration_seconds=1.5,
    )


PASSING_GATE = GateResult("build", GateStatus.PASSED, "go build ./... passed", "", True, 0.4)
FAILING_GATE = GateResult("vet", GateStatus.FAILED, "go vet ./... failed with exit code 1", "vet: suspicious shift", True, 0.9)


def test_render_text_shows_every_gate_with_status_and_duration():
    """B24: Each gate is visible with its verdict and how long it took."""
    output = render_text(make_report(PASSING_GATE, FAILING_GATE), use_colour=False)

    assert "build" in output
    assert "vet" in output
    assert "0.4" in output
    assert "0.9" in output


def test_render_text_shows_details_for_failed_gates_only():
    """B25: Passing gates show a summary line; failures show their evidence."""
    output = render_text(make_report(PASSING_GATE, FAILING_GATE), use_colour=False)

    assert "vet: suspicious shift" in output


def test_render_text_omits_details_for_passing_gates():
    """B25: A passing gate's output would be noise at a gate."""
    noisy_pass = GateResult("build", GateStatus.PASSED, "go build ./... passed", "SHOULD NOT APPEAR", True, 0.4)

    output = render_text(make_report(noisy_pass), use_colour=False)

    assert "SHOULD NOT APPEAR" not in output


def test_render_text_includes_warnings():
    """B23: Hygiene warnings must be visible or they serve no purpose."""
    output = render_text(make_report(PASSING_GATE, warnings=("poc/leaky has .go files but no go.mod",)), use_colour=False)

    assert "poc/leaky" in output


def test_render_text_without_colour_emits_no_escape_codes():
    """Gate output is frequently pasted into issues and logs where escapes are noise."""
    output = render_text(make_report(FAILING_GATE), use_colour=False)

    assert "\x1b[" not in output


def test_render_text_with_colour_emits_escape_codes():
    """Interactive use benefits from colour, so the flag must actually do something."""
    output = render_text(make_report(FAILING_GATE), use_colour=True)

    assert "\x1b[" in output


def test_render_json_is_valid_json_for_a_passing_report():
    """B27: Output must parse, or downstream automation cannot consume it."""
    parsed = json.loads(render_json(make_report(PASSING_GATE)))

    assert parsed["passed"] is True


def test_render_json_is_valid_json_for_a_failing_report():
    """B27: The failing path is the one automation actually branches on."""
    parsed = json.loads(render_json(make_report(PASSING_GATE, FAILING_GATE)))

    assert parsed["passed"] is False
    assert parsed["exit_code"] == 1


def test_render_json_includes_a_schema_version():
    """B26: Consumers need a version to branch on before the schema ever changes."""
    parsed = json.loads(render_json(make_report(PASSING_GATE)))

    assert parsed["schema_version"] == 1


def test_render_json_includes_every_gate_with_its_evidence():
    """B26: The JSON form is lossless; details survive for failed gates."""
    parsed = json.loads(render_json(make_report(PASSING_GATE, FAILING_GATE)))

    gates_by_name = {gate["name"]: gate for gate in parsed["gates"]}
    assert set(gates_by_name) == {"build", "vet"}
    assert gates_by_name["vet"]["status"] == "failed"
    assert "suspicious shift" in gates_by_name["vet"]["details"]
