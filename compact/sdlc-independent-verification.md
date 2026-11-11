# sdlc-independent-verification (compact)

When: Act as independent verifier: refute done claims via sampled real-server checks, cross-tenant and wrong-role accounts, and mutations, then grant or refuse a visa.

Goal: Make verification a separate role so a green gate cannot be produced by the same agent that wrote the work.

Steps:
1. Independence: start in a fresh context with only the registry, the repo, and this skill; ideally a different model than the…
2. Draw the sample before reading anything else: `python scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed…
3. Start the real server and client with demo data; never a stub written by the implementer.
4. For each sampled line start from the legacy behavior, not from the provided proof: run it through the public interface with a…
5. Send each legacy form field to the target and require it to be returned or rejected with 400; a field silently ignored is a…
6. Run mutations: break the essential rule of each multi-rule line in a copy outside the work tree and confirm at least one test…
7. Grant or refuse: `scripts/sdlc_registry.py visa` with your identifier, or `--refuse` with the finding.
8. Write the audit report: lines sampled, granted, refused, mutations tried, and gate result.

Never:
- Verifier mission is to refute; a line you could not try is not granted.
- Never modify target code; observe and report, the implementer fixes.
- Never grant on a green test or documentation alone.
- Never accept a server or dataset simulated by the implementer.

Next: `sdlc-migration-batch-orchestration` to reopen or close the batch, `sdlc-delivery-retrospective` for repeated refusal causes.
