# CORE-015 - Trust local-only and public boundary

Generated from [the specification](../specs/experiments.json). State: `partial`. Dependencies: None.

## Problem

Blender Python and MCP can execute host code; the public baseline must avoid hidden private/network dependencies.

## Contract

- Keep untrusted blend automatic Python disabled
- Keep MCP listeners local unless an explicit authenticated boundary is built
- Package only reviewed public source/original inputs and exclude secrets/private paths

## Acceptance

- Unknown/arbitrary-code request is rejected at project APIs
- Public build runs without private checkout/account/key
- Stage/package inspection detects unreviewed private dependencies

## Failure and recovery

Use trusted local scripts on original neutral copies; external services remain opt-in and unavailable until qualified.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
