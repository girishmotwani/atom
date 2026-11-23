---
project: "atom-v1-improvements"
phase: "phase-09-onboarding-example"
date: "2026-11-19"
status: "prepared-not-launched"
---

# Uninterrupted Quickstart Replay Preparation

## Approved Question

Can the developer follow the frozen published Ubuntu/Bash quickstart in one uninterrupted Copilot session from fresh Atom locations through genuine brief/report approvals and all three specified Go results, using only documented instructions and no outside coaching?

The developer approved [the brief](uninterrupted-quickstart-brief.md) with
"approved, lets proceed" after opening it in VS Code. This is one experienced-user,
developer-operated attempt, not a fresh-authentication or newcomer study. No
installation or interactive/model session has started at this preparation checkpoint.

## Frozen Inputs

| Input | Captured identity |
| --- | --- |
| Public source base | d976666b1b6b5d89bbe64f21315d036d0ca76101 |
| Published guide | 6136 UTF-8/LF bytes; fb1819f51636d9044ebf29e668af7bf8099b1702f97fe471b5e1d8ab1759f887 |
| Published setup block | 9bb099b7937997d2fff232b815f519d1f2a783264b00aa384efe75a2b8370304 |
| Setup with declared unused-directory substitution | 19afdebc0af96582726e298c81d644a1e0f794ec5a254e6012a20a4f9bd513c5 |
| Exact initial request extracted from the guide | b326f46653bafc7ec0141ea29425a5b0750a5051c9d3e5c416d3b54dfedf1094 |
| Brief at the actual approval, before status/log amendment | d7f43260922a1591d8fe471d56707c15b2d8267d01fee29da93fe49e2f991d55 |
| Selected existing client | 985f0e1b1b3e734bc996324651307a076ae3deae21e3fa9f9af917983ce309c4 |

Hashes are SHA-256. The private page, setup, initial request, full preflight
stdout/stderr and preparation.json are retained outside Git under this session's
files/phase09-uninterrupted-inputs. The setup has exactly the declared substitution
trial="$HOME/atom-quickstart-uninterrupted-20261119"; reversing it reproduces the
published block. No other setup text changed. The Atom tooling pin remains
5bb33cbe2c835382b5ccda840c5268321b24ac0b. The live marketplace identity is not yet
known and will not be assumed equal to the public source base.

## Actual Read-Only Ubuntu Preflight

The session-local Python preparation program ran version/help probes through
wsl.exe --distribution Ubuntu --exec python3 -. Each captured command exited 0
with empty stderr. Verbatim prerequisite stdout, in Go/Git/Python command order:

~~~text
go version go1.22.2 linux/amd64
git version 2.43.0
Python 3.12.3
~~~

Ordinary PATH client's --no-auto-update --version stdout:

~~~text
GitHub Copilot CLI 0.0.403.
Run 'copilot update' to check for updates.
~~~

Selected existing client's --no-auto-update --version stdout:

~~~text
GitHub Copilot CLI 1.0.107.
Run 'copilot update' to check for updates.
~~~

The selected executable resolves to /home/girish/.local/atom-phase09-tools/bin/copilot. Its own
--no-auto-update help environment confirms these controls verbatim:

~~~text
`COPILOT_HOME`: override the directory where configuration and state files are stored; defaults to `$HOME/.copilot`.

`COPILOT_AUTO_UPDATE`: set to "false" to disable downloading updated CLI versions automatically. Can also be disabled with the --no-auto-update flag. Auto-update is enabled by default, except in CI environments (detected via `CI`, `BUILD_NUMBER`, `RUN_ID`, or `SYSTEM_COLLECTIONURI` environment variables), where it is disabled by default. Standalone development builds run their bundled package by default and do not offer or install CLI updates unless release-style package behavior is selected with a canonical semantic version in `COPILOT_CLI_VERSION`. `COPILOT_CLI_DIST_DIR` selects an explicit package but does not enable updates for a development-identity package. On other standalone-binary installations, disabling it this way or with --no-auto-update also makes launches ignore any newer version already in the package cache and run the version built into the installed binary.
~~~

Python venv/ensurepip are available. /usr/bin/script supports the required flush,
return-status and timing-log controls. Both new trial/evidence destinations and
the proposed workspace/profile/tmp/venv paths are absent, including symlinks.
The earlier trial remains present. Only a child-process PATH selects the existing
supported client; no client update, global PATH/HOME/configuration change,
authentication action, credential copy or model override was performed.
Authentication usability and the model actually selected by the isolated client
remain unobserved until startup; do not infer them from version/help success.

## Recording And Participant Handoff

Use a new private session-local Python launcher and the existing system PTY
recorder. Run the frozen setup in Bash, without automatic approvals, restart
mode, extra model calls, Go scaffolding or edits to the installed instructions.
Keep the terminal visible after exit so an unexpected diagnostic is not lost.
Capture process identities, terminal output/timing and normal/abnormal exit
independently; a zero recorder exit is not a successful replay verdict.

Before sending the initial task, leave the freshly opened client at its startup
prompt while the observer takes a read-only installed-file and tooling-provenance
snapshot. This is a preparation boundary, not mid-task navigation help. The
snapshot must predate the first task request; verify that ordering in the saved
event stream. If the boundary cannot be evidenced, report Inconclusive instead
of reconstructing a before-manifest. Repeat the inventory after session exit.
Compare installed public content with the resolved public source before claiming
a plugin revision; no prior plugin count or commit is presumed current.

Once preparation is complete, the developer follows only the frozen page and
makes the actual brief/report decisions. Record active/pause intervals against
the approved 30-active-minute cap; absent measurements remain explicitly
unmeasured. Stop on failure, interruption, help request or unexpected scope/auth
request; preserve the first attempt and gate any recovery. No publication or
automatic Phase 09 completion is authorized.

## Verification Limits

This checkpoint verifies inputs and read-only prerequisites, not installation,
authentication, navigation, Go execution or an uninterrupted session. The root
Go-check applicability limit and reused Python CI baseline remain as recorded
in the approved brief. No new runtime-suite or replay success is claimed.
