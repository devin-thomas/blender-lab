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
