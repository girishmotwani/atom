"""Behaviour tests for diff acquisition -- B103 to B106b.

These tests never shell out. `FakeRunner` from conftest scripts git's output by
command tuple, which means the assertions are about *what Atom asks git for*
and *what it does with the answer* -- the two things the design actually fixes.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from atom.diff import (
    CapturedDiff,
    DiffSource,
    DiffUnavailable,
    NoDiffSourceSelected,
    TooManyDiffSourcesSelected,
    capture_diff,
    git_command_for,
    select_source,
)
from atom.runner import CommandOutcome

from tests.conftest import FakeRunner, command_result


# A three-file diff. Deliberately includes a rename, a context line that looks
# like a change, and both additions and removals, because each of those is a
# way a naive size count goes wrong.
MULTI_FILE_DIFF = """\
diff --git a/store/lookup.go b/store/lookup.go
index 1111111..2222222 100644
--- a/store/lookup.go
+++ b/store/lookup.go
@@ -10,7 +10,8 @@ func (s *Store) Lookup(key string) (string, bool) {
 	s.mu.RLock()
-	value := s.items[key]
+	value, ok := s.items[key]
+	_ = ok
 	return value, true
 }
diff --git a/store/reserve.go b/store/reserve.go
index 3333333..4444444 100644
--- a/store/reserve.go
+++ b/store/reserve.go
@@ -4,6 +4,7 @@ package store
 func (s *Store) Reserve(id string, n int) error {
-	s.stock[id] -= n
+	s.stock[id] = s.stock[id] - n
 	return nil
 }
diff --git a/store/old_name.go b/store/new_name.go
similarity index 90%
rename from store/old_name.go
rename to store/new_name.go
--- a/store/old_name.go
+++ b/store/new_name.go
@@ -1,3 +1,3 @@
 package store
