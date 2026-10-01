# CORE-014 - Scoped agent mutation and recovery

Generated from [the specification](../specs/experiments.json). State: `specified`. Dependencies: [CORE-003](CORE-003.md), [CORE-004](CORE-004.md), [CORE-005](CORE-005.md), [CORE-013](CORE-013.md).

## Problem

Live edits need inspected ownership, bounded intent and verified save boundaries.

## Contract

- Preflight source/target identity and trusted allowlisted operation
- Use separate staged copies/snapshots where practical
- Reinspect outcome and save only to the approved new artifact path

## Acceptance

- Changed target between inspect/apply prevents mutation
- Failed outcome leaves or restores the staged original with recovery state
- Unowned data is unchanged

## Failure and recovery

Move repetitive edits into a trusted versioned Python script and run on a new copy.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
