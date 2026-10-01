# Decisions

## ADR-001 - Native editable host

**Accepted:** use an installable Blender add-on with an N-sidebar host. The actual mesh/modifier/node/timeline data remains editable. This puts the mechanism next to the result and preserves Blender's native controls. The scripted background path complements the editor journey and cannot substitute for it.

## ADR-002 - Source-first distribution

**Accepted:** Git carries source, original procedural fixtures, and sanitized evidence summaries. Generated `.blend`, previews, glTF, logs, recordings, and packaged ZIPs stay local and ignored. Builders recreate outputs with versioned scripts. A later release may publish reviewed generated artifacts separately with their own provenance.

## ADR-003 - Narrow first pipeline

**Accepted:** ship six focused labs before expanding into every Blender subsystem. The first chain covers form, surface, repetition, motion, simulation, and interchange. Each future lab needs a real editable action and independent gate instead of a catalog-only claim.

## ADR-004 - Version-specific qualification

**Accepted:** test Blender 5.2.2 LTS/build d13f752e3b9c and declare 5.2 minimum. Do not infer compatibility from an API that appears familiar. Version changes can affect node sockets, shader behavior, animation representation, physics, and glTF export; qualify a second release with actual execution.

## ADR-005 - Original visual research translation

**Accepted:** translate texture-first, sparse-silhouette, broad-shade principles into original fixtures. Preserve research confidence labels and keep optional historical effects separate from the clean baseline. The lab does not redistribute research videos or another game's art.

## ADR-006 - Explicit interchange boundary

**Accepted:** glTF verification has a declared mesh contract and fresh reimport. Editable Blender node graphs, arbitrary shaders, modifiers, and physics are authoring mechanisms rather than portable interchange guarantees. Receiving-engine acceptance is a later named/versioned gate.
