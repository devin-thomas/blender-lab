# CORE-008 - Isolated job runner and queue

Generated from [the specification](../specs/experiments.json). State: `specified`. Dependencies: [CORE-004](CORE-004.md), [CORE-006](CORE-006.md), [CORE-007](CORE-007.md).

## Problem

Batch work needs resource isolation, job identity and truthful terminal states.

## Contract

- Validate versioned allowlisted task envelopes
- Launch a fresh Blender process per canonical job
- Track queued/running/completed/failed/cancelled states and separate output roots

## Acceptance

- Concurrent jobs cannot mutate one another outputs/state
- One worker failure does not corrupt completed work
- No arbitrary-code or unowned-path request launches

## Failure and recovery

Use bounded sequential CLI jobs with independent receipts.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
