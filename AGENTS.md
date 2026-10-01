# Blender Lab contributor instructions

## Product and boundaries

Deliver inspectable, editable Blender experiences with original neutral examples. Public builds must work from this repository alone, without accounts, private configuration, external assets, or network calls. The public add-on must not contain an owner mode or private dependency.

Read `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/EXTENSION_CONTRACT.md`, and the relevant lab card before implementation. Keep stable lab IDs. A new capability needs a concrete action, exposed parameter, explanation, reset behavior, and truthful acceptance gate.

## Working safely

- Inspect Git status first and preserve unrelated work.
- Generate into owned lab scenes/collections. Never clear an arbitrary user scene or purge unrelated datablocks.
- Write generated outputs below the explicitly selected output directory. Do not silently overwrite an unrelated asset.
- Source lives in `blender_lab/`; host scripts live in `scripts/`; generated `.blend`, `.glb`, preview, evidence, and add-on ZIP files are ignored.
- Use neutral local fixture names and inspect artifact metadata before publishing.
- Keep documentation synchronized with actual CLI flags, panel labels, and acceptance behavior.

## Verification

Run Python structural checks and the headless Blender scenario suite relevant to the change. Tested baseline is Blender 5.2.2 LTS; do not claim other versions are verified from a minimum-version declaration. Record host, exact version, command, result, and limitations in `docs/BUILD_STATUS.md`. Keep raw machine evidence local.

Structural scene checks, evaluated geometry, rendered appearance, editor interaction, and receiving-engine acceptance are separate states. Do not mark a lab complete because a screenshot looks plausible. Do not add a broad catch or success-shaped fallback when an operation fails.

## Visual direction

Preserve the original Copper Observatory motif, deliberate silhouettes, small pixel-authored motifs, and restrained shade shapes. Study referenced techniques; do not copy characters, logos, environments, textures, or marketing images. Do not imitate all historical renderer artifacts at once. Blender's native editor controls remain readable and familiar.
