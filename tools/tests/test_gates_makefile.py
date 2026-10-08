"""The build and test gates must run the project's Makefile when it has one."""

from __future__ import annotations

from pathlib import Path

import pytest

from atom.gates import BuildGate, GateStatus, TestGate
from tests.conftest import FakeRunner, command_result


@pytest.fixture()
def make_on_path(monkeypatch) -> None:
    """Pretend make is installed, so the choice turns on the Makefile alone."""

    monkeypatch.setattr("atom.buildsystem.shutil.which", lambda name: "/usr/bin/make")


def write_makefile(root: Path, body: str) -> None:
    (root / "Makefile").write_text(body, encoding="utf-8")


class TestBuildGate:
    def test_a_build_target_is_preferred_over_go_build(
        self, tmp_path: Path, make_on_path
    ) -> None:
        write_makefile(tmp_path, "build:\n\tgo build -tags prod ./...\n")
        command = ("make", "build")
        runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0)})

        result = BuildGate().evaluate(runner, tmp_path)

        assert result.status is GateStatus.PASSED
        assert runner.calls[0][0] == command
        assert "make build" in result.summary

    def test_without_a_build_target_go_build_still_runs(
        self, tmp_path: Path, make_on_path
    ) -> None:
        write_makefile(tmp_path, "test:\n\tgo test ./...\n")
        command = ("go", "build", "./...")
        runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0)})

        result = BuildGate().evaluate(runner, tmp_path)

        assert result.status is GateStatus.PASSED
        assert runner.calls[0][0] == command

    def test_a_failing_make_target_fails_the_gate(
        self, tmp_path: Path, make_on_path
    ) -> None:
        write_makefile(tmp_path, "build:\n\tgo build ./...\n")
        command = ("make", "build")
        runner = FakeRunner(
            {command: command_result(command, tmp_path, exit_code=2, stderr="boom\n")}
        )

        result = BuildGate().evaluate(runner, tmp_path)

        assert result.status is GateStatus.FAILED
        assert "boom" in result.details


class TestTestGate:
    def test_a_test_target_is_preferred_over_go_test(
        self, tmp_path: Path, make_on_path
    ) -> None:
        write_makefile(tmp_path, "test:\n\tgo test -count=1 ./...\n")
        command = ("make", "test")
        runner = FakeRunner(
            {command: command_result(command, tmp_path, exit_code=0, stdout="ok  pkg\n")}
        )

        result = TestGate().evaluate(runner, tmp_path)

        assert result.status is GateStatus.PASSED
        assert runner.calls[0][0] == command

    def test_a_failing_make_target_fails_the_gate(
        self, tmp_path: Path, make_on_path
    ) -> None:
        write_makefile(tmp_path, "test:\n\tgo test ./...\n")
        command = ("make", "test")
        runner = FakeRunner(
            {command: command_result(command, tmp_path, exit_code=1, stdout="FAIL pkg\n")}
        )

        result = TestGate().evaluate(runner, tmp_path)

        assert result.status is GateStatus.FAILED

    def test_no_test_files_is_still_reported_as_skipped_through_make(
        self, tmp_path: Path, make_on_path
    ) -> None:
        """Delegating must not turn "nothing was tested" into a green tick.

        `make` echoes the recipe before running it, so stdout carries lines that
        are not go's package results. Counting those as evidence of a test run
        is what would make an untested tree report PASSED.
        """

        write_makefile(tmp_path, "test:\n\tgo test ./...\n")
        command = ("make", "test")
        runner = FakeRunner(
            {
                command: command_result(
                    command,
                    tmp_path,
                    exit_code=0,
                    stdout="go test ./...\n?   \texample.com/m\t[no test files]\n",
                )
            }
        )

        result = TestGate().evaluate(runner, tmp_path)

        assert result.status is GateStatus.SKIPPED

    def test_a_real_test_run_through_make_is_not_downgraded(
        self, tmp_path: Path, make_on_path
    ) -> None:
        write_makefile(tmp_path, "test:\n\tgo test ./...\n")
        command = ("make", "test")
        runner = FakeRunner(
            {
                command: command_result(
                    command,
                    tmp_path,
                    exit_code=0,
                    stdout="go test ./...\nok  \texample.com/m\t0.2s\n",
                )
            }
        )

        result = TestGate().evaluate(runner, tmp_path)

        assert result.status is GateStatus.PASSED


class TestTheOtherGatesAreNotDelegated:
    def test_the_format_gate_ignores_a_makefile(self, tmp_path: Path, make_on_path) -> None:
        """gofmt's verdict is read from stdout, which `make fmt` would swallow."""

        from atom.gates import FormatGate

        write_makefile(tmp_path, "fmt:\n\tgofmt -w .\n")
        command = ("gofmt", "-l", ".")
        runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0)})

        result = FormatGate().evaluate(runner, tmp_path)

        assert result.status is GateStatus.PASSED
        assert runner.calls[0][0] == command

    def test_the_vet_gate_ignores_a_makefile(self, tmp_path: Path, make_on_path) -> None:
        from atom.gates import VetGate

        write_makefile(tmp_path, "vet:\n\tgo vet ./...\n")
        command = ("go", "vet", "./...")
        runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0)})

        result = VetGate().evaluate(runner, tmp_path)

        assert result.status is GateStatus.PASSED
        assert runner.calls[0][0] == command


def test_a_makefile_is_ignored_when_make_is_not_installed(
    tmp_path: Path, monkeypatch
) -> None:
    """A green tree must not turn red just because make is absent."""

    monkeypatch.setattr("atom.buildsystem.shutil.which", lambda name: None)
    write_makefile(tmp_path, "build:\n\tgo build ./...\n")
    command = ("go", "build", "./...")
    runner = FakeRunner({command: command_result(command, tmp_path, exit_code=0)})

    result = BuildGate().evaluate(runner, tmp_path)

    assert result.status is GateStatus.PASSED
    assert runner.calls[0][0] == command
