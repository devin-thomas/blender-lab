# Implementation and qualification queue

Generated from [the authoritative spec](../specs/experiments.json). 16 core tickets plus 192 lab tickets. A implements the inspectable capability; B proves bounded outcomes and recovery. The lab/core dependency graph is checked for unknown nodes and cycles by the generator.

## Core

| ID | Contract | State |
|---|---|---|
| [CORE-001](CORE-001.md) | Catalog host and capability navigation | partial |
| [CORE-002](CORE-002.md) | Authoritative specification and drift validation | implemented |
| [CORE-003](CORE-003.md) | Typed operation and control contracts | partial |
| [CORE-004](CORE-004.md) | Output staging and deliberate promotion | partial |
| [CORE-005](CORE-005.md) | Scene and datablock ownership lifecycle | partial |
| [CORE-006](CORE-006.md) | Operation receipts and artifact identity | partial |
| [CORE-007](CORE-007.md) | Runtime and execution-profile inventory | specified |
| [CORE-008](CORE-008.md) | Isolated job runner and queue | specified |
| [CORE-009](CORE-009.md) | Budgets cancellation and diagnostics | specified |
| [CORE-010](CORE-010.md) | Checkpoint cache and resume contract | specified |
| [CORE-011](CORE-011.md) | Remote execution and artifact handoff | specified |
| [CORE-012](CORE-012.md) | Performance and quality measurement | specified |
| [CORE-013](CORE-013.md) | Live MCP discovery and context boundary | specified |
| [CORE-014](CORE-014.md) | Scoped agent mutation and recovery | specified |
| [CORE-015](CORE-015.md) | Trust local-only and public boundary | partial |
| [CORE-016](CORE-016.md) | Qualification matrix and release controller | partial |

## Labs

