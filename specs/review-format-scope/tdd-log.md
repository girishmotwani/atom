# TDD evidence: changed-file review formatting

These are captured Python/Git/gofmt outputs, not a root Go atom check. Home/worktree path substitutions are explicitly redacted; all other captured text is retained. Commands ran from tools. The fixed synthetic POC is recorded separately.

Each production behavior below was observed failing before its implementation. Existing-behavior guards can pass immediately and are not represented as RED evidence. The UTF-8 fixture correction and legacy FakeRunner update are explained in decisions.md.

## Working changed-file scope

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests\test_review_formatting.py F                                        [100%]

================================== FAILURES ===================================
_______ test_clean_changed_file_is_not_blocked_by_untouched_formatting ________

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-397/test_clean_changed_file_is_not0')
model_prompts = []

    def test_clean_changed_file_is_not_blocked_by_untouched_formatting(
        repository: Path, model_prompts: list[str]
    ):
        (repository / "changed.go").write_bytes(CLEAN.encode())
        runner = ReviewRunner()
    
>       outcome = review(repository, runner)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:127: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:116: in review
    return run_review(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.WORKING: 'working'>, base_ref=None)
models = ('fixture-model',)
runner = <tests.test_review_formatting.ReviewRunner object at 0x00000272F898E3C0>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-397/test_clean_changed_file_is_not0')
runs = 1, concurrency = 1, window = 3, disable_mcp_servers = ()
skip_toolchain = False, include_style_rules = True

    def run_review(
        request: DiffRequest,
        models: Sequence[str],
        runner: CommandRunner,
        working_directory: Path,
        runs: int,
        concurrency: int,
        window: int = DEFAULT_PROXIMITY_WINDOW,
        disable_mcp_servers: Sequence[str] = (),
        skip_toolchain: bool = False,
        include_style_rules: bool = True,
    ) -> ReviewOutcome:
        """Capture a diff, ask every model about it, and merge what comes back.
    
        The order is fixed and the failures are not symmetric. A diff that cannot
        be captured raises, because there is nothing to review and pretending
        otherwise would produce a confident empty report. Everything after that
        point degrades instead: a run that fails is recorded, a reply nobody can
        parse is recorded, and the review continues with whatever answered (B129).
    
        `include_style_rules` exists for measurement, not for callers. Whether
        handing a reviewer seven consequence-phrased rules changes what it reports
        is an open question, and answering it needs the same review run with the
        rules absent. The CLI does not expose the switch, so the shipped behaviour
        is always on.
        """
    
        toolchain = _collect_toolchain_evidence(
            working_directory, runner, skip_toolchain=skip_toolchain
        )
        if toolchain.blocking_failures:
>           raise ToolchainGateFailed(toolchain.blocking_failures)
E           atom.review.ToolchainGateFailed: Required toolchain gates failed: fmt

atom\review.py:277: ToolchainGateFailed
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_clean_changed_file_is_not_blocked_by_untouched_formatting
============================== 1 failed in 1.59s ==============================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests\test_review_formatting.py .                                        [100%]

============================== 1 passed in 4.49s ==============================
~~~~

## Immutable staged snapshot

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests\test_review_formatting.py .FFF                                     [100%]

================================== FAILURES ===================================
_ test_staged_formatting_uses_index_snapshot_not_working_file[clean-index-dirty-worktree] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-399/test_staged_formatting_uses_in0')
model_prompts = [], staged = 'package fixture\n\nvar Value = 2\n'
working = 'package fixture\nvar Value=2\n'
expected = <GateStatus.PASSED: 'passed'>

    @pytest.mark.parametrize(
        ("staged", "working", "expected"),
        [
            (CLEAN, BAD, GateStatus.PASSED),
            (BAD, CLEAN, GateStatus.FAILED),
            (CLEAN, None, GateStatus.PASSED),
        ],
        ids=("clean-index-dirty-worktree", "dirty-index-clean-worktree", "worktree-file-absent"),
    )
    def test_staged_formatting_uses_index_snapshot_not_working_file(
        repository: Path, model_prompts: list[str], staged, working, expected
    ):
        path = repository / "changed.go"
        path.write_bytes(staged.encode())
        git(repository, "add", "changed.go")
        if working is None:
            path.unlink()
        else:
            path.write_bytes(working.encode())
        runner = ReviewRunner()
    
        if expected is GateStatus.FAILED:
            with pytest.raises(ToolchainGateFailed) as failure:
                review(repository, runner, DiffSource.STAGED)
            formatting = next(gate for gate in failure.value.failures if gate.name == "fmt")
            assert "changed.go" in formatting.summary
            assert model_prompts == []
        else:
>           outcome = review(repository, runner, DiffSource.STAGED)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:170: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:116: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.STAGED: 'staged'>, base_ref=None)
runner = <tests.test_review_formatting.ReviewRunner object at 0x000002040F2A9310>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-399/test_staged_formatting_uses_in0')

    def capture_review_diff(
        request: DiffRequest,
        runner: CommandRunner,
        working_directory: Path,
    ) -> tuple[CapturedDiff, ChangedFilesFormatGate]:
        """Capture the patch and changed-file identities in the same Git operation."""
    
        if request.source is not DiffSource.WORKING:
>           raise DiffUnavailable("This formatting snapshot source is not supported.")
E           atom.diff.DiffUnavailable: This formatting snapshot source is not supported.

atom\_review_format.py:89: DiffUnavailable
_ test_staged_formatting_uses_index_snapshot_not_working_file[dirty-index-clean-worktree] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-399/test_staged_formatting_uses_in1')
model_prompts = [], staged = 'package fixture\nvar Value=2\n'
working = 'package fixture\n\nvar Value = 2\n'
expected = <GateStatus.FAILED: 'failed'>

    @pytest.mark.parametrize(
        ("staged", "working", "expected"),
        [
            (CLEAN, BAD, GateStatus.PASSED),
            (BAD, CLEAN, GateStatus.FAILED),
            (CLEAN, None, GateStatus.PASSED),
        ],
        ids=("clean-index-dirty-worktree", "dirty-index-clean-worktree", "worktree-file-absent"),
    )
    def test_staged_formatting_uses_index_snapshot_not_working_file(
        repository: Path, model_prompts: list[str], staged, working, expected
    ):
        path = repository / "changed.go"
        path.write_bytes(staged.encode())
        git(repository, "add", "changed.go")
        if working is None:
            path.unlink()
        else:
            path.write_bytes(working.encode())
        runner = ReviewRunner()
    
        if expected is GateStatus.FAILED:
            with pytest.raises(ToolchainGateFailed) as failure:
>               review(repository, runner, DiffSource.STAGED)

tests\test_review_formatting.py:165: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:116: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.STAGED: 'staged'>, base_ref=None)
runner = <tests.test_review_formatting.ReviewRunner object at 0x000002040F2AA0D0>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-399/test_staged_formatting_uses_in1')

    def capture_review_diff(
        request: DiffRequest,
        runner: CommandRunner,
        working_directory: Path,
    ) -> tuple[CapturedDiff, ChangedFilesFormatGate]:
        """Capture the patch and changed-file identities in the same Git operation."""
    
        if request.source is not DiffSource.WORKING:
>           raise DiffUnavailable("This formatting snapshot source is not supported.")
E           atom.diff.DiffUnavailable: This formatting snapshot source is not supported.

atom\_review_format.py:89: DiffUnavailable
_ test_staged_formatting_uses_index_snapshot_not_working_file[worktree-file-absent] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-399/test_staged_formatting_uses_in2')
model_prompts = [], staged = 'package fixture\n\nvar Value = 2\n'
working = None, expected = <GateStatus.PASSED: 'passed'>

    @pytest.mark.parametrize(
        ("staged", "working", "expected"),
        [
            (CLEAN, BAD, GateStatus.PASSED),
            (BAD, CLEAN, GateStatus.FAILED),
            (CLEAN, None, GateStatus.PASSED),
        ],
        ids=("clean-index-dirty-worktree", "dirty-index-clean-worktree", "worktree-file-absent"),
    )
    def test_staged_formatting_uses_index_snapshot_not_working_file(
        repository: Path, model_prompts: list[str], staged, working, expected
    ):
        path = repository / "changed.go"
        path.write_bytes(staged.encode())
        git(repository, "add", "changed.go")
        if working is None:
            path.unlink()
        else:
            path.write_bytes(working.encode())
        runner = ReviewRunner()
    
        if expected is GateStatus.FAILED:
            with pytest.raises(ToolchainGateFailed) as failure:
                review(repository, runner, DiffSource.STAGED)
            formatting = next(gate for gate in failure.value.failures if gate.name == "fmt")
            assert "changed.go" in formatting.summary
            assert model_prompts == []
        else:
>           outcome = review(repository, runner, DiffSource.STAGED)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:170: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:116: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.STAGED: 'staged'>, base_ref=None)
runner = <tests.test_review_formatting.ReviewRunner object at 0x000002040F314640>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-399/test_staged_formatting_uses_in2')

    def capture_review_diff(
        request: DiffRequest,
        runner: CommandRunner,
        working_directory: Path,
    ) -> tuple[CapturedDiff, ChangedFilesFormatGate]:
        """Capture the patch and changed-file identities in the same Git operation."""
    
        if request.source is not DiffSource.WORKING:
>           raise DiffUnavailable("This formatting snapshot source is not supported.")
E           atom.diff.DiffUnavailable: This formatting snapshot source is not supported.

atom\_review_format.py:89: DiffUnavailable
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_staged_formatting_uses_index_snapshot_not_working_file[clean-index-dirty-worktree]
FAILED tests/test_review_formatting.py::test_staged_formatting_uses_index_snapshot_not_working_file[dirty-index-clean-worktree]
FAILED tests/test_review_formatting.py::test_staged_formatting_uses_index_snapshot_not_working_file[worktree-file-absent]
========================= 3 failed, 1 passed in 1.61s =========================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 4 items

tests\test_review_formatting.py ....                                     [100%]

============================== 4 passed in 2.51s ==============================
~~~~

## Committed branch snapshot

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k branch_formatting
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items / 4 deselected / 1 selected

tests\test_review_formatting.py F                                        [100%]

================================== FAILURES ===================================
__ test_branch_formatting_uses_committed_content_despite_dirty_working_file ___

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-401/test_branch_formatting_uses_co0')
model_prompts = []

    def test_branch_formatting_uses_committed_content_despite_dirty_working_file(
        repository: Path, model_prompts: list[str]
    ):
        base = git(repository, "rev-parse", "HEAD").strip()
        (repository / "changed.go").write_bytes(CLEAN.encode())
        git(repository, "add", "changed.go")
        git(repository, "commit", "--quiet", "-m", "selected clean source")
        (repository / "changed.go").write_bytes(BAD.encode())
        runner = ReviewRunner()
    
