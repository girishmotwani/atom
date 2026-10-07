# Findings

## 1. Copilot matches the `atom` executable, not nested Atom subcommands — High

Both `shell(atom artifact write)` and a saved command identifier of
`atom artifact write` failed to authorize the command. `shell(atom:*)` and a saved
identifier of `atom` succeeded, but also authorized adjacent Atom commands.

The previously proposed workflow cannot safely approve `atom artifact write`.

## 2. A dedicated executable has the required permission boundary — High

`atom-write-artifact` is independently identifiable by Copilot's shell permission
matcher. A saved `atom-write-artifact` grant ran that command while `atom artifact
check` remained unapproved.

## 3. The real guard remains effective behind the dedicated command — High

The approved dedicated command wrote `specs/allowed.md` and refused
`internal/main.go`; the forbidden file did not exist afterward.

## 4. Non-interactive denial exits zero — Medium

Copilot printed `Permission denied because no interactive user response was available`
but its process exited 0. Automation must grade this experiment from the output and
filesystem result, not the Copilot process exit code alone.
