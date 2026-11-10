---
name: sdlc-independent-verification
description: Act as an independent verifier whose job is to refute lines claimed as done: draw a reproducible sample, exercise each line through the public interface on the real server, try cross-tenant and wrong-role accounts, run mutations, and grant or refuse a visa. Use at every batch close, release gate, or whenever the author of a change must not be its only judge.
---

# SDLC Independent Verification

## Purpose

Make verification a separate role so a green gate cannot be produced by the same agent that wrote the work.

## Operating Depth

- **Lean**: produce one concise artifact or decision summary with explicit assumptions.
- **Standard**: produce the repo artifact, decisions, risks, owners, and validation path.
- **Enterprise-ready**: add traceability, evidence, auditability, sign-off points, and residual risk.

## Workflow

1. Independence: start in a fresh context with only the registry, the repo, and this skill; ideally a different model than the implementer. Do not read the implementer's reasoning or report first.
2. Draw the sample before reading anything else: `python scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed <n>`; all priority-1 lines plus a random share. Record the seed.
3. Start the real server and client with demo data; never a stub written by the implementer.
4. For each sampled line start from the legacy behavior, not from the provided proof: run it through the public interface with a correct-role account, a no-role account (expect 403), and an account from another tenant or scope (expect isolation).
5. Send each legacy form field to the target and require it to be returned or rejected with 400; a field silently ignored is a refusal. Check implicit constraints (uniqueness, reference existence, scoping).
6. Run mutations: break the essential rule of each multi-rule line in a copy outside the work tree and confirm at least one test fails; if all stay green the proof proves nothing.
7. Grant or refuse: `scripts/sdlc_registry.py visa` with your identifier, or `--refuse` with the finding. Priority-1 lines need two independent verifiers whose verdicts are made before they read each other.
8. Write the audit report: lines sampled, granted, refused, mutations tried, and gate result. If refusals exceed the project threshold, double the sample and reopen the batch.

## Expected Inputs

- User request, product context, repository state, or existing SDLC artifacts.
- Relevant files under `docs/`, tests, configs, architecture notes, and source code when working in a repo.
- Applicable preset from `presets/` when the domain changes the risk profile.

## Outputs

- Primary artifacts: `<batch>-audit.md`, registry visas and refusals, mutation log.
- Clear assumptions, open questions, risks, and owner recommendations.
- Links between product, behavior, architecture, code, tests, release, and production signals where applicable.

## Guardrails

- Verifier mission is to refute; a line you could not try is not granted.
- Never modify target code; observe and report, the implementer fixes.
- Never grant on a green test or documentation alone.
- Never accept a server or dataset simulated by the implementer.

## Handoff

`$sdlc-migration-batch-orchestration` to reopen or close the batch, `$sdlc-delivery-retrospective` for repeated refusal causes.

## Source Guidance

Original to this suite; informed by independent audit practice and mutation testing. Provenance is tracked in `docs/references/method-sources.md`.

Related references:

- `docs/references/depth-matrix.md`
- `docs/references/standards-map.md`