-// a removed comment
+// an added comment
"""


def working_directory(tmp_path: Path) -> Path:
    return tmp_path


class TestSourceSelection:
    """B103 and B104 -- the source is always chosen explicitly."""

    def test_staged_source_asks_git_for_the_index(self):
        assert git_command_for(select_source(staged=True)) == (
            "git",
            "diff",
            "--staged",
        )

    def test_working_source_asks_git_for_unstaged_changes(self):
        assert git_command_for(select_source(working=True)) == ("git", "diff")

    def test_branch_source_diffs_against_the_merge_base(self):
        # Three dots, not two. Two dots would include changes made on the base
        # branch since this one forked -- code the developer never wrote, sent
        # to a model as though they had.
        assert git_command_for(select_source(branch="main")) == (
            "git",
            "diff",
            "main...HEAD",
        )

    def test_selecting_no_source_names_all_three_options(self):
        # B104: guessing wastes minutes of model time on the wrong code.
        with pytest.raises(NoDiffSourceSelected) as error:
            select_source()

        message = str(error.value)
        assert "--staged" in message
        assert "--branch" in message
        assert "--working" in message

    def test_selecting_two_sources_is_an_error_rather_than_a_precedence_rule(self):
        # A precedence rule would silently review one of the two things asked
        # for, which is the same failure B104 exists to prevent.
        with pytest.raises(TooManyDiffSourcesSelected) as error:
            select_source(staged=True, working=True)

        assert "--staged" in str(error.value)
        assert "--working" in str(error.value)

    def test_the_chosen_source_is_recorded_on_the_request(self):
        assert select_source(staged=True).source is DiffSource.STAGED
        assert select_source(working=True).source is DiffSource.WORKING

        branch_request = select_source(branch="release-2")
        assert branch_request.source is DiffSource.BRANCH
        assert branch_request.base_ref == "release-2"


class TestCapture:
    """B105, B106 and B106a -- one capture, whole, empty is not a failure."""

    def test_capture_issues_exactly_one_git_command(self, tmp_path):
        # B106: every model must review byte-identical input, so the diff is
        # taken once. Re-running git per model would let the working tree move.
        runner = FakeRunner(
            {("git", "diff", "--staged"): command_result(
                ("git", "diff", "--staged"), tmp_path, stdout=MULTI_FILE_DIFF
            )}
        )

        capture_diff(select_source(staged=True), runner, working_directory(tmp_path))

        assert len(runner.calls) == 1

    def test_a_multi_file_diff_is_captured_whole(self, tmp_path):
        # B106a: no per-file chunking. Cross-file context is where a caller
        # that no longer matches its callee becomes visible.
        runner = FakeRunner(
            {("git", "diff", "--staged"): command_result(
                ("git", "diff", "--staged"), tmp_path, stdout=MULTI_FILE_DIFF
            )}
        )

        captured = capture_diff(
            select_source(staged=True), runner, working_directory(tmp_path)
        )

        assert captured.text == MULTI_FILE_DIFF
        assert captured.files == (
            "store/lookup.go",
            "store/new_name.go",
            "store/reserve.go",
        )

    def test_an_empty_diff_is_not_an_error(self, tmp_path):
        # B105: a docs-only commit must not fail a CI job.
        runner = FakeRunner(
            {("git", "diff"): command_result(("git", "diff"), tmp_path, stdout="")}
        )

        captured = capture_diff(
            select_source(working=True), runner, working_directory(tmp_path)
        )

        assert captured.is_empty
        assert captured.files == ()

    def test_a_whitespace_only_diff_counts_as_empty(self, tmp_path):
        runner = FakeRunner(
            {("git", "diff"): command_result(("git", "diff"), tmp_path, stdout="\n \n")}
        )

        captured = capture_diff(
            select_source(working=True), runner, working_directory(tmp_path)
        )

        assert captured.is_empty

    def test_nothing_is_truncated_however_large_the_diff(self, tmp_path):
        # B106b: no cap is imposed. A limit would be a number nobody measured.
        # The `@@` header is not decoration -- hunk-aware parsing needs it, and
        # real git output always has one.
        large_diff = (
            "diff --git a/big.go b/big.go\n"
            "--- a/big.go\n"
            "+++ b/big.go\n"
            "@@ -1,0 +1,5000 @@\n"
            + "".join(f"+line {n}\n" for n in range(5000))
        )
        runner = FakeRunner(
            {("git", "diff"): command_result(("git", "diff"), tmp_path, stdout=large_diff)}
        )

        captured = capture_diff(
            select_source(working=True), runner, working_directory(tmp_path)
        )

        assert captured.text == large_diff
        assert captured.changed_lines == 5000


class TestGitFailure:
    """A diff that cannot be obtained is loud -- never an empty review."""

    def test_a_failed_git_command_is_reported_not_swallowed(self, tmp_path):
        runner = FakeRunner(
            {("git", "diff", "unknown-ref...HEAD"): command_result(
                ("git", "diff", "unknown-ref...HEAD"),
                tmp_path,
                exit_code=128,
                stderr="fatal: bad revision 'unknown-ref'",
            )}
        )

        with pytest.raises(DiffUnavailable) as error:
            capture_diff(
                select_source(branch="unknown-ref"), runner, working_directory(tmp_path)
            )

        # The developer needs git's own words; a paraphrase loses the ref name.
        assert "bad revision" in str(error.value)

    def test_a_missing_git_is_reported_clearly(self, tmp_path):
        runner = FakeRunner()  # unscripted commands come back TOOL_MISSING

        with pytest.raises(DiffUnavailable) as error:
            capture_diff(
                select_source(staged=True), runner, working_directory(tmp_path)
            )

        assert "git" in str(error.value)

    def test_a_timed_out_git_command_is_reported(self, tmp_path):
        runner = FakeRunner(
            {("git", "diff"): command_result(
                ("git", "diff"),
                tmp_path,
                outcome=CommandOutcome.TIMED_OUT,
                exit_code=None,
                stderr="Command timed out after 30 seconds.",
            )}
        )

        with pytest.raises(DiffUnavailable):
            capture_diff(
                select_source(working=True), runner, working_directory(tmp_path)
            )


class TestSize:
    """B106b -- size is reported so a thin review has a visible explanation."""

    def test_changed_lines_count_additions_and_removals(self, tmp_path):
        captured = CapturedDiff(text=MULTI_FILE_DIFF)

        # lookup.go: 1 removed, 2 added. reserve.go: 1 removed, 1 added.
        # new_name.go: 1 removed, 1 added. Total 7.
        assert captured.changed_lines == 7

    def test_file_headers_are_not_counted_as_changed_lines(self):
        # `+++ b/file` and `--- a/file` start with + and - but are headers.
        # Counting them adds two per file: 13 instead of 7 on this diff.
        captured = CapturedDiff(text=MULTI_FILE_DIFF)

        naive_count = len(
            [line for line in MULTI_FILE_DIFF.splitlines() if line[:1] in "+-"]
        )
        assert naive_count == 13
        assert captured.changed_lines == 7

    def test_context_lines_are_not_counted(self):
        captured = CapturedDiff(
            text=(
                "diff --git a/x.go b/x.go\n"
                "--- a/x.go\n"
                "+++ b/x.go\n"
                "@@ -1,3 +1,3 @@\n"
                " unchanged context\n"
                "+added\n"
            )
        )

        assert captured.changed_lines == 1

    def test_file_count_follows_the_b_side_of_a_rename(self):
        # The review talks about the file as it will exist, not as it was.
        captured = CapturedDiff(text=MULTI_FILE_DIFF)

        assert "store/new_name.go" in captured.files
        assert "store/old_name.go" not in captured.files

    def test_a_file_is_counted_once_however_many_hunks_it_has(self):
        captured = CapturedDiff(
            text=(
                "diff --git a/x.go b/x.go\n"
                "--- a/x.go\n"
                "+++ b/x.go\n"
                "@@ -1,2 +1,2 @@\n"
                "+first\n"
                "@@ -40,2 +40,2 @@\n"
                "+second\n"
            )
        )

        assert captured.files == ("x.go",)
        assert captured.changed_lines == 2

    def test_size_reads_as_a_sentence_for_the_report(self):
        captured = CapturedDiff(text=MULTI_FILE_DIFF)

        assert captured.describe_size() == "7 changed lines across 3 files"

    def test_size_description_is_singular_for_one_file(self):
        captured = CapturedDiff(
            text="diff --git a/x.go b/x.go\n--- a/x.go\n+++ b/x.go\n@@ -1 +1 @@\n+one\n"
        )

        assert captured.describe_size() == "1 changed line across 1 file"

    def test_an_empty_diff_describes_itself_as_empty(self):
        assert CapturedDiff(text="").describe_size() == "nothing to review"


class TestDescription:
    """The phrases that end up in the report header under B127."""

    def test_staged_describes_itself(self):
        assert select_source(staged=True).describe() == "staged changes"

    def test_working_describes_itself(self):
        assert (
            select_source(working=True).describe()
            == "unstaged working-tree changes"
        )

    def test_branch_names_the_base_ref(self):
        assert select_source(branch="main").describe() == "this branch against main"

    def test_a_path_without_an_a_or_b_prefix_is_used_as_is(self):
        # `git diff --no-prefix` emits `+++ store/x.go` with no `b/`.
        captured = CapturedDiff(
            text=(
                "diff --git store/x.go store/x.go\n"
                "--- store/x.go\n"
                "+++ store/x.go\n"
                "@@ -1 +1 @@\n"
                "+changed\n"
            )
        )

        assert captured.files == ("store/x.go",)


class TestHeaderConfusion:
    """Diff *content* must never be mistaken for diff *headers*.

    A `+`/`-` prefix is added to every line inside a hunk, so content that
    already begins with `-` or `+` produces lines like `----` and `+++ x`.
    A prefix-only rule misreads both, and neither failure is visible in the
    output -- the size is quietly wrong and the file list quietly grows.
    """

    MARKDOWN_DIFF = (
        "diff --git a/doc.md b/doc.md\n"
        "--- a/doc.md\n"
        "+++ b/doc.md\n"
        "@@ -1,4 +1,2 @@\n"
        "----\n"             # removing a `---` front-matter delimiter
        "-title: x\n"
        "----\n"             # removing the closing `---`
        "-- a sql comment\n"  # removing a line that began with `-`
        "+kept\n"
    )

    def test_removing_a_markdown_rule_still_counts_as_a_changed_line(self):
        # Atom's own repo is mostly markdown with `---` front matter, so this
        # is the diff shape it will meet most often when reviewing itself.
        captured = CapturedDiff(text=self.MARKDOWN_DIFF)

        assert captured.changed_lines == 5

    def test_added_content_cannot_invent_a_file(self):
        # The danger is not cosmetic: B117 rejects findings naming a file that
        # is not in the diff, so a phantom entry widens the only guard against
        # a model describing code it was never shown.
        captured = CapturedDiff(
            text=(
                "diff --git a/real.go b/real.go\n"
                "--- a/real.go\n"
                "+++ b/real.go\n"
                "@@ -1,2 +1,3 @@\n"
                " ok\n"
                "+++ phantom/invented.go\n"
            )
        )

        assert captured.files == ("real.go",)
        assert captured.changed_lines == 1

    def test_content_that_looks_like_a_git_header_does_not_start_a_new_file(self):
        captured = CapturedDiff(
            text=(
                "diff --git a/readme.md b/readme.md\n"
                "--- a/readme.md\n"
                "+++ b/readme.md\n"
                "@@ -1,2 +1,3 @@\n"
                " example:\n"
                "+diff --git a/not-real.go b/not-real.go\n"
            )
        )

        assert captured.files == ("readme.md",)

    def test_content_that_looks_like_a_hunk_header_is_counted_as_a_change(self):
        captured = CapturedDiff(
            text=(
                "diff --git a/x.go b/x.go\n"
                "--- a/x.go\n"
                "+++ b/x.go\n"
                "@@ -1,2 +1,3 @@\n"
                " ok\n"
                "+@@ this is content @@\n"
            )
        )

        assert captured.changed_lines == 1

    def test_several_files_each_reset_the_header_state(self):
        captured = CapturedDiff(text=MULTI_FILE_DIFF + self.MARKDOWN_DIFF)

        assert captured.files == (
            "doc.md",
            "store/lookup.go",
            "store/new_name.go",
            "store/reserve.go",
        )
        assert captured.changed_lines == 7 + 5

    def test_a_deleted_file_is_named_by_its_old_path(self):
        captured = CapturedDiff(
            text=(
                "diff --git a/gone.go b/gone.go\n"
                "--- a/gone.go\n"
                "+++ /dev/null\n"
                "@@ -1,2 +0,0 @@\n"
                "-package store\n"
                "-// gone\n"
            )
        )

        assert captured.files == ("gone.go",)
        assert captured.changed_lines == 2

    def test_a_no_newline_marker_is_not_a_changed_line(self):
        captured = CapturedDiff(
            text=(
                "diff --git a/x.go b/x.go\n"
                "--- a/x.go\n"
                "+++ b/x.go\n"
                "@@ -1 +1 @@\n"
                "+last\n"
                "\\ No newline at end of file\n"
            )
        )

        assert captured.changed_lines == 1
