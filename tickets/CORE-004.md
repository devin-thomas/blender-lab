# CORE-004 - Output staging and deliberate promotion

Generated from [the specification](../specs/experiments.json). State: `partial`. Dependencies: [CORE-003](CORE-003.md).

## Problem

A fixed export path can overwrite unrelated content or expose half-completed output as final.

## Contract

- Use unique per-job staging directories
- Preflight resolved output paths and overwrite decisions
- Promote only verified complete artifacts with matching job/input identity

## Acceptance

- Unrelated existing output remains unchanged without explicit overwrite approval
- Failed job never promotes partial output
- Current artifact manifest matches promoted files

## Failure and recovery

Keep failed staging/logs and the previous approved artifact; retry in a new job.

## Evidence boundary

Implementation state is separate from qualification. Existing baseline behavior is recorded in docs/BUILD_STATUS.md; broader acceptance in this ticket remains pending until executed and reviewed.
