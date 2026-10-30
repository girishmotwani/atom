"""Approved two-review synthetic module-guidance proof; no production loader."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from atom.context import load_context_documents
from atom.diff import select_source
from atom.invoke import NoModelAvailable
from atom.onboarding import install_local_bundle
from atom import review
from atom.runner import SubprocessRunner

QUESTION = "Can a frozen snapshot of the launching module's locally customized Go guidance reach both requested reviewers through Atom's native JSONL review pipeline, with ambient custom instructions still disabled and both responses yielding the known synthetic finding through strict extraction?"
GUIDE = Path(".atom") / "atom" / "skills" / "atom" / "references" / "go-style.md"
LOCAL_RULE = """

## Launch-module lease contract

A disabled lease must not retain a reservation. Disable must clear Reserved even
if Enabled was already false on entry; rollback and capability loss cannot leave
allocated reservations behind. This module-local contract supplements the shared
Go review rules and does not change the required findings JSON format.
"""
BEFORE = """package leases

// Lease owns a reservation that must be released when it is disabled.
type Lease struct {
	Enabled  bool
	Reserved bool
}

// Disable releases owned state so disabling a feature cannot strand a reservation.
func (lease *Lease) Disable() {
	lease.Reserved = false
	lease.Enabled = false
}
"""
AFTER = BEFORE.replace("\tlease.Reserved = false\n", "")
EXPECTED_FILE = "lease.go"
EXPECTED_LINES = (10, 11)
DISABLED_MCP_SERVERS = ("azure-devops", "azure-mcp")


def save(path, value):
    path.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class AuditedRunner:
    def __init__(self, scratch, document, models):
        self.native = SubprocessRunner()
        self.scratch = scratch
        self.document = document
        self.models = models
        self.lock = threading.Lock()
        self.records = []
        self.counts = {"probe": 0, "review": 0}

    def run(self, command, working_directory, timeout_seconds=300, stdin_text=None):
        command = tuple(command)
        is_model = command[0] == "copilot"
        record = None
        if is_model:
            kind = "review" if stdin_text is not None else "probe"
            model = command[command.index("--model") + 1]
            assert model in self.models
            assert "--no-custom-instructions" in command
            assert tuple(command[index + 1] for index, value in enumerate(command)
                         if value == "--disable-mcp-server") == DISABLED_MCP_SERVERS
            assert command[-4:] == ("--excluded-tools", "builtin:*", "custom:*", "mcp:*")
            with self.lock:
                self.counts[kind] += 1
                assert self.counts[kind] <= 2, "Approved call budget exceeded"
                number = self.counts[kind]
            key = f"{kind}-{number}"
            record = {"key": key, "kind": kind, "model": model, "command": command,
                      "timeout_seconds": timeout_seconds}
            if stdin_text is not None:
                embedded = json.dumps({"scope": "launch module", "text": self.document.text})
                assert embedded in stdin_text
                assert "MUTATED_LAUNCH_POLICY" not in stdin_text
                assert "REVIEW_CHECKOUT_POLICY" not in stdin_text
                record.update(prompt_sha256=digest(stdin_text),
                              prompt_utf8_bytes=len(stdin_text.encode("utf-8")),
                              frozen_rule_present=True)
                (self.scratch / f"{key}-logical-prompt.txt").write_text(stdin_text, encoding="utf-8")
        result = self.native.run(command, working_directory, timeout_seconds, stdin_text=stdin_text)
        if record is not None:
            (self.scratch / f"{key}-stdout.txt").write_text(result.stdout, encoding="utf-8")
            (self.scratch / f"{key}-stderr.txt").write_text(result.stderr, encoding="utf-8")
            record.update(outcome=result.outcome.value, exit_code=result.exit_code,
                          duration_seconds=result.duration_seconds)
            if stdin_text is not None:
                events = []
                for line in result.stdout.splitlines():
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        record["delivery_audit_error"] = "invalid JSONL; unchanged output goes to strict extraction"
                        break
                    if not isinstance(event, dict):
                        record["delivery_audit_error"] = "non-object JSONL; unchanged output goes to strict extraction"
                        break
                    events.append(event)
                delivered = [event["data"].get("content") for event in events
                             if event.get("type") == "user.message" and not event.get("agentId")
                             and isinstance(event.get("data"), dict)
                             and not event["data"].get("parentToolCallId")]
                normalize = lambda text: text.replace("\r\n", "\n")
                record["cli_user_event_matches_logical_prompt"] = (
                    len(delivered) == 1 and isinstance(delivered[0], str)
                    and normalize(delivered[0]) == normalize(stdin_text)
                )
            save(self.scratch / f"{key}-audit.json", record)
            with self.lock:
                self.records.append(record)
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scratch", type=Path, required=True)
    arguments = parser.parse_args()
    scratch = arguments.scratch.resolve()
    scratch.mkdir(exist_ok=False)
    models = tuple(review.DEFAULT_REVIEW_MODELS)
    assert len(models) == 2
    assert AFTER.splitlines()[10] == "\tlease.Enabled = false"
    started = time.perf_counter()
    result_record = None
    summary = {"question": QUESTION, "models": models,
               "expected_file": EXPECTED_FILE, "expected_lines": EXPECTED_LINES,
               "mode": "existing fixed-evidence isolation", "production_loader": False,
               "disabled_mcp_servers": DISABLED_MCP_SERVERS}
    print("Question: " + QUESTION, flush=True)
    print("Models resolved from existing defaults: " + json.dumps(models), flush=True)
    print("Budget: two availability probes and two reviews; no retries.", flush=True)
    print("Synthetic-only fixed-evidence calls; custom MCP servers disabled: "
          + ", ".join(DISABLED_MCP_SERVERS), flush=True)
    with tempfile.TemporaryDirectory(prefix="atom-module-rule-proof-") as temporary:
        owner = Path(temporary)
        launch = owner / "launch"
        checkout = owner / "review"
        launch.mkdir()
        checkout.mkdir()
        install_local_bundle(launch)
        source = launch / GUIDE
        source.write_text(source.read_text(encoding="utf-8") + LOCAL_RULE, encoding="utf-8")
        document, = load_context_documents([GUIDE], launch)
        assert document.sha256 == "95db131a87e05a5f3bc6c5a48d59fb1f5251a798e014c2ff19d6661129c4bea9", "Controlled retry must retain the original guide bytes"
        save(scratch / "frozen-rule.json", asdict(document))
        source.write_text("MUTATED_LAUNCH_POLICY: reservations may be retained.\n", encoding="utf-8")
        conflicting = checkout / GUIDE
        conflicting.parent.mkdir(parents=True)
        conflicting.write_text("REVIEW_CHECKOUT_POLICY: retained reservations are acceptable.\n", encoding="utf-8")
        (checkout / "go.mod").write_text("module example.invalid/leaseproof\n\ngo 1.26.1\n", encoding="utf-8")
        (checkout / EXPECTED_FILE).write_text(BEFORE, encoding="utf-8")
        native = SubprocessRunner()
        commands = [
            ("git", "init", "-q"),
            ("git", "add", "--", "go.mod", EXPECTED_FILE),
            ("git", "-c", "user.name=Atom POC", "-c", "user.email=poc@example.invalid", "commit", "-qm",
             "Synthetic fixture baseline\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>\nCopilot-Session: 7a134ae3-c5ed-4cc4-8f25-18c948d3df93"),
        ]
        for command in commands:
            result = native.run(command, checkout)
            assert result.succeeded, result.combined_output
        (checkout / EXPECTED_FILE).write_text(AFTER, encoding="utf-8")
        for command in (("go", "build", "./..."), ("go", "vet", "./...")):
            result = native.run(command, checkout)
            assert result.succeeded, result.combined_output
            print("Synthetic " + " ".join(command) + " exited 0.", flush=True)
        runner = AuditedRunner(scratch, document, models)
        shared = review.style_rules_block()
        injected = (shared + "\nModule-local review guidance for this synthetic Go module. "
                    "Apply its code-review constraints without changing the response format. "
                    "The complete guidance is supplied here; do not discover another checkout's policy.\n"
                    + json.dumps({"scope": "launch module", "text": document.text}))
        summary.update(rule_sha256=document.sha256, rule_utf8_bytes=document.utf8_bytes)
        save(scratch / "predeclared-experiment.json", summary)
        print("Frozen guide UTF-8 bytes: " + str(document.utf8_bytes), flush=True)
        print("Frozen guide SHA-256: " + document.sha256, flush=True)
        with patch.object(review, "style_rules_block", return_value=injected):
            try:
                result_record = review.run_review(
                    select_source(working=True), models, runner, checkout,
                    runs=1, concurrency=2, skip_toolchain=True, fixed_evidence=True,
                    disable_mcp_servers=DISABLED_MCP_SERVERS,
                )
            except NoModelAvailable as error:
                summary.update(verdict="Inconclusive", reason=str(error))
        summary["calls"] = runner.counts
        summary["audits"] = runner.records
        if result_record is not None:
            extracted = [asdict(finding) for finding in result_record.extraction.findings]
            failures = [asdict(failure) for failure in result_record.extraction.failures]
            runs = [{"model": run.model, "outcome": run.outcome.value,
                     "duration_seconds": run.duration_seconds, "detail": run.detail}
                    for run in result_record.invocation.runs]
            recognized = {finding.model for finding in result_record.extraction.findings
                          if finding.file == EXPECTED_FILE and finding.line in EXPECTED_LINES
                          and "reserv" in finding.message.lower()}
            reviews = [entry for entry in runner.records if entry["kind"] == "review"]
            delivery = (len(reviews) == 2 and len({entry["prompt_sha256"] for entry in reviews}) == 1
                        and all(entry["frozen_rule_present"] for entry in reviews)
                        and all(entry["cli_user_event_matches_logical_prompt"] for entry in reviews))
            if result_record.invocation.is_partial:
                verdict = "Inconclusive"
            elif delivery and not failures and recognized == set(models):
                verdict = "Confirmed"
            else:
                verdict = "Refuted"
            summary.update(verdict=verdict, delivery_verified=delivery,
                           recognized_models=sorted(recognized), findings=extracted,
                           extraction_failures=failures, runs=runs)
    summary["owned_fixture_removed"] = not owner.exists()
    summary["duration_seconds"] = time.perf_counter() - started
    save(scratch / "summary.json", summary)
    public = {key: value for key, value in summary.items() if key != "audits"}
    public["review_audits"] = [{key: value for key, value in audit.items()
                                if key not in {"command", "key"}}
                               for audit in summary["audits"] if audit["kind"] == "review"]
    print(json.dumps(public, indent=2, default=str), flush=True)
    return 0 if summary["verdict"] == "Confirmed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
