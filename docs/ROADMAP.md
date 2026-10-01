# Living Blender roadmap

The authoritative [specification](../specs/experiments.json) defines 96 substantive capability contracts, 16 core delivery tickets and two tickets per lab. [Catalog](experiments/INDEX.md), [matrix](CAPABILITY_MATRIX.md), and [milestones](MILESTONES.md) expose the scope and actual states. The six original labs remain the verified foundation; expansion is explicitly staged.

## Production routes

### An original room reaches a game engine

Create form, quiet surface detail and authored atmosphere before verifying a named game-engine import.

[BL-007](experiments/BL-007.md) -> [BL-008](experiments/BL-008.md) -> [BL-009](experiments/BL-009.md) -> [BL-015](experiments/BL-015.md) -> [BL-006](experiments/BL-006.md) -> [BL-023](experiments/BL-023.md)

Artist review and receiver material/UV/color/scale checks are explicit; Blender-only roundtrip is not the receiver pass.

### A motion mechanism becomes an editable deliverable

Keep rig, constraint and timing source editable while testing a portable sampled result.

[BL-010](experiments/BL-010.md) -> [BL-037](experiments/BL-037.md) -> [BL-038](experiments/BL-038.md) -> [BL-011](experiments/BL-011.md) -> [BL-040](experiments/BL-040.md) -> [BL-082](experiments/BL-082.md)

Sampling, bone identity and axis conventions must be checked in the chosen qualified format/receiver.

### A short original visual supports a story

Start with useful motion and framing, then create an inspectable edit, audio timing and captions.

[BL-012](experiments/BL-012.md) -> [BL-004](experiments/BL-004.md) -> [BL-022](experiments/BL-022.md) -> [BL-051](experiments/BL-051.md) -> [BL-053](experiments/BL-053.md) -> [BL-054](experiments/BL-054.md)

Timing/probe/visual checks precede human editorial acceptance; no personal content is automatically ingested.

### Geometry state stays inspectable

Use typed attributes and interfaces to make procedural repeat/simulation/bake behavior testable.

[BL-028](experiments/BL-028.md) -> [BL-035](experiments/BL-035.md) -> [BL-014](experiments/BL-014.md) -> [BL-033](experiments/BL-033.md) -> [BL-032](experiments/BL-032.md) -> [BL-034](experiments/BL-034.md)

Validate domains, zone pairing, evaluated samples, budget and cache identity on the actual Blender build.

### A captured plate becomes a measured reconstruction

Use generated known-truth footage to qualify camera/lens/mask/planar mechanisms before real media.

[BL-047](experiments/BL-047.md) -> [BL-048](experiments/BL-048.md) -> [BL-049](experiments/BL-049.md) -> [BL-050](experiments/BL-050.md) -> [BL-057](experiments/BL-057.md)

Synthetic solve/composite qualification does not establish arbitrary real-footage quality.

### An agent operation leaves recoverable proof

Inspect source/context, submit a bounded job, preserve checkpoints, and publish only reviewed identity-linked artifacts.

[BL-088](experiments/BL-088.md) -> [BL-089](experiments/BL-089.md) -> [BL-090](experiments/BL-090.md) -> [BL-069](experiments/BL-069.md) -> [BL-092](experiments/BL-092.md) -> [BL-093](experiments/BL-093.md) -> [BL-094](experiments/BL-094.md) -> [BL-095](experiments/BL-095.md) -> [BL-096](experiments/BL-096.md)

MCP/service/remote execution are opt-in qualified surfaces; local no-cloud source rebuilding remains the baseline.

## Foundation work

Core delivery is a real work stream rather than invisible glue:

| Ticket | Contract | State |
|---|---|---|
| [CORE-001](../tickets/CORE-001.md) | Catalog host and capability navigation | partial |
| [CORE-002](../tickets/CORE-002.md) | Authoritative specification and drift validation | implemented |
| [CORE-003](../tickets/CORE-003.md) | Typed operation and control contracts | partial |
| [CORE-004](../tickets/CORE-004.md) | Output staging and deliberate promotion | partial |
| [CORE-005](../tickets/CORE-005.md) | Scene and datablock ownership lifecycle | partial |
| [CORE-006](../tickets/CORE-006.md) | Operation receipts and artifact identity | partial |
| [CORE-007](../tickets/CORE-007.md) | Runtime and execution-profile inventory | specified |
| [CORE-008](../tickets/CORE-008.md) | Isolated job runner and queue | specified |
| [CORE-009](../tickets/CORE-009.md) | Budgets cancellation and diagnostics | specified |
| [CORE-010](../tickets/CORE-010.md) | Checkpoint cache and resume contract | specified |
| [CORE-011](../tickets/CORE-011.md) | Remote execution and artifact handoff | specified |
| [CORE-012](../tickets/CORE-012.md) | Performance and quality measurement | specified |
| [CORE-013](../tickets/CORE-013.md) | Live MCP discovery and context boundary | specified |
| [CORE-014](../tickets/CORE-014.md) | Scoped agent mutation and recovery | specified |
| [CORE-015](../tickets/CORE-015.md) | Trust local-only and public boundary | partial |
| [CORE-016](../tickets/CORE-016.md) | Qualification matrix and release controller | partial |

## Sequencing and evidence

Follow the acyclic lab/core dependencies in the source. Qualification never advances merely because an API member exists or an A ticket is merged. Start with small original fixtures and cheap previews; use explicit profiles for expensive simulations, disk-heavy caches, GPU qualification and external tools. Every unimplemented catalog entry explains its missing mechanism and next gate. The local no-cloud route stays useful throughout expansion.

## Change policy

Edit the specification, run `python scripts/generate_catalog.py`, then `python scripts/generate_catalog.py --check`. Regeneration preserves stable IDs and statuses. Add outcome/recovery receipts before changing evidence states. Keep private plans, raw personal media and private dependencies outside the public source and package.
