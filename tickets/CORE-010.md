# CORE-010 - Checkpoint cache and resume contract

Generated from [the specification](../specs/experiments.json). State: `specified`. Dependencies: [CORE-006](CORE-006.md), [CORE-009](CORE-009.md).

## Problem

Independent frames, geometry conversions and simulation caches require different recovery rules.

## Contract

- Hash source/settings/input before checkpoint reuse
- Track complete item/cache ranges and integrity
- Define per-task resume/invalidation behavior with owned cache paths

## Acceptance

- Changed inputs invalidate incompatible cache
- Corrupt/missing checkpoint cannot be reused
- Resumed final manifest agrees with a clean bounded run

## Failure and recovery

Restart bounded work when a task lacks a safe resume contract.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