| Capability | Implement | Qualify | Milestone |
|---|---|---|---|
| BL-001 Silhouette Foundry | [implemented](BL-001-A.md) | [expanded-qualification-pending](BL-001-B.md) | M0 |
| BL-002 Pixel Surface Studio | [implemented](BL-002-A.md) | [expanded-qualification-pending](BL-002-B.md) | M0 |
| BL-003 Instance Conservatory | [implemented](BL-003-A.md) | [expanded-qualification-pending](BL-003-B.md) | M0 |
| BL-004 Motion Signal | [implemented](BL-004-A.md) | [expanded-qualification-pending](BL-004-B.md) | M0 |
| BL-005 Gravity Bench | [implemented](BL-005-A.md) | [expanded-qualification-pending](BL-005-B.md) | M0 |
| BL-006 Portable Artifact | [implemented](BL-006-A.md) | [expanded-qualification-pending](BL-006-B.md) | M0 |
| BL-007 Modular environment kit | [implemented](BL-007-A.md) | [expanded-qualification-pending](BL-007-B.md) | M1 |
| BL-008 Vertex shade composition | [implemented](BL-008-A.md) | [expanded-qualification-pending](BL-008-B.md) | M1 |
| BL-009 Gradient-card atmosphere | [implemented](BL-009-A.md) | [expanded-qualification-pending](BL-009-B.md) | M1 |
| BL-010 Rig and deformation desk | [implemented](BL-010-A.md) | [qualification-pending](BL-010-B.md) | M1 |
| BL-011 Action and NLA bench | [implemented](BL-011-A.md) | [qualification-pending](BL-011-B.md) | M1 |
| BL-012 Camera and staging lab | [implemented](BL-012-A.md) | [qualification-pending](BL-012-B.md) | M1 |
| BL-013 Geometry Nodes scatter | [implemented](BL-013-A.md) | [qualification-pending](BL-013-B.md) | M1 |
| BL-014 Geometry Nodes field inspector | [implemented](BL-014-A.md) | [qualification-pending](BL-014-B.md) | M1 |
| BL-015 UV and texel audit | [implemented](BL-015-A.md) | [qualification-pending](BL-015-B.md) | M1 |
| BL-016 Bake and material bridge | [specified](BL-016-A.md) | [not-run](BL-016-B.md) | M1 |
| BL-017 Cloth and soft bodies | [specified](BL-017-A.md) | [not-run](BL-017-B.md) | M1 |
| BL-018 Fluid boundary desk | [specified](BL-018-A.md) | [not-run](BL-018-B.md) | M1 |
| BL-019 Compositor bench | [implemented](BL-019-A.md) | [qualification-pending](BL-019-B.md) | M1 |
| BL-020 Lighting observatory | [implemented](BL-020-A.md) | [qualification-pending](BL-020-B.md) | M1 |
| BL-021 Asset-browser kit | [implemented](BL-021-A.md) | [qualification-pending](BL-021-B.md) | M1 |
| BL-022 Sprite-sheet camera | [implemented](BL-022-A.md) | [qualification-pending](BL-022-B.md) | M1 |
| BL-023 Godot receiving station | [specified](BL-023-A.md) | [not-run](BL-023-B.md) | M1 |
| BL-024 Source-to-preview receipt | [specified](BL-024-A.md) | [not-run](BL-024-B.md) | M1 |
| BL-025 Topology surgery | [implemented](BL-025-A.md) | [qualification-pending](BL-025-B.md) | M2 |
| BL-026 Boolean assembly | [implemented](BL-026-A.md) | [qualification-pending](BL-026-B.md) | M2 |
| BL-027 Retopology projection desk | [implemented](BL-027-A.md) | [qualification-pending](BL-027-B.md) | M2 |
| BL-028 Mesh attribute contracts | [implemented](BL-028-A.md) | [qualification-pending](BL-028-B.md) | M2 |
| BL-029 Shape-key expression desk | [implemented](BL-029-A.md) | [qualification-pending](BL-029-B.md) | M2 |
| BL-030 Curve path and profile forge | [implemented](BL-030-A.md) | [qualification-pending](BL-030-B.md) | M2 |
| BL-031 Typography geometry desk | [implemented](BL-031-A.md) | [qualification-pending](BL-031-B.md) | M2 |
| BL-032 Geometry Nodes simulation loop | [specified](BL-032-A.md) | [not-run](BL-032-B.md) | M2 |
| BL-033 Geometry Nodes repeat machine | [specified](BL-033-A.md) | [not-run](BL-033-B.md) | M2 |
| BL-034 Geometry Nodes bake boundary | [specified](BL-034-A.md) | [not-run](BL-034-B.md) | M2 |
| BL-035 Typed node-group interface | [specified](BL-035-A.md) | [not-run](BL-035-B.md) | M2 |
| BL-036 Material graph migration | [specified](BL-036-A.md) | [not-run](BL-036-B.md) | M2 |
| BL-037 Drivers and constraint observatory | [specified](BL-037-A.md) | [not-run](BL-037-B.md) | M3 |
| BL-038 Inverse-kinematics reach desk | [specified](BL-038-A.md) | [not-run](BL-038-B.md) | M3 |
| BL-039 Pose asset library | [specified](BL-039-A.md) | [not-run](BL-039-B.md) | M3 |
| BL-040 Animation bake interchange | [specified](BL-040-A.md) | [not-run](BL-040-B.md) | M3 |
| BL-041 Grease Pencil drawing desk | [specified](BL-041-A.md) | [not-run](BL-041-B.md) | M3 |
| BL-042 Grease Pencil modifier grammar | [specified](BL-042-A.md) | [not-run](BL-042-B.md) | M3 |
| BL-043 Grease Pencil timing desk | [specified](BL-043-A.md) | [not-run](BL-043-B.md) | M3 |
| BL-044 Sculpt stroke laboratory | [specified](BL-044-A.md) | [not-run](BL-044-B.md) | M3 |
| BL-045 Multires displacement ladder | [specified](BL-045-A.md) | [not-run](BL-045-B.md) | M3 |
| BL-046 Texture paint boundary desk | [specified](BL-046-A.md) | [not-run](BL-046-B.md) | M3 |
| BL-047 Camera solve reconstruction desk | [specified](BL-047-A.md) | [not-run](BL-047-B.md) | M3 |
| BL-048 Lens distortion calibration | [specified](BL-048-A.md) | [not-run](BL-048-B.md) | M3 |
| BL-049 Rotoscope mask desk | [specified](BL-049-A.md) | [not-run](BL-049-B.md) | M3 |
| BL-050 Planar sign replacement | [specified](BL-050-A.md) | [not-run](BL-050-B.md) | M3 |
| BL-051 Sequence editing bench | [specified](BL-051-A.md) | [not-run](BL-051-B.md) | M4 |
| BL-052 Proxy and media cache desk | [specified](BL-052-A.md) | [not-run](BL-052-B.md) | M4 |
| BL-053 Audio synchronization ruler | [specified](BL-053-A.md) | [not-run](BL-053-B.md) | M4 |
| BL-054 Caption timing composition | [specified](BL-054-A.md) | [not-run](BL-054-B.md) | M4 |
| BL-055 Render passes and AOV inspector | [specified](BL-055-A.md) | [not-run](BL-055-B.md) | M4 |
| BL-056 Light linking room | [specified](BL-056-A.md) | [not-run](BL-056-B.md) | M4 |
| BL-057 Shadow catcher composition | [specified](BL-057-A.md) | [not-run](BL-057-B.md) | M4 |
| BL-058 World environment forge | [specified](BL-058-A.md) | [not-run](BL-058-B.md) | M4 |
| BL-059 Procedural material spectrum | [specified](BL-059-A.md) | [not-run](BL-059-B.md) | M4 |
| BL-060 Normal and displacement bridge | [specified](BL-060-A.md) | [not-run](BL-060-B.md) | M4 |
| BL-061 Transparency sorting chamber | [specified](BL-061-A.md) | [not-run](BL-061-B.md) | M4 |
| BL-062 Volume grid inspection | [specified](BL-062-A.md) | [not-run](BL-062-B.md) | M4 |
| BL-063 Hair curves grooming desk | [specified](BL-063-A.md) | [not-run](BL-063-B.md) | M4 |
| BL-064 Rigid-body constraint machine | [specified](BL-064-A.md) | [not-run](BL-064-B.md) | M4 |
| BL-065 Mesh cache playback desk | [specified](BL-065-A.md) | [not-run](BL-065-B.md) | M4 |
| BL-066 Dynamic paint contact canvas | [specified](BL-066-A.md) | [not-run](BL-066-B.md) | M4 |
| BL-067 Force-field particle boundary | [specified](BL-067-A.md) | [not-run](BL-067-B.md) | M4 |
| BL-068 Motion blur sampling chamber | [specified](BL-068-A.md) | [not-run](BL-068-B.md) | M4 |
| BL-069 Local worker queue | [specified](BL-069-A.md) | [not-run](BL-069-B.md) | M5 |
| BL-070 GPU capability qualification | [specified](BL-070-A.md) | [not-run](BL-070-B.md) | M5 |
| BL-071 CPU render optimization bench | [specified](BL-071-A.md) | [not-run](BL-071-B.md) | M5 |
| BL-072 Dependency-graph profiler | [specified](BL-072-A.md) | [not-run](BL-072-B.md) | M5 |
| BL-073 Instance memory scale ruler | [specified](BL-073-A.md) | [not-run](BL-073-B.md) | M5 |
| BL-074 Texture footprint and packing audit | [specified](BL-074-A.md) | [not-run](BL-074-B.md) | M5 |
| BL-075 Linked library override desk | [specified](BL-075-A.md) | [not-run](BL-075-B.md) | M5 |
| BL-076 Asset catalogs and provenance | [specified](BL-076-A.md) | [not-run](BL-076-B.md) | M5 |
| BL-077 RNA and operator extension desk | [specified](BL-077-A.md) | [not-run](BL-077-B.md) | M5 |
| BL-078 Units and transform conventions | [specified](BL-078-A.md) | [not-run](BL-078-B.md) | M5 |
| BL-079 Collection and view-layer composition | [specified](BL-079-A.md) | [not-run](BL-079-B.md) | M5 |
| BL-080 USD scene interchange | [specified](BL-080-A.md) | [not-run](BL-080-B.md) | M5 |
| BL-081 Alembic geometry cache bridge | [specified](BL-081-A.md) | [not-run](BL-081-B.md) | M5 |
| BL-082 FBX rig boundary desk | [specified](BL-082-A.md) | [not-run](BL-082-B.md) | M5 |
| BL-083 OBJ and STL geometry station | [specified](BL-083-A.md) | [not-run](BL-083-B.md) | M5 |
| BL-084 Vector and Grease Pencil exchange | [specified](BL-084-A.md) | [not-run](BL-084-B.md) | M5 |
| BL-085 Point-cloud intake contract | [specified](BL-085-A.md) | [not-run](BL-085-B.md) | M5 |
| BL-086 Batch conversion contract matrix | [specified](BL-086-A.md) | [not-run](BL-086-B.md) | M5 |
| BL-087 Blender as a Python library | [specified](BL-087-A.md) | [not-run](BL-087-B.md) | M6 |
| BL-088 Background CLI execution contract | [specified](BL-088-A.md) | [not-run](BL-088-B.md) | M6 |
| BL-089 Live MCP context inspection | [specified](BL-089-A.md) | [not-run](BL-089-B.md) | M6 |
| BL-090 Scoped MCP mutation rehearsal | [specified](BL-090-A.md) | [not-run](BL-090-B.md) | M6 |
| BL-091 Authenticated Blender job service | [specified](BL-091-A.md) | [not-run](BL-091-B.md) | M6 |
| BL-092 Checkpoint and resume studio | [specified](BL-092-A.md) | [not-run](BL-092-B.md) | M6 |
| BL-093 Cancellation and failure diagnostics | [specified](BL-093-A.md) | [not-run](BL-093-B.md) | M6 |
| BL-094 Artifact provenance release desk | [specified](BL-094-A.md) | [not-run](BL-094-B.md) | M6 |
| BL-095 Version and surface qualification matrix | [specified](BL-095-A.md) | [not-run](BL-095-B.md) | M6 |
| BL-096 Offline project recovery route | [specified](BL-096-A.md) | [not-run](BL-096-B.md) | M6 |
