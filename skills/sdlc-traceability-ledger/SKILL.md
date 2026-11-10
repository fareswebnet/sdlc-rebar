---
name: sdlc-traceability-ledger
description: Maintain a machine-checkable chain from requirement id to BDD scenario, task, test, commit, release, and production metric, and verify it with scripts/sdlc_trace.py. Use when starting spec-driven work, before a review or release gate, or when coverage of requirements is unclear.
---

# SDLC Traceability Ledger

## Purpose

Make 'is every requirement built and proven?' a command you can run, not an opinion.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Assign stable ids to every requirement in `docs/product/`: `FR-###` functional, `NFR-###` quality, `SEC-###` security and privacy, `AI-###` model behavior. Never reuse or renumber an id.
2. Tag every BDD scenario with the ids it proves (`@FR-001`), and add the ids in parentheses to each task in `docs/engineering/tasks.md`.
3. Name or comment tests with the requirement id they verify so the script and reviewers can find them.
4. Run `python scripts/sdlc_trace.py --target <repo>`; fix every HIGH finding (uncovered requirement, unknown id, duplicate task id, malformed task) before the plan is approved.
5. Re-run at each gate: after planning, before review, before release. Use `--strict` at release to fail on done tasks without tests.
6. Extend the chain downstream: record the commit or PR, release version, feature flag, and the metric or SLO that shows the requirement works in production.
7. When the spec changes, update ids in place (retire, never delete) and re-run to expose orphaned tasks and tests.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: Tagged specs, scenarios, tasks, and tests; coverage matrix from `scripts/sdlc_trace.py`; entry in the review or release evidence.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Ids are contracts: renumbering silently breaks the whole chain.
- Coverage percent is a smoke alarm, not proof of quality; read the failing items.
- Setup and polish tasks may lack requirement refs; everything else must have one.
- Do not edit the script output to pass a gate; fix the artifacts instead.

## Handoff

`sdlc-cross-artifact-analysis` for semantic checks the script cannot do, `sdlc-release-production-readiness` for downstream links.

## Source Guidance

Original to this suite; informed by the Spec Kit analyze idea of coverage mapping, extended into an executable, id-based, end-to-end ledger. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
