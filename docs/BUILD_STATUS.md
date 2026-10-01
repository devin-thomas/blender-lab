# Build status

## Historical foundation qualification

Qualified on 2026-10-01: Blender **5.2.2 LTS**, build **d13f752e3b9c**, macOS arm64 Research. Minimum declared version is 5.2; other editor hosts/versions remain unqualified. Source-only checks also passed on Windows Python 3.14 and Node 24.18.0.

Final Blender source SHA-256 (sorted `blender_lab/*.py` bytes): `05e921ca61a72e8f108b3402d78e33ef66f056d4edaf5b20407fe2aa5d5696e6`. Final test receipt began 2026-10-01 15:10:31 UTC. Raw receipts, machine paths, generated media and exports remain ignored.

| Gate | Result | Evidence scope |
|---|---|---|
| Catalog/docs/source-only ZIP | Passed | Six matching IDs/titles, valid local links, exact Python source + GPL license allowlist |
| Headless outcomes | Passed | All six labs, distinct outcomes at values 0.5/1.5, shared UI Apply and scoped Reset |
| Saved-file reopening | Passed | All six `.blend` files reopened/reverified, packed pixel assets included |
| Installed add-on / real window | Passed automatically | ZIP install/enable, six Open/Apply/Reset journeys, unrelated scene sentinel preserved, eight resets per lab with stable datablock counts, drawn panel screenshot inspected |
| UI export preservation | Passed | Two exports create distinct take folders |
| Preview stills | Rendered/inspected | Six original 800x600 Cycles previews and contact sheet |
| Native motion | Rendered/inspected | BL-004 60 frames / 2.50s; BL-005 90 frames / 3.75s; 640x480, 24fps, H.264/yuv420p, FFprobe verified; early/middle/end inspected |
| Cappy | Passed | Official @uppercut-labs/cappy 0.1.0; seven protocol/lifecycle tests; six scenario discoveries; six real Blender recipe record/replay pairs |
| OBS capture | Not run | Delivered adapter uses background Blender; native renders are separate evidence |
| Godot receiving engine | Not run | Separate import/appearance contract required |
| Human workflow/art approval | Not run | Automated editor checks do not prove comfort, accessibility or artist approval |

Measured defaults: BL-001 8 base / 24 evaluated vertices with changing bevel coordinates; BL-002 packed 32px Closest image, corner colors, UVs, strength and connected shader graph; BL-003 five cones / 60 evaluated vertices spanning X -3.3..3.3; BL-004 Z 1.2/3.2/1.2 at frames 1/30/60; BL-005 release Z4.0 settles Z1.2 by frame90 within 1.0..1.5 tolerance. BL-006 reimports exactly one active-scene artifact, 24 vertices/12 triangles, matching world bounds, UV/color attribute presence and 32px material image. Numerical UV/color/image fidelity and arbitrary shader parity are outside this check.

Final Cappy sessions (BL-001..006 in order): `ses_0b8080ad-096d-411e-a0dd-b37aafe53805`, `ses_5c0b709b-39a1-4668-a06e-f93bb1f8d2a3`, `ses_1db69164-6283-4932-9048-5e4f38ebbca6`, `ses_f6b9ec91-f296-44b5-b257-fd457ed1ba66`, `ses_03382a26-3901-47b8-8304-3437c15823f4`, `ses_ec5230a6-db20-43dd-a2e0-3bcd0e0b66ec`. Each completed at value1.25 and replay verified the matching lab. Recipe recording does not record arbitrary editing or promise bit-identical physics.

Reproduce with `python scripts/package.py`, `python scripts/check.py`, `python scripts/run.py test --blender /path/to/blender`, then `blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python scripts/reopen_check.py -- --output build`. For real-window acceptance: `blender --factory-startup --disable-autoexec --python scripts/ui_acceptance.py`. The script suppresses splash only in that process, installs into Blender's user add-on folder, enables without saving global preferences, writes `build/ui/` and quits its process. Cappy: `cd capture`, `npm ci`, then `BLENDER_BIN=/path/to/blender npm run verify`. See [CAPTURE](CAPTURE.md). Use spacious scratch.

## Comprehensive atlas and authoring expansion

