# CORE-016 - Qualification matrix and release controller

Generated from [the specification](../specs/experiments.json). State: `partial`. Dependencies: [CORE-002](CORE-002.md), [CORE-006](CORE-006.md), [CORE-007](CORE-007.md), [CORE-015](CORE-015.md).

## Problem

Implementation, preview, editor smoke, downstream acceptance and publication must remain distinct.

## Contract

- Record separate automated/editor/visual/receiver gates per source/runtime/profile
- Verify clean public-only package allowlist and source equality
- Promote reviewed artifacts only after applicable gates pass

## Acceptance

- Every passed matrix cell has matching current evidence
- Generated catalog --check and package/source checks pass
- Unavailable/pending downstream cells remain explicit in release summary

## Failure and recovery

Release only the verified local/source subset and retain pending gates visibly.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
