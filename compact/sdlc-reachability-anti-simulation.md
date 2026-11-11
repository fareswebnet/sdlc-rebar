# sdlc-reachability-anti-simulation (compact)

When: Block three defects via scripts and a ratchet: unrouted handlers, API client methods faking data, docs citing missing files.

Goal: Stop delivery of code that exists but cannot be reached, calls nothing, or is documented but absent.

Steps:
1. Reachability: list every public method of application controllers or handlers and require it to be routed or annotated as…
2. Anti-simulation: list every public method of API clients and require it to perform a real network call, or carry an explicit…
3. Links: check that every file or class cited in docs, specs, and feature matrices exists.
4. Freeze pre-existing violations in a baseline and run `python scripts/sdlc_registry.py ratchet <baseline> <current>`; a new…
5. Never regenerate the baseline to pass a new violation; fix the cause: add the route, contract and test, replace the fake with a…
6. Test the detectors themselves with a fixture containing known positives and negatives, and write their conventions in their error…
7. Remember the limit: reachable is not conformant.

Never:
- Annotations that suppress a finding need a true reason; blanket suppression is a violation.
- A baseline that grows is a failed gate.
- Local-only markers never apply to business data.
- A green detector does not prove there are no other controllers or clients outside its scan.

Next: `sdlc-independent-verification` for behavior, `sdlc-test-strategy` for broader gates.