The specification now contains 96 cards in 24 domains, seven milestones, 16 core tickets and 192 lab A/B tickets. Nine scene adapters are implemented. Generated views and dependency validation are source checks; they do not qualify the remaining 87 adapters.

Expansion checks on the same Blender 5.2.2 LTS build:

| Gate | Result | Scope |
|---|---|---|
| Catalog/DAG/docs/package | Passed | 96 stable entries; nine available IDs agree with Python/Cappy; exact source/license/catalog ZIP |
| Outcome suite | Passed | Nine adapters; 0.1/2 endpoints, 0.5/1.5 effects, invalid values, conflicting retry, wrong scope, planned ID rejection, sentinel preservation |
| Persistence | Passed | Nine generated files reopened/reverified with packed dependencies |
| Installed native host | Operator smoke passed | 96-entry installed catalog, search/available filter/planned inspection, nine Open/Apply/Reset journeys, 72 repeated resets with stable datablocks |
| Editor appearance | Screenshot inspected | Clean actual Blender window and drawn atlas panel; first-run splash suppressed without saving preferences |
| New previews | Inspected | Modular kit, three shade models and gradient cards; missing kit shade data caught in preview and fixed with shader assertions |
| Cappy | Passed | Nine real record/replay pairs at value1.25; seven protocol/lifecycle tests; background recipe scope |
| Expanded card qualification | Pending | Feature-specific new failure fixtures, profile/resource admission and complete B-ticket contracts still require evidence |
| MCP/OBS/receiving engine/human | Not run | Separate live connection, captured media, downstream and artist/workflow gates |

BL-007 measures eight kit parts sharing five meshes, zero doorway seam/corner pivot error at default, stair fit, packed atlas and valid vertex shade on every part. BL-008 verifies identical 56-vertex fixtures under emission/emission/Principled graphs and shared packed texture. BL-009 verifies five editable cards, texture-alpha/mix/output links, gradient ranges, shader strength and depth offsets. Source and catalog hashes are recorded in local receipts; release acceptance uses the exact published Git revision.

A reviewed bounded outcome or operator-smoke result does not close all expanded card assertions. Durable jobs, atomic publication, enforced per-card budgets, visible capture and service integrations remain explicit core/experiment work.

Qualified source expansion: `44fdffe8e49598b5eb867af8f0a8b067c6f3270e`. A fresh public-only GitHub checkout passed package/catalog validation and all nine outcomes at 2026-10-01 16:10:15 UTC. Python-source SHA-256: `4eab6ad360771136bc183a779e646fd91a1e357017f7342ee92c5870c7425420`. Canonical LF catalog SHA-256: `e7eb82f763c9ac34b48d44e1313a876fbd2823311c02983a3166369350ec92bd`. Generator writes/checks exact UTF-8 LF bytes so Windows and macOS packages carry identical catalog bytes.

Installed editor qualification completed 16:07:07 UTC; nine files reopened after outcome checks. Final Cappy recipe qualification began 16:07:37 UTC, all nine sessions completed with verified replay. New authoring session IDs: BL-007 `ses_1d81f865-7943-40fc-9918-dbcd12ee12b9`, BL-008 `ses_8b95afd8-eb76-45eb-8031-b8de166601c9`, BL-009 `ses_78254583-2518-4b81-a722-eeb22bdd4809`. Raw receipts remain local and identify their actual catalog bytes; canonical package requalification follows the publication revision rather than reusing older media as new evidence.


## Typed authoring wave: 26 implemented adapters

Published source checkpoint `8a09f0bf21eab488cd440bb640960234405ccff9` adds BL-010..015, BL-019..022 and BL-025..031. The atlas still contains 96 contracts; 26 adapters are implemented and 70 remain specified. GPT-6 Luna authored the geometry module and GPT-6.1 Sol authored motion and the typed/wave harness; root integrated production, controls, ownership and validation. Syntax-only worker checks preceded parent runtime waves.

A fresh public-only GitHub checkout qualified on the same macOS arm64 / Blender 5.2.2 LTS `d13f752e3b9c` baseline:

