# CORE-011 - Remote execution and artifact handoff

Generated from [the specification](../specs/experiments.json). State: `specified`. Dependencies: [CORE-007](CORE-007.md), [CORE-008](CORE-008.md), [CORE-015](CORE-015.md).

## Problem

Heavy work should run on a selected capable host without leaking credentials or losing task identity.

## Contract

- Select explicit trusted host and scratch root
- Transfer only source/spec/original selected fixtures
- Verify remote runtime/source/job and returned artifact digests

## Acceptance

- Remote result matches requested source/settings/job identity
- Interrupted transfer remains incomplete
- Credentials and unrelated files never enter logs/packages

## Failure and recovery

Run a smaller local preview with remote qualification unavailable.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
