# Cappy and Blender Lab

This is a lab-owned Blender adapter for the released **@uppercut-labs/cappy 0.1.0** controller. The package bundles the official Cappy agent skill at `node_modules/@uppercut-labs/cappy/.agents/skills/cappy/SKILL.md`. The unscoped npm package `cappy` belongs to a different project; do not install it.

Cappy owns launch, session storage, replay handoff, OBS recording and media processing. Blender Lab owns the six experiments and their verification. This adapter implements Cappy's version 1 loopback WebSocket protocol without changing the Cappy source repository or pretending the shipped Godot addon runs in Blender.

## Install and inspect

Requires Node.js 24 or newer and an existing Blender installation. Run from this directory:

```sh
npm ci
npm test
npm run scenarios
npm run doctor
```

`scenarios` negotiates with the actual released Cappy CLI and lists `bl-001` through `bl-006`. Cappy requires lowercase scenario identifiers; the Blender lab cards and Python API use `BL-001` through `BL-006`.

The npm scripts use the checked-in portable `cappy.config.example.json` explicitly. For customized direct CLI commands, copy that file to the ignored `cappy.config.json`, or keep passing `--config cappy.config.example.json`.

Set `BLENDER_BIN` to the existing Blender executable, or put Blender on PATH. On macOS:

```sh
export BLENDER_BIN=/Applications/Blender.app/Contents/MacOS/Blender
npm run verify
```

On Windows PowerShell:

```powershell
$env:BLENDER_BIN = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
npm run verify
```

Use the actual installed path. These commands do not install Blender, OBS or FFmpeg.

## What verification proves

`npm run verify` uses the official CLI to list six scenarios, records a scripted recipe for each lab, then invokes `cappy replay <session-id> --no-capture`. Both recording and replay launch real Blender with `--background --factory-startup --python-exit-code 1` and the checked-in `scripts/entry.py`. Each verifies the lab at numeric `value=1.25`, saves its blend file and requires an evidence report confirming the requested lab, value and passing outcome.

The adapter stores small SHA-256 checked inline recipes containing only format, lab ID and numeric parameter. Replaying rebuilds and verifies that same configuration. It does **not** record arbitrary mouse/keyboard editing or promise byte-identical Blender files or rigid-body solver output across versions. It deliberately does not advertise `deterministic_replay`.

`record` uses Cappy's session API to persist one scripted recipe; it completes automatically after Blender verification. To choose a single recipe:

```sh
BLENDER_LAB_SCENARIO=BL-003 BLENDER_LAB_VALUE=1.5 npx cappy record -C . --config cappy.config.example.json --json
npx cappy replay <returned-session-id> --no-capture -C . --config cappy.config.example.json --json
```

`BLENDER_LAB_SCENARIO` defaults to `BL-001`; `BLENDER_LAB_VALUE` defaults to `1`. Supported values are finite numbers from `0.1` to `2`, matching Blender's panel control. The scenario protocol accepts a `value` parameter with that same range. Unknown parameters, presentation overrides, invalid replay digests and failed Blender checks return structured failures. Heartbeats remain responsive during the Blender process; cancel stops it. A 120-second timeout also stops Blender, escalating to forced termination after two seconds if needed. The adapter waits for process exit and closed output pipes before writing its log. An early stop fails rather than declaring an unfinished lab verified.

The advertised capabilities are `scenarios` (six parameterized lab recipes), `freeform_recording` (Cappy's record/session storage lifecycle, used here for one automatically completed scripted recipe), and `replay` (rebuild and verify a returned recipe). The recording capability does not mean arbitrary Blender UI input is recorded. There is no `deterministic_replay`, `time_scale`, `alternate_cameras`, `seek` or `snapshots` claim.

Output is local and ignored: `.cappy/sessions/` contains Cappy's session, hashed replay and timeline; `../build/cappy/` contains Blender's generated scene, evidence and process log. `verification.json` records host, package version, session IDs and replay evidence after all six checks pass. Do not commit those generated artifacts.

## Capture acceptance remains separate

This adapter currently launches Blender in background mode. Its timeline measures the elapsed lab execution, not an animation shown in a visible Blender window. **A passing test, scenario listing or replay check does not verify OBS capture.** `cappy run`, captured replay and `record --capture` are not acceptance commands for this background adapter.

A future visible adapter must prepare the same scene inside Blender, signal ready only when the intended view is visible, apply the parameter when Cappy starts, and report events when they actually appear. Then the user must have a running OBS and confirm an existing scene shows only the intended Blender window before the first recording. The official Cappy skill says never to create, edit or switch OBS scenes/settings on the user's behalf; preserve this boundary. Keep any OBS WebSocket password only in an environment variable, never in config, logs or Git.

The protocol tests use an explicitly injected mock lab runner. They prove handshake, immediate post-welcome requests, parameter validation, heartbeat, scenario/replay lifecycle, digest validation, failure propagation and cancellation. Only `npm run verify` with the real Blender executable establishes Blender playback acceptance, and neither check establishes screen capture acceptance.
