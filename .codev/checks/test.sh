#!/usr/bin/env bash
# Per-builder test DISPATCHER for porch's implement/review test-check.
# Ported from multibench (.codev/checks/test.sh @ 14f6c9d4).
#
# porch.checks is GLOBAL (no per-project override), so a single hardcoded command would either
# run the wrong app's tests or break builders that lack another app's toolchain. Instead, this
# script runs the test suite of each top-level app/pipeline THIS builder actually touched
# (its diff vs origin/main), looked up in the registry below.
#
# Result: a builder that only touched apps/viewer runs ONLY vitest; a Python builder that only
# touched pipelines/ runs ONLY its pytest. Adding an app = one registry line. porch runs this
# from the worktree root.
set -uo pipefail

# Registry: touched top-level dir -> test command (run from the repo root). "" = unregistered.
test_cmd_for() {
  case "$1" in
    pipelines)   echo "uv --project pipelines run pytest pipelines" ;;
    apps/viewer) echo "pnpm -C apps/viewer test" ;;
    *)           echo "" ;;
  esac
}

base="origin/main"
git rev-parse --verify --quiet "$base" >/dev/null || base="main"

changed=$(git diff --name-only "${base}...HEAD" 2>/dev/null)
# runs/** (committed evidence), texts/** (corpus), and configs/** (the example panel that
# test_phase2_tools.py loads and asserts on) map to the pipelines lane, whose pytest includes
# the committed-artifact copyright audit — so a PR touching only those paths is still tested
# and audited, not silently skipped. CODE_WALKTHROUGH.md also maps to the pipelines lane: its
# file:line pointer guard (pipelines/tests/test_code_walkthrough.py) must run when the doc
# changes, even if no pipeline code did.
touched=$(printf '%s\n' "$changed" \
  | grep -oE '^(apps/[^/]+|pipelines|runs|texts|configs|CODE_WALKTHROUGH\.md)' \
  | sed -E 's#^(runs|texts|configs|CODE_WALKTHROUGH\.md)$#pipelines#' | sort -u)

# fixtures/ holds cross-language shared fixtures (e.g. the failure-kind parity cases) asserted by
# BOTH the pipelines pytest and the apps/viewer vitest suites. It matches no prefix above, so a
# fixture-only edit would otherwise run ZERO tests and let the two implementations drift unchecked.
# Map it to both lanes.
if printf '%s\n' "$changed" | grep -qE '^fixtures/'; then
  touched=$(printf '%s\npipelines\napps/viewer\n' "$touched" | grep -v '^[[:space:]]*$' | sort -u)
fi

# runs/** and texts/** are read by BOTH lanes: pipelines pytest asserts the committed-run numbers and
# the corpus, and apps/viewer vitest asserts the SAME committed-run evidence (src/local/tutorialRun.
# test.ts loads the real runs/tutorial-2026-10-11 and pins its counts). The sed above maps these to
# the pipelines lane only, so a runs- or texts-only change (e.g. a sanctioned scoring rebaseline)
# would silently skip vitest — the exact multi-app dispatcher trap in lessons-critical (same class as
# the fixtures/ gap PR #44 closed; Spec 48's viewer break was the proof case). Map them to both lanes.
# NOTE: this means a pipelines-only builder touching runs/ or texts/ needs the pnpm toolchain to pass
# the gate (accepted on this machine).
if printf '%s\n' "$changed" | grep -qE '^(runs|texts)/'; then
  touched=$(printf '%s\npipelines\napps/viewer\n' "$touched" | grep -v '^[[:space:]]*$' | sort -u)
fi

if [ -z "${touched//[$'\n']/}" ]; then
  echo "test-dispatcher: no app/pipeline changed vs ${base} — nothing to test."
  exit 0
fi

status=0
while IFS= read -r app; do
  [ -z "$app" ] && continue
  cmd="$(test_cmd_for "$app")"
  if [ -z "$cmd" ]; then
    echo "test-dispatcher: '$app' has no registered test command — skipping."
    continue
  fi
  echo "test-dispatcher: $app -> $cmd"
  if ! bash -c "$cmd"; then
    echo "test-dispatcher: FAILED for $app"
    status=1
  fi
done <<EOF
$touched
EOF

[ "$status" -eq 0 ] && echo "test-dispatcher: all touched apps passed."
exit "$status"