>       outcome = review(repository, runner, DiffSource.BRANCH, base)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:189: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:116: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.BRANCH: 'branch'>, base_ref='769273ee7c9b5483fd513f9bbe29e49c45daba2b')
runner = <tests.test_review_formatting.ReviewRunner object at 0x000001C49EACBCB0>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-401/test_branch_formatting_uses_co0')

    def capture_review_diff(
        request: DiffRequest,
        runner: CommandRunner,
        working_directory: Path,
    ) -> tuple[CapturedDiff, ChangedFilesFormatGate]:
        """Capture the patch and changed-file identities in the same Git operation."""
    
        if request.source not in (DiffSource.WORKING, DiffSource.STAGED):
>           raise DiffUnavailable("This formatting snapshot source is not supported.")
E           atom.diff.DiffUnavailable: This formatting snapshot source is not supported.

atom\_review_format.py:120: DiffUnavailable
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_branch_formatting_uses_committed_content_despite_dirty_working_file
======================= 1 failed, 4 deselected in 0.65s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items

tests\test_review_formatting.py .....                                    [100%]

============================== 5 passed in 3.66s ==============================
~~~~

## Pure rename destination and canonical paths

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k pure_rename
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items / 5 deselected / 1 selected

tests\test_review_formatting.py F                                        [100%]

================================== FAILURES ===================================
___ test_pure_rename_formats_destination_and_preserves_canonical_diff_path ____

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-403/test_pure_rename_formats_desti0')
model_prompts = []

    def test_pure_rename_formats_destination_and_preserves_canonical_diff_path(
        repository: Path, model_prompts: list[str]
    ):
        git(repository, "mv", "changed.go", "renamed file.go")
        runner = ReviewRunner()
    
>       outcome = review(repository, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:205: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:116: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.STAGED: 'staged'>, base_ref=None)
runner = <tests.test_review_formatting.ReviewRunner object at 0x00000163D6612A50>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-403/test_pure_rename_formats_desti0')

    def capture_review_diff(
        request: DiffRequest,
        runner: CommandRunner,
        working_directory: Path,
    ) -> tuple[CapturedDiff, ChangedFilesFormatGate]:
        """Capture the patch and changed-file identities in the same Git operation."""
    
        root = Path(_git(
            runner, working_directory, ("git", "rev-parse", "--show-toplevel")
        ).rstrip("\r\n")).resolve()
        selected_request = request
        if request.source is DiffSource.BRANCH:
            base = _git(
                runner, working_directory,
                ("git", "rev-parse", "--verify", "--end-of-options", f"{request.base_ref}^{{commit}}"),
            ).strip()
            selected_request = DiffRequest(DiffSource.BRANCH, base)
        command = git_command_for(selected_request) + (
            "--raw", "--no-abbrev", "-z", "--patch", "--full-index",
            "--no-ext-diff", "--no-textconv", "--no-color", "--no-relative", "--",
        )
        raw = _git(runner, working_directory, command)
        if not raw:
            return CapturedDiff("", request), ChangedFilesFormatGate((), request.describe())
        metadata, separator, patch = raw.partition("\0\0")
        if not separator:
            raise DiffUnavailable("Git did not provide a framed review file manifest.")
        fields = metadata.split("\0")
        blocks = re.split(r"(?m)(?=^diff --git )", patch)[1:]
        files: list[FormattingFile] = []
        index = 0
        block_index = 0
        while index < len(fields):
            header = fields[index].split()
            if len(header) != 5 or index + 1 >= len(fields):
>               raise DiffUnavailable("Git provided a malformed review file manifest.")
E               atom.diff.DiffUnavailable: Git provided a malformed review file manifest.

atom\_review_format.py:147: DiffUnavailable
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_pure_rename_formats_destination_and_preserves_canonical_diff_path
======================= 1 failed, 5 deselected in 1.02s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 6 items

tests\test_review_formatting.py ......                                   [100%]

============================== 6 passed in 4.45s ==============================
~~~~

## Zero-file formatting coverage

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k no_surviving
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 9 items / 6 deselected / 3 selected

tests\test_review_formatting.py FFF                                      [100%]

================================== FAILURES ===================================
____ test_no_surviving_go_files_skips_formatter_with_explicit_scope[empty] ____

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-405/test_no_surviving_go_files_ski0')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu...em\n\nRespond with the JSON array and nothing else. No prose, no explanation, no headings.\n\nHere is the diff:\n\n\n']
change = 'empty'

    @pytest.mark.parametrize("change", ("empty", "non-go", "deleted"))
    def test_no_surviving_go_files_skips_formatter_with_explicit_scope(
        repository: Path, model_prompts: list[str], change
    ):
        if change == "non-go":
            (repository / "README.md").write_text("fixture\n", encoding="utf-8")
            git(repository, "add", "README.md")
        elif change == "deleted":
            git(repository, "rm", "--quiet", "changed.go")
        runner = ReviewRunner()
    
        outcome = review(repository, runner, DiffSource.STAGED)
    
        formatting = next(gate for gate in outcome.toolchain.gate_results if gate.name == "fmt")
>       assert formatting.status is GateStatus.SKIPPED
E       AssertionError: assert <GateStatus.PASSED: 'passed'> is <GateStatus.SKIPPED: 'skipped'>
E        +  where <GateStatus.PASSED: 'passed'> = GateResult(name='fmt', status=<GateStatus.PASSED: 'passed'>, summary='Checked 0 changed Go file(s) from staged changes: ', details='Formatting applies only to these selected file snapshots.', required=True, duration_seconds=0.0).status
E        +  and   <GateStatus.SKIPPED: 'skipped'> = GateStatus.SKIPPED

tests\test_review_formatting.py:227: AssertionError
___ test_no_surviving_go_files_skips_formatter_with_explicit_scope[non-go] ____

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-405/test_no_surviving_go_files_ski1')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu...00000000000000..ea35a87ca89191b486513d92bf87cb03df59be2c\n--- /dev/null\n+++ b/README.md\n@@ -0,0 +1 @@\n+fixture\n\n']
change = 'non-go'

    @pytest.mark.parametrize("change", ("empty", "non-go", "deleted"))
    def test_no_surviving_go_files_skips_formatter_with_explicit_scope(
        repository: Path, model_prompts: list[str], change
    ):
        if change == "non-go":
            (repository / "README.md").write_text("fixture\n", encoding="utf-8")
            git(repository, "add", "README.md")
        elif change == "deleted":
            git(repository, "rm", "--quiet", "changed.go")
        runner = ReviewRunner()
    
        outcome = review(repository, runner, DiffSource.STAGED)
    
        formatting = next(gate for gate in outcome.toolchain.gate_results if gate.name == "fmt")
>       assert formatting.status is GateStatus.SKIPPED
E       AssertionError: assert <GateStatus.PASSED: 'passed'> is <GateStatus.SKIPPED: 'skipped'>
E        +  where <GateStatus.PASSED: 'passed'> = GateResult(name='fmt', status=<GateStatus.PASSED: 'passed'>, summary='Checked 0 changed Go file(s) from staged changes: ', details='Formatting applies only to these selected file snapshots.', required=True, duration_seconds=0.0).status
E        +  and   <GateStatus.SKIPPED: 'skipped'> = GateStatus.SKIPPED

tests\test_review_formatting.py:227: AssertionError
___ test_no_surviving_go_files_skips_formatter_with_explicit_scope[deleted] ___

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-405/test_no_surviving_go_files_ski2')
model_prompts = [], change = 'deleted'

    @pytest.mark.parametrize("change", ("empty", "non-go", "deleted"))
    def test_no_surviving_go_files_skips_formatter_with_explicit_scope(
        repository: Path, model_prompts: list[str], change
    ):
        if change == "non-go":
            (repository / "README.md").write_text("fixture\n", encoding="utf-8")
            git(repository, "add", "README.md")
        elif change == "deleted":
            git(repository, "rm", "--quiet", "changed.go")
        runner = ReviewRunner()
    
>       outcome = review(repository, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:224: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:116: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\_review_format.py:168: in capture_review_diff
    content = _read_blob(runner, working_directory, header[3])
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

runner = <tests.test_review_formatting.ReviewRunner object at 0x000001550E5AE990>
directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-405/test_no_surviving_go_files_ski2')
object_id = '0000000000000000000000000000000000000000'

    def _read_blob(runner: CommandRunner, directory: Path, object_id: str) -> bytes:
        if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", object_id) or not int(object_id, 16):
>           raise DiffUnavailable("Git provided an invalid selected file identity.")
E           atom.diff.DiffUnavailable: Git provided an invalid selected file identity.

atom\_review_format.py:96: DiffUnavailable
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_no_surviving_go_files_skips_formatter_with_explicit_scope[empty]
FAILED tests/test_review_formatting.py::test_no_surviving_go_files_skips_formatter_with_explicit_scope[non-go]
FAILED tests/test_review_formatting.py::test_no_surviving_go_files_skips_formatter_with_explicit_scope[deleted]
======================= 3 failed, 6 deselected in 2.02s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 9 items

tests\test_review_formatting.py .........                                [100%]

============================== 9 passed in 6.04s ==============================
~~~~

## Outside and nested module exclusions

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k module_boundary
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 10 items / 9 deselected / 1 selected

tests\test_review_formatting.py F                                        [100%]

================================== FAILURES ===================================
_ test_module_boundary_exclusions_are_explicit_without_checking_other_modules _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-407/test_module_boundary_exclusion0')
model_prompts = []

    def test_module_boundary_exclusions_are_explicit_without_checking_other_modules(
        repository: Path, model_prompts: list[str]
    ):
        module = repository / "service"
        nested = module / "nested"
        nested.mkdir(parents=True)
        for directory in (module, nested):
            (directory / "go.mod").write_bytes(b"module example.invalid/sub\n\ngo 1.23\n")
            (directory / "source.go").write_bytes(BASE.encode())
        git(repository, "add", "--all")
        git(repository, "commit", "--quiet", "-m", "module fixtures")
        (repository / "changed.go").write_bytes(BAD.encode())
        (nested / "source.go").write_bytes(BAD.encode())
        (module / "source.go").write_bytes(CLEAN.encode())
        runner = ReviewRunner()
    
>       outcome = review(module, runner)
                  ^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:251: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:116: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\_review_format.py:163: in capture_review_diff
    relative = root.joinpath(*name.split("/")).relative_to(working_directory.resolve()).as_posix()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-407/test_module_boundary_exclusion0/changed.go')
other = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-407/test_module_boundary_exclusion0/service')
walk_up = False, _deprecated = ()

    def relative_to(self, other, /, *_deprecated, walk_up=False):
        """Return the relative path to another path identified by the passed
        arguments.  If the operation is not possible (because this is not
        related to the other path), raise ValueError.
    
        The *walk_up* parameter controls whether `..` may be used to resolve
        the path.
        """
        if _deprecated:
            msg = ("support for supplying more than one positional argument "
                   "to pathlib.PurePath.relative_to() is deprecated and "
                   "scheduled for removal in Python 3.14")
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            other = self.with_segments(other, *_deprecated)
        elif not isinstance(other, PurePath):
            other = self.with_segments(other)
        for step, path in enumerate(chain([other], other.parents)):
            if path == self or path in self.parents:
                break
            elif not walk_up:
>               raise ValueError(f"{str(self)!r} is not in the subpath of {str(other)!r}")
E               ValueError: 'C:\\Users\\gimotwan\\AppData\\Local\\Temp\\pytest-of-gimotwan\\pytest-407\\test_module_boundary_exclusion0\\changed.go' is not in the subpath of 'C:\\Users\\gimotwan\\AppData\\Local\\Temp\\pytest-of-gimotwan\\pytest-407\\test_module_boundary_exclusion0\\service'

C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:385: ValueError
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_module_boundary_exclusions_are_explicit_without_checking_other_modules
======================= 1 failed, 9 deselected in 0.81s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 10 items

tests\test_review_formatting.py ..........                               [100%]

============================= 10 passed in 5.97s ==============================
~~~~

## Honest formatting prompt

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k prompt_names
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 12 items / 10 deselected / 2 selected

tests\test_review_formatting.py FF                                       [100%]

================================== FAILURES ===================================
_ test_prompt_names_selected_formatting_scope_without_claiming_module_scan[True] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-409/test_prompt_names_selected_for0')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu... 100644\n--- a/changed.go\n+++ b/changed.go\n@@ -1,3 +1,3 @@\n package fixture\n \n-var Value = 1\n+var Value = 2\n\n']
has_go_change = True

    @pytest.mark.parametrize("has_go_change", (True, False))
    def test_prompt_names_selected_formatting_scope_without_claiming_module_scan(
        repository: Path, model_prompts: list[str], has_go_change
    ):
        if has_go_change:
            (repository / "changed.go").write_bytes(CLEAN.encode())
    
        review(repository, ReviewRunner())
    
        prompt = model_prompts[0]
