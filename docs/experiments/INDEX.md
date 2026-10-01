# Capability catalog

96 scoped capability contracts span Blender authoring, production, interchange and automation. Generated from [the reviewed specification](../../specs/experiments.json). Implementation and qualification are separate; a specified card is an unavailable capability with a real plan, not shipped behavior.

[Capability matrix](../CAPABILITY_MATRIX.md), [milestones](../MILESTONES.md), [roadmap](../ROADMAP.md), [ticket board](../../tickets/README.md).

## Mesh authoring

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-001](BL-001.md) | Silhouette Foundry | See a small bevel change a sparse original silhouette without destroying its base mesh. | implemented | expanded-qualification-pending |
| [BL-025](BL-025.md) | Topology surgery | Apply one topological edit and inspect manifoldness before trusting the silhouette. | implemented | expanded-qualification-pending |
| [BL-026](BL-026.md) | Boolean assembly | Inspect an opening created by subtraction while keeping operands editable. | implemented | expanded-qualification-pending |
| [BL-027](BL-027.md) | Retopology projection desk | Fit a sparse cage to an original curved target without confusing projection with good topology. | implemented | expanded-qualification-pending |
| [BL-029](BL-029.md) | Shape-key expression desk | Blend two original expressions and inspect the vertex motion rather than a rendered face alone. | implemented | expanded-qualification-pending |

## Materials and UV

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-002](BL-002.md) | Pixel Surface Studio | Separate original pixel detail from broad vertex shade and inspect both contributions. | implemented | expanded-qualification-pending |
| [BL-008](BL-008.md) | Vertex shade composition | Compare texture-only, authored shade and restrained light without mistaking them for the same mechanism. | implemented | expanded-qualification-pending |
| [BL-015](BL-015.md) | UV and texel audit | Find a stretched island or leaking atlas margin before it becomes a game-art defect. | implemented | expanded-qualification-pending |
| [BL-016](BL-016.md) | Bake and material bridge | Carry a chosen authored shade into a portable image and compare it with the editable source. | implemented | not-run |
| [BL-036](BL-036.md) | Material graph migration | Upgrade a known material contract while preserving unrelated user nodes. | implemented | not-run |
| [BL-059](BL-059.md) | Procedural material spectrum | Inspect scale and seed in an original procedural material before baking it into texture space. | implemented | not-run |
| [BL-060](BL-060.md) | Normal and displacement bridge | Compare a tangent-normal detail with actual displaced silhouette on the same original surface. | specified | not-run |
| [BL-061](BL-061.md) | Transparency sorting chamber | Compare opaque, cutout and blended original surfaces from viewpoints that reveal their limits. | specified | not-run |

## Geometry Nodes

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-003](BL-003.md) | Instance Conservatory | Change a row count and inspect the realized geometry that actually reaches the renderer. | implemented | expanded-qualification-pending |
| [BL-013](BL-013.md) | Geometry Nodes scatter | Scatter original modules with a seed you can replay and a density you can afford. | implemented | expanded-qualification-pending |
| [BL-014](BL-014.md) | Geometry Nodes field inspector | See why a field changes when it crosses point, edge and face domains. | implemented | expanded-qualification-pending |
| [BL-032](BL-032.md) | Geometry Nodes simulation loop | Persist a small state through frames and inspect what the simulation zone remembers. | specified | not-run |
| [BL-033](BL-033.md) | Geometry Nodes repeat machine | Iterate a bounded construction and inspect why repeat count changes the final geometry. | implemented | not-run |
| [BL-034](BL-034.md) | Geometry Nodes bake boundary | Freeze one procedural result and see which editable inputs are deliberately no longer live. | specified | not-run |
| [BL-035](BL-035.md) | Typed node-group interface | Expose a useful parameter contract that an agent can inspect without guessing socket indexes. | implemented | not-run |

