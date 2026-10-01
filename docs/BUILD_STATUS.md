# Build status

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

Reproduce with `python scripts/package.py`, `python scripts/check.py`, `python scripts/run.py test --blender /path/to/blender`, then `blender --background --factory-startup --python-exit-code 1 --python scripts/reopen_check.py -- --output build`. For real-window acceptance: `blender --no-splash --factory-startup --python scripts/ui_acceptance.py`. It installs into Blender's user add-on folder, enables the test process without saving global preferences, writes `build/ui/` and quits its own process. Cappy: `cd capture`, `npm ci`, then `BLENDER_BIN=/path/to/blender npm run verify`. See [CAPTURE](CAPTURE.md) for motion commands and remaining recording gates. Put render/cache scratch on a spacious volume.
