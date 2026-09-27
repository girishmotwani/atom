"""Sentinel script bundled inside the probe plugin.

Its only job is to leave proof on disk that it actually executed. The spike
must not depend on the agent reporting its own behaviour -- an agent can
describe running a script perfectly convincingly while running nothing at all
(see finding F10). A file either exists afterwards or it does not.
"""

import os
import sys
import tempfile


def main() -> int:
    # Record where this file physically lives. That answers the real question:
    # whether the agent resolved a path relative to the loaded skill, or
    # guessed something that happened to run.
    here = os.path.abspath(__file__)

    token = sys.argv[1] if len(sys.argv) > 1 else "NO_TOKEN"
    target = os.path.join(tempfile.gettempdir(), "atom-bundle-probe-%s.txt" % token)

    with open(target, "w", encoding="utf-8") as handle:
        handle.write("script_path=%s\n" % here)
        handle.write("argv=%s\n" % " ".join(sys.argv[1:]))
        handle.write("cwd=%s\n" % os.getcwd())

    # Printed so a human reading the transcript can see it, but the transcript
    # is never the evidence -- the file is.
    print("ATOM_BUNDLE_PROBE_RAN path=%s token=%s" % (here, token))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
