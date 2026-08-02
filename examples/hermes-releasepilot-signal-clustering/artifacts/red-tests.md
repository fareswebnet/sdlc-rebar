# Red Tests

These tests define the expected failing tests before the Signal Clustering implementation starts.

The exact test framework should match the target repository. The examples below assume TypeScript with domain unit tests and component tests.

## Domain Tests

Target file:

`tests/domain/signal-clustering.test.ts`

```ts
describe("signal clustering", () => {
  it("groups similar rollback-note signals into one candidate cluster", () => {
    const signals = [
      signal("support", "Alpha", "Exported release notes miss rollback details"),
      signal("support", "Beta", "We need rollback guidance in release notes"),
      signal("sales", "Gamma", "Buyers ask how rollback is documented"),
    ];

    const clusters = clusterSignals(signals, { tenantId: "acme" });

    expect(clusters).toHaveLength(1);
    expect(clusters[0].name).toBe("Rollback details in release notes");
    expect(clusters[0].evidence).toHaveLength(3);
    expect(clusters[0].confidence).not.toBe("low");
    expect(clusters[0].specDraftId).toBeNull();
  });

  it("keeps conflicting detail-level signals visible", () => {
    const clusters = clusterSignals([
      signal("support", "Alpha", "Release notes are too long"),
      signal("support", "Beta", "Release notes need more rollback detail"),
    ], { tenantId: "acme" });

    expect(clusters[0].conflicts).toContainEqual(
      expect.objectContaining({ name: "detail level" })
    );
    expect(clusters[0].availableDecisions).toContain("split");
  });

  it("does not generate a spec for an unvalidated or low-confidence cluster", () => {
    const cluster = candidateCluster({ confidence: "low", validation: "pending" });

    expect(() => generateSpecDraft(cluster)).toThrow("cluster requires human validation");
  });

  it("generates a spec draft only after human acceptance", () => {
    const cluster = candidateCluster({
      name: "Rollback details in release notes",
      confidence: "medium",
      validation: "accepted",
    });

    const draft = generateSpecDraft(cluster);

    expect(draft.problem).toContain("rollback");
    expect(draft.evidence).not.toHaveLength(0);
    expect(draft.validationDecisionId).toBe(cluster.validationDecisionId);
  });

  it("denies cross-tenant cluster access", () => {
    const cluster = candidateCluster({ tenantId: "acme" });

    expect(() => getClusterForTenant(cluster.id, "otherco")).toThrow("not found");
  });
});
```

## Component Tests

Target file:

`tests/components/signal-cluster-review.test.tsx`

```tsx
describe("SignalClusterReview", () => {
  it("renders empty, loading, low-confidence, accepted, rejected, and error states", async () => {
    expect(renderState("empty")).toMatchVisibleState("No signals to cluster");
    expect(renderState("loading")).toMatchVisibleState("Analyzing signals");
    expect(renderState("low-confidence")).toDisableAction("Generate spec");
    expect(renderState("accepted")).toEnableAction("Generate spec");
    expect(renderState("rejected")).toHideAction("Generate spec");
    expect(renderState("error")).toMatchVisibleState("Could not cluster signals");
  });
});
```

## Red Gate

The `releasepilot-tdd` skill must record:

- failing command
- failing assertions
- why each failure maps to BDD
- which implementation files are expected to turn the tests green

Implementation is blocked until this evidence exists.
