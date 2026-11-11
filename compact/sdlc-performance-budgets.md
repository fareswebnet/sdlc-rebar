# sdlc-performance-budgets (compact)

When: Define performance budgets (latency percentiles, throughput, payload and bundle size, memory, startup, query counts, cost per request) tied to user journeys and SLOs, measure them in CI and production, and treat a…

Goal: Turn 'it should be fast' into numbers with owners, tests, and consequences.

Steps:
1. Pick the journeys that matter and the user-visible metrics for each (for web: LCP, INP, CLS; for APIs: p50, p95, p99 latency…
2. Set a budget per metric from the SLO and the competition or baseline, with an explicit environment and data volume; add resource…
3. Measure the baseline before changing anything, on production-shaped data.
4. Automate: load and benchmark tests in CI for hot paths, bundle-size and query-count checks per PR, and synthetic checks in…
5. Break down the budget across tiers (client, edge, service, database) so each team owns a share.
6. On breach, fail the gate or require a recorded waiver with owner and expiry; investigate with profiling before optimizing.
7. Review budgets each release and after incidents; tighten what is comfortably met.

Never:
- Do not optimize without a measurement and a budget.
- Averages hide tail latency; budget percentiles.
- Budgets measured on toy data are fiction; state the data volume.
- A waiver without an expiry becomes the new budget.

Next: `sdlc-performance-scalability-cost` for capacity and cost, `sdlc-observability-reliability` for production SLOs.
