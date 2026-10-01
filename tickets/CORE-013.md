# CORE-013 - Live MCP discovery and context boundary

Generated from [the specification](../specs/experiments.json). State: `specified`. Dependencies: [CORE-003](CORE-003.md), [CORE-007](CORE-007.md), [CORE-015](CORE-015.md).

## Problem

An agent must discover the actual official tools and inspect only the requested scene scope.

## Contract

- Verify official add-on/server identity and discover exposed schemas
- Inspect active scene/target/camera/render context
- Bound returned records and disclose unavailable context

## Acceptance

- Discovered schema matches actual server version
- Context reflects the selected scope without unrelated personal inventory
- Missing/mismatched server blocks guessed tools

## Failure and recovery

Use a selected saved-scene CLI inspection.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
