# Capture and motion evidence

The optional adapter uses the released **@uppercut-labs/cappy 0.1.0** NPM package. Read [capture/README](../capture/README.md) for setup, commands, protocol boundaries and acceptance. The unrelated unscoped `cappy` package must not be used.

Thirty-six scenarios share the CLI operation/build/verification path with the native sidebar. Cappy recording stores lab ID and numeric input; replay launches Blender and repeats verification. Planned atlas entries are not recipes. This is recipe replay, not arbitrary editing or deterministic cross-version physics. Outputs stay in ignored `build/cappy/` and `capture/.cappy/`.

The delivered adapter launches background Blender. OBS capture is not implemented or verified by this adapter. A future visible-window adapter must wait for readiness, animate the authored presentation, emit events during playback, and preserve the same scenario outcome checks. Recording additionally requires a user-confirmed OBS scene, a visible desktop window, and a verified master/derivative manifest. Never count headless replay, a native Blender render, or a fake OBS fixture as OBS capture.

## Native rendered motion

Blender can independently render the two timeline labs without capture software. These commands produce bounded PNG sequences with an evidence JSON:

```sh
blender --background --factory-startup --python-exit-code 1 --python scripts/render_motion.py -- --lab BL-004 --output /your/scratch/motion-004
blender --background --factory-startup --python-exit-code 1 --python scripts/render_motion.py -- --lab BL-005 --output /your/scratch/motion-005
ffmpeg -framerate 24 -i /your/scratch/motion-004/frame-%04d.png -c:v libx264 -pix_fmt yuv420p /your/scratch/motion-004.mp4
```

BL-004 renders 60 frames; BL-005 renders 90. Both use 640x480, 8 Cycles samples and original fixtures. Keep scratch on a sufficiently spacious volume. Inspect moving output as well as numerical checks before approving presentation. No audio or spoken content is generated, so transcription adds no useful evidence here.
