# CORE-002 - Authoritative specification and drift validation

Generated from [the specification](../specs/experiments.json). State: `implemented`. Dependencies: None.

## Problem

Hand-edited cards/tickets/matrices drift and hide coverage or dependency defects.

## Contract

- Define required schema fields and stable 96 IDs
- Generate catalog/cards/A-B tickets/core queue/matrices deterministically
- Validate references/dependency DAG and support read-only --check

## Acceptance

- Two generations from identical source produce identical text
- --check reports modified/missing outputs without writing
- Unknown dependencies/cycles/empty outcome contracts fail

## Failure and recovery

Preserve the spec and report the exact drift/schema error; do not repair statuses silently.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
