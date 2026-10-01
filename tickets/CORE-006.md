# CORE-006 - Operation receipts and artifact identity

Generated from [the specification](../specs/experiments.json). State: `partial`. Dependencies: [CORE-003](CORE-003.md), [CORE-004](CORE-004.md).

## Problem

A nonempty file or old success JSON cannot prove the current task completed.

## Contract

- Record source/runtime/input/settings/job/artifact identity
- Separate stdout logs from final structured result
- Sanitize tracked summaries while retaining raw local receipts

## Acceptance

- Receipt identity and digests match the current request/artifacts
- Stale or incomplete receipt fails
- Exact asserted fields and remaining gates are recorded

## Failure and recovery

Preserve current failure logs and previous evidence with distinct identities; never reinterpret it as the new run.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