>       assert "gofmt -l ." not in prompt
E       AssertionError: assert 'gofmt -l .' not in 'You are rev...alue = 2\n\n'
E         
E         'gofmt -l .' is contained here:
E            PASSED
E             gofmt -l .           PASSED
E         ?   ++++++++++
E             go test ./...        PASSED
E             go test -race ./...  PASSED...
E         
E         ...Full output truncated (71 lines hidden), use '-vv' to show

tests\test_review_formatting.py:271: AssertionError
_ test_prompt_names_selected_formatting_scope_without_claiming_module_scan[False] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-409/test_prompt_names_selected_for1')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu...em\n\nRespond with the JSON array and nothing else. No prose, no explanation, no headings.\n\nHere is the diff:\n\n\n']
has_go_change = False

    @pytest.mark.parametrize("has_go_change", (True, False))
    def test_prompt_names_selected_formatting_scope_without_claiming_module_scan(
        repository: Path, model_prompts: list[str], has_go_change
    ):
        if has_go_change:
            (repository / "changed.go").write_bytes(CLEAN.encode())
    
        review(repository, ReviewRunner())
    
        prompt = model_prompts[0]
>       assert "gofmt -l ." not in prompt
E       AssertionError: assert 'gofmt -l .' not in 'You are rev... diff:\n\n\n'
E         
E         'gofmt -l .' is contained here:
E            PASSED
E             gofmt -l .           SKIPPED - Checked 0 changed Go files from unstaged working-tree changes
E         ?   ++++++++++
E             go test ./...        PASSED
E             go test -race ./...  PASSED...
E         
E         ...Full output truncated (62 lines hidden), use '-vv' to show

tests\test_review_formatting.py:271: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_prompt_names_selected_formatting_scope_without_claiming_module_scan[True]
FAILED tests/test_review_formatting.py::test_prompt_names_selected_formatting_scope_without_claiming_module_scan[False]
====================== 2 failed, 10 deselected in 1.07s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py tests\test_toolchain.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 15 items

tests\test_review_formatting.py ............                             [ 80%]
tests\test_toolchain.py ...                                              [100%]

============================= 15 passed in 7.15s ==============================
~~~~

## Non-regular Git entry refusal

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k non_regular
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 13 items / 12 deselected / 1 selected

tests\test_review_formatting.py F                                        [100%]

================================== FAILURES ===================================
__ test_non_regular_selected_go_entry_is_refused_before_formatter_or_models ___

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-411/test_non_regular_selected_go_e0')
model_prompts = []

    def test_non_regular_selected_go_entry_is_refused_before_formatter_or_models(
        repository: Path, model_prompts: list[str]
    ):
        identity = git(repository, "rev-parse", "HEAD:changed.go").strip()
        git(repository, "update-index", "--cacheinfo", f"120000,{identity},changed.go")
        runner = ReviewRunner()
    
