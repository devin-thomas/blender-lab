# Data contracts

## Atlas v2

Entries bind ID/title/category, visible moment, API research leads, typed controls, ordered interaction, original fixture, ownership, positive/negative checks, dependencies, profiles, budgets, fallback, limitations, milestone, primary sources and independent status fields. API leads remain research targets until runtime execution qualifies them. The generator checks the dependency DAG and emits deterministic views; edit the specification rather than generated cards.

## Local operations v1

Request fields: operation (open/apply/reset), implemented ID, finite value 0.1..2, scene instance ID for Apply/Reset and bounded request ID and optional immutable `controls_json` string (maximum 16384 characters). Nonempty typed payloads must be JSON objects keyed by exact declared control names; Reset rejects typed payloads. Booleans/nonfinite/out-of-range values and mismatched scope fail before mutation. Receipt fields: schema version, request ID, operation, lab, resulting instance/value, summary, UTC timestamp and serialized applied controls. Typed payloads are canonicalized for request signature comparison. Receipts live on generated scenes. Retry retention is process-local, capped at 128; restarting Blender loses it.

## Evidence

CLI reports include schemaVersion, Blender version/build hash, sorted Python-source and catalog SHA-256, timestamp, action and per-lab ID/status/requested value/metrics/final operation request ID/original Open request ID. Reports emit after assertions/saves; nonzero exit/logs are authoritative on failure. Reopen/editor reports have separate scopes. Exact published Git revisions identify the complete source and scripts.

## Planned manifests and jobs

Artifact manifests will bind run/recipe identity, hashes, role/format/dimensions/frames/units, source/runtime/profile, rights and assertions. Jobs will track queued/running/validating/publishing/succeeded/failed/cancelled, owned process/cache roots, budgets, checkpoints and terminal reason. Durable storage, schema migration, atomic publication and recovery remain core tickets; current receipts are not those services.
