---
name: sdlc-reachability-anti-simulation
description: Make three defects blocking through scripts and a ratchet: controller or handler methods that no route reaches, API client methods that fabricate data instead of calling the server, and documentation that cites files or classes that do not exist. Use at every batch close, before every validation, and in CI for any generated or agent-written code.
---

# SDLC Reachability And Anti-Simulation

## Purpose

Stop delivery of code that exists but cannot be reached, calls nothing, or is documented but absent.

## Workflow

1. Reachability: list every public method of application controllers or handlers and require it to be routed or annotated as intentionally not exposed with a real reason.
2. Anti-simulation: list every public method of API clients and require it to perform a real network call, or carry an explicit local-only marker with a reason, reserved for deliberate local computation such as an offline engine or format validation.
3. Links: check that every file or class cited in docs, specs, and feature matrices exists.
4. Freeze pre-existing violations in a baseline and run `python scripts/sdlc_registry.py ratchet <baseline> <current>`; a new violation fails and a resolved one must be removed from the baseline.
5. Never regenerate the baseline to pass a new violation; fix the cause: add the route, contract and test, replace the fake with a real call, correct the reference.
6. Test the detectors themselves with a fixture containing known positives and negatives, and write their conventions in their error messages and in project config, not in agent memory.
7. Remember the limit: reachable is not conformant. A reachable route that ignores legacy form fields remains a refusal under `sdlc-independent-verification`.

## Outputs

- Primary artifacts: Detector commands, baseline files, ratchet CI step, fixture tests.

## Guardrails

- Annotations that suppress a finding need a true reason; blanket suppression is a violation.
- A baseline that grows is a failed gate.
- Local-only markers never apply to business data.
- A green detector does not prove there are no other controllers or clients outside its scan.

## Handoff

`sdlc-independent-verification` for behavior, `sdlc-quality-test-strategy` for broader gates.

## Provenance

Original to this suite; informed by ratchet-based quality gates. Provenance is tracked in `docs/references/method-sources.md`.
