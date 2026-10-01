# CORE-003 - Typed operation and control contracts

Generated from [the specification](../specs/experiments.json). State: `partial`. Dependencies: [CORE-001](CORE-001.md), [CORE-002](CORE-002.md).

## Problem

Agents and UI must select known operations and meaningful controls rather than arbitrary Python or ordinal sockets.

## Contract

- Version operation IDs/control schemas and ownership requirements
- Share validation between native/scripted paths
- Return explicit errors for invalid values/unavailable context

## Acceptance

- Same typed request gives the same declared outcome through supported surfaces
- Unknown operations and nonfinite/out-of-range values fail before mutation
- UI exposes applicable bounds and unavailable reasons

## Failure and recovery

Use trusted checked-in scripts on original copies while unsupported interactive surfaces stay unavailable.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
