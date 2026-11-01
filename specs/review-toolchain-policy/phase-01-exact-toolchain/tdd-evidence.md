---
project: "review-toolchain-policy"
phase: "phase-01-exact-toolchain"
date: "2026-10-31"
status: "local-gate-passed-ci-failing"
---

# Phase 01 TDD Evidence

Implemented the approved [design](design-spec.md); all twenty behaviors remain
mapped in the [test spec](test-spec.md). The [confirmed POC](../poc-report-local-executable.md)
is separate evidence, not production code or a replayed experiment.

## Current Result And Limits

The latest unchanged Windows full run passed: 1615 passed, 5 skipped in 176.32s,
95% coverage. Selection coverage is 99%; review orchestration is 100%.
An earlier full run failed the strict handle-count assertion (330 versus 328).
Its full failure and the isolated diagnostic pass remain below; the passing
rerun does not establish the cause or count as a cleanup fix.

CI run 41194476670 on source commit 2d42f6f passed both Linux CLI jobs, all three
existing POC jobs and documentation. Both macOS and both Windows CLI jobs failed.
See [current findings](../findings.md) for actual result lines and the run link.
This evidence does not claim a green cross-platform suite.

The native installed-distribution fixture exercises actual probes, build/vet/test,
runtime version, selected-root gofmt, minimum rejection and unchanged parent/
GOENV settings. It isolates its standard-library fixture settings; production
preserves caller settings. Successful native race/CGO and real dependency
compatibility remain unestablished. The five local skips are existing
Windows-inapplicable symlink and POSIX cleanup/interrupt cases.

## Evidence Selection And Provenance

The developer approved pruning superseded successful validation transcripts
and consolidating status notes. The two earlier successful full-suite captures
and old documentation capture are archived intact outside Git with this
complete pre-cleanup artifact; [publication evidence](../publication-evidence.md)
records their hashes and an immutable historical Git link.

All meaningful selection/native RED/GREEN captures, setup/selector errors, the
later root-regression/full-gate failure, isolated handle diagnosis and latest
complete passing full gate are retained below. Their fenced capture bytes are
unchanged; labels substitute local paths and captured trailing spaces remain.
No failed output, experiment driver, source, test or approved behavior was removed.

The key-lookup fixture correction, nonexistent selector and discipline-reread
deviations remain in [decisions](../decisions.md). Models saw the snapshot before
the later root guard/test, not that final amendment. No new model call, test run
or experiment occurred during this documentation-only cleanup.

## Selection, orchestration, CLI and evidence loop

```text
INITIAL RED: python -m pytest tests\test_go_selection.py -q --tb=short
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 0 items / 1 error

=================================== ERRORS ====================================
_________________ ERROR collecting tests/test_go_selection.py _________________
ImportError while importing test module '<FEATURE_WORKTREE>\tools\tests\test_go_selection.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\test_go_selection.py:8: in <module>
    from atom.go_selection import capture_go_toolchain_request
E   ModuleNotFoundError: No module named 'atom.go_selection'
=========================== short test summary info ===========================
ERROR tests/test_go_selection.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 1.08s ===============================
ASSERTION RED: capture_project_version
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests\test_go_selection.py F                                             [100%]

================================== FAILURES ===================================
________________________ test_capture_project_version _________________________
tests\test_go_selection.py:28: in test_capture_project_version
    assert request is not None, "configured exact version was not captured"
E   AssertionError: configured exact version was not captured
E   assert None is not None
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_capture_project_version - AssertionEr...
============================== 1 failed in 5.27s ==============================
GREEN: capture_project_version
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 1 item

tests\test_go_selection.py .                                             [100%]

============================== 1 passed in 4.49s ==============================
RED: invalid_project_version
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 15 items / 1 deselected / 14 selected

tests\test_go_selection.py FFFFFFFFFFFFFF                                [100%]

================================== FAILURES ===================================
_____________________ test_invalid_project_version[None] ______________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
_______________________ test_invalid_project_version[] ________________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
_____________________ test_invalid_project_version[1269] ______________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
_____________________ test_invalid_project_version[True] ______________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
___________________ test_invalid_project_version[version4] ____________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
___________________ test_invalid_project_version[version5] ____________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
___________________ test_invalid_project_version[go1.26.9] ____________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
_____________________ test_invalid_project_version[1.26] ______________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
____________________ test_invalid_project_version[1.026.9] ____________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
____________________ test_invalid_project_version[1.26.09] ____________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
____________________ test_invalid_project_version[1.20.9] _____________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
__________________ test_invalid_project_version[1.26.9+auto] __________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
____________________ test_invalid_project_version[1.26.9 ] ____________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
____________________ test_invalid_project_version[1.27rc1] ____________________
tests\test_go_selection.py:44: in test_invalid_project_version
    with pytest.raises(GoToolchainConfigError, match="review_go_version"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainConfigError
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_invalid_project_version[None] - Faile...
FAILED tests/test_go_selection.py::test_invalid_project_version[] - Failed: D...
FAILED tests/test_go_selection.py::test_invalid_project_version[1269] - Faile...
FAILED tests/test_go_selection.py::test_invalid_project_version[True] - Faile...
FAILED tests/test_go_selection.py::test_invalid_project_version[version4] - F...
FAILED tests/test_go_selection.py::test_invalid_project_version[version5] - F...
FAILED tests/test_go_selection.py::test_invalid_project_version[go1.26.9] - F...
FAILED tests/test_go_selection.py::test_invalid_project_version[1.26] - Faile...
FAILED tests/test_go_selection.py::test_invalid_project_version[1.026.9] - Fa...
FAILED tests/test_go_selection.py::test_invalid_project_version[1.26.09] - Fa...
FAILED tests/test_go_selection.py::test_invalid_project_version[1.20.9] - Fai...
FAILED tests/test_go_selection.py::test_invalid_project_version[1.26.9+auto]
FAILED tests/test_go_selection.py::test_invalid_project_version[1.26.9 ] - Fa...
FAILED tests/test_go_selection.py::test_invalid_project_version[1.27rc1] - Fa...
====================== 14 failed, 1 deselected in 0.63s =======================
GREEN: project version validation
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 15 items

tests\test_go_selection.py ...............                               [100%]

============================= 15 passed in 0.18s ==============================
RED: CLI exact override semantics
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 20 items / 15 deselected / 5 selected

tests\test_go_selection.py FFFFF                                         [100%]

================================== FAILURES ===================================
_______________ test_cli_override_records_project_version[True] _______________
tests\test_go_selection.py:54: in test_cli_override_records_project_version
    assert (request.version, request.source, request.project_version) == (
E   AssertionError: assert ('1.26.9', 'p...ct', '1.26.9') == ('1.27.0', 'cli', '1.26.9')
E     
E     At index 0 diff: '1.26.9' != '1.27.0'
E     Use -v to get more diff
______________ test_cli_override_records_project_version[False] _______________
tests\test_go_selection.py:53: in test_cli_override_records_project_version
    assert request is not None, "explicit version was ignored"
E   AssertionError: explicit version was ignored
E   assert None is not None
_____________ test_invalid_cli_override_is_not_ambient_fallback[] _____________
tests\test_go_selection.py:61: in test_invalid_cli_override_is_not_ambient_fallback
    with pytest.raises(ValueError, match="exact stable Go"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE ValueError
___________ test_invalid_cli_override_is_not_ambient_fallback[auto] ___________
tests\test_go_selection.py:61: in test_invalid_cli_override_is_not_ambient_fallback
    with pytest.raises(ValueError, match="exact stable Go"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE ValueError
_________ test_invalid_cli_override_is_not_ambient_fallback[go1.26.9] _________
tests\test_go_selection.py:61: in test_invalid_cli_override_is_not_ambient_fallback
    with pytest.raises(ValueError, match="exact stable Go"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE ValueError
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_cli_override_records_project_version[True]
FAILED tests/test_go_selection.py::test_cli_override_records_project_version[False]
FAILED tests/test_go_selection.py::test_invalid_cli_override_is_not_ambient_fallback[]
FAILED tests/test_go_selection.py::test_invalid_cli_override_is_not_ambient_fallback[auto]
FAILED tests/test_go_selection.py::test_invalid_cli_override_is_not_ambient_fallback[go1.26.9]
====================== 5 failed, 15 deselected in 0.17s =======================
GREEN: CLI precedence and exact validation
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 20 items

tests\test_go_selection.py ....................                          [100%]

============================= 20 passed in 0.19s ==============================
RED: config errors have wrong public category
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 26 items / 23 deselected / 3 selected

tests\test_go_selection.py FFF                                           [100%]

================================== FAILURES ===================================
_________________________ test_config_read_errors[{] __________________________
atom\storage.py:113: in read_json
    parsed = json.loads(raw_text)
             ^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\json\__init__.py:352: in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\json\decoder.py:345: in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\json\decoder.py:361: in raw_decode
    obj, end = self.scan_once(s, idx)
               ^^^^^^^^^^^^^^^^^^^^^^
E   json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)

The above exception was the direct cause of the following exception:
tests\test_go_selection.py:70: in test_config_read_errors
    capture_go_toolchain_request(tmp_path, version_override="1.27.0")
atom\go_selection.py:36: in capture_go_toolchain_request
    config = project.load_config() if project.config_path.exists() else {}
             ^^^^^^^^^^^^^^^^^^^^^
atom\state.py:257: in load_config
    return read_json(self.config_path, required_keys=("module_path",))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\storage.py:115: in read_json
    raise StateFileCorrupt(
E   atom.storage.StateFileCorrupt: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-556\test_config_read_errors___0\.atom\config.json is not valid JSON: Expecting property name enclosed in double quotes: line 1 column 2 (char 1).
E   It was probably damaged by a process that stopped mid-write.
E   If there is a `.unsaved` file beside it, that holds your last known state -- move it over this file.
E   Otherwise run `atom init --force` to start the project record again; your spikes and specs are not touched.

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:72: in test_config_read_errors
    assert isinstance(error, GoToolchainConfigError), (
E   AssertionError: config error escaped the policy boundary: StateFileCorrupt
E   assert False
E    +  where False = isinstance(StateFileCorrupt('<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-556\\test_config_read_errors__...is file.\nOtherwise run `atom init --force` to start the project record again; your spikes and specs are not touched.'), GoToolchainConfigError)
_________________________ test_config_read_errors[[]] _________________________
tests\test_go_selection.py:70: in test_config_read_errors
    capture_go_toolchain_request(tmp_path, version_override="1.27.0")
atom\go_selection.py:36: in capture_go_toolchain_request
    config = project.load_config() if project.config_path.exists() else {}
             ^^^^^^^^^^^^^^^^^^^^^
atom\state.py:257: in load_config
    return read_json(self.config_path, required_keys=("module_path",))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\storage.py:124: in read_json
    raise StateFileCorrupt(
E   atom.storage.StateFileCorrupt: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-556\test_config_read_errors____0\.atom\config.json does not contain Atom state: expected a JSON object, found a list.
E   If there is a `.unsaved` file beside it, that holds your last known state -- move it over this file.
E   Otherwise run `atom init --force` to start the project record again; your spikes and specs are not touched.

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:72: in test_config_read_errors
    assert isinstance(error, GoToolchainConfigError), (
E   AssertionError: config error escaped the policy boundary: StateFileCorrupt
E   assert False
E    +  where False = isinstance(StateFileCorrupt('<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-556\\test_config_read_errors__...is file.\nOtherwise run `atom init --force` to start the project record again; your spikes and specs are not touched.'), GoToolchainConfigError)
_________________________ test_config_read_errors[{}] _________________________
tests\test_go_selection.py:70: in test_config_read_errors
    capture_go_toolchain_request(tmp_path, version_override="1.27.0")
atom\go_selection.py:36: in capture_go_toolchain_request
    config = project.load_config() if project.config_path.exists() else {}
             ^^^^^^^^^^^^^^^^^^^^^
atom\state.py:257: in load_config
    return read_json(self.config_path, required_keys=("module_path",))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
atom\storage.py:132: in read_json
    raise StateFileCorrupt(
E   atom.storage.StateFileCorrupt: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-556\test_config_read_errors____1\.atom\config.json is missing required key: module_path.

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:72: in test_config_read_errors
    assert isinstance(error, GoToolchainConfigError), (
E   AssertionError: config error escaped the policy boundary: StateFileCorrupt
E   assert False
E    +  where False = isinstance(StateFileCorrupt('<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-556\\test_config_read_errors____1\\.atom\\config.json is missing required key: module_path.'), GoToolchainConfigError)
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_config_read_errors[{] - AssertionErro...
FAILED tests/test_go_selection.py::test_config_read_errors[[]] - AssertionErr...
FAILED tests/test_go_selection.py::test_config_read_errors[{}] - AssertionErr...
====================== 3 failed, 23 deselected in 0.24s =======================
GREEN: config read boundary
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 26 items / 2 deselected / 24 selected

tests\test_go_selection.py ........................                      [100%]

====================== 24 passed, 2 deselected in 0.23s =======================
RED: executable override is frozen and requires intent
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 26 items / 24 deselected / 2 selected

tests\test_go_selection.py FF                                            [100%]

================================== FAILURES ===================================
________________ test_request_freezes_relative_path_and_policy ________________
tests\test_go_selection.py:86: in test_request_freezes_relative_path_and_policy
    assert request.executable == (tmp_path / "sdk" / "bin" / "go.exe").resolve()
E   AssertionError: assert None == WindowsPath('<LOCAL_TEMP>/pytest-of-gimotwan/pytest-558/test_request_freezes_relative_0/sdk/bin/go.exe')
E    +  where None = GoToolchainRequest(version='1.26.9', source='project', project_version='1.26.9', executable=None).executable
E    +  and   WindowsPath('<LOCAL_TEMP>/pytest-of-gimotwan/pytest-558/test_request_freezes_relative_0/sdk/bin/go.exe') = resolve()
E    +    where resolve = (((WindowsPath('<LOCAL_TEMP>/pytest-of-gimotwan/pytest-558/test_request_freezes_relative_0') / 'sdk') / 'bin') / 'go.exe').resolve
______________________ test_executable_requires_version _______________________
tests\test_go_selection.py:91: in test_executable_requires_version
    with pytest.raises(ValueError, match="requires"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE ValueError
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_request_freezes_relative_path_and_policy
FAILED tests/test_go_selection.py::test_executable_requires_version - Failed:...
====================== 2 failed, 24 deselected in 0.19s =======================
GREEN: policy capture and frozen executable paths
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 26 items

tests\test_go_selection.py ..........................                    [100%]

============================= 26 passed in 0.21s ==============================
RED: verified direct distribution
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 27 items / 26 deselected / 1 selected

tests\test_go_selection.py F                                             [100%]

================================== FAILURES ===================================
__________________ test_resolve_verifies_actual_distribution __________________
tests\test_go_selection.py:144: in test_resolve_verifies_actual_distribution
    assert selected.status == "verified", "actual distribution was not verified"
E   AssertionError: actual distribution was not verified
E   assert 'not_run' == 'verified'
E     
E     - verified
E     + not_run
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_resolve_verifies_actual_distribution
====================== 1 failed, 26 deselected in 0.30s =======================
GREEN: direct installed distribution
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 27 items

tests\test_go_selection.py ...........................                   [100%]

============================= 27 passed in 0.22s ==============================
RED: invalid actual probes cannot verify
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 41 items / 27 deselected / 14 selected

tests\test_go_selection.py FFFFFFFFFFFFFF                                [100%]

================================== FAILURES ===================================
_______________ test_probe_failure_cannot_verify[wrong_version] _______________
tests\test_go_selection.py:205: in test_probe_failure_cannot_verify
    pytest.fail("invalid actual probe was accepted as exact selection")
E   Failed: invalid actual probe was accepted as exact selection
______________ test_probe_failure_cannot_verify[version_nonzero] ______________
tests\test_go_selection.py:205: in test_probe_failure_cannot_verify
    pytest.fail("invalid actual probe was accepted as exact selection")
E   Failed: invalid actual probe was accepted as exact selection
_____________ test_probe_failure_cannot_verify[version_timed_out] _____________
tests\test_go_selection.py:205: in test_probe_failure_cannot_verify
    pytest.fail("invalid actual probe was accepted as exact selection")
E   Failed: invalid actual probe was accepted as exact selection
______________ test_probe_failure_cannot_verify[version_missing] ______________
tests\test_go_selection.py:205: in test_probe_failure_cannot_verify
    pytest.fail("invalid actual probe was accepted as exact selection")
E   Failed: invalid actual probe was accepted as exact selection
___________ test_probe_failure_cannot_verify[version_runner_error] ____________
tests\test_go_selection.py:205: in test_probe_failure_cannot_verify
    pytest.fail("invalid actual probe was accepted as exact selection")
E   Failed: invalid actual probe was accepted as exact selection
________________ test_probe_failure_cannot_verify[env_nonzero] ________________
tests\test_go_selection.py:205: in test_probe_failure_cannot_verify
    pytest.fail("invalid actual probe was accepted as exact selection")
E   Failed: invalid actual probe was accepted as exact selection
_____________ test_probe_failure_cannot_verify[env_invalid_json] ______________
tests\test_go_selection.py:195: in test_probe_failure_cannot_verify
    resolve_go_toolchain(
atom\go_selection.py:70: in resolve_go_toolchain
    values = json.loads(actual.stdout)
             ^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\json\__init__.py:352: in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\json\decoder.py:345: in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\json\decoder.py:361: in raw_decode
    obj, end = self.scan_once(s, idx)
               ^^^^^^^^^^^^^^^^^^^^^^
E   json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:200: in test_probe_failure_cannot_verify
    assert isinstance(error, GoToolchainSelectionError), (
E   AssertionError: invalid probe escaped the selection boundary: JSONDecodeError
E   assert False
E    +  where False = isinstance(JSONDecodeError('Expecting property name enclosed in double quotes: line 1 column 2 (char 1)'), GoToolchainSelectionError)
_________________ test_probe_failure_cannot_verify[env_list] __________________
tests\test_go_selection.py:195: in test_probe_failure_cannot_verify
    resolve_go_toolchain(
atom\go_selection.py:72: in resolve_go_toolchain
    request, status="verified", observed_version=values["GOVERSION"].removeprefix("go"),
                                                 ^^^^^^^^^^^^^^^^^^^
E   TypeError: list indices must be integers or slices, not str

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:200: in test_probe_failure_cannot_verify
    assert isinstance(error, GoToolchainSelectionError), (
E   AssertionError: invalid probe escaped the selection boundary: TypeError
E   assert False
E    +  where False = isinstance(TypeError('list indices must be integers or slices, not str'), GoToolchainSelectionError)
_________________ test_probe_failure_cannot_verify[env_null] __________________
tests\test_go_selection.py:195: in test_probe_failure_cannot_verify
    resolve_go_toolchain(
atom\go_selection.py:72: in resolve_go_toolchain
    request, status="verified", observed_version=values["GOVERSION"].removeprefix("go"),
                                                 ^^^^^^^^^^^^^^^^^^^
E   TypeError: 'NoneType' object is not subscriptable

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:200: in test_probe_failure_cannot_verify
    assert isinstance(error, GoToolchainSelectionError), (
E   AssertionError: invalid probe escaped the selection boundary: TypeError
E   assert False
E    +  where False = isinstance(TypeError("'NoneType' object is not subscriptable"), GoToolchainSelectionError)
________________ test_probe_failure_cannot_verify[env_missing] ________________
tests\test_go_selection.py:195: in test_probe_failure_cannot_verify
    resolve_go_toolchain(
atom\go_selection.py:72: in resolve_go_toolchain
    request, status="verified", observed_version=values["GOVERSION"].removeprefix("go"),
                                                 ^^^^^^^^^^^^^^^^^^^
E   KeyError: 'GOVERSION'

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:200: in test_probe_failure_cannot_verify
    assert isinstance(error, GoToolchainSelectionError), (
E   AssertionError: invalid probe escaped the selection boundary: KeyError
E   assert False
E    +  where False = isinstance(KeyError('GOVERSION'), GoToolchainSelectionError)
_____________ test_probe_failure_cannot_verify[env_wrong_version] _____________
tests\test_go_selection.py:205: in test_probe_failure_cannot_verify
    pytest.fail("invalid actual probe was accepted as exact selection")
E   Failed: invalid actual probe was accepted as exact selection
______________ test_probe_failure_cannot_verify[env_wrong_root] _______________
tests\test_go_selection.py:205: in test_probe_failure_cannot_verify
    pytest.fail("invalid actual probe was accepted as exact selection")
E   Failed: invalid actual probe was accepted as exact selection
______________ test_probe_failure_cannot_verify[env_wrong_mode] _______________
tests\test_go_selection.py:205: in test_probe_failure_cannot_verify
    pytest.fail("invalid actual probe was accepted as exact selection")
E   Failed: invalid actual probe was accepted as exact selection
______________ test_probe_failure_cannot_verify[env_wrong_type] _______________
tests\test_go_selection.py:195: in test_probe_failure_cannot_verify
    resolve_go_toolchain(
atom\go_selection.py:73: in resolve_go_toolchain
    executable=binary, goroot=Path(values["GOROOT"]).resolve(),
                              ^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:503: in __init__
    super().__init__(*args)
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:132: in __init__
    raise TypeError(
E   TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'list'

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:200: in test_probe_failure_cannot_verify
    assert isinstance(error, GoToolchainSelectionError), (
E   AssertionError: invalid probe escaped the selection boundary: TypeError
E   assert False
E    +  where False = isinstance(TypeError("argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'list'"), GoToolchainSelectionError)
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[wrong_version]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[version_nonzero]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[version_timed_out]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[version_missing]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[version_runner_error]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[env_nonzero]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[env_invalid_json]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[env_list]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[env_null]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[env_missing]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_version]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_root]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_mode]
FAILED tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_type]
====================== 14 failed, 27 deselected in 0.42s ======================
GREEN: probe validation and fail-closed provenance
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 41 items

tests\test_go_selection.py .........................................     [100%]

============================= 41 passed in 0.32s ==============================
RED: explicit distribution layout and formatter checks
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 46 items / 41 deselected / 5 selected

tests\test_go_selection.py FFFFF                                         [100%]

================================== FAILURES ===================================
__________ test_explicit_candidate_never_falls_back[missing_binary] ___________
tests\test_go_selection.py:229: in test_explicit_candidate_never_falls_back
    resolve_go_toolchain(
atom\go_selection.py:77: in resolve_go_toolchain
    initial_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
                                  ^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_abc.py:625: in read_bytes
    with self.open(mode='rb') as f:
         ^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:537: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-564\\test_explicit_candidate_never_0\\installed\\bin\\go.exe'

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:234: in test_explicit_candidate_never_falls_back
    assert isinstance(error, GoToolchainSelectionError), (
E   AssertionError: candidate failure escaped the selection boundary: FileNotFoundError
E   assert False
E    +  where False = isinstance(FileNotFoundError(2, 'No such file or directory'), GoToolchainSelectionError)
__________ test_explicit_candidate_never_falls_back[missing_version] __________
tests\test_go_selection.py:239: in test_explicit_candidate_never_falls_back
    pytest.fail("incomplete or wrong explicit distribution was accepted")
E   Failed: incomplete or wrong explicit distribution was accepted
__________ test_explicit_candidate_never_falls_back[wrong_metadata] ___________
tests\test_go_selection.py:239: in test_explicit_candidate_never_falls_back
    pytest.fail("incomplete or wrong explicit distribution was accepted")
E   Failed: incomplete or wrong explicit distribution was accepted
______________ test_explicit_candidate_never_falls_back[wrapper] ______________
tests\test_go_selection.py:239: in test_explicit_candidate_never_falls_back
    pytest.fail("incomplete or wrong explicit distribution was accepted")
E   Failed: incomplete or wrong explicit distribution was accepted
_________ test_explicit_candidate_never_falls_back[missing_formatter] _________
tests\test_go_selection.py:239: in test_explicit_candidate_never_falls_back
    pytest.fail("incomplete or wrong explicit distribution was accepted")
E   Failed: incomplete or wrong explicit distribution was accepted
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_binary]
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_version]
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[wrong_metadata]
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[wrapper]
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_formatter]
====================== 5 failed, 41 deselected in 0.26s =======================
GREEN: explicit complete distributions only
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 46 items

tests\test_go_selection.py ............................................. [ 97%]
.                                                                        [100%]

============================= 46 passed in 0.42s ==============================
RED: bounded automatic local discovery
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 53 items / 46 deselected / 7 selected

tests\test_go_selection.py FFFFFFF                                       [100%]

================================== FAILURES ===================================
_____________________ test_bounded_discovery_order[path] ______________________
tests\test_go_selection.py:273: in test_bounded_discovery_order
    assert selected.status == "verified", "bounded installed distribution was not found"
E   AssertionError: bounded installed distribution was not found
E   assert 'not_run' == 'verified'
E     
E     - verified
E     + not_run
____________________ test_bounded_discovery_order[goroot] _____________________
tests\test_go_selection.py:273: in test_bounded_discovery_order
    assert selected.status == "verified", "bounded installed distribution was not found"
E   AssertionError: bounded installed distribution was not found
E   assert 'not_run' == 'verified'
E     
E     - verified
E     + not_run
______________________ test_bounded_discovery_order[sdk] ______________________
tests\test_go_selection.py:273: in test_bounded_discovery_order
    assert selected.status == "verified", "bounded installed distribution was not found"
E   AssertionError: bounded installed distribution was not found
E   assert 'not_run' == 'verified'
E     
E     - verified
E     + not_run
_________________ test_bounded_discovery_order[module_cache] __________________
tests\test_go_selection.py:273: in test_bounded_discovery_order
    assert selected.status == "verified", "bounded installed distribution was not found"
E   AssertionError: bounded installed distribution was not found
E   assert 'not_run' == 'verified'
E     
E     - verified
E     + not_run
____________________ test_bounded_discovery_order[gopath] _____________________
tests\test_go_selection.py:273: in test_bounded_discovery_order
    assert selected.status == "verified", "bounded installed distribution was not found"
E   AssertionError: bounded installed distribution was not found
E   assert 'not_run' == 'verified'
E     
E     - verified
E     + not_run
_________________ test_bounded_discovery_order[default_cache] _________________
tests\test_go_selection.py:273: in test_bounded_discovery_order
    assert selected.status == "verified", "bounded installed distribution was not found"
E   AssertionError: bounded installed distribution was not found
E   assert 'not_run' == 'verified'
E     
E     - verified
E     + not_run
_______________ test_discovery_unavailable_does_not_use_ambient _______________
tests\test_go_selection.py:284: in test_discovery_unavailable_does_not_use_ambient
    with pytest.raises(GoToolchainSelectionError, match="--go-executable") as raised:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE GoToolchainSelectionError
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_bounded_discovery_order[path] - Asser...
FAILED tests/test_go_selection.py::test_bounded_discovery_order[goroot] - Ass...
FAILED tests/test_go_selection.py::test_bounded_discovery_order[sdk] - Assert...
FAILED tests/test_go_selection.py::test_bounded_discovery_order[module_cache]
FAILED tests/test_go_selection.py::test_bounded_discovery_order[gopath] - Ass...
FAILED tests/test_go_selection.py::test_bounded_discovery_order[default_cache]
FAILED tests/test_go_selection.py::test_discovery_unavailable_does_not_use_ambient
====================== 7 failed, 46 deselected in 0.27s =======================
GREEN: bounded common-location discovery
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 53 items

tests\test_go_selection.py ............................................. [ 84%]
........                                                                 [100%]

============================= 53 passed in 0.62s ==============================
RED: Windows case-insensitive child environment
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 54 items / 53 deselected / 1 selected

tests\test_go_selection.py F                                             [100%]

================================== FAILURES ===================================
____________ test_selected_environment_preserves_project_settings _____________
tests\test_go_selection.py:310: in test_selected_environment_preserves_project_settings
    assert not any(key.casefold() == "goroot" for key in child)
E   assert not True
E    +  where True = any(<generator object test_selected_environment_preserves_project_settings.<locals>.<genexpr> at 0x00000296F21EDA40>)
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_selected_environment_preserves_project_settings
====================== 1 failed, 53 deselected in 0.21s =======================
GREEN: isolated case-safe selection controls
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 54 items

tests\test_go_selection.py ............................................. [ 83%]
.........                                                                [100%]

============================= 54 passed in 0.50s ==============================
RED: review actually applies selected gates
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 5 items / 4 deselected / 1 selected

tests\test_review_toolchain.py F                                         [100%]

================================== FAILURES ===================================
___________________ test_pinned_review_uses_selected_gates ____________________
tests\test_review_toolchain.py:169: in test_pinned_review_uses_selected_gates
    assert selection is not None, "review ignored its exact toolchain request"
E   AssertionError: review ignored its exact toolchain request
E   assert None is not None
=========================== short test summary info ===========================
FAILED tests/test_review_toolchain.py::test_pinned_review_uses_selected_gates
======================= 1 failed, 4 deselected in 0.56s =======================
GREEN: selected review gate integration
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 125 items

tests\test_go_selection.py ............................................. [ 36%]
.........                                                                [ 43%]
tests\test_review_toolchain.py .....                                     [ 47%]
tests\test_review_formatting.py ........................................ [ 79%]
..........................                                               [100%]

============================ 125 passed in 44.35s =============================
RED: pinned wrappers refused before Go probes
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 7 items / 5 deselected / 2 selected

tests\test_review_toolchain.py FF                                        [100%]

================================== FAILURES ===================================
_______________ test_pinned_makefile_stops_before_probes[build] _______________
tests\test_review_toolchain.py:186: in test_pinned_makefile_stops_before_probes
    run_review(
atom\review.py:320: in run_review
    raise ToolchainGateFailed(toolchain.blocking_failures)
E   atom.review.ToolchainGateFailed: Required toolchain gates failed: build

During handling of the above exception, another exception occurred:
tests\test_review_toolchain.py:191: in test_pinned_makefile_stops_before_probes
    assert isinstance(error, GoToolchainSelectionError), "wrapper failure was misclassified"
E   AssertionError: wrapper failure was misclassified
E   assert False
E    +  where False = isinstance(ToolchainGateFailed('Required toolchain gates failed: build'), GoToolchainSelectionError)
_______________ test_pinned_makefile_stops_before_probes[test] ________________
tests\test_review_toolchain.py:186: in test_pinned_makefile_stops_before_probes
    run_review(
atom\review.py:320: in run_review
    raise ToolchainGateFailed(toolchain.blocking_failures)
E   atom.review.ToolchainGateFailed: Required toolchain gates failed: test

During handling of the above exception, another exception occurred:
tests\test_review_toolchain.py:191: in test_pinned_makefile_stops_before_probes
    assert isinstance(error, GoToolchainSelectionError), "wrapper failure was misclassified"
E   AssertionError: wrapper failure was misclassified
E   assert False
E    +  where False = isinstance(ToolchainGateFailed('Required toolchain gates failed: test'), GoToolchainSelectionError)
=========================== short test summary info ===========================
FAILED tests/test_review_toolchain.py::test_pinned_makefile_stops_before_probes[build]
FAILED tests/test_review_toolchain.py::test_pinned_makefile_stops_before_probes[test]
======================= 2 failed, 5 deselected in 0.33s =======================
GREEN: pinned Makefile preflight
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 61 items

tests\test_go_selection.py ............................................. [ 73%]
.........                                                                [ 88%]
tests\test_review_toolchain.py .......                                   [100%]

============================= 61 passed in 0.60s ==============================
RED: late Makefile delegation is rejected by selected adapter
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 8 items / 7 deselected / 1 selected

tests\test_review_toolchain.py F                                         [100%]

================================== FAILURES ===================================
_________ test_pinned_runner_refuses_delegation_added_after_preflight _________
tests\test_review_toolchain.py:212: in test_pinned_runner_refuses_delegation_added_after_preflight
    run_review(
atom\review.py:334: in run_review
    raise ToolchainGateFailed(toolchain.blocking_failures)
E   atom.review.ToolchainGateFailed: Required toolchain gates failed: build

During handling of the above exception, another exception occurred:
tests\test_review_toolchain.py:217: in test_pinned_runner_refuses_delegation_added_after_preflight
    assert isinstance(error, GoToolchainSelectionError), "late delegation escaped the adapter"
E   AssertionError: late delegation escaped the adapter
E   assert False
E    +  where False = isinstance(ToolchainGateFailed('Required toolchain gates failed: build'), GoToolchainSelectionError)
=========================== short test summary info ===========================
FAILED tests/test_review_toolchain.py::test_pinned_runner_refuses_delegation_added_after_preflight
======================= 1 failed, 7 deselected in 1.45s =======================
GREEN: selected adapter refuses late delegation
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 8 items

tests\test_review_toolchain.py ........                                  [100%]

============================== 8 passed in 0.18s ==============================
RED: non-executed pin remains intent, not observed Go
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 10 items / 8 deselected / 2 selected

tests\test_review_toolchain.py FF                                        [100%]

================================== FAILURES ===================================
__ test_unexecuted_pin_retains_intent_without_observations[configured-skip] ___
tests\test_review_toolchain.py:237: in test_unexecuted_pin_retains_intent_without_observations
    assert selection is not None, "unexecuted pin disappeared"
E   AssertionError: unexecuted pin disappeared
E   assert None is not None
_____ test_unexecuted_pin_retains_intent_without_observations[no-module] ______
tests\test_review_toolchain.py:237: in test_unexecuted_pin_retains_intent_without_observations
    assert selection is not None, "unexecuted pin disappeared"
E   AssertionError: unexecuted pin disappeared
E   assert None is not None
=========================== short test summary info ===========================
FAILED tests/test_review_toolchain.py::test_unexecuted_pin_retains_intent_without_observations[configured-skip]
FAILED tests/test_review_toolchain.py::test_unexecuted_pin_retains_intent_without_observations[no-module]
======================= 2 failed, 8 deselected in 0.29s =======================
GREEN: unexecuted pin records not_run without probes
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 10 items

tests\test_review_toolchain.py ..........                                [100%]

============================= 10 passed in 0.18s ==============================
RED: failed required gates retain selected Go provenance
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 15 items / 10 deselected / 5 selected

tests\test_review_toolchain.py FFFFF                                     [100%]

================================== FAILURES ===================================
_ test_pinned_gate_failure_retains_selection_and_blocks_models[arguments0-CommandOutcome.COMPLETED-1-go.mod requires go >= 1.27.0] _
tests\test_review_toolchain.py:268: in test_pinned_gate_failure_retains_selection_and_blocks_models
    assert getattr(raised.value, "selection", None) is not None, "failed gate lost its version context"
E   AssertionError: failed gate lost its version context
E   assert None is not None
E    +  where None = getattr(ToolchainGateFailed('Required toolchain gates failed: build'), 'selection', None)
E    +    where ToolchainGateFailed('Required toolchain gates failed: build') = <ExceptionInfo ToolchainGateFailed('Required toolchain gates failed: build') tblen=2>.value
_ test_pinned_gate_failure_retains_selection_and_blocks_models[arguments1-CommandOutcome.COMPLETED-1-undefined: missingSymbol] _
tests\test_review_toolchain.py:268: in test_pinned_gate_failure_retains_selection_and_blocks_models
    assert getattr(raised.value, "selection", None) is not None, "failed gate lost its version context"
E   AssertionError: failed gate lost its version context
E   assert None is not None
E    +  where None = getattr(ToolchainGateFailed('Required toolchain gates failed: build'), 'selection', None)
E    +    where ToolchainGateFailed('Required toolchain gates failed: build') = <ExceptionInfo ToolchainGateFailed('Required toolchain gates failed: build') tblen=2>.value
_ test_pinned_gate_failure_retains_selection_and_blocks_models[arguments2-CommandOutcome.COMPLETED-1-WARNING: DATA RACE] _
tests\test_review_toolchain.py:268: in test_pinned_gate_failure_retains_selection_and_blocks_models
    assert getattr(raised.value, "selection", None) is not None, "failed gate lost its version context"
E   AssertionError: failed gate lost its version context
E   assert None is not None
E    +  where None = getattr(ToolchainGateFailed('Required toolchain gates failed: race'), 'selection', None)
E    +    where ToolchainGateFailed('Required toolchain gates failed: race') = <ExceptionInfo ToolchainGateFailed('Required toolchain gates failed: race') tblen=2>.value
_ test_pinned_gate_failure_retains_selection_and_blocks_models[arguments3-CommandOutcome.TOOL_MISSING-None-required tool is missing] _
tests\test_review_toolchain.py:268: in test_pinned_gate_failure_retains_selection_and_blocks_models
    assert getattr(raised.value, "selection", None) is not None, "failed gate lost its version context"
E   AssertionError: failed gate lost its version context
E   assert None is not None
E    +  where None = getattr(ToolchainGateFailed('Required toolchain gates failed: test'), 'selection', None)
E    +    where ToolchainGateFailed('Required toolchain gates failed: test') = <ExceptionInfo ToolchainGateFailed('Required toolchain gates failed: test') tblen=2>.value
_ test_pinned_gate_failure_retains_selection_and_blocks_models[arguments4-CommandOutcome.COMPLETED-2-unknown compiler problem] _
tests\test_review_toolchain.py:268: in test_pinned_gate_failure_retains_selection_and_blocks_models
    assert getattr(raised.value, "selection", None) is not None, "failed gate lost its version context"
E   AssertionError: failed gate lost its version context
E   assert None is not None
E    +  where None = getattr(ToolchainGateFailed('Required toolchain gates failed: build'), 'selection', None)
E    +    where ToolchainGateFailed('Required toolchain gates failed: build') = <ExceptionInfo ToolchainGateFailed('Required toolchain gates failed: build') tblen=2>.value
=========================== short test summary info ===========================
FAILED tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments0-CommandOutcome.COMPLETED-1-go.mod requires go >= 1.27.0]
FAILED tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments1-CommandOutcome.COMPLETED-1-undefined: missingSymbol]
FAILED tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments2-CommandOutcome.COMPLETED-1-WARNING: DATA RACE]
FAILED tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments3-CommandOutcome.TOOL_MISSING-None-required tool is missing]
FAILED tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments4-CommandOutcome.COMPLETED-2-unknown compiler problem]
====================== 5 failed, 10 deselected in 0.28s =======================
GREEN: selected required failures remain blocking with provenance
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 15 items

tests\test_review_toolchain.py ...............                           [100%]

============================= 15 passed in 0.24s ==============================
RED: executable replacement or deletion blocks model calls
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 19 items / 15 deselected / 4 selected

tests\test_review_toolchain.py FFFF                                      [100%]

================================== FAILURES ===================================
__________ test_changed_selected_identity_blocks_models[replaced-go] __________
tests\test_review_toolchain.py:304: in test_changed_selected_identity_blocks_models
    pytest.fail("changed selected identity reached models")
E   Failed: changed selected identity reached models
________ test_changed_selected_identity_blocks_models[replaced-gofmt] _________
tests\test_review_toolchain.py:304: in test_changed_selected_identity_blocks_models
    pytest.fail("changed selected identity reached models")
E   Failed: changed selected identity reached models
__________ test_changed_selected_identity_blocks_models[deleted-go] ___________
tests\test_review_toolchain.py:293: in test_changed_selected_identity_blocks_models
    run_review(
atom\review.py:336: in run_review
    toolchain = replace(toolchain, selection=selected_runner.finish())
                                             ^^^^^^^^^^^^^^^^^^^^^^^^
atom\go_selection.py:119: in finish
    executable_sha256_after=hashlib.sha256(self.binary.read_bytes()).hexdigest(),
                                           ^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_abc.py:625: in read_bytes
    with self.open(mode='rb') as f:
         ^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:537: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-580\\test_changed_selected_identity2\\installed\\bin\\go.exe'

During handling of the above exception, another exception occurred:
tests\test_review_toolchain.py:298: in test_changed_selected_identity_blocks_models
    assert isinstance(error, GoToolchainSelectionError), "identity failure escaped its category"
E   AssertionError: identity failure escaped its category
E   assert False
E    +  where False = isinstance(FileNotFoundError(2, 'No such file or directory'), GoToolchainSelectionError)
_________ test_changed_selected_identity_blocks_models[deleted-gofmt] _________
tests\test_review_toolchain.py:293: in test_changed_selected_identity_blocks_models
    run_review(
atom\review.py:336: in run_review
    toolchain = replace(toolchain, selection=selected_runner.finish())
                                             ^^^^^^^^^^^^^^^^^^^^^^^^
atom\go_selection.py:120: in finish
    gofmt_sha256_after=hashlib.sha256(self.formatter.read_bytes()).hexdigest(),
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_abc.py:625: in read_bytes
    with self.open(mode='rb') as f:
         ^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:537: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-580\\test_changed_selected_identity3\\installed\\bin\\gofmt.exe'

During handling of the above exception, another exception occurred:
tests\test_review_toolchain.py:298: in test_changed_selected_identity_blocks_models
    assert isinstance(error, GoToolchainSelectionError), "identity failure escaped its category"
E   AssertionError: identity failure escaped its category
E   assert False
E    +  where False = isinstance(FileNotFoundError(2, 'No such file or directory'), GoToolchainSelectionError)
=========================== short test summary info ===========================
FAILED tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[replaced-go]
FAILED tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[replaced-gofmt]
FAILED tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[deleted-go]
FAILED tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[deleted-gofmt]
====================== 4 failed, 15 deselected in 0.36s =======================
GREEN: selected executable identities rechecked before models
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 73 items

tests\test_go_selection.py ............................................. [ 61%]
.........                                                                [ 73%]
tests\test_review_toolchain.py ...................                       [100%]

============================= 73 passed in 0.77s ==============================
RED: consistent optional selection evidence across outputs
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 21 items / 19 deselected / 2 selected

tests\test_review_toolchain.py FF                                        [100%]

================================== FAILURES ===================================
__________ test_pinned_evidence_is_consistent_across_outputs[False] ___________
tests\test_review_toolchain.py:322: in test_pinned_evidence_is_consistent_across_outputs
    assert "selection" in payload["toolchain"], "report omitted requested selection"
E   AssertionError: report omitted requested selection
E   assert 'selection' in {'gates': [{'details': 'ok example.com/fixture 0.1s\n', 'duration_seconds': 0.25, 'name': 'build', 'required': True, ....k', 'duration_seconds': 0.25, 'name': 'staticcheck', 'required': False, ...}, ...], 'skip_reason': '', 'was_run': True}
___________ test_pinned_evidence_is_consistent_across_outputs[True] ___________
tests\test_review_toolchain.py:322: in test_pinned_evidence_is_consistent_across_outputs
    assert "selection" in payload["toolchain"], "report omitted requested selection"
E   AssertionError: report omitted requested selection
E   assert 'selection' in {'gates': [], 'skip_reason': 'toolchain checks were skipped by request', 'was_run': False}
=========================== short test summary info ===========================
FAILED tests/test_review_toolchain.py::test_pinned_evidence_is_consistent_across_outputs[False]
FAILED tests/test_review_toolchain.py::test_pinned_evidence_is_consistent_across_outputs[True]
====================== 2 failed, 19 deselected in 0.26s =======================
GREEN: selection evidence in prompt Markdown and additive schema-2 JSON
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
ERROR: file or directory not found: tests\test_report_review.py
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 0 items

============================ no tests ran in 0.03s ============================

GREEN retry: corrected existing report test selector; prior command collected nothing
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 43 items

tests\test_review_toolchain.py .....................                     [ 48%]
tests\test_toolchain.py ...                                              [ 55%]
tests\test_report.py ...................                                 [100%]

============================= 43 passed in 0.42s ==============================
RED: CLI captures configured launch policy
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 55 items / 54 deselected / 1 selected

tests\test_cli_review.py F                                               [100%]

================================== FAILURES ===================================
______________ test_review_cli_captures_project_toolchain_policy ______________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:119: in test_review_cli_captures_project_toolchain_policy
    assert "selection" in payload["toolchain"], "CLI did not capture launch policy"
E   AssertionError: CLI did not capture launch policy
E   assert 'selection' in {'gates': [], 'skip_reason': 'toolchain checks were skipped by request', 'was_run': False}
=========================== short test summary info ===========================
FAILED tests/test_cli_review.py::test_review_cli_captures_project_toolchain_policy
====================== 1 failed, 54 deselected in 0.37s =======================
GREEN: CLI captures project policy without changing ambient calls
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 55 items

tests\test_cli_review.py ............................................... [ 85%]
........                                                                 [100%]

============================= 55 passed in 2.87s ==============================
API scaffold needed: exact toolchain flags are not yet parsed
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 57 items / 55 deselected / 2 selected

tests\test_cli_review.py FF                                              [100%]

================================== FAILURES ===================================
___________ test_review_cli_version_and_executable_override[False] ____________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:143: in test_review_cli_version_and_executable_override
    assert review(
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:110: in review
    return main(["review", *args])
           ^^^^^^^^^^^^^^^^^^^^^^^
<FEATURE_WORKTREE>\tools\atom\cli.py:81: in main
    arguments = parser.parse_args(argv)
                ^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\argparse.py:1930: in parse_args
    self.error(msg)
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\argparse.py:2686: in error
    self.exit(2, _('%(prog)s: error: %(message)s\n') % args)
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\argparse.py:2673: in exit
    _sys.exit(status)
E   SystemExit: 2
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: unrecognized arguments: --go-version 1.25.0 --go-executable sdk\bin\go
____________ test_review_cli_version_and_executable_override[True] ____________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:143: in test_review_cli_version_and_executable_override
    assert review(
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:110: in review
    return main(["review", *args])
           ^^^^^^^^^^^^^^^^^^^^^^^
<FEATURE_WORKTREE>\tools\atom\cli.py:81: in main
    arguments = parser.parse_args(argv)
                ^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\argparse.py:1930: in parse_args
    self.error(msg)
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\argparse.py:2686: in error
    self.exit(2, _('%(prog)s: error: %(message)s\n') % args)
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\argparse.py:2673: in exit
    _sys.exit(status)
E   SystemExit: 2
---------------------------- Captured stderr call -----------------------------
usage: atom [-h] {check,poc,init,status,review,ship,setup-path} ...
atom: error: unrecognized arguments: --go-version 1.25.0 --go-executable sdk\bin\go
=========================== short test summary info ===========================
FAILED tests/test_cli_review.py::test_review_cli_version_and_executable_override[False]
FAILED tests/test_cli_review.py::test_review_cli_version_and_executable_override[True]
====================== 2 failed, 55 deselected in 0.40s =======================
RED: parsed exact-Go overrides must win and freeze executable paths
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 57 items / 55 deselected / 2 selected

tests\test_cli_review.py FF                                              [100%]

================================== FAILURES ===================================
___________ test_review_cli_version_and_executable_override[False] ____________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:147: in test_review_cli_version_and_executable_override
    assert captured[0] is not None, "explicit toolchain request was ignored"
E   AssertionError: explicit toolchain request was ignored
E   assert None is not None
---------------------------- Captured stdout call -----------------------------
{
  "diff": {
    "changed_lines": 3,
    "files": [
      "store/cache.go"
    ],
    "source": "working"
  },
  "findings": [
    {
      "agreement": [
        {
          "model": "gemini-3.8-flash",
          "runs_reporting": 1,
          "runs_total": 1
        },
        {
          "model": "gpt-5.4",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "store/cache.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "high",
      "is_corroborated": true,
      "line": 41,
      "lines": [
        41
      ],
      "messages": [
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gemini-3.8-flash",
          "run_index": 1,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gpt-5.4",
          "run_index": 1,
          "severity": "high"
        }
      ],
      "severities": [
        "high"
      ]
    }
  ],
  "has_no_usable_response": false,
  "is_partial": false,
  "models": [
    {
      "model": "gpt-5.4",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    },
    {
      "model": "gemini-3.8-flash",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    }
  ],
  "module_rules": {
    "provenance": "local-launch",
    "sources": [],
    "status": "not-found"
  },
  "schema_version": 2,
  "silent_runs": [],
  "toolchain": {
    "gates": [],
    "skip_reason": "No go.mod found in <LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-587\\test_review_cli_version_and_ex0",
    "was_run": false
  },
  "unavailable_models": [],
  "unparsed_responses": []
}
____________ test_review_cli_version_and_executable_override[True] ____________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:148: in test_review_cli_version_and_executable_override
    assert captured[0].version == "1.25.0"
E   AssertionError: assert '1.26.9' == '1.25.0'
E     
E     - 1.25.0
E     + 1.26.9
---------------------------- Captured stdout call -----------------------------
{
  "diff": {
    "changed_lines": 3,
    "files": [
      "store/cache.go"
    ],
    "source": "working"
  },
  "findings": [
    {
      "agreement": [
        {
          "model": "gemini-3.8-flash",
          "runs_reporting": 1,
          "runs_total": 1
        },
        {
          "model": "gpt-5.4",
          "runs_reporting": 1,
          "runs_total": 1
        }
      ],
      "file": "store/cache.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "high",
      "is_corroborated": true,
      "line": 41,
      "lines": [
        41
      ],
      "messages": [
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gemini-3.8-flash",
          "run_index": 1,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gpt-5.4",
          "run_index": 1,
          "severity": "high"
        }
      ],
      "severities": [
        "high"
      ]
    }
  ],
  "has_no_usable_response": false,
  "is_partial": false,
  "models": [
    {
      "model": "gpt-5.4",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    },
    {
      "model": "gemini-3.8-flash",
      "runs_answered": 1,
      "runs_completed": 1,
      "runs_requested": 1
    }
  ],
  "module_rules": {
    "provenance": "local-launch",
    "sources": [],
    "status": "not-found"
  },
  "schema_version": 2,
  "silent_runs": [],
  "toolchain": {
    "gates": [],
    "selection": {
      "commands": [],
      "discovery_diagnostics": [],
      "executable": null,
      "executable_sha256": null,
      "executable_sha256_after": null,
      "gofmt_executable": null,
      "gofmt_sha256": null,
      "gofmt_sha256_after": null,
      "goroot": null,
      "observed_version": null,
      "probes": [],
      "project_version": "1.26.9",
      "reason": "No go.mod found in <LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-587\\test_review_cli_version_and_ex1",
      "request_source": "project",
      "requested_version": "1.26.9",
      "selection_source": null,
      "status": "not_run"
    },
    "skip_reason": "No go.mod found in <LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-587\\test_review_cli_version_and_ex1",
    "was_run": false
  },
  "unavailable_models": [],
  "unparsed_responses": []
}
=========================== short test summary info ===========================
FAILED tests/test_cli_review.py::test_review_cli_version_and_executable_override[False]
FAILED tests/test_cli_review.py::test_review_cli_version_and_executable_override[True]
====================== 2 failed, 55 deselected in 0.25s =======================
GREEN: explicit Go flags override policy and freeze paths
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 57 items / 54 deselected / 3 selected

tests\test_cli_review.py ...                                             [100%]

====================== 3 passed, 54 deselected in 0.18s =======================
RED: explicit Go flags conflict with skipping checks
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 59 items / 57 deselected / 2 selected

tests\test_cli_review.py FF                                              [100%]

================================== FAILURES ===================================
_______ test_explicit_go_options_conflict_with_skip_toolchain[option0] ________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:163: in test_explicit_go_options_conflict_with_skip_toolchain
    assert review("--working", "--skip-toolchain", *option, "--json") == EXIT_USAGE_ERROR
E   AssertionError: assert 0 == 2
E    +  where 0 = review('--working', '--skip-toolchain', *('--go-version', '1.26.9'), '--json')
---------------------------- Captured stdout call -----------------------------
{
  "diff": {
    "changed_lines": 3,
    "files": [
      "store/cache.go"
    ],
    "source": "working"
  },
  "findings": [
    {
      "agreement": [
        {
          "model": "gemini-3.8-flash",
          "runs_reporting": 3,
          "runs_total": 3
        },
        {
          "model": "gpt-5.4",
          "runs_reporting": 3,
          "runs_total": 3
        }
      ],
      "file": "store/cache.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "high",
      "is_corroborated": true,
      "line": 41,
      "lines": [
        41
      ],
      "messages": [
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gemini-3.8-flash",
          "run_index": 1,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gemini-3.8-flash",
          "run_index": 2,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gemini-3.8-flash",
          "run_index": 3,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gpt-5.4",
          "run_index": 1,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gpt-5.4",
          "run_index": 2,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gpt-5.4",
          "run_index": 3,
          "severity": "high"
        }
      ],
      "severities": [
        "high"
      ]
    }
  ],
  "has_no_usable_response": false,
  "is_partial": false,
  "models": [
    {
      "model": "gpt-5.4",
      "runs_answered": 3,
      "runs_completed": 3,
      "runs_requested": 3
    },
    {
      "model": "gemini-3.8-flash",
      "runs_answered": 3,
      "runs_completed": 3,
      "runs_requested": 3
    }
  ],
  "module_rules": {
    "provenance": "local-launch",
    "sources": [],
    "status": "not-found"
  },
  "schema_version": 2,
  "silent_runs": [],
  "toolchain": {
    "gates": [],
    "selection": {
      "commands": [],
      "discovery_diagnostics": [],
      "executable": null,
      "executable_sha256": null,
      "executable_sha256_after": null,
      "gofmt_executable": null,
      "gofmt_sha256": null,
      "gofmt_sha256_after": null,
      "goroot": null,
      "observed_version": null,
      "probes": [],
      "project_version": "1.26.9",
      "reason": "toolchain checks were skipped by request",
      "request_source": "cli",
      "requested_version": "1.26.9",
      "selection_source": null,
      "status": "not_run"
    },
    "skip_reason": "toolchain checks were skipped by request",
    "was_run": false
  },
  "unavailable_models": [],
  "unparsed_responses": []
}
_______ test_explicit_go_options_conflict_with_skip_toolchain[option1] ________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:163: in test_explicit_go_options_conflict_with_skip_toolchain
    assert review("--working", "--skip-toolchain", *option, "--json") == EXIT_USAGE_ERROR
E   AssertionError: assert 0 == 2
E    +  where 0 = review('--working', '--skip-toolchain', *('--go-executable', 'sdk'), '--json')
---------------------------- Captured stdout call -----------------------------
{
  "diff": {
    "changed_lines": 3,
    "files": [
      "store/cache.go"
    ],
    "source": "working"
  },
  "findings": [
    {
      "agreement": [
        {
          "model": "gemini-3.8-flash",
          "runs_reporting": 3,
          "runs_total": 3
        },
        {
          "model": "gpt-5.4",
          "runs_reporting": 3,
          "runs_total": 3
        }
      ],
      "file": "store/cache.go",
      "has_nearby_multi_model_reports": false,
      "has_severity_disagreement": false,
      "highest_severity": "high",
      "is_corroborated": true,
      "line": 41,
      "lines": [
        41
      ],
      "messages": [
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gemini-3.8-flash",
          "run_index": 1,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gemini-3.8-flash",
          "run_index": 2,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gemini-3.8-flash",
          "run_index": 3,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gpt-5.4",
          "run_index": 1,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gpt-5.4",
          "run_index": 2,
          "severity": "high"
        },
        {
          "line": 41,
          "message": "Export reads without the lock.",
          "model": "gpt-5.4",
          "run_index": 3,
          "severity": "high"
        }
      ],
      "severities": [
        "high"
      ]
    }
  ],
  "has_no_usable_response": false,
  "is_partial": false,
  "models": [
    {
      "model": "gpt-5.4",
      "runs_answered": 3,
      "runs_completed": 3,
      "runs_requested": 3
    },
    {
      "model": "gemini-3.8-flash",
      "runs_answered": 3,
      "runs_completed": 3,
      "runs_requested": 3
    }
  ],
  "module_rules": {
    "provenance": "local-launch",
    "sources": [],
    "status": "not-found"
  },
  "schema_version": 2,
  "silent_runs": [],
  "toolchain": {
    "gates": [],
    "selection": {
      "commands": [],
      "discovery_diagnostics": [],
      "executable": null,
      "executable_sha256": null,
      "executable_sha256_after": null,
      "gofmt_executable": null,
      "gofmt_sha256": null,
      "gofmt_sha256_after": null,
      "goroot": null,
      "observed_version": null,
      "probes": [],
      "project_version": "1.26.9",
      "reason": "toolchain checks were skipped by request",
      "request_source": "project",
      "requested_version": "1.26.9",
      "selection_source": null,
      "status": "not_run"
    },
    "skip_reason": "toolchain checks were skipped by request",
    "was_run": false
  },
  "unavailable_models": [],
  "unparsed_responses": []
}
=========================== short test summary info ===========================
FAILED tests/test_cli_review.py::test_explicit_go_options_conflict_with_skip_toolchain[option0]
FAILED tests/test_cli_review.py::test_explicit_go_options_conflict_with_skip_toolchain[option1]
====================== 2 failed, 57 deselected in 0.29s =======================
GREEN: explicit skip conflict refused before commands
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 59 items / 54 deselected / 5 selected

tests\test_cli_review.py .....                                           [100%]

====================== 5 passed, 54 deselected in 0.20s =======================
RED: CLI typed failures keep selection context and empty JSON stdout
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 62 items / 59 deselected / 3 selected

tests\test_cli_review.py FFF                                             [100%]

================================== FAILURES ===================================
________ test_toolchain_setup_failures_are_stderr_only[configuration] _________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:208: in test_toolchain_setup_failures_are_stderr_only
    code = review("--working", "--json")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:113: in review
    return main(["review", *args])
           ^^^^^^^^^^^^^^^^^^^^^^^
<FEATURE_WORKTREE>\tools\atom\cli.py:99: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<FEATURE_WORKTREE>\tools\atom\cli.py:682: in _run_review_command
    outcome = run_review(
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:204: in blocked
    raise error
E   atom.go_selection.GoToolchainConfigError: config.json: invalid review_go_version

During handling of the above exception, another exception occurred:
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:210: in test_toolchain_setup_failures_are_stderr_only
    pytest.fail(f"typed setup error escaped CLI diagnostics: {type(escaped).__name__}")
E   Failed: typed setup error escaped CLI diagnostics: GoToolchainConfigError
__________ test_toolchain_setup_failures_are_stderr_only[selection] ___________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:208: in test_toolchain_setup_failures_are_stderr_only
    code = review("--working", "--json")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:113: in review
    return main(["review", *args])
           ^^^^^^^^^^^^^^^^^^^^^^^
<FEATURE_WORKTREE>\tools\atom\cli.py:99: in main
    return _run_review_command(arguments)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<FEATURE_WORKTREE>\tools\atom\cli.py:682: in _run_review_command
    outcome = run_review(
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:204: in blocked
    raise error
E   atom.go_selection.GoToolchainSelectionError: Go 1.26.9 selection execution_failed: probe failed
E   fixture-go version: timed_out, exit=None
E   probe-specific stderr

During handling of the above exception, another exception occurred:
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:210: in test_toolchain_setup_failures_are_stderr_only
    pytest.fail(f"typed setup error escaped CLI diagnostics: {type(escaped).__name__}")
E   Failed: typed setup error escaped CLI diagnostics: GoToolchainSelectionError
___________ test_toolchain_setup_failures_are_stderr_only[required] ___________
<FEATURE_WORKTREE>\tools\tests\test_cli_review.py:214: in test_toolchain_setup_failures_are_stderr_only
    assert all(text in captured.err for text in expected)
E   assert False
E    +  where False = all(<generator object test_toolchain_setup_failures_are_stderr_only.<locals>.<genexpr> at 0x00000290FFDB5D80>)
=========================== short test summary info ===========================
FAILED tests/test_cli_review.py::test_toolchain_setup_failures_are_stderr_only[configuration]
FAILED tests/test_cli_review.py::test_toolchain_setup_failures_are_stderr_only[selection]
FAILED tests/test_cli_review.py::test_toolchain_setup_failures_are_stderr_only[required]
====================== 3 failed, 59 deselected in 0.34s =======================
GREEN: typed CLI failures retain original output and no success-shaped JSON
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 86 items

tests\test_cli_review.py ............................................... [ 54%]
...............                                                          [ 72%]
tests\test_cli_pr_review.py ........................                     [100%]

============================= 86 passed in 5.19s ==============================
RED: direct library requests obey frozen valid policy boundaries
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 58 items / 54 deselected / 4 selected

tests\test_go_selection.py FFFF                                          [100%]

================================== FAILURES ===================================
____________ test_invalid_library_request_is_rejected[overrides0] _____________
tests\test_go_selection.py:115: in test_invalid_library_request_is_rejected
    pytest.fail("invalid library request was accepted")
E   Failed: invalid library request was accepted
____________ test_invalid_library_request_is_rejected[overrides1] _____________
tests\test_go_selection.py:115: in test_invalid_library_request_is_rejected
    pytest.fail("invalid library request was accepted")
E   Failed: invalid library request was accepted
____________ test_invalid_library_request_is_rejected[overrides2] _____________
tests\test_go_selection.py:115: in test_invalid_library_request_is_rejected
    pytest.fail("invalid library request was accepted")
E   Failed: invalid library request was accepted
____________ test_invalid_library_request_is_rejected[overrides3] _____________
tests\test_go_selection.py:115: in test_invalid_library_request_is_rejected
    pytest.fail("invalid library request was accepted")
E   Failed: invalid library request was accepted
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides0]
FAILED tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides1]
FAILED tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides2]
FAILED tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides3]
====================== 4 failed, 54 deselected in 0.19s =======================
GREEN: library requests cannot bypass policy validation
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 79 items

tests\test_go_selection.py ............................................. [ 56%]
.............                                                            [ 73%]
tests\test_review_toolchain.py .....................                     [100%]

============================= 79 passed in 0.74s ==============================
RED: terminal actual-probe failure retains discovery diagnostics
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 59 items / 58 deselected / 1 selected

tests\test_go_selection.py F                                             [100%]

================================== FAILURES ===================================
____ test_real_probe_failure_is_terminal_and_retains_discovery_diagnostics ____
tests\test_go_selection.py:326: in test_real_probe_failure_is_terminal_and_retains_discovery_diagnostics
    assert raised.value.diagnostics, "real probe failure discarded earlier candidate diagnostics"
E   AssertionError: real probe failure discarded earlier candidate diagnostics
E   assert ()
E    +  where () = GoToolchainSelectionError('Go 1.26.9 selection verification_failed: version probe did not match request\n<LOCAL_PROFILE>\\test_real_probe_failure_is_ter0\\first\\bin\\go.exe version: completed, exit=0\ngo version go1.27.0 windows/amd64').diagnostics
E    +    where GoToolchainSelectionError('Go 1.26.9 selection verification_failed: version probe did not match request\n<LOCAL_PROFILE>\\test_real_probe_failure_is_ter0\\first\\bin\\go.exe version: completed, exit=0\ngo version go1.27.0 windows/amd64') = <ExceptionInfo GoToolchainSelectionError('Go 1.26.9 selection verification_failed: version probe did not match request...real_probe_failure_is_ter0\\first\\bin\\go.exe version: completed, exit=0\ngo version go1.27.0 windows/amd64') tblen=2>.value
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_real_probe_failure_is_terminal_and_retains_discovery_diagnostics
====================== 1 failed, 58 deselected in 0.43s =======================
GREEN: terminal probe rejection retains earlier discovery failures
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 59 items

tests\test_go_selection.py ............................................. [ 76%]
..............                                                           [100%]

============================= 59 passed in 2.67s ==============================
RED: explicit distribution errors include direct-path remedy
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 59 items / 54 deselected / 5 selected

tests\test_go_selection.py FFFFF                                         [100%]

================================== FAILURES ===================================
__________ test_explicit_candidate_never_falls_back[missing_binary] ___________
atom\go_selection.py:178: in resolve_go_toolchain
    binary, initial_hash, formatter, formatter_hash = _inspect_distribution(
atom\go_selection.py:325: in _inspect_distribution
    binary = binary.resolve(strict=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:670: in resolve
    return self.with_segments(os.path.realpath(self, strict=strict))
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [WinError 2] The system cannot find the file specified: '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-596\\test_explicit_candidate_never_0\\installed\\bin\\go.exe'

The above exception was the direct cause of the following exception:
tests\test_go_selection.py:245: in test_explicit_candidate_never_falls_back
    resolve_go_toolchain(
atom\go_selection.py:184: in resolve_go_toolchain
    raise GoToolchainSelectionError(
E   atom.go_selection.GoToolchainSelectionError: Go 1.26.9 selection verification_failed: reading explicit distribution
E   explicit: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-596\test_explicit_candidate_never_0\installed\bin\go.exe: [WinError 2] The system cannot find the file specified: '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-596\\test_explicit_candidate_never_0\\installed\\bin\\go.exe'

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:254: in test_explicit_candidate_never_falls_back
    assert "--go-executable" in str(error), "explicit-path remedy was omitted"
E   AssertionError: explicit-path remedy was omitted
E   assert '--go-executable' in "Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...\\\Local\\\\Temp\\\\pytest-of-gimotwan\\\\pytest-596\\\\test_explicit_candidate_never_0\\\\installed\\\\bin\\\\go.exe'"
E    +  where "Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...\\\Local\\\\Temp\\\\pytest-of-gimotwan\\\\pytest-596\\\\test_explicit_candidate_never_0\\\\installed\\\\bin\\\\go.exe'" = str(GoToolchainSelectionError("Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: C:\\Users...\\Local\\\\Temp\\\\pytest-of-gimotwan\\\\pytest-596\\\\test_explicit_candidate_never_0\\\\installed\\\\bin\\\\go.exe'"))
__________ test_explicit_candidate_never_falls_back[missing_version] __________
atom\go_selection.py:178: in resolve_go_toolchain
    binary, initial_hash, formatter, formatter_hash = _inspect_distribution(
atom\go_selection.py:329: in _inspect_distribution
    metadata = (binary.parent.parent / "VERSION").read_text(encoding="utf-8").splitlines()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:546: in read_text
    return PathBase.read_text(self, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_abc.py:632: in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:537: in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [Errno 2] No such file or directory: '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-596\\test_explicit_candidate_never_1\\installed\\VERSION'

The above exception was the direct cause of the following exception:
tests\test_go_selection.py:245: in test_explicit_candidate_never_falls_back
    resolve_go_toolchain(
atom\go_selection.py:184: in resolve_go_toolchain
    raise GoToolchainSelectionError(
E   atom.go_selection.GoToolchainSelectionError: Go 1.26.9 selection verification_failed: reading explicit distribution
E   explicit: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-596\test_explicit_candidate_never_1\installed\bin\go.exe: [Errno 2] No such file or directory: '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-596\\test_explicit_candidate_never_1\\installed\\VERSION'

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:254: in test_explicit_candidate_never_falls_back
    assert "--go-executable" in str(error), "explicit-path remedy was omitted"
E   AssertionError: explicit-path remedy was omitted
E   assert '--go-executable' in "Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...pData\\\\Local\\\\Temp\\\\pytest-of-gimotwan\\\\pytest-596\\\\test_explicit_candidate_never_1\\\\installed\\\\VERSION'"
E    +  where "Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...pData\\\\Local\\\\Temp\\\\pytest-of-gimotwan\\\\pytest-596\\\\test_explicit_candidate_never_1\\\\installed\\\\VERSION'" = str(GoToolchainSelectionError("Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: C:\\Users...Data\\\\Local\\\\Temp\\\\pytest-of-gimotwan\\\\pytest-596\\\\test_explicit_candidate_never_1\\\\installed\\\\VERSION'"))
__________ test_explicit_candidate_never_falls_back[wrong_metadata] ___________
atom\go_selection.py:178: in resolve_go_toolchain
    binary, initial_hash, formatter, formatter_hash = _inspect_distribution(
atom\go_selection.py:331: in _inspect_distribution
    raise ValueError(f"{binary} has missing or mismatching VERSION metadata")
E   ValueError: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-596\test_explicit_candidate_never_2\installed\bin\go.exe has missing or mismatching VERSION metadata

The above exception was the direct cause of the following exception:
tests\test_go_selection.py:245: in test_explicit_candidate_never_falls_back
    resolve_go_toolchain(
atom\go_selection.py:184: in resolve_go_toolchain
    raise GoToolchainSelectionError(
E   atom.go_selection.GoToolchainSelectionError: Go 1.26.9 selection verification_failed: reading explicit distribution
E   explicit: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-596\test_explicit_candidate_never_2\installed\bin\go.exe: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-596\test_explicit_candidate_never_2\installed\bin\go.exe has missing or mismatching VERSION metadata

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:254: in test_explicit_candidate_never_falls_back
    assert "--go-executable" in str(error), "explicit-path remedy was omitted"
E   AssertionError: explicit-path remedy was omitted
E   assert '--go-executable' in 'Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...otwan\\pytest-596\\test_explicit_candidate_never_2\\installed\\bin\\go.exe has missing or mismatching VERSION metadata'
E    +  where 'Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...otwan\\pytest-596\\test_explicit_candidate_never_2\\installed\\bin\\go.exe has missing or mismatching VERSION metadata' = str(GoToolchainSelectionError('Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: C:\\Users...twan\\pytest-596\\test_explicit_candidate_never_2\\installed\\bin\\go.exe has missing or mismatching VERSION metadata'))
______________ test_explicit_candidate_never_falls_back[wrapper] ______________
atom\go_selection.py:178: in resolve_go_toolchain
    binary, initial_hash, formatter, formatter_hash = _inspect_distribution(
atom\go_selection.py:328: in _inspect_distribution
    raise ValueError(f"{binary} is not a direct distribution bin/{expected_name}")
E   ValueError: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-596\test_explicit_candidate_never_3\installed\bin\go.cmd is not a direct distribution bin/go.exe

The above exception was the direct cause of the following exception:
tests\test_go_selection.py:245: in test_explicit_candidate_never_falls_back
    resolve_go_toolchain(
atom\go_selection.py:184: in resolve_go_toolchain
    raise GoToolchainSelectionError(
E   atom.go_selection.GoToolchainSelectionError: Go 1.26.9 selection verification_failed: reading explicit distribution
E   explicit: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-596\test_explicit_candidate_never_3\installed\bin\go.cmd: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-596\test_explicit_candidate_never_3\installed\bin\go.cmd is not a direct distribution bin/go.exe

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:254: in test_explicit_candidate_never_falls_back
    assert "--go-executable" in str(error), "explicit-path remedy was omitted"
E   AssertionError: explicit-path remedy was omitted
E   assert '--go-executable' in 'Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...-gimotwan\\pytest-596\\test_explicit_candidate_never_3\\installed\\bin\\go.cmd is not a direct distribution bin/go.exe'
E    +  where 'Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...-gimotwan\\pytest-596\\test_explicit_candidate_never_3\\installed\\bin\\go.cmd is not a direct distribution bin/go.exe' = str(GoToolchainSelectionError('Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: C:\\Users...gimotwan\\pytest-596\\test_explicit_candidate_never_3\\installed\\bin\\go.cmd is not a direct distribution bin/go.exe'))
_________ test_explicit_candidate_never_falls_back[missing_formatter] _________
atom\go_selection.py:178: in resolve_go_toolchain
    binary, initial_hash, formatter, formatter_hash = _inspect_distribution(
atom\go_selection.py:332: in _inspect_distribution
    formatter = binary.with_name("gofmt.exe" if os.name == "nt" else "gofmt").resolve(strict=True)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\pathlib\_local.py:670: in resolve
    return self.with_segments(os.path.realpath(self, strict=strict))
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   FileNotFoundError: [WinError 2] The system cannot find the file specified: '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-596\\test_explicit_candidate_never_4\\installed\\bin\\gofmt.exe'

The above exception was the direct cause of the following exception:
tests\test_go_selection.py:245: in test_explicit_candidate_never_falls_back
    resolve_go_toolchain(
atom\go_selection.py:184: in resolve_go_toolchain
    raise GoToolchainSelectionError(
E   atom.go_selection.GoToolchainSelectionError: Go 1.26.9 selection verification_failed: reading explicit distribution
E   explicit: <LOCAL_TEMP>\pytest-of-gimotwan\pytest-596\test_explicit_candidate_never_4\installed\bin\go.exe: [WinError 2] The system cannot find the file specified: '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-596\\test_explicit_candidate_never_4\\installed\\bin\\gofmt.exe'

During handling of the above exception, another exception occurred:
tests\test_go_selection.py:254: in test_explicit_candidate_never_falls_back
    assert "--go-executable" in str(error), "explicit-path remedy was omitted"
E   AssertionError: explicit-path remedy was omitted
E   assert '--go-executable' in "Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...Local\\\\Temp\\\\pytest-of-gimotwan\\\\pytest-596\\\\test_explicit_candidate_never_4\\\\installed\\\\bin\\\\gofmt.exe'"
E    +  where "Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: <LOCAL_PROFILE>\\AppData\\Local...Local\\\\Temp\\\\pytest-of-gimotwan\\\\pytest-596\\\\test_explicit_candidate_never_4\\\\installed\\\\bin\\\\gofmt.exe'" = str(GoToolchainSelectionError("Go 1.26.9 selection verification_failed: reading explicit distribution\nexplicit: C:\\Users...ocal\\\\Temp\\\\pytest-of-gimotwan\\\\pytest-596\\\\test_explicit_candidate_never_4\\\\installed\\\\bin\\\\gofmt.exe'"))
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_binary]
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_version]
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[wrong_metadata]
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[wrapper]
FAILED tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_formatter]
====================== 5 failed, 54 deselected in 0.43s =======================
GREEN: unsupported explicit layouts report remedy without fallback
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 59 items / 54 deselected / 5 selected

tests\test_go_selection.py .....                                         [100%]

====================== 5 passed, 54 deselected in 0.13s =======================
REGRESSION/NATIVE: frozen PR intent, ambient/advisory compatibility, installed runtime and formatter
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 175 items

tests\test_go_selection.py ............................................. [ 25%]
...............                                                          [ 34%]
tests\test_review_toolchain.py .......................                   [ 47%]
tests\test_cli_review.py ............................................... [ 74%]
..................                                                       [ 84%]
tests\test_cli_pr_review.py ...........................                  [100%]

============================ 175 passed in 33.69s =============================
RED: selected adapter honors copied optional child mapping without leaking it
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 61 items / 60 deselected / 1 selected

tests\test_go_selection.py F                                             [100%]

================================== FAILURES ===================================
_________ test_selected_runner_keeps_optional_child_mapping_isolated __________
tests\test_go_selection.py:443: in test_selected_runner_keeps_optional_child_mapping_isolated
    assert runner.environments[-1]["CUSTOM_ONLY"] == "custom"
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'CUSTOM_ONLY'
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_selected_runner_keeps_optional_child_mapping_isolated
====================== 1 failed, 60 deselected in 0.21s =======================
RED assertion: compare absent optional override instead of leaking KeyError from test
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 61 items / 60 deselected / 1 selected

tests\test_go_selection.py F                                             [100%]

================================== FAILURES ===================================
_________ test_selected_runner_keeps_optional_child_mapping_isolated __________
tests\test_go_selection.py:443: in test_selected_runner_keeps_optional_child_mapping_isolated
    assert runner.environments[-1].get("CUSTOM_ONLY") == "custom", "child override was ignored"
E   AssertionError: child override was ignored
E   assert None == 'custom'
E    +  where None = <built-in method get of dict object at 0x000001A1D5E4FFC0>('CUSTOM_ONLY')
E    +    where <built-in method get of dict object at 0x000001A1D5E4FFC0> = {'BASE_ONLY': 'base', 'PATH': '<LOCAL_TEMP>\\pytest-of-gimotwan\\pytest-600\\test_selected_runner_keeps_opt0\\installed\\bin', 'GOTOOLCHAIN': 'local'}.get
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_selected_runner_keeps_optional_child_mapping_isolated
====================== 1 failed, 60 deselected in 0.20s =======================
GREEN: selected adapter copies each optional mapping and retains local controls
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 61 items / 1 deselected / 60 selected

tests\test_go_selection.py ............................................. [ 75%]
...............                                                          [100%]

====================== 60 passed, 1 deselected in 0.84s =======================
RED: non-executable or invalid-format selected POSIX launch becomes failure evidence
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 30 items / 28 deselected / 2 selected

tests\test_runner.py FF                                                  [100%]

================================== FAILURES ===================================
________ test_posix_launch_errors_are_failed_command_evidence[error0] _________
tests\test_runner.py:234: in test_posix_launch_errors_are_failed_command_evidence
    result = SubprocessRunner().run(
atom\runner.py:135: in run
    process = _launch(
tests\test_runner.py:227: in failed_launch
    raise error
E   PermissionError: selected executable is not executable

During handling of the above exception, another exception occurred:
tests\test_runner.py:238: in test_posix_launch_errors_are_failed_command_evidence
    pytest.fail("unlaunchable selected executable escaped command evidence")
E   Failed: unlaunchable selected executable escaped command evidence
________ test_posix_launch_errors_are_failed_command_evidence[error1] _________
tests\test_runner.py:234: in test_posix_launch_errors_are_failed_command_evidence
    result = SubprocessRunner().run(
atom\runner.py:135: in run
    process = _launch(
tests\test_runner.py:227: in failed_launch
    raise error
E   OSError: [Errno 8] selected executable has invalid format

During handling of the above exception, another exception occurred:
tests\test_runner.py:238: in test_posix_launch_errors_are_failed_command_evidence
    pytest.fail("unlaunchable selected executable escaped command evidence")
E   Failed: unlaunchable selected executable escaped command evidence
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_posix_launch_errors_are_failed_command_evidence[error0]
FAILED tests/test_runner.py::test_posix_launch_errors_are_failed_command_evidence[error1]
====================== 2 failed, 28 deselected in 0.22s =======================
GREEN: selected POSIX launch errors are explicit non-success command results
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 30 items / 28 deselected / 2 selected

tests\test_runner.py ..                                                  [100%]

====================== 2 passed, 28 deselected in 0.11s =======================
REFACTOR/PRESERVATION: focused selector, protocol and boundary regressions after final readability pass
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 86 items / 1 deselected / 85 selected

tests\test_go_selection.py ............................................. [ 52%]
.................                                                        [ 72%]
tests\test_review_toolchain.py .......................                   [100%]

====================== 85 passed, 1 deselected in 3.79s =======================

```

## Native runner environment loop

```text
=== RED API: python -m pytest tests\test_runner.py -k child_environment_is_complete -v ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 18 items / 17 deselected / 1 selected

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent FAILED [100%]

================================== FAILURES ===================================
__ test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent __

tmp_path = WindowsPath('<LOCAL_TEMP>/pytest-of-gimotwan/pytest-551/test_child_environment_is_comp0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001A90CBBAC40>

    def test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent(
        tmp_path, monkeypatch,
    ):
        monkeypatch.setenv("ATOM_PARENT_ONLY", "must not leak")
        parent = dict(os.environ)
        environment = {"ATOM_CHILD": "selected \u03bb \U0001f680", "PYTHONIOENCODING": "utf-8"}
        original = dict(environment)
        script = (
            "import json, os, sys; "
            "print(json.dumps([os.environ.get('ATOM_CHILD'), "
            "os.environ.get('ATOM_PARENT_ONLY'), sys.stdin.read()]))"
        )
    
>       result = SubprocessRunner().run(
            [sys.executable, "-c", script], tmp_path, timeout_seconds=5,
            stdin_text="prompt \u03bb\n", environment=environment,
        )
E       TypeError: SubprocessRunner.run() got an unexpected keyword argument 'environment'

tests\test_runner.py:32: TypeError
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent - TypeError: SubprocessRunner.run() got an unexpected keyword argument 'environment'
====================== 1 failed, 17 deselected in 4.50s =======================
EXIT CODE: 1
=== RED assertion: python -m pytest tests\test_runner.py -k child_environment_is_complete -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 18 items / 17 deselected / 1 selected

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent FAILED [100%]

================================== FAILURES ===================================
__ test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent __

tmp_path = WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_child_environment_is_comp0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001DD6ADEAB10>

    def test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent(
        tmp_path, monkeypatch,
    ):
        monkeypatch.setenv("ATOM_PARENT_ONLY", "must not leak")
        parent = dict(os.environ)
        environment = {"ATOM_CHILD": "selected \u03bb \U0001f680", "PYTHONIOENCODING": "utf-8"}
        original = dict(environment)
        script = (
            "import json, os, sys; "
            "print(json.dumps([os.environ.get('ATOM_CHILD'), "
            "os.environ.get('ATOM_PARENT_ONLY'), sys.stdin.read()]))"
        )
    
        result = SubprocessRunner().run(
            [sys.executable, "-c", script], tmp_path, timeout_seconds=5,
            stdin_text="prompt \u03bb\n", environment=environment,
        )
    
        assert result.succeeded, result.stderr
>       assert json.loads(result.stdout) == ["selected \u03bb \U0001f680", None, "prompt \u03bb\n"]
E       AssertionError: assert [None, 'must not leak', 'prompt \xce\xbb\\n'] == ['selected \u03bb \U0001f680', None, 'prompt \u03bb\\n']
E         
E         At index 0 diff: None != 'selected \u03bb \U0001f680'
E         
E         Full diff:
E           [
E         -     'selected \u03bb \U0001f680',
E               None,
E         +     'must not leak',
E         -     'prompt \u03bb\\n',
E         ?             ^
E         +     'prompt λ\n',
E         ?             ^^
E           ]

tests\test_runner.py:38: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent - AssertionError: assert [None, 'must not leak', 'prompt \xce\xbb\\n'] == ['selected \u03bb \U0001f680', None, 'prompt \u03bb\\n']\n  \n  At index 0 diff: None != 'selected \u03bb \U0001f680'\n  \n  Full diff:\n    [\n  -     'selected \u03bb \U0001f680',\n        None,\n  +     'must not leak',\n  -     'prompt \u03bb\\n',\n  ?             ^\n  +     'prompt \xce\xbb\\n',\n  ?             ^^\n    ]
====================== 1 failed, 17 deselected in 0.32s =======================
EXIT CODE: 1
=== GREEN Unicode complete environment: python -m pytest tests\test_runner.py -k child_environment_is_complete -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 18 items / 17 deselected / 1 selected

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [100%]

====================== 1 passed, 17 deselected in 0.27s =======================
EXIT CODE: 0
=== RED child PATH/PATHEXT: python -m pytest tests\test_runner.py -k executable_lookup_uses_complete -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 19 items / 18 deselected / 1 selected

tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext FAILED [100%]

================================== FAILURES ===================================
_____ test_executable_lookup_uses_complete_child_path_and_windows_pathext _____

tmp_path = WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_executable_lookup_uses_co0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000024C9C26AC40>

    def test_executable_lookup_uses_complete_child_path_and_windows_pathext(
        tmp_path, monkeypatch,
    ):
        child_bin = tmp_path / "child-bin"
        child_bin.mkdir()
        environment = dict(os.environ)
        if os.name == "nt":
            executable = child_bin / "atom-env-tool.ENVTOOL"
            shutil.copyfile(Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe", executable)
            arguments = ["/d", "/c", "echo child-path"]
            environment = {
                key: value for key, value in environment.items()
                if key.upper() not in ("PATH", "PATHEXT")
            }
            environment.update({"pAtH": str(child_bin), "pAtHeXt": ".ENVTOOL"})
        else:
            executable = child_bin / "atom-env-tool"
            shutil.copyfile(sys.executable, executable)
            executable.chmod(0o755)
            arguments = ["-c", "print('child-path')"]
            environment["PATH"] = str(child_bin)
        monkeypatch.setenv("PATH", str(tmp_path / "parent-empty-bin"))
        monkeypatch.setenv("PATHEXT", ".EXE")
        parent = dict(os.environ)
    
        result = SubprocessRunner().run(
            ["atom-env-tool", *arguments], tmp_path, timeout_seconds=5,
            environment=environment,
        )
    
>       assert result.succeeded, result.stderr
E       AssertionError: Executable not found on PATH: atom-env-tool
E       assert False
E        +  where False = CommandResult(command=('atom-env-tool', '/d', '/c', 'echo child-path'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_executable_lookup_uses_co0'), outcome=<CommandOutcome.TOOL_MISSING: 'tool_missing'>, exit_code=None, stdout='', stderr='Executable not found on PATH: atom-env-tool', duration_seconds=0.002572900033555925).succeeded

tests\test_runner.py:75: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext - AssertionError: Executable not found on PATH: atom-env-tool
assert False
 +  where False = CommandResult(command=('atom-env-tool', '/d', '/c', 'echo child-path'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_executable_lookup_uses_co0'), outcome=<CommandOutcome.TOOL_MISSING: 'tool_missing'>, exit_code=None, stdout='', stderr='Executable not found on PATH: atom-env-tool', duration_seconds=0.002572900033555925).succeeded
====================== 1 failed, 18 deselected in 0.17s =======================
EXIT CODE: 1
=== GREEN child PATH/PATHEXT: python -m pytest tests\test_runner.py -k "executable_lookup_uses_complete or child_environment_is_complete" -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 19 items / 17 deselected / 2 selected

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [ 50%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext PASSED [100%]

====================== 2 passed, 17 deselected in 0.51s =======================
EXIT CODE: 0
=== RED missing child tool: python -m pytest tests\test_runner.py -k missing_child_tool -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 20 items / 19 deselected / 1 selected

tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path FAILED [100%]

================================== FAILURES ===================================
___________ test_missing_child_tool_never_falls_back_to_parent_path ___________

tmp_path = WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000020F54B6AFD0>

    def test_missing_child_tool_never_falls_back_to_parent_path(tmp_path, monkeypatch):
        parent_bin = tmp_path / "parent-bin"
        parent_bin.mkdir()
        if os.name == "nt":
            shutil.copyfile(
                Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe",
                parent_bin / "atom-parent-only.exe",
            )
            arguments = ["/d", "/c", "echo parent-tool-ran"]
        else:
            executable = parent_bin / "atom-parent-only"
            shutil.copyfile(sys.executable, executable)
            executable.chmod(0o755)
            arguments = ["-c", "print('parent-tool-ran')"]
        monkeypatch.setenv("PATH", str(parent_bin))
        environment = {"PATH": str(tmp_path / "child-empty-bin"), "PATHEXT": ".EXE"}
    
        result = SubprocessRunner().run(
            ["atom-parent-only", *arguments], tmp_path, timeout_seconds=5,
            environment=environment,
        )
    
>       assert result.outcome is CommandOutcome.TOOL_MISSING, result
E       AssertionError: CommandResult(command=('atom-parent-only', '/d', '/c', 'echo parent-tool-ran'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_0'), outcome=<CommandOutcome.COMPLETED: 'completed'>, exit_code=0, stdout='parent-tool-ran
E         ', stderr='', duration_seconds=0.15019590000156313)
E       assert <CommandOutcome.COMPLETED: 'completed'> is <CommandOutcome.TOOL_MISSING: 'tool_missing'>
E        +  where <CommandOutcome.COMPLETED: 'completed'> = CommandResult(command=('atom-parent-only', '/d', '/c', 'echo parent-tool-ran'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_0'), outcome=<CommandOutcome.COMPLETED: 'completed'>, exit_code=0, stdout='parent-tool-ran\n', stderr='', duration_seconds=0.15019590000156313).outcome
E        +  and   <CommandOutcome.TOOL_MISSING: 'tool_missing'> = CommandOutcome.TOOL_MISSING

tests\test_runner.py:102: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path - AssertionError: CommandResult(command=('atom-parent-only', '/d', '/c', 'echo parent-tool-ran'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_0'), outcome=<CommandOutcome.COMPLETED: 'completed'>, exit_code=0, stdout='parent-tool-ran
  ', stderr='', duration_seconds=0.15019590000156313)
assert <CommandOutcome.COMPLETED: 'completed'> is <CommandOutcome.TOOL_MISSING: 'tool_missing'>
 +  where <CommandOutcome.COMPLETED: 'completed'> = CommandResult(command=('atom-parent-only', '/d', '/c', 'echo parent-tool-ran'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_0'), outcome=<CommandOutcome.COMPLETED: 'completed'>, exit_code=0, stdout='parent-tool-ran\n', stderr='', duration_seconds=0.15019590000156313).outcome
 +  and   <CommandOutcome.TOOL_MISSING: 'tool_missing'> = CommandOutcome.TOOL_MISSING
====================== 1 failed, 19 deselected in 0.34s =======================
EXIT CODE: 1
=== GREEN missing child tool: python -m pytest tests\test_runner.py -k "missing_child_tool or executable_lookup_uses_complete or child_environment_is_complete" -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 20 items / 17 deselected / 3 selected

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [ 33%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext PASSED [ 66%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path PASSED [100%]

====================== 3 passed, 17 deselected in 0.49s =======================
EXIT CODE: 0
=== RED child shadow diagnosis: python -m pytest tests\test_runner.py -k child_path_diagnostic -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 21 items / 20 deselected / 1 selected

tests/test_runner.py::test_windows_child_path_diagnostic_names_shadowed_copy FAILED [100%]

================================== FAILURES ===================================
___________ test_windows_child_path_diagnostic_names_shadowed_copy ____________

tmp_path = WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_windows_child_path_diagno0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001BAD16FAD70>

    @pytest.mark.skipif(os.name != "nt", reason="Windows stale executable diagnosis")
    def test_windows_child_path_diagnostic_names_shadowed_copy(tmp_path, monkeypatch):
        broken = tmp_path / "broken"
        working = tmp_path / "working"
        broken.mkdir()
        working.mkdir()
        first = broken / "atom-shadow.ENVTOOL"
        second = working / "atom-shadow.ENVTOOL"
        first.touch()
        shutil.copyfile(Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe", second)
        monkeypatch.setenv("PATH", str(tmp_path / "parent-empty-bin"))
        environment = {"pAtH": os.pathsep.join(map(str, (broken, working))),
                       "pAtHeXt": ".ENVTOOL"}
    
        result = SubprocessRunner().run(
            ["atom-shadow"], tmp_path, timeout_seconds=5, environment=environment,
        )
    
        assert result.outcome is CommandOutcome.TOOL_MISSING
        assert str(first) in result.stderr
>       assert str(second) in result.stderr
E       assert '<FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\working\\atom-shadow.ENVTOOL' in "Found 'atom-shadow' at <FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\broken\\atom-shadow.ENVTOOL but the system could not start it. The entry on PATH is present but not launchable. This usually means a broken or stale install. Reinstall the tool."
E        +  where '<FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\working\\atom-shadow.ENVTOOL' = str(WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_windows_child_path_diagno0/working/atom-shadow.ENVTOOL'))
E        +  and   "Found 'atom-shadow' at <FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\broken\\atom-shadow.ENVTOOL but the system could not start it. The entry on PATH is present but not launchable. This usually means a broken or stale install. Reinstall the tool." = CommandResult(command=('atom-shadow',), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_windows_child_path_diagno0'), outcome=<CommandOutcome.TOOL_MISSING: 'tool_missing'>, exit_code=None, stdout='', stderr="Found 'atom-shadow' at <FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\broken\\atom-shadow.ENVTOOL but the system could not start it. The entry on PATH is present but not launchable. This usually means a broken or stale install. Reinstall the tool.", duration_seconds=0.0073998000007122755).stderr

tests\test_runner.py:127: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_windows_child_path_diagnostic_names_shadowed_copy - assert '<FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\working\\atom-shadow.ENVTOOL' in "Found 'atom-shadow' at <FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\broken\\atom-shadow.ENVTOOL but the system could not start it. The entry on PATH is present but not launchable. This usually means a broken or stale install. Reinstall the tool."
 +  where '<FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\working\\atom-shadow.ENVTOOL' = str(WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_windows_child_path_diagno0/working/atom-shadow.ENVTOOL'))
 +  and   "Found 'atom-shadow' at <FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\broken\\atom-shadow.ENVTOOL but the system could not start it. The entry on PATH is present but not launchable. This usually means a broken or stale install. Reinstall the tool." = CommandResult(command=('atom-shadow',), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_windows_child_path_diagno0'), outcome=<CommandOutcome.TOOL_MISSING: 'tool_missing'>, exit_code=None, stdout='', stderr="Found 'atom-shadow' at <FEATURE_WORKTREE>\\tools\\.pytest-runner-env-work\\test_windows_child_path_diagno0\\broken\\atom-shadow.ENVTOOL but the system could not start it. The entry on PATH is present but not launchable. This usually means a broken or stale install. Reinstall the tool.", duration_seconds=0.0073998000007122755).stderr
====================== 1 failed, 20 deselected in 0.18s =======================
EXIT CODE: 1
=== GREEN child shadow diagnosis and legacy: python -m pytest tests\test_runner.py -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 21 items

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [  4%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext PASSED [  9%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path PASSED [ 14%]
tests/test_runner.py::test_windows_child_path_diagnostic_names_shadowed_copy PASSED [ 19%]
tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape PASSED [ 23%]
tests/test_runner.py::test_command_result_succeeded_only_for_completed_zero PASSED [ 28%]
tests/test_runner.py::test_command_result_combined_output_preserves_both_streams PASSED [ 33%]
tests/test_runner.py::test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately PASSED [ 38%]
tests/test_runner.py::test_subprocess_runner_returns_timed_out_without_raising PASSED [ 42%]
tests/test_runner.py::test_subprocess_runner_returns_tool_missing_without_raising PASSED [ 47%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_absent_tool_is_reported_as_missing_from_path PASSED [ 52%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_unlaunchable_path_entry_is_not_blamed_on_path PASSED [ 57%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_a_working_copy_hidden_behind_the_broken_one_is_named PASSED [ 61%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_missing_working_directory_is_not_blamed_on_the_tool PASSED [ 66%]
tests/test_runner.py::TestStdinIsNeverInherited::test_a_child_reading_stdin_sees_end_of_input_immediately PASSED [ 71%]
tests/test_runner.py::TestStdinIsNeverInherited::test_supplied_text_reaches_the_child PASSED [ 76%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind PASSED [ 80%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_output_written_before_the_kill_is_still_returned PASSED [ 85%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_the_reported_duration_matches_the_time_actually_spent PASSED [ 90%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 95%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [100%]

======================== 19 passed, 2 skipped in 4.17s ========================
EXIT CODE: 0
=== RED absolute executable ignores PATHEXT: python -m pytest tests\test_runner.py -k absolute_executable_does_not -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 22 items / 21 deselected / 1 selected

tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext FAILED [100%]

================================== FAILURES ===================================
__________ test_absolute_executable_does_not_depend_on_child_pathext __________

tmp_path = WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_absolute_executable_does_0')

    @pytest.mark.skipif(os.name != "nt", reason="Windows PATHEXT affects name lookup only")
    def test_absolute_executable_does_not_depend_on_child_pathext(tmp_path):
        result = SubprocessRunner().run(
            [sys.executable, "-c", "print('absolute')"], tmp_path, timeout_seconds=5,
            environment={"PATHEXT": ".NOTEXE", "PYTHONIOENCODING": "utf-8"},
        )
    
>       assert result.succeeded, result.stderr
E       AssertionError: Executable not found on PATH: <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
E       assert False
E        +  where False = CommandResult(command=('<LOCAL_PROFILE>\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\python.exe', '-c', "print('absolute')"), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_absolute_executable_does_0'), outcome=<CommandOutcome.TOOL_MISSING: 'tool_missing'>, exit_code=None, stdout='', stderr='Executable not found on PATH: <LOCAL_PROFILE>\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\python.exe', duration_seconds=0.002474999986588955).succeeded

tests\test_runner.py:139: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext - AssertionError: Executable not found on PATH: <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
assert False
 +  where False = CommandResult(command=('<LOCAL_PROFILE>\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\python.exe', '-c', "print('absolute')"), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_absolute_executable_does_0'), outcome=<CommandOutcome.TOOL_MISSING: 'tool_missing'>, exit_code=None, stdout='', stderr='Executable not found on PATH: <LOCAL_PROFILE>\\AppData\\Local\\Microsoft\\WindowsApps\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\python.exe', duration_seconds=0.002474999986588955).succeeded
====================== 1 failed, 21 deselected in 0.17s =======================
EXIT CODE: 1
=== GREEN absolute executable ignores PATHEXT: python -m pytest tests\test_runner.py -k absolute_executable_does_not -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 22 items / 21 deselected / 1 selected

tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext PASSED [100%]

====================== 1 passed, 21 deselected in 0.22s =======================
EXIT CODE: 0
=== RED relative child PATH: python -m pytest tests\test_runner.py -k executable_lookup_uses_complete -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 23 items / 21 deselected / 2 selected

tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[False] PASSED [ 50%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[True] FAILED [100%]

================================== FAILURES ===================================
__ test_executable_lookup_uses_complete_child_path_and_windows_pathext[True] __

tmp_path = WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_executable_lookup_uses_co1')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x0000022C5A75A520>
relative_path = True

    @pytest.mark.parametrize("relative_path", [False, True])
    def test_executable_lookup_uses_complete_child_path_and_windows_pathext(
        tmp_path, monkeypatch, relative_path,
    ):
        child_bin = tmp_path / "child-bin"
        child_bin.mkdir()
        child_path = child_bin.name if relative_path else str(child_bin)
        environment = dict(os.environ)
        if os.name == "nt":
            executable = child_bin / "atom-env-tool.ENVTOOL"
            shutil.copyfile(Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe", executable)
            arguments = ["/d", "/c", "echo child-path"]
            environment = {
                key: value for key, value in environment.items()
                if key.upper() not in ("PATH", "PATHEXT")
            }
            environment.update({"pAtH": child_path, "pAtHeXt": ".ENVTOOL"})
        else:
            executable = child_bin / "atom-env-tool"
            shutil.copyfile(sys.executable, executable)
            executable.chmod(0o755)
            arguments = ["-c", "print('child-path')"]
            environment["PATH"] = child_path
        monkeypatch.setenv("PATH", str(tmp_path / "parent-empty-bin"))
        monkeypatch.setenv("PATHEXT", ".EXE")
        parent = dict(os.environ)
    
        result = SubprocessRunner().run(
            ["atom-env-tool", *arguments], tmp_path, timeout_seconds=5,
            environment=environment,
        )
    
>       assert result.succeeded, result.stderr
E       AssertionError: Executable not found on PATH: atom-env-tool
E       assert False
E        +  where False = CommandResult(command=('atom-env-tool', '/d', '/c', 'echo child-path'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_executable_lookup_uses_co1'), outcome=<CommandOutcome.TOOL_MISSING: 'tool_missing'>, exit_code=None, stdout='', stderr='Executable not found on PATH: atom-env-tool', duration_seconds=0.0004897000035271049).succeeded

tests\test_runner.py:77: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[True] - AssertionError: Executable not found on PATH: atom-env-tool
assert False
 +  where False = CommandResult(command=('atom-env-tool', '/d', '/c', 'echo child-path'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_executable_lookup_uses_co1'), outcome=<CommandOutcome.TOOL_MISSING: 'tool_missing'>, exit_code=None, stdout='', stderr='Executable not found on PATH: atom-env-tool', duration_seconds=0.0004897000035271049).succeeded
================= 1 failed, 1 passed, 21 deselected in 0.34s ==================
EXIT CODE: 1
=== GREEN relative child PATH: python -m pytest tests\test_runner.py -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 23 items

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [  4%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[False] PASSED [  8%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[True] PASSED [ 13%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path PASSED [ 17%]
tests/test_runner.py::test_windows_child_path_diagnostic_names_shadowed_copy PASSED [ 21%]
tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext PASSED [ 26%]
tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape PASSED [ 30%]
tests/test_runner.py::test_command_result_succeeded_only_for_completed_zero PASSED [ 34%]
tests/test_runner.py::test_command_result_combined_output_preserves_both_streams PASSED [ 39%]
tests/test_runner.py::test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately PASSED [ 43%]
tests/test_runner.py::test_subprocess_runner_returns_timed_out_without_raising PASSED [ 47%]
tests/test_runner.py::test_subprocess_runner_returns_tool_missing_without_raising PASSED [ 52%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_absent_tool_is_reported_as_missing_from_path PASSED [ 56%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_unlaunchable_path_entry_is_not_blamed_on_path PASSED [ 60%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_a_working_copy_hidden_behind_the_broken_one_is_named PASSED [ 65%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_missing_working_directory_is_not_blamed_on_the_tool PASSED [ 69%]
tests/test_runner.py::TestStdinIsNeverInherited::test_a_child_reading_stdin_sees_end_of_input_immediately PASSED [ 73%]
tests/test_runner.py::TestStdinIsNeverInherited::test_supplied_text_reaches_the_child PASSED [ 78%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind PASSED [ 82%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_output_written_before_the_kill_is_still_returned PASSED [ 86%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_the_reported_duration_matches_the_time_actually_spent PASSED [ 91%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 95%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [100%]

======================== 21 passed, 2 skipped in 4.44s ========================
EXIT CODE: 0
=== GREEN preservation: copy, concurrency, empty environment, timeout and native ownership; python -m pytest tests\test_runner.py tests\test_windows_process.py -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 73 items

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [  1%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[False] PASSED [  2%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[True] PASSED [  4%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path PASSED [  5%]
tests/test_runner.py::test_windows_child_path_diagnostic_names_shadowed_copy PASSED [  6%]
tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext PASSED [  8%]
tests/test_runner.py::test_environment_is_copied_before_launch PASSED    [  9%]
tests/test_runner.py::test_concurrent_child_environments_do_not_leak_into_base_calls PASSED [ 10%]
tests/test_runner.py::test_empty_environment_does_not_inherit_parent_settings PASSED [ 12%]
tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape PASSED [ 13%]
tests/test_runner.py::test_command_result_succeeded_only_for_completed_zero PASSED [ 15%]
tests/test_runner.py::test_command_result_combined_output_preserves_both_streams PASSED [ 16%]
tests/test_runner.py::test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately PASSED [ 17%]
tests/test_runner.py::test_subprocess_runner_returns_timed_out_without_raising PASSED [ 19%]
tests/test_runner.py::test_subprocess_runner_returns_tool_missing_without_raising PASSED [ 20%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_absent_tool_is_reported_as_missing_from_path PASSED [ 21%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_unlaunchable_path_entry_is_not_blamed_on_path PASSED [ 23%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_a_working_copy_hidden_behind_the_broken_one_is_named PASSED [ 24%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_missing_working_directory_is_not_blamed_on_the_tool PASSED [ 26%]
tests/test_runner.py::TestStdinIsNeverInherited::test_a_child_reading_stdin_sees_end_of_input_immediately PASSED [ 27%]
tests/test_runner.py::TestStdinIsNeverInherited::test_supplied_text_reaches_the_child PASSED [ 28%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[False] PASSED [ 30%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[True] PASSED [ 31%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_output_written_before_the_kill_is_still_returned PASSED [ 32%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_the_reported_duration_matches_the_time_actually_spent PASSED [ 34%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 35%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [ 36%]
tests/test_windows_process.py::test_windows_native_job_is_private PASSED [ 38%]
tests/test_windows_process.py::test_windows_launch_is_suspended_until_owned PASSED [ 39%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[0] PASSED [ 41%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[7] PASSED [ 42%]
tests/test_windows_process.py::test_windows_fixture_waits_for_readable_identity_record PASSED [ 43%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[PermissionError] PASSED [ 45%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[FileNotFoundError] PASSED [ 46%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[False] PASSED [ 47%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[True] FAILED [ 49%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[False] PASSED [ 50%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[True] PASSED [ 52%]
tests/test_windows_process.py::test_windows_large_stdin_and_unicode_argv PASSED [ 53%]
tests/test_windows_process.py::test_windows_communication_sleeps_only_while_idle PASSED [ 54%]
tests/test_windows_process.py::test_windows_busy_communication_still_checks_deadline PASSED [ 56%]
tests/test_windows_process.py::test_windows_large_streams_do_not_spend_the_deadline_sleeping PASSED [ 57%]
tests/test_windows_process.py::test_windows_cmd_shim_preserves_arguments PASSED [ 58%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[create_job] PASSED [ 60%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[pipe] PASSED [ 61%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[launch] PASSED [ 63%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[assign] PASSED [ 64%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[contains] PASSED [ 65%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[resume] PASSED [ 67%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[terminate_job] PASSED [ 68%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[active_processes] PASSED [ 69%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[1] PASSED [ 71%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[2] PASSED [ 72%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[0] PASSED [ 73%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[1] PASSED [ 75%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[2] PASSED [ 76%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[completion_receipt] PASSED [ 78%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[missing_file_diagnosis] PASSED [ 79%]
tests/test_windows_process.py::test_windows_communication_observes_deferred_interrupt PASSED [ 80%]
tests/test_windows_process.py::test_windows_sigint_during_communication_is_prompt_and_reclaims_children PASSED [ 82%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[0] PASSED [ 83%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[7] PASSED [ 84%]
tests/test_windows_process.py::test_windows_partial_capture_names_incomplete_streams PASSED [ 86%]
tests/test_windows_process.py::test_windows_concurrent_runs_are_isolated PASSED [ 87%]
tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers PASSED [ 89%]
tests/test_windows_process.py::test_windows_interrupt_during_native_launch_reclaims_suspended_parent PASSED [ 90%]
tests/test_windows_process.py::test_windows_sigint_during_handle_acquisition_does_not_lose_job PASSED [ 91%]
tests/test_windows_process.py::test_windows_broken_executable_is_diagnosed_as_unlaunchable PASSED [ 93%]
tests/test_windows_process.py::test_windows_runner_assigns_and_checks_membership_before_resume PASSED [ 94%]
tests/test_windows_process.py::test_windows_child_can_close_stdin_early PASSED [ 95%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[None] PASSED [ 97%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary1] PASSED [ 98%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary2] PASSED [100%]

================================== FAILURES ===================================
_______________ test_windows_parent_exits_before_timeout[True] ________________

tmp_path = WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_windows_parent_exits_befo1')
with_environment = True

    @pytest.mark.parametrize("with_environment", [False, True])
    def test_windows_parent_exits_before_timeout(tmp_path, with_environment):
        native = _windows_module()._Native()
        with _tree_fixture(tmp_path, hold_output=True) as (command, directory, identities):
            options = {}
            if with_environment:
                options["environment"] = {
                    "ATOM_CHILD": "owned \u03bb", "PYTHONIOENCODING": "utf-8",
                }
                command = [
                    *command[:-1],
                    "import os; print(os.environ.get('ATOM_CHILD'), flush=True); " + command[-1],
                ]
            started = time.monotonic()
            result = SubprocessRunner().run(command, tmp_path, timeout_seconds=2, **options)
            elapsed = time.monotonic() - started
            handle = _retained_identity(identities)
            assert result.outcome is CommandOutcome.TIMED_OUT, result.stderr
            if with_environment:
                assert "owned \u03bb" in result.stdout
            assert elapsed < 5
>           assert result.stdout == "child-out\n"
E           AssertionError: assert 'owned \u03bb\\nchild-out\\n' == 'child-out\\n'
E             
E             + owned \u03bb
E               child-out

tests\test_windows_process.py:244: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_windows_process.py::test_windows_parent_exits_before_timeout[True] - AssertionError: assert 'owned \u03bb\\nchild-out\\n' == 'child-out\\n'\n  \n  + owned \u03bb\n    child-out
================== 1 failed, 70 passed, 2 skipped in 23.81s ===================
EXIT CODE: 1
NOTE: Expanded Windows timeout fixture intentionally prints its selected environment marker before child-out. Its legacy-only exact stdout expectation was incorrect for the new True case; corrected to exact owned-lambda newline child-out newline, keeping the False expectation unchanged. No production change demanded by this fixture defect. Copy/concurrency/empty-env/timeout cases are preservation regressions of the already RED-driven environment plumbing, not claimed independent REDs.
=== GREEN preservation after fixture correction: python -m pytest tests\test_runner.py tests\test_windows_process.py -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 73 items

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [  1%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[False] PASSED [  2%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[True] PASSED [  4%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path PASSED [  5%]
tests/test_runner.py::test_windows_child_path_diagnostic_names_shadowed_copy PASSED [  6%]
tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext PASSED [  8%]
tests/test_runner.py::test_environment_is_copied_before_launch PASSED    [  9%]
tests/test_runner.py::test_concurrent_child_environments_do_not_leak_into_base_calls PASSED [ 10%]
tests/test_runner.py::test_empty_environment_does_not_inherit_parent_settings PASSED [ 12%]
tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape PASSED [ 13%]
tests/test_runner.py::test_command_result_succeeded_only_for_completed_zero PASSED [ 15%]
tests/test_runner.py::test_command_result_combined_output_preserves_both_streams PASSED [ 16%]
tests/test_runner.py::test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately PASSED [ 17%]
tests/test_runner.py::test_subprocess_runner_returns_timed_out_without_raising PASSED [ 19%]
tests/test_runner.py::test_subprocess_runner_returns_tool_missing_without_raising PASSED [ 20%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_absent_tool_is_reported_as_missing_from_path PASSED [ 21%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_unlaunchable_path_entry_is_not_blamed_on_path PASSED [ 23%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_a_working_copy_hidden_behind_the_broken_one_is_named PASSED [ 24%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_missing_working_directory_is_not_blamed_on_the_tool PASSED [ 26%]
tests/test_runner.py::TestStdinIsNeverInherited::test_a_child_reading_stdin_sees_end_of_input_immediately PASSED [ 27%]
tests/test_runner.py::TestStdinIsNeverInherited::test_supplied_text_reaches_the_child PASSED [ 28%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[False] PASSED [ 30%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[True] PASSED [ 31%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_output_written_before_the_kill_is_still_returned PASSED [ 32%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_the_reported_duration_matches_the_time_actually_spent PASSED [ 34%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 35%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [ 36%]
tests/test_windows_process.py::test_windows_native_job_is_private PASSED [ 38%]
tests/test_windows_process.py::test_windows_launch_is_suspended_until_owned PASSED [ 39%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[0] PASSED [ 41%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[7] PASSED [ 42%]
tests/test_windows_process.py::test_windows_fixture_waits_for_readable_identity_record PASSED [ 43%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[PermissionError] PASSED [ 45%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[FileNotFoundError] PASSED [ 46%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[False] PASSED [ 47%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[True] PASSED [ 49%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[False] PASSED [ 50%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[True] PASSED [ 52%]
tests/test_windows_process.py::test_windows_large_stdin_and_unicode_argv PASSED [ 53%]
tests/test_windows_process.py::test_windows_communication_sleeps_only_while_idle PASSED [ 54%]
tests/test_windows_process.py::test_windows_busy_communication_still_checks_deadline PASSED [ 56%]
tests/test_windows_process.py::test_windows_large_streams_do_not_spend_the_deadline_sleeping PASSED [ 57%]
tests/test_windows_process.py::test_windows_cmd_shim_preserves_arguments PASSED [ 58%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[create_job] PASSED [ 60%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[pipe] PASSED [ 61%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[launch] PASSED [ 63%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[assign] PASSED [ 64%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[contains] PASSED [ 65%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[resume] PASSED [ 67%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[terminate_job] PASSED [ 68%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[active_processes] PASSED [ 69%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[1] PASSED [ 71%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[2] PASSED [ 72%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[0] PASSED [ 73%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[1] PASSED [ 75%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[2] PASSED [ 76%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[completion_receipt] PASSED [ 78%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[missing_file_diagnosis] PASSED [ 79%]
tests/test_windows_process.py::test_windows_communication_observes_deferred_interrupt PASSED [ 80%]
tests/test_windows_process.py::test_windows_sigint_during_communication_is_prompt_and_reclaims_children PASSED [ 82%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[0] PASSED [ 83%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[7] PASSED [ 84%]
tests/test_windows_process.py::test_windows_partial_capture_names_incomplete_streams PASSED [ 86%]
tests/test_windows_process.py::test_windows_concurrent_runs_are_isolated PASSED [ 87%]
tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers PASSED [ 89%]
tests/test_windows_process.py::test_windows_interrupt_during_native_launch_reclaims_suspended_parent PASSED [ 90%]
tests/test_windows_process.py::test_windows_sigint_during_handle_acquisition_does_not_lose_job PASSED [ 91%]
tests/test_windows_process.py::test_windows_broken_executable_is_diagnosed_as_unlaunchable PASSED [ 93%]
tests/test_windows_process.py::test_windows_runner_assigns_and_checks_membership_before_resume PASSED [ 94%]
tests/test_windows_process.py::test_windows_child_can_close_stdin_early PASSED [ 95%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[None] PASSED [ 97%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary1] PASSED [ 98%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary2] PASSED [100%]

======================= 71 passed, 2 skipped in 23.68s ========================
EXIT CODE: 0
=== RED empty child PATH: python -m pytest tests\test_runner.py -k missing_child_tool -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 28 items / 26 deselected / 2 selected

tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[False] PASSED [ 50%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[True] FAILED [100%]

================================== FAILURES ===================================
________ test_missing_child_tool_never_falls_back_to_parent_path[True] ________

tmp_path = WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_1')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001FFB955A520>
empty_path = True

    @pytest.mark.parametrize("empty_path", [False, True])
    def test_missing_child_tool_never_falls_back_to_parent_path(
        tmp_path, monkeypatch, empty_path,
    ):
        parent_bin = tmp_path / "parent-bin"
        parent_bin.mkdir()
        if os.name == "nt":
            shutil.copyfile(
                Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe",
                parent_bin / "atom-parent-only.exe",
            )
            arguments = ["/d", "/c", "echo parent-tool-ran"]
        else:
            executable = parent_bin / "atom-parent-only"
            shutil.copyfile(sys.executable, executable)
            executable.chmod(0o755)
            arguments = ["-c", "print('parent-tool-ran')"]
        monkeypatch.setenv("PATH", str(parent_bin))
        monkeypatch.chdir(parent_bin)
        environment = {
            "PATH": "" if empty_path else str(tmp_path / "child-empty-bin"),
            "PATHEXT": ".EXE",
        }
    
        result = SubprocessRunner().run(
            ["atom-parent-only", *arguments], tmp_path, timeout_seconds=5,
            environment=environment,
        )
    
>       assert result.outcome is CommandOutcome.TOOL_MISSING, result
E       AssertionError: CommandResult(command=('atom-parent-only', '/d', '/c', 'echo parent-tool-ran'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_1'), outcome=<CommandOutcome.COMPLETED: 'completed'>, exit_code=0, stdout='parent-tool-ran
E         ', stderr='', duration_seconds=0.14640910003799945)
E       assert <CommandOutcome.COMPLETED: 'completed'> is <CommandOutcome.TOOL_MISSING: 'tool_missing'>
E        +  where <CommandOutcome.COMPLETED: 'completed'> = CommandResult(command=('atom-parent-only', '/d', '/c', 'echo parent-tool-ran'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_1'), outcome=<CommandOutcome.COMPLETED: 'completed'>, exit_code=0, stdout='parent-tool-ran\n', stderr='', duration_seconds=0.14640910003799945).outcome
E        +  and   <CommandOutcome.TOOL_MISSING: 'tool_missing'> = CommandOutcome.TOOL_MISSING

<FEATURE_WORKTREE>\tools\tests\test_runner.py:112: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[True] - AssertionError: CommandResult(command=('atom-parent-only', '/d', '/c', 'echo parent-tool-ran'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_1'), outcome=<CommandOutcome.COMPLETED: 'completed'>, exit_code=0, stdout='parent-tool-ran
  ', stderr='', duration_seconds=0.14640910003799945)
assert <CommandOutcome.COMPLETED: 'completed'> is <CommandOutcome.TOOL_MISSING: 'tool_missing'>
 +  where <CommandOutcome.COMPLETED: 'completed'> = CommandResult(command=('atom-parent-only', '/d', '/c', 'echo parent-tool-ran'), working_directory=WindowsPath('<FEATURE_WORKTREE>/tools/.pytest-runner-env-work/test_missing_child_tool_never_1'), outcome=<CommandOutcome.COMPLETED: 'completed'>, exit_code=0, stdout='parent-tool-ran\n', stderr='', duration_seconds=0.14640910003799945).outcome
 +  and   <CommandOutcome.TOOL_MISSING: 'tool_missing'> = CommandOutcome.TOOL_MISSING
================= 1 failed, 1 passed, 26 deselected in 0.35s ==================
EXIT CODE: 1
=== GREEN empty child PATH: python -m pytest tests\test_runner.py -k missing_child_tool -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 28 items / 26 deselected / 2 selected

tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[False] PASSED [ 50%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[True] PASSED [100%]

====================== 2 passed, 26 deselected in 0.10s =======================
EXIT CODE: 0
=== REFACTOR/FINAL GREEN: python -m pytest tests\test_runner.py tests\test_windows_process.py -v --basetemp=.pytest-runner-env-work ===
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 74 items

tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [  1%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[False] PASSED [  2%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[True] PASSED [  4%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[False] PASSED [  5%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[True] PASSED [  6%]
tests/test_runner.py::test_windows_child_path_diagnostic_names_shadowed_copy PASSED [  8%]
tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext PASSED [  9%]
tests/test_runner.py::test_environment_is_copied_before_launch PASSED    [ 10%]
tests/test_runner.py::test_concurrent_child_environments_do_not_leak_into_base_calls PASSED [ 12%]
tests/test_runner.py::test_empty_environment_does_not_inherit_parent_settings PASSED [ 13%]
tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape PASSED [ 14%]
tests/test_runner.py::test_command_result_succeeded_only_for_completed_zero PASSED [ 16%]
tests/test_runner.py::test_command_result_combined_output_preserves_both_streams PASSED [ 17%]
tests/test_runner.py::test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately PASSED [ 18%]
tests/test_runner.py::test_subprocess_runner_returns_timed_out_without_raising PASSED [ 20%]
tests/test_runner.py::test_subprocess_runner_returns_tool_missing_without_raising PASSED [ 21%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_absent_tool_is_reported_as_missing_from_path PASSED [ 22%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_unlaunchable_path_entry_is_not_blamed_on_path PASSED [ 24%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_a_working_copy_hidden_behind_the_broken_one_is_named PASSED [ 25%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_missing_working_directory_is_not_blamed_on_the_tool PASSED [ 27%]
tests/test_runner.py::TestStdinIsNeverInherited::test_a_child_reading_stdin_sees_end_of_input_immediately PASSED [ 28%]
tests/test_runner.py::TestStdinIsNeverInherited::test_supplied_text_reaches_the_child PASSED [ 29%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[False] PASSED [ 31%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[True] PASSED [ 32%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_output_written_before_the_kill_is_still_returned PASSED [ 33%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_the_reported_duration_matches_the_time_actually_spent PASSED [ 35%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 36%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [ 37%]
tests/test_windows_process.py::test_windows_native_job_is_private PASSED [ 39%]
tests/test_windows_process.py::test_windows_launch_is_suspended_until_owned PASSED [ 40%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[0] PASSED [ 41%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[7] PASSED [ 43%]
tests/test_windows_process.py::test_windows_fixture_waits_for_readable_identity_record PASSED [ 44%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[PermissionError] PASSED [ 45%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[FileNotFoundError] PASSED [ 47%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[False] PASSED [ 48%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[True] PASSED [ 50%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[False] PASSED [ 51%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[True] PASSED [ 52%]
tests/test_windows_process.py::test_windows_large_stdin_and_unicode_argv PASSED [ 54%]
tests/test_windows_process.py::test_windows_communication_sleeps_only_while_idle PASSED [ 55%]
tests/test_windows_process.py::test_windows_busy_communication_still_checks_deadline PASSED [ 56%]
tests/test_windows_process.py::test_windows_large_streams_do_not_spend_the_deadline_sleeping PASSED [ 58%]
tests/test_windows_process.py::test_windows_cmd_shim_preserves_arguments PASSED [ 59%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[create_job] PASSED [ 60%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[pipe] PASSED [ 62%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[launch] PASSED [ 63%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[assign] PASSED [ 64%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[contains] PASSED [ 66%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[resume] PASSED [ 67%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[terminate_job] PASSED [ 68%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[active_processes] PASSED [ 70%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[1] PASSED [ 71%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[2] PASSED [ 72%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[0] PASSED [ 74%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[1] PASSED [ 75%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[2] PASSED [ 77%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[completion_receipt] PASSED [ 78%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[missing_file_diagnosis] PASSED [ 79%]
tests/test_windows_process.py::test_windows_communication_observes_deferred_interrupt PASSED [ 81%]
tests/test_windows_process.py::test_windows_sigint_during_communication_is_prompt_and_reclaims_children PASSED [ 82%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[0] PASSED [ 83%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[7] PASSED [ 85%]
tests/test_windows_process.py::test_windows_partial_capture_names_incomplete_streams PASSED [ 86%]
tests/test_windows_process.py::test_windows_concurrent_runs_are_isolated PASSED [ 87%]
tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers PASSED [ 89%]
tests/test_windows_process.py::test_windows_interrupt_during_native_launch_reclaims_suspended_parent PASSED [ 90%]
tests/test_windows_process.py::test_windows_sigint_during_handle_acquisition_does_not_lose_job PASSED [ 91%]
tests/test_windows_process.py::test_windows_broken_executable_is_diagnosed_as_unlaunchable PASSED [ 93%]
tests/test_windows_process.py::test_windows_runner_assigns_and_checks_membership_before_resume PASSED [ 94%]
tests/test_windows_process.py::test_windows_child_can_close_stdin_early PASSED [ 95%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[None] PASSED [ 97%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary1] PASSED [ 98%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary2] PASSED [100%]

======================= 72 passed, 2 skipped in 23.50s ========================
EXIT CODE: 0
=== Final whitespace: git --no-pager diff --check -- tools\atom\runner.py tools\atom\_windows_process.py tools\tests\test_runner.py tools\tests\test_windows_process.py ===
EXIT CODE: 0

```

## Archived-driver and packaged-guidance integrity

```text
poc\review-toolchain-policy\spike-local-executable.py SHA-256: 7a2cbac4d29ea40659fee5c5b0f445c5f0e889b30c417ff52ca8809715d2f3b3 (unchanged)
poc\review-toolchain-policy\spike.py SHA-256: c4053f08e473fefb756712137717b040c65940c4cc512f3050cc786cb14cd73e (unchanged)
git diff --check: exit 0
Canonical and packaged review skill: identical SHA-256

```

## Additional Native Automatic-Discovery Assertion

After the full gate, only the existing native test was strengthened to verify actual automatic PATH selection alongside the explicit path. No production source changed. The focused case passed with installed Go 1.27.0 on Windows; it also reran real build/vet/test, formatter, higher-minimum and unchanged-settings assertions. This closes a real-native automatic-discovery observation, not Linux/macOS or arbitrary SDK-layout validation.
```text
COMMAND: python -m pytest tests\test_go_selection.py -k native_installed -v --capture=tee-sys
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 63 items / 62 deselected / 1 selected

tests/test_go_selection.py::test_native_installed_distribution_runtime_formatter_and_minimum {"automatic_source": "path", "executable": "C:\\Program Files\\Go\\bin\\go.exe", "formatter": "C:\\Program Files\\Go\\bin\\gofmt.exe", "native_platform": "Windows", "observed_version": "1.27.0", "requested_version": "1.27.0"}
PASSED [100%]

====================== 1 passed, 62 deselected in 7.64s =======================
EXIT CODE: 0

```

## Post-Review Canonical-Root RED/GREEN And Final Gate

Historical capture sequence; current outcome and limits are stated above.
Original capture SHA-256: `6f47ec09f4e01e29dd0b15f8b0a75e1ec9fb287f2ec6eaeae02cb51a1db478e7`, `421c207d9e59b9fd520bc9cb3916182d0570b00103f74ab97710d8b36de4e9b8`.

```text
RED: python -m pytest tests\test_go_selection.py -k different_observed_root -v
GREEN: python -m pytest tests\test_go_selection.py tests\test_review_toolchain.py tests\test_cli_review.py tests\test_cli_pr_review.py -q
RED: independently verify observed GOROOT when its bin/go resolves to the selected executable
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 64 items / 63 deselected / 1 selected

tests/test_go_selection.py::test_different_observed_root_is_rejected_even_when_binary_identity_matches FAILED [100%]

================================== FAILURES ===================================
_ test_different_observed_root_is_rejected_even_when_binary_identity_matches __

tmp_path = WindowsPath('<LOCAL_TEMP>/pytest-of-gimotwan/pytest-608/test_different_observed_root_i0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x00000295916343E0>

    def test_different_observed_root_is_rejected_even_when_binary_identity_matches(tmp_path, monkeypatch):
        binary = distribution(tmp_path / "installed")
        other_root = tmp_path / "other-root"
        other_root.mkdir()
        alias = other_root / "bin" / binary.name
        original_resolve = Path.resolve
    
        def resolve_alias(path, strict=False):
            if path == alias:
                return binary
            return original_resolve(path, strict=strict)
    
        monkeypatch.setattr(Path, "resolve", resolve_alias)
        runner = distribution_runner(binary, tmp_path)
        command = tuple(runner.scripted_results)[1]
        values = json.loads(runner.scripted_results[command].stdout)
        values["GOROOT"] = str(other_root)
        runner.scripted_results[command] = command_result(command, tmp_path, stdout=json.dumps(values))
    
>       with pytest.raises(GoToolchainSelectionError, match="observed version/root/mode/hash") as raised:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE GoToolchainSelectionError

tests\test_go_selection.py:257: Failed
=========================== short test summary info ===========================
FAILED tests/test_go_selection.py::test_different_observed_root_is_rejected_even_when_binary_identity_matches - Failed: DID NOT RAISE GoToolchainSelectionError
====================== 1 failed, 63 deselected in 6.47s =======================
EXIT CODE: 1
GREEN: independently require the observed canonical GOROOT to match the inspected distribution root
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collected 179 items

tests\test_go_selection.py ............................................. [ 25%]
...................                                                      [ 35%]
tests\test_review_toolchain.py .......................                   [ 48%]
tests\test_cli_review.py ............................................... [ 74%]
..................                                                       [ 84%]
tests\test_cli_pr_review.py ...........................                  [100%]

============================ 179 passed in 28.93s =============================
EXIT CODE: 0

```

```text
python -m pytest tests -v --cov=atom --cov-report=term-missing
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1620 items

tests/test_artifact_cli.py::test_main_allowed_target_writes_exact_utf8_content PASSED [  0%]
tests/test_artifact_cli.py::test_main_empty_stdin_creates_empty_artifact PASSED [  0%]
tests/test_artifact_cli.py::test_module_execution_runs_main_entry_point PASSED [  0%]
tests/test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback PASSED [  0%]
tests/test_artifact_cli.py::test_main_normalizes_native_shell_line_endings_to_lf PASSED [  0%]
tests/test_artifact_cli.py::test_main_strips_the_byte_order_mark_windows_shells_prepend PASSED [  0%]
tests/test_artifact_cli.py::test_main_strips_only_the_first_byte_order_mark PASSED [  0%]
tests/test_artifact_cli.py::test_main_invalid_utf8_writes_nothing PASSED [  0%]
tests/test_artifact_cli.py::test_main_refused_target_does_not_read_stdin PASSED [  0%]
tests/test_artifact_cli.py::test_main_wrong_argument_count_exits_usage_error[arguments0] PASSED [  0%]
tests/test_artifact_cli.py::test_main_wrong_argument_count_exits_usage_error[arguments1] PASSED [  0%]
tests/test_artifact_cli.py::test_main_filesystem_failure_reports_error_without_partial_file PASSED [  0%]
tests/test_artifact_cli.py::test_main_refusal_during_write_is_reported PASSED [  0%]
tests/test_artifact_integration.py::test_package_registers_only_the_dedicated_artifact_writer PASSED [  0%]
tests/test_artifact_integration.py::test_main_atom_cli_does_not_expose_artifact_subcommand PASSED [  0%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[discover] PASSED [  0%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[poc] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[plan] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[spec] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[tdd] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[review] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_writer_instruction_forbids_bypass_and_source_writes PASSED [  1%]
tests/test_artifact_integration.py::test_onboarding_installs_artifact_writer_instructions PASSED [  1%]
tests/test_artifact_integration.py::test_onboarding_does_not_edit_copilot_permission_configuration PASSED [  1%]
tests/test_artifact_integration.py::test_built_package_installs_working_dedicated_console_script PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[specs/project/design.md-allowed-artifact-directory] PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[poc/spike/README.md-allowed-artifact-directory] PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/config.json-allowed-runtime-file] PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/state.json-allowed-runtime-file] PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/baseline.json-allowed-runtime-file] PASSED [  1%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[internal/server.go-outside-artifact-set] PASSED [  1%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[tools/atom/cli.py-outside-artifact-set] PASSED [  1%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.github/copilot-instructions.md-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/atom/AGENTS.md-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/events.jsonl-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/credentials.json-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[specs-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[specs/../internal/escape.go-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[../elsewhere/escape.md-outside-repository] PASSED [  2%]
tests/test_artifacts.py::test_absolute_path_outside_the_repository_is_refused PASSED [  2%]
tests/test_artifacts.py::test_link_inside_specs_is_refused_before_containment PASSED [  2%]
tests/test_artifacts.py::test_link_pointing_back_inside_is_still_refused PASSED [  2%]
tests/test_artifacts.py::test_write_creates_nested_artifact_directories PASSED [  2%]
tests/test_artifacts.py::test_write_replaces_an_existing_artifact PASSED [  2%]
tests/test_artifacts.py::test_write_leaves_no_temporary_files_behind PASSED [  2%]
tests/test_artifacts.py::test_mixed_batch_writes_nothing PASSED          [  2%]
tests/test_artifacts.py::test_every_refusal_in_a_batch_is_reported PASSED [  2%]
tests/test_artifacts.py::test_write_through_a_link_is_refused_and_writes_nothing PASSED [  2%]
tests/test_artifacts.py::test_link_appearing_after_validation_is_caught_before_the_write PASSED [  3%]
tests/test_artifacts.py::test_cleanup_removes_a_link_planted_where_it_created_a_directory PASSED [  3%]
tests/test_artifacts.py::test_a_file_in_place_of_a_directory_is_refused PASSED [  3%]
tests/test_artifacts.py::test_a_path_on_another_drive_is_refused PASSED  [  3%]
tests/test_artifacts.py::test_a_failed_stage_leaves_nothing_behind PASSED [  3%]
tests/test_artifacts.py::test_a_failed_replace_preserves_existing_file_and_removes_temporary PASSED [  3%]
tests/test_body.py::TestExtractPurpose::test_the_purpose_prose_is_returned PASSED [  3%]
tests/test_body.py::TestExtractPurpose::test_every_paragraph_of_the_purpose_survives PASSED [  3%]
tests/test_body.py::TestExtractPurpose::test_a_missing_purpose_section_returns_none PASSED [  3%]
tests/test_body.py::TestExtractPurpose::test_the_next_heading_ends_the_purpose_section PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_body_title_is_the_h1 PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_why_quotes_the_purpose_paragraph PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_what_changed_lists_the_commit_subjects PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_parts_appear_in_the_specified_order PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_body_links_to_each_artifact_rather_than_embedding_it PASSED [  3%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_every_link_embeds_the_pushed_commit_sha PASSED [  3%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_no_link_uses_a_branch_name_as_the_ref PASSED [  4%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_no_link_points_at_the_base_branch PASSED [  4%]
tests/test_body.py::TestWriteBodyFile::test_the_written_file_contains_no_carriage_return PASSED [  4%]
tests/test_body.py::TestWriteBodyFile::test_the_returned_count_is_the_character_count PASSED [  4%]
tests/test_body.py::TestWriteBodyFile::test_the_character_count_is_below_the_text_mode_byte_count PASSED [  4%]
tests/test_body.py::TestWriteBodyFile::test_the_reported_count_matches_the_bytes_on_disk PASSED [  4%]
tests/test_body.py::TestEvidenceStatesAbsence::test_a_gate_table_carries_one_row_per_gate PASSED [  4%]
tests/test_body.py::TestEvidenceStatesAbsence::test_the_recorded_line_replaces_the_table_it_does_not_empty_the_section PASSED [  4%]
tests/test_body.py::TestEvidenceStatesAbsence::test_an_overridden_failure_is_stated_never_asserted_green PASSED [  4%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_no_artifacts_produces_no_invented_link PASSED [  4%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_the_body_never_editorialises_a_missing_artifact PASSED [  4%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_only_the_artifacts_present_are_linked PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_a_plain_rule_is_a_target PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_several_targets_on_one_rule_are_all_read PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_prerequisites_are_not_targets PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_a_double_colon_rule_is_a_target PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS := -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS ::= -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS ?= -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS += -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS = -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_a_recipe_line_is_never_a_target PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_pattern_and_variable_targets_are_ignored PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_special_targets_are_ignored PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_a_comment_does_not_create_a_target PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_unreadable_makefile_yields_no_targets PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_without_a_makefile_the_go_defaults_stand PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_a_makefile_with_both_targets_takes_over PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[GNUmakefile] PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[makefile] PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[Makefile] PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_each_gate_is_decided_on_its_own_target PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[GNUmakefile] PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[makefile] PASSED [  6%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[Makefile] PASSED [  6%]
tests/test_buildsystem.py::TestChoosingCommands::test_gnumakefile_wins_over_makefile_as_make_would PASSED [  6%]
tests/test_buildsystem.py::TestChoosingCommands::test_without_make_installed_the_makefile_is_not_used PASSED [  6%]
tests/test_check.py::test_run_check_evaluates_every_gate_even_after_a_failure PASSED [  6%]
tests/test_check.py::test_report_passes_only_when_every_required_gate_passed_or_skipped PASSED [  6%]
tests/test_check.py::test_report_fails_when_a_required_gate_failed PASSED [  6%]
tests/test_check.py::test_optional_gate_failure_does_not_fail_the_check PASSED [  6%]
tests/test_check.py::test_warning_status_never_affects_the_verdict PASSED [  6%]
tests/test_check.py::test_exit_code_is_zero_only_when_the_check_passed[passed] PASSED [  6%]
tests/test_check.py::test_exit_code_is_zero_only_when_the_check_passed[failed] PASSED [  6%]
tests/test_check.py::test_run_check_refuses_a_directory_that_does_not_exist PASSED [  6%]
tests/test_check.py::test_run_check_refuses_a_directory_without_go_mod PASSED [  6%]
tests/test_check.py::test_run_check_refuses_before_running_any_gate PASSED [  6%]
tests/test_check.py::test_finds_poc_directories_with_go_files_but_no_go_mod PASSED [  6%]
tests/test_check.py::test_ignores_poc_directories_that_have_a_go_mod PASSED [  6%]
tests/test_check.py::test_ignores_poc_directories_with_no_go_files PASSED [  7%]
tests/test_check.py::test_returns_empty_list_when_there_is_no_poc_directory PASSED [  7%]
tests/test_check.py::test_poc_warnings_appear_in_the_report_without_failing_it PASSED [  7%]
tests/test_cli.py::test_check_returns_zero_when_every_gate_passes PASSED [  7%]
tests/test_cli.py::test_check_returns_one_when_a_gate_fails PASSED       [  7%]
tests/test_cli.py::test_check_json_flag_emits_parseable_json PASSED      [  7%]
tests/test_cli.py::test_check_reports_a_missing_directory_without_a_traceback PASSED [  7%]
tests/test_cli.py::test_check_reports_a_directory_without_go_mod_clearly PASSED [  7%]
tests/test_cli.py::test_check_defaults_to_the_current_directory PASSED   [  7%]
tests/test_cli.py::test_no_race_flag_disables_the_race_gate PASSED       [  7%]
tests/test_cli.py::test_the_cli_runs_as_a_module_without_exploding PASSED [  7%]
tests/test_cli.py::test_every_subcommand_is_reachable_in_a_real_process PASSED [  7%]
tests/test_cli_poc.py::test_poc_list_on_an_empty_repo_succeeds PASSED    [  7%]
tests/test_cli_poc.py::test_poc_list_shows_each_spike PASSED             [  7%]
tests/test_cli_poc.py::test_poc_list_flags_a_spike_missing_go_mod PASSED [  7%]
tests/test_cli_poc.py::test_poc_list_json_is_machine_readable PASSED     [  7%]
tests/test_cli_poc.py::test_poc_new_rejects_a_bad_slug_as_a_usage_error PASSED [  8%]
tests/test_cli_poc.py::test_poc_new_bad_slug_writes_one_line_to_stderr PASSED [  8%]
tests/test_cli_poc.py::test_poc_new_refuses_an_existing_spike_as_a_usage_error PASSED [  8%]
tests/test_cli_poc.py::test_poc_run_on_a_missing_spike_is_a_usage_error PASSED [  8%]
tests/test_cli_poc.py::test_poc_run_on_a_spike_without_go_mod_is_a_usage_error PASSED [  8%]
tests/test_cli_poc.py::test_a_crashed_spike_makes_the_command_exit_non_zero PASSED [  8%]
tests/test_cli_poc.py::test_every_real_verdict_makes_the_command_exit_zero PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_source_dispatch PASSED              [  8%]
tests/test_cli_pr_review.py::test_pr_freezes_launch_toolchain_request[project] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_freezes_launch_toolchain_request[cli] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_freezes_launch_toolchain_request[ambient] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra0] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra1] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra2] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra3] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra4] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra5] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_report_provenance_and_limitations[True] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_report_provenance_and_limitations[False] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_review_options_and_partial_status PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_no_model_available_is_not_clean_review PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_transport_failure_is_partial_and_still_cleans_checkout PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_required_checks_still_block[False] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_required_checks_still_block[True] PASSED [  9%]
tests/test_cli_pr_review.py::test_cleanup_failure_prevents_success_output PASSED [  9%]
tests/test_cli_pr_review.py::test_local_reports_have_no_pr_fields PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_context_is_captured_before_preparation_from_launch_directory[False] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_context_is_captured_before_preparation_from_launch_directory[True] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_context_failure_prevents_preparation PASSED [  9%]
tests/test_cli_pr_review.py::test_missing_source_help_mentions_pr PASSED [  9%]
tests/test_cli_pr_review.py::test_cli_freezes_launch_rules_before_pr_preparation[False] PASSED [  9%]
tests/test_cli_pr_review.py::test_cli_freezes_launch_rules_before_pr_preparation[True] PASSED [  9%]
tests/test_cli_pr_review.py::test_cli_rule_error_prevents_preparation_or_execution[False] PASSED [ 10%]
tests/test_cli_pr_review.py::test_cli_rule_error_prevents_preparation_or_execution[True] PASSED [ 10%]
tests/test_cli_review.py::test_review_cli_captures_project_toolchain_policy PASSED [ 10%]
tests/test_cli_review.py::test_review_cli_version_and_executable_override[False] PASSED [ 10%]
tests/test_cli_review.py::test_review_cli_version_and_executable_override[True] PASSED [ 10%]
tests/test_cli_review.py::test_explicit_go_options_conflict_with_skip_toolchain[option0] PASSED [ 10%]
tests/test_cli_review.py::test_explicit_go_options_conflict_with_skip_toolchain[option1] PASSED [ 10%]
tests/test_cli_review.py::test_toolchain_setup_failures_are_stderr_only[configuration] PASSED [ 10%]
tests/test_cli_review.py::test_toolchain_setup_failures_are_stderr_only[selection] PASSED [ 10%]
tests/test_cli_review.py::test_toolchain_setup_failures_are_stderr_only[required] PASSED [ 10%]
tests/test_cli_review.py::test_invalid_go_policy_fails_before_runner_commands[options0-2-exact stable Go] PASSED [ 10%]
tests/test_cli_review.py::test_invalid_go_policy_fails_before_runner_commands[options1-2-requires] PASSED [ 10%]
tests/test_cli_review.py::test_invalid_go_policy_fails_before_runner_commands[options2-1-review_go_version] PASSED [ 10%]
tests/test_cli_review.py::test_context_requires_opt_in_before_io PASSED  [ 10%]
tests/test_cli_review.py::test_context_cli_failure_blocks_runner[missing-1-could not be read] PASSED [ 10%]
tests/test_cli_review.py::test_context_cli_failure_blocks_runner[blank-1-empty content] PASSED [ 10%]
tests/test_cli_review.py::test_context_cli_failure_blocks_runner[duplicate-2-duplicate context-file] PASSED [ 10%]
tests/test_cli_review.py::test_fixed_evidence_cli_uses_mode PASSED       [ 11%]
tests/test_cli_review.py::test_fixed_evidence_cli_reports_scope[False-False] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_cli_reports_scope[False-True] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_cli_reports_scope[True-False] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_cli_reports_scope[True-True] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_execution_violation_is_incomplete[False] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_execution_violation_is_incomplete[True] PASSED [ 11%]
tests/test_cli_review.py::test_structured_failure_streams_never_reach_cli_reports[False-False] PASSED [ 11%]
tests/test_cli_review.py::test_structured_failure_streams_never_reach_cli_reports[False-True] PASSED [ 11%]
tests/test_cli_review.py::test_structured_failure_streams_never_reach_cli_reports[True-False] PASSED [ 11%]
tests/test_cli_review.py::test_structured_failure_streams_never_reach_cli_reports[True-True] PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_no_source_is_a_usage_error PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_two_sources_is_a_usage_error PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_working_is_accepted PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_staged_is_accepted PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_branch_is_accepted PASSED [ 11%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_setting_that_consults_nobody_is_refused[--runs-0] PASSED [ 12%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_setting_that_consults_nobody_is_refused[--concurrency-0] PASSED [ 12%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_negative_window_is_refused PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_a_complete_review_exits_zero_even_with_findings PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_a_partial_review_exits_non_zero PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_no_usable_response_fails_loudly PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_every_model_unavailable_fails_rather_than_reporting_nothing PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_a_git_failure_is_not_reported_as_a_clean_review PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_a_blocked_toolchain_returns_check_failed_without_reviewing PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_only_parent_findings_reach_the_report[False] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_only_parent_findings_reach_the_report[True] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_transport_failure_keeps_completion_but_not_answer_count PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[ \n\t] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[[]] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[not JSONL] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[{"type": "result", "exitCode": 0, "sessionId": "fixture"}] PASSED [ 13%]
tests/test_cli_review.py::TestChannels::test_the_report_goes_to_stdout PASSED [ 13%]
tests/test_cli_review.py::TestChannels::test_failure_detail_goes_to_stderr_only PASSED [ 13%]
tests/test_cli_review.py::TestChannels::test_json_output_is_parseable PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_each_model_is_asked_the_requested_number_of_times PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_custom_instructions_are_disabled PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_named_mcp_exclusions_reach_probes_and_reviews PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_no_named_mcp_server_is_disabled_by_default PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_the_prompt_carries_the_whole_diff_in_one_call PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_the_module_can_be_executed PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_appears_in_the_top_level_help PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_help_runs_without_error PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_without_a_source_exits_two_and_explains PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_with_two_sources_exits_two_and_explains PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_a_refused_setting_does_not_produce_a_traceback PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_nothing_is_defined_below_the_main_guard PASSED [ 13%]
tests/test_cli_review.py::TestTheDefaultModelPairIsTheMeasuredOne::test_the_default_models_are_the_two_that_scored_above_ninety_percent PASSED [ 14%]
tests/test_cli_review.py::TestTheDefaultModelPairIsTheMeasuredOne::test_the_help_text_names_the_models_it_actually_uses PASSED [ 14%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_ship_builds_its_gates_without_raising PASSED [ 14%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_no_race_still_builds_gates PASSED [ 14%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_five_gates_are_passed_through PASSED [ 14%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_no_race_disables_only_the_race_gate PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_base_defaults_to_main PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_base_is_forwarded PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_phase_and_title_are_forwarded PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_push_defaults_off_and_is_forwarded_when_given PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_allow_failing_checks_is_forwarded PASSED [ 14%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_a_refusal_exits_one_and_prints_to_stderr PASSED [ 14%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_an_overridden_failing_check_exits_non_zero PASSED [ 14%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_an_overridden_run_says_so_on_stderr PASSED [ 14%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_a_created_pr_says_opened PASSED [ 14%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_an_updated_pr_says_updated PASSED [ 14%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_the_commit_is_abbreviated_not_printed_whole PASSED [ 15%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_appears_in_the_top_level_help PASSED [ 15%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_help_runs_without_error PASSED [ 15%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_outside_a_phase_branch_refuses_without_a_traceback PASSED [ 15%]
tests/test_cli_state.py::test_init_creates_the_project PASSED            [ 15%]
tests/test_cli_state.py::test_init_starts_the_project_with_no_approvals PASSED [ 15%]
tests/test_cli_state.py::test_init_does_not_claim_a_phase PASSED         [ 15%]
tests/test_cli_state.py::test_init_refuses_to_overwrite_an_existing_project PASSED [ 15%]
tests/test_cli_state.py::test_init_force_overwrites_deliberately PASSED  [ 15%]
tests/test_cli_state.py::test_status_reports_the_current_phase PASSED    [ 15%]
tests/test_cli_state.py::test_status_answers_without_any_state_file_at_all PASSED [ 15%]
tests/test_cli_state.py::test_status_exits_zero_when_state_is_corrupt PASSED [ 15%]
tests/test_cli_state.py::test_status_exits_zero_whatever_it_finds PASSED [ 15%]
tests/test_cli_state.py::test_status_json_is_machine_readable PASSED     [ 15%]
tests/test_cli_state.py::test_status_json_still_emits_on_corrupt_state PASSED [ 15%]
tests/test_cli_state.py::test_status_reports_every_problem_at_once PASSED [ 15%]
tests/test_cli_state.py::test_status_reports_unsaved_work PASSED         [ 15%]
tests/test_cli_state.py::test_status_shows_the_most_recent_event PASSED  [ 16%]
tests/test_cli_state.py::test_status_sweeps_leftover_temp_files_and_says_so PASSED [ 16%]
tests/test_cli_state.py::test_the_sweep_never_touches_unsaved_work PASSED [ 16%]
tests/test_cli_state.py::test_status_works_while_the_event_log_lock_is_held PASSED [ 16%]
tests/test_cli_state.py::test_no_project_wide_lock_file_is_created PASSED [ 16%]
tests/test_cli_state.py::test_init_runs_as_a_real_process PASSED         [ 16%]
tests/test_cli_state.py::test_the_atom_package_imports_cleanly PASSED    [ 16%]
tests/test_cli_state.py::test_status_runs_as_a_subprocess_and_exits_zero PASSED [ 16%]
tests/test_cli_state.py::test_status_json_output_is_parseable_from_a_subprocess PASSED [ 16%]
tests/test_cli_state.py::test_status_runs_in_a_directory_that_is_not_a_project PASSED [ 16%]
tests/test_cli_state.py::test_status_runs_with_no_state_file_present PASSED [ 16%]
tests/test_cli_state.py::test_status_exits_zero_as_a_real_process_when_corrupt PASSED [ 16%]
tests/test_cli_state.py::test_init_that_cannot_write_is_fatal_and_says_how_to_recover PASSED [ 16%]
tests/test_cli_state.py::test_init_does_not_promise_safety_it_cannot_deliver PASSED [ 16%]
tests/test_cli_state.py::test_status_reports_a_corrupt_config_separately_from_state PASSED [ 16%]
tests/test_cli_state.py::test_status_counts_damaged_event_log_lines PASSED [ 16%]
tests/test_cli_state.py::test_status_tells_the_developer_how_to_recover_from_corruption PASSED [ 17%]
tests/test_cli_state.py::test_status_prints_each_problem_exactly_once PASSED [ 17%]
tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[source] PASSED [ 17%]
tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[packaged] PASSED [ 17%]
tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[source] PASSED [ 17%]
tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[packaged] PASSED [ 17%]
tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[source] PASSED [ 17%]
tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[packaged] PASSED [ 17%]
tests/test_comment_guidance.py::test_the_two_tdd_skill_copies_stay_identical PASSED [ 17%]
tests/test_comment_guidance.py::test_the_review_rule_names_a_missing_comment_as_the_defect PASSED [ 17%]
tests/test_context.py::test_context_capture_preserves_bytes_and_order PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[blank-empty content] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[nul-NUL content] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[encoding-invalid UTF-8] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[directory-is not a regular file] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[missing-could not be read] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[permission-could not be read] PASSED [ 18%]
tests/test_context.py::test_context_capture_rejects_invalid_input[resolution-could not be read] PASSED [ 18%]
tests/test_context.py::test_context_capture_rejects_duplicate_paths PASSED [ 18%]
tests/test_diff.py::test_runner_failure_details_survive_diff_rejection[CommandOutcome.RUNNER_ERROR] PASSED [ 18%]
tests/test_diff.py::test_runner_failure_details_survive_diff_rejection[CommandOutcome.TIMED_OUT] PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_staged_source_asks_git_for_the_index PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_working_source_asks_git_for_unstaged_changes PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_branch_source_diffs_against_the_merge_base PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_selecting_no_source_names_all_three_options PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_selecting_two_sources_is_an_error_rather_than_a_precedence_rule PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_the_chosen_source_is_recorded_on_the_request PASSED [ 18%]
tests/test_diff.py::TestCapture::test_capture_issues_exactly_one_git_command PASSED [ 18%]
tests/test_diff.py::TestCapture::test_a_multi_file_diff_is_captured_whole PASSED [ 18%]
tests/test_diff.py::TestCapture::test_an_empty_diff_is_not_an_error PASSED [ 18%]
tests/test_diff.py::TestCapture::test_a_whitespace_only_diff_counts_as_empty PASSED [ 18%]
tests/test_diff.py::TestCapture::test_nothing_is_truncated_however_large_the_diff PASSED [ 18%]
tests/test_diff.py::TestGitFailure::test_a_failed_git_command_is_reported_not_swallowed PASSED [ 19%]
tests/test_diff.py::TestGitFailure::test_a_missing_git_is_reported_clearly PASSED [ 19%]
tests/test_diff.py::TestGitFailure::test_a_timed_out_git_command_is_reported PASSED [ 19%]
tests/test_diff.py::TestSize::test_changed_lines_count_additions_and_removals PASSED [ 19%]
tests/test_diff.py::TestSize::test_file_headers_are_not_counted_as_changed_lines PASSED [ 19%]
tests/test_diff.py::TestSize::test_context_lines_are_not_counted PASSED  [ 19%]
tests/test_diff.py::TestSize::test_file_count_follows_the_b_side_of_a_rename PASSED [ 19%]
tests/test_diff.py::TestSize::test_a_file_is_counted_once_however_many_hunks_it_has PASSED [ 19%]
tests/test_diff.py::TestSize::test_size_reads_as_a_sentence_for_the_report PASSED [ 19%]
tests/test_diff.py::TestSize::test_size_description_is_singular_for_one_file PASSED [ 19%]
tests/test_diff.py::TestSize::test_an_empty_diff_describes_itself_as_empty PASSED [ 19%]
tests/test_diff.py::TestDescription::test_staged_describes_itself PASSED [ 19%]
tests/test_diff.py::TestDescription::test_working_describes_itself PASSED [ 19%]
tests/test_diff.py::TestDescription::test_branch_names_the_base_ref PASSED [ 19%]
tests/test_diff.py::TestDescription::test_a_path_without_an_a_or_b_prefix_is_used_as_is PASSED [ 19%]
tests/test_diff.py::TestHeaderConfusion::test_removing_a_markdown_rule_still_counts_as_a_changed_line PASSED [ 19%]
tests/test_diff.py::TestHeaderConfusion::test_added_content_cannot_invent_a_file PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_content_that_looks_like_a_git_header_does_not_start_a_new_file PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_content_that_looks_like_a_hunk_header_is_counted_as_a_change PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_several_files_each_reset_the_header_state PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_a_deleted_file_is_named_by_its_old_path PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_a_no_newline_marker_is_not_a_changed_line PASSED [ 20%]
tests/test_eventlog.py::test_appending_then_reading_round_trips PASSED   [ 20%]
tests/test_eventlog.py::test_appending_creates_the_log_and_its_directory PASSED [ 20%]
tests/test_eventlog.py::test_each_event_is_one_line PASSED               [ 20%]
tests/test_eventlog.py::test_appending_never_rewrites_existing_content PASSED [ 20%]
tests/test_eventlog.py::test_a_timestamp_is_recorded_for_each_event PASSED [ 20%]
tests/test_eventlog.py::test_the_caller_cannot_be_clobbered_by_the_timestamp PASSED [ 20%]
tests/test_eventlog.py::test_appending_uses_a_separate_lock_file PASSED  [ 20%]
tests/test_eventlog.py::test_a_truncated_final_line_is_skipped_with_a_warning PASSED [ 20%]
tests/test_eventlog.py::test_a_corrupt_line_in_the_middle_does_not_hide_later_ones PASSED [ 20%]
tests/test_eventlog.py::test_a_corrupt_line_reports_its_line_number PASSED [ 20%]
tests/test_eventlog.py::test_a_json_array_line_is_treated_as_damaged PASSED [ 20%]
tests/test_eventlog.py::test_blank_lines_are_ignored_rather_than_reported PASSED [ 21%]
tests/test_eventlog.py::test_reading_a_log_that_does_not_exist_yet_is_not_an_error PASSED [ 21%]
tests/test_eventlog.py::test_reading_does_not_take_the_lock PASSED       [ 21%]
tests/test_eventlog.py::test_concurrent_appends_from_real_processes_lose_nothing PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event0] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event1] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event2] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event3] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event4] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event5] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event0] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event1] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event2] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event3] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event4] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event5] PASSED [ 21%]
tests/test_extract.py::TestCliResponseIsolation::test_selects_parent_content_before_strict_findings_validation[[]] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_selects_parent_content_before_strict_findings_validation[[{"file": "store/cache.go", "line": 44, "severity": "high", "message": "Mutex is copied by value."}]] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_child_cannot_replace_parent_regardless_of_order[False-agentId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_child_cannot_replace_parent_regardless_of_order[False-parentToolCallId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_child_cannot_replace_parent_regardless_of_order[True-agentId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_child_cannot_replace_parent_regardless_of_order[True-parentToolCallId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_commentary_and_tool_requests_are_not_answers[data0] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_commentary_and_tool_requests_are_not_answers[data1] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_unphased_parent_is_supported[absent] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_unphased_parent_is_supported[None] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_malformed_candidate_fields_are_transport_failures[data0] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_malformed_candidate_fields_are_transport_failures[data1] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_record_type_is_not_ignored_as_metadata[event0] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_record_type_is_not_ignored_as_metadata[event1] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_record_type_is_not_ignored_as_metadata[event2] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[-agentId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[-parentToolCallId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[False-agentId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[False-parentToolCallId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[0-agentId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[0-parentToolCallId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[value3-agentId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[value3-parentToolCallId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_unsupported_response_format_does_not_fall_back_to_text PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[missing] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[nonzero] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[bool] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[missing_code] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[string_code] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[missing_id] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[blank_id] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[invalid_id] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[duplicate] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[trailing] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[root_error] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[child_result_only] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[[]] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[null] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[42] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[true] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback["string"] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{}] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{"type": "PRIVATE] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{"type": "assistant.message"}] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{"type": "assistant.message", "data": null}] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{"type": "assistant.message", "data": []}] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data0] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data1] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data2] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data3] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data4] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data5] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[missing] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[blank] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[child_only] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[multiple] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[unphased_multiple] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[session.error-agentId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[session.error-parentToolCallId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[result-agentId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[result-parentToolCallId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[assistant.message-agentId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[assistant.message-parentToolCallId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_crlf_blank_lines_and_non_message_events_do_not_contribute_content PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[not JSON] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[Here are findings: []] PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[{}] PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[[{"file": "store/cache.go", "line": 44, "severity": "invalid", "message": "Mutex is copied by value."}]] PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[[{"file": "store/cache.go", "line": "44", "severity": "high", "message": "Mutex is copied by value."}]] PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_keeps_fence_handling_and_file_guard PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_stream_does_not_discard_another_run PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_plain_json_needs_no_stripping PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_a_json_labelled_fence_is_stripped PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_an_unlabelled_fence_is_stripped PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_surrounding_whitespace_is_ignored PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_a_json_labelled_fence_wins_over_an_earlier_unlabelled_one PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_an_unlabelled_fence_still_works_when_it_is_the_only_one PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_a_backtick_inside_a_message_fails_loudly_rather_than_quietly PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_a_fenced_response_extracts_normally PASSED [ 26%]
tests/test_extract.py::TestNoHeuristicSalvage::test_prose_around_bare_json_is_a_failure_not_a_rescue PASSED [ 26%]
tests/test_extract.py::TestNoHeuristicSalvage::test_prose_outside_a_fence_is_still_extracted PASSED [ 26%]
tests/test_extract.py::TestSchemaValidation::test_a_well_formed_response_yields_findings PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_an_empty_array_is_a_clean_review_not_a_failure PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_non_array_payload_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_unparseable_text_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[file] PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[line] PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[severity] PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[message] PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_severity_outside_the_allowed_set_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_all_four_allowed_severities_are_accepted PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_string_line_number_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_boolean_line_number_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_line_number_below_one_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_line_zero_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_line_one_is_accepted PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_an_element_that_is_not_an_object_is_rejected PASSED [ 27%]
tests/test_extract.py::TestFileGuard::test_a_finding_naming_a_file_outside_the_diff_is_rejected PASSED [ 28%]
tests/test_extract.py::TestFileGuard::test_rejecting_one_finding_does_not_discard_its_siblings PASSED [ 28%]
tests/test_extract.py::TestFileGuard::test_the_guard_is_skipped_when_no_file_list_is_given PASSED [ 28%]
tests/test_extract.py::TestFailuresAreLoud::test_a_failure_records_which_model_and_which_run PASSED [ 28%]
tests/test_extract.py::TestFailuresAreLoud::test_a_failure_keeps_an_excerpt_of_what_was_returned PASSED [ 28%]
tests/test_extract.py::TestFailuresAreLoud::test_the_excerpt_is_bounded_so_a_huge_reply_cannot_flood_the_report PASSED [ 28%]
tests/test_extract.py::TestFailuresAreLoud::test_an_unusable_run_is_not_silently_ignored PASSED [ 28%]
tests/test_extract.py::TestAcrossRuns::test_findings_carry_their_model_and_run PASSED [ 28%]
tests/test_extract.py::TestAcrossRuns::test_one_bad_run_does_not_lose_the_good_ones PASSED [ 28%]
tests/test_extract.py::TestAcrossRuns::test_a_report_knows_whether_anything_failed PASSED [ 28%]
tests/test_extract.py::TestAcrossRuns::test_duplicate_findings_are_preserved_for_the_merge_step_to_count PASSED [ 28%]
tests/test_filelock.py::test_lock_is_exclusive_across_real_processes PASSED [ 28%]
tests/test_filelock.py::test_lock_can_be_taken_and_released PASSED       [ 28%]
tests/test_filelock.py::test_lock_creates_the_lock_file_when_absent PASSED [ 28%]
tests/test_filelock.py::test_lock_file_is_separate_from_the_file_being_appended PASSED [ 28%]
tests/test_filelock.py::test_lock_is_released_when_the_body_raises PASSED [ 28%]
tests/test_filelock.py::test_lock_times_out_when_already_held PASSED     [ 29%]
tests/test_filelock.py::test_timeout_message_explains_how_to_recover PASSED [ 29%]
tests/test_filelock.py::test_lock_does_not_truncate_an_existing_lock_file PASSED [ 29%]
tests/test_gates.py::test_runner_error_is_failed_gate_evidence PASSED    [ 29%]
tests/test_gates.py::test_go_command_gate_passes_when_command_exits_zero[build] PASSED [ 29%]
tests/test_gates.py::test_go_command_gate_passes_when_command_exits_zero[vet] PASSED [ 29%]
tests/test_gates.py::test_build_gate_fails_with_stderr_details_when_build_exits_nonzero PASSED [ 29%]
tests/test_gates.py::test_vet_gate_fails_when_vet_exits_nonzero PASSED   [ 29%]
tests/test_gates.py::test_format_gate_fails_on_printed_filenames_despite_zero_exit_code PASSED [ 29%]
tests/test_gates.py::test_format_gate_passes_when_gofmt_prints_nothing PASSED [ 29%]
tests/test_gates.py::test_format_gate_names_unformatted_files_in_summary PASSED [ 29%]
tests/test_gates.py::test_format_gate_ignores_blank_lines_in_gofmt_output PASSED [ 29%]
tests/test_gates.py::test_format_gate_fails_when_gofmt_itself_errors PASSED [ 29%]
tests/test_gates.py::test_test_gate_passes_when_go_test_exits_zero PASSED [ 29%]
tests/test_gates.py::test_test_gate_fails_and_preserves_raw_output PASSED [ 29%]
tests/test_gates.py::test_test_gate_skips_when_go_reports_no_test_files PASSED [ 29%]
tests/test_gates.py::test_test_gate_failure_wins_over_no_test_files_marker PASSED [ 30%]
tests/test_gates.py::test_race_gate_runs_go_test_with_race_flag PASSED   [ 30%]
tests/test_gates.py::test_race_gate_is_skipped_when_disabled PASSED      [ 30%]
tests/test_gates.py::test_gate_fails_and_names_tool_when_executable_missing PASSED [ 30%]
tests/test_gates.py::test_test_gate_skips_when_download_chatter_accompanies_no_test_files PASSED [ 30%]
tests/test_gates.py::test_race_gate_skips_when_no_packages_have_tests PASSED [ 30%]
tests/test_gates.py::test_race_gate_still_passes_when_tests_actually_ran PASSED [ 30%]
tests/test_gates.py::test_format_gate_ignores_files_belonging_to_a_nested_module PASSED [ 30%]
tests/test_gates.py::test_format_gate_still_reports_unformatted_files_in_the_root_module PASSED [ 30%]
tests/test_gates.py::test_format_gate_does_not_fail_for_line_ending_only_differences PASSED [ 30%]
tests/test_gates.py::test_format_gate_names_line_endings_as_the_cause PASSED [ 30%]
tests/test_gates.py::test_format_gate_still_fails_when_a_crlf_file_is_also_badly_formatted PASSED [ 30%]
tests/test_gates.py::test_format_gate_reports_a_genuine_problem_even_beside_a_line_ending_one PASSED [ 30%]
tests/test_gates.py::test_default_gates_covers_all_five_signals_in_order PASSED [ 30%]
tests/test_gates.py::test_default_gates_can_disable_race_without_removing_it PASSED [ 30%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[staticcheck] PASSED [ 30%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[errcheck] PASSED [ 30%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[govulncheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[staticcheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[errcheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[govulncheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[staticcheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[errcheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[govulncheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gates_returns_all_optional_review_signals PASSED [ 31%]
tests/test_gates_makefile.py::TestBuildGate::test_a_build_target_is_preferred_over_go_build PASSED [ 31%]
tests/test_gates_makefile.py::TestBuildGate::test_without_a_build_target_go_build_still_runs PASSED [ 31%]
tests/test_gates_makefile.py::TestBuildGate::test_a_failing_make_target_fails_the_gate PASSED [ 31%]
tests/test_gates_makefile.py::TestTestGate::test_a_test_target_is_preferred_over_go_test PASSED [ 31%]
tests/test_gates_makefile.py::TestTestGate::test_a_failing_make_target_fails_the_gate PASSED [ 31%]
tests/test_gates_makefile.py::TestTestGate::test_no_test_files_is_still_reported_as_skipped_through_make PASSED [ 31%]
tests/test_gates_makefile.py::TestTestGate::test_a_real_test_run_through_make_is_not_downgraded PASSED [ 31%]
tests/test_gates_makefile.py::TestTheOtherGatesAreNotDelegated::test_the_format_gate_ignores_a_makefile PASSED [ 31%]
tests/test_gates_makefile.py::TestTheOtherGatesAreNotDelegated::test_the_vet_gate_ignores_a_makefile PASSED [ 32%]
tests/test_gates_makefile.py::test_a_makefile_is_ignored_when_make_is_not_installed PASSED [ 32%]
tests/test_go_selection.py::test_capture_project_version PASSED          [ 32%]
tests/test_go_selection.py::test_invalid_project_version[None] PASSED    [ 32%]
tests/test_go_selection.py::test_invalid_project_version[] PASSED        [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1269] PASSED    [ 32%]
tests/test_go_selection.py::test_invalid_project_version[True] PASSED    [ 32%]
tests/test_go_selection.py::test_invalid_project_version[version4] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[version5] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[go1.26.9] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.26] PASSED    [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.026.9] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.26.09] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.20.9] PASSED  [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.26.9+auto] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.26.9 ] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.27rc1] PASSED [ 33%]
tests/test_go_selection.py::test_cli_override_records_project_version[True] PASSED [ 33%]
tests/test_go_selection.py::test_cli_override_records_project_version[False] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_cli_override_is_not_ambient_fallback[] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_cli_override_is_not_ambient_fallback[auto] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_cli_override_is_not_ambient_fallback[go1.26.9] PASSED [ 33%]
tests/test_go_selection.py::test_config_read_errors[{] PASSED            [ 33%]
tests/test_go_selection.py::test_config_read_errors[[]] PASSED           [ 33%]
tests/test_go_selection.py::test_config_read_errors[{}] PASSED           [ 33%]
tests/test_go_selection.py::test_unreadable_config_does_not_become_unconfigured PASSED [ 33%]
tests/test_go_selection.py::test_request_freezes_relative_path_and_policy PASSED [ 33%]
tests/test_go_selection.py::test_executable_requires_version PASSED      [ 33%]
tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides0] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides1] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides2] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides3] PASSED [ 33%]
tests/test_go_selection.py::test_no_implicit_or_ancestor_policy PASSED   [ 34%]
tests/test_go_selection.py::test_resolve_verifies_actual_distribution PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[wrong_version] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[version_nonzero] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[version_timed_out] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[version_missing] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[version_runner_error] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_nonzero] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_invalid_json] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_list] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_null] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_missing] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_version] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_root] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_mode] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_type] PASSED [ 34%]
tests/test_go_selection.py::test_different_observed_root_is_rejected_even_when_binary_identity_matches PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_binary] PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_version] PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[wrong_metadata] PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[wrapper] PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_formatter] PASSED [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[path] PASSED    [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[goroot] PASSED  [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[sdk] PASSED     [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[module_cache] PASSED [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[gopath] PASSED  [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[default_cache] PASSED [ 35%]
tests/test_go_selection.py::test_discovery_unavailable_does_not_use_ambient PASSED [ 35%]
tests/test_go_selection.py::test_real_probe_failure_is_terminal_and_retains_discovery_diagnostics PASSED [ 35%]
tests/test_go_selection.py::test_unsupported_host_mapping_requires_an_inspectable_installed_path PASSED [ 35%]
tests/test_go_selection.py::test_selected_environment_preserves_project_settings PASSED [ 35%]
tests/test_go_selection.py::test_native_installed_distribution_runtime_formatter_and_minimum PASSED [ 35%]
tests/test_go_selection.py::test_selected_runner_keeps_optional_child_mapping_isolated PASSED [ 36%]
tests/test_index.py::test_lists_every_spike PASSED                       [ 36%]
tests/test_index.py::test_ignores_nested_directories PASSED              [ 36%]
tests/test_index.py::test_reads_the_question_from_the_readme PASSED      [ 36%]
tests/test_index.py::test_question_is_none_when_there_is_no_readme PASSED [ 36%]
tests/test_index.py::test_question_is_none_when_the_readme_has_no_question_section PASSED [ 36%]
tests/test_index.py::test_reports_a_spike_that_has_a_go_mod PASSED       [ 36%]
tests/test_index.py::test_flags_a_spike_missing_its_go_mod PASSED        [ 36%]
tests/test_index.py::test_missing_poc_root_is_an_empty_list_not_an_error PASSED [ 36%]
tests/test_index.py::test_empty_poc_root_is_an_empty_list PASSED         [ 36%]
tests/test_index.py::test_ignores_loose_files_in_poc_root PASSED         [ 36%]
tests/test_index.py::test_results_are_sorted_for_stable_output PASSED    [ 36%]
tests/test_index.py::test_multiline_question_is_collapsed_to_one_line PASSED [ 36%]
tests/test_index.py::test_question_skips_the_blockquote_guidance PASSED  [ 36%]
tests/test_init_repeat.py::test_matching_repeat_is_a_read_only_success[False] PASSED [ 36%]
tests/test_init_repeat.py::test_matching_repeat_is_a_read_only_success[True] PASSED [ 36%]
tests/test_init_repeat.py::test_partial_initialization_is_refused_without_writes[config.json] PASSED [ 37%]
tests/test_init_repeat.py::test_partial_initialization_is_refused_without_writes[state.json] PASSED [ 37%]
tests/test_init_repeat.py::test_existing_atom_entry_is_not_a_fresh_project[True] PASSED [ 37%]
tests/test_init_repeat.py::test_existing_atom_entry_is_not_a_fresh_project[False] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[None-module_path] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[None-build_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[None-test_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[7-module_path] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[7-build_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[7-test_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[value2-module_path] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[value2-build_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[value2-test_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[-module_path] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[-build_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[-test_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[   -module_path] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[   -build_command] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[   -test_command] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_missing_configuration_fields[module_path] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_missing_configuration_fields[build_command] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_missing_configuration_fields[test_command] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[{-config.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[{-state.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[[]-config.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[[]-state.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[\ufffd-config.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[\ufffd-state.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload0] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload1] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload2] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload3] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload4] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload5] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload6] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload7] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload8] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload9] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload10] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload11] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload12] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[None-arguments0---module] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[module example.com/other\n-arguments1-go.mod] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[module example.com/other\n-arguments2-go.mod] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[module example.com/target\n-arguments3---module] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[go 1.23.0\n-arguments4-go.mod] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_reports_record_read_failures[relative_path0] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_reports_record_read_failures[relative_path1] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_reports_record_read_failures[relative_path2] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path0] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path1] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path2] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path3] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path4] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path5] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path6] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path7] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path8] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path9] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path10] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path11] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path12] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path13] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path14] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path15] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path0] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path1] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path2] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path3] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path4] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path5] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path6] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path7] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path8] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path9] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path10] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path11] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path12] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path13] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path14] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path15] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload0] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload1] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload2] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload3] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload4] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload5] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_bundle_manifest[None] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_bundle_manifest[{] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_bundle_manifest[[]] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_bundle_manifest[\ufffd] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_missing_local_instruction_reference[None] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_missing_local_instruction_reference[] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_missing_local_instruction_reference[<!-- Atom managed onboarding -->] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_missing_local_instruction_reference[../.atom/atom/AGENTS.md] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[None] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# >>> Atom generated runtime files >>>\n.atom/baseline.json\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# <<< Atom generated runtime files <<<\n# >>> Atom generated runtime files >>>\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# >>> Atom generated runtime files >>>\n# >>> Atom generated runtime files >>>\n# <<< Atom generated runtime files <<<\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# >>> Atom generated runtime files >>>\n# <<< Atom generated runtime files <<<\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# >>> Atom generated runtime files >>>\n.atom/baseline.json\n.atom/events.jsonl\n# <<< Atom generated runtime files <<<\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_reports_scaffold_read_failures[relative_path0] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_reports_scaffold_read_failures[relative_path1] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_reports_scaffold_read_failures[relative_path2] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_reports_scaffold_read_failures[relative_path3] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_does_not_require_or_inspect_machine_local_files[absent] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_does_not_require_or_inspect_machine_local_files[unusable] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_succeeds_as_a_real_process PASSED [ 43%]
tests/test_init_repeat.py::test_force_still_resets_a_partial_project PASSED [ 43%]
tests/test_init_repeat.py::test_init_help_explains_no_op_and_destructive_force PASSED [ 43%]
tests/test_invoke.py::test_fixed_evidence_exclusions_reach_probes_and_reviews PASSED [ 43%]
tests/test_invoke.py::test_runner_error_is_not_usable_model_evidence PASSED [ 43%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.TIMED_OUT-None-timed out-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.TIMED_OUT-None-timed out-True] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.TOOL_MISSING-None-CLI not found-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.TOOL_MISSING-None-CLI not found-True] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.RUNNER_ERROR-None-runner error-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.RUNNER_ERROR-None-runner error-True] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.RUNNER_ERROR-0-runner error-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.RUNNER_ERROR-0-runner error-True] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.COMPLETED-2-exited with code 2-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.COMPLETED-2-exited with code 2-True] PASSED [ 44%]
tests/test_invoke.py::test_fixed_probe_failure_is_safe_without_fallback PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_requests_structured_review_output_to_isolate_delegated_answers PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_always_disables_custom_instructions PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_always_disables_builtin_mcp_servers PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_names_no_vendor_specific_mcp_servers_by_default PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_extra_mcp_servers_can_be_disabled_by_the_caller PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_carries_the_prompt_and_the_model PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_empty_exclusions_preserve_the_exact_probe_command[None] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_empty_exclusions_preserve_the_exact_probe_command[servers1] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_empty_exclusions_preserve_the_exact_probe_command[servers2] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_probe_command_preserves_exclusions_and_caller_input PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_probe_models_forwards_exclusions_and_preserves_call_settings PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_failed_excluded_probe_keeps_diagnostic_and_prevents_review[CommandOutcome.COMPLETED-1-model rejected] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_failed_excluded_probe_keeps_diagnostic_and_prevents_review[CommandOutcome.TIMED_OUT-None-probe timed out] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_excluded_probes_preserve_partial_review_reporting PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_probes_every_model PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_a_rejected_model_is_reported_unavailable_with_its_reason PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_no_review_call_happens_before_every_probe_has_run PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_an_unavailable_model_is_never_asked_to_review PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_probing_no_models_returns_nothing_rather_than_failing PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_when_no_model_is_available_the_review_fails_loudly PASSED [ 45%]
tests/test_invoke.py::TestRepetition::test_calls_each_model_three_times_by_default PASSED [ 45%]
tests/test_invoke.py::TestRepetition::test_run_count_is_overridable PASSED [ 45%]
tests/test_invoke.py::TestRepetition::test_runs_of_one_model_are_byte_identical_calls PASSED [ 46%]
tests/test_invoke.py::TestRepetition::test_every_model_gets_the_same_number_of_runs PASSED [ 46%]
tests/test_invoke.py::TestRepetition::test_runs_are_numbered_from_one PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_a_timeout_is_a_recorded_outcome_not_a_raise PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_a_nonzero_exit_is_recorded_as_a_failed_run PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_one_failing_run_does_not_stop_the_others PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_response_text_is_kept_for_completed_runs PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_native_response_encoding_is_recorded_without_parsing_stdout PASSED [ 46%]
tests/test_invoke.py::TestPartialReviews::test_a_complete_review_is_not_partial PASSED [ 46%]
tests/test_invoke.py::TestPartialReviews::test_one_failed_run_out_of_six_makes_the_whole_review_partial PASSED [ 46%]
tests/test_invoke.py::TestPartialReviews::test_participation_states_completed_over_requested_per_model PASSED [ 46%]
tests/test_invoke.py::TestPartialReviews::test_usable_responses_are_offered_even_when_the_review_is_partial PASSED [ 46%]
tests/test_invoke.py::TestConcurrency::test_default_concurrency_is_the_measured_four PASSED [ 46%]
tests/test_invoke.py::TestConcurrency::test_never_exceeds_the_concurrency_limit PASSED [ 46%]
tests/test_invoke.py::TestConcurrency::test_calls_genuinely_overlap_rather_than_merely_staying_under_the_limit PASSED [ 46%]
tests/test_invoke.py::TestConcurrency::test_all_runs_complete_even_when_they_outnumber_the_workers PASSED [ 46%]
tests/test_invoke.py::TestReportingWhatFailed::test_unavailable_models_are_listed_with_their_reasons PASSED [ 47%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_missing_cli_is_reported_as_tool_missing_not_as_a_refusal PASSED [ 47%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_silent_failure_still_gets_a_reason PASSED [ 47%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_silent_timeout_is_named_by_its_outcome PASSED [ 47%]
tests/test_invoke.py::TestNonsensicalSettings::test_zero_runs_is_rejected_rather_than_reported_as_complete PASSED [ 47%]
tests/test_invoke.py::TestNonsensicalSettings::test_negative_runs_is_rejected PASSED [ 47%]
tests/test_invoke.py::TestNonsensicalSettings::test_zero_concurrency_is_rejected_rather_than_silently_corrected PASSED [ 47%]
tests/test_invoke.py::TestNonsensicalSettings::test_no_models_at_all_is_rejected PASSED [ 47%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_review_command_does_not_contain_the_prompt PASSED [ 47%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_command_length_stays_flat_as_the_prompt_grows PASSED [ 47%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_the_prompt_reaches_the_runner_as_stdin PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_the_default_window_is_three_lines PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_identical_lines_merge PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_nearby_lines_merge PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_lines_beyond_the_window_stay_separate PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_the_window_is_configurable PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_the_same_line_in_different_files_never_merges PASSED [ 48%]
tests/test_merge.py::TestGroupingByProximity::test_a_group_never_spans_more_than_the_window PASSED [ 48%]
tests/test_merge.py::TestGroupingByProximity::test_grouping_does_not_depend_on_the_order_findings_arrive_in PASSED [ 48%]
tests/test_merge.py::TestNothingIsDiscarded::test_every_message_survives_the_merge PASSED [ 48%]
tests/test_merge.py::TestNothingIsDiscarded::test_each_message_is_attributed_to_its_model_and_run PASSED [ 48%]
tests/test_merge.py::TestNothingIsDiscarded::test_each_message_keeps_the_line_it_was_reported_at PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_a_merged_finding_names_the_models_that_reported_it PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_agreement_counts_how_many_runs_of_each_model_reported_it PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_one_run_reporting_a_line_twice_counts_once PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_a_single_model_finding_is_reported_not_suppressed PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_a_finding_from_both_models_is_marked_corroborated PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_two_models_on_different_lines_of_one_group_is_not_corroboration PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_two_models_on_the_same_line_is_still_corroboration PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_agreement_on_one_line_survives_an_unrelated_line_joining_the_group PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_one_model_reporting_twice_on_a_line_is_not_corroboration PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_model_count_still_reports_every_model_in_the_group PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_a_single_line_group_from_two_models_is_unaffected PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_the_same_defect_at_adjacent_lines_is_reported_as_nearby PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_same_line_agreement_is_not_also_reported_as_nearby PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_agreement_on_one_line_wins_over_a_nearby_report PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_one_model_across_several_lines_is_neither_signal PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_a_lone_finding_is_neither_signal PASSED [ 49%]
tests/test_merge.py::TestSeverity::test_disagreeing_severities_are_all_preserved PASSED [ 49%]
tests/test_merge.py::TestSeverity::test_severity_is_not_collapsed_into_one_verdict PASSED [ 49%]
tests/test_merge.py::TestSeverity::test_agreement_on_severity_is_not_reported_as_disagreement PASSED [ 49%]
tests/test_merge.py::TestSeverity::test_the_highest_claimed_severity_is_available_for_ordering PASSED [ 49%]
tests/test_merge.py::TestOrdering::test_findings_are_ordered_by_highest_severity PASSED [ 49%]
tests/test_merge.py::TestOrdering::test_one_model_calling_it_critical_lifts_the_whole_finding PASSED [ 49%]
tests/test_merge.py::TestOrdering::test_equal_severities_are_ordered_predictably PASSED [ 49%]
tests/test_merge.py::TestKnownLimits::test_drift_lets_a_group_reach_further_than_the_window PASSED [ 49%]
tests/test_merge.py::TestEdges::test_severity_ordering_depends_on_the_allowed_list_staying_ordered PASSED [ 49%]
tests/test_merge.py::TestEdges::test_agreement_renders_as_the_fraction_a_report_shows PASSED [ 49%]
tests/test_merge.py::TestEdges::test_no_findings_merge_to_nothing PASSED [ 50%]
tests/test_merge.py::TestEdges::test_a_model_absent_from_the_run_counts_is_rejected PASSED [ 50%]
tests/test_merge.py::TestEdges::test_a_negative_window_is_rejected PASSED [ 50%]
tests/test_merge.py::TestEdges::test_a_zero_window_means_exact_line_matching PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_model_with_no_runs_cannot_have_reported_anything PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_model_that_completed_no_runs_is_allowed_to_report_nothing PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_negative_run_count_is_rejected PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_more_reporting_runs_than_runs_total_is_rejected PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_an_unrecognised_severity_names_what_is_allowed PASSED [ 50%]
tests/test_module_rules.py::test_capture_preserves_selected_order_and_original_bytes PASSED [ 50%]
tests/test_module_rules.py::test_capture_optional_sources_and_ignores_unselected_paths[sources0] PASSED [ 50%]
tests/test_module_rules.py::test_capture_optional_sources_and_ignores_unselected_paths[sources1] PASSED [ 50%]
tests/test_module_rules.py::test_capture_optional_sources_and_ignores_unselected_paths[sources2] PASSED [ 50%]
tests/test_module_rules.py::test_capture_optional_sources_and_ignores_unselected_paths[sources3] PASSED [ 50%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[] PASSED [ 50%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[ \r\n] PASSED [ 50%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[a\x00b] PASSED [ 50%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[\xff] PASSED [ 51%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[None] PASSED [ 51%]
tests/test_module_rules.py::test_capture_non_directory_guide_parent_is_not_absence[.atom] PASSED [ 51%]
tests/test_module_rules.py::test_capture_non_directory_guide_parent_is_not_absence[.atom/atom] PASSED [ 51%]
tests/test_module_rules.py::test_capture_non_directory_guide_parent_is_not_absence[.atom/atom/skills/atom/references] PASSED [ 51%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[outside] SKIPPED [ 51%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[dangling] SKIPPED [ 51%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[duplicate] SKIPPED [ 51%]
tests/test_module_rules.py::test_capture_read_failure_is_not_absence PASSED [ 51%]
tests/test_module_rules.py::test_capture_refuses_resolved_escape_before_read PASSED [ 51%]
tests/test_module_rules.py::test_capture_refuses_duplicate_resolved_targets PASSED [ 51%]
tests/test_module_rules.py::test_capture_dangling_source_is_not_absence PASSED [ 51%]
tests/test_module_rules.py::test_capture_unreadable_traversal_is_not_absence PASSED [ 51%]
tests/test_module_rules.py::test_capture_skip_modes_do_not_access_candidates[False-False-disabled] PASSED [ 51%]
tests/test_module_rules.py::test_capture_skip_modes_do_not_access_candidates[True-True-fixed-evidence] PASSED [ 51%]
tests/test_module_rules.py::test_capture_skip_modes_do_not_access_candidates[False-True-fixed-evidence] PASSED [ 51%]
tests/test_module_rules.py::test_review_delivers_frozen_guidance_to_every_run PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[hash] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[source] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[length] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[status] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[empty] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[fixed] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[duplicate] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[order] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags0-loaded] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags1-not-found] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags2-disabled] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags3-fixed-evidence] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags4-fixed-evidence] PASSED [ 52%]
tests/test_onboarding.py::test_init_records_the_makefile_commands_it_will_actually_run PASSED [ 52%]
tests/test_onboarding.py::test_init_records_a_partial_makefile_one_gate_at_a_time PASSED [ 52%]
tests/test_onboarding.py::test_init_infers_module_and_installs_local_instructions PASSED [ 53%]
tests/test_onboarding.py::test_init_skill_delegates_baseline_and_scaffold_to_one_cli_command PASSED [ 53%]
tests/test_onboarding.py::test_init_updates_existing_instructions_once PASSED [ 53%]
tests/test_onboarding.py::test_init_removes_legacy_external_atom_references PASSED [ 53%]
tests/test_onboarding.py::test_init_requires_module_when_go_mod_is_absent PASSED [ 53%]
tests/test_onboarding.py::test_init_ignores_only_generated_atom_runtime_files PASSED [ 53%]
tests/test_onboarding.py::test_init_preserves_existing_gitignore_and_updates_it_once PASSED [ 53%]
tests/test_onboarding.py::test_init_replaces_stale_atom_gitignore_block PASSED [ 53%]
tests/test_onboarding.py::test_init_preserves_existing_gitignore_newlines PASSED [ 53%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# >>> Atom generated runtime files >>>\n.atom/first.json\n# >>> Atom generated runtime files >>>\n.atom/second.json\n# <<< Atom generated runtime files <<<\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# >>> Atom generated runtime files >>>\n.atom/first.json\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# <<< Atom generated runtime files <<<\n.atom/first.json\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# <<< Atom generated runtime files <<<\n# >>> Atom generated runtime files >>>\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_separates_the_managed_block_without_changing_existing_content[vendor/-\n\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_separates_the_managed_block_without_changing_existing_content[vendor/\n\n-] PASSED [ 53%]
tests/test_onboarding.py::test_gitignore_update_keeps_original_when_atomic_replace_fails PASSED [ 53%]
tests/test_onboarding.py::test_init_reports_an_unreadable_gitignore_without_a_traceback PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_help_works_in_a_real_process PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_adds_commands_without_onboarding PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[exact] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[case] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[quoted] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[trailing-separator] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[dot] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[variable] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_unsupported_platform_without_io[linux] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_unsupported_platform_without_io[darwin] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_an_invalid_registry_value[C:\\keep-7] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_an_invalid_registry_value[value1-7] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_an_invalid_registry_value[123-1] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_creates_a_missing_user_path[key] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_creates_a_missing_user_path[value] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_reports_registry_permission_errors[OpenKey-read] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_registry_permission_errors[QueryValueEx-read] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_registry_permission_errors[CreateKeyEx-write] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_registry_permission_errors[SetValueEx-write] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_partial_notification_failure[timeout-False] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_partial_notification_failure[timeout-True] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_partial_notification_failure[os-error-False] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_partial_notification_failure[os-error-True] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_rejects_an_ambiguous_scripts_directory[semicolon] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_rejects_an_ambiguous_scripts_directory[nul] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_enforces_the_windows_utf16_length_limit[False-0] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_enforces_the_windows_utf16_length_limit[False-1] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_enforces_the_windows_utf16_length_limit[True-0] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_enforces_the_windows_utf16_length_limit[True-1] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_discovery_errors PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_requires_both_installed_console_scripts[atom.exe] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_requires_both_installed_console_scripts[atom-write-artifact.exe] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_requires_both_installed_console_scripts[not-a-file] PASSED [ 56%]
tests/test_pathsetup.py::test_setup_path_prefers_the_default_scheme_when_complete PASSED [ 56%]
tests/test_pathsetup.py::test_setup_path_changes_only_the_user_registry_value PASSED [ 56%]
tests/test_pathsetup.py::test_setup_path_uses_a_pointer_sized_environment_notification PASSED [ 56%]
tests/test_pathsetup.py::test_ordinary_init_does_not_opt_in_to_path_setup PASSED [ 56%]
tests/test_pathsetup.py::test_setup_path_prints_literal_powershell_executable_paths PASSED [ 56%]
tests/test_pathsetup.py::test_onboarding_documents_one_time_path_setup[relative0] PASSED [ 56%]
tests/test_pathsetup.py::test_onboarding_documents_one_time_path_setup[relative1] PASSED [ 56%]
tests/test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation PASSED [ 56%]
tests/test_phases.py::test_a_well_formed_phase_directory_is_recognised PASSED [ 56%]
tests/test_phases.py::test_a_single_digit_phase_number_is_not_a_phase_directory PASSED [ 56%]
tests/test_phases.py::test_an_uppercase_slug_is_not_a_phase_directory PASSED [ 56%]
tests/test_phases.py::test_a_directory_merely_containing_a_phase_name_is_not_one PASSED [ 56%]
tests/test_phases.py::test_a_file_named_like_a_phase_directory_is_not_one PASSED [ 56%]
tests/test_phases.py::test_a_non_phase_directory_is_ignored PASSED       [ 56%]
tests/test_phases.py::test_a_non_phase_directory_produces_no_problem PASSED [ 56%]
tests/test_phases.py::test_the_phase_plan_document_beside_the_phases_is_not_a_phase PASSED [ 57%]
tests/test_phases.py::test_phases_are_ordered_lexically PASSED           [ 57%]
tests/test_phases.py::test_the_two_digit_prefix_makes_lexical_order_numeric PASSED [ 57%]
tests/test_phases.py::test_phase_ten_sorts_after_phase_nine PASSED       [ 57%]
tests/test_phases.py::test_a_phase_branch_names_the_current_phase PASSED [ 57%]
tests/test_phases.py::test_the_branch_wins_over_the_lexically_greatest_phase PASSED [ 57%]
tests/test_phases.py::test_main_falls_back_to_the_lexically_greatest_phase PASSED [ 57%]
tests/test_phases.py::test_a_detached_head_falls_back_to_the_lexically_greatest_phase PASSED [ 57%]
tests/test_phases.py::test_an_unrelated_branch_name_falls_back PASSED    [ 57%]
tests/test_phases.py::test_a_branch_that_cannot_be_read_falls_back PASSED [ 57%]
tests/test_phases.py::test_a_branch_naming_a_missing_phase_directory_is_still_current PASSED [ 57%]
tests/test_phases.py::test_a_phase_with_no_directory_is_marked_not_started PASSED [ 57%]
tests/test_phases.py::test_a_phase_with_no_directory_reports_every_artifact_absent PASSED [ 57%]
tests/test_phases.py::test_a_phase_with_no_directory_is_not_an_error PASSED [ 57%]
tests/test_phases.py::test_a_project_with_no_phases_has_no_current_phase PASSED [ 57%]
tests/test_phases.py::test_a_project_with_no_phases_is_not_an_error PASSED [ 57%]
tests/test_phases.py::test_an_absent_specs_directory_is_not_a_crash PASSED [ 58%]
tests/test_phases.py::test_creating_an_artifact_in_an_old_phase_does_not_make_it_current PASSED [ 58%]
tests/test_phases.py::test_editing_an_artifact_in_an_old_phase_does_not_make_it_current PASSED [ 58%]
tests/test_phases.py::test_the_current_phase_is_stable_when_every_directory_is_touched_in_reverse_order PASSED [ 58%]
tests/test_phases.py::test_the_required_artifacts_are_the_seven_named PASSED [ 58%]
tests/test_phases.py::test_an_unexpected_file_in_a_phase_directory_is_not_required PASSED [ 58%]
tests/test_phases.py::test_an_unexpected_file_does_not_appear_in_the_artifact_report PASSED [ 58%]
tests/test_phases.py::test_an_existing_artifact_is_present PASSED        [ 58%]
tests/test_phases.py::test_a_missing_artifact_is_absent PASSED           [ 58%]
tests/test_phases.py::test_an_empty_artifact_file_is_still_present PASSED [ 58%]
tests/test_phases.py::test_a_directory_named_like_an_artifact_is_not_present PASSED [ 58%]
tests/test_phases.py::test_the_artifact_report_has_exactly_two_states PASSED [ 58%]
tests/test_phases.py::test_a_one_byte_artifact_is_present PASSED         [ 58%]
tests/test_phases.py::test_a_document_with_no_headings_is_present PASSED [ 58%]
tests/test_phases.py::test_a_document_of_only_headings_is_present PASSED [ 58%]
tests/test_phases.py::test_no_artifact_but_the_poc_report_is_ever_opened PASSED [ 58%]
tests/test_phases.py::test_a_ran_poc_requires_a_brief PASSED             [ 59%]
tests/test_phases.py::test_a_skipped_poc_does_not_require_a_brief PASSED [ 59%]
tests/test_phases.py::test_a_skipped_phase_with_no_brief_is_complete PASSED [ 59%]
tests/test_phases.py::test_a_skipped_phase_requires_the_other_six PASSED [ 59%]
tests/test_phases.py::test_an_unrecognised_status_is_reported_as_a_problem PASSED [ 59%]
tests/test_phases.py::test_an_unrecognised_status_still_requires_the_brief PASSED [ 59%]
tests/test_phases.py::test_a_missing_status_field_is_reported_and_requires_the_brief PASSED [ 59%]
tests/test_phases.py::test_the_unrecognised_status_problem_names_the_value_it_found PASSED [ 59%]
tests/test_phases.py::test_an_absent_poc_report_makes_both_it_and_the_brief_absent PASSED [ 59%]
tests/test_phases.py::test_an_absent_poc_report_raises_no_problem_beyond_the_absences PASSED [ 59%]
tests/test_phases.py::test_a_phase_with_no_poc_report_still_requires_the_brief PASSED [ 59%]
tests/test_phases.py::test_the_status_vocabulary_is_exactly_two_tokens PASSED [ 59%]
tests/test_phases.py::test_a_status_containing_skipped_as_a_substring_is_not_skipped PASSED [ 59%]
tests/test_phases.py::test_the_prose_status_values_this_repo_used_before_are_not_accepted PASSED [ 59%]
tests/test_phases.py::test_status_matching_is_case_sensitive PASSED      [ 59%]
tests/test_phases.py::test_an_unquoted_status_is_recognised PASSED       [ 59%]
tests/test_phases.py::test_a_truncated_design_spec_is_reported_present PASSED [ 60%]
tests/test_phases.py::test_no_rendering_describes_any_artifact_as_complete PASSED [ 60%]
tests/test_phases.py::test_the_report_exposes_no_completeness_field PASSED [ 60%]
tests/test_phases.py::test_a_two_section_tdd_log_is_present PASSED       [ 60%]
tests/test_phases.py::test_the_real_phase_one_tdd_log_is_present PASSED  [ 60%]
tests/test_phases.py::test_the_real_repository_resolves_eight_phases PASSED [ 60%]
tests/test_phases.py::test_the_real_repository_orders_phases_one_through_eight PASSED [ 60%]
tests/test_phases.py::test_phases_one_through_five_have_every_required_artifact PASSED [ 60%]
tests/test_phases.py::test_the_real_phase_one_is_complete_despite_having_no_brief PASSED [ 60%]
tests/test_phases.py::test_the_real_phase_six_is_missing_exactly_its_unwritten_artifacts PASSED [ 60%]
tests/test_phases.py::test_a_real_detached_head_falls_back_to_lexical PASSED [ 60%]
tests/test_phases.py::test_a_real_phase_branch_resolves_to_its_directory PASSED [ 60%]
tests/test_phases.py::test_a_real_clone_preserves_phase_ordering PASSED  [ 60%]
tests/test_phases.py::test_a_problem_in_a_non_current_phase_is_still_reported PASSED [ 60%]
tests/test_phases.py::test_a_reported_problem_names_the_phase_it_came_from PASSED [ 60%]
tests/test_phases.py::test_problems_are_reported_in_phase_order PASSED   [ 60%]
tests/test_phases.py::test_the_current_phase_problem_is_reported_exactly_once PASSED [ 60%]
tests/test_phases.py::test_a_clean_tree_still_reports_no_problems PASSED [ 61%]
tests/test_plugin.py::test_the_plugin_manifest_declares_agent_plugins_1_0 PASSED [ 61%]
tests/test_plugin.py::test_the_plugin_manifest_uses_only_allowed_fields PASSED [ 61%]
tests/test_plugin.py::test_no_command_shares_a_name_with_a_skill PASSED  [ 61%]
tests/test_plugin.py::test_the_plugin_owns_the_atom_command_namespace PASSED [ 61%]
tests/test_plugin.py::test_no_command_shares_a_name_with_the_plugin PASSED [ 61%]
tests/test_plugin.py::test_the_atom_router_is_available_as_start PASSED  [ 61%]
tests/test_plugin.py::test_no_skill_shares_a_name_with_the_plugin PASSED [ 61%]
tests/test_plugin.py::test_the_plugin_exposes_exactly_the_compact_skill_names PASSED [ 61%]
tests/test_plugin.py::test_the_marketplace_lists_the_plugin_by_its_manifest_name PASSED [ 61%]
tests/test_plugin.py::test_the_marketplace_sources_the_repository_root PASSED [ 61%]
tests/test_plugin.py::test_every_atom_skill_directory_is_discoverable PASSED [ 61%]
tests/test_pr_checkout_integration.py::test_real_git_merge_base_and_dirty_original_preserved PASSED [ 61%]
tests/test_pr_checkout_integration.py::test_native_cli_uses_real_checkout_and_cleans_it PASSED [ 61%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[] PASSED [ 61%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[not a URL] PASSED [ 61%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[http://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com.attacker.test/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com:443/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://user:password@dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/other%2fproject/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/other%5cproject/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/%2e%2e/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/%00/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/bad%zz/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/project/_git/repository/pullrequest/0] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/project/_git/repository/pullrequest/-1] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/project/_git/repository/pullrequest/42/extra] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/project/_git/repository/pullrequest/42\n] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[ https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TOOL_MISSING-None-https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TOOL_MISSING-None-https://dev.azure.com/example/project/_git/repository/pullrequest/42?_a=files#discussion] PASSED [ 62%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TOOL_MISSING-None-https://example.visualstudio.com/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TIMED_OUT-None-https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TIMED_OUT-None-https://dev.azure.com/example/project/_git/repository/pullrequest/42?_a=files#discussion] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TIMED_OUT-None-https://example.visualstudio.com/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.RUNNER_ERROR-0-https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.RUNNER_ERROR-0-https://dev.azure.com/example/project/_git/repository/pullrequest/42?_a=files#discussion] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.RUNNER_ERROR-0-https://example.visualstudio.com/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.COMPLETED-1-https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.COMPLETED-1-https://dev.azure.com/example/project/_git/repository/pullrequest/42?_a=files#discussion] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.COMPLETED-1-https://example.visualstudio.com/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change0] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change1] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change2] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change3] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change4] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change5] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change6] PASSED [ 64%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change7] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone[{] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone[[]] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone[null] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone[{}] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone["text"] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://user:password@dev.azure.com/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://someone@dev.azure.com/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://example@attacker.test/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://example@dev.azure.com/example/project/_git/different] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://example@dev.azure.com:444/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://example@dev.azure.com/example/project/_git/repository\n] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[ https://example@dev.azure.com/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_local_scope_is_required[missing module] PASSED [ 64%]
tests/test_pull_request.py::test_local_scope_is_required[wrong origin] PASSED [ 64%]
tests/test_pull_request.py::test_local_scope_is_required[ssh origin] PASSED [ 65%]
tests/test_pull_request.py::test_local_scope_is_required[outside root] PASSED [ 65%]
tests/test_pull_request.py::test_clone_failure_is_cleaned PASSED         [ 65%]
tests/test_pull_request.py::test_independent_clone_and_pinned_checkout PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command0-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb-0-source moved] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command1-invalid-0-commit ID] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command2--0-exactly one] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command3-cccccccccccccccccccccccccccccccccccccccc\nbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb-0-exactly one] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command4--1-checking out] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command5-missing.go\x00-0-missing tracked] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command6-dirty-1-clean pinned] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_on_failure_and_interrupt[failure0] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_on_failure_and_interrupt[failure1] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_failure_preserves_primary_error[False] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_failure_preserves_primary_error[True] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_interruption_names_retained_directory PASSED [ 65%]
tests/test_pull_request.py::test_repository_package_cannot_shadow_cleanup_worker PASSED [ 65%]
tests/test_pull_request.py::test_percent_encoded_names_keep_their_metadata_scope[False] PASSED [ 66%]
tests/test_pull_request.py::test_percent_encoded_names_keep_their_metadata_scope[True] PASSED [ 66%]
tests/test_pull_request.py::test_zero_exit_with_lifecycle_error_is_not_a_snapshot[stage0] PASSED [ 66%]
tests/test_pull_request.py::test_zero_exit_with_lifecycle_error_is_not_a_snapshot[stage1] PASSED [ 66%]
tests/test_pull_request.py::test_cleanup_worker_checks_ownership_and_handles_readonly_files[False] PASSED [ 66%]
tests/test_pull_request.py::test_cleanup_worker_checks_ownership_and_handles_readonly_files[True] PASSED [ 66%]
tests/test_pull_request.py::test_cleanup_success_exit_still_requires_path_absence PASSED [ 66%]
tests/test_pull_request.py::test_pr_module_must_still_have_go_mod_file PASSED [ 66%]
tests/test_report.py::test_render_text_shows_every_gate_with_status_and_duration PASSED [ 66%]
tests/test_report.py::test_render_text_shows_details_for_failed_gates_only PASSED [ 66%]
tests/test_report.py::test_render_text_omits_details_for_passing_gates PASSED [ 66%]
tests/test_report.py::test_render_text_includes_warnings PASSED          [ 66%]
tests/test_report.py::test_render_text_without_colour_emits_no_escape_codes PASSED [ 66%]
tests/test_report.py::test_render_text_with_colour_emits_escape_codes PASSED [ 66%]
tests/test_report.py::test_render_json_is_valid_json_for_a_passing_report PASSED [ 66%]
tests/test_report.py::test_render_json_is_valid_json_for_a_failing_report PASSED [ 66%]
tests/test_report.py::test_render_json_includes_a_schema_version PASSED  [ 67%]
tests/test_report.py::test_render_json_includes_every_gate_with_its_evidence PASSED [ 67%]
tests/test_report.py::test_a_spike_that_answered_is_not_rendered_as_a_failed_stage PASSED [ 67%]
tests/test_report.py::test_an_answering_stage_says_it_answered_rather_than_that_it_exited PASSED [ 67%]
tests/test_report.py::test_a_refuted_spike_is_not_rendered_as_a_failure_either PASSED [ 67%]
tests/test_report.py::test_a_crashed_spike_is_still_rendered_as_a_failure PASSED [ 67%]
tests/test_report.py::test_a_crash_explains_that_exit_2_was_a_panic_not_a_verdict PASSED [ 67%]
tests/test_report.py::test_the_spike_output_is_shown_even_when_nothing_failed PASSED [ 67%]
tests/test_report.py::test_json_reports_no_failed_stage_for_a_spike_that_answered PASSED [ 67%]
tests/test_report.py::test_json_exposes_answered_separately_from_ran PASSED [ 67%]
tests/test_report.py::test_stderr_is_rendered_before_stdout PASSED       [ 67%]
tests/test_review_formatting.py::test_clean_changed_file_is_not_blocked_by_untouched_formatting PASSED [ 67%]
tests/test_review_formatting.py::test_fixed_evidence_keeps_changed_file_formatting_and_one_diff_capture PASSED [ 67%]
tests/test_review_formatting.py::test_staged_formatting_uses_index_snapshot_not_working_file[clean-index-dirty-worktree] PASSED [ 67%]
tests/test_review_formatting.py::test_staged_formatting_uses_index_snapshot_not_working_file[dirty-index-clean-worktree] PASSED [ 67%]
tests/test_review_formatting.py::test_staged_formatting_uses_index_snapshot_not_working_file[worktree-file-absent] PASSED [ 67%]
tests/test_review_formatting.py::test_branch_formatting_uses_committed_content_despite_dirty_working_file PASSED [ 68%]
tests/test_review_formatting.py::test_pure_rename_formats_destination_and_preserves_canonical_diff_path PASSED [ 68%]
tests/test_review_formatting.py::test_no_surviving_go_files_skips_formatter_with_explicit_scope[empty] PASSED [ 68%]
tests/test_review_formatting.py::test_no_surviving_go_files_skips_formatter_with_explicit_scope[non-go] PASSED [ 68%]
tests/test_review_formatting.py::test_no_surviving_go_files_skips_formatter_with_explicit_scope[deleted] PASSED [ 68%]
tests/test_review_formatting.py::test_module_boundary_exclusions_are_explicit_without_checking_other_modules PASSED [ 68%]
tests/test_review_formatting.py::test_prompt_names_selected_formatting_scope_without_claiming_module_scan[True] PASSED [ 68%]
tests/test_review_formatting.py::test_prompt_names_selected_formatting_scope_without_claiming_module_scan[False] PASSED [ 68%]
tests/test_review_formatting.py::test_non_regular_selected_go_entry_is_refused_before_formatter_or_models PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[parent-path] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[absolute-path] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[windows-path] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[unmerged] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[unknown-status] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[bad-mode] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[bad-identity] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_utf8_is_required_formatting_failure_not_replacement_success[DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_invalid_utf8_is_required_formatting_failure_not_replacement_success[DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_working_file_substituted_with_non_regular_path_is_not_read PASSED [ 69%]
tests/test_review_formatting.py::test_added_and_renamed_go_paths_use_nul_delimited_canonical_names[added] PASSED [ 69%]
tests/test_review_formatting.py::test_added_and_renamed_go_paths_use_nul_delimited_canonical_names[renamed-from-text] PASSED [ 69%]
tests/test_review_formatting.py::test_added_and_renamed_go_paths_use_nul_delimited_canonical_names[unicode-space] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[crlf-DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[crlf-DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[mixed-endings-DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[mixed-endings-DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[crlf-real-formatting-defect-DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[crlf-real-formatting-defect-DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[utf8-DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[utf8-DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[missing] PASSED [ 69%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[timeout] PASSED [ 69%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[runner-error] PASSED [ 70%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[syntax-error] PASSED [ 70%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[empty-stdout] PASSED [ 70%]
tests/test_review_formatting.py::test_working_file_movement_after_diff_capture_blocks_models PASSED [ 70%]
tests/test_review_formatting.py::test_snapshot_acquisition_and_blob_transport_fail_closed[git-failure] PASSED [ 70%]
tests/test_review_formatting.py::test_snapshot_acquisition_and_blob_transport_fail_closed[blob-read-failure] PASSED [ 70%]
tests/test_review_formatting.py::test_snapshot_acquisition_and_blob_transport_fail_closed[bad-base64] PASSED [ 70%]
tests/test_review_formatting.py::test_snapshot_acquisition_and_blob_transport_fail_closed[wrong-blob] PASSED [ 70%]
tests/test_review_formatting.py::test_cli_reports_selected_file_formatting_coverage[False] PASSED [ 70%]
tests/test_review_formatting.py::test_cli_reports_selected_file_formatting_coverage[True] PASSED [ 70%]
tests/test_review_formatting.py::test_non_go_type_change_does_not_break_changed_go_snapshot_pairing PASSED [ 70%]
tests/test_review_formatting.py::test_non_format_required_gate_commands_and_failures_remain_unchanged[failing_command0] PASSED [ 70%]
tests/test_review_formatting.py::test_non_format_required_gate_commands_and_failures_remain_unchanged[failing_command1] PASSED [ 70%]
tests/test_review_formatting.py::test_non_format_required_gate_commands_and_failures_remain_unchanged[failing_command2] PASSED [ 70%]
tests/test_review_formatting.py::test_non_format_required_gate_commands_and_failures_remain_unchanged[failing_command3] PASSED [ 70%]
tests/test_review_formatting.py::test_whole_changed_file_defect_blocks_even_when_other_snapshot_is_clean[DiffSource.WORKING] PASSED [ 70%]
tests/test_review_formatting.py::test_whole_changed_file_defect_blocks_even_when_other_snapshot_is_clean[DiffSource.STAGED] PASSED [ 70%]
tests/test_review_formatting.py::test_whole_changed_file_defect_blocks_even_when_other_snapshot_is_clean[DiffSource.BRANCH] PASSED [ 71%]
tests/test_review_formatting.py::test_captured_content_is_reused_when_checks_change_working_tree PASSED [ 71%]
tests/test_review_formatting.py::test_invalid_branch_ref_fails_before_checks_or_models PASSED [ 71%]
tests/test_review_formatting.py::test_untracked_go_file_is_not_added_to_working_diff_scope PASSED [ 71%]
tests/test_review_formatting.py::test_submodule_display_config_cannot_change_manifest_patch_framing[log] PASSED [ 71%]
tests/test_review_formatting.py::test_submodule_display_config_cannot_change_manifest_patch_framing[diff] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[non-go-:] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[non-go-\\] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[deleted-:] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[deleted-\\] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[outside-module-:] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[outside-module-\\] PASSED [ 71%]
tests/test_review_output.py::test_direct_context_requires_opt_in_before_runner PASSED [ 71%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes0] PASSED [ 71%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes1] PASSED [ 71%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes2] PASSED [ 71%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes3] PASSED [ 72%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes4] PASSED [ 72%]
tests/test_review_output.py::test_fixed_prompt_freezes_json_documents_and_preserves_diff PASSED [ 72%]
tests/test_review_output.py::test_fixed_evidence_keeps_diff_file_guard PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_names_every_model_that_took_part PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_states_how_many_runs_each_model_completed PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_describes_the_diff_that_was_reviewed PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_a_model_that_failed_every_run_is_still_named PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_an_unavailable_model_is_named_but_its_error_text_is_not_repeated PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_responses_nobody_could_parse_are_reported PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_findings_are_grouped_under_their_file PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_a_single_line_finding_shows_that_line PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_a_finding_spanning_several_lines_shows_the_span PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_no_bare_finding_count_is_printed PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_every_model_message_is_shown_with_its_author PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_the_report_lists_toolchain_verdicts PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_agreement_is_shown_as_a_fraction_per_model PASSED [ 73%]
tests/test_review_output.py::TestFindingPresentation::test_disagreement_about_severity_is_visible PASSED [ 73%]
tests/test_review_output.py::TestFindingPresentation::test_findings_appear_in_severity_order PASSED [ 73%]
tests/test_review_output.py::TestFindingPresentation::test_a_review_with_no_findings_says_so_explicitly PASSED [ 73%]
tests/test_review_output.py::TestPartialReviews::test_a_partial_review_is_marked_partial_in_markdown PASSED [ 73%]
tests/test_review_output.py::TestPartialReviews::test_a_complete_review_is_not_marked_partial PASSED [ 73%]
tests/test_review_output.py::TestPartialReviews::test_a_partial_review_is_marked_partial_in_json PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_is_valid_and_carries_a_schema_version PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_review_schema_version_records_the_corroboration_narrowing PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_other_reports_did_not_change_and_keep_their_version PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_findings_with_their_line_span PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_agreement_with_both_halves_of_the_fraction PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_keeps_every_attributed_message PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_names_models_that_produced_nothing PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_unparseable_responses PASSED [ 73%]
tests/test_review_output.py::TestChannelSeparation::test_operational_problems_render_separately_from_the_report PASSED [ 73%]
tests/test_review_output.py::TestChannelSeparation::test_a_clean_review_produces_no_problem_output PASSED [ 74%]
tests/test_review_output.py::TestChannelSeparation::test_the_markdown_report_does_not_repeat_the_problem_text PASSED [ 74%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_knows_it_is_partial_when_a_run_failed PASSED [ 74%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_with_every_run_answered_is_not_partial PASSED [ 74%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_knows_when_no_model_produced_anything_usable PASSED [ 74%]
tests/test_review_output.py::TestReviewOutcome::test_a_review_that_ran_but_found_nothing_is_not_treated_as_unusable PASSED [ 74%]
tests/test_review_output.py::TestAnUnreadableReplyIsNotACleanReview::test_a_completed_run_whose_reply_was_unreadable_yields_no_usable_response PASSED [ 74%]
tests/test_review_output.py::TestAnUnreadableReplyIsNotACleanReview::test_such_a_review_does_not_exit_zero PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unreadable_reply_is_left_out_of_the_denominator PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_finding_both_readable_runs_reported_is_not_shown_as_a_dissent PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_completed_without_answering_makes_the_review_partial PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_partial_notice_counts_the_run_that_could_not_be_read PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_payload_reports_answered_runs_alongside_completed_ones PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_that_partly_parsed_still_counts_as_an_answer PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_clean_review_still_counts_every_run_and_is_not_partial PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_model_whose_every_reply_was_unreadable_renders_without_crashing PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_missing_run_is_still_partial PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[   \n\t ] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[I reviewed it and found nothing.] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_returned_nothing_is_named_in_the_report PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[file-guard only] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[schema-invalid] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[mixed] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unreadable_reply_is_not_named_twice PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_answered_is_never_also_counted_as_overruled PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_answered_despite_a_malformed_element_is_not_called_unreadable PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_is_not_called_a_review_that_produced_nothing PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_gets_its_own_heading PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_partial_total_excludes_an_overruled_reply PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_banner_does_not_promise_stderr_detail PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_payload_distinguishes_an_overruled_reply_from_an_unreadable_one PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_overruled_by_the_file_guard_does_not_make_the_review_partial PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_still_leaves_the_denominator PASSED [ 76%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unparseable_reply_is_still_silence PASSED [ 76%]
tests/test_review_output.py::TestTheReportSurvivesEveryConsoleEncoding::test_rendered_markdown_is_pure_ascii PASSED [ 76%]
tests/test_review_toolchain.py::test_empty_toolchain_placeholder_preserves_original_prompt_bytes PASSED [ 76%]
tests/test_review_toolchain.py::test_run_review_blocks_before_models_when_required_gate_fails[False] PASSED [ 76%]
tests/test_review_toolchain.py::test_run_review_blocks_before_models_when_required_gate_fails[True] PASSED [ 76%]
tests/test_review_toolchain.py::test_run_review_continues_with_no_exclusions_when_directory_is_not_go_module PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_review_uses_selected_gates PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_makefile_stops_before_probes[build] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_makefile_stops_before_probes[test] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_runner_refuses_delegation_added_after_preflight PASSED [ 76%]
tests/test_review_toolchain.py::test_unexecuted_pin_retains_intent_without_observations[configured-skip] PASSED [ 76%]
tests/test_review_toolchain.py::test_unexecuted_pin_retains_intent_without_observations[no-module] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments0-CommandOutcome.COMPLETED-1-go.mod requires go >= 1.27.0] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments1-CommandOutcome.COMPLETED-1-undefined: missingSymbol] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments2-CommandOutcome.COMPLETED-1-WARNING: DATA RACE] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments3-CommandOutcome.TOOL_MISSING-None-required tool is missing] PASSED [ 77%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments4-CommandOutcome.COMPLETED-2-unknown compiler problem] PASSED [ 77%]
tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[replaced-go] PASSED [ 77%]
tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[replaced-gofmt] PASSED [ 77%]
tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[deleted-go] PASSED [ 77%]
tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[deleted-gofmt] PASSED [ 77%]
tests/test_review_toolchain.py::test_pinned_evidence_is_consistent_across_outputs[False] PASSED [ 77%]
tests/test_review_toolchain.py::test_pinned_evidence_is_consistent_across_outputs[True] PASSED [ 77%]
tests/test_review_toolchain.py::test_unconfigured_review_preserves_legacy_evidence PASSED [ 77%]
tests/test_review_toolchain.py::test_advisory_commands_receive_environment_only_scope PASSED [ 77%]
tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [ 77%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[False] PASSED [ 77%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[True] PASSED [ 77%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[False] PASSED [ 77%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[True] PASSED [ 77%]
tests/test_runner.py::test_windows_child_path_diagnostic_names_shadowed_copy PASSED [ 77%]
tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext PASSED [ 78%]
tests/test_runner.py::test_environment_is_copied_before_launch PASSED    [ 78%]
tests/test_runner.py::test_concurrent_child_environments_do_not_leak_into_base_calls PASSED [ 78%]
tests/test_runner.py::test_empty_environment_does_not_inherit_parent_settings PASSED [ 78%]
tests/test_runner.py::test_posix_launch_errors_are_failed_command_evidence[error0] PASSED [ 78%]
tests/test_runner.py::test_posix_launch_errors_are_failed_command_evidence[error1] PASSED [ 78%]
tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape PASSED [ 78%]
tests/test_runner.py::test_command_result_succeeded_only_for_completed_zero PASSED [ 78%]
tests/test_runner.py::test_command_result_combined_output_preserves_both_streams PASSED [ 78%]
tests/test_runner.py::test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately PASSED [ 78%]
tests/test_runner.py::test_subprocess_runner_returns_timed_out_without_raising PASSED [ 78%]
tests/test_runner.py::test_subprocess_runner_returns_tool_missing_without_raising PASSED [ 78%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_absent_tool_is_reported_as_missing_from_path PASSED [ 78%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_unlaunchable_path_entry_is_not_blamed_on_path PASSED [ 78%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_a_working_copy_hidden_behind_the_broken_one_is_named PASSED [ 78%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_missing_working_directory_is_not_blamed_on_the_tool PASSED [ 78%]
tests/test_runner.py::TestStdinIsNeverInherited::test_a_child_reading_stdin_sees_end_of_input_immediately PASSED [ 79%]
tests/test_runner.py::TestStdinIsNeverInherited::test_supplied_text_reaches_the_child PASSED [ 79%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[False] PASSED [ 79%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[True] PASSED [ 79%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_output_written_before_the_kill_is_still_returned PASSED [ 79%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_the_reported_duration_matches_the_time_actually_spent PASSED [ 79%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 79%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [ 79%]
tests/test_scaffold.py::test_scaffold_creates_exactly_three_files PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_shells_out_to_go_mod_init PASSED   [ 79%]
tests/test_scaffold.py::test_scaffold_go_mod_pins_full_patch_version PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_module_path_is_namespaced_under_spike PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_rolls_back_completely_when_go_mod_init_fails PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_rollback_leaves_sibling_spikes_untouched PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_main_go_is_package_main_with_a_main_function PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_main_go_prints_the_question PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_main_go_documents_the_exit_code_convention PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_readme_has_the_report_sections PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_readme_records_the_question PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[Json-Streaming] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[json_streaming] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[json streaming] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[-leading] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[trailing-] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[double--hyphen] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[] PASSED    [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[../escape] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[json] PASSED   [ 80%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[json-streaming] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[http2-vs-http3] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[a1] PASSED     [ 80%]
tests/test_scaffold.py::test_scaffold_slug_error_explains_the_rule PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_refuses_to_overwrite_an_existing_spike PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_does_not_modify_an_existing_spike_when_refusing PASSED [ 81%]
tests/test_scaffold.py::test_scaffold_creates_poc_root_when_missing PASSED [ 81%]
tests/test_scaffold.py::test_scaffold_reports_every_file_it_created PASSED [ 81%]
tests/test_ship.py::TestGhPrecondition::test_a_missing_gh_is_an_unmet_precondition_not_a_late_failure PASSED [ 81%]
tests/test_ship.py::TestGhPrecondition::test_gh_is_verified_before_any_git_work_begins PASSED [ 81%]
tests/test_ship.py::TestGhPrecondition::test_the_missing_gh_message_names_the_install PASSED [ 81%]
tests/test_ship.py::TestBranchPreconditions::test_a_detached_head_has_nothing_to_ship_from PASSED [ 81%]
tests/test_ship.py::TestBranchPreconditions::test_shipping_the_base_branch_itself_is_refused PASSED [ 81%]
tests/test_ship.py::TestDirtyTree::test_a_dirty_working_tree_is_refused PASSED [ 81%]
tests/test_ship.py::TestDirtyTree::test_the_dirty_tree_refusal_lists_the_modified_files PASSED [ 81%]
tests/test_ship.py::TestDirtyTree::test_a_clean_tree_is_allowed_to_proceed PASSED [ 81%]
tests/test_ship.py::TestUpstream::test_a_branch_with_no_upstream_and_no_push_is_refused PASSED [ 81%]
tests/test_ship.py::TestUpstream::test_the_missing_upstream_refusal_prints_the_command_that_fixes_it PASSED [ 81%]
tests/test_ship.py::TestUpstream::test_the_push_flag_pushes_the_branch_and_sets_the_upstream PASSED [ 81%]
tests/test_ship.py::TestUpstream::test_the_push_is_a_git_command_never_gh PASSED [ 81%]
tests/test_ship.py::TestPhaseResolution::test_the_phase_directory_is_derived_from_the_branch_name PASSED [ 81%]
tests/test_ship.py::TestPhaseResolution::test_the_phase_flag_overrides_the_branch_derivation PASSED [ 82%]
tests/test_ship.py::TestPhaseResolution::test_a_missing_phase_directory_is_refused_naming_the_path_it_tried PASSED [ 82%]
tests/test_ship.py::TestPhaseResolution::test_the_artifacts_are_the_files_the_phase_directory_holds PASSED [ 82%]
tests/test_ship.py::TestPhaseResolution::test_a_missing_artifact_is_omitted_rather_than_described_as_pending PASSED [ 82%]
tests/test_ship.py::TestFreshCheck::test_the_check_runs_fresh_as_part_of_ship PASSED [ 82%]
tests/test_ship.py::TestFreshCheck::test_a_recorded_check_result_is_not_accepted PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_skips_the_gates PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_the_absent_module_is_recorded_as_an_absence_not_a_failure PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_does_not_trigger_the_check_refusal PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_needs_no_allow_failing_checks_flag PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_the_evidence_section_states_the_absence_rather_than_omitting_it PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_the_body_carries_one_verdict_row_per_gate PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_the_verdict_table_is_bounded_at_five_rows PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_the_body_does_not_embed_the_gates_full_output PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_when_there_is_no_module_the_table_is_replaced_by_the_recorded_line PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_the_recorded_line_replaces_the_table_it_does_not_leave_the_section_empty PASSED [ 82%]
tests/test_ship.py::TestCheckRefusal::test_a_failing_check_refuses_to_open_or_update_the_pr PASSED [ 83%]
tests/test_ship.py::TestCheckRefusal::test_the_check_refusal_names_the_failing_gates PASSED [ 83%]
tests/test_ship.py::TestCheckRefusal::test_allow_failing_checks_overrides_the_refusal PASSED [ 83%]
tests/test_ship.py::TestCheckRefusal::test_a_failing_gate_in_a_real_go_module_is_still_refused_not_excused_as_absent PASSED [ 83%]
tests/test_ship.py::TestOverride::test_an_overridden_run_states_the_failure_in_the_body PASSED [ 83%]
tests/test_ship.py::TestOverride::test_an_overridden_body_never_asserts_green_while_red PASSED [ 83%]
tests/test_ship.py::TestOverride::test_an_overridden_run_still_exits_non_zero PASSED [ 83%]
tests/test_ship.py::TestBody::test_the_body_is_summary_plus_links PASSED [ 83%]
tests/test_ship.py::TestBody::test_the_body_never_embeds_an_artifacts_content PASSED [ 83%]
tests/test_ship.py::TestBody::test_the_body_title_comes_from_the_design_specs_h1 PASSED [ 83%]
tests/test_ship.py::TestBody::test_a_title_flag_overrides_the_design_spec_h1 PASSED [ 83%]
tests/test_ship.py::TestBody::test_the_body_quotes_the_design_specs_purpose_paragraph PASSED [ 83%]
tests/test_ship.py::TestBody::test_what_changed_lists_the_commit_subjects_on_the_branch PASSED [ 83%]
tests/test_ship.py::TestArtifactLinks::test_artifact_links_point_at_the_pushed_commit_sha PASSED [ 83%]
tests/test_ship.py::TestArtifactLinks::test_no_artifact_link_uses_a_branch_name PASSED [ 83%]
tests/test_ship.py::TestArtifactLinks::test_no_artifact_link_points_at_the_base_branch PASSED [ 83%]
tests/test_ship.py::TestArtifactLinks::test_the_push_happens_before_the_body_is_assembled PASSED [ 84%]
tests/test_ship.py::TestBodyFile::test_the_body_file_contains_no_carriage_return PASSED [ 84%]
tests/test_ship.py::TestBodyFile::test_the_reported_size_is_the_character_count_not_the_byte_count PASSED [ 84%]
tests/test_ship.py::TestBodyFile::test_the_body_travels_by_body_file PASSED [ 84%]
tests/test_ship.py::TestBodyFile::test_the_body_flag_never_appears_in_the_argv PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_an_existing_pr_is_queried_before_any_create PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_the_duplicate_error_is_treated_as_a_fallback_not_the_primary_signal PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_the_duplicate_error_still_recovers_when_the_query_missed_it PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_re_running_on_a_branch_with_a_pr_updates_the_body PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_re_running_is_not_treated_as_an_error PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_ghs_error_text_is_passed_through_verbatim PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_every_gh_call_receives_empty_stdin PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_ship_reuses_the_phase_one_to_three_exit_codes PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_an_unmet_precondition_exits_by_the_ordinary_failure_route PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_there_is_no_distinct_precondition_exit_code PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_ship_never_issues_a_commit PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_no_git_commit_command_is_ever_run PASSED [ 85%]
tests/test_ship.py::TestOutcomeShape::test_a_clean_run_reports_succeeded PASSED [ 85%]
tests/test_ship.py::TestOutcomeShape::test_an_overridden_run_reports_not_succeeded PASSED [ 85%]
tests/test_ship.py::TestOutcomeShape::test_a_created_pr_reports_the_created_action_and_url PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_an_unreadable_branch_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_an_unreadable_status_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_failed_push_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_an_unresolvable_head_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_missing_origin_remote_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_failed_log_leaves_the_what_changed_section_empty_not_fatal PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_failed_edit_is_refused_with_ghs_text PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_create_failure_with_no_output_still_refuses PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_create_success_without_a_url_falls_back_to_raw_stdout PASSED [ 85%]
tests/test_ship.py::TestPhaseResolutionEdges::test_a_direct_relative_path_resolves_the_phase PASSED [ 85%]
tests/test_ship.py::TestPhaseResolutionEdges::test_an_ambiguous_phase_name_is_refused PASSED [ 85%]
tests/test_ship.py::TestPhaseResolutionEdges::test_an_artifact_outside_the_repo_root_keeps_its_full_path PASSED [ 85%]
tests/test_ship.py::TestBareTitleAndSlug::test_the_title_falls_back_to_the_branch_when_no_design_spec PASSED [ 85%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_design_spec_without_an_h1_falls_back_to_the_branch_title PASSED [ 86%]
tests/test_ship.py::TestBareTitleAndSlug::test_an_ssh_remote_url_yields_the_owner_name_slug PASSED [ 86%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_pr_view_with_empty_output_is_treated_as_no_existing_pr PASSED [ 86%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_pr_view_that_prints_a_bare_url_is_accepted PASSED [ 86%]
tests/test_ship.py::TestDirtyTreeParsing::test_a_rename_lists_the_new_path PASSED [ 86%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_a_refused_ship_never_pushes_even_when_push_was_requested PASSED [ 86%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_the_check_runs_before_the_push_on_a_passing_run PASSED [ 86%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_an_overridden_failing_check_still_pushes PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_a_branch_ahead_of_its_upstream_is_refused PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_the_refusal_says_how_far_ahead_and_how_to_fix_it PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_a_branch_level_with_its_upstream_ships PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_being_ahead_is_irrelevant_when_push_was_requested PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_no_pr_is_opened_when_the_commit_is_not_on_the_remote PASSED [ 86%]
tests/test_spike.py::test_runner_error_cannot_confirm_a_spike PASSED     [ 86%]
tests/test_spike.py::test_runs_vet_then_build_then_execute PASSED        [ 86%]
tests/test_spike.py::test_reports_all_three_stages PASSED                [ 86%]
tests/test_spike.py::test_never_uses_go_run PASSED                       [ 87%]
tests/test_spike.py::test_build_failure_skips_execute PASSED             [ 87%]
tests/test_spike.py::test_vet_failure_skips_build_and_execute PASSED     [ 87%]
tests/test_spike.py::test_build_failure_is_reported_as_build_not_execute PASSED [ 87%]
tests/test_spike.py::test_execute_failure_is_reported_as_execute_not_build PASSED [ 87%]
tests/test_spike.py::test_captures_both_streams_from_the_spike PASSED    [ 87%]
tests/test_spike.py::test_keeps_stdout_from_a_spike_that_failed PASSED   [ 87%]
tests/test_spike.py::test_maps_exit_code_to_verdict[0-Verdict.CONFIRMED] PASSED [ 87%]
tests/test_spike.py::test_maps_exit_code_to_verdict[1-Verdict.REFUTED] PASSED [ 87%]
tests/test_spike.py::test_maps_exit_code_to_verdict[2-Verdict.INCONCLUSIVE] PASSED [ 87%]
tests/test_spike.py::test_inconclusive_survives_as_inconclusive PASSED   [ 87%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[3] PASSED [ 87%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[7] PASSED [ 87%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[42] PASSED [ 87%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[127] PASSED [ 87%]
tests/test_spike.py::test_no_verdict_when_the_spike_never_ran PASSED     [ 87%]
tests/test_spike.py::test_binary_is_not_left_in_the_spike_directory PASSED [ 88%]
tests/test_spike.py::test_binary_is_removed_even_when_the_spike_fails PASSED [ 88%]
tests/test_spike.py::test_build_output_path_is_outside_the_spike_directory PASSED [ 88%]
tests/test_spike.py::test_default_timeout_is_300_seconds PASSED          [ 88%]
tests/test_spike.py::test_timeout_is_overridable PASSED                  [ 88%]
tests/test_spike.py::test_timed_out_spike_has_no_verdict PASSED          [ 88%]
tests/test_spike.py::test_detects_a_command_spike_from_its_source PASSED [ 88%]
tests/test_spike.py::test_detects_a_library_spike_from_its_source PASSED [ 88%]
tests/test_spike.py::test_library_spike_runs_go_test_instead_of_a_binary PASSED [ 88%]
tests/test_spike.py::test_library_spike_still_builds_first PASSED        [ 88%]
tests/test_spike.py::test_library_spike_passing_tests_is_confirmed PASSED [ 88%]
tests/test_spike.py::test_library_spike_failing_tests_is_refuted PASSED  [ 88%]
tests/test_spike.py::test_library_spike_can_never_be_inconclusive PASSED [ 88%]
tests/test_spike.py::test_library_spike_does_not_build_a_binary PASSED   [ 88%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[0] PASSED [ 88%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[1] PASSED [ 88%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[2] PASSED [ 89%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[42] PASSED [ 89%]
tests/test_spike.py::test_execute_stage_that_timed_out_did_not_produce_an_answer PASSED [ 89%]
tests/test_spike.py::test_skipped_execute_stage_did_not_produce_an_answer PASSED [ 89%]
tests/test_spike.py::test_vet_and_build_stages_never_claim_to_produce_an_answer[vet] PASSED [ 89%]
tests/test_spike.py::test_vet_and_build_stages_never_claim_to_produce_an_answer[build] PASSED [ 89%]
tests/test_spike.py::test_panicking_spike_is_crashed_not_inconclusive PASSED [ 89%]
tests/test_spike.py::test_deliberate_exit_2_is_still_inconclusive PASSED [ 89%]
tests/test_spike.py::test_crash_detection_needs_both_the_exit_code_and_the_signature PASSED [ 89%]
tests/test_spike.py::test_crash_detection_requires_a_stack_dump_not_just_the_word PASSED [ 89%]
tests/test_spike.py::test_a_crashed_spike_still_reports_its_exit_code PASSED [ 89%]
tests/test_spike.py::test_a_crashed_spike_did_not_answer PASSED          [ 89%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[0] PASSED [ 89%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[1] PASSED [ 89%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[2] PASSED [ 89%]
tests/test_spike.py::test_a_spike_that_answered_has_no_failed_stage[1] PASSED [ 89%]
tests/test_spike.py::test_a_spike_that_answered_has_no_failed_stage[2] PASSED [ 90%]
tests/test_spike.py::test_a_crashed_spike_does_have_a_failed_stage PASSED [ 90%]
tests/test_spike.py::test_a_build_failure_is_still_a_failed_stage PASSED [ 90%]
tests/test_spike.py::test_library_spike_panicking_is_also_crashed PASSED [ 90%]
tests/test_state.py::test_all_state_lives_under_a_single_directory PASSED [ 90%]
tests/test_state.py::test_config_and_state_are_separate_files PASSED     [ 90%]
tests/test_state.py::test_a_project_without_a_state_file_is_not_initialised PASSED [ 90%]
tests/test_state.py::test_a_project_is_initialised_once_both_files_exist PASSED [ 90%]
tests/test_state.py::test_init_writes_the_module_path PASSED             [ 90%]
tests/test_state.py::test_init_writes_an_empty_approvals_list PASSED     [ 90%]
tests/test_state.py::test_init_writes_no_phase_or_status PASSED          [ 90%]
tests/test_state.py::test_init_records_an_event PASSED                   [ 90%]
tests/test_state.py::test_the_state_file_holds_configuration_and_approvals PASSED [ 90%]
tests/test_state.py::test_the_module_path_stays_in_config_not_state PASSED [ 90%]
tests/test_state.py::test_the_state_file_has_no_phase_field PASSED       [ 90%]
tests/test_state.py::test_the_state_file_has_no_status_field PASSED      [ 90%]
tests/test_state.py::test_an_approval_records_phase_gate_and_date PASSED [ 90%]
tests/test_state.py::test_recording_an_approval_appends_rather_than_replaces PASSED [ 91%]
tests/test_state.py::test_an_absent_state_file_is_not_an_error PASSED    [ 91%]
tests/test_state.py::test_an_absent_state_file_reports_no_approvals PASSED [ 91%]
tests/test_state.py::test_a_corrupt_state_file_is_reported_as_a_problem PASSED [ 91%]
tests/test_state.py::test_a_non_string_module_path_is_ignored_not_trusted PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[json-array-at-top-level] PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[json-string] PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[dict-missing-approvals] PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[approvals-not-a-list] PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[approval-entry-not-a-dict] PASSED [ 91%]
tests/test_state.py::test_project_state_carries_configuration_and_approvals PASSED [ 91%]
tests/test_state.py::test_project_state_carries_no_phase PASSED          [ 91%]
tests/test_state.py::test_the_state_module_exposes_no_phase_enum PASSED  [ 91%]
tests/test_state.py::test_the_state_module_exposes_no_status_enum PASSED [ 91%]
tests/test_state.py::test_the_state_module_exposes_no_transition_machinery PASSED [ 91%]
tests/test_state.py::test_a_version_one_state_file_is_reported_as_outdated PASSED [ 91%]
tests/test_state.py::test_an_outdated_state_file_is_not_called_corrupt PASSED [ 92%]
tests/test_state.py::test_an_outdated_state_file_says_what_to_do_about_it PASSED [ 92%]
tests/test_state.py::test_an_outdated_state_file_yields_no_approvals PASSED [ 92%]
tests/test_state.py::test_a_file_missing_approvals_without_the_v1_shape_is_still_corrupt PASSED [ 92%]
tests/test_state.py::test_an_approval_missing_a_field_is_a_problem PASSED [ 92%]
tests/test_state.py::test_an_empty_approval_object_is_not_a_valid_approval PASSED [ 92%]
tests/test_state.py::test_an_approval_with_a_non_string_field_is_a_problem PASSED [ 92%]
tests/test_state.py::test_a_malformed_approval_names_its_position PASSED [ 92%]
tests/test_state.py::test_well_formed_approvals_still_load PASSED        [ 92%]
tests/test_status.py::test_the_text_rendering_names_the_project_root PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_names_the_current_phase PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_says_the_phase_came_from_the_branch PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_says_the_phase_came_from_the_fallback PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_lists_every_required_artifact PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_shows_a_recorded_approval PASSED [ 92%]
tests/test_status.py::test_every_other_phase_gets_one_summary_line PASSED [ 92%]
tests/test_status.py::test_the_summary_line_reports_present_over_required PASSED [ 93%]
tests/test_status.py::test_a_skipped_poc_phase_summarises_out_of_six PASSED [ 93%]
tests/test_status.py::test_the_current_phase_is_not_repeated_in_the_summary PASSED [ 93%]
tests/test_status.py::test_the_summary_is_ordered_lexically PASSED       [ 93%]
tests/test_status.py::test_the_json_contract_has_the_documented_keys PASSED [ 93%]
tests/test_status.py::test_the_json_phases_array_covers_every_phase PASSED [ 93%]
tests/test_status.py::test_the_json_phases_array_includes_the_current_phase PASSED [ 93%]
tests/test_status.py::test_the_json_artifact_map_is_name_to_boolean PASSED [ 93%]
tests/test_status.py::test_the_json_is_parseable_when_problems_exist PASSED [ 93%]
tests/test_status.py::test_two_problems_are_both_reported PASSED         [ 93%]
tests/test_status.py::test_a_problem_does_not_suppress_the_rest_of_the_report PASSED [ 93%]
tests/test_status.py::test_a_phase_missing_artifacts_still_answers PASSED [ 93%]
tests/test_status.py::test_a_project_with_no_phases_still_answers PASSED [ 93%]
tests/test_status.py::test_a_corrupt_state_file_still_answers PASSED     [ 93%]
tests/test_status.py::test_an_unreadable_project_root_is_reported_not_raised PASSED [ 93%]
tests/test_status.py::test_the_status_report_exposes_no_could_answer PASSED [ 93%]
tests/test_status.py::test_the_temp_file_sweep_still_runs PASSED         [ 94%]
tests/test_status.py::test_the_sweep_is_still_reported_never_silent PASSED [ 94%]
tests/test_status.py::test_no_rendering_describes_any_artifact_as_complete PASSED [ 94%]
tests/test_status.py::test_the_default_runner_and_project_resolution_are_used PASSED [ 94%]
tests/test_status.py::test_the_default_path_without_a_specs_directory_reports_no_phases PASSED [ 94%]
tests/test_status.py::test_a_specs_directory_without_a_project_reports_no_phases PASSED [ 94%]
tests/test_status.py::test_more_than_one_project_directory_is_reported_and_the_first_used PASSED [ 94%]
tests/test_status.py::test_a_project_directory_beside_loose_phase_directories_is_reported PASSED [ 94%]
tests/test_status.py::test_the_mixed_layout_still_reports_the_project_directory_phases PASSED [ 94%]
tests/test_status.py::test_a_flat_layout_is_accepted_without_comment PASSED [ 94%]
tests/test_status.py::test_real_repository_reports_multiple_projects_and_atom_cli_history_remains_readable PASSED [ 94%]
tests/test_status.py::test_a_corrupt_config_is_reported_separately PASSED [ 94%]
tests/test_status.py::test_the_last_event_and_damaged_lines_are_reported PASSED [ 94%]
tests/test_status.py::test_the_text_rendering_shows_the_module_path PASSED [ 94%]
tests/test_status.py::test_the_text_rendering_marks_a_not_started_phase PASSED [ 94%]
tests/test_status.py::test_the_text_rendering_states_when_there_is_no_current_phase PASSED [ 94%]
tests/test_status.py::test_the_text_rendering_shows_the_last_event PASSED [ 95%]
tests/test_status.py::test_the_text_rendering_points_at_the_problems PASSED [ 95%]
tests/test_status.py::test_the_problem_renderer_is_empty_when_there_are_no_problems PASSED [ 95%]
tests/test_status.py::test_the_problem_renderer_uses_amber_advisories PASSED [ 95%]
tests/test_status.py::test_the_problem_renderer_never_uses_red PASSED    [ 95%]
tests/test_storage.py::test_reading_a_missing_file_says_it_is_missing PASSED [ 95%]
tests/test_storage.py::test_reading_unparseable_json_reports_corruption PASSED [ 95%]
tests/test_storage.py::test_reading_valid_json_of_the_wrong_type_is_still_corruption PASSED [ 95%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected["just a string"-str] PASSED [ 95%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[42-int] PASSED [ 95%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[null-NoneType] PASSED [ 95%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[true-bool] PASSED [ 95%]
tests/test_storage.py::test_an_empty_file_is_corruption_not_emptiness PASSED [ 95%]
tests/test_storage.py::test_a_file_of_nul_bytes_is_corruption PASSED     [ 95%]
tests/test_storage.py::test_a_missing_required_key_is_corruption_and_names_the_key PASSED [ 95%]
tests/test_storage.py::test_reading_a_well_formed_file_returns_the_object PASSED [ 95%]
tests/test_storage.py::test_reading_does_not_keep_the_file_open PASSED   [ 95%]
tests/test_storage.py::test_writing_then_reading_round_trips PASSED      [ 96%]
tests/test_storage.py::test_writing_creates_the_parent_directory PASSED  [ 96%]
tests/test_storage.py::test_writing_leaves_no_temp_file_behind_on_success PASSED [ 96%]
tests/test_storage.py::test_writing_replaces_rather_than_truncating PASSED [ 96%]
tests/test_storage.py::test_writing_retries_while_the_destination_is_held_open PASSED [ 96%]
tests/test_storage.py::test_a_write_that_cannot_succeed_fails_loudly PASSED [ 96%]
tests/test_storage.py::test_sweeping_removes_leftover_temp_files PASSED  [ 96%]
tests/test_storage.py::test_sweeping_reports_what_it_removed PASSED      [ 96%]
tests/test_storage.py::test_sweeping_leaves_unsaved_recovery_files_alone PASSED [ 96%]
tests/test_storage.py::test_sweeping_leaves_real_state_files_alone PASSED [ 96%]
tests/test_storage.py::test_sweeping_an_absent_directory_is_not_an_error PASSED [ 96%]
tests/test_style.py::test_style_rules_reach_the_model_by_default PASSED  [ 96%]
tests/test_style.py::test_style_rules_can_be_switched_off_for_measurement PASSED [ 96%]
tests/test_style.py::test_style_rules_sit_before_the_output_format_instruction PASSED [ 96%]
tests/test_style.py::test_every_rule_is_numbered_and_present PASSED      [ 96%]
tests/test_style.py::test_no_rule_is_phrased_as_a_preference PASSED      [ 96%]
tests/test_toolchain.py::test_prompt_block_excludes_everything_the_passing_toolchain_proved PASSED [ 97%]
tests/test_toolchain.py::test_prompt_block_does_not_exclude_ignored_errors_when_errcheck_was_skipped PASSED [ 97%]
tests/test_toolchain.py::test_prompt_block_says_nothing_is_excluded_when_toolchain_did_not_run PASSED [ 97%]
tests/test_windows_process.py::test_windows_native_job_is_private PASSED [ 97%]
tests/test_windows_process.py::test_windows_launch_is_suspended_until_owned PASSED [ 97%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[0] PASSED [ 97%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[7] PASSED [ 97%]
tests/test_windows_process.py::test_windows_fixture_waits_for_readable_identity_record PASSED [ 97%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[PermissionError] PASSED [ 97%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[FileNotFoundError] PASSED [ 97%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[False] PASSED [ 97%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[True] PASSED [ 97%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[False] PASSED [ 97%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[True] PASSED [ 97%]
tests/test_windows_process.py::test_windows_large_stdin_and_unicode_argv PASSED [ 97%]
tests/test_windows_process.py::test_windows_communication_sleeps_only_while_idle PASSED [ 97%]
tests/test_windows_process.py::test_windows_busy_communication_still_checks_deadline PASSED [ 98%]
tests/test_windows_process.py::test_windows_large_streams_do_not_spend_the_deadline_sleeping PASSED [ 98%]
tests/test_windows_process.py::test_windows_cmd_shim_preserves_arguments PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[create_job] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[pipe] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[launch] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[assign] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[contains] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[resume] PASSED [ 98%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[terminate_job] PASSED [ 98%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[active_processes] PASSED [ 98%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[1] PASSED [ 98%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[2] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[0] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[1] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[2] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[completion_receipt] PASSED [ 99%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[missing_file_diagnosis] PASSED [ 99%]
tests/test_windows_process.py::test_windows_communication_observes_deferred_interrupt PASSED [ 99%]
tests/test_windows_process.py::test_windows_sigint_during_communication_is_prompt_and_reclaims_children PASSED [ 99%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[0] PASSED [ 99%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[7] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_capture_names_incomplete_streams PASSED [ 99%]
tests/test_windows_process.py::test_windows_concurrent_runs_are_isolated PASSED [ 99%]
tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers FAILED [ 99%]
tests/test_windows_process.py::test_windows_interrupt_during_native_launch_reclaims_suspended_parent PASSED [ 99%]
tests/test_windows_process.py::test_windows_sigint_during_handle_acquisition_does_not_lose_job PASSED [ 99%]
tests/test_windows_process.py::test_windows_broken_executable_is_diagnosed_as_unlaunchable PASSED [ 99%]
tests/test_windows_process.py::test_windows_runner_assigns_and_checks_membership_before_resume PASSED [ 99%]
tests/test_windows_process.py::test_windows_child_can_close_stdin_early PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[None] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary1] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary2] PASSED [100%]

================================== FAILURES ===================================
___________ test_windows_repeated_runs_release_handles_and_workers ____________

tmp_path = WindowsPath('<LOCAL_TEMP>/pytest-of-gimotwan/pytest-610/test_windows_repeated_runs_rel0')

    def test_windows_repeated_runs_release_handles_and_workers(tmp_path):
        import ctypes
        from ctypes import wintypes
    
        native = _windows_module()._Native()
        native._bind("GetProcessHandleCount", [wintypes.HANDLE, wintypes.LPVOID])
    
        def handle_count():
            count = wintypes.DWORD()
            native._check(
                native.library.GetProcessHandleCount(wintypes.HANDLE(-1), ctypes.byref(count)),
                "GetProcessHandleCount:fixture",
            )
            return count.value
    
        runner = SubprocessRunner()
        assert runner.run([sys.executable, "-c", "pass"], tmp_path).succeeded
        gc.collect()
        baseline = handle_count()
        threads = set(threading.enumerate())
        for _ in range(12):
            result = runner.run([sys.executable, "-c", "print('done')"], tmp_path)
            assert result.succeeded, result.stderr
        gc.collect()
>       assert handle_count() <= baseline, "native handles leaked across command runs"
E       AssertionError: native handles leaked across command runs
E       assert 330 <= 328
E        +  where 330 = <function test_windows_repeated_runs_release_handles_and_workers.<locals>.handle_count at 0x00000204F8AF2DE0>()

tests\test_windows_process.py:761: AssertionError
=============================== tests coverage ================================
______________ coverage: platform win32, python 3.13.14-final-0 _______________

Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
atom\__init__.py                1      0   100%
atom\_checkout_cleanup.py      30     21    30%   13-30, 34-41, 45
atom\_review_format.py        149      7    95%   125, 178, 201, 210, 234, 244, 257
atom\_windows_process.py      381     28    93%   188-190, 243, 309, 317, 346-350, 357-359, 362-363, 377, 386-387, 405, 414, 455-456, 485, 487, 560-561, 610, 618
atom\artifact_cli.py           35      1    97%   58
atom\artifacts.py             174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\body.py                   71      0   100%
atom\buildsystem.py            76      5    93%   57-60, 72, 116, 180
atom\check.py                  43      2    95%   117-118
atom\cli.py                   366     21    94%   107-108, 372-373, 383-393, 415-425, 684, 875
atom\context.py                61      2    97%   86-87
atom\diff.py                  124      0   100%
atom\eventlog.py               50      0   100%
atom\extract.py               164      0   100%
atom\filelock.py               64     10    84%   69-80, 169
atom\gates.py                 173      6    97%   91, 407-408, 412, 462, 472
atom\go_selection.py          220      3    99%   97, 181, 280
atom\index.py                  40      5    88%   66-67, 81, 86, 98
atom\invoke.py                137      4    97%   445, 449-451
atom\merge.py                  92      0   100%
atom\module_rules.py           52      2    96%   53-54
atom\onboarding.py            137      4    97%   100, 138, 263-264
atom\pathsetup.py              66      0   100%
atom\phases.py                 92      0   100%
atom\pull_request.py          209      6    97%   81, 306-307, 311-312, 341
atom\report.py                396     10    97%   193, 208, 220, 234, 250, 252, 259, 931, 933, 935
atom\review.py                131      0   100%
atom\runner.py                213     54    75%   144-145, 161-207, 262, 268, 306-312, 345-357, 369-373, 384-395, 416, 457, 467, 469, 541
atom\scaffold.py               46      1    98%   127
atom\ship.py                  252      3    99%   387, 390-391
atom\spike.py                 128      4    97%   169, 265, 268-269
atom\state.py                 103      1    99%   235
atom\status.py                 77      0   100%
atom\storage.py                79      0   100%
atom\style.py                   4      0   100%
atom\toolchain.py              72      4    94%   124, 180, 188, 190
---------------------------------------------------------
TOTAL                        4508    223    95%
=========================== short test summary info ===========================
FAILED tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers - AssertionError: native handles leaked across command runs
assert 330 <= 328
 +  where 330 = <function test_windows_repeated_runs_release_handles_and_workers.<locals>.handle_count at 0x00000204F8AF2DE0>()
============ 1 failed, 1614 passed, 5 skipped in 214.87s (0:03:34) ============
EXIT CODE: 1

```

## Unchanged Strict Handle Test: Focused Diagnosis

Historical capture sequence; current outcome and limits are stated above.
Original capture SHA-256: `326acc2487cbc7d46f612f6ae206b887b9df08e3e7a70828e4eadb2a08607f77`.

```text
python -m pytest tests\test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers -v
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers PASSED [100%]

============================== 1 passed in 1.37s ==============================
EXIT CODE: 0

```

## Approved Unchanged Full Rerun

Historical capture sequence; current outcome and limits are stated above.
Original capture SHA-256: `e66cfc052c050b47e113252b9017eeb3a029b1de7e98872659df361ca5a40132`.

```text
python -m pytest tests -v --cov=atom --cov-report=term-missing
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0 -- <LOCAL_PROFILE>\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: <FEATURE_WORKTREE>\tools
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1620 items

tests/test_artifact_cli.py::test_main_allowed_target_writes_exact_utf8_content PASSED [  0%]
tests/test_artifact_cli.py::test_main_empty_stdin_creates_empty_artifact PASSED [  0%]
tests/test_artifact_cli.py::test_module_execution_runs_main_entry_point PASSED [  0%]
tests/test_artifact_cli.py::test_bootstrap_documents_hidden_artifact_writer_fallback PASSED [  0%]
tests/test_artifact_cli.py::test_main_normalizes_native_shell_line_endings_to_lf PASSED [  0%]
tests/test_artifact_cli.py::test_main_strips_the_byte_order_mark_windows_shells_prepend PASSED [  0%]
tests/test_artifact_cli.py::test_main_strips_only_the_first_byte_order_mark PASSED [  0%]
tests/test_artifact_cli.py::test_main_invalid_utf8_writes_nothing PASSED [  0%]
tests/test_artifact_cli.py::test_main_refused_target_does_not_read_stdin PASSED [  0%]
tests/test_artifact_cli.py::test_main_wrong_argument_count_exits_usage_error[arguments0] PASSED [  0%]
tests/test_artifact_cli.py::test_main_wrong_argument_count_exits_usage_error[arguments1] PASSED [  0%]
tests/test_artifact_cli.py::test_main_filesystem_failure_reports_error_without_partial_file PASSED [  0%]
tests/test_artifact_cli.py::test_main_refusal_during_write_is_reported PASSED [  0%]
tests/test_artifact_integration.py::test_package_registers_only_the_dedicated_artifact_writer PASSED [  0%]
tests/test_artifact_integration.py::test_main_atom_cli_does_not_expose_artifact_subcommand PASSED [  0%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[discover] PASSED [  0%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[poc] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[plan] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[spec] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[tdd] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_producing_skills_use_dedicated_writer[review] PASSED [  1%]
tests/test_artifact_integration.py::test_artifact_writer_instruction_forbids_bypass_and_source_writes PASSED [  1%]
tests/test_artifact_integration.py::test_onboarding_installs_artifact_writer_instructions PASSED [  1%]
tests/test_artifact_integration.py::test_onboarding_does_not_edit_copilot_permission_configuration PASSED [  1%]
tests/test_artifact_integration.py::test_built_package_installs_working_dedicated_console_script PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[specs/project/design.md-allowed-artifact-directory] PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[poc/spike/README.md-allowed-artifact-directory] PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/config.json-allowed-runtime-file] PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/state.json-allowed-runtime-file] PASSED [  1%]
tests/test_artifacts.py::test_artifact_paths_are_allowed[.atom/baseline.json-allowed-runtime-file] PASSED [  1%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[internal/server.go-outside-artifact-set] PASSED [  1%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[tools/atom/cli.py-outside-artifact-set] PASSED [  1%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.github/copilot-instructions.md-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/atom/AGENTS.md-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/events.jsonl-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[.atom/credentials.json-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[specs-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[specs/../internal/escape.go-outside-artifact-set] PASSED [  2%]
tests/test_artifacts.py::test_non_artifact_paths_are_refused[../elsewhere/escape.md-outside-repository] PASSED [  2%]
tests/test_artifacts.py::test_absolute_path_outside_the_repository_is_refused PASSED [  2%]
tests/test_artifacts.py::test_link_inside_specs_is_refused_before_containment PASSED [  2%]
tests/test_artifacts.py::test_link_pointing_back_inside_is_still_refused PASSED [  2%]
tests/test_artifacts.py::test_write_creates_nested_artifact_directories PASSED [  2%]
tests/test_artifacts.py::test_write_replaces_an_existing_artifact PASSED [  2%]
tests/test_artifacts.py::test_write_leaves_no_temporary_files_behind PASSED [  2%]
tests/test_artifacts.py::test_mixed_batch_writes_nothing PASSED          [  2%]
tests/test_artifacts.py::test_every_refusal_in_a_batch_is_reported PASSED [  2%]
tests/test_artifacts.py::test_write_through_a_link_is_refused_and_writes_nothing PASSED [  2%]
tests/test_artifacts.py::test_link_appearing_after_validation_is_caught_before_the_write PASSED [  3%]
tests/test_artifacts.py::test_cleanup_removes_a_link_planted_where_it_created_a_directory PASSED [  3%]
tests/test_artifacts.py::test_a_file_in_place_of_a_directory_is_refused PASSED [  3%]
tests/test_artifacts.py::test_a_path_on_another_drive_is_refused PASSED  [  3%]
tests/test_artifacts.py::test_a_failed_stage_leaves_nothing_behind PASSED [  3%]
tests/test_artifacts.py::test_a_failed_replace_preserves_existing_file_and_removes_temporary PASSED [  3%]
tests/test_body.py::TestExtractPurpose::test_the_purpose_prose_is_returned PASSED [  3%]
tests/test_body.py::TestExtractPurpose::test_every_paragraph_of_the_purpose_survives PASSED [  3%]
tests/test_body.py::TestExtractPurpose::test_a_missing_purpose_section_returns_none PASSED [  3%]
tests/test_body.py::TestExtractPurpose::test_the_next_heading_ends_the_purpose_section PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_body_title_is_the_h1 PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_why_quotes_the_purpose_paragraph PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_what_changed_lists_the_commit_subjects PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_parts_appear_in_the_specified_order PASSED [  3%]
tests/test_body.py::TestBodyIsSummaryPlusLinks::test_the_body_links_to_each_artifact_rather_than_embedding_it PASSED [  3%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_every_link_embeds_the_pushed_commit_sha PASSED [  3%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_no_link_uses_a_branch_name_as_the_ref PASSED [  4%]
tests/test_body.py::TestLinksPointAtTheCommitSha::test_no_link_points_at_the_base_branch PASSED [  4%]
tests/test_body.py::TestWriteBodyFile::test_the_written_file_contains_no_carriage_return PASSED [  4%]
tests/test_body.py::TestWriteBodyFile::test_the_returned_count_is_the_character_count PASSED [  4%]
tests/test_body.py::TestWriteBodyFile::test_the_character_count_is_below_the_text_mode_byte_count PASSED [  4%]
tests/test_body.py::TestWriteBodyFile::test_the_reported_count_matches_the_bytes_on_disk PASSED [  4%]
tests/test_body.py::TestEvidenceStatesAbsence::test_a_gate_table_carries_one_row_per_gate PASSED [  4%]
tests/test_body.py::TestEvidenceStatesAbsence::test_the_recorded_line_replaces_the_table_it_does_not_empty_the_section PASSED [  4%]
tests/test_body.py::TestEvidenceStatesAbsence::test_an_overridden_failure_is_stated_never_asserted_green PASSED [  4%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_no_artifacts_produces_no_invented_link PASSED [  4%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_the_body_never_editorialises_a_missing_artifact PASSED [  4%]
tests/test_body.py::TestMissingArtifactsAreAbsent::test_only_the_artifacts_present_are_linked PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_a_plain_rule_is_a_target PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_several_targets_on_one_rule_are_all_read PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_prerequisites_are_not_targets PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_a_double_colon_rule_is_a_target PASSED [  4%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS := -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS ::= -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS ?= -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS += -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_assignment_is_never_a_target[BUILD_FLAGS = -race] PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_a_recipe_line_is_never_a_target PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_pattern_and_variable_targets_are_ignored PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_special_targets_are_ignored PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_a_comment_does_not_create_a_target PASSED [  5%]
tests/test_buildsystem.py::TestReadingTargets::test_an_unreadable_makefile_yields_no_targets PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_without_a_makefile_the_go_defaults_stand PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_a_makefile_with_both_targets_takes_over PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[GNUmakefile] PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[makefile] PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_the_reported_name_is_the_one_actually_on_disk[Makefile] PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_each_gate_is_decided_on_its_own_target PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[GNUmakefile] PASSED [  5%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[makefile] PASSED [  6%]
tests/test_buildsystem.py::TestChoosingCommands::test_every_name_make_itself_honours_is_honoured[Makefile] PASSED [  6%]
tests/test_buildsystem.py::TestChoosingCommands::test_gnumakefile_wins_over_makefile_as_make_would PASSED [  6%]
tests/test_buildsystem.py::TestChoosingCommands::test_without_make_installed_the_makefile_is_not_used PASSED [  6%]
tests/test_check.py::test_run_check_evaluates_every_gate_even_after_a_failure PASSED [  6%]
tests/test_check.py::test_report_passes_only_when_every_required_gate_passed_or_skipped PASSED [  6%]
tests/test_check.py::test_report_fails_when_a_required_gate_failed PASSED [  6%]
tests/test_check.py::test_optional_gate_failure_does_not_fail_the_check PASSED [  6%]
tests/test_check.py::test_warning_status_never_affects_the_verdict PASSED [  6%]
tests/test_check.py::test_exit_code_is_zero_only_when_the_check_passed[passed] PASSED [  6%]
tests/test_check.py::test_exit_code_is_zero_only_when_the_check_passed[failed] PASSED [  6%]
tests/test_check.py::test_run_check_refuses_a_directory_that_does_not_exist PASSED [  6%]
tests/test_check.py::test_run_check_refuses_a_directory_without_go_mod PASSED [  6%]
tests/test_check.py::test_run_check_refuses_before_running_any_gate PASSED [  6%]
tests/test_check.py::test_finds_poc_directories_with_go_files_but_no_go_mod PASSED [  6%]
tests/test_check.py::test_ignores_poc_directories_that_have_a_go_mod PASSED [  6%]
tests/test_check.py::test_ignores_poc_directories_with_no_go_files PASSED [  7%]
tests/test_check.py::test_returns_empty_list_when_there_is_no_poc_directory PASSED [  7%]
tests/test_check.py::test_poc_warnings_appear_in_the_report_without_failing_it PASSED [  7%]
tests/test_cli.py::test_check_returns_zero_when_every_gate_passes PASSED [  7%]
tests/test_cli.py::test_check_returns_one_when_a_gate_fails PASSED       [  7%]
tests/test_cli.py::test_check_json_flag_emits_parseable_json PASSED      [  7%]
tests/test_cli.py::test_check_reports_a_missing_directory_without_a_traceback PASSED [  7%]
tests/test_cli.py::test_check_reports_a_directory_without_go_mod_clearly PASSED [  7%]
tests/test_cli.py::test_check_defaults_to_the_current_directory PASSED   [  7%]
tests/test_cli.py::test_no_race_flag_disables_the_race_gate PASSED       [  7%]
tests/test_cli.py::test_the_cli_runs_as_a_module_without_exploding PASSED [  7%]
tests/test_cli.py::test_every_subcommand_is_reachable_in_a_real_process PASSED [  7%]
tests/test_cli_poc.py::test_poc_list_on_an_empty_repo_succeeds PASSED    [  7%]
tests/test_cli_poc.py::test_poc_list_shows_each_spike PASSED             [  7%]
tests/test_cli_poc.py::test_poc_list_flags_a_spike_missing_go_mod PASSED [  7%]
tests/test_cli_poc.py::test_poc_list_json_is_machine_readable PASSED     [  7%]
tests/test_cli_poc.py::test_poc_new_rejects_a_bad_slug_as_a_usage_error PASSED [  8%]
tests/test_cli_poc.py::test_poc_new_bad_slug_writes_one_line_to_stderr PASSED [  8%]
tests/test_cli_poc.py::test_poc_new_refuses_an_existing_spike_as_a_usage_error PASSED [  8%]
tests/test_cli_poc.py::test_poc_run_on_a_missing_spike_is_a_usage_error PASSED [  8%]
tests/test_cli_poc.py::test_poc_run_on_a_spike_without_go_mod_is_a_usage_error PASSED [  8%]
tests/test_cli_poc.py::test_a_crashed_spike_makes_the_command_exit_non_zero PASSED [  8%]
tests/test_cli_poc.py::test_every_real_verdict_makes_the_command_exit_zero PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_source_dispatch PASSED              [  8%]
tests/test_cli_pr_review.py::test_pr_freezes_launch_toolchain_request[project] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_freezes_launch_toolchain_request[cli] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_freezes_launch_toolchain_request[ambient] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra0] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra1] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra2] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra3] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra4] PASSED [  8%]
tests/test_cli_pr_review.py::test_pr_invalid_options_fail_before_preparation[extra5] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_report_provenance_and_limitations[True] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_report_provenance_and_limitations[False] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_review_options_and_partial_status PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_no_model_available_is_not_clean_review PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_transport_failure_is_partial_and_still_cleans_checkout PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_required_checks_still_block[False] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_required_checks_still_block[True] PASSED [  9%]
tests/test_cli_pr_review.py::test_cleanup_failure_prevents_success_output PASSED [  9%]
tests/test_cli_pr_review.py::test_local_reports_have_no_pr_fields PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_context_is_captured_before_preparation_from_launch_directory[False] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_context_is_captured_before_preparation_from_launch_directory[True] PASSED [  9%]
tests/test_cli_pr_review.py::test_pr_context_failure_prevents_preparation PASSED [  9%]
tests/test_cli_pr_review.py::test_missing_source_help_mentions_pr PASSED [  9%]
tests/test_cli_pr_review.py::test_cli_freezes_launch_rules_before_pr_preparation[False] PASSED [  9%]
tests/test_cli_pr_review.py::test_cli_freezes_launch_rules_before_pr_preparation[True] PASSED [  9%]
tests/test_cli_pr_review.py::test_cli_rule_error_prevents_preparation_or_execution[False] PASSED [ 10%]
tests/test_cli_pr_review.py::test_cli_rule_error_prevents_preparation_or_execution[True] PASSED [ 10%]
tests/test_cli_review.py::test_review_cli_captures_project_toolchain_policy PASSED [ 10%]
tests/test_cli_review.py::test_review_cli_version_and_executable_override[False] PASSED [ 10%]
tests/test_cli_review.py::test_review_cli_version_and_executable_override[True] PASSED [ 10%]
tests/test_cli_review.py::test_explicit_go_options_conflict_with_skip_toolchain[option0] PASSED [ 10%]
tests/test_cli_review.py::test_explicit_go_options_conflict_with_skip_toolchain[option1] PASSED [ 10%]
tests/test_cli_review.py::test_toolchain_setup_failures_are_stderr_only[configuration] PASSED [ 10%]
tests/test_cli_review.py::test_toolchain_setup_failures_are_stderr_only[selection] PASSED [ 10%]
tests/test_cli_review.py::test_toolchain_setup_failures_are_stderr_only[required] PASSED [ 10%]
tests/test_cli_review.py::test_invalid_go_policy_fails_before_runner_commands[options0-2-exact stable Go] PASSED [ 10%]
tests/test_cli_review.py::test_invalid_go_policy_fails_before_runner_commands[options1-2-requires] PASSED [ 10%]
tests/test_cli_review.py::test_invalid_go_policy_fails_before_runner_commands[options2-1-review_go_version] PASSED [ 10%]
tests/test_cli_review.py::test_context_requires_opt_in_before_io PASSED  [ 10%]
tests/test_cli_review.py::test_context_cli_failure_blocks_runner[missing-1-could not be read] PASSED [ 10%]
tests/test_cli_review.py::test_context_cli_failure_blocks_runner[blank-1-empty content] PASSED [ 10%]
tests/test_cli_review.py::test_context_cli_failure_blocks_runner[duplicate-2-duplicate context-file] PASSED [ 10%]
tests/test_cli_review.py::test_fixed_evidence_cli_uses_mode PASSED       [ 11%]
tests/test_cli_review.py::test_fixed_evidence_cli_reports_scope[False-False] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_cli_reports_scope[False-True] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_cli_reports_scope[True-False] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_cli_reports_scope[True-True] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_execution_violation_is_incomplete[False] PASSED [ 11%]
tests/test_cli_review.py::test_fixed_evidence_execution_violation_is_incomplete[True] PASSED [ 11%]
tests/test_cli_review.py::test_structured_failure_streams_never_reach_cli_reports[False-False] PASSED [ 11%]
tests/test_cli_review.py::test_structured_failure_streams_never_reach_cli_reports[False-True] PASSED [ 11%]
tests/test_cli_review.py::test_structured_failure_streams_never_reach_cli_reports[True-False] PASSED [ 11%]
tests/test_cli_review.py::test_structured_failure_streams_never_reach_cli_reports[True-True] PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_no_source_is_a_usage_error PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_two_sources_is_a_usage_error PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_working_is_accepted PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_staged_is_accepted PASSED [ 11%]
tests/test_cli_review.py::TestDiffSourceSelection::test_branch_is_accepted PASSED [ 11%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_setting_that_consults_nobody_is_refused[--runs-0] PASSED [ 12%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_setting_that_consults_nobody_is_refused[--concurrency-0] PASSED [ 12%]
tests/test_cli_review.py::TestNonsensicalSettings::test_a_negative_window_is_refused PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_a_complete_review_exits_zero_even_with_findings PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_a_partial_review_exits_non_zero PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_no_usable_response_fails_loudly PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_every_model_unavailable_fails_rather_than_reporting_nothing PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_a_git_failure_is_not_reported_as_a_clean_review PASSED [ 12%]
tests/test_cli_review.py::TestExitCodes::test_a_blocked_toolchain_returns_check_failed_without_reviewing PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_only_parent_findings_reach_the_report[False] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_only_parent_findings_reach_the_report[True] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_transport_failure_keeps_completion_but_not_answer_count PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[ \n\t] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[[]] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[not JSONL] PASSED [ 12%]
tests/test_cli_review.py::TestStructuredResponses::test_no_readable_parent_never_becomes_a_clean_review[{"type": "result", "exitCode": 0, "sessionId": "fixture"}] PASSED [ 13%]
tests/test_cli_review.py::TestChannels::test_the_report_goes_to_stdout PASSED [ 13%]
tests/test_cli_review.py::TestChannels::test_failure_detail_goes_to_stderr_only PASSED [ 13%]
tests/test_cli_review.py::TestChannels::test_json_output_is_parseable PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_each_model_is_asked_the_requested_number_of_times PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_custom_instructions_are_disabled PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_named_mcp_exclusions_reach_probes_and_reviews PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_no_named_mcp_server_is_disabled_by_default PASSED [ 13%]
tests/test_cli_review.py::TestCommandsIssued::test_the_prompt_carries_the_whole_diff_in_one_call PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_the_module_can_be_executed PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_appears_in_the_top_level_help PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_help_runs_without_error PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_without_a_source_exits_two_and_explains PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_review_with_two_sources_exits_two_and_explains PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_a_refused_setting_does_not_produce_a_traceback PASSED [ 13%]
tests/test_cli_review.py::TestTheProgramActuallyRuns::test_nothing_is_defined_below_the_main_guard PASSED [ 13%]
tests/test_cli_review.py::TestTheDefaultModelPairIsTheMeasuredOne::test_the_default_models_are_the_two_that_scored_above_ninety_percent PASSED [ 14%]
tests/test_cli_review.py::TestTheDefaultModelPairIsTheMeasuredOne::test_the_help_text_names_the_models_it_actually_uses PASSED [ 14%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_ship_builds_its_gates_without_raising PASSED [ 14%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_no_race_still_builds_gates PASSED [ 14%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_five_gates_are_passed_through PASSED [ 14%]
tests/test_cli_ship.py::TestTheCommandFunctionIsReached::test_no_race_disables_only_the_race_gate PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_base_defaults_to_main PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_base_is_forwarded PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_phase_and_title_are_forwarded PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_push_defaults_off_and_is_forwarded_when_given PASSED [ 14%]
tests/test_cli_ship.py::TestArgumentsReachRunShip::test_allow_failing_checks_is_forwarded PASSED [ 14%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_a_refusal_exits_one_and_prints_to_stderr PASSED [ 14%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_an_overridden_failing_check_exits_non_zero PASSED [ 14%]
tests/test_cli_ship.py::TestRefusalsAndExitCodes::test_an_overridden_run_says_so_on_stderr PASSED [ 14%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_a_created_pr_says_opened PASSED [ 14%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_an_updated_pr_says_updated PASSED [ 14%]
tests/test_cli_ship.py::TestWhatIsPrinted::test_the_commit_is_abbreviated_not_printed_whole PASSED [ 15%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_appears_in_the_top_level_help PASSED [ 15%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_help_runs_without_error PASSED [ 15%]
tests/test_cli_ship.py::TestTheProgramActuallyRuns::test_ship_outside_a_phase_branch_refuses_without_a_traceback PASSED [ 15%]
tests/test_cli_state.py::test_init_creates_the_project PASSED            [ 15%]
tests/test_cli_state.py::test_init_starts_the_project_with_no_approvals PASSED [ 15%]
tests/test_cli_state.py::test_init_does_not_claim_a_phase PASSED         [ 15%]
tests/test_cli_state.py::test_init_refuses_to_overwrite_an_existing_project PASSED [ 15%]
tests/test_cli_state.py::test_init_force_overwrites_deliberately PASSED  [ 15%]
tests/test_cli_state.py::test_status_reports_the_current_phase PASSED    [ 15%]
tests/test_cli_state.py::test_status_answers_without_any_state_file_at_all PASSED [ 15%]
tests/test_cli_state.py::test_status_exits_zero_when_state_is_corrupt PASSED [ 15%]
tests/test_cli_state.py::test_status_exits_zero_whatever_it_finds PASSED [ 15%]
tests/test_cli_state.py::test_status_json_is_machine_readable PASSED     [ 15%]
tests/test_cli_state.py::test_status_json_still_emits_on_corrupt_state PASSED [ 15%]
tests/test_cli_state.py::test_status_reports_every_problem_at_once PASSED [ 15%]
tests/test_cli_state.py::test_status_reports_unsaved_work PASSED         [ 15%]
tests/test_cli_state.py::test_status_shows_the_most_recent_event PASSED  [ 16%]
tests/test_cli_state.py::test_status_sweeps_leftover_temp_files_and_says_so PASSED [ 16%]
tests/test_cli_state.py::test_the_sweep_never_touches_unsaved_work PASSED [ 16%]
tests/test_cli_state.py::test_status_works_while_the_event_log_lock_is_held PASSED [ 16%]
tests/test_cli_state.py::test_no_project_wide_lock_file_is_created PASSED [ 16%]
tests/test_cli_state.py::test_init_runs_as_a_real_process PASSED         [ 16%]
tests/test_cli_state.py::test_the_atom_package_imports_cleanly PASSED    [ 16%]
tests/test_cli_state.py::test_status_runs_as_a_subprocess_and_exits_zero PASSED [ 16%]
tests/test_cli_state.py::test_status_json_output_is_parseable_from_a_subprocess PASSED [ 16%]
tests/test_cli_state.py::test_status_runs_in_a_directory_that_is_not_a_project PASSED [ 16%]
tests/test_cli_state.py::test_status_runs_with_no_state_file_present PASSED [ 16%]
tests/test_cli_state.py::test_status_exits_zero_as_a_real_process_when_corrupt PASSED [ 16%]
tests/test_cli_state.py::test_init_that_cannot_write_is_fatal_and_says_how_to_recover PASSED [ 16%]
tests/test_cli_state.py::test_init_does_not_promise_safety_it_cannot_deliver PASSED [ 16%]
tests/test_cli_state.py::test_status_reports_a_corrupt_config_separately_from_state PASSED [ 16%]
tests/test_cli_state.py::test_status_counts_damaged_event_log_lines PASSED [ 16%]
tests/test_cli_state.py::test_status_tells_the_developer_how_to_recover_from_corruption PASSED [ 17%]
tests/test_cli_state.py::test_status_prints_each_problem_exactly_once PASSED [ 17%]
tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[source] PASSED [ 17%]
tests/test_comment_guidance.py::test_tdd_asks_the_author_for_a_comment_pass[packaged] PASSED [ 17%]
tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[source] PASSED [ 17%]
tests/test_comment_guidance.py::test_tdd_scopes_comments_to_what_the_code_cannot_say[packaged] PASSED [ 17%]
tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[source] PASSED [ 17%]
tests/test_comment_guidance.py::test_the_comment_pass_is_in_the_completion_checklist[packaged] PASSED [ 17%]
tests/test_comment_guidance.py::test_the_two_tdd_skill_copies_stay_identical PASSED [ 17%]
tests/test_comment_guidance.py::test_the_review_rule_names_a_missing_comment_as_the_defect PASSED [ 17%]
tests/test_context.py::test_context_capture_preserves_bytes_and_order PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[blank-empty content] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[nul-NUL content] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[encoding-invalid UTF-8] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[directory-is not a regular file] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[missing-could not be read] PASSED [ 17%]
tests/test_context.py::test_context_capture_rejects_invalid_input[permission-could not be read] PASSED [ 18%]
tests/test_context.py::test_context_capture_rejects_invalid_input[resolution-could not be read] PASSED [ 18%]
tests/test_context.py::test_context_capture_rejects_duplicate_paths PASSED [ 18%]
tests/test_diff.py::test_runner_failure_details_survive_diff_rejection[CommandOutcome.RUNNER_ERROR] PASSED [ 18%]
tests/test_diff.py::test_runner_failure_details_survive_diff_rejection[CommandOutcome.TIMED_OUT] PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_staged_source_asks_git_for_the_index PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_working_source_asks_git_for_unstaged_changes PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_branch_source_diffs_against_the_merge_base PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_selecting_no_source_names_all_three_options PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_selecting_two_sources_is_an_error_rather_than_a_precedence_rule PASSED [ 18%]
tests/test_diff.py::TestSourceSelection::test_the_chosen_source_is_recorded_on_the_request PASSED [ 18%]
tests/test_diff.py::TestCapture::test_capture_issues_exactly_one_git_command PASSED [ 18%]
tests/test_diff.py::TestCapture::test_a_multi_file_diff_is_captured_whole PASSED [ 18%]
tests/test_diff.py::TestCapture::test_an_empty_diff_is_not_an_error PASSED [ 18%]
tests/test_diff.py::TestCapture::test_a_whitespace_only_diff_counts_as_empty PASSED [ 18%]
tests/test_diff.py::TestCapture::test_nothing_is_truncated_however_large_the_diff PASSED [ 18%]
tests/test_diff.py::TestGitFailure::test_a_failed_git_command_is_reported_not_swallowed PASSED [ 19%]
tests/test_diff.py::TestGitFailure::test_a_missing_git_is_reported_clearly PASSED [ 19%]
tests/test_diff.py::TestGitFailure::test_a_timed_out_git_command_is_reported PASSED [ 19%]
tests/test_diff.py::TestSize::test_changed_lines_count_additions_and_removals PASSED [ 19%]
tests/test_diff.py::TestSize::test_file_headers_are_not_counted_as_changed_lines PASSED [ 19%]
tests/test_diff.py::TestSize::test_context_lines_are_not_counted PASSED  [ 19%]
tests/test_diff.py::TestSize::test_file_count_follows_the_b_side_of_a_rename PASSED [ 19%]
tests/test_diff.py::TestSize::test_a_file_is_counted_once_however_many_hunks_it_has PASSED [ 19%]
tests/test_diff.py::TestSize::test_size_reads_as_a_sentence_for_the_report PASSED [ 19%]
tests/test_diff.py::TestSize::test_size_description_is_singular_for_one_file PASSED [ 19%]
tests/test_diff.py::TestSize::test_an_empty_diff_describes_itself_as_empty PASSED [ 19%]
tests/test_diff.py::TestDescription::test_staged_describes_itself PASSED [ 19%]
tests/test_diff.py::TestDescription::test_working_describes_itself PASSED [ 19%]
tests/test_diff.py::TestDescription::test_branch_names_the_base_ref PASSED [ 19%]
tests/test_diff.py::TestDescription::test_a_path_without_an_a_or_b_prefix_is_used_as_is PASSED [ 19%]
tests/test_diff.py::TestHeaderConfusion::test_removing_a_markdown_rule_still_counts_as_a_changed_line PASSED [ 19%]
tests/test_diff.py::TestHeaderConfusion::test_added_content_cannot_invent_a_file PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_content_that_looks_like_a_git_header_does_not_start_a_new_file PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_content_that_looks_like_a_hunk_header_is_counted_as_a_change PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_several_files_each_reset_the_header_state PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_a_deleted_file_is_named_by_its_old_path PASSED [ 20%]
tests/test_diff.py::TestHeaderConfusion::test_a_no_newline_marker_is_not_a_changed_line PASSED [ 20%]
tests/test_eventlog.py::test_appending_then_reading_round_trips PASSED   [ 20%]
tests/test_eventlog.py::test_appending_creates_the_log_and_its_directory PASSED [ 20%]
tests/test_eventlog.py::test_each_event_is_one_line PASSED               [ 20%]
tests/test_eventlog.py::test_appending_never_rewrites_existing_content PASSED [ 20%]
tests/test_eventlog.py::test_a_timestamp_is_recorded_for_each_event PASSED [ 20%]
tests/test_eventlog.py::test_the_caller_cannot_be_clobbered_by_the_timestamp PASSED [ 20%]
tests/test_eventlog.py::test_appending_uses_a_separate_lock_file PASSED  [ 20%]
tests/test_eventlog.py::test_a_truncated_final_line_is_skipped_with_a_warning PASSED [ 20%]
tests/test_eventlog.py::test_a_corrupt_line_in_the_middle_does_not_hide_later_ones PASSED [ 20%]
tests/test_eventlog.py::test_a_corrupt_line_reports_its_line_number PASSED [ 20%]
tests/test_eventlog.py::test_a_json_array_line_is_treated_as_damaged PASSED [ 20%]
tests/test_eventlog.py::test_blank_lines_are_ignored_rather_than_reported PASSED [ 21%]
tests/test_eventlog.py::test_reading_a_log_that_does_not_exist_yet_is_not_an_error PASSED [ 21%]
tests/test_eventlog.py::test_reading_does_not_take_the_lock PASSED       [ 21%]
tests/test_eventlog.py::test_concurrent_appends_from_real_processes_lose_nothing PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event0] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event1] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event2] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event3] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event4] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[False-event5] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event0] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event1] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event2] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event3] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event4] PASSED [ 21%]
tests/test_extract.py::test_fixed_evidence_rejects_observable_execution[True-event5] PASSED [ 21%]
tests/test_extract.py::TestCliResponseIsolation::test_selects_parent_content_before_strict_findings_validation[[]] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_selects_parent_content_before_strict_findings_validation[[{"file": "store/cache.go", "line": 44, "severity": "high", "message": "Mutex is copied by value."}]] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_child_cannot_replace_parent_regardless_of_order[False-agentId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_child_cannot_replace_parent_regardless_of_order[False-parentToolCallId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_child_cannot_replace_parent_regardless_of_order[True-agentId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_child_cannot_replace_parent_regardless_of_order[True-parentToolCallId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_commentary_and_tool_requests_are_not_answers[data0] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_commentary_and_tool_requests_are_not_answers[data1] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_unphased_parent_is_supported[absent] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_unphased_parent_is_supported[None] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_malformed_candidate_fields_are_transport_failures[data0] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_malformed_candidate_fields_are_transport_failures[data1] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_record_type_is_not_ignored_as_metadata[event0] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_record_type_is_not_ignored_as_metadata[event1] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_record_type_is_not_ignored_as_metadata[event2] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[-agentId] PASSED [ 22%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[-parentToolCallId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[False-agentId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[False-parentToolCallId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[0-agentId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[0-parentToolCallId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[value3-agentId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_ownership_does_not_default_to_root[value3-parentToolCallId] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_unsupported_response_format_does_not_fall_back_to_text PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[missing] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[nonzero] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[bool] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[missing_code] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[string_code] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[missing_id] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[blank_id] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[invalid_id] PASSED [ 23%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[duplicate] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[trailing] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[root_error] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_incomplete_or_failed_stream_cannot_report_clean[child_result_only] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[[]] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[null] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[42] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[true] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback["string"] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{}] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{"type": "PRIVATE] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{"type": "assistant.message"}] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{"type": "assistant.message", "data": null}] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_framing_has_safe_line_diagnostics_without_fallback[{"type": "assistant.message", "data": []}] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data0] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data1] PASSED [ 24%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data2] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data3] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data4] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_invalid_parent_data_is_not_a_findings_schema_error[data5] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[missing] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[blank] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[child_only] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[multiple] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_missing_or_ambiguous_parent_is_not_rescued[unphased_multiple] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[session.error-agentId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[session.error-parentToolCallId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[result-agentId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[result-parentToolCallId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[assistant.message-agentId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_child_completion_errors_and_invalid_findings_do_not_overrule_root[assistant.message-parentToolCallId] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_crlf_blank_lines_and_non_message_events_do_not_contribute_content PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[not JSON] PASSED [ 25%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[Here are findings: []] PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[{}] PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[[{"file": "store/cache.go", "line": 44, "severity": "invalid", "message": "Mutex is copied by value."}]] PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_still_obeys_strict_findings_schema[[{"file": "store/cache.go", "line": "44", "severity": "high", "message": "Mutex is copied by value."}]] PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_selected_parent_keeps_fence_handling_and_file_guard PASSED [ 26%]
tests/test_extract.py::TestCliResponseIsolation::test_bad_stream_does_not_discard_another_run PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_plain_json_needs_no_stripping PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_a_json_labelled_fence_is_stripped PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_an_unlabelled_fence_is_stripped PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_surrounding_whitespace_is_ignored PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_a_json_labelled_fence_wins_over_an_earlier_unlabelled_one PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_an_unlabelled_fence_still_works_when_it_is_the_only_one PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_a_backtick_inside_a_message_fails_loudly_rather_than_quietly PASSED [ 26%]
tests/test_extract.py::TestFenceStripping::test_a_fenced_response_extracts_normally PASSED [ 26%]
tests/test_extract.py::TestNoHeuristicSalvage::test_prose_around_bare_json_is_a_failure_not_a_rescue PASSED [ 26%]
tests/test_extract.py::TestNoHeuristicSalvage::test_prose_outside_a_fence_is_still_extracted PASSED [ 26%]
tests/test_extract.py::TestSchemaValidation::test_a_well_formed_response_yields_findings PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_an_empty_array_is_a_clean_review_not_a_failure PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_non_array_payload_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_unparseable_text_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[file] PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[line] PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[severity] PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_every_required_field_is_required[message] PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_severity_outside_the_allowed_set_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_all_four_allowed_severities_are_accepted PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_string_line_number_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_boolean_line_number_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_a_line_number_below_one_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_line_zero_is_rejected PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_line_one_is_accepted PASSED [ 27%]
tests/test_extract.py::TestSchemaValidation::test_an_element_that_is_not_an_object_is_rejected PASSED [ 27%]
tests/test_extract.py::TestFileGuard::test_a_finding_naming_a_file_outside_the_diff_is_rejected PASSED [ 28%]
tests/test_extract.py::TestFileGuard::test_rejecting_one_finding_does_not_discard_its_siblings PASSED [ 28%]
tests/test_extract.py::TestFileGuard::test_the_guard_is_skipped_when_no_file_list_is_given PASSED [ 28%]
tests/test_extract.py::TestFailuresAreLoud::test_a_failure_records_which_model_and_which_run PASSED [ 28%]
tests/test_extract.py::TestFailuresAreLoud::test_a_failure_keeps_an_excerpt_of_what_was_returned PASSED [ 28%]
tests/test_extract.py::TestFailuresAreLoud::test_the_excerpt_is_bounded_so_a_huge_reply_cannot_flood_the_report PASSED [ 28%]
tests/test_extract.py::TestFailuresAreLoud::test_an_unusable_run_is_not_silently_ignored PASSED [ 28%]
tests/test_extract.py::TestAcrossRuns::test_findings_carry_their_model_and_run PASSED [ 28%]
tests/test_extract.py::TestAcrossRuns::test_one_bad_run_does_not_lose_the_good_ones PASSED [ 28%]
tests/test_extract.py::TestAcrossRuns::test_a_report_knows_whether_anything_failed PASSED [ 28%]
tests/test_extract.py::TestAcrossRuns::test_duplicate_findings_are_preserved_for_the_merge_step_to_count PASSED [ 28%]
tests/test_filelock.py::test_lock_is_exclusive_across_real_processes PASSED [ 28%]
tests/test_filelock.py::test_lock_can_be_taken_and_released PASSED       [ 28%]
tests/test_filelock.py::test_lock_creates_the_lock_file_when_absent PASSED [ 28%]
tests/test_filelock.py::test_lock_file_is_separate_from_the_file_being_appended PASSED [ 28%]
tests/test_filelock.py::test_lock_is_released_when_the_body_raises PASSED [ 28%]
tests/test_filelock.py::test_lock_times_out_when_already_held PASSED     [ 29%]
tests/test_filelock.py::test_timeout_message_explains_how_to_recover PASSED [ 29%]
tests/test_filelock.py::test_lock_does_not_truncate_an_existing_lock_file PASSED [ 29%]
tests/test_gates.py::test_runner_error_is_failed_gate_evidence PASSED    [ 29%]
tests/test_gates.py::test_go_command_gate_passes_when_command_exits_zero[build] PASSED [ 29%]
tests/test_gates.py::test_go_command_gate_passes_when_command_exits_zero[vet] PASSED [ 29%]
tests/test_gates.py::test_build_gate_fails_with_stderr_details_when_build_exits_nonzero PASSED [ 29%]
tests/test_gates.py::test_vet_gate_fails_when_vet_exits_nonzero PASSED   [ 29%]
tests/test_gates.py::test_format_gate_fails_on_printed_filenames_despite_zero_exit_code PASSED [ 29%]
tests/test_gates.py::test_format_gate_passes_when_gofmt_prints_nothing PASSED [ 29%]
tests/test_gates.py::test_format_gate_names_unformatted_files_in_summary PASSED [ 29%]
tests/test_gates.py::test_format_gate_ignores_blank_lines_in_gofmt_output PASSED [ 29%]
tests/test_gates.py::test_format_gate_fails_when_gofmt_itself_errors PASSED [ 29%]
tests/test_gates.py::test_test_gate_passes_when_go_test_exits_zero PASSED [ 29%]
tests/test_gates.py::test_test_gate_fails_and_preserves_raw_output PASSED [ 29%]
tests/test_gates.py::test_test_gate_skips_when_go_reports_no_test_files PASSED [ 29%]
tests/test_gates.py::test_test_gate_failure_wins_over_no_test_files_marker PASSED [ 30%]
tests/test_gates.py::test_race_gate_runs_go_test_with_race_flag PASSED   [ 30%]
tests/test_gates.py::test_race_gate_is_skipped_when_disabled PASSED      [ 30%]
tests/test_gates.py::test_gate_fails_and_names_tool_when_executable_missing PASSED [ 30%]
tests/test_gates.py::test_test_gate_skips_when_download_chatter_accompanies_no_test_files PASSED [ 30%]
tests/test_gates.py::test_race_gate_skips_when_no_packages_have_tests PASSED [ 30%]
tests/test_gates.py::test_race_gate_still_passes_when_tests_actually_ran PASSED [ 30%]
tests/test_gates.py::test_format_gate_ignores_files_belonging_to_a_nested_module PASSED [ 30%]
tests/test_gates.py::test_format_gate_still_reports_unformatted_files_in_the_root_module PASSED [ 30%]
tests/test_gates.py::test_format_gate_does_not_fail_for_line_ending_only_differences PASSED [ 30%]
tests/test_gates.py::test_format_gate_names_line_endings_as_the_cause PASSED [ 30%]
tests/test_gates.py::test_format_gate_still_fails_when_a_crlf_file_is_also_badly_formatted PASSED [ 30%]
tests/test_gates.py::test_format_gate_reports_a_genuine_problem_even_beside_a_line_ending_one PASSED [ 30%]
tests/test_gates.py::test_default_gates_covers_all_five_signals_in_order PASSED [ 30%]
tests/test_gates.py::test_default_gates_can_disable_race_without_removing_it PASSED [ 30%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[staticcheck] PASSED [ 30%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[errcheck] PASSED [ 30%]
tests/test_gates.py::test_advisory_gate_skips_when_tool_is_missing[govulncheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[staticcheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[errcheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_warns_and_preserves_output_when_tool_finds_something[govulncheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[staticcheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[errcheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gate_passes_when_tool_exits_zero[govulncheck] PASSED [ 31%]
tests/test_gates.py::test_advisory_gates_returns_all_optional_review_signals PASSED [ 31%]
tests/test_gates_makefile.py::TestBuildGate::test_a_build_target_is_preferred_over_go_build PASSED [ 31%]
tests/test_gates_makefile.py::TestBuildGate::test_without_a_build_target_go_build_still_runs PASSED [ 31%]
tests/test_gates_makefile.py::TestBuildGate::test_a_failing_make_target_fails_the_gate PASSED [ 31%]
tests/test_gates_makefile.py::TestTestGate::test_a_test_target_is_preferred_over_go_test PASSED [ 31%]
tests/test_gates_makefile.py::TestTestGate::test_a_failing_make_target_fails_the_gate PASSED [ 31%]
tests/test_gates_makefile.py::TestTestGate::test_no_test_files_is_still_reported_as_skipped_through_make PASSED [ 31%]
tests/test_gates_makefile.py::TestTestGate::test_a_real_test_run_through_make_is_not_downgraded PASSED [ 31%]
tests/test_gates_makefile.py::TestTheOtherGatesAreNotDelegated::test_the_format_gate_ignores_a_makefile PASSED [ 31%]
tests/test_gates_makefile.py::TestTheOtherGatesAreNotDelegated::test_the_vet_gate_ignores_a_makefile PASSED [ 32%]
tests/test_gates_makefile.py::test_a_makefile_is_ignored_when_make_is_not_installed PASSED [ 32%]
tests/test_go_selection.py::test_capture_project_version PASSED          [ 32%]
tests/test_go_selection.py::test_invalid_project_version[None] PASSED    [ 32%]
tests/test_go_selection.py::test_invalid_project_version[] PASSED        [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1269] PASSED    [ 32%]
tests/test_go_selection.py::test_invalid_project_version[True] PASSED    [ 32%]
tests/test_go_selection.py::test_invalid_project_version[version4] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[version5] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[go1.26.9] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.26] PASSED    [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.026.9] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.26.09] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.20.9] PASSED  [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.26.9+auto] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.26.9 ] PASSED [ 32%]
tests/test_go_selection.py::test_invalid_project_version[1.27rc1] PASSED [ 33%]
tests/test_go_selection.py::test_cli_override_records_project_version[True] PASSED [ 33%]
tests/test_go_selection.py::test_cli_override_records_project_version[False] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_cli_override_is_not_ambient_fallback[] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_cli_override_is_not_ambient_fallback[auto] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_cli_override_is_not_ambient_fallback[go1.26.9] PASSED [ 33%]
tests/test_go_selection.py::test_config_read_errors[{] PASSED            [ 33%]
tests/test_go_selection.py::test_config_read_errors[[]] PASSED           [ 33%]
tests/test_go_selection.py::test_config_read_errors[{}] PASSED           [ 33%]
tests/test_go_selection.py::test_unreadable_config_does_not_become_unconfigured PASSED [ 33%]
tests/test_go_selection.py::test_request_freezes_relative_path_and_policy PASSED [ 33%]
tests/test_go_selection.py::test_executable_requires_version PASSED      [ 33%]
tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides0] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides1] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides2] PASSED [ 33%]
tests/test_go_selection.py::test_invalid_library_request_is_rejected[overrides3] PASSED [ 33%]
tests/test_go_selection.py::test_no_implicit_or_ancestor_policy PASSED   [ 34%]
tests/test_go_selection.py::test_resolve_verifies_actual_distribution PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[wrong_version] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[version_nonzero] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[version_timed_out] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[version_missing] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[version_runner_error] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_nonzero] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_invalid_json] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_list] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_null] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_missing] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_version] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_root] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_mode] PASSED [ 34%]
tests/test_go_selection.py::test_probe_failure_cannot_verify[env_wrong_type] PASSED [ 34%]
tests/test_go_selection.py::test_different_observed_root_is_rejected_even_when_binary_identity_matches PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_binary] PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_version] PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[wrong_metadata] PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[wrapper] PASSED [ 35%]
tests/test_go_selection.py::test_explicit_candidate_never_falls_back[missing_formatter] PASSED [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[path] PASSED    [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[goroot] PASSED  [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[sdk] PASSED     [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[module_cache] PASSED [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[gopath] PASSED  [ 35%]
tests/test_go_selection.py::test_bounded_discovery_order[default_cache] PASSED [ 35%]
tests/test_go_selection.py::test_discovery_unavailable_does_not_use_ambient PASSED [ 35%]
tests/test_go_selection.py::test_real_probe_failure_is_terminal_and_retains_discovery_diagnostics PASSED [ 35%]
tests/test_go_selection.py::test_unsupported_host_mapping_requires_an_inspectable_installed_path PASSED [ 35%]
tests/test_go_selection.py::test_selected_environment_preserves_project_settings PASSED [ 35%]
tests/test_go_selection.py::test_native_installed_distribution_runtime_formatter_and_minimum PASSED [ 35%]
tests/test_go_selection.py::test_selected_runner_keeps_optional_child_mapping_isolated PASSED [ 36%]
tests/test_index.py::test_lists_every_spike PASSED                       [ 36%]
tests/test_index.py::test_ignores_nested_directories PASSED              [ 36%]
tests/test_index.py::test_reads_the_question_from_the_readme PASSED      [ 36%]
tests/test_index.py::test_question_is_none_when_there_is_no_readme PASSED [ 36%]
tests/test_index.py::test_question_is_none_when_the_readme_has_no_question_section PASSED [ 36%]
tests/test_index.py::test_reports_a_spike_that_has_a_go_mod PASSED       [ 36%]
tests/test_index.py::test_flags_a_spike_missing_its_go_mod PASSED        [ 36%]
tests/test_index.py::test_missing_poc_root_is_an_empty_list_not_an_error PASSED [ 36%]
tests/test_index.py::test_empty_poc_root_is_an_empty_list PASSED         [ 36%]
tests/test_index.py::test_ignores_loose_files_in_poc_root PASSED         [ 36%]
tests/test_index.py::test_results_are_sorted_for_stable_output PASSED    [ 36%]
tests/test_index.py::test_multiline_question_is_collapsed_to_one_line PASSED [ 36%]
tests/test_index.py::test_question_skips_the_blockquote_guidance PASSED  [ 36%]
tests/test_init_repeat.py::test_matching_repeat_is_a_read_only_success[False] PASSED [ 36%]
tests/test_init_repeat.py::test_matching_repeat_is_a_read_only_success[True] PASSED [ 36%]
tests/test_init_repeat.py::test_partial_initialization_is_refused_without_writes[config.json] PASSED [ 37%]
tests/test_init_repeat.py::test_partial_initialization_is_refused_without_writes[state.json] PASSED [ 37%]
tests/test_init_repeat.py::test_existing_atom_entry_is_not_a_fresh_project[True] PASSED [ 37%]
tests/test_init_repeat.py::test_existing_atom_entry_is_not_a_fresh_project[False] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[None-module_path] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[None-build_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[None-test_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[7-module_path] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[7-build_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[7-test_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[value2-module_path] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[value2-build_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[value2-test_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[-module_path] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[-build_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[-test_command] PASSED [ 37%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[   -module_path] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[   -build_command] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_configuration_fields[   -test_command] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_missing_configuration_fields[module_path] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_missing_configuration_fields[build_command] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_missing_configuration_fields[test_command] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[{-config.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[{-state.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[[]-config.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[[]-state.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[\ufffd-config.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_json_records[\ufffd-state.json] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload0] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload1] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload2] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload3] PASSED [ 38%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload4] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload5] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload6] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload7] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload8] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload9] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload10] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload11] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_state_records[payload12] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[None-arguments0---module] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[module example.com/other\n-arguments1-go.mod] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[module example.com/other\n-arguments2-go.mod] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[module example.com/target\n-arguments3---module] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_refuses_module_conflicts[go 1.23.0\n-arguments4-go.mod] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_reports_record_read_failures[relative_path0] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_reports_record_read_failures[relative_path1] PASSED [ 39%]
tests/test_init_repeat.py::test_repeat_reports_record_read_failures[relative_path2] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path0] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path1] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path2] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path3] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path4] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path5] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path6] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path7] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path8] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path9] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path10] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path11] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path12] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path13] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path14] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[missing-relative_path15] PASSED [ 40%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path0] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path1] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path2] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path3] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path4] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path5] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path6] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path7] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path8] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path9] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path10] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path11] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path12] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path13] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path14] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_bundle_files[empty-relative_path15] PASSED [ 41%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload0] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload1] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload2] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload3] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload4] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_invalid_bundle_manifest[payload5] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_bundle_manifest[None] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_bundle_manifest[{] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_bundle_manifest[[]] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_damaged_bundle_manifest[\ufffd] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_missing_local_instruction_reference[None] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_missing_local_instruction_reference[] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_missing_local_instruction_reference[<!-- Atom managed onboarding -->] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_missing_local_instruction_reference[../.atom/atom/AGENTS.md] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[None] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[] PASSED [ 42%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# >>> Atom generated runtime files >>>\n.atom/baseline.json\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# <<< Atom generated runtime files <<<\n# >>> Atom generated runtime files >>>\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# >>> Atom generated runtime files >>>\n# >>> Atom generated runtime files >>>\n# <<< Atom generated runtime files <<<\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# >>> Atom generated runtime files >>>\n# <<< Atom generated runtime files <<<\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_refuses_incomplete_managed_ignore_rules[# >>> Atom generated runtime files >>>\n.atom/baseline.json\n.atom/events.jsonl\n# <<< Atom generated runtime files <<<\n] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_reports_scaffold_read_failures[relative_path0] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_reports_scaffold_read_failures[relative_path1] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_reports_scaffold_read_failures[relative_path2] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_reports_scaffold_read_failures[relative_path3] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_does_not_require_or_inspect_machine_local_files[absent] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_does_not_require_or_inspect_machine_local_files[unusable] PASSED [ 43%]
tests/test_init_repeat.py::test_repeat_succeeds_as_a_real_process PASSED [ 43%]
tests/test_init_repeat.py::test_force_still_resets_a_partial_project PASSED [ 43%]
tests/test_init_repeat.py::test_init_help_explains_no_op_and_destructive_force PASSED [ 43%]
tests/test_invoke.py::test_fixed_evidence_exclusions_reach_probes_and_reviews PASSED [ 43%]
tests/test_invoke.py::test_runner_error_is_not_usable_model_evidence PASSED [ 43%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.TIMED_OUT-None-timed out-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.TIMED_OUT-None-timed out-True] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.TOOL_MISSING-None-CLI not found-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.TOOL_MISSING-None-CLI not found-True] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.RUNNER_ERROR-None-runner error-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.RUNNER_ERROR-None-runner error-True] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.RUNNER_ERROR-0-runner error-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.RUNNER_ERROR-0-runner error-True] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.COMPLETED-2-exited with code 2-False] PASSED [ 44%]
tests/test_invoke.py::test_structured_failure_retains_raw_evidence_without_diagnostic_leak[CommandOutcome.COMPLETED-2-exited with code 2-True] PASSED [ 44%]
tests/test_invoke.py::test_fixed_probe_failure_is_safe_without_fallback PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_requests_structured_review_output_to_isolate_delegated_answers PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_always_disables_custom_instructions PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_always_disables_builtin_mcp_servers PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_names_no_vendor_specific_mcp_servers_by_default PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_extra_mcp_servers_can_be_disabled_by_the_caller PASSED [ 44%]
tests/test_invoke.py::TestMandatoryFlags::test_carries_the_prompt_and_the_model PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_empty_exclusions_preserve_the_exact_probe_command[None] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_empty_exclusions_preserve_the_exact_probe_command[servers1] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_empty_exclusions_preserve_the_exact_probe_command[servers2] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_probe_command_preserves_exclusions_and_caller_input PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_probe_models_forwards_exclusions_and_preserves_call_settings PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_failed_excluded_probe_keeps_diagnostic_and_prevents_review[CommandOutcome.COMPLETED-1-model rejected] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_failed_excluded_probe_keeps_diagnostic_and_prevents_review[CommandOutcome.TIMED_OUT-None-probe timed out] PASSED [ 45%]
tests/test_invoke.py::TestProbeExclusions::test_excluded_probes_preserve_partial_review_reporting PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_probes_every_model PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_a_rejected_model_is_reported_unavailable_with_its_reason PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_no_review_call_happens_before_every_probe_has_run PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_an_unavailable_model_is_never_asked_to_review PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_probing_no_models_returns_nothing_rather_than_failing PASSED [ 45%]
tests/test_invoke.py::TestAvailabilityProbing::test_when_no_model_is_available_the_review_fails_loudly PASSED [ 45%]
tests/test_invoke.py::TestRepetition::test_calls_each_model_three_times_by_default PASSED [ 45%]
tests/test_invoke.py::TestRepetition::test_run_count_is_overridable PASSED [ 45%]
tests/test_invoke.py::TestRepetition::test_runs_of_one_model_are_byte_identical_calls PASSED [ 46%]
tests/test_invoke.py::TestRepetition::test_every_model_gets_the_same_number_of_runs PASSED [ 46%]
tests/test_invoke.py::TestRepetition::test_runs_are_numbered_from_one PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_a_timeout_is_a_recorded_outcome_not_a_raise PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_a_nonzero_exit_is_recorded_as_a_failed_run PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_one_failing_run_does_not_stop_the_others PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_response_text_is_kept_for_completed_runs PASSED [ 46%]
tests/test_invoke.py::TestPerRunOutcomes::test_native_response_encoding_is_recorded_without_parsing_stdout PASSED [ 46%]
tests/test_invoke.py::TestPartialReviews::test_a_complete_review_is_not_partial PASSED [ 46%]
tests/test_invoke.py::TestPartialReviews::test_one_failed_run_out_of_six_makes_the_whole_review_partial PASSED [ 46%]
tests/test_invoke.py::TestPartialReviews::test_participation_states_completed_over_requested_per_model PASSED [ 46%]
tests/test_invoke.py::TestPartialReviews::test_usable_responses_are_offered_even_when_the_review_is_partial PASSED [ 46%]
tests/test_invoke.py::TestConcurrency::test_default_concurrency_is_the_measured_four PASSED [ 46%]
tests/test_invoke.py::TestConcurrency::test_never_exceeds_the_concurrency_limit PASSED [ 46%]
tests/test_invoke.py::TestConcurrency::test_calls_genuinely_overlap_rather_than_merely_staying_under_the_limit PASSED [ 46%]
tests/test_invoke.py::TestConcurrency::test_all_runs_complete_even_when_they_outnumber_the_workers PASSED [ 46%]
tests/test_invoke.py::TestReportingWhatFailed::test_unavailable_models_are_listed_with_their_reasons PASSED [ 47%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_missing_cli_is_reported_as_tool_missing_not_as_a_refusal PASSED [ 47%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_silent_failure_still_gets_a_reason PASSED [ 47%]
tests/test_invoke.py::TestReportingWhatFailed::test_a_silent_timeout_is_named_by_its_outcome PASSED [ 47%]
tests/test_invoke.py::TestNonsensicalSettings::test_zero_runs_is_rejected_rather_than_reported_as_complete PASSED [ 47%]
tests/test_invoke.py::TestNonsensicalSettings::test_negative_runs_is_rejected PASSED [ 47%]
tests/test_invoke.py::TestNonsensicalSettings::test_zero_concurrency_is_rejected_rather_than_silently_corrected PASSED [ 47%]
tests/test_invoke.py::TestNonsensicalSettings::test_no_models_at_all_is_rejected PASSED [ 47%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_review_command_does_not_contain_the_prompt PASSED [ 47%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_command_length_stays_flat_as_the_prompt_grows PASSED [ 47%]
tests/test_invoke.py::TestThePromptDoesNotTravelInArgv::test_the_prompt_reaches_the_runner_as_stdin PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_the_default_window_is_three_lines PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_identical_lines_merge PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_nearby_lines_merge PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_lines_beyond_the_window_stay_separate PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_the_window_is_configurable PASSED [ 47%]
tests/test_merge.py::TestGroupingByProximity::test_the_same_line_in_different_files_never_merges PASSED [ 48%]
tests/test_merge.py::TestGroupingByProximity::test_a_group_never_spans_more_than_the_window PASSED [ 48%]
tests/test_merge.py::TestGroupingByProximity::test_grouping_does_not_depend_on_the_order_findings_arrive_in PASSED [ 48%]
tests/test_merge.py::TestNothingIsDiscarded::test_every_message_survives_the_merge PASSED [ 48%]
tests/test_merge.py::TestNothingIsDiscarded::test_each_message_is_attributed_to_its_model_and_run PASSED [ 48%]
tests/test_merge.py::TestNothingIsDiscarded::test_each_message_keeps_the_line_it_was_reported_at PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_a_merged_finding_names_the_models_that_reported_it PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_agreement_counts_how_many_runs_of_each_model_reported_it PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_one_run_reporting_a_line_twice_counts_once PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_a_single_model_finding_is_reported_not_suppressed PASSED [ 48%]
tests/test_merge.py::TestAgreement::test_a_finding_from_both_models_is_marked_corroborated PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_two_models_on_different_lines_of_one_group_is_not_corroboration PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_two_models_on_the_same_line_is_still_corroboration PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_agreement_on_one_line_survives_an_unrelated_line_joining_the_group PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_one_model_reporting_twice_on_a_line_is_not_corroboration PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_model_count_still_reports_every_model_in_the_group PASSED [ 48%]
tests/test_merge.py::TestCorroborationMeansTheSameLine::test_a_single_line_group_from_two_models_is_unaffected PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_the_same_defect_at_adjacent_lines_is_reported_as_nearby PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_same_line_agreement_is_not_also_reported_as_nearby PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_agreement_on_one_line_wins_over_a_nearby_report PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_one_model_across_several_lines_is_neither_signal PASSED [ 49%]
tests/test_merge.py::TestNearbyReportsAreTheirOwnSignal::test_a_lone_finding_is_neither_signal PASSED [ 49%]
tests/test_merge.py::TestSeverity::test_disagreeing_severities_are_all_preserved PASSED [ 49%]
tests/test_merge.py::TestSeverity::test_severity_is_not_collapsed_into_one_verdict PASSED [ 49%]
tests/test_merge.py::TestSeverity::test_agreement_on_severity_is_not_reported_as_disagreement PASSED [ 49%]
tests/test_merge.py::TestSeverity::test_the_highest_claimed_severity_is_available_for_ordering PASSED [ 49%]
tests/test_merge.py::TestOrdering::test_findings_are_ordered_by_highest_severity PASSED [ 49%]
tests/test_merge.py::TestOrdering::test_one_model_calling_it_critical_lifts_the_whole_finding PASSED [ 49%]
tests/test_merge.py::TestOrdering::test_equal_severities_are_ordered_predictably PASSED [ 49%]
tests/test_merge.py::TestKnownLimits::test_drift_lets_a_group_reach_further_than_the_window PASSED [ 49%]
tests/test_merge.py::TestEdges::test_severity_ordering_depends_on_the_allowed_list_staying_ordered PASSED [ 49%]
tests/test_merge.py::TestEdges::test_agreement_renders_as_the_fraction_a_report_shows PASSED [ 49%]
tests/test_merge.py::TestEdges::test_no_findings_merge_to_nothing PASSED [ 50%]
tests/test_merge.py::TestEdges::test_a_model_absent_from_the_run_counts_is_rejected PASSED [ 50%]
tests/test_merge.py::TestEdges::test_a_negative_window_is_rejected PASSED [ 50%]
tests/test_merge.py::TestEdges::test_a_zero_window_means_exact_line_matching PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_model_with_no_runs_cannot_have_reported_anything PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_model_that_completed_no_runs_is_allowed_to_report_nothing PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_a_negative_run_count_is_rejected PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_more_reporting_runs_than_runs_total_is_rejected PASSED [ 50%]
tests/test_merge.py::TestImpossibleAgreementIsRefused::test_an_unrecognised_severity_names_what_is_allowed PASSED [ 50%]
tests/test_module_rules.py::test_capture_preserves_selected_order_and_original_bytes PASSED [ 50%]
tests/test_module_rules.py::test_capture_optional_sources_and_ignores_unselected_paths[sources0] PASSED [ 50%]
tests/test_module_rules.py::test_capture_optional_sources_and_ignores_unselected_paths[sources1] PASSED [ 50%]
tests/test_module_rules.py::test_capture_optional_sources_and_ignores_unselected_paths[sources2] PASSED [ 50%]
tests/test_module_rules.py::test_capture_optional_sources_and_ignores_unselected_paths[sources3] PASSED [ 50%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[] PASSED [ 50%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[ \r\n] PASSED [ 50%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[a\x00b] PASSED [ 50%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[\xff] PASSED [ 51%]
tests/test_module_rules.py::test_capture_invalid_present_sources_fail[None] PASSED [ 51%]
tests/test_module_rules.py::test_capture_non_directory_guide_parent_is_not_absence[.atom] PASSED [ 51%]
tests/test_module_rules.py::test_capture_non_directory_guide_parent_is_not_absence[.atom/atom] PASSED [ 51%]
tests/test_module_rules.py::test_capture_non_directory_guide_parent_is_not_absence[.atom/atom/skills/atom/references] PASSED [ 51%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[outside] SKIPPED [ 51%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[dangling] SKIPPED [ 51%]
tests/test_module_rules.py::test_capture_refuses_unsafe_targets[duplicate] SKIPPED [ 51%]
tests/test_module_rules.py::test_capture_read_failure_is_not_absence PASSED [ 51%]
tests/test_module_rules.py::test_capture_refuses_resolved_escape_before_read PASSED [ 51%]
tests/test_module_rules.py::test_capture_refuses_duplicate_resolved_targets PASSED [ 51%]
tests/test_module_rules.py::test_capture_dangling_source_is_not_absence PASSED [ 51%]
tests/test_module_rules.py::test_capture_unreadable_traversal_is_not_absence PASSED [ 51%]
tests/test_module_rules.py::test_capture_skip_modes_do_not_access_candidates[False-False-disabled] PASSED [ 51%]
tests/test_module_rules.py::test_capture_skip_modes_do_not_access_candidates[True-True-fixed-evidence] PASSED [ 51%]
tests/test_module_rules.py::test_capture_skip_modes_do_not_access_candidates[False-True-fixed-evidence] PASSED [ 51%]
tests/test_module_rules.py::test_review_delivers_frozen_guidance_to_every_run PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[hash] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[source] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[length] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[status] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[empty] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[fixed] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[duplicate] PASSED [ 52%]
tests/test_module_rules.py::test_review_rejects_invalid_policy_before_execution[order] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags0-loaded] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags1-not-found] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags2-disabled] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags3-fixed-evidence] PASSED [ 52%]
tests/test_module_rules.py::test_cli_rule_metadata_never_serializes_policy[flags4-fixed-evidence] PASSED [ 52%]
tests/test_onboarding.py::test_init_records_the_makefile_commands_it_will_actually_run PASSED [ 52%]
tests/test_onboarding.py::test_init_records_a_partial_makefile_one_gate_at_a_time PASSED [ 52%]
tests/test_onboarding.py::test_init_infers_module_and_installs_local_instructions PASSED [ 53%]
tests/test_onboarding.py::test_init_skill_delegates_baseline_and_scaffold_to_one_cli_command PASSED [ 53%]
tests/test_onboarding.py::test_init_updates_existing_instructions_once PASSED [ 53%]
tests/test_onboarding.py::test_init_removes_legacy_external_atom_references PASSED [ 53%]
tests/test_onboarding.py::test_init_requires_module_when_go_mod_is_absent PASSED [ 53%]
tests/test_onboarding.py::test_init_ignores_only_generated_atom_runtime_files PASSED [ 53%]
tests/test_onboarding.py::test_init_preserves_existing_gitignore_and_updates_it_once PASSED [ 53%]
tests/test_onboarding.py::test_init_replaces_stale_atom_gitignore_block PASSED [ 53%]
tests/test_onboarding.py::test_init_preserves_existing_gitignore_newlines PASSED [ 53%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# >>> Atom generated runtime files >>>\n.atom/first.json\n# >>> Atom generated runtime files >>>\n.atom/second.json\n# <<< Atom generated runtime files <<<\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# >>> Atom generated runtime files >>>\n.atom/first.json\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# <<< Atom generated runtime files <<<\n.atom/first.json\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_refuses_ambiguous_atom_gitignore_markers[# <<< Atom generated runtime files <<<\n# >>> Atom generated runtime files >>>\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_separates_the_managed_block_without_changing_existing_content[vendor/-\n\n] PASSED [ 53%]
tests/test_onboarding.py::test_init_separates_the_managed_block_without_changing_existing_content[vendor/\n\n-] PASSED [ 53%]
tests/test_onboarding.py::test_gitignore_update_keeps_original_when_atomic_replace_fails PASSED [ 53%]
tests/test_onboarding.py::test_init_reports_an_unreadable_gitignore_without_a_traceback PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_help_works_in_a_real_process PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_adds_commands_without_onboarding PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[exact] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[case] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[quoted] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[trailing-separator] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[dot] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_does_not_rewrite_an_equivalent_entry[variable] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_unsupported_platform_without_io[linux] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_unsupported_platform_without_io[darwin] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_an_invalid_registry_value[C:\\keep-7] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_an_invalid_registry_value[value1-7] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_rejects_an_invalid_registry_value[123-1] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_creates_a_missing_user_path[key] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_creates_a_missing_user_path[value] PASSED [ 54%]
tests/test_pathsetup.py::test_setup_path_reports_registry_permission_errors[OpenKey-read] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_registry_permission_errors[QueryValueEx-read] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_registry_permission_errors[CreateKeyEx-write] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_registry_permission_errors[SetValueEx-write] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_partial_notification_failure[timeout-False] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_partial_notification_failure[timeout-True] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_partial_notification_failure[os-error-False] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_partial_notification_failure[os-error-True] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_rejects_an_ambiguous_scripts_directory[semicolon] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_rejects_an_ambiguous_scripts_directory[nul] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_enforces_the_windows_utf16_length_limit[False-0] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_enforces_the_windows_utf16_length_limit[False-1] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_enforces_the_windows_utf16_length_limit[True-0] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_enforces_the_windows_utf16_length_limit[True-1] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_reports_discovery_errors PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_requires_both_installed_console_scripts[atom.exe] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_requires_both_installed_console_scripts[atom-write-artifact.exe] PASSED [ 55%]
tests/test_pathsetup.py::test_setup_path_requires_both_installed_console_scripts[not-a-file] PASSED [ 56%]
tests/test_pathsetup.py::test_setup_path_prefers_the_default_scheme_when_complete PASSED [ 56%]
tests/test_pathsetup.py::test_setup_path_changes_only_the_user_registry_value PASSED [ 56%]
tests/test_pathsetup.py::test_setup_path_uses_a_pointer_sized_environment_notification PASSED [ 56%]
tests/test_pathsetup.py::test_ordinary_init_does_not_opt_in_to_path_setup PASSED [ 56%]
tests/test_pathsetup.py::test_setup_path_prints_literal_powershell_executable_paths PASSED [ 56%]
tests/test_pathsetup.py::test_onboarding_documents_one_time_path_setup[relative0] PASSED [ 56%]
tests/test_pathsetup.py::test_onboarding_documents_one_time_path_setup[relative1] PASSED [ 56%]
tests/test_pathsetup.py::test_readme_documents_the_setup_command_and_session_limitation PASSED [ 56%]
tests/test_phases.py::test_a_well_formed_phase_directory_is_recognised PASSED [ 56%]
tests/test_phases.py::test_a_single_digit_phase_number_is_not_a_phase_directory PASSED [ 56%]
tests/test_phases.py::test_an_uppercase_slug_is_not_a_phase_directory PASSED [ 56%]
tests/test_phases.py::test_a_directory_merely_containing_a_phase_name_is_not_one PASSED [ 56%]
tests/test_phases.py::test_a_file_named_like_a_phase_directory_is_not_one PASSED [ 56%]
tests/test_phases.py::test_a_non_phase_directory_is_ignored PASSED       [ 56%]
tests/test_phases.py::test_a_non_phase_directory_produces_no_problem PASSED [ 56%]
tests/test_phases.py::test_the_phase_plan_document_beside_the_phases_is_not_a_phase PASSED [ 57%]
tests/test_phases.py::test_phases_are_ordered_lexically PASSED           [ 57%]
tests/test_phases.py::test_the_two_digit_prefix_makes_lexical_order_numeric PASSED [ 57%]
tests/test_phases.py::test_phase_ten_sorts_after_phase_nine PASSED       [ 57%]
tests/test_phases.py::test_a_phase_branch_names_the_current_phase PASSED [ 57%]
tests/test_phases.py::test_the_branch_wins_over_the_lexically_greatest_phase PASSED [ 57%]
tests/test_phases.py::test_main_falls_back_to_the_lexically_greatest_phase PASSED [ 57%]
tests/test_phases.py::test_a_detached_head_falls_back_to_the_lexically_greatest_phase PASSED [ 57%]
tests/test_phases.py::test_an_unrelated_branch_name_falls_back PASSED    [ 57%]
tests/test_phases.py::test_a_branch_that_cannot_be_read_falls_back PASSED [ 57%]
tests/test_phases.py::test_a_branch_naming_a_missing_phase_directory_is_still_current PASSED [ 57%]
tests/test_phases.py::test_a_phase_with_no_directory_is_marked_not_started PASSED [ 57%]
tests/test_phases.py::test_a_phase_with_no_directory_reports_every_artifact_absent PASSED [ 57%]
tests/test_phases.py::test_a_phase_with_no_directory_is_not_an_error PASSED [ 57%]
tests/test_phases.py::test_a_project_with_no_phases_has_no_current_phase PASSED [ 57%]
tests/test_phases.py::test_a_project_with_no_phases_is_not_an_error PASSED [ 57%]
tests/test_phases.py::test_an_absent_specs_directory_is_not_a_crash PASSED [ 58%]
tests/test_phases.py::test_creating_an_artifact_in_an_old_phase_does_not_make_it_current PASSED [ 58%]
tests/test_phases.py::test_editing_an_artifact_in_an_old_phase_does_not_make_it_current PASSED [ 58%]
tests/test_phases.py::test_the_current_phase_is_stable_when_every_directory_is_touched_in_reverse_order PASSED [ 58%]
tests/test_phases.py::test_the_required_artifacts_are_the_seven_named PASSED [ 58%]
tests/test_phases.py::test_an_unexpected_file_in_a_phase_directory_is_not_required PASSED [ 58%]
tests/test_phases.py::test_an_unexpected_file_does_not_appear_in_the_artifact_report PASSED [ 58%]
tests/test_phases.py::test_an_existing_artifact_is_present PASSED        [ 58%]
tests/test_phases.py::test_a_missing_artifact_is_absent PASSED           [ 58%]
tests/test_phases.py::test_an_empty_artifact_file_is_still_present PASSED [ 58%]
tests/test_phases.py::test_a_directory_named_like_an_artifact_is_not_present PASSED [ 58%]
tests/test_phases.py::test_the_artifact_report_has_exactly_two_states PASSED [ 58%]
tests/test_phases.py::test_a_one_byte_artifact_is_present PASSED         [ 58%]
tests/test_phases.py::test_a_document_with_no_headings_is_present PASSED [ 58%]
tests/test_phases.py::test_a_document_of_only_headings_is_present PASSED [ 58%]
tests/test_phases.py::test_no_artifact_but_the_poc_report_is_ever_opened PASSED [ 58%]
tests/test_phases.py::test_a_ran_poc_requires_a_brief PASSED             [ 59%]
tests/test_phases.py::test_a_skipped_poc_does_not_require_a_brief PASSED [ 59%]
tests/test_phases.py::test_a_skipped_phase_with_no_brief_is_complete PASSED [ 59%]
tests/test_phases.py::test_a_skipped_phase_requires_the_other_six PASSED [ 59%]
tests/test_phases.py::test_an_unrecognised_status_is_reported_as_a_problem PASSED [ 59%]
tests/test_phases.py::test_an_unrecognised_status_still_requires_the_brief PASSED [ 59%]
tests/test_phases.py::test_a_missing_status_field_is_reported_and_requires_the_brief PASSED [ 59%]
tests/test_phases.py::test_the_unrecognised_status_problem_names_the_value_it_found PASSED [ 59%]
tests/test_phases.py::test_an_absent_poc_report_makes_both_it_and_the_brief_absent PASSED [ 59%]
tests/test_phases.py::test_an_absent_poc_report_raises_no_problem_beyond_the_absences PASSED [ 59%]
tests/test_phases.py::test_a_phase_with_no_poc_report_still_requires_the_brief PASSED [ 59%]
tests/test_phases.py::test_the_status_vocabulary_is_exactly_two_tokens PASSED [ 59%]
tests/test_phases.py::test_a_status_containing_skipped_as_a_substring_is_not_skipped PASSED [ 59%]
tests/test_phases.py::test_the_prose_status_values_this_repo_used_before_are_not_accepted PASSED [ 59%]
tests/test_phases.py::test_status_matching_is_case_sensitive PASSED      [ 59%]
tests/test_phases.py::test_an_unquoted_status_is_recognised PASSED       [ 59%]
tests/test_phases.py::test_a_truncated_design_spec_is_reported_present PASSED [ 60%]
tests/test_phases.py::test_no_rendering_describes_any_artifact_as_complete PASSED [ 60%]
tests/test_phases.py::test_the_report_exposes_no_completeness_field PASSED [ 60%]
tests/test_phases.py::test_a_two_section_tdd_log_is_present PASSED       [ 60%]
tests/test_phases.py::test_the_real_phase_one_tdd_log_is_present PASSED  [ 60%]
tests/test_phases.py::test_the_real_repository_resolves_eight_phases PASSED [ 60%]
tests/test_phases.py::test_the_real_repository_orders_phases_one_through_eight PASSED [ 60%]
tests/test_phases.py::test_phases_one_through_five_have_every_required_artifact PASSED [ 60%]
tests/test_phases.py::test_the_real_phase_one_is_complete_despite_having_no_brief PASSED [ 60%]
tests/test_phases.py::test_the_real_phase_six_is_missing_exactly_its_unwritten_artifacts PASSED [ 60%]
tests/test_phases.py::test_a_real_detached_head_falls_back_to_lexical PASSED [ 60%]
tests/test_phases.py::test_a_real_phase_branch_resolves_to_its_directory PASSED [ 60%]
tests/test_phases.py::test_a_real_clone_preserves_phase_ordering PASSED  [ 60%]
tests/test_phases.py::test_a_problem_in_a_non_current_phase_is_still_reported PASSED [ 60%]
tests/test_phases.py::test_a_reported_problem_names_the_phase_it_came_from PASSED [ 60%]
tests/test_phases.py::test_problems_are_reported_in_phase_order PASSED   [ 60%]
tests/test_phases.py::test_the_current_phase_problem_is_reported_exactly_once PASSED [ 60%]
tests/test_phases.py::test_a_clean_tree_still_reports_no_problems PASSED [ 61%]
tests/test_plugin.py::test_the_plugin_manifest_declares_agent_plugins_1_0 PASSED [ 61%]
tests/test_plugin.py::test_the_plugin_manifest_uses_only_allowed_fields PASSED [ 61%]
tests/test_plugin.py::test_no_command_shares_a_name_with_a_skill PASSED  [ 61%]
tests/test_plugin.py::test_the_plugin_owns_the_atom_command_namespace PASSED [ 61%]
tests/test_plugin.py::test_no_command_shares_a_name_with_the_plugin PASSED [ 61%]
tests/test_plugin.py::test_the_atom_router_is_available_as_start PASSED  [ 61%]
tests/test_plugin.py::test_no_skill_shares_a_name_with_the_plugin PASSED [ 61%]
tests/test_plugin.py::test_the_plugin_exposes_exactly_the_compact_skill_names PASSED [ 61%]
tests/test_plugin.py::test_the_marketplace_lists_the_plugin_by_its_manifest_name PASSED [ 61%]
tests/test_plugin.py::test_the_marketplace_sources_the_repository_root PASSED [ 61%]
tests/test_plugin.py::test_every_atom_skill_directory_is_discoverable PASSED [ 61%]
tests/test_pr_checkout_integration.py::test_real_git_merge_base_and_dirty_original_preserved PASSED [ 61%]
tests/test_pr_checkout_integration.py::test_native_cli_uses_real_checkout_and_cleans_it PASSED [ 61%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[] PASSED [ 61%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[not a URL] PASSED [ 61%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[http://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com.attacker.test/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com:443/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://user:password@dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/other%2fproject/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/other%5cproject/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/%2e%2e/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/%00/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/bad%zz/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/project/_git/repository/pullrequest/0] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/project/_git/repository/pullrequest/-1] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/project/_git/repository/pullrequest/42/extra] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[https://dev.azure.com/example/project/_git/repository/pullrequest/42\n] PASSED [ 62%]
tests/test_pull_request.py::test_unsafe_pr_url_starts_no_command[ https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TOOL_MISSING-None-https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 62%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TOOL_MISSING-None-https://dev.azure.com/example/project/_git/repository/pullrequest/42?_a=files#discussion] PASSED [ 62%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TOOL_MISSING-None-https://example.visualstudio.com/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TIMED_OUT-None-https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TIMED_OUT-None-https://dev.azure.com/example/project/_git/repository/pullrequest/42?_a=files#discussion] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.TIMED_OUT-None-https://example.visualstudio.com/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.RUNNER_ERROR-0-https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.RUNNER_ERROR-0-https://dev.azure.com/example/project/_git/repository/pullrequest/42?_a=files#discussion] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.RUNNER_ERROR-0-https://example.visualstudio.com/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.COMPLETED-1-https://dev.azure.com/example/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.COMPLETED-1-https://dev.azure.com/example/project/_git/repository/pullrequest/42?_a=files#discussion] PASSED [ 63%]
tests/test_pull_request.py::test_metadata_failure_stops_before_clone[CommandOutcome.COMPLETED-1-https://example.visualstudio.com/project/_git/repository/pullrequest/42] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change0] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change1] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change2] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change3] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change4] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change5] PASSED [ 63%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change6] PASSED [ 64%]
tests/test_pull_request.py::test_invalid_metadata_stops_before_clone[change7] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone[{] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone[[]] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone[null] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone[{}] PASSED [ 64%]
tests/test_pull_request.py::test_malformed_metadata_stops_before_clone["text"] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://user:password@dev.azure.com/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://someone@dev.azure.com/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://example@attacker.test/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://example@dev.azure.com/example/project/_git/different] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://example@dev.azure.com:444/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[https://example@dev.azure.com/example/project/_git/repository\n] PASSED [ 64%]
tests/test_pull_request.py::test_metadata_remote_identity_is_checked[ https://example@dev.azure.com/example/project/_git/repository] PASSED [ 64%]
tests/test_pull_request.py::test_local_scope_is_required[missing module] PASSED [ 64%]
tests/test_pull_request.py::test_local_scope_is_required[wrong origin] PASSED [ 64%]
tests/test_pull_request.py::test_local_scope_is_required[ssh origin] PASSED [ 65%]
tests/test_pull_request.py::test_local_scope_is_required[outside root] PASSED [ 65%]
tests/test_pull_request.py::test_clone_failure_is_cleaned PASSED         [ 65%]
tests/test_pull_request.py::test_independent_clone_and_pinned_checkout PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command0-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb-0-source moved] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command1-invalid-0-commit ID] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command2--0-exactly one] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command3-cccccccccccccccccccccccccccccccccccccccc\nbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb-0-exactly one] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command4--1-checking out] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command5-missing.go\x00-0-missing tracked] PASSED [ 65%]
tests/test_pull_request.py::test_snapshot_failure_prevents_review_and_is_cleaned[command6-dirty-1-clean pinned] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_on_failure_and_interrupt[failure0] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_on_failure_and_interrupt[failure1] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_failure_preserves_primary_error[False] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_failure_preserves_primary_error[True] PASSED [ 65%]
tests/test_pull_request.py::test_cleanup_interruption_names_retained_directory PASSED [ 65%]
tests/test_pull_request.py::test_repository_package_cannot_shadow_cleanup_worker PASSED [ 65%]
tests/test_pull_request.py::test_percent_encoded_names_keep_their_metadata_scope[False] PASSED [ 66%]
tests/test_pull_request.py::test_percent_encoded_names_keep_their_metadata_scope[True] PASSED [ 66%]
tests/test_pull_request.py::test_zero_exit_with_lifecycle_error_is_not_a_snapshot[stage0] PASSED [ 66%]
tests/test_pull_request.py::test_zero_exit_with_lifecycle_error_is_not_a_snapshot[stage1] PASSED [ 66%]
tests/test_pull_request.py::test_cleanup_worker_checks_ownership_and_handles_readonly_files[False] PASSED [ 66%]
tests/test_pull_request.py::test_cleanup_worker_checks_ownership_and_handles_readonly_files[True] PASSED [ 66%]
tests/test_pull_request.py::test_cleanup_success_exit_still_requires_path_absence PASSED [ 66%]
tests/test_pull_request.py::test_pr_module_must_still_have_go_mod_file PASSED [ 66%]
tests/test_report.py::test_render_text_shows_every_gate_with_status_and_duration PASSED [ 66%]
tests/test_report.py::test_render_text_shows_details_for_failed_gates_only PASSED [ 66%]
tests/test_report.py::test_render_text_omits_details_for_passing_gates PASSED [ 66%]
tests/test_report.py::test_render_text_includes_warnings PASSED          [ 66%]
tests/test_report.py::test_render_text_without_colour_emits_no_escape_codes PASSED [ 66%]
tests/test_report.py::test_render_text_with_colour_emits_escape_codes PASSED [ 66%]
tests/test_report.py::test_render_json_is_valid_json_for_a_passing_report PASSED [ 66%]
tests/test_report.py::test_render_json_is_valid_json_for_a_failing_report PASSED [ 66%]
tests/test_report.py::test_render_json_includes_a_schema_version PASSED  [ 67%]
tests/test_report.py::test_render_json_includes_every_gate_with_its_evidence PASSED [ 67%]
tests/test_report.py::test_a_spike_that_answered_is_not_rendered_as_a_failed_stage PASSED [ 67%]
tests/test_report.py::test_an_answering_stage_says_it_answered_rather_than_that_it_exited PASSED [ 67%]
tests/test_report.py::test_a_refuted_spike_is_not_rendered_as_a_failure_either PASSED [ 67%]
tests/test_report.py::test_a_crashed_spike_is_still_rendered_as_a_failure PASSED [ 67%]
tests/test_report.py::test_a_crash_explains_that_exit_2_was_a_panic_not_a_verdict PASSED [ 67%]
tests/test_report.py::test_the_spike_output_is_shown_even_when_nothing_failed PASSED [ 67%]
tests/test_report.py::test_json_reports_no_failed_stage_for_a_spike_that_answered PASSED [ 67%]
tests/test_report.py::test_json_exposes_answered_separately_from_ran PASSED [ 67%]
tests/test_report.py::test_stderr_is_rendered_before_stdout PASSED       [ 67%]
tests/test_review_formatting.py::test_clean_changed_file_is_not_blocked_by_untouched_formatting PASSED [ 67%]
tests/test_review_formatting.py::test_fixed_evidence_keeps_changed_file_formatting_and_one_diff_capture PASSED [ 67%]
tests/test_review_formatting.py::test_staged_formatting_uses_index_snapshot_not_working_file[clean-index-dirty-worktree] PASSED [ 67%]
tests/test_review_formatting.py::test_staged_formatting_uses_index_snapshot_not_working_file[dirty-index-clean-worktree] PASSED [ 67%]
tests/test_review_formatting.py::test_staged_formatting_uses_index_snapshot_not_working_file[worktree-file-absent] PASSED [ 67%]
tests/test_review_formatting.py::test_branch_formatting_uses_committed_content_despite_dirty_working_file PASSED [ 68%]
tests/test_review_formatting.py::test_pure_rename_formats_destination_and_preserves_canonical_diff_path PASSED [ 68%]
tests/test_review_formatting.py::test_no_surviving_go_files_skips_formatter_with_explicit_scope[empty] PASSED [ 68%]
tests/test_review_formatting.py::test_no_surviving_go_files_skips_formatter_with_explicit_scope[non-go] PASSED [ 68%]
tests/test_review_formatting.py::test_no_surviving_go_files_skips_formatter_with_explicit_scope[deleted] PASSED [ 68%]
tests/test_review_formatting.py::test_module_boundary_exclusions_are_explicit_without_checking_other_modules PASSED [ 68%]
tests/test_review_formatting.py::test_prompt_names_selected_formatting_scope_without_claiming_module_scan[True] PASSED [ 68%]
tests/test_review_formatting.py::test_prompt_names_selected_formatting_scope_without_claiming_module_scan[False] PASSED [ 68%]
tests/test_review_formatting.py::test_non_regular_selected_go_entry_is_refused_before_formatter_or_models PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[parent-path] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[absolute-path] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[windows-path] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[unmerged] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[unknown-status] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[bad-mode] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_manifest_is_refused_without_empty_scope_success[bad-identity] PASSED [ 68%]
tests/test_review_formatting.py::test_invalid_utf8_is_required_formatting_failure_not_replacement_success[DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_invalid_utf8_is_required_formatting_failure_not_replacement_success[DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_working_file_substituted_with_non_regular_path_is_not_read PASSED [ 69%]
tests/test_review_formatting.py::test_added_and_renamed_go_paths_use_nul_delimited_canonical_names[added] PASSED [ 69%]
tests/test_review_formatting.py::test_added_and_renamed_go_paths_use_nul_delimited_canonical_names[renamed-from-text] PASSED [ 69%]
tests/test_review_formatting.py::test_added_and_renamed_go_paths_use_nul_delimited_canonical_names[unicode-space] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[crlf-DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[crlf-DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[mixed-endings-DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[mixed-endings-DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[crlf-real-formatting-defect-DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[crlf-real-formatting-defect-DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[utf8-DiffSource.WORKING] PASSED [ 69%]
tests/test_review_formatting.py::test_selected_bytes_are_preserved_and_only_line_endings_are_normalized[utf8-DiffSource.STAGED] PASSED [ 69%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[missing] PASSED [ 69%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[timeout] PASSED [ 69%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[runner-error] PASSED [ 70%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[syntax-error] PASSED [ 70%]
tests/test_review_formatting.py::test_formatter_failures_keep_path_and_original_diagnostic[empty-stdout] PASSED [ 70%]
tests/test_review_formatting.py::test_working_file_movement_after_diff_capture_blocks_models PASSED [ 70%]
tests/test_review_formatting.py::test_snapshot_acquisition_and_blob_transport_fail_closed[git-failure] PASSED [ 70%]
tests/test_review_formatting.py::test_snapshot_acquisition_and_blob_transport_fail_closed[blob-read-failure] PASSED [ 70%]
tests/test_review_formatting.py::test_snapshot_acquisition_and_blob_transport_fail_closed[bad-base64] PASSED [ 70%]
tests/test_review_formatting.py::test_snapshot_acquisition_and_blob_transport_fail_closed[wrong-blob] PASSED [ 70%]
tests/test_review_formatting.py::test_cli_reports_selected_file_formatting_coverage[False] PASSED [ 70%]
tests/test_review_formatting.py::test_cli_reports_selected_file_formatting_coverage[True] PASSED [ 70%]
tests/test_review_formatting.py::test_non_go_type_change_does_not_break_changed_go_snapshot_pairing PASSED [ 70%]
tests/test_review_formatting.py::test_non_format_required_gate_commands_and_failures_remain_unchanged[failing_command0] PASSED [ 70%]
tests/test_review_formatting.py::test_non_format_required_gate_commands_and_failures_remain_unchanged[failing_command1] PASSED [ 70%]
tests/test_review_formatting.py::test_non_format_required_gate_commands_and_failures_remain_unchanged[failing_command2] PASSED [ 70%]
tests/test_review_formatting.py::test_non_format_required_gate_commands_and_failures_remain_unchanged[failing_command3] PASSED [ 70%]
tests/test_review_formatting.py::test_whole_changed_file_defect_blocks_even_when_other_snapshot_is_clean[DiffSource.WORKING] PASSED [ 70%]
tests/test_review_formatting.py::test_whole_changed_file_defect_blocks_even_when_other_snapshot_is_clean[DiffSource.STAGED] PASSED [ 70%]
tests/test_review_formatting.py::test_whole_changed_file_defect_blocks_even_when_other_snapshot_is_clean[DiffSource.BRANCH] PASSED [ 71%]
tests/test_review_formatting.py::test_captured_content_is_reused_when_checks_change_working_tree PASSED [ 71%]
tests/test_review_formatting.py::test_invalid_branch_ref_fails_before_checks_or_models PASSED [ 71%]
tests/test_review_formatting.py::test_untracked_go_file_is_not_added_to_working_diff_scope PASSED [ 71%]
tests/test_review_formatting.py::test_submodule_display_config_cannot_change_manifest_patch_framing[log] PASSED [ 71%]
tests/test_review_formatting.py::test_submodule_display_config_cannot_change_manifest_patch_framing[diff] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[non-go-:] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[non-go-\\] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[deleted-:] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[deleted-\\] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[outside-module-:] PASSED [ 71%]
tests/test_review_formatting.py::test_unread_manifest_paths_do_not_apply_native_source_path_restrictions[outside-module-\\] PASSED [ 71%]
tests/test_review_output.py::test_direct_context_requires_opt_in_before_runner PASSED [ 71%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes0] PASSED [ 71%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes1] PASSED [ 71%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes2] PASSED [ 71%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes3] PASSED [ 72%]
tests/test_review_output.py::test_direct_context_rejects_inconsistent_metadata[changes4] PASSED [ 72%]
tests/test_review_output.py::test_fixed_prompt_freezes_json_documents_and_preserves_diff PASSED [ 72%]
tests/test_review_output.py::test_fixed_evidence_keeps_diff_file_guard PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_names_every_model_that_took_part PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_states_how_many_runs_each_model_completed PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_the_report_describes_the_diff_that_was_reviewed PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_a_model_that_failed_every_run_is_still_named PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_an_unavailable_model_is_named_but_its_error_text_is_not_repeated PASSED [ 72%]
tests/test_review_output.py::TestWhatWasReviewed::test_responses_nobody_could_parse_are_reported PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_findings_are_grouped_under_their_file PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_a_single_line_finding_shows_that_line PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_a_finding_spanning_several_lines_shows_the_span PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_no_bare_finding_count_is_printed PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_every_model_message_is_shown_with_its_author PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_the_report_lists_toolchain_verdicts PASSED [ 72%]
tests/test_review_output.py::TestFindingPresentation::test_agreement_is_shown_as_a_fraction_per_model PASSED [ 73%]
tests/test_review_output.py::TestFindingPresentation::test_disagreement_about_severity_is_visible PASSED [ 73%]
tests/test_review_output.py::TestFindingPresentation::test_findings_appear_in_severity_order PASSED [ 73%]
tests/test_review_output.py::TestFindingPresentation::test_a_review_with_no_findings_says_so_explicitly PASSED [ 73%]
tests/test_review_output.py::TestPartialReviews::test_a_partial_review_is_marked_partial_in_markdown PASSED [ 73%]
tests/test_review_output.py::TestPartialReviews::test_a_complete_review_is_not_marked_partial PASSED [ 73%]
tests/test_review_output.py::TestPartialReviews::test_a_partial_review_is_marked_partial_in_json PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_is_valid_and_carries_a_schema_version PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_review_schema_version_records_the_corroboration_narrowing PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_other_reports_did_not_change_and_keep_their_version PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_findings_with_their_line_span PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_agreement_with_both_halves_of_the_fraction PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_keeps_every_attributed_message PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_names_models_that_produced_nothing PASSED [ 73%]
tests/test_review_output.py::TestJsonContract::test_the_json_reports_unparseable_responses PASSED [ 73%]
tests/test_review_output.py::TestChannelSeparation::test_operational_problems_render_separately_from_the_report PASSED [ 73%]
tests/test_review_output.py::TestChannelSeparation::test_a_clean_review_produces_no_problem_output PASSED [ 74%]
tests/test_review_output.py::TestChannelSeparation::test_the_markdown_report_does_not_repeat_the_problem_text PASSED [ 74%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_knows_it_is_partial_when_a_run_failed PASSED [ 74%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_with_every_run_answered_is_not_partial PASSED [ 74%]
tests/test_review_output.py::TestReviewOutcome::test_an_outcome_knows_when_no_model_produced_anything_usable PASSED [ 74%]
tests/test_review_output.py::TestReviewOutcome::test_a_review_that_ran_but_found_nothing_is_not_treated_as_unusable PASSED [ 74%]
tests/test_review_output.py::TestAnUnreadableReplyIsNotACleanReview::test_a_completed_run_whose_reply_was_unreadable_yields_no_usable_response PASSED [ 74%]
tests/test_review_output.py::TestAnUnreadableReplyIsNotACleanReview::test_such_a_review_does_not_exit_zero PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unreadable_reply_is_left_out_of_the_denominator PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_finding_both_readable_runs_reported_is_not_shown_as_a_dissent PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_completed_without_answering_makes_the_review_partial PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_partial_notice_counts_the_run_that_could_not_be_read PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_payload_reports_answered_runs_alongside_completed_ones PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_that_partly_parsed_still_counts_as_an_answer PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_clean_review_still_counts_every_run_and_is_not_partial PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_model_whose_every_reply_was_unreadable_renders_without_crashing PASSED [ 74%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_missing_run_is_still_partial PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[   \n\t ] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_with_no_findings_in_it_counts_as_silence[I reviewed it and found nothing.] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_returned_nothing_is_named_in_the_report PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[file-guard only] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[schema-invalid] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_only_a_pure_file_guard_rejection_counts_as_an_answer[mixed] PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unreadable_reply_is_not_named_twice PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_answered_is_never_also_counted_as_overruled PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_run_that_answered_despite_a_malformed_element_is_not_called_unreadable PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_is_not_called_a_review_that_produced_nothing PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_gets_its_own_heading PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_partial_total_excludes_an_overruled_reply PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_banner_does_not_promise_stderr_detail PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_the_payload_distinguishes_an_overruled_reply_from_an_unreadable_one PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_a_reply_overruled_by_the_file_guard_does_not_make_the_review_partial PASSED [ 75%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_overruled_reply_still_leaves_the_denominator PASSED [ 76%]
tests/test_review_output.py::TestTheDenominatorCountsRunsThatAnswered::test_an_unparseable_reply_is_still_silence PASSED [ 76%]
tests/test_review_output.py::TestTheReportSurvivesEveryConsoleEncoding::test_rendered_markdown_is_pure_ascii PASSED [ 76%]
tests/test_review_toolchain.py::test_empty_toolchain_placeholder_preserves_original_prompt_bytes PASSED [ 76%]
tests/test_review_toolchain.py::test_run_review_blocks_before_models_when_required_gate_fails[False] PASSED [ 76%]
tests/test_review_toolchain.py::test_run_review_blocks_before_models_when_required_gate_fails[True] PASSED [ 76%]
tests/test_review_toolchain.py::test_run_review_continues_with_no_exclusions_when_directory_is_not_go_module PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_review_uses_selected_gates PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_makefile_stops_before_probes[build] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_makefile_stops_before_probes[test] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_runner_refuses_delegation_added_after_preflight PASSED [ 76%]
tests/test_review_toolchain.py::test_unexecuted_pin_retains_intent_without_observations[configured-skip] PASSED [ 76%]
tests/test_review_toolchain.py::test_unexecuted_pin_retains_intent_without_observations[no-module] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments0-CommandOutcome.COMPLETED-1-go.mod requires go >= 1.27.0] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments1-CommandOutcome.COMPLETED-1-undefined: missingSymbol] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments2-CommandOutcome.COMPLETED-1-WARNING: DATA RACE] PASSED [ 76%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments3-CommandOutcome.TOOL_MISSING-None-required tool is missing] PASSED [ 77%]
tests/test_review_toolchain.py::test_pinned_gate_failure_retains_selection_and_blocks_models[arguments4-CommandOutcome.COMPLETED-2-unknown compiler problem] PASSED [ 77%]
tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[replaced-go] PASSED [ 77%]
tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[replaced-gofmt] PASSED [ 77%]
tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[deleted-go] PASSED [ 77%]
tests/test_review_toolchain.py::test_changed_selected_identity_blocks_models[deleted-gofmt] PASSED [ 77%]
tests/test_review_toolchain.py::test_pinned_evidence_is_consistent_across_outputs[False] PASSED [ 77%]
tests/test_review_toolchain.py::test_pinned_evidence_is_consistent_across_outputs[True] PASSED [ 77%]
tests/test_review_toolchain.py::test_unconfigured_review_preserves_legacy_evidence PASSED [ 77%]
tests/test_review_toolchain.py::test_advisory_commands_receive_environment_only_scope PASSED [ 77%]
tests/test_runner.py::test_child_environment_is_complete_unicode_and_preserves_stdin_and_parent PASSED [ 77%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[False] PASSED [ 77%]
tests/test_runner.py::test_executable_lookup_uses_complete_child_path_and_windows_pathext[True] PASSED [ 77%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[False] PASSED [ 77%]
tests/test_runner.py::test_missing_child_tool_never_falls_back_to_parent_path[True] PASSED [ 77%]
tests/test_runner.py::test_windows_child_path_diagnostic_names_shadowed_copy PASSED [ 77%]
tests/test_runner.py::test_absolute_executable_does_not_depend_on_child_pathext PASSED [ 78%]
tests/test_runner.py::test_environment_is_copied_before_launch PASSED    [ 78%]
tests/test_runner.py::test_concurrent_child_environments_do_not_leak_into_base_calls PASSED [ 78%]
tests/test_runner.py::test_empty_environment_does_not_inherit_parent_settings PASSED [ 78%]
tests/test_runner.py::test_posix_launch_errors_are_failed_command_evidence[error0] PASSED [ 78%]
tests/test_runner.py::test_posix_launch_errors_are_failed_command_evidence[error1] PASSED [ 78%]
tests/test_runner.py::test_runner_error_cannot_succeed_or_change_result_shape PASSED [ 78%]
tests/test_runner.py::test_command_result_succeeded_only_for_completed_zero PASSED [ 78%]
tests/test_runner.py::test_command_result_combined_output_preserves_both_streams PASSED [ 78%]
tests/test_runner.py::test_subprocess_runner_captures_stdout_stderr_and_exit_code_separately PASSED [ 78%]
tests/test_runner.py::test_subprocess_runner_returns_timed_out_without_raising PASSED [ 78%]
tests/test_runner.py::test_subprocess_runner_returns_tool_missing_without_raising PASSED [ 78%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_absent_tool_is_reported_as_missing_from_path PASSED [ 78%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_unlaunchable_path_entry_is_not_blamed_on_path PASSED [ 78%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_a_working_copy_hidden_behind_the_broken_one_is_named PASSED [ 78%]
tests/test_runner.py::TestFileNotFoundErrorIsDiagnosed::test_missing_working_directory_is_not_blamed_on_the_tool PASSED [ 78%]
tests/test_runner.py::TestStdinIsNeverInherited::test_a_child_reading_stdin_sees_end_of_input_immediately PASSED [ 79%]
tests/test_runner.py::TestStdinIsNeverInherited::test_supplied_text_reaches_the_child PASSED [ 79%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[False] PASSED [ 79%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_run_returns_promptly_when_the_child_leaves_a_process_behind[True] PASSED [ 79%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_output_written_before_the_kill_is_still_returned PASSED [ 79%]
tests/test_runner.py::TestTimeoutIsBoundedEvenWhenChildrenSurvive::test_the_reported_duration_matches_the_time_actually_spent PASSED [ 79%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_abandoned_drain_says_so_instead_of_reporting_silence SKIPPED [ 79%]
tests/test_runner.py::TestTheGuaranteesSurviveWhenTheKillDoesNot::test_an_interrupt_takes_the_process_tree_down_with_it SKIPPED [ 79%]
tests/test_scaffold.py::test_scaffold_creates_exactly_three_files PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_shells_out_to_go_mod_init PASSED   [ 79%]
tests/test_scaffold.py::test_scaffold_go_mod_pins_full_patch_version PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_module_path_is_namespaced_under_spike PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_rolls_back_completely_when_go_mod_init_fails PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_rollback_leaves_sibling_spikes_untouched PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_main_go_is_package_main_with_a_main_function PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_main_go_prints_the_question PASSED [ 79%]
tests/test_scaffold.py::test_scaffold_main_go_documents_the_exit_code_convention PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_readme_has_the_report_sections PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_readme_records_the_question PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[Json-Streaming] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[json_streaming] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[json streaming] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[-leading] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[trailing-] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[double--hyphen] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[] PASSED    [ 80%]
tests/test_scaffold.py::test_scaffold_rejects_unusable_slugs[../escape] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[json] PASSED   [ 80%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[json-streaming] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[http2-vs-http3] PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_accepts_valid_slugs[a1] PASSED     [ 80%]
tests/test_scaffold.py::test_scaffold_slug_error_explains_the_rule PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_refuses_to_overwrite_an_existing_spike PASSED [ 80%]
tests/test_scaffold.py::test_scaffold_does_not_modify_an_existing_spike_when_refusing PASSED [ 81%]
tests/test_scaffold.py::test_scaffold_creates_poc_root_when_missing PASSED [ 81%]
tests/test_scaffold.py::test_scaffold_reports_every_file_it_created PASSED [ 81%]
tests/test_ship.py::TestGhPrecondition::test_a_missing_gh_is_an_unmet_precondition_not_a_late_failure PASSED [ 81%]
tests/test_ship.py::TestGhPrecondition::test_gh_is_verified_before_any_git_work_begins PASSED [ 81%]
tests/test_ship.py::TestGhPrecondition::test_the_missing_gh_message_names_the_install PASSED [ 81%]
tests/test_ship.py::TestBranchPreconditions::test_a_detached_head_has_nothing_to_ship_from PASSED [ 81%]
tests/test_ship.py::TestBranchPreconditions::test_shipping_the_base_branch_itself_is_refused PASSED [ 81%]
tests/test_ship.py::TestDirtyTree::test_a_dirty_working_tree_is_refused PASSED [ 81%]
tests/test_ship.py::TestDirtyTree::test_the_dirty_tree_refusal_lists_the_modified_files PASSED [ 81%]
tests/test_ship.py::TestDirtyTree::test_a_clean_tree_is_allowed_to_proceed PASSED [ 81%]
tests/test_ship.py::TestUpstream::test_a_branch_with_no_upstream_and_no_push_is_refused PASSED [ 81%]
tests/test_ship.py::TestUpstream::test_the_missing_upstream_refusal_prints_the_command_that_fixes_it PASSED [ 81%]
tests/test_ship.py::TestUpstream::test_the_push_flag_pushes_the_branch_and_sets_the_upstream PASSED [ 81%]
tests/test_ship.py::TestUpstream::test_the_push_is_a_git_command_never_gh PASSED [ 81%]
tests/test_ship.py::TestPhaseResolution::test_the_phase_directory_is_derived_from_the_branch_name PASSED [ 81%]
tests/test_ship.py::TestPhaseResolution::test_the_phase_flag_overrides_the_branch_derivation PASSED [ 82%]
tests/test_ship.py::TestPhaseResolution::test_a_missing_phase_directory_is_refused_naming_the_path_it_tried PASSED [ 82%]
tests/test_ship.py::TestPhaseResolution::test_the_artifacts_are_the_files_the_phase_directory_holds PASSED [ 82%]
tests/test_ship.py::TestPhaseResolution::test_a_missing_artifact_is_omitted_rather_than_described_as_pending PASSED [ 82%]
tests/test_ship.py::TestFreshCheck::test_the_check_runs_fresh_as_part_of_ship PASSED [ 82%]
tests/test_ship.py::TestFreshCheck::test_a_recorded_check_result_is_not_accepted PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_skips_the_gates PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_the_absent_module_is_recorded_as_an_absence_not_a_failure PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_does_not_trigger_the_check_refusal PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_a_tree_with_no_go_module_needs_no_allow_failing_checks_flag PASSED [ 82%]
tests/test_ship.py::TestNotAGoModule::test_the_evidence_section_states_the_absence_rather_than_omitting_it PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_the_body_carries_one_verdict_row_per_gate PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_the_verdict_table_is_bounded_at_five_rows PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_the_body_does_not_embed_the_gates_full_output PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_when_there_is_no_module_the_table_is_replaced_by_the_recorded_line PASSED [ 82%]
tests/test_ship.py::TestVerdictTable::test_the_recorded_line_replaces_the_table_it_does_not_leave_the_section_empty PASSED [ 82%]
tests/test_ship.py::TestCheckRefusal::test_a_failing_check_refuses_to_open_or_update_the_pr PASSED [ 83%]
tests/test_ship.py::TestCheckRefusal::test_the_check_refusal_names_the_failing_gates PASSED [ 83%]
tests/test_ship.py::TestCheckRefusal::test_allow_failing_checks_overrides_the_refusal PASSED [ 83%]
tests/test_ship.py::TestCheckRefusal::test_a_failing_gate_in_a_real_go_module_is_still_refused_not_excused_as_absent PASSED [ 83%]
tests/test_ship.py::TestOverride::test_an_overridden_run_states_the_failure_in_the_body PASSED [ 83%]
tests/test_ship.py::TestOverride::test_an_overridden_body_never_asserts_green_while_red PASSED [ 83%]
tests/test_ship.py::TestOverride::test_an_overridden_run_still_exits_non_zero PASSED [ 83%]
tests/test_ship.py::TestBody::test_the_body_is_summary_plus_links PASSED [ 83%]
tests/test_ship.py::TestBody::test_the_body_never_embeds_an_artifacts_content PASSED [ 83%]
tests/test_ship.py::TestBody::test_the_body_title_comes_from_the_design_specs_h1 PASSED [ 83%]
tests/test_ship.py::TestBody::test_a_title_flag_overrides_the_design_spec_h1 PASSED [ 83%]
tests/test_ship.py::TestBody::test_the_body_quotes_the_design_specs_purpose_paragraph PASSED [ 83%]
tests/test_ship.py::TestBody::test_what_changed_lists_the_commit_subjects_on_the_branch PASSED [ 83%]
tests/test_ship.py::TestArtifactLinks::test_artifact_links_point_at_the_pushed_commit_sha PASSED [ 83%]
tests/test_ship.py::TestArtifactLinks::test_no_artifact_link_uses_a_branch_name PASSED [ 83%]
tests/test_ship.py::TestArtifactLinks::test_no_artifact_link_points_at_the_base_branch PASSED [ 83%]
tests/test_ship.py::TestArtifactLinks::test_the_push_happens_before_the_body_is_assembled PASSED [ 84%]
tests/test_ship.py::TestBodyFile::test_the_body_file_contains_no_carriage_return PASSED [ 84%]
tests/test_ship.py::TestBodyFile::test_the_reported_size_is_the_character_count_not_the_byte_count PASSED [ 84%]
tests/test_ship.py::TestBodyFile::test_the_body_travels_by_body_file PASSED [ 84%]
tests/test_ship.py::TestBodyFile::test_the_body_flag_never_appears_in_the_argv PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_an_existing_pr_is_queried_before_any_create PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_the_duplicate_error_is_treated_as_a_fallback_not_the_primary_signal PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_the_duplicate_error_still_recovers_when_the_query_missed_it PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_re_running_on_a_branch_with_a_pr_updates_the_body PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_re_running_is_not_treated_as_an_error PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_ghs_error_text_is_passed_through_verbatim PASSED [ 84%]
tests/test_ship.py::TestCreateAndUpdate::test_every_gh_call_receives_empty_stdin PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_ship_reuses_the_phase_one_to_three_exit_codes PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_an_unmet_precondition_exits_by_the_ordinary_failure_route PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_there_is_no_distinct_precondition_exit_code PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_ship_never_issues_a_commit PASSED [ 84%]
tests/test_ship.py::TestExitCodesAndScope::test_no_git_commit_command_is_ever_run PASSED [ 85%]
tests/test_ship.py::TestOutcomeShape::test_a_clean_run_reports_succeeded PASSED [ 85%]
tests/test_ship.py::TestOutcomeShape::test_an_overridden_run_reports_not_succeeded PASSED [ 85%]
tests/test_ship.py::TestOutcomeShape::test_a_created_pr_reports_the_created_action_and_url PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_an_unreadable_branch_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_an_unreadable_status_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_failed_push_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_an_unresolvable_head_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_missing_origin_remote_is_refused PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_failed_log_leaves_the_what_changed_section_empty_not_fatal PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_failed_edit_is_refused_with_ghs_text PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_create_failure_with_no_output_still_refuses PASSED [ 85%]
tests/test_ship.py::TestDegradedGit::test_a_create_success_without_a_url_falls_back_to_raw_stdout PASSED [ 85%]
tests/test_ship.py::TestPhaseResolutionEdges::test_a_direct_relative_path_resolves_the_phase PASSED [ 85%]
tests/test_ship.py::TestPhaseResolutionEdges::test_an_ambiguous_phase_name_is_refused PASSED [ 85%]
tests/test_ship.py::TestPhaseResolutionEdges::test_an_artifact_outside_the_repo_root_keeps_its_full_path PASSED [ 85%]
tests/test_ship.py::TestBareTitleAndSlug::test_the_title_falls_back_to_the_branch_when_no_design_spec PASSED [ 85%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_design_spec_without_an_h1_falls_back_to_the_branch_title PASSED [ 86%]
tests/test_ship.py::TestBareTitleAndSlug::test_an_ssh_remote_url_yields_the_owner_name_slug PASSED [ 86%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_pr_view_with_empty_output_is_treated_as_no_existing_pr PASSED [ 86%]
tests/test_ship.py::TestBareTitleAndSlug::test_a_pr_view_that_prints_a_bare_url_is_accepted PASSED [ 86%]
tests/test_ship.py::TestDirtyTreeParsing::test_a_rename_lists_the_new_path PASSED [ 86%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_a_refused_ship_never_pushes_even_when_push_was_requested PASSED [ 86%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_the_check_runs_before_the_push_on_a_passing_run PASSED [ 86%]
tests/test_ship.py::TestRefusalLeavesTheRemoteAlone::test_an_overridden_failing_check_still_pushes PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_a_branch_ahead_of_its_upstream_is_refused PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_the_refusal_says_how_far_ahead_and_how_to_fix_it PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_a_branch_level_with_its_upstream_ships PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_being_ahead_is_irrelevant_when_push_was_requested PASSED [ 86%]
tests/test_ship.py::TestTheRemoteActuallyHasTheCommit::test_no_pr_is_opened_when_the_commit_is_not_on_the_remote PASSED [ 86%]
tests/test_spike.py::test_runner_error_cannot_confirm_a_spike PASSED     [ 86%]
tests/test_spike.py::test_runs_vet_then_build_then_execute PASSED        [ 86%]
tests/test_spike.py::test_reports_all_three_stages PASSED                [ 86%]
tests/test_spike.py::test_never_uses_go_run PASSED                       [ 87%]
tests/test_spike.py::test_build_failure_skips_execute PASSED             [ 87%]
tests/test_spike.py::test_vet_failure_skips_build_and_execute PASSED     [ 87%]
tests/test_spike.py::test_build_failure_is_reported_as_build_not_execute PASSED [ 87%]
tests/test_spike.py::test_execute_failure_is_reported_as_execute_not_build PASSED [ 87%]
tests/test_spike.py::test_captures_both_streams_from_the_spike PASSED    [ 87%]
tests/test_spike.py::test_keeps_stdout_from_a_spike_that_failed PASSED   [ 87%]
tests/test_spike.py::test_maps_exit_code_to_verdict[0-Verdict.CONFIRMED] PASSED [ 87%]
tests/test_spike.py::test_maps_exit_code_to_verdict[1-Verdict.REFUTED] PASSED [ 87%]
tests/test_spike.py::test_maps_exit_code_to_verdict[2-Verdict.INCONCLUSIVE] PASSED [ 87%]
tests/test_spike.py::test_inconclusive_survives_as_inconclusive PASSED   [ 87%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[3] PASSED [ 87%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[7] PASSED [ 87%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[42] PASSED [ 87%]
tests/test_spike.py::test_unrecognised_exit_code_is_unknown_not_refuted[127] PASSED [ 87%]
tests/test_spike.py::test_no_verdict_when_the_spike_never_ran PASSED     [ 87%]
tests/test_spike.py::test_binary_is_not_left_in_the_spike_directory PASSED [ 88%]
tests/test_spike.py::test_binary_is_removed_even_when_the_spike_fails PASSED [ 88%]
tests/test_spike.py::test_build_output_path_is_outside_the_spike_directory PASSED [ 88%]
tests/test_spike.py::test_default_timeout_is_300_seconds PASSED          [ 88%]
tests/test_spike.py::test_timeout_is_overridable PASSED                  [ 88%]
tests/test_spike.py::test_timed_out_spike_has_no_verdict PASSED          [ 88%]
tests/test_spike.py::test_detects_a_command_spike_from_its_source PASSED [ 88%]
tests/test_spike.py::test_detects_a_library_spike_from_its_source PASSED [ 88%]
tests/test_spike.py::test_library_spike_runs_go_test_instead_of_a_binary PASSED [ 88%]
tests/test_spike.py::test_library_spike_still_builds_first PASSED        [ 88%]
tests/test_spike.py::test_library_spike_passing_tests_is_confirmed PASSED [ 88%]
tests/test_spike.py::test_library_spike_failing_tests_is_refuted PASSED  [ 88%]
tests/test_spike.py::test_library_spike_can_never_be_inconclusive PASSED [ 88%]
tests/test_spike.py::test_library_spike_does_not_build_a_binary PASSED   [ 88%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[0] PASSED [ 88%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[1] PASSED [ 88%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[2] PASSED [ 89%]
tests/test_spike.py::test_execute_stage_that_produced_an_answer_is_not_a_failure[42] PASSED [ 89%]
tests/test_spike.py::test_execute_stage_that_timed_out_did_not_produce_an_answer PASSED [ 89%]
tests/test_spike.py::test_skipped_execute_stage_did_not_produce_an_answer PASSED [ 89%]
tests/test_spike.py::test_vet_and_build_stages_never_claim_to_produce_an_answer[vet] PASSED [ 89%]
tests/test_spike.py::test_vet_and_build_stages_never_claim_to_produce_an_answer[build] PASSED [ 89%]
tests/test_spike.py::test_panicking_spike_is_crashed_not_inconclusive PASSED [ 89%]
tests/test_spike.py::test_deliberate_exit_2_is_still_inconclusive PASSED [ 89%]
tests/test_spike.py::test_crash_detection_needs_both_the_exit_code_and_the_signature PASSED [ 89%]
tests/test_spike.py::test_crash_detection_requires_a_stack_dump_not_just_the_word PASSED [ 89%]
tests/test_spike.py::test_a_crashed_spike_still_reports_its_exit_code PASSED [ 89%]
tests/test_spike.py::test_a_crashed_spike_did_not_answer PASSED          [ 89%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[0] PASSED [ 89%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[1] PASSED [ 89%]
tests/test_spike.py::test_a_spike_that_concluded_anything_has_answered[2] PASSED [ 89%]
tests/test_spike.py::test_a_spike_that_answered_has_no_failed_stage[1] PASSED [ 89%]
tests/test_spike.py::test_a_spike_that_answered_has_no_failed_stage[2] PASSED [ 90%]
tests/test_spike.py::test_a_crashed_spike_does_have_a_failed_stage PASSED [ 90%]
tests/test_spike.py::test_a_build_failure_is_still_a_failed_stage PASSED [ 90%]
tests/test_spike.py::test_library_spike_panicking_is_also_crashed PASSED [ 90%]
tests/test_state.py::test_all_state_lives_under_a_single_directory PASSED [ 90%]
tests/test_state.py::test_config_and_state_are_separate_files PASSED     [ 90%]
tests/test_state.py::test_a_project_without_a_state_file_is_not_initialised PASSED [ 90%]
tests/test_state.py::test_a_project_is_initialised_once_both_files_exist PASSED [ 90%]
tests/test_state.py::test_init_writes_the_module_path PASSED             [ 90%]
tests/test_state.py::test_init_writes_an_empty_approvals_list PASSED     [ 90%]
tests/test_state.py::test_init_writes_no_phase_or_status PASSED          [ 90%]
tests/test_state.py::test_init_records_an_event PASSED                   [ 90%]
tests/test_state.py::test_the_state_file_holds_configuration_and_approvals PASSED [ 90%]
tests/test_state.py::test_the_module_path_stays_in_config_not_state PASSED [ 90%]
tests/test_state.py::test_the_state_file_has_no_phase_field PASSED       [ 90%]
tests/test_state.py::test_the_state_file_has_no_status_field PASSED      [ 90%]
tests/test_state.py::test_an_approval_records_phase_gate_and_date PASSED [ 90%]
tests/test_state.py::test_recording_an_approval_appends_rather_than_replaces PASSED [ 91%]
tests/test_state.py::test_an_absent_state_file_is_not_an_error PASSED    [ 91%]
tests/test_state.py::test_an_absent_state_file_reports_no_approvals PASSED [ 91%]
tests/test_state.py::test_a_corrupt_state_file_is_reported_as_a_problem PASSED [ 91%]
tests/test_state.py::test_a_non_string_module_path_is_ignored_not_trusted PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[json-array-at-top-level] PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[json-string] PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[dict-missing-approvals] PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[approvals-not-a-list] PASSED [ 91%]
tests/test_state.py::test_a_state_file_of_valid_json_but_wrong_shape_is_a_problem[approval-entry-not-a-dict] PASSED [ 91%]
tests/test_state.py::test_project_state_carries_configuration_and_approvals PASSED [ 91%]
tests/test_state.py::test_project_state_carries_no_phase PASSED          [ 91%]
tests/test_state.py::test_the_state_module_exposes_no_phase_enum PASSED  [ 91%]
tests/test_state.py::test_the_state_module_exposes_no_status_enum PASSED [ 91%]
tests/test_state.py::test_the_state_module_exposes_no_transition_machinery PASSED [ 91%]
tests/test_state.py::test_a_version_one_state_file_is_reported_as_outdated PASSED [ 91%]
tests/test_state.py::test_an_outdated_state_file_is_not_called_corrupt PASSED [ 92%]
tests/test_state.py::test_an_outdated_state_file_says_what_to_do_about_it PASSED [ 92%]
tests/test_state.py::test_an_outdated_state_file_yields_no_approvals PASSED [ 92%]
tests/test_state.py::test_a_file_missing_approvals_without_the_v1_shape_is_still_corrupt PASSED [ 92%]
tests/test_state.py::test_an_approval_missing_a_field_is_a_problem PASSED [ 92%]
tests/test_state.py::test_an_empty_approval_object_is_not_a_valid_approval PASSED [ 92%]
tests/test_state.py::test_an_approval_with_a_non_string_field_is_a_problem PASSED [ 92%]
tests/test_state.py::test_a_malformed_approval_names_its_position PASSED [ 92%]
tests/test_state.py::test_well_formed_approvals_still_load PASSED        [ 92%]
tests/test_status.py::test_the_text_rendering_names_the_project_root PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_names_the_current_phase PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_says_the_phase_came_from_the_branch PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_says_the_phase_came_from_the_fallback PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_lists_every_required_artifact PASSED [ 92%]
tests/test_status.py::test_the_text_rendering_shows_a_recorded_approval PASSED [ 92%]
tests/test_status.py::test_every_other_phase_gets_one_summary_line PASSED [ 92%]
tests/test_status.py::test_the_summary_line_reports_present_over_required PASSED [ 93%]
tests/test_status.py::test_a_skipped_poc_phase_summarises_out_of_six PASSED [ 93%]
tests/test_status.py::test_the_current_phase_is_not_repeated_in_the_summary PASSED [ 93%]
tests/test_status.py::test_the_summary_is_ordered_lexically PASSED       [ 93%]
tests/test_status.py::test_the_json_contract_has_the_documented_keys PASSED [ 93%]
tests/test_status.py::test_the_json_phases_array_covers_every_phase PASSED [ 93%]
tests/test_status.py::test_the_json_phases_array_includes_the_current_phase PASSED [ 93%]
tests/test_status.py::test_the_json_artifact_map_is_name_to_boolean PASSED [ 93%]
tests/test_status.py::test_the_json_is_parseable_when_problems_exist PASSED [ 93%]
tests/test_status.py::test_two_problems_are_both_reported PASSED         [ 93%]
tests/test_status.py::test_a_problem_does_not_suppress_the_rest_of_the_report PASSED [ 93%]
tests/test_status.py::test_a_phase_missing_artifacts_still_answers PASSED [ 93%]
tests/test_status.py::test_a_project_with_no_phases_still_answers PASSED [ 93%]
tests/test_status.py::test_a_corrupt_state_file_still_answers PASSED     [ 93%]
tests/test_status.py::test_an_unreadable_project_root_is_reported_not_raised PASSED [ 93%]
tests/test_status.py::test_the_status_report_exposes_no_could_answer PASSED [ 93%]
tests/test_status.py::test_the_temp_file_sweep_still_runs PASSED         [ 94%]
tests/test_status.py::test_the_sweep_is_still_reported_never_silent PASSED [ 94%]
tests/test_status.py::test_no_rendering_describes_any_artifact_as_complete PASSED [ 94%]
tests/test_status.py::test_the_default_runner_and_project_resolution_are_used PASSED [ 94%]
tests/test_status.py::test_the_default_path_without_a_specs_directory_reports_no_phases PASSED [ 94%]
tests/test_status.py::test_a_specs_directory_without_a_project_reports_no_phases PASSED [ 94%]
tests/test_status.py::test_more_than_one_project_directory_is_reported_and_the_first_used PASSED [ 94%]
tests/test_status.py::test_a_project_directory_beside_loose_phase_directories_is_reported PASSED [ 94%]
tests/test_status.py::test_the_mixed_layout_still_reports_the_project_directory_phases PASSED [ 94%]
tests/test_status.py::test_a_flat_layout_is_accepted_without_comment PASSED [ 94%]
tests/test_status.py::test_real_repository_reports_multiple_projects_and_atom_cli_history_remains_readable PASSED [ 94%]
tests/test_status.py::test_a_corrupt_config_is_reported_separately PASSED [ 94%]
tests/test_status.py::test_the_last_event_and_damaged_lines_are_reported PASSED [ 94%]
tests/test_status.py::test_the_text_rendering_shows_the_module_path PASSED [ 94%]
tests/test_status.py::test_the_text_rendering_marks_a_not_started_phase PASSED [ 94%]
tests/test_status.py::test_the_text_rendering_states_when_there_is_no_current_phase PASSED [ 94%]
tests/test_status.py::test_the_text_rendering_shows_the_last_event PASSED [ 95%]
tests/test_status.py::test_the_text_rendering_points_at_the_problems PASSED [ 95%]
tests/test_status.py::test_the_problem_renderer_is_empty_when_there_are_no_problems PASSED [ 95%]
tests/test_status.py::test_the_problem_renderer_uses_amber_advisories PASSED [ 95%]
tests/test_status.py::test_the_problem_renderer_never_uses_red PASSED    [ 95%]
tests/test_storage.py::test_reading_a_missing_file_says_it_is_missing PASSED [ 95%]
tests/test_storage.py::test_reading_unparseable_json_reports_corruption PASSED [ 95%]
tests/test_storage.py::test_reading_valid_json_of_the_wrong_type_is_still_corruption PASSED [ 95%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected["just a string"-str] PASSED [ 95%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[42-int] PASSED [ 95%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[null-NoneType] PASSED [ 95%]
tests/test_storage.py::test_other_valid_json_scalars_are_also_rejected[true-bool] PASSED [ 95%]
tests/test_storage.py::test_an_empty_file_is_corruption_not_emptiness PASSED [ 95%]
tests/test_storage.py::test_a_file_of_nul_bytes_is_corruption PASSED     [ 95%]
tests/test_storage.py::test_a_missing_required_key_is_corruption_and_names_the_key PASSED [ 95%]
tests/test_storage.py::test_reading_a_well_formed_file_returns_the_object PASSED [ 95%]
tests/test_storage.py::test_reading_does_not_keep_the_file_open PASSED   [ 95%]
tests/test_storage.py::test_writing_then_reading_round_trips PASSED      [ 96%]
tests/test_storage.py::test_writing_creates_the_parent_directory PASSED  [ 96%]
tests/test_storage.py::test_writing_leaves_no_temp_file_behind_on_success PASSED [ 96%]
tests/test_storage.py::test_writing_replaces_rather_than_truncating PASSED [ 96%]
tests/test_storage.py::test_writing_retries_while_the_destination_is_held_open PASSED [ 96%]
tests/test_storage.py::test_a_write_that_cannot_succeed_fails_loudly PASSED [ 96%]
tests/test_storage.py::test_sweeping_removes_leftover_temp_files PASSED  [ 96%]
tests/test_storage.py::test_sweeping_reports_what_it_removed PASSED      [ 96%]
tests/test_storage.py::test_sweeping_leaves_unsaved_recovery_files_alone PASSED [ 96%]
tests/test_storage.py::test_sweeping_leaves_real_state_files_alone PASSED [ 96%]
tests/test_storage.py::test_sweeping_an_absent_directory_is_not_an_error PASSED [ 96%]
tests/test_style.py::test_style_rules_reach_the_model_by_default PASSED  [ 96%]
tests/test_style.py::test_style_rules_can_be_switched_off_for_measurement PASSED [ 96%]
tests/test_style.py::test_style_rules_sit_before_the_output_format_instruction PASSED [ 96%]
tests/test_style.py::test_every_rule_is_numbered_and_present PASSED      [ 96%]
tests/test_style.py::test_no_rule_is_phrased_as_a_preference PASSED      [ 96%]
tests/test_toolchain.py::test_prompt_block_excludes_everything_the_passing_toolchain_proved PASSED [ 97%]
tests/test_toolchain.py::test_prompt_block_does_not_exclude_ignored_errors_when_errcheck_was_skipped PASSED [ 97%]
tests/test_toolchain.py::test_prompt_block_says_nothing_is_excluded_when_toolchain_did_not_run PASSED [ 97%]
tests/test_windows_process.py::test_windows_native_job_is_private PASSED [ 97%]
tests/test_windows_process.py::test_windows_launch_is_suspended_until_owned PASSED [ 97%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[0] PASSED [ 97%]
tests/test_windows_process.py::test_windows_success_stops_pipe_independent_child[7] PASSED [ 97%]
tests/test_windows_process.py::test_windows_fixture_waits_for_readable_identity_record PASSED [ 97%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[PermissionError] PASSED [ 97%]
tests/test_windows_process.py::test_windows_fixture_readiness_deadline_preserves_read_failure[FileNotFoundError] PASSED [ 97%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[False] PASSED [ 97%]
tests/test_windows_process.py::test_windows_parent_exits_before_timeout[True] PASSED [ 97%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[False] PASSED [ 97%]
tests/test_windows_process.py::test_windows_new_member_during_exit_capture_cannot_be_verified[True] PASSED [ 97%]
tests/test_windows_process.py::test_windows_large_stdin_and_unicode_argv PASSED [ 97%]
tests/test_windows_process.py::test_windows_communication_sleeps_only_while_idle PASSED [ 97%]
tests/test_windows_process.py::test_windows_busy_communication_still_checks_deadline PASSED [ 98%]
tests/test_windows_process.py::test_windows_large_streams_do_not_spend_the_deadline_sleeping PASSED [ 98%]
tests/test_windows_process.py::test_windows_cmd_shim_preserves_arguments PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[create_job] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[pipe] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[launch] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[assign] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[contains] PASSED [ 98%]
tests/test_windows_process.py::test_windows_setup_failure_never_executes_command[resume] PASSED [ 98%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[terminate_job] PASSED [ 98%]
tests/test_windows_process.py::test_windows_timeout_keeps_primary_reason_on_cleanup_failure[active_processes] PASSED [ 98%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[1] PASSED [ 98%]
tests/test_windows_process.py::test_windows_admission_query_failure_cannot_verify_cleanup[2] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[0] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[1] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_finalizes_owned_processes[2] PASSED [ 98%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[completion_receipt] PASSED [ 99%]
tests/test_windows_process.py::test_windows_interrupt_outside_communication_still_finalizes[missing_file_diagnosis] PASSED [ 99%]
tests/test_windows_process.py::test_windows_communication_observes_deferred_interrupt PASSED [ 99%]
tests/test_windows_process.py::test_windows_sigint_during_communication_is_prompt_and_reclaims_children PASSED [ 99%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[0] PASSED [ 99%]
tests/test_windows_process.py::test_windows_lifecycle_failure_preserves_primary_exit[7] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_capture_names_incomplete_streams PASSED [ 99%]
tests/test_windows_process.py::test_windows_concurrent_runs_are_isolated PASSED [ 99%]
tests/test_windows_process.py::test_windows_repeated_runs_release_handles_and_workers PASSED [ 99%]
tests/test_windows_process.py::test_windows_interrupt_during_native_launch_reclaims_suspended_parent PASSED [ 99%]
tests/test_windows_process.py::test_windows_sigint_during_handle_acquisition_does_not_lose_job PASSED [ 99%]
tests/test_windows_process.py::test_windows_broken_executable_is_diagnosed_as_unlaunchable PASSED [ 99%]
tests/test_windows_process.py::test_windows_runner_assigns_and_checks_membership_before_resume PASSED [ 99%]
tests/test_windows_process.py::test_windows_child_can_close_stdin_early PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[None] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary1] PASSED [ 99%]
tests/test_windows_process.py::test_windows_partial_pipe_rollback_preserves_primary_and_closes_other_handles[primary2] PASSED [100%]

=============================== tests coverage ================================
______________ coverage: platform win32, python 3.13.14-final-0 _______________

Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
atom\__init__.py                1      0   100%
atom\_checkout_cleanup.py      30     21    30%   13-30, 34-41, 45
atom\_review_format.py        149      7    95%   125, 178, 201, 210, 234, 244, 257
atom\_windows_process.py      381     28    93%   188-190, 243, 309, 317, 346-350, 357-359, 362-363, 377, 386-387, 405, 414, 455-456, 485, 487, 560-561, 610, 618
atom\artifact_cli.py           35      1    97%   58
atom\artifacts.py             174     19    89%   103, 153, 219, 241, 256, 265, 276-284, 309-316, 346-348
atom\body.py                   71      0   100%
atom\buildsystem.py            76      5    93%   57-60, 72, 116, 180
atom\check.py                  43      2    95%   117-118
atom\cli.py                   366     21    94%   107-108, 372-373, 383-393, 415-425, 684, 875
atom\context.py                61      2    97%   86-87
atom\diff.py                  124      0   100%
atom\eventlog.py               50      0   100%
atom\extract.py               164      0   100%
atom\filelock.py               64     10    84%   69-80, 169
atom\gates.py                 173      6    97%   91, 407-408, 412, 462, 472
atom\go_selection.py          220      3    99%   97, 181, 280
atom\index.py                  40      5    88%   66-67, 81, 86, 98
atom\invoke.py                137      4    97%   445, 449-451
atom\merge.py                  92      0   100%
atom\module_rules.py           52      2    96%   53-54
atom\onboarding.py            137      4    97%   100, 138, 263-264
atom\pathsetup.py              66      0   100%
atom\phases.py                 92      0   100%
atom\pull_request.py          209      6    97%   81, 306-307, 311-312, 341
atom\report.py                396     10    97%   193, 208, 220, 234, 250, 252, 259, 931, 933, 935
atom\review.py                131      0   100%
atom\runner.py                213     54    75%   144-145, 161-207, 262, 268, 306-312, 345-357, 369-373, 384-395, 416, 457, 467, 469, 541
atom\scaffold.py               46      1    98%   127
atom\ship.py                  252      3    99%   387, 390-391
atom\spike.py                 128      4    97%   169, 265, 268-269
atom\state.py                 103      1    99%   235
atom\status.py                 77      0   100%
atom\storage.py                79      0   100%
atom\style.py                   4      0   100%
atom\toolchain.py              72      4    94%   124, 180, 188, 190
---------------------------------------------------------
TOTAL                        4508    223    95%
================= 1615 passed, 5 skipped in 176.32s (0:02:56) =================
EXIT CODE: 0

```
