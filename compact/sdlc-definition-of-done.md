# sdlc-definition-of-done (compact)

When: Define and apply a Definition of Done that scales with Lean, Standard, or Enterprise-ready depth and risk, where every criterion names the evidence that proves it.

Goal: Replace subjective 'done' with a short checklist whose every line has a proof.

Steps:
1. Read `docs/references/depth-matrix.md` and pick the depth for this change from risk, blast radius, regulation, and reversibility.
2. Build the criteria set in three levels: task (tests green, diff reviewed, docs touched), story (acceptance scenarios pass…
3. Attach an evidence type to each criterion: command output, CI link, screenshot, trace id, review thread, or decision-log entry.
4. Add risk-triggered criteria: migrations need a rollback rehearsal, new dependencies need a license record, AI features need an…
5. At closure, walk the list; any unmet criterion is either completed, explicitly waived by a named owner with a reason, or turns…
6. Record waivers in `docs/governance/decision-log.md` and review waiver patterns each retrospective.

Never:
- A criterion without evidence is removed or fixed, not kept as decoration.
- Waivers need an owner and a reason; silent skipping is a process failure.
- Keep Lean to under ten lines; Enterprise-ready may be longer but still evidence-first.
- Do not weaken criteria mid-sprint to make a deadline.

Next: `sdlc-verification-before-completion` to produce the evidence, `sdlc-release-production-readiness` for release-level criteria.
