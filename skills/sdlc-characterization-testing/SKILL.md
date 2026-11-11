---
name: sdlc-characterization-testing
description: Pin down legacy behavior with characterization tests and golden masters, with numeric tolerances, to prove a migrated system equivalent. Use before replacing untested behavior or when migrated numbers differ from the old system.
---

# SDLC Characterization Testing

## Purpose

Prove equivalence by executing both sides on the same inputs, not by reading code.

## Workflow

1. Choose the oracle: the real legacy system where it can run, otherwise recorded outputs from it; a reimplementation written by the same team is never an oracle.
2. Design input sets by risk class: R1 gets exhaustive boundaries, random reproducible fuzz with a recorded seed, and real-shape data; R2 gets scenario coverage; R3 gets sample and visual checks.
3. Fix the comparison contract: exact equality for identifiers and money after the contractual rounding, separate justified tolerances for rates and solvers, and units and precision written down.
4. Capture golden masters with provenance (source system version, date, input seed) and store them with the tests.
5. Run the same inputs through the target's public interface, not its internals, and diff outputs; investigate every difference as legacy defect, target defect, or oracle error.
6. Check the comparison is not vacuous: series are non-empty, no mask hides a gap, and a deliberately broken rule makes the suite fail (mutation check).
7. Test events and data flows where relevant: duplicates, reordering, replay, schema compatibility, and atomicity between data and outbox.

## Outputs

- Primary artifacts: Characterization suite, golden-master datasets with provenance, differential-run report, mutation-check evidence.

## Guardrails

- Never certify a line with a test that only passes against code written by the same agent.
- Do not widen a tolerance to make a diff pass; justify it or fix the code.
- Synthetic data needs provenance and limits stated; do not present it as historical truth.
- Dependencies that cannot run in the test environment are written down as unproven, not skipped silently.

## Handoff

`sdlc-independent-verification` for the visa, `sdlc-test-driven-development` for new behavior.

## Provenance

Original to this suite; informed by golden master, characterization, and differential testing practice. Provenance is tracked in `docs/references/method-sources.md`.
