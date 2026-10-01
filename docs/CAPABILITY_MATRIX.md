# Capability matrix

Generated from [specs/experiments.json](../specs/experiments.json). Profiles are requirements, not evidence that a host was qualified. API leads are recorded separately in each card. Budgets are original planning caps, not measured performance promises.

| ID | Category | Mechanism | Profiles | Milestone | Implementation | Automated / editor / visual / downstream |
|---|---|---|---|---|---|---|
| [BL-001](experiments/BL-001.md) | Mesh authoring | Mesh data plus a non-destructive Bevel modifier; compare authored and evaluated geometry. | local, editor | M0 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-002](experiments/BL-002.md) | Materials and UV | A packed 32x32 image, Closest sampling, explicit UVs, CORNER color attribute and linked multiply material graph. | local, editor | M0 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-003](experiments/BL-003.md) | Geometry Nodes | Mesh Line points instance an original cone; Set Material and Realize Instances form an editable Geometry Nodes graph. | local, editor | M0 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-004](experiments/BL-004.md) | Animation | Editable location/rotation keyframes evaluated at frames 1, 30 and 60. | local, editor | M0 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-005](experiments/BL-005.md) | Simulation | Rigid-body world, active box, passive plinth and sequential evaluation through 90 frames. | local, editor | M0 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-006](experiments/BL-006.md) | Interchange | Selected GLB export with supported image/color material, isolated-scene reimport and bounded mesh comparison. | local, editor | M0 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-007](experiments/BL-007.md) | Environment authoring | Direct mesh datablocks, explicit transforms and atlas-ready modular assembly in an owned scene. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-008](experiments/BL-008.md) | Materials and UV | Per-corner color attributes, triangulation inspection and controlled material contributions. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-009](experiments/BL-009.md) | Environment authoring | Original alpha-gradient images on intersecting cards with explicit material and depth placement. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-010](experiments/BL-010.md) | Rigging | Armature bones, deform vertex groups and evaluated Armature modifier. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-011](experiments/BL-011.md) | Animation | Actions, action slots, NLA tracks/strips and bounded blend evaluation. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-012](experiments/BL-012.md) | Camera and tracking | Explicit camera transforms, perspective/orthographic projection, clipping and composition guides. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-013](experiments/BL-013.md) | Geometry Nodes | Surface point distribution, seed-driven instances and explicit realization/export boundary. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-014](experiments/BL-014.md) | Geometry Nodes | Named attributes and Evaluate on Domain with output samples mapped to visible colors. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-015](experiments/BL-015.md) | Materials and UV | UV loop coordinates, geometric face area and texture-size-aware density/margin measurements. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-016](experiments/BL-016.md) | Materials and UV | Explicit Cycles bake context, UV target image and portable Principled material reconstruction. | local, editor, GPU | M1 | specified | not-run / not-run / not-run / not-run |
| [BL-017](experiments/BL-017.md) | Simulation | Cloth and Soft Body modifiers with pin/goal groups and owned cache ranges. | local, editor, disk | M1 | specified | not-run / not-run / not-run / not-run |
| [BL-018](experiments/BL-018.md) | Simulation | Fluid domain/flow/effector configuration and explicit data/mesh cache staging. | local, editor, disk | M1 | specified | not-run / not-run / not-run / not-run |
| [BL-019](experiments/BL-019.md) | Compositing | Scene compositor nodes, explicit image inputs and color-managed output. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-020](experiments/BL-020.md) | Lighting and rendering | Explicit light datablocks, world shader and matched Cycles/Eevee comparison. | local, editor, GPU | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-021](experiments/BL-021.md) | Asset management | Asset-marked object/material datablocks, previews and a local asset library path. | local, editor | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-022](experiments/BL-022.md) | Rendering deliverables | Orthographic animation rendering, alpha output and frame-to-atlas packing manifest. | local, disk | M1 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-023](experiments/BL-023.md) | Interchange | glTF export plus a public neutral Godot import scenario and explicit material/scale/animation assertions. | local, external | M1 | specified | not-run / not-run / not-run / not-run |
| [BL-024](experiments/BL-024.md) | Automation evidence | Versioned operation recipe, source hash, artifact manifest and optional official Cappy replay. | local, external | M1 | specified | not-run / not-run / not-run / not-run |
| [BL-025](experiments/BL-025.md) | Mesh authoring | BMesh split/dissolve operations with face-loop and boundary validation. | local, editor | M2 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-026](experiments/BL-026.md) | Mesh authoring | Exact Boolean modifier with separate owned operands and evaluated topology checks. | local, editor | M2 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-027](experiments/BL-027.md) | Mesh authoring | Shrinkwrap modifier, explicit projection direction and measured cage-to-target distances. | local, editor | M2 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-028](experiments/BL-028.md) | Data and geometry | Mesh attributes with explicit domain/type/cardinality contracts and controlled migration. | local, editor | M2 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-029](experiments/BL-029.md) | Mesh authoring | Relative shape keys with topology identity and evaluated displacement checks. | local, editor | M2 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-030](experiments/BL-030.md) | Curves and text | Curve splines, bevel/profile geometry and conversion of a separate evaluated copy. | local, editor | M2 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-031](experiments/BL-031.md) | Curves and text | Text Curve datablock, alignment/extrusion and explicit font dependency. | local, editor | M2 | implemented | bounded-outcomes-passed / operator-smoke-passed / previews-inspected / not-run |
| [BL-032](experiments/BL-032.md) | Geometry Nodes | Simulation input/output zones, initial state and frame-by-frame evaluated attributes. | local, editor, disk | M2 | specified | not-run / not-run / not-run / not-run |
| [BL-033](experiments/BL-033.md) | Geometry Nodes | Repeat zones with explicit iteration/state sockets and geometry growth limits. | local, editor | M2 | specified | not-run / not-run / not-run / not-run |
| [BL-034](experiments/BL-034.md) | Geometry Nodes | Geometry Nodes bake/cached state with artifact identity and explicit invalidation. | local, editor, disk | M2 | specified | not-run / not-run / not-run / not-run |
| [BL-035](experiments/BL-035.md) | Geometry Nodes | NodeTree interface sockets, stable identifiers, constraints and modifier inputs. | local, editor | M2 | specified | not-run / not-run / not-run / not-run |
| [BL-036](experiments/BL-036.md) | Materials and UV | Named node/link schema inspection, staged graph replacement and affected-output validation. | local, editor | M2 | specified | not-run / not-run / not-run / not-run |
| [BL-037](experiments/BL-037.md) | Rigging | Driver variables, explicit data paths and bounded object constraints. | local, editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-038](experiments/BL-038.md) | Rigging | Armature edit/pose bones, IK constraint chain, pole target and explicit limits. | local, editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-039](experiments/BL-039.md) | Rigging | Pose Actions/asset metadata, bone-channel filtering and explicit pose application. | local, editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-040](experiments/BL-040.md) | Animation | Visual-keying bake on a staged copy with explicit sampling, frame range and export. | local, editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-041](experiments/BL-041.md) | Grease Pencil | Grease Pencil layers/frames/drawings with stroke positions and material roles. | local, editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-042](experiments/BL-042.md) | Grease Pencil | Grease Pencil modifier stack with thickness/noise/geometry evaluation and source preservation. | local, editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-043](experiments/BL-043.md) | Grease Pencil | Grease Pencil frame data, original drawing exposures and frame evaluation. | local, editor, disk | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-044](experiments/BL-044.md) | Sculpt and paint | Trusted sculpt brush/operator context, mask data and before/after vertex samples. | editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-045](experiments/BL-045.md) | Sculpt and paint | Multires modifier levels, displacement evaluation and level-aware inspection. | local, editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-046](experiments/BL-046.md) | Sculpt and paint | Image paint context, UV/material target selection and pixel-difference validation. | editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-047](experiments/BL-047.md) | Camera and tracking | MovieClip tracking markers, camera solve settings and reconstruction-error inspection. | editor, disk | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-048](experiments/BL-048.md) | Camera and tracking | Tracking camera intrinsics and distortion/undistortion paths with grid error measurements. | local, editor | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-049](experiments/BL-049.md) | Compositing | Mask layers/splines, keyframed points and compositor mask output. | editor, disk | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-050](experiments/BL-050.md) | Camera and tracking | Plane tracking data and compositor planar deformation with explicit source corners. | editor, disk | M3 | specified | not-run / not-run / not-run / not-run |
| [BL-051](experiments/BL-051.md) | Video Sequence Editor | SequenceEditor strips, channels, trim ranges and explicit output timing. | local, editor, disk | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-052](experiments/BL-052.md) | Video Sequence Editor | VSE proxy rebuild, cache settings and original/proxy identity comparison. | local, editor, disk | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-053](experiments/BL-053.md) | Video Sequence Editor | Sound datablocks, VSE audio strips, FPS/sample-rate conversion and event frame markers. | local, editor, disk | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-054](experiments/BL-054.md) | Video Sequence Editor | Text-scene/image overlay composition, frame markers and subtitle/overlay timing manifest. | local, editor, disk | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-055](experiments/BL-055.md) | Compositing | View-layer passes, custom AOVs, multilayer EXR and explicit compositor routing. | local, GPU, disk | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-056](experiments/BL-056.md) | Lighting and rendering | Light-linking receiver/blocker collection membership and matched rendered measurements. | local, GPU | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-057](experiments/BL-057.md) | Lighting and rendering | Cycles shadow-catcher object settings, film transparency and compositor alignment. | local, GPU, disk | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-058](experiments/BL-058.md) | Lighting and rendering | World nodes, original equirectangular image and controlled environment rotation/strength. | local, editor | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-059](experiments/BL-059.md) | Materials and UV | Noise/Voronoi coordinates, ramps and explicit roughness/metalness material inputs. | local, editor | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-060](experiments/BL-060.md) | Materials and UV | Normal Map/Bump nodes, mesh tangent basis and bounded displacement geometry. | local, GPU | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-061](experiments/BL-061.md) | Materials and UV | Material alpha surface settings, depth ordering and matched renderer previews. | local, GPU | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-062](experiments/BL-062.md) | Volumes and hair | Volume datablock/grid loading, density material and bounded frame/file references. | local, GPU, disk, external | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-063](experiments/BL-063.md) | Volumes and hair | Curves geometry, guide attachment/interpolation and controlled strand counts. | local, editor, GPU | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-064](experiments/BL-064.md) | Simulation | Rigid-body constraints, connected object identities and forward solver evaluation. | local, editor, disk | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-065](experiments/BL-065.md) | Simulation | Mesh Sequence Cache modifier, frame mapping and topology-aware evaluated comparisons. | local, disk, external | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-066](experiments/BL-066.md) | Simulation | Dynamic Paint brush/canvas modifier and bounded vertex/image output cache. | local, editor, disk | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-067](experiments/BL-067.md) | Simulation | Particle emitter/settings and FieldSettings under explicit capability detection. | local, editor, disk | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-068](experiments/BL-068.md) | Lighting and rendering | Render motion-blur/shutter settings, transform/deformation motion and reference-frame comparison. | local, GPU | M4 | specified | not-run / not-run / not-run / not-run |
| [BL-069](experiments/BL-069.md) | Automation runtime | Versioned queued task specs launching isolated background Blender workers with per-job outputs. | local, disk | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-070](experiments/BL-070.md) | Automation runtime | Cycles device enumeration/selection and a measured original render with recorded driver/backend. | local, GPU | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-071](experiments/BL-071.md) | Automation runtime | Cycles CPU sampling, adaptive settings/denoise and matched quality/timing reference. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-072](experiments/BL-072.md) | Automation runtime | Depsgraph evaluation timing, operation trace and authored/evaluated counts. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-073](experiments/BL-073.md) | Automation runtime | Instance/evaluated datablock accounting, realization and bounded memory/vertex measurements. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-074](experiments/BL-074.md) | Asset management | Image dimensions/channels/source-path/packed-data audit with byte-budget estimates. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-075](experiments/BL-075.md) | Asset management | Library linking/appending, ID overrides and relationship/ownership inspection. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-076](experiments/BL-076.md) | Asset management | Asset metadata, catalog UUID sidecar contracts and preview/source identity. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-077](experiments/BL-077.md) | Blender extensions | Registered RNA properties, operator poll/execute, panel controls and unregister cleanup. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-078](experiments/BL-078.md) | Data and geometry | Scene unit settings, transform matrices and explicit export-axis contracts. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-079](experiments/BL-079.md) | Scene organization | Collections, LayerCollection visibility/exclusion and explicitly named view layers. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-080](experiments/BL-080.md) | Interchange | USD import/export operators with explicit hierarchy/material/animation options and reimport comparison. | local, external, disk | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-081](experiments/BL-081.md) | Interchange | Alembic export/import, CacheFile references and explicit sampled geometry comparisons. | local, external, disk | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-082](experiments/BL-082.md) | Interchange | Optional FBX exporter/importer, staged rig/action bake and bounded joint/sample comparison. | local, external | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-083](experiments/BL-083.md) | Interchange | OBJ/STL export/import with unit, normal, manifold and bounds contracts. | local, external | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-084](experiments/BL-084.md) | Interchange | Grease Pencil/vector import-export operator detection with stroke/bounds comparison. | local, editor, external | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-085](experiments/BL-085.md) | Data and geometry | PointCloud/mesh point attributes, bounds/unit normalization and explicit point-to-geometry conversion. | local, editor | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-086](experiments/BL-086.md) | Interchange | Versioned conversion jobs, exporter profiles, independent receipts and bounded reimport checks. | local, external, disk | M5 | specified | not-run / not-run / not-run / not-run |
| [BL-087](experiments/BL-087.md) | Automation surfaces | Official bpy module in a compatible pinned interpreter with data-first generation and explicit runtime report. | local, external | M6 | specified | not-run / not-run / not-run / not-run |
| [BL-088](experiments/BL-088.md) | Automation surfaces | Ordered Blender CLI arguments, trusted checked-in Python entry and versioned result envelope. | local | M6 | specified | not-run / not-run / not-run / not-run |
| [BL-089](experiments/BL-089.md) | Automation surfaces | Official Blender Lab MCP tool/resource discovery followed by scoped scene/data inspection. | editor, external | M6 | specified | not-run / not-run / not-run / not-run |
| [BL-090](experiments/BL-090.md) | Automation surfaces | Discovered official MCP mutation surface, ownership preflight, staged/source snapshot and post-mutation verification. | editor, external | M6 | specified | not-run / not-run / not-run / not-run |
| [BL-091](experiments/BL-091.md) | Automation surfaces | Project-owned authenticated API/queue envelope around fresh Blender worker processes and separate artifact retrieval. | local, external | M6 | specified | not-run / not-run / not-run / not-run |
| [BL-092](experiments/BL-092.md) | Automation surfaces | Per-frame/item checkpoints, source/input/settings hashes and resumed staging manifest. | local, disk | M6 | specified | not-run / not-run / not-run / not-run |
| [BL-093](experiments/BL-093.md) | Automation surfaces | Worker cancellation lifecycle, time/memory/disk budgets and structured diagnostic/result separation. | local, disk | M6 | specified | not-run / not-run / not-run / not-run |
| [BL-094](experiments/BL-094.md) | Automation evidence | Allowlisted package manifest, source/runtime/settings hashes, rights ledger and clean-root reproduction. | local, disk | M6 | specified | not-run / not-run / not-run / not-run |
| [BL-095](experiments/BL-095.md) | Automation evidence | Pinned runtime inventory, scoped outcome suite and per-version/profile evidence matrix. | local, editor, external | M6 | specified | not-run / not-run / not-run / not-run |
| [BL-096](experiments/BL-096.md) | Automation evidence | Public-only source/spec package, dependency manifest, local rebuild and scoped recovery workflow. | local, disk | M6 | specified | not-run / not-run / not-run / not-run |

## Profile boundaries

- local: trusted CPU/data-first scripts and the no-account public source baseline.
- editor: actual installed native UI/mode/area context; background success does not qualify it.
- GPU: enumerate and execute on a named backend/device; configuration alone is not a pass.
- disk: preflight owned cache/output scratch and enforce recorded size/frame limits.
- external: optional exporter/receiver/library/MCP/service; discover and qualify actual version/schema or report unavailable.

## Category coverage

| Category | Contracts |
|---|---|
| Mesh authoring | 5 |
| Materials and UV | 8 |
| Geometry Nodes | 7 |
| Animation | 3 |
| Simulation | 7 |
| Interchange | 8 |
| Environment authoring | 2 |
| Rigging | 4 |
| Camera and tracking | 4 |
| Compositing | 3 |
| Lighting and rendering | 5 |
| Asset management | 4 |
| Rendering deliverables | 1 |
| Automation evidence | 4 |
| Data and geometry | 3 |
| Curves and text | 2 |
| Grease Pencil | 3 |
| Sculpt and paint | 3 |
| Video Sequence Editor | 4 |
| Volumes and hair | 2 |
| Automation runtime | 5 |
| Blender extensions | 1 |
| Scene organization | 1 |
| Automation surfaces | 7 |
