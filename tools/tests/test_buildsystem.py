"""A repository's own Makefile outsranks Atom's Go defaults."""

from __future__ import annotations

from pathlib import Path

import pytest

from atom.buildsystem import (
    DEFAULT_BUILD_COMMAND,
    DEFAULT_TEST_COMMAND,
    detect,
    makefile_targets,
)


class TestReadingTargets:
    def test_a_plain_rule_is_a_target(self, tmp_path: Path) -> None:
        makefile = tmp_path / "Makefile"
        makefile.write_text("build:\n\tgo build ./...\n", encoding="utf-8")

        assert makefile_targets(makefile) == {"build"}

    def test_several_targets_on_one_rule_are_all_read(self, tmp_path: Path) -> None:
        makefile = tmp_path / "Makefile"
        makefile.write_text("build test lint:\n\techo hi\n", encoding="utf-8")

        assert makefile_targets(makefile) == {"build", "test", "lint"}

    def test_prerequisites_are_not_targets(self, tmp_path: Path) -> None:
        makefile = tmp_path / "Makefile"
        makefile.write_text("build: generate deps\n\tgo build ./...\n", encoding="utf-8")

        assert makefile_targets(makefile) == {"build"}

    def test_a_double_colon_rule_is_a_target(self, tmp_path: Path) -> None:
        makefile = tmp_path / "Makefile"
        makefile.write_text("build:: deps\n\tgo build ./...\n", encoding="utf-8")

        assert makefile_targets(makefile) == {"build"}

    @pytest.mark.parametrize(
        "line",
        [
            "BUILD_FLAGS := -race",
            "BUILD_FLAGS ::= -race",
            "BUILD_FLAGS ?= -race",
            "BUILD_FLAGS += -race",
            "BUILD_FLAGS = -race",
        ],
    )
    def test_an_assignment_is_never_a_target(self, tmp_path: Path, line: str) -> None:
        """`:=` is an assignment, and reading it as a rule invents a target."""

        makefile = tmp_path / "Makefile"
        makefile.write_text(f"{line}\nbuild:\n\tgo build ./...\n", encoding="utf-8")

        assert makefile_targets(makefile) == {"build"}

    def test_a_recipe_line_is_never_a_target(self, tmp_path: Path) -> None:
        """Recipe lines are tab-indented and routinely contain a colon."""

        makefile = tmp_path / "Makefile"
        makefile.write_text(
            "build:\n\tdocker run image:tag go build ./...\n", encoding="utf-8"
        )

        assert makefile_targets(makefile) == {"build"}

    def test_pattern_and_variable_targets_are_ignored(self, tmp_path: Path) -> None:
        """Neither can be invoked as a literal `make build`."""

        makefile = tmp_path / "Makefile"
        makefile.write_text(
            "%.o: %.c\n\tcc $<\n$(BINARY): main.go\n\tgo build\n", encoding="utf-8"
        )

        assert makefile_targets(makefile) == set()

    def test_special_targets_are_ignored(self, tmp_path: Path) -> None:
        """`.PHONY` names targets; it is not itself one worth running."""

        makefile = tmp_path / "Makefile"
        makefile.write_text(".PHONY: build\nbuild:\n\tgo build\n", encoding="utf-8")

        assert makefile_targets(makefile) == {"build"}

    def test_a_comment_does_not_create_a_target(self, tmp_path: Path) -> None:
        makefile = tmp_path / "Makefile"
        makefile.write_text("# deploy: not implemented\nbuild:\n\tgo build\n", encoding="utf-8")

        assert makefile_targets(makefile) == {"build"}

    def test_an_unreadable_makefile_yields_no_targets(self, tmp_path: Path) -> None:
        """Detection must never raise into a gate; it falls back instead."""

        assert makefile_targets(tmp_path / "absent") == set()


class TestChoosingCommands:
    def test_without_a_makefile_the_go_defaults_stand(self, tmp_path: Path) -> None:
        chosen = detect(tmp_path, make_is_available=lambda: True)

        assert chosen.build_command == DEFAULT_BUILD_COMMAND
        assert chosen.test_command == DEFAULT_TEST_COMMAND
        assert chosen.makefile is None

    def test_a_makefile_with_both_targets_takes_over(self, tmp_path: Path) -> None:
        (tmp_path / "Makefile").write_text(
            "build:\n\tgo build ./...\ntest:\n\tgo test ./...\n", encoding="utf-8"
        )

        chosen = detect(tmp_path, make_is_available=lambda: True)

        assert chosen.build_command == ("make", "build")
        assert chosen.test_command == ("make", "test")
        assert chosen.makefile == tmp_path / "Makefile"

    @pytest.mark.parametrize("name", ["GNUmakefile", "makefile", "Makefile"])
    def test_the_reported_name_is_the_one_actually_on_disk(
        self, tmp_path: Path, name: str
    ) -> None:
        """On a case-insensitive filesystem a probe for one spelling opens another.

        macOS and Windows both answer ``(root / "makefile").is_file()`` with True when
        the real file is ``Makefile``, so probing names in order reports a path that
        does not exist under that spelling. The developer is told Atom is reading a
        file they cannot find.
        """

        (tmp_path / name).write_text("build:\n\tgo build ./...\n", encoding="utf-8")

        chosen = detect(tmp_path, make_is_available=lambda: True)

        assert chosen.makefile is not None
        assert chosen.makefile.name == name
        assert name in chosen.reason

    def test_each_gate_is_decided_on_its_own_target(self, tmp_path: Path) -> None:
        """A Makefile that builds but does not test must not fake a test target."""

        (tmp_path / "Makefile").write_text("build:\n\tgo build ./...\n", encoding="utf-8")

        chosen = detect(tmp_path, make_is_available=lambda: True)

        assert chosen.build_command == ("make", "build")
        assert chosen.test_command == DEFAULT_TEST_COMMAND

    @pytest.mark.parametrize("name", ["GNUmakefile", "makefile", "Makefile"])
    def test_every_name_make_itself_honours_is_honoured(
        self, tmp_path: Path, name: str
    ) -> None:
        (tmp_path / name).write_text("build:\n\tgo build ./...\n", encoding="utf-8")

        assert detect(tmp_path, make_is_available=lambda: True).build_command == (
            "make",
            "build",
        )

    def test_gnumakefile_wins_over_makefile_as_make_would(self, tmp_path: Path) -> None:
        """GNU make reads GNUmakefile first, so Atom must agree with it."""

        (tmp_path / "GNUmakefile").write_text("build:\n\tgo build ./...\n", encoding="utf-8")
        (tmp_path / "Makefile").write_text("test:\n\tgo test ./...\n", encoding="utf-8")

        chosen = detect(tmp_path, make_is_available=lambda: True)

        assert chosen.makefile == tmp_path / "GNUmakefile"
        assert chosen.build_command == ("make", "build")
        assert chosen.test_command == DEFAULT_TEST_COMMAND

    def test_without_make_installed_the_makefile_is_not_used(self, tmp_path: Path) -> None:
        """Preferring a command that cannot run would turn a green tree red."""

        (tmp_path / "Makefile").write_text(
            "build:\n\tgo build ./...\ntest:\n\tgo test ./...\n", encoding="utf-8"
        )

        chosen = detect(tmp_path, make_is_available=lambda: False)

        assert chosen.build_command == DEFAULT_BUILD_COMMAND
        assert chosen.test_command == DEFAULT_TEST_COMMAND
        assert "make is not installed" in chosen.reason
