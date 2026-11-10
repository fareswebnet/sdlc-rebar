# Pipeline: System Merge

Use when integrating a second system or estate into an existing target, such as an acquisition or platform consolidation.

## Outcome

One target serving every source, with per-source proof, decided contradictions, and green cumulative regression.

## Sequence

1. `legacy-analyst` inventories the incoming source independently and extracts its rules.
2. `legacy-analyst` classifies rules as equivalent, parameterizable, additive, or contradictory.
3. `solution-architect` fixes ownership, identity resolution, and data mapping.
4. `fullstack-builder` converges end-to-end slices, core calculations first.
5. `qa-test-engineer` runs cumulative regression across all sources.
6. `independent-verifier` verifies per source with separate visas.
7. `release-manager` rehearses and executes the staged cutover.

## Gates

- Do not implement before the incoming rule matrix exists.
- Do not treat matching names as equivalence; prove it on both sources.
- Do not copy a visa between sources.
- A regression of an earlier source reopens its lines.

## Runtime Hints

- Keep one registry with a source column and a cross-source matrix.
- Use a distinct context for the converger and the verifier.