| Gate | Result | Actual scope |
|---|---|---|
| Public source/package/catalog | Passed | 26 registered/Cappy IDs match; 96 cards, DAG, links and exact allowlisted source ZIP |
| Headless test + fresh reopen | Passed | All 26 labs, completed 2026-10-01 18:17:39 UTC; each test save loaded in another fresh process |
| Typed controls | Passed | 102 numeric-endpoint/enum alternatives across 34 controls; 202 invalid typed requests; measured output selectors, partial merge and reset/default/shared-data sentinels |
| Feature corruption | Passed | All 17 new adapters detect one broken scene mechanism each, recover through reset and preserve an unrelated scene sentinel |
| Installed editor | Operator smoke passed | Completed 18:17:48 UTC; 96-entry atlas, 26 Open/Apply/Reset journeys, 208 repeated resets with stable datablock counts, typed rig widgets actually drawn and screenshot inspected |
| New previews | Rendered and inspected | All 17 default stills; sprite atlas plus representative alpha frames inspected; original neutral fixtures and intended mechanisms remain editable |
| Cappy | Passed | Seven protocol/lifecycle tests; all 26 real scalar recipe record/replay pairs, began 18:19:20 UTC; no capture |
| Complete cards/profiles/downstream/human | Pending | B tickets, named engines/devices and artist acceptance remain separate |

Python module SHA-256: `00d2a3fdbe57dcbc2398b3fb5172a489c7808766395733a1bbad4170e76406ad`. Checkpoint catalog SHA-256: `4e8ffb06c6038f13170c9a5caaa625e7dc7bb8a4a8ff0a5e240d9bcfb0ac51d3`. Source identity, commands, process deadlines and per-lab evidence are in ignored wave manifests. The status-only catalog promotion changes its hash without changing the qualified controls or mechanisms; release-pin requalification is recorded separately.

Testing caught and fixed real failures: integer ID-property bounds, mesh replacement invalidating its object, use of freed evaluated meshes, generated checker packing, Python compositor menu names, lazy packed-image loading after reopen, unreferenced sprite atlas persistence, and asset fake-user retention leaking across resets. Cleanup clears owned fake-user retention only when no real references survive.

Acceptance limits stay explicit. BL-019 compares clean/requested/enabled pixels at 96x64 and has a rendered 800px default preview; full-size readability/treatment comparison is still unqualified. BL-020 checks actual light/renderer/reference data and a Cycles preview, not paired luminance, EEVEE parity or a named GPU backend. BL-021 saves/reopens actual marked assets with packed dependencies and custom previews; independent library append remains pending. Geometry field/attribute/topology fixtures require their native data/editor inspection rather than inferring field values from a still. Cappy v1 covers the documented scalar shortcut; it does not replay every typed control or arbitrary editing. The camera lab deliberately frames its subject; a full-plinth label is outside that gameplay frame.

Reproduce staged checks with `python scripts/wave.py test --blender PATH --output build/waves` (the 17 authoring adapters by default), explicit `--labs` for any implemented subset, and `blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python scripts/feature_failures.py -- --output build/negative`. Use the existing installed-editor and Cappy commands above for their separate surfaces. Raw outputs stay local; no personal assets or vendor account information enter public source.

## Ten additional labs: background qualification

Source checkpoints `0f9f46d` and `4e234e4de191b6bbb37e19127cd3dfb403fe33fe` add BL-016, BL-033, BL-035..040 and BL-058..059. There are now **36 implemented adapters**, including **27 typed adapters / 54 controls**, in the 96-contract atlas; 60 remain specified. GPT-6 Luna implemented the surface and node modules; GPT-6.1 Sol implemented kinematics and independently reviewed the integration. Parent runtime waves followed worker syntax checks.

Every Blender invocation in this pass used `--background` on macOS arm64 / Blender 5.2.2 LTS `d13f752e3b9c`. No GUI Blender process was opened, no desktop focus was requested, and no add-on installation or global preference change occurred. The new ten retain `editor=not-run`; the background operator checker does not promote that gate.

