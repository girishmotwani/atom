# Archived POC brief: synthetic Windows ownership

Publication-safe extract of the question/budget approved before the 2026-10-20 spike, not a newly proposed or rerun experiment.

## Question

Can a stdlib-only Python Windows Job Object fixture assign a suspended parent before it runs and, when a two-second deadline expires after that parent has exited, return within five seconds with its recorded child stopped, both output markers recovered and its empty working directory removable before safety rescue, while an owned outside-job control stays alive?

## Planned evidence and bounds

Disposable Python/native exception for the Python tooling defect. At most three identical serial trials, stopping at the first Refuted or Inconclusive result; 20-second worker watchdog, 120-second total including owned safety rescue. Finite synthetic processes only, with retained identities and separate safety intervention. Child exit, EOF/markers, directory release and control survival must be observed before rescue; later expiry/rescue does not count as candidate success.

Original command (private absolute scratch argument omitted):

```text
python poc\windows-job-cleanup\spike.py --scratch <new-private-scratch-directory>
```

The [report](poc-report.md) records the actual three-trial Confirmed result, frozen source hashes, earlier counterexample and limits. No model call, external source checkout, production repair or supported-CI claim was part of that experiment. The original private approval ledger remains local; unrelated investigation material is not copied here.
