# Handoff

Continue in `brainboxemb/template.cad.library` until issue #23 is qualified and promoted.

The template is being realigned with `template.cad.model-project`:

- root is `models/`, not `examples/`;
- one physical model directory is one selection/publication owner;
- `model.yml.purpose` accepts `example`, `verification`, or both;
- multiple CAD engines are `implementations` inside that owner;
- `build.yml` selects `models`;
- durable output is grouped below `build/<scope>/models/<owner>/`.

After #23, rebase website issue #12 on this contract. Only then resume bootstrap/migration in `brainboxemb/lib.py.solidcraft.forge.NEW`. The old Forge repository remains unchanged and authoritative for A/B comparison during migration.
