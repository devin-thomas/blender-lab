# Product specification

## Promise

A user can build an original example in Blender, change a meaningful input, inspect the implementation, restore its baseline, and reproduce bounded evidence. The laboratory teaches through Blender's real editable data rather than a video-only explanation or a custom imitation editor.

## First release

Six labs form a complete small production chain: silhouette -> UV/material -> procedural repetition -> animation -> simulation -> interchange. They share one N-sidebar host, stable IDs, original fixtures, a CLI runner, optional capture, and a documented extension contract. The runtime baseline is Blender 5.2.2 LTS; compatibility beyond the tested host remains explicit.

## Required behavior

| Requirement | Acceptance |
|---|---|
| Account-free start | Install and generate from a public-only checkout offline after Blender/Python installation |
| Editable mechanism | Generated objects, modifiers, nodes, keyframes, and material data remain inspectable |
| Visible parameter | Changing the lab input produces a corresponding scene/data change |
| Scoped reset | Reset replaces only the generated lab's owned data |
| Honest evidence | Every receipt states what was asserted and which gates remain |
| Repeatable source | A clean checkout can recreate scenes and package the add-on |
| Original fixtures | No copied game assets, personal files, or unavailable downloads |
| Interchange proof | Export file is reimported and compared for the bounded geometry contract |

## Completion states

`specified` means documented; `implemented` means source exists; `automated` means declared assertions passed on the recorded host; `editor-verified` means the actual panel and interaction journey were exercised; `artist-reviewed` means the editable workflow and appearance received human review; `engine-verified` means an exported asset was checked in a named receiving engine. These states are cumulative only when their own evidence is present.

No state implies production certification. In particular a glTF roundtrip in Blender does not prove Godot import settings, material fidelity, collider behavior, or game performance.

## Out of scope for this slice

Full game production, production character art, a replacement for an artist, online services, cloud rendering, an asset marketplace, and every Blender subsystem are expansion opportunities. The workshop remains useful before those additions. Preserve original project ownership and license review when introducing external material.