## Animation

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-004](BL-004.md) | Motion Signal | Edit a travel beat and prove the object reaches its apex before returning. | implemented | expanded-qualification-pending |
| [BL-011](BL-011.md) | Action and NLA bench | Reuse two clips and inspect a transition rather than hiding motion in a baked movie. | implemented | expanded-qualification-pending |
| [BL-040](BL-040.md) | Animation bake interchange | Bake a constrained motion and compare sampled output before sending it elsewhere. | implemented | not-run |

## Simulation

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-005](BL-005.md) | Gravity Bench | Watch an authored release become a simulated contact result and inspect the body roles. | implemented | expanded-qualification-pending |
| [BL-017](BL-017.md) | Cloth and soft bodies | Distinguish a pinned cloth sheet from a goal-driven soft body using the same small frame budget. | specified | not-run |
| [BL-018](BL-018.md) | Fluid boundary desk | Bake a tiny fluid domain and inspect its boundary, disk cost and reset path. | specified | not-run |
| [BL-064](BL-064.md) | Rigid-body constraint machine | Build an original hinge and measure its limits while the connected bodies stay editable. | specified | not-run |
| [BL-065](BL-065.md) | Mesh cache playback desk | Replay an original geometry cache and distinguish evaluated motion from the editable source generator. | specified | not-run |
| [BL-066](BL-066.md) | Dynamic paint contact canvas | Trace contact as an original surface attribute and inspect which object painted it. | specified | not-run |
| [BL-067](BL-067.md) | Force-field particle boundary | Measure an original particle response to a field and disclose whether the installed legacy system exists. | specified | not-run |

## Interchange

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-006](BL-006.md) | Portable Artifact | Export one original mesh and learn precisely what a fresh glTF reimport proves. | implemented | expanded-qualification-pending |
| [BL-023](BL-023.md) | Godot receiving station | Confirm an original Blender export in a named Godot renderer instead of stopping at file creation. | specified | not-run |
| [BL-080](BL-080.md) | USD scene interchange | Carry a small original scene hierarchy through USD and report unsupported semantics precisely. | specified | not-run |
| [BL-081](BL-081.md) | Alembic geometry cache bridge | Export original evaluated motion as a cache and compare sampled geometry on reimport. | specified | not-run |
| [BL-082](BL-082.md) | FBX rig boundary desk | Compare an original small rig through FBX while keeping its axis/bake limitations visible. | specified | not-run |
| [BL-083](BL-083.md) | OBJ and STL geometry station | Choose between a surface interchange and a solid-print mesh using explicit geometry checks. | specified | not-run |
| [BL-084](BL-084.md) | Vector and Grease Pencil exchange | Move an original drawing between editable strokes and a declared vector export. | specified | not-run |
| [BL-086](BL-086.md) | Batch conversion contract matrix | Convert a small original fixture set and see per-format failures instead of one misleading batch success. | specified | not-run |

## Environment authoring

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-007](BL-007.md) | Modular environment kit | Build a corner, stair and doorway from one reusable original kit instead of a copied game room. | implemented | expanded-qualification-pending |
| [BL-009](BL-009.md) | Gradient-card atmosphere | Author a local recess shadow and shaft card, then reveal the camera angles where the illusion breaks. | implemented | expanded-qualification-pending |

## Rigging

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-010](BL-010.md) | Rig and deformation desk | Compare a rigid segmented limb with a weighted limb at the same bend. | implemented | expanded-qualification-pending |
| [BL-037](BL-037.md) | Drivers and constraint observatory | Explain a driven motion by inspecting its variables and constraint order. | implemented | not-run |
| [BL-038](BL-038.md) | Inverse-kinematics reach desk | Move an effector and measure which poses are reachable without hiding joint limits. | implemented | not-run |
| [BL-039](BL-039.md) | Pose asset library | Reuse a labeled original pose while preserving bone identity and blend meaning. | implemented | not-run |

