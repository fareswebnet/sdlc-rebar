# sdlc-traceability-ledger (compact)

When: Maintain a machine-checkable chain from requirement id to BDD scenario, task, test, commit, release, and production metric, and verify it with scripts/sdlc_trace.py.

Goal: Make 'is every requirement built and proven?' a command you can run, not an opinion.

Steps:
1. Assign stable ids to every requirement in `docs/product/`: `FR-###` functional, `NFR-###` quality, `SEC-###` security and…
2. Tag every BDD scenario with the ids it proves (`@FR-001`), and add the ids in parentheses to each task in…
3. Name or comment tests with the requirement id they verify so the script and reviewers can find them.
4. Run `python scripts/sdlc_trace.py --target <repo>`; fix every HIGH finding (uncovered requirement, unknown id, duplicate task id…
5. Re-run at each gate: after planning, before review, before release.
6. Extend the chain downstream: record the commit or PR, release version, feature flag, and the metric or SLO that shows the…
7. When the spec changes, update ids in place (retire, never delete) and re-run to expose orphaned tasks and tests.

Never:
- Ids are contracts: renumbering silently breaks the whole chain.
- Coverage percent is a smoke alarm, not proof of quality; read the failing items.
- Setup and polish tasks may lack requirement refs; everything else must have one.
- Do not edit the script output to pass a gate; fix the artifacts instead.

Next: `sdlc-cross-artifact-analysis` for semantic checks the script cannot do, `sdlc-release-production-readiness` for downstream links.
