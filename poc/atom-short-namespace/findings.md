# Findings

- With `--plugin-dir`, `/atom:poc` reached the `poc` skill and
  `/atom:start` reached the `start` command.
- After marketplace installation, `/atom:poc` reached the command named
  `atom` instead of the `poc` skill.
- After marketplace installation, `/start` reached Copilot CLI's built-in
  session-start behavior instead of the fixture's `start` command.
- Direct-load results gathered while the real `atom-go@atom` registration was
  copied into the isolated home were invalid. The final probes clear only the
  temporary config's `installedPlugins` list before execution.
