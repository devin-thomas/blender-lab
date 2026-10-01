# Blender Lab

**Make a thing. Change the mechanism. Inspect what survives.**

Blender Lab is an editable capability workshop inside Blender. Six original retro-styled scenes introduce mesh construction, pixel-textured materials, Geometry Nodes, animation, rigid-body simulation, and glTF interchange. The scene, node tree, modifier stack, and timeline are the product: rendered previews help you see the result, and automated receipts explain what was checked.

The first implementation targets Blender **5.2.2 LTS**. The add-on declares Blender 5.2 as its minimum; other releases remain unqualified until tested. Current execution evidence and remaining editor gates belong in [BUILD_STATUS](docs/BUILD_STATUS.md).

## Open the workshop

1. Run `python scripts/package.py` to create the local add-on ZIP.
2. In Blender, use Preferences > Add-ons > Install from Disk, select the generated ZIP, and enable Blender Lab.
3. In the 3D Viewport, press **N**, open **Blender Lab**, choose a lab, and build its scene.
4. Change Experiment value and click Apply experiment value, then inspect its objects, materials, modifiers, nodes, or timeline. Save your own `.blend` copy when you want to keep edits.

[START_HERE](docs/START_HERE.md) explains the first journey and scripted workflow. Each Open experiment action creates a new separate scene. Apply experiment value changes the active lab; Reset this lab asks for confirmation and replaces only that active lab scene, discarding its edits.

```powershell
python scripts/run.py --blender "C:\path\to\blender.exe" build
python scripts/run.py --blender "C:\path\to\blender.exe" test
python scripts/run.py --blender "C:\path\to\blender.exe" render
python scripts/run.py --blender "C:\path\to\blender.exe" export
```

Generated scenes, renders, exports, logs, and ZIPs remain local and ignored. The repository ships source and original procedural fixtures. No account, key, network service, or recording application is required for the workshop. Optional [capture tooling](docs/CAPTURE.md) supports documentation and analysis.

## The first six labs

| ID | Workshop | What you can inspect |
|---|---|---|
| BL-001 | Silhouette Foundry | Mesh topology, bevels, and modifier evaluation |
| BL-002 | Pixel Surface Studio | Closest sampling, UV regions, and vertex-color modulation |
| BL-003 | Instance Conservatory | A parameterized Geometry Nodes array |
| BL-004 | Motion Signal | Editable keyframes and evaluated motion |
| BL-005 | Gravity Bench | Active/passive rigid bodies and simulated positions |
| BL-006 | Portable Artifact | Selected glTF export and reimport comparison |

Each has a [workshop card](docs/experiments/INDEX.md) with a user payoff, mechanism, exercise, acceptance gate, and limitation. The [roadmap](docs/ROADMAP.md) specifies expansion opportunities without presenting them as shipped.

## Build and extend

Read [SPEC](docs/SPEC.md), [ARCHITECTURE](docs/ARCHITECTURE.md), [OPERATIONS](docs/OPERATIONS.md), [ART_DIRECTION](docs/ART_DIRECTION.md), and [TEST_STRATEGY](docs/TEST_STRATEGY.md). Builders follow [AGENTS](AGENTS.md) and the [extension contract](docs/EXTENSION_CONTRACT.md). [SOURCE_INDEX](docs/SOURCE_INDEX.md) records the research lineage and confidence boundaries; [ADR](docs/ADR.md) records decisions.

Project source is [GPL-3.0-or-later](LICENSE), chosen for the Blender add-on. Independently supplied tools and assets retain their own licenses. No third-party game art is bundled; see [ASSET_POLICY](docs/ASSET_POLICY.md). This is an independent project, not endorsed by Blender or the games used as research references.
