# Start here

## First journey

Install the locally packaged add-on and open its **Blender Lab** tab in the 3D Viewport sidebar. Begin with BL-001. Build the scene, orbit the object, and inspect its modifier stack. Change Experiment value and click Apply experiment value. The useful question is: which visible edge changed, and which modifier caused it?

Continue to BL-002 to inspect a pixel atlas and color attribute, then BL-003 to inspect a node graph. BL-004 and BL-005 add time: scrub keyframes deliberately, and evaluate physics forward from the initial frame. BL-006 closes the loop by exporting and reimporting an artifact.

Continue to BL-007 for a modular doorway/wall/stair kit, BL-008 for identical geometry under three shade models and BL-009 for editable atmosphere cards. Search/filter/page the full 96-entry atlas to find a domain. Planned cards display their status and fallback; only implemented adapters offer Open. Follow [milestones](MILESTONES.md) and [tickets](../tickets/README.md) to see what enables each future capability.

Save a separate copy before freeform edits. Open experiment creates a new scene. Apply experiment value changes the active lab. Reset this lab asks for confirmation and restores that active lab's scripted baseline, discarding its edits while preserving other scenes. Working artists can preserve a variation in their own file before reset.

## Source workflow

Use a local Python interpreter for orchestration and pass the Blender executable explicitly:

```powershell
python scripts/run.py --blender "C:\path\to\blender.exe" build
python scripts/run.py --blender "C:\path\to\blender.exe" test
python scripts/run.py --blender "C:\path\to\blender.exe" render
python scripts/run.py --blender "C:\path\to\blender.exe" export
python scripts/package.py
```

Use `python scripts/run.py --help` for current output and selection options. Packaging writes `dist/blender-lab-0.1.0.zip`. Outputs default to local `build/`. Heavy rendering should run on a suitably provisioned host; orchestration and source checks can run on a lightweight workstation.

## Troubleshooting

If the tab is absent, confirm the add-on is enabled and the active editor is the 3D Viewport. Read Blender's reported error when installation or generation fails. If an imported model differs, inspect materials, UVs, color attributes, transforms, and normals before assuming a renderer defect. A passed automated check is scoped to its assertions; [BUILD_STATUS](BUILD_STATUS.md) records remaining gates.