## Camera and tracking

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-012](BL-012.md) | Camera and staging lab | Prove a detail reads at gameplay distance before spending geometry on its close-up. | implemented | expanded-qualification-pending |
| [BL-047](BL-047.md) | Camera solve reconstruction desk | Recover a generated camera motion and compare it with the known original camera. | specified | not-run |
| [BL-048](BL-048.md) | Lens distortion calibration | Separate lens distortion from camera motion using a generated reference grid. | specified | not-run |
| [BL-050](BL-050.md) | Planar sign replacement | Place an original sign onto a generated moving plane and measure corner alignment. | specified | not-run |

## Compositing

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-019](BL-019.md) | Compositor bench | Compare clean output with one deliberate display treatment without obscuring the mechanism. | implemented | expanded-qualification-pending |
| [BL-049](BL-049.md) | Rotoscope mask desk | Edit a mask that follows one original moving subject and inspect the matte edges. | specified | not-run |
| [BL-055](BL-055.md) | Render passes and AOV inspector | Inspect separate scene contributions and trace a final composite back to its pass inputs. | specified | not-run |

## Lighting and rendering

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-020](BL-020.md) | Lighting observatory | Compare world, area-light and material response while recording the rendering conditions. | implemented | expanded-qualification-pending |
| [BL-056](BL-056.md) | Light linking room | Make a light affect one original object group and prove an excluded object stays unchanged. | specified | not-run |
| [BL-057](BL-057.md) | Shadow catcher composition | Composite an original object onto an original plate and inspect the shadow contribution separately. | specified | not-run |
| [BL-058](BL-058.md) | World environment forge | Build an original environment map and distinguish background appearance from lighting energy. | implemented | not-run |
| [BL-068](BL-068.md) | Motion blur sampling chamber | Compare a sharp motion sample with shutter-integrated output and expose its sampling cost. | specified | not-run |

## Asset management

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-021](BL-021.md) | Asset-browser kit | Reuse an original part and see its provenance rather than searching unnamed files. | implemented | expanded-qualification-pending |
| [BL-074](BL-074.md) | Texture footprint and packing audit | Find an oversized or unresolved image dependency before distributing a scene. | specified | not-run |
| [BL-075](BL-075.md) | Linked library override desk | Change one permitted part of an original linked asset while keeping its library origin visible. | specified | not-run |
| [BL-076](BL-076.md) | Asset catalogs and provenance | Browse original assets by role and trace a selected result to its source/license metadata. | specified | not-run |

## Rendering deliverables

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-022](BL-022.md) | Sprite-sheet camera | Render a small original motion as an ordered transparent sprite atlas. | implemented | expanded-qualification-pending |

## Automation evidence

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-024](BL-024.md) | Source-to-preview receipt | Link a reviewed preview to the exact source operation that created it. | specified | not-run |
| [BL-094](BL-094.md) | Artifact provenance release desk | Inspect exactly which original source and dependency produced a distributable artifact. | specified | not-run |
| [BL-095](BL-095.md) | Version and surface qualification matrix | Know which Blender build and execution surface actually passed a capability contract. | specified | not-run |
| [BL-096](BL-096.md) | Offline project recovery route | Recreate an original editable deliverable from source and recover locally without a cloud account. | specified | not-run |

## Data and geometry

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-028](BL-028.md) | Mesh attribute contracts | Make a wrong attribute domain or data type fail before downstream nodes consume it. | implemented | expanded-qualification-pending |
| [BL-078](BL-078.md) | Units and transform conventions | Make a scale/axis mismatch visible before an original asset leaves Blender. | specified | not-run |
| [BL-085](BL-085.md) | Point-cloud intake contract | Inspect a neutral point dataset and reject wrong units or attribute schemas before conversion. | specified | not-run |

## Curves and text

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-030](BL-030.md) | Curve path and profile forge | Sweep an original profile along a path and inspect the editable curve that creates it. | implemented | expanded-qualification-pending |
| [BL-031](BL-031.md) | Typography geometry desk | Turn original station text into geometry without losing legibility or font provenance. | implemented | expanded-qualification-pending |