>       with pytest.raises(DiffUnavailable, match="non-regular"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: Regex pattern did not match.
E         Expected regex: 'non-regular'
E         Actual message: 'Git manifest and patch entries do not match.'

tests\test_review_formatting.py:289: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_non_regular_selected_go_entry_is_refused_before_formatter_or_models
====================== 1 failed, 12 deselected in 1.07s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q -k non_regular
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 13 items / 12 deselected / 1 selected

tests\test_review_formatting.py .                                        [100%]

====================== 1 passed, 12 deselected in 0.59s =======================
~~~~

## Malformed manifest and unsafe path refusal

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k invalid_manifest
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 20 items / 13 deselected / 7 selected

tests\test_review_formatting.py ..FFFFF                                  [100%]

================================== FAILURES ===================================
_ test_invalid_manifest_is_refused_without_empty_scope_success[windows-path] __

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-413/test_invalid_manifest_is_refus2')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu... 100644\n--- a/changed.go\n+++ b/changed.go\n@@ -1,3 +1,3 @@\n package fixture\n \n-var Value = 1\n+var Value = 2\n\n']
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x00000177B88A5250>
corruption = 'windows-path'

    @pytest.mark.parametrize(
        "corruption",
        ("parent-path", "absolute-path", "windows-path", "unmerged", "unknown-status", "bad-mode", "bad-identity"),
    )
    def test_invalid_manifest_is_refused_without_empty_scope_success(
        repository: Path, model_prompts: list[str], monkeypatch, corruption
    ):
        (repository / "changed.go").write_bytes(CLEAN.encode())
        runner = ReviewRunner()
        original_run = runner.run
    
        def corrupt(command, directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                header, name = metadata.split("\0")
                fields = header.split()
                if corruption == "parent-path":
                    name = "../outside.go"
                elif corruption == "absolute-path":
                    name = "/outside.go"
                elif corruption == "windows-path":
                    name = "C:\\outside.go"
                elif corruption == "unmerged":
                    fields[4] = "U"
                elif corruption == "unknown-status":
                    fields[4] = "Q"
                elif corruption == "bad-mode":
                    fields[0] = ":oops"
                else:
                    fields[2] = "not-a-hash"
                result = replace(result, stdout=" ".join(fields) + "\0" + name + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", corrupt)
>       with pytest.raises(DiffUnavailable, match="unsafe|invalid|malformed|unmerged"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE DiffUnavailable

tests\test_review_formatting.py:332: Failed
___ test_invalid_manifest_is_refused_without_empty_scope_success[unmerged] ____

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-413/test_invalid_manifest_is_refus3')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu... 100644\n--- a/changed.go\n+++ b/changed.go\n@@ -1,3 +1,3 @@\n package fixture\n \n-var Value = 1\n+var Value = 2\n\n']
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x00000177B884D260>
corruption = 'unmerged'

    @pytest.mark.parametrize(
        "corruption",
        ("parent-path", "absolute-path", "windows-path", "unmerged", "unknown-status", "bad-mode", "bad-identity"),
    )
    def test_invalid_manifest_is_refused_without_empty_scope_success(
        repository: Path, model_prompts: list[str], monkeypatch, corruption
    ):
        (repository / "changed.go").write_bytes(CLEAN.encode())
        runner = ReviewRunner()
        original_run = runner.run
    
        def corrupt(command, directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                header, name = metadata.split("\0")
                fields = header.split()
                if corruption == "parent-path":
                    name = "../outside.go"
                elif corruption == "absolute-path":
                    name = "/outside.go"
                elif corruption == "windows-path":
                    name = "C:\\outside.go"
                elif corruption == "unmerged":
                    fields[4] = "U"
                elif corruption == "unknown-status":
                    fields[4] = "Q"
                elif corruption == "bad-mode":
                    fields[0] = ":oops"
                else:
                    fields[2] = "not-a-hash"
                result = replace(result, stdout=" ".join(fields) + "\0" + name + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", corrupt)
>       with pytest.raises(DiffUnavailable, match="unsafe|invalid|malformed|unmerged"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE DiffUnavailable

tests\test_review_formatting.py:332: Failed
_ test_invalid_manifest_is_refused_without_empty_scope_success[unknown-status] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-413/test_invalid_manifest_is_refus4')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu... 100644\n--- a/changed.go\n+++ b/changed.go\n@@ -1,3 +1,3 @@\n package fixture\n \n-var Value = 1\n+var Value = 2\n\n']
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x00000177B884D480>
corruption = 'unknown-status'

    @pytest.mark.parametrize(
        "corruption",
        ("parent-path", "absolute-path", "windows-path", "unmerged", "unknown-status", "bad-mode", "bad-identity"),
    )
    def test_invalid_manifest_is_refused_without_empty_scope_success(
        repository: Path, model_prompts: list[str], monkeypatch, corruption
    ):
        (repository / "changed.go").write_bytes(CLEAN.encode())
        runner = ReviewRunner()
        original_run = runner.run
    
        def corrupt(command, directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                header, name = metadata.split("\0")
                fields = header.split()
                if corruption == "parent-path":
                    name = "../outside.go"
                elif corruption == "absolute-path":
                    name = "/outside.go"
                elif corruption == "windows-path":
                    name = "C:\\outside.go"
                elif corruption == "unmerged":
                    fields[4] = "U"
                elif corruption == "unknown-status":
                    fields[4] = "Q"
                elif corruption == "bad-mode":
                    fields[0] = ":oops"
                else:
                    fields[2] = "not-a-hash"
                result = replace(result, stdout=" ".join(fields) + "\0" + name + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", corrupt)
>       with pytest.raises(DiffUnavailable, match="unsafe|invalid|malformed|unmerged"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE DiffUnavailable

tests\test_review_formatting.py:332: Failed
___ test_invalid_manifest_is_refused_without_empty_scope_success[bad-mode] ____

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-413/test_invalid_manifest_is_refus5')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu... 100644\n--- a/changed.go\n+++ b/changed.go\n@@ -1,3 +1,3 @@\n package fixture\n \n-var Value = 1\n+var Value = 2\n\n']
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x00000177B895BC50>
corruption = 'bad-mode'

    @pytest.mark.parametrize(
        "corruption",
        ("parent-path", "absolute-path", "windows-path", "unmerged", "unknown-status", "bad-mode", "bad-identity"),
    )
    def test_invalid_manifest_is_refused_without_empty_scope_success(
        repository: Path, model_prompts: list[str], monkeypatch, corruption
    ):
        (repository / "changed.go").write_bytes(CLEAN.encode())
        runner = ReviewRunner()
        original_run = runner.run
    
        def corrupt(command, directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                header, name = metadata.split("\0")
                fields = header.split()
                if corruption == "parent-path":
                    name = "../outside.go"
                elif corruption == "absolute-path":
                    name = "/outside.go"
                elif corruption == "windows-path":
                    name = "C:\\outside.go"
                elif corruption == "unmerged":
                    fields[4] = "U"
                elif corruption == "unknown-status":
                    fields[4] = "Q"
                elif corruption == "bad-mode":
                    fields[0] = ":oops"
                else:
                    fields[2] = "not-a-hash"
                result = replace(result, stdout=" ".join(fields) + "\0" + name + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", corrupt)
>       with pytest.raises(DiffUnavailable, match="unsafe|invalid|malformed|unmerged"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE DiffUnavailable

tests\test_review_formatting.py:332: Failed
_ test_invalid_manifest_is_refused_without_empty_scope_success[bad-identity] __

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-413/test_invalid_manifest_is_refus6')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu... 100644\n--- a/changed.go\n+++ b/changed.go\n@@ -1,3 +1,3 @@\n package fixture\n \n-var Value = 1\n+var Value = 2\n\n']
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x00000177B8964350>
corruption = 'bad-identity'

    @pytest.mark.parametrize(
        "corruption",
        ("parent-path", "absolute-path", "windows-path", "unmerged", "unknown-status", "bad-mode", "bad-identity"),
    )
    def test_invalid_manifest_is_refused_without_empty_scope_success(
        repository: Path, model_prompts: list[str], monkeypatch, corruption
    ):
        (repository / "changed.go").write_bytes(CLEAN.encode())
        runner = ReviewRunner()
        original_run = runner.run
    
        def corrupt(command, directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                header, name = metadata.split("\0")
                fields = header.split()
                if corruption == "parent-path":
                    name = "../outside.go"
                elif corruption == "absolute-path":
                    name = "/outside.go"
                elif corruption == "windows-path":
                    name = "C:\\outside.go"
                elif corruption == "unmerged":
                    fields[4] = "U"
                elif corruption == "unknown-status":
                    fields[4] = "Q"
                elif corruption == "bad-mode":
                    fields[0] = ":oops"
                else:
                    fields[2] = "not-a-hash"
                result = replace(result, stdout=" ".join(fields) + "\0" + name + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", corrupt)
>       with pytest.raises(DiffUnavailable, match="unsafe|invalid|malformed|unmerged"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE DiffUnavailable

tests\test_review_formatting.py:332: Failed
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[windows-path]
FAILED tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[unmerged]
FAILED tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[unknown-status]
FAILED tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[bad-mode]
FAILED tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[bad-identity]
================= 5 failed, 2 passed, 13 deselected in 3.14s ==================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 20 items

tests\test_review_formatting.py ....................                     [100%]

============================= 20 passed in 10.29s =============================
~~~~

## Invalid UTF-8 required failure

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k invalid_utf8
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 22 items / 20 deselected / 2 selected

tests\test_review_formatting.py FF                                       [100%]

================================== FAILURES ===================================
_ test_invalid_utf8_is_required_formatting_failure_not_replacement_success[DiffSource.WORKING] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-415/test_invalid_utf8_is_required_0')
model_prompts = [], source = <DiffSource.WORKING: 'working'>

    @pytest.mark.parametrize("source", (DiffSource.WORKING, DiffSource.STAGED))
    def test_invalid_utf8_is_required_formatting_failure_not_replacement_success(
        repository: Path, model_prompts: list[str], source
    ):
        (repository / "changed.go").write_bytes(b"package fixture\n\n// invalid \xff\n")
        if source is DiffSource.STAGED:
            git(repository, "add", "changed.go")
        runner = ReviewRunner()
    
        with pytest.raises(ToolchainGateFailed) as raised:
>           review(repository, runner, source)

tests\test_review_formatting.py:348: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:117: in review
    return run_review(
atom\review.py:280: in run_review
    toolchain = _collect_toolchain_evidence(
atom\review.py:347: in _collect_toolchain_evidence
    required_report = run_check(working_directory, required_gates, runner)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\check.py:66: in run_check
    gate_results = [gate.evaluate(runner, directory) for gate in gates]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <atom._review_format.ChangedFilesFormatGate object at 0x000001C3C8BFEF90>
runner = <tests.test_review_formatting.ReviewRunner object at 0x000001C3C8BFE270>
directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-415/test_invalid_utf8_is_required_0')

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult:
        scope = (
            f"Formatting checks selected snapshots from {self.source}: "
            + ", ".join(repr(file.path) for file in self.files)
        )
        if self.exclusions:
            scope += "\nNot checked: " + "; ".join(self.exclusions)
        if not self.files:
            return GateResult(
                self.name, GateStatus.SKIPPED,
                f"Checked 0 changed Go files from {self.source}",
                f"No surviving changed Go files belong to this module.\n{scope}",
                True, 0.0,
            )
        duration = 0.0
        for file in self.files:
>           text = file.content.decode("utf-8").replace("\r\n", "\n")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 28: invalid start byte

atom\_review_format.py:69: UnicodeDecodeError
_ test_invalid_utf8_is_required_formatting_failure_not_replacement_success[DiffSource.STAGED] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-415/test_invalid_utf8_is_required_1')
model_prompts = [], source = <DiffSource.STAGED: 'staged'>

    @pytest.mark.parametrize("source", (DiffSource.WORKING, DiffSource.STAGED))
    def test_invalid_utf8_is_required_formatting_failure_not_replacement_success(
        repository: Path, model_prompts: list[str], source
    ):
        (repository / "changed.go").write_bytes(b"package fixture\n\n// invalid \xff\n")
        if source is DiffSource.STAGED:
            git(repository, "add", "changed.go")
        runner = ReviewRunner()
    
        with pytest.raises(ToolchainGateFailed) as raised:
>           review(repository, runner, source)

tests\test_review_formatting.py:348: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:117: in review
    return run_review(
atom\review.py:280: in run_review
    toolchain = _collect_toolchain_evidence(
atom\review.py:347: in _collect_toolchain_evidence
    required_report = run_check(working_directory, required_gates, runner)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\check.py:66: in run_check
    gate_results = [gate.evaluate(runner, directory) for gate in gates]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <atom._review_format.ChangedFilesFormatGate object at 0x000001C3C8C12AD0>
runner = <tests.test_review_formatting.ReviewRunner object at 0x000001C3C8C12350>
directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-415/test_invalid_utf8_is_required_1')

    def evaluate(self, runner: CommandRunner, directory: Path) -> GateResult:
        scope = (
            f"Formatting checks selected snapshots from {self.source}: "
            + ", ".join(repr(file.path) for file in self.files)
        )
        if self.exclusions:
            scope += "\nNot checked: " + "; ".join(self.exclusions)
        if not self.files:
            return GateResult(
                self.name, GateStatus.SKIPPED,
                f"Checked 0 changed Go files from {self.source}",
                f"No surviving changed Go files belong to this module.\n{scope}",
                True, 0.0,
            )
        duration = 0.0
        for file in self.files:
>           text = file.content.decode("utf-8").replace("\r\n", "\n")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 28: invalid start byte

atom\_review_format.py:69: UnicodeDecodeError
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_invalid_utf8_is_required_formatting_failure_not_replacement_success[DiffSource.WORKING]
FAILED tests/test_review_formatting.py::test_invalid_utf8_is_required_formatting_failure_not_replacement_success[DiffSource.STAGED]
====================== 2 failed, 20 deselected in 1.37s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q -k invalid_utf8
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 22 items / 20 deselected / 2 selected

tests\test_review_formatting.py ..                                       [100%]

====================== 2 passed, 20 deselected in 1.22s =======================
~~~~

## Non-regular working path substitution

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k substituted
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 23 items / 22 deselected / 1 selected

tests\test_review_formatting.py F                                        [100%]

================================== FAILURES ===================================
_______ test_working_file_substituted_with_non_regular_path_is_not_read _______

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-417/test_working_file_substituted_0')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu... 100644\n--- a/changed.go\n+++ b/changed.go\n@@ -1,3 +1,3 @@\n package fixture\n \n-var Value = 1\n+var Value = 2\n\n']
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001F06EB708A0>

    def test_working_file_substituted_with_non_regular_path_is_not_read(
        repository: Path, model_prompts: list[str], monkeypatch
    ):
        path = repository / "changed.go"
        path.write_bytes(CLEAN.encode())
        original_lstat = Path.lstat
        original_read = Path.read_bytes
        read_attempts = []
    
        def substituted_lstat(candidate):
            result = original_lstat(candidate)
            if candidate == path:
                values = list(result)
                values[0] = stat.S_IFLNK | 0o777
                return type(result)(values)
            return result
    
        def read(candidate):
            if candidate == path:
                read_attempts.append(candidate)
            return original_read(candidate)
    
        monkeypatch.setattr(Path, "lstat", substituted_lstat)
        monkeypatch.setattr(Path, "read_bytes", read)
    
>       with pytest.raises(DiffUnavailable, match="non-regular|unsafe"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE DiffUnavailable

tests\test_review_formatting.py:383: Failed
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_working_file_substituted_with_non_regular_path_is_not_read
====================== 1 failed, 22 deselected in 0.96s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 23 items

tests\test_review_formatting.py .......................                  [100%]

============================= 23 passed in 13.07s =============================
~~~~

## CLI JSON and Markdown formatting coverage

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k cli_reports
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 46 items / 44 deselected / 2 selected

tests\test_review_formatting.py FF                                       [100%]

================================== FAILURES ===================================
__________ test_cli_reports_selected_file_formatting_coverage[False] __________

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-421/test_cli_reports_selected_file0')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu... 100644\n--- a/changed.go\n+++ b/changed.go\n@@ -1,3 +1,3 @@\n package fixture\n \n-var Value = 1\n+var Value = 2\n\n']
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000002910B491810>
capsys = <_pytest.capture.CaptureFixture object at 0x000002910B14F8C0>
as_json = False

    @pytest.mark.parametrize("as_json", (False, True))
    def test_cli_reports_selected_file_formatting_coverage(
        repository: Path, model_prompts: list[str], monkeypatch, capsys, as_json
    ):
        (repository / "changed.go").write_bytes(CLEAN.encode())
        monkeypatch.chdir(repository)
        monkeypatch.setattr("atom.cli.SubprocessRunner", ReviewRunner)
        arguments = ["review", "--working", "--model", "fixture-model", "--runs", "1"]
        if as_json:
            arguments.append("--json")
    
        assert main(arguments) == EXIT_PASSED
    
        output = capsys.readouterr().out
        if as_json:
            payload = json.loads(output)
            formatting = next(gate for gate in payload["toolchain"]["gates"] if gate["name"] == "fmt")
            assert formatting["status"] == "passed"
            assert "changed.go" in formatting["summary"]
            assert "unstaged working-tree changes" in formatting["summary"]
        else:
>           assert "gofmt -l ." not in output
E           AssertionError: assert 'gofmt -l .' not in '# Code revi...eported.\n\n'
E             
E             'gofmt -l .' is contained here:
E               SSED |
E               | `gofmt -l .` | PASSED |
E             ?    ++++++++++
E               | `go test ./...` | PASSED |
E               | `go test -race ./...` | PASSED |...
E             
E             ...Full output truncated (8 lines hidden), use '-vv' to show

<worktree>\tools\tests\test_review_formatting.py:558: AssertionError
__________ test_cli_reports_selected_file_formatting_coverage[True] ___________

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-421/test_cli_reports_selected_file1')
model_prompts = ['You are reviewing a Go diff. Report real problems only.\nA Go toolchain ran over this code before review. These resu... 100644\n--- a/changed.go\n+++ b/changed.go\n@@ -1,3 +1,3 @@\n package fixture\n \n-var Value = 1\n+var Value = 2\n\n']
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000002910B4915B0>
capsys = <_pytest.capture.CaptureFixture object at 0x000002910B4656D0>
as_json = True

    @pytest.mark.parametrize("as_json", (False, True))
    def test_cli_reports_selected_file_formatting_coverage(
        repository: Path, model_prompts: list[str], monkeypatch, capsys, as_json
    ):
        (repository / "changed.go").write_bytes(CLEAN.encode())
        monkeypatch.chdir(repository)
        monkeypatch.setattr("atom.cli.SubprocessRunner", ReviewRunner)
        arguments = ["review", "--working", "--model", "fixture-model", "--runs", "1"]
        if as_json:
            arguments.append("--json")
    
        assert main(arguments) == EXIT_PASSED
    
        output = capsys.readouterr().out
        if as_json:
            payload = json.loads(output)
>           formatting = next(gate for gate in payload["toolchain"]["gates"] if gate["name"] == "fmt")
                                               ^^^^^^^^^^^^^^^^^^^^
E           KeyError: 'toolchain'

<worktree>\tools\tests\test_review_formatting.py:553: KeyError
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_cli_reports_selected_file_formatting_coverage[False]
FAILED tests/test_review_formatting.py::test_cli_reports_selected_file_formatting_coverage[True]
====================== 2 failed, 44 deselected in 1.37s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py tests\test_review_toolchain.py tests\test_toolchain.py tests\test_diff.py tests\test_gates.py tests\test_cli_review.py tests\test_review_output.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 219 items

tests\test_review_formatting.py ........................................ [ 18%]
......                                                                   [ 21%]
tests\test_review_toolchain.py ...                                       [ 22%]
tests\test_toolchain.py ...                                              [ 23%]
tests\test_diff.py ...................................                   [ 39%]
tests\test_gates.py ......................................               [ 57%]
tests\test_cli_review.py ..............................                  [ 70%]
tests\test_review_output.py ............................................ [ 90%]
....................                                                     [100%]

============================ 219 passed in 28.54s =============================
~~~~

## One raw type-change record versus two patch blocks

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k non_go_type
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 47 items / 46 deselected / 1 selected

tests\test_review_formatting.py F                                        [100%]

================================== FAILURES ===================================
_____ test_non_go_type_change_does_not_break_changed_go_snapshot_pairing ______

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-423/test_non_go_type_change_does_n0')
model_prompts = []

    def test_non_go_type_change_does_not_break_changed_go_snapshot_pairing(
        repository: Path, model_prompts: list[str]
    ):
        (repository / "first.txt").write_bytes(BASE.encode())
        git(repository, "add", "first.txt")
        git(repository, "commit", "--quiet", "-m", "regular text fixture")
        identity = git(repository, "rev-parse", "HEAD:first.txt").strip()
        git(repository, "update-index", "--cacheinfo", f"120000,{identity},first.txt")
        (repository / "changed.go").write_bytes(CLEAN.encode())
        git(repository, "add", "changed.go")
        runner = ReviewRunner()
    
>       outcome = review(repository, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:576: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:120: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.STAGED: 'staged'>, base_ref=None)
runner = <tests.test_review_formatting.ReviewRunner object at 0x000001CEBC6F8830>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-423/test_non_go_type_change_does_n0')

    def capture_review_diff(
        request: DiffRequest,
        runner: CommandRunner,
        working_directory: Path,
    ) -> tuple[CapturedDiff, ChangedFilesFormatGate]:
        """Capture the patch and changed-file identities in the same Git operation."""
    
        root = Path(_git(
            runner, working_directory, ("git", "rev-parse", "--show-toplevel")
        ).rstrip("\r\n")).resolve()
        selected_request = request
        if request.source is DiffSource.BRANCH:
            base = _git(
                runner, working_directory,
                ("git", "rev-parse", "--verify", "--end-of-options", f"{request.base_ref}^{{commit}}"),
            ).strip()
            selected_request = DiffRequest(DiffSource.BRANCH, base)
        command = git_command_for(selected_request) + (
            "--raw", "--no-abbrev", "-z", "--patch", "--full-index",
            "--no-ext-diff", "--no-textconv", "--no-color", "--no-relative", "--",
        )
        raw = _git(runner, working_directory, command)
        if not raw:
            return CapturedDiff("", request), ChangedFilesFormatGate((), request.describe())
        metadata, separator, patch = raw.partition("\0\0")
        if not separator:
            raise DiffUnavailable("Git did not provide a framed review file manifest.")
        fields = metadata.split("\0")
        blocks = re.split(r"(?m)(?=^diff --git )", patch)[1:]
        files: list[FormattingFile] = []
        paths: list[str] = []
        exclusions: list[str] = []
        index = 0
        block_index = 0
        while index < len(fields):
            record = fields[index]
            if not re.fullmatch(
                r":(?:[0-7]{6}) (?:[0-7]{6}) "
                r"(?:[0-9a-f]{40}|[0-9a-f]{64}) (?:[0-9a-f]{40}|[0-9a-f]{64}) "
                r"(?:[ADMT]|M[0-9]{1,3}|[RC][0-9]{1,3})",
                record,
            ) or index + 1 >= len(fields):
                raise DiffUnavailable("Git provided a malformed review file manifest.")
            header = record.split()
            name = fields[index + 1]
            _validate_name(name)
            index += 2
            if header[4].startswith(("R", "C")):
                if index >= len(fields):
                    raise DiffUnavailable("Git omitted a rename destination.")
                name = fields[index]
                _validate_name(name)
                index += 1
            paths.append(name)
            if name.endswith(".go") and header[4] != "D" and header[1] not in ("100644", "100755"):
                raise DiffUnavailable(f"Selected Go file {name!r} is a non-regular Git entry.")
            if block_index >= len(blocks):
                raise DiffUnavailable("Git manifest and patch entries do not match.")
            block = blocks[block_index]
            block_index += 1
            if not name.endswith(".go") or header[4] == "D":
                continue
            path = root.joinpath(*name.split("/"))
            if not path.is_relative_to(working_directory.resolve()):
                exclusions.append(f"{name!r}: outside selected module")
                continue
            relative = path.relative_to(working_directory.resolve()).as_posix()
            if request.source is DiffSource.WORKING:
                try:
                    if (
                        not stat.S_ISREG(path.lstat().st_mode)
                        or not path.resolve().is_relative_to(working_directory.resolve())
                    ):
                        raise DiffUnavailable(f"Changed Go file {name!r} is unsafe or non-regular.")
                except OSError as error:
                    raise DiffUnavailable(f"Could not inspect changed Go file {name!r}: {error}") from error
            if _belongs_to_a_nested_module(relative, working_directory):
                exclusions.append(f"{name!r}: nested module")
                continue
            try:
                relative = path.relative_to(working_directory.resolve()).as_posix()
                if request.source is not DiffSource.WORKING:
                    content = _read_blob(runner, working_directory, header[3])
                else:
                    content = path.read_bytes()
            except (OSError, ValueError) as error:
                raise DiffUnavailable(f"Could not read changed Go file {name!r}: {error}") from error
            if request.source is DiffSource.WORKING:
                identity = re.search(r"(?m)^index [0-9a-f]+\.\.([0-9a-f]+)", block)
                expected = identity.group(1) if identity else header[2]
                # Git may normalize CRLF while computing its diff, but no other
                # transforming filter can safely substitute the bytes we format.
                if all(
                    _blob_hash(candidate, expected) != expected
                    for candidate in (content, content.replace(b"\r\n", b"\n"))
                ):
                    raise DiffUnavailable(f"Changed Go file {name!r} no longer matches the captured diff.")
            files.append(FormattingFile(name, content))
        if block_index != len(blocks):
>           raise DiffUnavailable("Git manifest and patch entries do not match.")
E           atom.diff.DiffUnavailable: Git manifest and patch entries do not match.

atom\_review_format.py:247: DiffUnavailable
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_non_go_type_change_does_not_break_changed_go_snapshot_pairing
====================== 1 failed, 46 deselected in 1.86s =======================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q -k "type_change or non_regular"
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 47 items / 44 deselected / 3 selected

tests\test_review_formatting.py ...                                      [100%]

====================== 3 passed, 44 deselected in 2.12s =======================
~~~~

## Retain formatter diagnostics on a differing response

### RED

~~~~text
python -m pytest tests\test_review_formatting.py -q -k formatter_failures
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 57 items / 52 deselected / 5 selected

tests\test_review_formatting.py ....F                                    [100%]

================================== FAILURES ===================================
___ test_formatter_failures_keep_path_and_original_diagnostic[empty-stdout] ___

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-426/test_formatter_failures_keep_p4')
model_prompts = []
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001AACDA10270>
outcome = <CommandOutcome.COMPLETED: 'completed'>, exit_code = 0, stdout = ''

    @pytest.mark.parametrize(
        ("outcome", "exit_code", "stdout"),
        (
            (CommandOutcome.TOOL_MISSING, None, ""),
            (CommandOutcome.TIMED_OUT, None, ""),
            (CommandOutcome.RUNNER_ERROR, None, ""),
            (CommandOutcome.COMPLETED, 2, ""),
            (CommandOutcome.COMPLETED, 0, ""),
        ),
        ids=("missing", "timeout", "runner-error", "syntax-error", "empty-stdout"),
    )
    def test_formatter_failures_keep_path_and_original_diagnostic(
        repository: Path, model_prompts: list[str], monkeypatch, outcome, exit_code, stdout
    ):
        (repository / "changed.go").write_bytes(CLEAN.encode())
        runner = ReviewRunner()
        original_run = runner.run
    
        def failing_format(command, directory, timeout_seconds=300, stdin_text=None):
            if command[0] == "gofmt":
                return command_result(
                    tuple(command), directory, outcome, exit_code,
                    stdout=stdout, stderr="formatter diagnostic",
                )
            return original_run(command, directory, timeout_seconds, stdin_text)
    
        monkeypatch.setattr(runner, "run", failing_format)
        with pytest.raises(ToolchainGateFailed) as raised:
            review(repository, runner)
        formatting = next(gate for gate in raised.value.failures if gate.name == "fmt")
        assert "changed.go" in formatting.summary
>       assert "formatter diagnostic" in formatting.details
E       assert 'formatter diagnostic' in 'Selected changed file: changed.go'
E        +  where 'Selected changed file: changed.go' = GateResult(name='fmt', status=<GateStatus.FAILED: 'failed'>, summary="'changed.go' needs gofmt (unstaged working-tree changes)", details='Selected changed file: changed.go', required=True, duration_seconds=0.25).details

tests\test_review_formatting.py:484: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[empty-stdout]
================= 1 failed, 4 passed, 52 deselected in 2.10s ==================
~~~~

### GREEN

~~~~text
python -m pytest tests\test_review_formatting.py -q -k formatter_failures
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 57 items / 52 deselected / 5 selected

tests\test_review_formatting.py .....                                    [100%]

====================== 5 passed, 52 deselected in 2.05s =======================
~~~~

## Additional guards: initial fixture failure, not production RED

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 44 items

tests\test_review_formatting.py ................................FF...... [ 90%]
....                                                                     [100%]

================================== FAILURES ===================================
_ test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[utf8-DiffSource.WORKING] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-419/test_selected_bytes_are_preser6')
model_prompts = [], source = <DiffSource.WORKING: 'working'>
content = b'package fixture\n\nvar Value = 2\n// caf\xc3\xa9\n', is_clean = True

    @pytest.mark.parametrize("source", (DiffSource.WORKING, DiffSource.STAGED))
    @pytest.mark.parametrize(
        ("content", "is_clean"),
        (
            (CLEAN.replace("\n", "\r\n").encode(), True),
            (CLEAN.replace("\n", "\r\n", 1).encode(), True),
            (BAD.replace("\n", "\r\n").encode(), False),
            ((CLEAN + "// caf" + chr(0xe9) + "\n").encode(), True),
        ),
        ids=("crlf", "mixed-endings", "crlf-real-formatting-defect", "utf8"),
    )
    def test_selected_bytes_are_preserved_and_only_line_endings_are_normalized(
        repository: Path, model_prompts: list[str], source, content, is_clean
    ):
        path = repository / "changed.go"
        path.write_bytes(content)
        if source is DiffSource.STAGED:
            git(repository, "add", "changed.go")
        before = git(repository, "status", "--porcelain=v1")
        runner = ReviewRunner()
    
        if is_clean:
>           review(repository, runner, source)

tests\test_review_formatting.py:438: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:118: in review
    return run_review(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.WORKING: 'working'>, base_ref=None)
models = ('fixture-model',)
runner = <tests.test_review_formatting.ReviewRunner object at 0x0000015F6D34D2B0>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-419/test_selected_bytes_are_preser6')
runs = 1, concurrency = 1, window = 3, disable_mcp_servers = ()
skip_toolchain = False, include_style_rules = True

    def run_review(
        request: DiffRequest,
        models: Sequence[str],
        runner: CommandRunner,
        working_directory: Path,
        runs: int,
        concurrency: int,
        window: int = DEFAULT_PROXIMITY_WINDOW,
        disable_mcp_servers: Sequence[str] = (),
        skip_toolchain: bool = False,
        include_style_rules: bool = True,
    ) -> ReviewOutcome:
        """Capture a diff, ask every model about it, and merge what comes back.
    
        The order is fixed and the failures are not symmetric. A diff that cannot
        be captured raises, because there is nothing to review and pretending
        otherwise would produce a confident empty report. Everything after that
        point degrades instead: a run that fails is recorded, a reply nobody can
        parse is recorded, and the review continues with whatever answered (B129).
    
        `include_style_rules` exists for measurement, not for callers. Whether
        handing a reviewer seven consequence-phrased rules changes what it reports
        is an open question, and answering it needs the same review run with the
        rules absent. The CLI does not expose the switch, so the shipped behaviour
        is always on.
        """
    
        format_gate = None
        if not skip_toolchain and (working_directory / "go.mod").is_file():
            diff, format_gate = capture_review_diff(request, runner, working_directory)
        else:
            diff = capture_diff(request, runner, working_directory)
    
        toolchain = _collect_toolchain_evidence(
            working_directory, runner, skip_toolchain=skip_toolchain,
            format_gate=format_gate,
        )
        if toolchain.blocking_failures:
>           raise ToolchainGateFailed(toolchain.blocking_failures)
E           atom.review.ToolchainGateFailed: Required toolchain gates failed: fmt

atom\review.py:285: ToolchainGateFailed
_ test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[utf8-DiffSource.STAGED] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-419/test_selected_bytes_are_preser7')
model_prompts = [], source = <DiffSource.STAGED: 'staged'>
content = b'package fixture\n\nvar Value = 2\n// caf\xc3\xa9\n', is_clean = True

    @pytest.mark.parametrize("source", (DiffSource.WORKING, DiffSource.STAGED))
    @pytest.mark.parametrize(
        ("content", "is_clean"),
        (
            (CLEAN.replace("\n", "\r\n").encode(), True),
            (CLEAN.replace("\n", "\r\n", 1).encode(), True),
            (BAD.replace("\n", "\r\n").encode(), False),
            ((CLEAN + "// caf" + chr(0xe9) + "\n").encode(), True),
        ),
        ids=("crlf", "mixed-endings", "crlf-real-formatting-defect", "utf8"),
    )
    def test_selected_bytes_are_preserved_and_only_line_endings_are_normalized(
        repository: Path, model_prompts: list[str], source, content, is_clean
    ):
        path = repository / "changed.go"
        path.write_bytes(content)
        if source is DiffSource.STAGED:
            git(repository, "add", "changed.go")
        before = git(repository, "status", "--porcelain=v1")
        runner = ReviewRunner()
    
        if is_clean:
>           review(repository, runner, source)

tests\test_review_formatting.py:438: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:118: in review
    return run_review(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.STAGED: 'staged'>, base_ref=None)
models = ('fixture-model',)
runner = <tests.test_review_formatting.ReviewRunner object at 0x0000015F6D34F710>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-419/test_selected_bytes_are_preser7')
runs = 1, concurrency = 1, window = 3, disable_mcp_servers = ()
skip_toolchain = False, include_style_rules = True

    def run_review(
        request: DiffRequest,
        models: Sequence[str],
        runner: CommandRunner,
        working_directory: Path,
        runs: int,
        concurrency: int,
        window: int = DEFAULT_PROXIMITY_WINDOW,
        disable_mcp_servers: Sequence[str] = (),
        skip_toolchain: bool = False,
        include_style_rules: bool = True,
    ) -> ReviewOutcome:
        """Capture a diff, ask every model about it, and merge what comes back.
    
        The order is fixed and the failures are not symmetric. A diff that cannot
        be captured raises, because there is nothing to review and pretending
        otherwise would produce a confident empty report. Everything after that
        point degrades instead: a run that fails is recorded, a reply nobody can
        parse is recorded, and the review continues with whatever answered (B129).
    
        `include_style_rules` exists for measurement, not for callers. Whether
        handing a reviewer seven consequence-phrased rules changes what it reports
        is an open question, and answering it needs the same review run with the
        rules absent. The CLI does not expose the switch, so the shipped behaviour
        is always on.
        """
    
        format_gate = None
        if not skip_toolchain and (working_directory / "go.mod").is_file():
            diff, format_gate = capture_review_diff(request, runner, working_directory)
        else:
            diff = capture_diff(request, runner, working_directory)
    
        toolchain = _collect_toolchain_evidence(
            working_directory, runner, skip_toolchain=skip_toolchain,
            format_gate=format_gate,
        )
        if toolchain.blocking_failures:
>           raise ToolchainGateFailed(toolchain.blocking_failures)
E           atom.review.ToolchainGateFailed: Required toolchain gates failed: fmt

atom\review.py:285: ToolchainGateFailed
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[utf8-DiffSource.WORKING]
FAILED tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[utf8-DiffSource.STAGED]
======================== 2 failed, 42 passed in 23.77s ========================
~~~~

## Combined guards: legacy fixture lacked new Git boundary

~~~~text
python -m pytest tests\test_review_formatting.py tests\test_review_toolchain.py tests\test_toolchain.py tests\test_diff.py tests\test_gates.py tests\test_cli_review.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 153 items

tests\test_review_formatting.py ........................................ [ 26%]
....                                                                     [ 28%]
tests\test_review_toolchain.py .F.                                       [ 30%]
tests\test_toolchain.py ...                                              [ 32%]
tests\test_diff.py ...................................                   [ 55%]
tests\test_gates.py ......................................               [ 80%]
tests\test_cli_review.py ..............................                  [100%]

================================== FAILURES ===================================
________ test_run_review_blocks_before_models_when_required_gate_fails ________

tmp_path = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-420/test_run_review_blocks_before_0')

    def test_run_review_blocks_before_models_when_required_gate_fails(tmp_path):
        """A tree that fails required gates is not ready to spend model calls."""
        (tmp_path / "go.mod").write_text("module example.com/toolchain\n", encoding="utf-8")
        build = ("go", "build", "./...")
        runner = FakeRunner({
            build: command_result(build, tmp_path, exit_code=1, stderr="compile failed"),
            ("go", "vet", "./..."): command_result(("go", "vet", "./..."), tmp_path),
            ("gofmt", "-l", "."): command_result(("gofmt", "-l", "."), tmp_path),
            ("go", "test", "./..."): command_result(("go", "test", "./..."), tmp_path, stdout="ok example 0.1s\n"),
            ("go", "test", "-race", "./..."): command_result(("go", "test", "-race", "./..."), tmp_path, stdout="ok example 0.1s\n"),
            ("staticcheck", "./..."): command_result(("staticcheck", "./..."), tmp_path),
            ("errcheck", "./..."): command_result(("errcheck", "./..."), tmp_path),
            ("govulncheck", "./..."): command_result(("govulncheck", "./..."), tmp_path),
        })
    
        with pytest.raises(ToolchainGateFailed) as raised:
>           run_review(
                request=DiffRequest(DiffSource.WORKING, None),
                models=("gpt-5.4",),
                runner=runner,
                working_directory=tmp_path,
                runs=1,
                concurrency=1,
            )

tests\test_review_toolchain.py:58: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\_review_format.py:155: in capture_review_diff
    root = Path(_git(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

runner = <tests.conftest.FakeRunner object at 0x000001E33FE31FD0>
directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-420/test_run_review_blocks_before_0')
command = ('git', 'rev-parse', '--show-toplevel')

    def _git(runner: CommandRunner, directory: Path, command: tuple[str, ...]) -> str:
        result = runner.run(command, directory, 60)
        if not result.succeeded:
            detail = result.combined_output or result.outcome.value
>           raise DiffUnavailable(f"Could not capture review formatting inputs: {detail}")
E           atom.diff.DiffUnavailable: Could not capture review formatting inputs: missing: git

atom\_review_format.py:112: DiffUnavailable
=========================== short test summary info ===========================
FAILED tests/test_review_toolchain.py::test_run_review_blocks_before_models_when_required_gate_fails
======================= 1 failed, 152 passed in 27.57s ========================
~~~~

## Snapshot and unchanged-command guards

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 57 items

tests\test_review_formatting.py ........................................ [ 70%]
.................                                                        [100%]

============================= 57 passed in 33.62s =============================
~~~~


## Independent review repairs

One round only; no extra model calls after fixes. Both Opus findings were accepted. The submodule diff-mode arm already passed; only log mode is claimed as reproduced RED. All six unread-name cases failed before the path-validation repair.

### Submodule display framing

RED:

~~~~text
python -m pytest tests\test_review_formatting.py -q -k submodule_display
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 59 items / 57 deselected / 2 selected

tests\test_review_formatting.py F.                                       [100%]

================================== FAILURES ===================================
___ test_submodule_display_config_cannot_change_manifest_patch_framing[log] ___

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-431/test_submodule_display_config_0')
model_prompts = [], display = 'log'

    @pytest.mark.parametrize("display", ("log", "diff"))
    def test_submodule_display_config_cannot_change_manifest_patch_framing(
        repository: Path, model_prompts: list[str], display
    ):
        dependency = repository / "dependency"
        dependency.mkdir()
        git(dependency, "init", "--quiet", "--initial-branch=main")
        (dependency / "source.txt").write_text("before\n", encoding="utf-8")
        git(dependency, "add", "source.txt")
        git(dependency, "commit", "--quiet", "-m", "dependency before")
        first = git(dependency, "rev-parse", "HEAD").strip()
        git(repository, "update-index", "--add", "--cacheinfo", f"160000,{first},dependency")
        git(repository, "commit", "--quiet", "-m", "dependency pointer fixture")
        (dependency / "source.txt").write_text("after\n", encoding="utf-8")
        git(dependency, "add", "source.txt")
        git(dependency, "commit", "--quiet", "-m", "dependency after")
        second = git(dependency, "rev-parse", "HEAD").strip()
        git(repository, "update-index", "--cacheinfo", f"160000,{second},dependency")
        (repository / "changed.go").write_bytes(CLEAN.encode())
        git(repository, "add", "changed.go")
        git(repository, "config", "--local", "diff.submodule", display)
        runner = ReviewRunner()
    
>       outcome = review(repository, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:697: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:120: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

request = DiffRequest(source=<DiffSource.STAGED: 'staged'>, base_ref=None)
runner = <tests.test_review_formatting.ReviewRunner object at 0x000001B3CD094830>
working_directory = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-431/test_submodule_display_config_0')

    def capture_review_diff(
        request: DiffRequest,
        runner: CommandRunner,
        working_directory: Path,
    ) -> tuple[CapturedDiff, ChangedFilesFormatGate]:
        """Capture the patch and changed-file identities in the same Git operation."""
    
        root = Path(_git(
            runner, working_directory, ("git", "rev-parse", "--show-toplevel")
        ).rstrip("\r\n")).resolve()
        module = working_directory.resolve()
        selected_request = request
        if request.source is DiffSource.BRANCH:
            base = _git(
                runner, working_directory,
                ("git", "rev-parse", "--verify", "--end-of-options", f"{request.base_ref}^{{commit}}"),
            ).strip()
            selected_request = DiffRequest(DiffSource.BRANCH, base)
        command = git_command_for(selected_request) + (
            "--raw", "--no-abbrev", "-z", "--patch", "--full-index",
            "--no-ext-diff", "--no-textconv", "--no-color", "--no-relative", "--",
        )
        raw = _git(runner, working_directory, command)
        if not raw:
            return CapturedDiff("", request), ChangedFilesFormatGate((), request.describe())
        metadata, separator, patch = raw.partition("\0\0")
        if not separator:
            raise DiffUnavailable("Git did not provide a framed review file manifest.")
        fields = metadata.split("\0")
        blocks = re.split(r"(?m)(?=^diff --git )", patch)[1:]
        files: list[FormattingFile] = []
        paths: list[str] = []
        exclusions: list[str] = []
        index = 0
        block_index = 0
        while index < len(fields):
            record = fields[index]
            if not re.fullmatch(
                r":(?:[0-7]{6}) (?:[0-7]{6}) "
                r"(?:[0-9a-f]{40}|[0-9a-f]{64}) (?:[0-9a-f]{40}|[0-9a-f]{64}) "
                r"(?:[ADMT]|M[0-9]{1,3}|[RC][0-9]{1,3})",
                record,
            ) or index + 1 >= len(fields):
                raise DiffUnavailable("Git provided a malformed review file manifest.")
            header = record.split()
            name = fields[index + 1]
            _validate_name(name)
            index += 2
            if header[4].startswith(("R", "C")):
                if index >= len(fields):
                    raise DiffUnavailable("Git omitted a rename destination.")
                name = fields[index]
                _validate_name(name)
                index += 1
            paths.append(name)
            if name.endswith(".go") and header[4] != "D" and header[1] not in ("100644", "100755"):
                raise DiffUnavailable(f"Selected Go file {name!r} is a non-regular Git entry.")
            # Git renders a type change as deletion plus addition, but supplies
            # one raw entry. The second patch carries the surviving content.
            block_count = 2 if header[4] == "T" else 1
            if block_index + block_count > len(blocks):
>               raise DiffUnavailable("Git manifest and patch entries do not match.")
E               atom.diff.DiffUnavailable: Git manifest and patch entries do not match.

atom\_review_format.py:209: DiffUnavailable
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_submodule_display_config_cannot_change_manifest_patch_framing[log]
================= 1 failed, 1 passed, 57 deselected in 6.59s ==================
~~~~

GREEN:

~~~~text
python -m pytest tests\test_review_formatting.py tests\test_review_toolchain.py -q -k "submodule_display or blocks_before_models"
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 62 items / 59 deselected / 3 selected

tests\test_review_formatting.py ..                                       [ 66%]
tests\test_review_toolchain.py .                                         [100%]

====================== 3 passed, 59 deselected in 6.41s =======================
~~~~

### Source restrictions apply only to inputs that will be read

RED:

~~~~text
python -m pytest tests\test_review_formatting.py -q -k unread_manifest
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 65 items / 59 deselected / 6 selected

tests\test_review_formatting.py FFFFFF                                   [100%]

================================== FAILURES ===================================
_ test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[non-go-:] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-433/test_unread_manifest_paths_do_0')
model_prompts = []
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000028F75E81940>
character = ':', scope = 'non-go'

    @pytest.mark.parametrize("character", (":", "\\"))
    @pytest.mark.parametrize("scope", ("non-go", "deleted", "outside-module"))
    def test_unread_manifest_paths_do_not_apply_native_source_path_restrictions(
        repository: Path, model_prompts: list[str], monkeypatch, character, scope
    ):
        """Inject POSIX-valid names without creating Windows-invalid checkout paths."""
        directory = repository
        original_name = "changed.go"
        if scope == "outside-module":
            directory = repository / "service"
            directory.mkdir()
            (directory / "go.mod").write_bytes(b"module example.invalid/service\n\ngo 1.23\n")
            git(repository, "add", "--all")
            git(repository, "commit", "--quiet", "-m", "selected module")
        if scope == "deleted":
            git(repository, "rm", "--quiet", original_name)
        else:
            if scope == "non-go":
                original_name = "notes.txt"
            (repository / original_name).write_bytes(CLEAN.encode())
            git(repository, "add", original_name)
        name = "other/part" + character + "one" + (".txt" if scope == "non-go" else ".go")
        runner = ReviewRunner()
        original_run = runner.run
    
        def selected_name(command, working_directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, working_directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                metadata = metadata.replace("\0" + original_name, "\0" + name)
                result = replace(result, stdout=metadata + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", selected_name)
    
>       outcome = review(directory, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:740: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:120: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\_review_format.py:195: in capture_review_diff
    _validate_name(name)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'other/part:one.txt'

    def _validate_name(name: str) -> None:
        if (
            not name or "\\" in name or ":" in name
            or any(part in ("", ".", "..") for part in name.split("/"))
        ):
>           raise DiffUnavailable(f"Git provided an unsafe review path: {name!r}.")
E           atom.diff.DiffUnavailable: Git provided an unsafe review path: 'other/part:one.txt'.

atom\_review_format.py:145: DiffUnavailable
_ test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[non-go-\\] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-433/test_unread_manifest_paths_do_1')
model_prompts = []
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000028F75E816E0>
character = '\\', scope = 'non-go'

    @pytest.mark.parametrize("character", (":", "\\"))
    @pytest.mark.parametrize("scope", ("non-go", "deleted", "outside-module"))
    def test_unread_manifest_paths_do_not_apply_native_source_path_restrictions(
        repository: Path, model_prompts: list[str], monkeypatch, character, scope
    ):
        """Inject POSIX-valid names without creating Windows-invalid checkout paths."""
        directory = repository
        original_name = "changed.go"
        if scope == "outside-module":
            directory = repository / "service"
            directory.mkdir()
            (directory / "go.mod").write_bytes(b"module example.invalid/service\n\ngo 1.23\n")
            git(repository, "add", "--all")
            git(repository, "commit", "--quiet", "-m", "selected module")
        if scope == "deleted":
            git(repository, "rm", "--quiet", original_name)
        else:
            if scope == "non-go":
                original_name = "notes.txt"
            (repository / original_name).write_bytes(CLEAN.encode())
            git(repository, "add", original_name)
        name = "other/part" + character + "one" + (".txt" if scope == "non-go" else ".go")
        runner = ReviewRunner()
        original_run = runner.run
    
        def selected_name(command, working_directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, working_directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                metadata = metadata.replace("\0" + original_name, "\0" + name)
                result = replace(result, stdout=metadata + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", selected_name)
    
>       outcome = review(directory, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:740: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:120: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\_review_format.py:195: in capture_review_diff
    _validate_name(name)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'other/part\\one.txt'

    def _validate_name(name: str) -> None:
        if (
            not name or "\\" in name or ":" in name
            or any(part in ("", ".", "..") for part in name.split("/"))
        ):
>           raise DiffUnavailable(f"Git provided an unsafe review path: {name!r}.")
E           atom.diff.DiffUnavailable: Git provided an unsafe review path: 'other/part\\one.txt'.

atom\_review_format.py:145: DiffUnavailable
_ test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[deleted-:] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-433/test_unread_manifest_paths_do_2')
model_prompts = []
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000028F75DFD250>
character = ':', scope = 'deleted'

    @pytest.mark.parametrize("character", (":", "\\"))
    @pytest.mark.parametrize("scope", ("non-go", "deleted", "outside-module"))
    def test_unread_manifest_paths_do_not_apply_native_source_path_restrictions(
        repository: Path, model_prompts: list[str], monkeypatch, character, scope
    ):
        """Inject POSIX-valid names without creating Windows-invalid checkout paths."""
        directory = repository
        original_name = "changed.go"
        if scope == "outside-module":
            directory = repository / "service"
            directory.mkdir()
            (directory / "go.mod").write_bytes(b"module example.invalid/service\n\ngo 1.23\n")
            git(repository, "add", "--all")
            git(repository, "commit", "--quiet", "-m", "selected module")
        if scope == "deleted":
            git(repository, "rm", "--quiet", original_name)
        else:
            if scope == "non-go":
                original_name = "notes.txt"
            (repository / original_name).write_bytes(CLEAN.encode())
            git(repository, "add", original_name)
        name = "other/part" + character + "one" + (".txt" if scope == "non-go" else ".go")
        runner = ReviewRunner()
        original_run = runner.run
    
        def selected_name(command, working_directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, working_directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                metadata = metadata.replace("\0" + original_name, "\0" + name)
                result = replace(result, stdout=metadata + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", selected_name)
    
>       outcome = review(directory, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:740: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:120: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\_review_format.py:195: in capture_review_diff
    _validate_name(name)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'other/part:one.go'

    def _validate_name(name: str) -> None:
        if (
            not name or "\\" in name or ":" in name
            or any(part in ("", ".", "..") for part in name.split("/"))
        ):
>           raise DiffUnavailable(f"Git provided an unsafe review path: {name!r}.")
E           atom.diff.DiffUnavailable: Git provided an unsafe review path: 'other/part:one.go'.

atom\_review_format.py:145: DiffUnavailable
_ test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[deleted-\\] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-433/test_unread_manifest_paths_do_3')
model_prompts = []
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000028F75E1C5A0>
character = '\\', scope = 'deleted'

    @pytest.mark.parametrize("character", (":", "\\"))
    @pytest.mark.parametrize("scope", ("non-go", "deleted", "outside-module"))
    def test_unread_manifest_paths_do_not_apply_native_source_path_restrictions(
        repository: Path, model_prompts: list[str], monkeypatch, character, scope
    ):
        """Inject POSIX-valid names without creating Windows-invalid checkout paths."""
        directory = repository
        original_name = "changed.go"
        if scope == "outside-module":
            directory = repository / "service"
            directory.mkdir()
            (directory / "go.mod").write_bytes(b"module example.invalid/service\n\ngo 1.23\n")
            git(repository, "add", "--all")
            git(repository, "commit", "--quiet", "-m", "selected module")
        if scope == "deleted":
            git(repository, "rm", "--quiet", original_name)
        else:
            if scope == "non-go":
                original_name = "notes.txt"
            (repository / original_name).write_bytes(CLEAN.encode())
            git(repository, "add", original_name)
        name = "other/part" + character + "one" + (".txt" if scope == "non-go" else ".go")
        runner = ReviewRunner()
        original_run = runner.run
    
        def selected_name(command, working_directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, working_directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                metadata = metadata.replace("\0" + original_name, "\0" + name)
                result = replace(result, stdout=metadata + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", selected_name)
    
>       outcome = review(directory, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:740: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:120: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\_review_format.py:195: in capture_review_diff
    _validate_name(name)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'other/part\\one.go'

    def _validate_name(name: str) -> None:
        if (
            not name or "\\" in name or ":" in name
            or any(part in ("", ".", "..") for part in name.split("/"))
        ):
>           raise DiffUnavailable(f"Git provided an unsafe review path: {name!r}.")
E           atom.diff.DiffUnavailable: Git provided an unsafe review path: 'other/part\\one.go'.

atom\_review_format.py:145: DiffUnavailable
_ test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[outside-module-:] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-433/test_unread_manifest_paths_do_4')
model_prompts = []
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000028F75E1CD10>
character = ':', scope = 'outside-module'

    @pytest.mark.parametrize("character", (":", "\\"))
    @pytest.mark.parametrize("scope", ("non-go", "deleted", "outside-module"))
    def test_unread_manifest_paths_do_not_apply_native_source_path_restrictions(
        repository: Path, model_prompts: list[str], monkeypatch, character, scope
    ):
        """Inject POSIX-valid names without creating Windows-invalid checkout paths."""
        directory = repository
        original_name = "changed.go"
        if scope == "outside-module":
            directory = repository / "service"
            directory.mkdir()
            (directory / "go.mod").write_bytes(b"module example.invalid/service\n\ngo 1.23\n")
            git(repository, "add", "--all")
            git(repository, "commit", "--quiet", "-m", "selected module")
        if scope == "deleted":
            git(repository, "rm", "--quiet", original_name)
        else:
            if scope == "non-go":
                original_name = "notes.txt"
            (repository / original_name).write_bytes(CLEAN.encode())
            git(repository, "add", original_name)
        name = "other/part" + character + "one" + (".txt" if scope == "non-go" else ".go")
        runner = ReviewRunner()
        original_run = runner.run
    
        def selected_name(command, working_directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, working_directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                metadata = metadata.replace("\0" + original_name, "\0" + name)
                result = replace(result, stdout=metadata + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", selected_name)
    
>       outcome = review(directory, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:740: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:120: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\_review_format.py:195: in capture_review_diff
    _validate_name(name)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'other/part:one.go'

    def _validate_name(name: str) -> None:
        if (
            not name or "\\" in name or ":" in name
            or any(part in ("", ".", "..") for part in name.split("/"))
        ):
>           raise DiffUnavailable(f"Git provided an unsafe review path: {name!r}.")
E           atom.diff.DiffUnavailable: Git provided an unsafe review path: 'other/part:one.go'.

atom\_review_format.py:145: DiffUnavailable
_ test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[outside-module-\\] _

repository = WindowsPath('<home>/AppData/Local/Temp/pytest-of-gimotwan/pytest-433/test_unread_manifest_paths_do_5')
model_prompts = []
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000028F75E5B050>
character = '\\', scope = 'outside-module'

    @pytest.mark.parametrize("character", (":", "\\"))
    @pytest.mark.parametrize("scope", ("non-go", "deleted", "outside-module"))
    def test_unread_manifest_paths_do_not_apply_native_source_path_restrictions(
        repository: Path, model_prompts: list[str], monkeypatch, character, scope
    ):
        """Inject POSIX-valid names without creating Windows-invalid checkout paths."""
        directory = repository
        original_name = "changed.go"
        if scope == "outside-module":
            directory = repository / "service"
            directory.mkdir()
            (directory / "go.mod").write_bytes(b"module example.invalid/service\n\ngo 1.23\n")
            git(repository, "add", "--all")
            git(repository, "commit", "--quiet", "-m", "selected module")
        if scope == "deleted":
            git(repository, "rm", "--quiet", original_name)
        else:
            if scope == "non-go":
                original_name = "notes.txt"
            (repository / original_name).write_bytes(CLEAN.encode())
            git(repository, "add", original_name)
        name = "other/part" + character + "one" + (".txt" if scope == "non-go" else ".go")
        runner = ReviewRunner()
        original_run = runner.run
    
        def selected_name(command, working_directory, timeout_seconds=300, stdin_text=None):
            result = original_run(command, working_directory, timeout_seconds, stdin_text)
            if "--raw" in command:
                metadata, patch = result.stdout.split("\0\0", 1)
                metadata = metadata.replace("\0" + original_name, "\0" + name)
                result = replace(result, stdout=metadata + "\0\0" + patch)
            return result
    
        monkeypatch.setattr(runner, "run", selected_name)
    
>       outcome = review(directory, runner, DiffSource.STAGED)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_review_formatting.py:740: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_review_formatting.py:120: in review
    return run_review(
atom\review.py:276: in run_review
    diff, format_gate = capture_review_diff(request, runner, working_directory)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\_review_format.py:195: in capture_review_diff
    _validate_name(name)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'other/part\\one.go'

    def _validate_name(name: str) -> None:
        if (
            not name or "\\" in name or ":" in name
            or any(part in ("", ".", "..") for part in name.split("/"))
        ):
>           raise DiffUnavailable(f"Git provided an unsafe review path: {name!r}.")
E           atom.diff.DiffUnavailable: Git provided an unsafe review path: 'other/part\\one.go'.

atom\_review_format.py:145: DiffUnavailable
=========================== short test summary info ===========================
FAILED tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[non-go-:]
FAILED tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[non-go-\\]
FAILED tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[deleted-:]
FAILED tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[deleted-\\]
FAILED tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[outside-module-:]
FAILED tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[outside-module-\\]
====================== 6 failed, 59 deselected in 4.65s =======================
~~~~

GREEN:

~~~~text
python -m pytest tests\test_review_formatting.py -q
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <worktree>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 65 items

tests\test_review_formatting.py ........................................ [ 61%]
.........................                                                [100%]

============================= 65 passed in 40.13s =============================
~~~~
