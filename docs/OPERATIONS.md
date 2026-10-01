# Operation contract

## Native controls

**Open experiment** creates a new separate owned scene. **Experiment value** accepts 0.1 through 2.0; **Apply experiment value** changes the active scene's mechanism. **Reset this lab** asks for confirmation and replaces only that active owned scene, discarding its edits. Other scenes remain. BL-006 adds **Output folder** and **Export verified glTF**.

| Lab | Value controls | Useful inspection |
|---|---|---|
| BL-001 | Bevel width: 0.08 x value | Base mesh versus evaluated modifier result |
| BL-002 | Vertex shade strength: value / 2 | Packed original atlas, UVs, shader and color attribute |
| BL-003 | Array count: rounded 5 x value, minimum 1 | Mesh Line, instances, realization |
| BL-004 | Travel apex: 1.2 + 2 x value | Frames 1, 30, 60 and editable keys |
| BL-005 | Release height: 2 + 2 x value | Active/passive roles, forward playback from frame 1 |
| BL-006 | Artifact X scale: value | Selected source and reimported mesh contract |

These formulas describe the initial implementation and its original fixtures. They are not production-art budgets or measurements from a referenced game.

## CLI

`python scripts/run.py ACTION --blender PATH [--lab BL-001] [--value 1] [--output PATH]`

Actions are `build`, `test`, `render`, and `export`. Without a lab selection, all six labs run. The default output is the repository's ignored `build/`. `BLENDER_BIN` or a Blender executable on PATH can supply the executable when `--blender` is absent.

Every action generates and verifies its selected labs, saves `.blend` source artifacts, and writes a local `evidence.json`. BL-006 verification performs glTF export/reimport. `test` adds alternate-value comparisons and scoped-reset checks; `render` adds one still per selected lab. This is a source-driven background workflow; it does not automatically prove native panel interaction.

## Evidence schema

The runner receipt includes schema version, Blender version/build hash, combined add-on source SHA-256, timestamp, action, selected lab IDs, applied values, and assertion metrics. The receipt is written after the selected run completes. A nonzero Blender/Python operation must propagate through the host runner; inspect the error rather than treating a previous receipt as the new run's result.

Record the Git commit separately for release acceptance. The source hash identifies add-on source, not every documentation or orchestration file. The [evidence ledger](BUILD_STATUS.md) records reviewed results and limitations.
