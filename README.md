# Blender Lab

**Make a thing. Change the mechanism. Inspect what survives.**

Blender Lab is an editable capability atlas inside Blender: **96 detailed experiment contracts**, **16 core infrastructure tickets** and **192 implementation/qualification tickets** cover Blender authoring and automation. Thirty-six implemented adapters span modeling, surfaces, procedural geometry, rigging, actions, staging, simulation, interchange, compositor, lighting, asset metadata and sprite production. Qualification is recorded separately for each adapter. The scene, node tree, modifier stack and timeline are the product; measured receipts explain what actually ran.

The first implementation targets Blender **5.2.2 LTS**. The add-on declares Blender 5.2 as its minimum; other releases remain unqualified until tested. Current execution evidence and remaining editor gates belong in [BUILD_STATUS](docs/BUILD_STATUS.md).

## Open the workshop

1. Run `python scripts/package.py` to create the local add-on ZIP.
2. In Blender, use Preferences > Add-ons > Install from Disk, select the generated ZIP, and enable Blender Lab.
3. In the 3D Viewport, press **N**, open **Blender Lab**, search/filter the atlas and build an available lab. Planned entries show their contract and status.
4. Change the available controls and click Apply controls, then inspect its objects, materials, modifiers, nodes, or timeline. Save your own `.blend` copy when you want to keep edits.

[START_HERE](docs/START_HERE.md) explains the first journey and scripted workflow. Each Open experiment action creates a new separate scene. Apply controls changes the active lab; Reset this lab asks for confirmation and replaces only that active lab scene, discarding its edits.

```powershell
python scripts/run.py --blender "C:\path\to\blender.exe" build
python scripts/run.py --blender "C:\path\to\blender.exe" test
python scripts/run.py --blender "C:\path\to\blender.exe" render
python scripts/run.py --blender "C:\path\to\blender.exe" export
```

Generated scenes, renders, exports, logs, and ZIPs remain local and ignored. The repository ships source and original procedural fixtures. No account, key, network service, or recording application is required for the workshop. Optional [capture tooling](docs/CAPTURE.md) supports documentation and analysis.

## Implemented experiments

| ID | Workshop | What you can inspect |
|---|---|---|
| BL-001 | Silhouette Foundry | Mesh topology, bevels, and modifier evaluation |
| BL-002 | Pixel Surface Studio | Closest sampling, UV regions, and vertex-color modulation |
| BL-003 | Instance Conservatory | A parameterized Geometry Nodes array |
| BL-004 | Motion Signal | Editable keyframes and evaluated motion |
| BL-005 | Gravity Bench | Active/passive rigid bodies and simulated positions |
| BL-006 | Portable Artifact | Selected glTF export and reimport comparison |
| BL-007 | Modular environment kit | Linked wall/corner/post meshes, doorway seams, packed atlas and stairs |
| BL-008 | Vertex shade composition | Identical texture-only, vertex-unlit and vertex-lit fixtures |
| BL-009 | Gradient-card atmosphere | Editable transparent gradient quads, alpha wiring and depth offsets |
| BL-010 | Rig and deformation desk | Weighted and rigid limbs, bone weights and evaluated deformation |
| BL-011 | Action and NLA bench | Slotted Actions, NLA blends and sampled motion |
| BL-012 | Camera and staging lab | Gameplay/showcase cameras, projected motif size and coverage |
| BL-013 | Geometry Nodes scatter | Seeded surface scattering and realized instance geometry |
| BL-014 | Geometry Nodes field inspector | Named field values, domains and selection cardinality |
| BL-015 | UV and texel audit | Measured UV density, stretch and island margins |
| BL-019 | Compositor bench | Packed original chart, clean/treatment graph and pixel comparisons |
| BL-020 | Lighting observatory | Light energy, renderer selection and neutral references; pixel parity pending |
| BL-021 | Asset-browser kit | Marked assets, stable metadata, packed dependencies and custom thumbnails |
| BL-022 | Sprite-sheet camera | Transparent sampled frames, PNG atlas order and alpha roundtrip |
| BL-025 | Topology surgery | Editable BMesh cuts, limited dissolve and manifold checks |
| BL-026 | Boolean assembly | Exact Boolean operations and evaluated volume |
| BL-027 | Retopology projection desk | Editable projection cage and measured shrinkwrap target fit |
| BL-028 | Mesh attribute contracts | Attribute type/domain cardinality and known samples |
| BL-029 | Shape-key expression desk | Relative brow/mouth keys and evaluated offsets |
| BL-030 | Curve path and profile forge | Editable curve sweep/profile and converted mesh copy |
| BL-031 | Typography geometry desk | Bundled font, text fitting, extrusion and converted geometry |

| BL-016 | Bake and material bridge | Actual Cycles contribution bake, UV target and packed portable image |
| BL-033 | Geometry Nodes repeat machine | Paired repeat state, zero-iteration identity and bounded tower growth |
| BL-035 | Typed node-group interface | Stable socket identifiers, typed modifier RNA and measured rail dimensions |
| BL-036 | Material graph migration | Staged known schemas, original recovery graph and measured tint response |
| BL-037 | Drivers and constraint observatory | Trusted non-scripted dependency and ordered evaluated clamps |
| BL-038 | Inverse-kinematics reach desk | Two-bone crane, poles, limits and measured reach residuals |
| BL-039 | Pose asset library | Marked slotted pose Actions and scoped bone blending |
| BL-040 | Animation bake interchange | Separate visual-key Action, source preservation and interpolation error; export pending |
| BL-058 | World environment forge | Original packed equirectangular sky and rendered rotation/energy effects |
| BL-059 | Procedural material spectrum | Noise/Voronoi copper and stone, rendered scale/roughness effects |

All 96 [workshop cards](docs/experiments/INDEX.md) specify controls, original fixtures, interactions, positive/negative checks, ownership, budgets and fallbacks. Explore the [capability matrix](docs/CAPABILITY_MATRIX.md), [milestones](docs/MILESTONES.md), [roadmap](docs/ROADMAP.md) and [dependency tickets](tickets/README.md). Additional sculpting, baking, simulations, 2D/tracking, render profiles, interchange and connected services remain delivery work. Implemented cards retain open qualification gates; metadata does not establish full domain support.

## Build and extend

Read [SPEC](docs/SPEC.md), [ARCHITECTURE](docs/ARCHITECTURE.md), [OPERATIONS](docs/OPERATIONS.md), [ART_DIRECTION](docs/ART_DIRECTION.md), and [TEST_STRATEGY](docs/TEST_STRATEGY.md). Builders follow [AGENTS](AGENTS.md) and the [extension contract](docs/EXTENSION_CONTRACT.md). [SOURCE_INDEX](docs/SOURCE_INDEX.md) records the research lineage and confidence boundaries; [ADR](docs/ADR.md) records decisions.

Edit `specs/experiments.json`, then run `python scripts/generate_catalog.py`. Validate with `python scripts/package.py`, `python scripts/check.py` and `cd capture; npm test`. [Data contracts](docs/DATA_CONTRACTS.md), [profiles](docs/EXECUTION_PROFILES.md) and [automation surfaces](docs/AUTOMATION_SURFACES.md) distinguish the current runtime spine from planned services.

Project source is [GPL-3.0-or-later](LICENSE), chosen for the Blender add-on. Independently supplied tools and assets retain their own licenses. No third-party game art is bundled; see [ASSET_POLICY](docs/ASSET_POLICY.md). This is an independent project, not endorsed by Blender or the games used as research references.
