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


# --------------------------------------------------------------------------
# B67 -- one coherent story for one event
#
# Found by running the tool, not by reading it. A spike exiting 2 rendered
# `FAIL execute exited 2` immediately above `Verdict: INCONCLUSIVE`, and the
# process exited 0. Three accounts of the same event, two of them wrong.
# The execute stage's job is to run the spike; it did that perfectly. The
# exit code is the spike's answer, and the verdict line is where answers
# belong.
# --------------------------------------------------------------------------

from atom.spike import SpikeKind, SpikeResult, Stage, StageResult, Verdict
from atom.report import render_spike_text, render_spike_json


GO_PANIC_STDERR = "panic: runtime error: index out of range [5] with length 0\n\ngoroutine 1 [running]:\nmain.main()\n"


def make_spike_result(execute_exit: int, verdict: Verdict, stderr: str = "") -> SpikeResult:
    """Build a SpikeResult whose earlier stages all passed, isolating the execute stage."""
    stages = (
        StageResult(Stage.VET, 0, "", ""),
        StageResult(Stage.BUILD, 0, "", ""),
        StageResult(Stage.EXECUTE, execute_exit, "measured 1.2ms", stderr),
    )
    return SpikeResult("json-streaming", SpikeKind.COMMAND, stages, verdict, execute_exit)


def test_a_spike_that_answered_is_not_rendered_as_a_failed_stage():
    """B67: the defect itself -- FAIL contradicted the verdict printed below it."""
    output = render_spike_text(make_spike_result(2, Verdict.INCONCLUSIVE), use_colour=False)

    assert "FAIL" not in output
    assert "INCONCLUSIVE" in output


def test_an_answering_stage_says_it_answered_rather_than_that_it_exited():
    """B67: `exited 2` reads as a malfunction; `answered with exit 2` reads as a result."""
    output = render_spike_text(make_spike_result(2, Verdict.INCONCLUSIVE), use_colour=False)

    assert "answered with exit 2" in output


def test_a_refuted_spike_is_not_rendered_as_a_failure_either():
    """B67: Refuted is the most valuable verdict a spike can give."""
    output = render_spike_text(make_spike_result(1, Verdict.REFUTED), use_colour=False)

    assert "FAIL" not in output
    assert "REFUTED" in output


def test_a_crashed_spike_is_still_rendered_as_a_failure():
    """B67/B68: the control -- without this, 'never FAIL' would pass every test above."""
    output = render_spike_text(make_spike_result(2, Verdict.CRASHED, GO_PANIC_STDERR), use_colour=False)

    assert "FAIL" in output
    assert "CRASHED" in output


def test_a_crash_explains_that_exit_2_was_a_panic_not_a_verdict():
    """B68: the developer needs to know why this 2 was read differently from any other 2."""
    output = render_spike_text(make_spike_result(2, Verdict.CRASHED, GO_PANIC_STDERR), use_colour=False)

    assert "panic" in output.lower()


def test_the_spike_output_is_shown_even_when_nothing_failed():
    """B67: for an answered spike the output IS the evidence, so it must not be hidden."""
    output = render_spike_text(make_spike_result(2, Verdict.INCONCLUSIVE), use_colour=False)

    assert "measured 1.2ms" in output


def test_json_reports_no_failed_stage_for_a_spike_that_answered():
    """B67: machine consumers were being told `failed_stage: execute` as well."""
    parsed = json.loads(render_spike_json(make_spike_result(2, Verdict.INCONCLUSIVE)))

    assert parsed["failed_stage"] is None
    assert parsed["verdict"] == "inconclusive"


def test_json_exposes_answered_separately_from_ran():
    """B69: a crashed spike ran but did not answer, and consumers need both facts."""
    parsed = json.loads(render_spike_json(make_spike_result(2, Verdict.CRASHED, GO_PANIC_STDERR)))

    assert parsed["ran"] is True
    assert parsed["answered"] is False


def test_stderr_is_rendered_before_stdout():
    """B48: a gap found by auditing the spec against the tests, not by failure.

    When a spike fails, stdout is usually empty and stderr holds the entire
    explanation. Printing stdout first buries the only useful line. This had
    no test until the test spec was written -- and the rendering code around
    it was edited the same day, with nothing to catch a flip.
    """
    output = render_spike_text(make_spike_result(2, Verdict.CRASHED, GO_PANIC_STDERR), use_colour=False)

    assert output.index("stderr:") < output.index("stdout:")