## Grease Pencil

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-041](BL-041.md) | Grease Pencil drawing desk | Inspect original strokes as editable 3D drawing data rather than an image overlay. | specified | not-run |
| [BL-042](BL-042.md) | Grease Pencil modifier grammar | See one drawing mechanism change stroke structure without flattening its source. | specified | not-run |
| [BL-043](BL-043.md) | Grease Pencil timing desk | Compare held and in-between drawings with an explicit frame timing contract. | specified | not-run |

## Sculpt and paint

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-044](BL-044.md) | Sculpt stroke laboratory | Inspect how one bounded sculpt stroke changes an original surface and respects its mask. | specified | not-run |
| [BL-045](BL-045.md) | Multires displacement ladder | Compare editable low-level form with high-level surface detail under a bounded memory budget. | specified | not-run |
| [BL-046](BL-046.md) | Texture paint boundary desk | Paint one original mark onto the intended UV image without touching another material. | specified | not-run |

## Video Sequence Editor

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-051](BL-051.md) | Sequence editing bench | Build a short original edit whose cuts and handles remain inspectable. | specified | not-run |
| [BL-052](BL-052.md) | Proxy and media cache desk | Measure a bounded proxy workflow and distinguish cache speed from altered source media. | specified | not-run |
| [BL-053](BL-053.md) | Audio synchronization ruler | Align a synthetic click with an original visual event and inspect the measured offset. | specified | not-run |
| [BL-054](BL-054.md) | Caption timing composition | Keep short original labels readable and timed to the actual demonstrated event. | specified | not-run |

## Volumes and hair

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-062](BL-062.md) | Volume grid inspection | Inspect an original small density grid and make its bounds, channels and cost explicit. | specified | not-run |
| [BL-063](BL-063.md) | Hair curves grooming desk | Inspect original guide curves and the interpolated result without pretending a small groom is final character hair. | specified | not-run |

## Automation runtime

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-069](BL-069.md) | Local worker queue | Run two independent original jobs without sharing mutable Blender process state. | specified | not-run |
| [BL-070](BL-070.md) | GPU capability qualification | Prove which render device actually works rather than trusting a configured GPU name. | specified | not-run |
| [BL-071](BL-071.md) | CPU render optimization bench | Measure a quality/time tradeoff on original output before choosing a heavier render. | specified | not-run |
| [BL-072](BL-072.md) | Dependency-graph profiler | Locate expensive evaluation in a scene using measured operations rather than polygon-count guesses. | specified | not-run |
| [BL-073](BL-073.md) | Instance memory scale ruler | Compare shared instances with realized geometry using the same original workload. | specified | not-run |

## Blender extensions

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-077](BL-077.md) | RNA and operator extension desk | Build a tiny native operation whose typed properties and failure behavior an agent can inspect. | specified | not-run |

## Scene organization

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-079](BL-079.md) | Collection and view-layer composition | Exclude one original scene group without deleting it and inspect the result per view layer. | specified | not-run |

## Automation surfaces

| ID | Capability | User payoff | Implementation | Qualification |
|---|---|---|---|---|
| [BL-087](BL-087.md) | Blender as a Python library | Build a neutral scene from a pinned bpy Python environment and disclose its platform limits. | specified | not-run |
| [BL-088](BL-088.md) | Background CLI execution contract | Make process exit, Blender logs and the final operation result agree. | specified | not-run |
| [BL-089](BL-089.md) | Live MCP context inspection | Let an agent inspect the real open Blender scene before requesting a mutation. | specified | not-run |
| [BL-090](BL-090.md) | Scoped MCP mutation rehearsal | Review a bounded live edit, verify its result and keep an escape path before saving. | specified | not-run |
| [BL-091](BL-091.md) | Authenticated Blender job service | Submit a versioned neutral task to isolated workers without exposing arbitrary Python execution. | specified | not-run |
| [BL-092](BL-092.md) | Checkpoint and resume studio | Resume a long original job from verified completed work instead of rerendering everything blindly. | specified | not-run |
| [BL-093](BL-093.md) | Cancellation and failure diagnostics | Stop a bounded job and retain enough honest evidence to understand where it ended. | specified | not-run |
