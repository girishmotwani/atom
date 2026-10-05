# Decisions

- Renamed the `/atom` router to `/atom:start`; retaining command `atom` would
  make every compact skill unreachable after marketplace installation.
- Renamed only the nine pipeline skills. `/atom-status` and `/atom-check`
  remain command files because the experiment did not establish a compatible
  migration path for those existing command names.
- Preserved older POC reports and completed design artifacts as historical
  evidence instead of rewriting them to describe a repository state that did
  not exist when they were produced.
