# CORE-007 - Runtime and execution-profile inventory

Generated from [the specification](../specs/experiments.json). State: `specified`. Dependencies: [CORE-006](CORE-006.md).

## Problem

Configured version, device or server names are not execution proof.

## Contract

- Detect Blender binary/version/build/options and permitted surface
- Inventory CPU/GPU/editor/disk/receiver requirements
- Return explicit unavailable profile states with useful local fallback

## Acceptance

- Runtime report matches the actually launched process
- GPU/server/receiver availability is tested separately
- Missing optional capability does not block the no-cloud baseline

## Failure and recovery

Run the qualified local CPU/CLI subset and list unavailable profiles.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
