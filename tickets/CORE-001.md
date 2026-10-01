# CORE-001 - Catalog host and capability navigation

Generated from [the specification](../specs/experiments.json). State: `partial`. Dependencies: None.

## Problem

A six-button host cannot communicate the full Blender capability plan or real availability.

## Contract

- Read the versioned public catalog inside the add-on
- Provide search/category/status navigation across all 96 contracts
- Open only implemented runtime IDs and explain missing mechanism/profile/gate for the rest

## Acceptance

- Catalog and runtime registered IDs agree for implemented entries
- Search/category selection preserves stable IDs and states
- Specified cards cannot accidentally invoke missing builders

## Failure and recovery

Keep the verified implemented subset usable when an expansion profile is unavailable.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
