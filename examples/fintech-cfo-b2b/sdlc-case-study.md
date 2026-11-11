# Example Case Study - Fintech CFO B2B

This example shows how the suite can structure a B2B fintech product idea.

## Raw Idea

A CFO copilot for startups that tracks burn, runway, forecast, budget variance, investor metrics, and board-ready reporting.

## Suggested Skill Flow

1. `sdlc-idea-framing`
2. `sdlc-market-user-discovery`
3. `sdlc-idea-framing`
4. `sdlc-domain-modeling`
5. `sdlc-bounded-context-map`
6. `sdlc-bdd-specifications`
7. `sdlc-ux-product-design`
8. `sdlc-data-architecture`
9. `sdlc-security-privacy-compliance`
10. `sdlc-security-privacy-compliance`
11. `sdlc-ai-product-architecture`
12. `sdlc-delivery-roadmap-backlog`
13. `sdlc-definition-of-done`
14. `sdlc-observability-reliability`

## Candidate Bounded Contexts

- Company and tenant management
- Financial data ingestion
- Forecasting and scenarios
- KPI and investor metrics
- Alerts and recommendations
- Billing and entitlement
- Audit and compliance

## Example Behavior

```gherkin
Feature: Runway monitoring

Scenario: CFO sees a runway risk
  Given a company has 120000 EUR of cash
  And the average monthly burn is 30000 EUR
  When the CFO opens the finance dashboard
  Then the system shows a runway of 4 months
  And flags the company as below the 6 month safety threshold
```

## Important Disclaimer

This suite structures software/product work. It does not provide financial, legal, accounting, compliance, or investment advice.
