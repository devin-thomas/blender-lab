# CORE-009 - Budgets cancellation and diagnostics

Generated from [the specification](../specs/experiments.json). State: `specified`. Dependencies: [CORE-008](CORE-008.md).

## Problem

Expensive jobs must stop within declared limits without success-shaped fallbacks.

## Contract

- Preflight memory/disk/time/concurrency budget
- Implement cooperative then process termination boundaries
- Preserve last complete item and failure-class diagnostics

## Acceptance

- Timeout/cancel release the worker and produce terminal incomplete state
- Resource cap blocks unsafe scale-up
- Retry is new identity and never silently expands budget

## Failure and recovery

Keep complete artifacts and logs while identifying incomplete frames/caches.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
