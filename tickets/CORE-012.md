# CORE-012 - Performance and quality measurement

Generated from [the specification](../specs/experiments.json). State: `specified`. Dependencies: [CORE-006](CORE-006.md), [CORE-007](CORE-007.md).

## Problem

Optimization claims need measured workload, hardware and visual cost.

## Contract

- Record timing/count/memory estimates with warmup policy
- Compare bounded baseline and changed settings
- Preserve representative-frame quality review alongside numerical metrics

## Acceptance

- Every claimed improvement has a comparable measured case
- Image/detail tolerance is checked before choosing faster settings
- Measurement failures remain explicit

## Failure and recovery

Use the verified cheap baseline and state that optimization is not measured.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
