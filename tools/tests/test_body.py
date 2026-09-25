"""Behaviour tests for the pull request body (B148-B151).

The body is the artifact a human actually reads on GitHub, so every test here
guards a property the POC measured the hard way: that a body assembled from
links cannot outgrow the character ceiling (B148), that its links resolve
because they name the pushed commit and not a branch that 404s until merge
(B149), and that its size accounting is honest on a platform where a text-mode
write silently adds one byte per line (B150).
"""

from __future__ import annotations

from atom.body import (
    BodyInputs,
    CheckSummary,
    extract_purpose,
    render_body,
    write_body_file,
)


def passing_check() -> CheckSummary:
    return CheckSummary(
        gate_rows=(("gofmt", "PASS"), ("go vet", "PASS")),
        absent_reason=None,
        passed=True,
    )


def body_inputs(
    title: str = "Phase 5: atom ship",
    purpose: str | None = "Ship turns a finished phase into a pull request.",
    commit_subjects: tuple[str, ...] = ("[Feature] Add ship command",),
    check: CheckSummary | None = None,
    artifacts: tuple[str, ...] = ("specs/atom-cli/phase-05-ship/design-spec.md",),
    repo_slug: str = "octocat/atom",
    commit_sha: str = "0123456789abcdef0123456789abcdef01234567",
) -> BodyInputs:
    return BodyInputs(
        title=title,
        purpose=purpose,
        commit_subjects=commit_subjects,
        check=check if check is not None else passing_check(),
        artifacts=artifacts,
        repo_slug=repo_slug,
        commit_sha=commit_sha,
    )


class TestExtractPurpose:
    """The Why section quotes the design spec's Purpose prose (B148)."""

    def test_the_purpose_prose_is_returned(self):
        markdown = (
            "# Design Spec\n\n"
            "## Purpose\n\n"
            "Ship turns a finished phase into a pull request.\n\n"
            "## Evidence Base\n\n"
            "Six predictions were recorded.\n"
        )

        assert extract_purpose(markdown) == (
            "Ship turns a finished phase into a pull request."
        )

    def test_every_paragraph_of_the_purpose_survives(self):
        # The real design spec's Purpose is two paragraphs. Returning only the
        # first would silently drop half of what the section says, which is the
        # quiet omission this project exists to prevent.
        markdown = (
            "## Purpose\n\n"
            "First paragraph of the why.\n\n"
            "Second paragraph of the why.\n\n"
            "## Evidence Base\n\n"
            "Unrelated.\n"
        )

        prose = extract_purpose(markdown)

        assert "First paragraph of the why." in prose
        assert "Second paragraph of the why." in prose

    def test_a_missing_purpose_section_returns_none(self):
        # B144's principle applied to prose: absence is reported as absence, not
        # invented. render_body decides how to state it; extract only reports it.
        markdown = "# Design Spec\n\n## Evidence Base\n\nNo purpose here.\n"

        assert extract_purpose(markdown) is None

    def test_the_next_heading_ends_the_purpose_section(self):
        markdown = (
            "## Purpose\n\n"
            "Only this belongs to the section.\n\n"
            "## Creating And Updating\n\n"
            "This paragraph must not leak into the purpose.\n"
        )

        prose = extract_purpose(markdown)

        assert "Only this belongs" in prose
        assert "must not leak" not in prose


class TestBodyIsSummaryPlusLinks:
    """B148 - the body is assembled parts, never embedded artifact content."""

    def test_the_body_title_is_the_h1(self):
        # Where the title comes from (spec H1 versus branch name) is ship's
        # choice; render simply promotes whatever title it is handed to the H1.
        body = render_body(body_inputs(title="Phase 5: atom ship"))

        assert body.splitlines()[0] == "# Phase 5: atom ship"

    def test_the_why_quotes_the_purpose_paragraph(self):
        body = render_body(
            body_inputs(purpose="Ship points at facts already on disk.")
        )

        assert "> Ship points at facts already on disk." in body

    def test_what_changed_lists_the_commit_subjects(self):
        body = render_body(
            body_inputs(
                commit_subjects=(
                    "[Feature] Add ship command",
                    "[Docs] Record the POC",
                )
            )
        )

        assert "[Feature] Add ship command" in body
        assert "[Docs] Record the POC" in body

    def test_the_parts_appear_in_the_specified_order(self):
        # Title, Why, What changed, Evidence, Artifacts (B148's table).
        body = render_body(body_inputs())

        order = [
            body.index("# Phase 5: atom ship"),
            body.index("Why"),
            body.index("What changed"),
            body.index("Evidence"),
            body.index("Artifacts"),
        ]

        assert order == sorted(order)

    def test_the_body_links_to_each_artifact_rather_than_embedding_it(self):
        # render_body is handed paths, never content, so embedding is impossible
        # by construction - but the test pins the property a future refactor
        # that started reading files could quietly break.
        body = render_body(
            body_inputs(
                artifacts=(
                    "specs/atom-cli/phase-05-ship/design-spec.md",
                    "specs/atom-cli/phase-05-ship/poc-report.md",
                )
            )
        )

        assert "(https://github.com/octocat/atom/blob/" in body
        assert "design-spec.md" in body
        assert "poc-report.md" in body


