# Verification strategy

## Layers

| Layer | Establishes | Does not establish |
|---|---|---|
| Python/source checks | Syntax, metadata, manifest, packaging structure | Blender operator correctness |
| Headless Blender | Scene structure and declared evaluated assertions | N-sidebar interaction or visual quality |
| Render inspection | Preview appearance on a recorded renderer | Editable workflow or interchange fidelity |
| Real editor journey | Install, panel, generate, parameter, inspect, reset, save | Receiving-engine behavior |
| Blender glTF roundtrip | Export/reimport comparison for chosen fields | Full material or engine feature parity |
| Named engine import | Specific asset behavior in that engine/version | Every device or target renderer |

## Focused lab gates

BL-001 checks owned mesh and modifier data plus evaluated geometry. BL-002 checks image interpolation, UVs, color attributes, and material wiring. BL-003 evaluates the procedural result at more than one parameter value. BL-004 evaluates time-separated transforms. BL-005 evaluates forward simulation and compares movement against the initial position. BL-006 writes a selected glTF and reimports it for bounded geometry comparison.

The exact assertions live with source and receipts. This document describes intent; it does not upgrade an unexecuted assertion to evidence. Physics comparison uses tolerances and records Blender version; do not require byte-identical caches across machines.

## Editor acceptance

In a fresh file install/enable the ZIP, open the tab, build each lab, adjust its control, inspect the mechanism, and save/reopen a copy. Reset one lab while unrelated content exists and confirm unrelated content remains. Exercise the error path for an invalid output location. Check normal viewport scale and a narrow sidebar. Record the real journey separately from background tests.

## Evidence records

Record source commit, host, Blender version/build hash, command, timestamp, asserted fields, result, artifact paths, and remaining gates. Keep raw paths/logs/media local and publish a sanitized summary. Update [BUILD_STATUS](BUILD_STATUS.md) only after inspecting actual results.
