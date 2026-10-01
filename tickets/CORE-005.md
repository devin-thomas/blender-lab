# CORE-005 - Scene and datablock ownership lifecycle

Generated from [the specification](../specs/experiments.json). State: `partial`. Dependencies: [CORE-003](CORE-003.md).

## Problem

Scope mistakes or incomplete cleanup can delete user data or accumulate simulation/action dependencies.

## Contract

- Track owned scene/collection/datablock identities
- Preserve shared/unowned data and reconcile generated scope
- Reset with confirmation and collect only unreferenced owned dependencies to a fixed point

## Acceptance

- Repeated resets stay bounded for every implemented lab including Actions/collections/material graphs
- Shared/unowned sentinel data survives
- Failed build does not purge unrelated datablocks

## Failure and recovery

Keep a separate authored copy and report orphan/ownership diagnostics instead of global purging.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