class TestLinksPointAtTheCommitSha:
    """B149 - a link to a branch 404s until merge, so links name the SHA."""

    SHA = "abcabcabcabcabcabcabcabcabcabcabcabcabca"

    def _artifact_link_lines(self, body: str) -> list[str]:
        return [line for line in body.splitlines() if "https://github.com/" in line]

    def test_every_link_embeds_the_pushed_commit_sha(self):
        body = render_body(
            body_inputs(
                commit_sha=self.SHA,
                artifacts=(
                    "specs/atom-cli/phase-05-ship/design-spec.md",
                    "specs/atom-cli/phase-05-ship/poc-report.md",
                ),
            )
        )

        links = self._artifact_link_lines(body)
        assert links, "expected at least one artifact link"
        for link in links:
            assert f"/blob/{self.SHA}/" in link

    def test_no_link_uses_a_branch_name_as_the_ref(self):
        # The ref sits immediately after /blob/. The branch name may legitimately
        # appear later in the path (specs/.../phase-05-ship/...), so the test
        # pins the ref position specifically rather than the whole URL.
        body = render_body(
            body_inputs(
                commit_sha=self.SHA,
                artifacts=("specs/atom-cli/phase-05-ship/design-spec.md",),
            )
        )

        for link in self._artifact_link_lines(body):
            assert "/blob/phase-05-ship/" not in link

    def test_no_link_points_at_the_base_branch(self):
        body = render_body(body_inputs(commit_sha=self.SHA))

        for link in self._artifact_link_lines(body):
            assert "/blob/main/" not in link
            assert "/blob/master/" not in link


class TestWriteBodyFile:
    """B150 - explicit newline='\\n', and the count is characters not bytes."""

    def test_the_written_file_contains_no_carriage_return(self, tmp_path):
        # The POC wrote in text mode and Windows turned every \n into \r\n,
        # inflating the body. Reading back as raw bytes is the only check that
        # catches it: a text-mode read would translate the \r away again.
        path = tmp_path / "body.md"
        text = "line one\nline two\nline three\n"

        write_body_file(text, path)

        raw = path.read_bytes()
        assert b"\r" not in raw
        assert 0x0D not in raw

    def test_the_returned_count_is_the_character_count(self, tmp_path):
        path = tmp_path / "body.md"
        text = "a body with\nseveral\nlines\n"

        assert write_body_file(text, path) == len(text)

    def test_the_character_count_is_below_the_text_mode_byte_count(self, tmp_path):
        # A many-line body written in text mode on Windows would weigh
        # len(text) + one byte per newline on disk. The reported figure must be
        # the smaller, true character count, or size accounting is wrong by the
        # ~2% the POC measured at 70,000 characters.
        path = tmp_path / "body.md"
        text = "".join(f"line {index}\n" for index in range(500))

        reported = write_body_file(text, path)
        text_mode_byte_count = len(text) + text.count("\n")

        assert reported == len(text)
        assert reported < text_mode_byte_count

    def test_the_reported_count_matches_the_bytes_on_disk(self, tmp_path):
        # Because the write forces newline='\n', the honest character count and
        # the real on-disk byte count agree for an ASCII body - which is the
        # proof the inflation did not happen on this platform.
        path = tmp_path / "body.md"
        text = "".join(f"line {index}\n" for index in range(500))

        reported = write_body_file(text, path)

        assert reported == len(path.read_bytes())


class TestEvidenceStatesAbsence:
    """B145a/B146 - an absent check is stated, never silently dropped."""

    def test_a_gate_table_carries_one_row_per_gate(self):
        body = render_body(
            body_inputs(
                check=CheckSummary(
                    gate_rows=(("gofmt", "PASS"), ("go vet", "PASS"), ("build", "PASS")),
                    absent_reason=None,
                    passed=True,
                )
            )
        )

        rows = [line for line in body.splitlines() if line.startswith("| ") and "Gate" not in line and "---" not in line]
        assert len(rows) == 3

    def test_the_recorded_line_replaces_the_table_it_does_not_empty_the_section(self):
        # The distinction most likely to be mis-implemented: an empty Evidence
        # section and one that says "no gates run" are different claims, and
        # only the second is honest. The sentence must be present, not merely
        # the table absent.
        body = render_body(
            body_inputs(
                check=CheckSummary(
                    gate_rows=(),
                    absent_reason="not a Go module; no gates run",
                    passed=True,
                )
            )
        )

        assert "## Evidence" in body
        assert "not a Go module; no gates run" in body
        assert "| Gate | Status |" not in body

    def test_an_overridden_failure_is_stated_never_asserted_green(self):
        # B147a: shipping over a failing gate changes whether the PR opens, not
        # what the body claims. A body that read green while red is the confident
        # falsehood Atom exists to prevent.
        body = render_body(
            body_inputs(
                check=CheckSummary(
                    gate_rows=(("gofmt", "PASS"), ("go vet", "FAIL")),
                    absent_reason=None,
                    passed=False,
                )
            )
        )

        assert "did not pass" in body
        assert "All gates passed." not in body


class TestMissingArtifactsAreAbsent:
    """B144 - a missing artifact is omitted, never invented, never 'pending'."""

    def test_no_artifacts_produces_no_invented_link(self):
        body = render_body(body_inputs(artifacts=()))

        assert "## Artifacts" in body
        assert "https://github.com/" not in body

    def test_the_body_never_editorialises_a_missing_artifact(self):
        body = render_body(body_inputs(artifacts=()))

        lowered = body.lower()
        assert "pending" not in lowered
        assert "todo" not in lowered

    def test_only_the_artifacts_present_are_linked(self):
        body = render_body(
            body_inputs(
                artifacts=("specs/atom-cli/phase-05-ship/design-spec.md",)
            )
        )

        links = [line for line in body.splitlines() if "https://github.com/" in line]
        assert len(links) == 1