| Gate | Result | Measured scope |
|---|---|---|
| Source/package/catalog | Passed | 36 Python/Cappy IDs, deterministic 96-card catalog/DAG, documentation links and exact source-only ZIP |
| Clean published-source regression | Passed | All 36 tests and fresh-process reopens at source checkpoint 4e234e4; completed 2026-10-01 19:23:48 UTC |
| Typed alternatives/admission | Passed | 161 valid alternatives across 54 controls and 327 invalid typed requests; this ten-lab wave adds 59 alternatives / 125 rejections |
| Recovery regression | Passed | Shared bake image preserved across two replacements; socket display reorder preserves identifier-based geometry; rejected damaged migration allocates no staging data |
| New mechanism corruption | Passed | Ten damaged mechanisms detected; reset recovers and preserves the unrelated-scene sentinel |
| Background operators | Passed | Ten Open/Apply/Reset journeys and 80 repeated stable reset cycles; background flag and source identity recorded |
| New preview stills | Rendered/inspected | Ten 800x600 default stills; repeat gaps, migration UV texture and distinct stone material corrected after inspection |
| Cappy | Passed | Seven protocol/lifecycle checks and 36 actual scalar record/replay pairs; @uppercut-labs/cappy 0.1.0 / Node 25.9.0 on macOS; began 19:23:48 UTC; captured=false |
| New native editor / downstream / human | Not run | No drawn-panel, dialog, named receiving-engine, live MCP/OBS or artist acceptance claimed |

Python module SHA-256: `365a2e7d39ed0a998e83b2ae1d8c99fb438328b4fca032595057c9da3a5bd0f2`. Source-checkpoint catalog SHA-256: `b9bfdd0b75cfa5c5ff8a84522ec3cb4e47182f52706c294cc6c0ce0bfab05fe7`. Status promotion changes the catalog hash while preserving the qualified mechanisms and controls. Cappy v1 covers the scalar compatibility recipe, not every typed field or arbitrary editing. Raw job manifests/logs/scenes/media remain ignored in owned scratch; the internal repository pins the final exact public revision.

BL-016 performs a real Cycles diffuse-color bake with explicit active image/UV/selection context, packs the result, measures image dimensions and margin-dependent pixels, and retains its editable source. Matched source/portable render tolerance remains pending. BL-033 evaluates paired repeat state at zero and bounded iterations. BL-035 uses stable socket identifiers and the runtime's typed modifier RNA; display reorder is exercised. BL-036 stages known graph schemas, keeps v1 recovery and unrelated nodes, verifies non-overlapping UV islands, and compares actual texture/tint pixels. Full tint correctly masks the original texture.

BL-037 evaluates non-scripted SUM dependencies through ordered constraints. BL-038 measures actual two-bone tip residual, poles and declared limits, including unreachable targets. BL-039 applies marked slotted pose Actions only to selected bones and checks untouched channels. BL-040 writes separate visual-key Action channels from evaluated bone matrices, compares every keyed and intervening frame, and proves source preservation. A step-4/range-60 probe exceeded the 0.04 interpolation tolerance and was explicitly reported as sparse sampling; sampled transforms remained within 3e-5. No interchange-ready or exporter/receiver pass is claimed.

BL-058 and BL-059 compare real 96x72 rendered pixels for environment direction/energy and procedural scale/roughness. Zero world strength explicitly makes rotation unobservable. Temporary PNG decoding avoids inaccessible background Render Result buffers and restores render/material/world state. Original LDR maps, CPU previews and these small probes do not qualify HDR, renderer/GPU parity or full-card workload profiles.

The implementation fixes include actual 5.2 RepeatItem/socket types and modifier RNA, explicit dependency-graph invalidation, an initially singular IK chain, stale evaluations from driven and animated channels sharing one target, packed recovery-material persistence, valid-control identity comparisons, and the independent review's shared-image/staged-material defects. Full B-ticket profiles, capture and human gates remain open.

Reproduce the selected batch with `python scripts/wave.py test --blender PATH --labs BL-016 BL-033 BL-035 BL-036 BL-037 BL-038 BL-039 BL-040 BL-058 BL-059 --timeout 180`. The wave now defaults to all 27 typed adapters. Use the [background operator command](OPERATIONS.md#background-only-acceptance) for focus-preserving reset checks, `feature_failures.py` for negative mechanisms, and [Cappy subset verification](../capture/README.md) for recipe replay.
