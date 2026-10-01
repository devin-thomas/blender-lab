# Add a lab

## Required card

Give every experiment a stable ID, user payoff, mechanism, editable input, original fixture, reset rule, automated scenario, visual/editor acceptance, limitation, and source confidence. Start as `specified`; implementation and evidence advance independently.

## Implementation rules

Build inside owned scenes/collections, expose a meaningful native parameter, and preserve useful Blender data instead of flattening everything prematurely. Provide a reasonable default and a second scenario demonstrating the parameter's effect. Resetting must not delete unrelated data. Fail visibly and return nonzero/error status when a prerequisite is absent.

Keep core generation local. Optional external integrations require an adapter, explicit invocation, documented unavailable behavior, and independent acceptance. A recording tool is not a runtime dependency. Promote reusable mechanisms with neutral fixtures and rights-reviewed assets.

## Contribution acceptance

Update the catalog, card, sidebar/CLI wiring, relevant tests, source index, and evidence ledger together. Verify source packaging from a clean public-only checkout. Record the tested Blender version. For export-dependent features, define which properties survive and verify them in the receiving tool before claiming interchange success.
