# Signal Clustering SDLC Map

This map defines what Hermes and its subagents should produce for the first ReleasePilot Signal Clustering slice.

## Product Intent

The product owner wants to convert raw feedback signals into validated product work without losing evidence or context.

First slice:

- ingest a small batch of manually provided feedback signals
- cluster similar signals by theme, pain, requested outcome, and affected account segment
- calculate a transparent confidence score
- show evidence and conflicts
- require human accept, reject, split, or merge action
- generate a PRD/spec draft only after human validation

Non-goals:

- no autonomous roadmap reprioritization
- no production customer messaging
- no external support, CRM, or observability connector
- no model fine-tuning
- no fully automated ticket creation

## Domain Concepts

| Concept | Meaning |
|---|---|
| Signal | A single feedback item, support note, user interview quote, product event, or incident note. |
| Signal Source | Origin of the signal, such as support, sales, product analytics, incident, or interview. |
| Candidate Cluster | A proposed group of similar signals that still needs human validation. |
| Cluster Evidence | The signals, themes, quotes, accounts, and metadata used to justify a cluster. |
| Confidence Score | A transparent estimate that the grouped signals represent one product problem. |
| Conflict | Evidence that weakens or splits the cluster, such as divergent user goals or contradictory severity. |
| Human Validation | Product-owner decision to accept, reject, split, or merge a candidate cluster. |
| Spec Draft | A generated product spec derived from an accepted cluster. |

## Bounded Contexts

| Context | Responsibility | Does Not Own |
|---|---|---|
| Signal Intake | Store normalized signal text, source, account, author, and timestamps. | Prioritization, engineering specs, release decisions. |
| Signal Clustering | Propose clusters, confidence, evidence, and conflicts. | Final product decision, roadmap rank, implementation tasks. |
| Product Decisioning | Validate clusters and decide whether they become product work. | Raw ingestion pipelines, model internals. |
| Spec Generation | Generate PRD and BDD draft from accepted clusters. | Human approval and roadmap commitment. |
| Tenant Administration | Enforce tenant membership, permissions, audit, and data boundaries. | Product semantics. |

## Behavior Contract

The accepted behavior is stored in `artifacts/bdd-scenarios.feature`.

Core rules:

- A cluster cannot become a spec until a human validates it.
- A low-confidence cluster must expose why confidence is low.
- Conflicting signals must be visible before validation.
- The system must preserve source evidence in the generated spec.
- A tenant must not access another tenant's signals or clusters.

## Architecture Direction

Recommended first-slice architecture:

- modular monolith
- deterministic domain services around clustering decisions
- LLM or embedding use behind an interface, not spread through UI code
- relational persistence for signals, clusters, evidence, validation decisions, and audit events
- feature flag wrapping the entire user-visible module
- no background worker until the manual batch workflow proves useful
- no external integrations before internal workflow validation

## Data Ownership

| Data | Owner Context | Notes |
|---|---|---|
| Raw signal text | Signal Intake | Treat as sensitive customer data. |
| Normalized signal metadata | Signal Intake | Tenant-scoped. |
| Candidate cluster | Signal Clustering | Recomputable, but decisions are auditable. |
| Validation decision | Product Decisioning | Durable audit record. |
| Generated spec | Spec Generation | Linked to cluster evidence and validation decision. |
| Feature flag state | Delivery Platform | Owner and rollout conditions recorded. |

## TDD Contract

The first implementation cannot start until red tests exist for:

- grouping similar signals into one candidate cluster
- keeping conflicting signals visible
- blocking spec generation before human validation
- generating a spec draft after acceptance
- blocking cross-tenant access
- rendering empty, loading, low-confidence, accepted, rejected, and error states

## Feature Flag

The feature is guarded by `releasepilot.signal_clustering`.

Initial environments:

- local: enabled for developers
- preview: enabled for internal product reviewers
- production: disabled until release owner approves

## PR Evidence

The PR must include:

- problem and scope
- BDD scenarios
- architecture and data impact
- red-to-green test evidence
- screenshots or local preview notes
- security and privacy review
- rollout and rollback notes
- residual risk

## Post-Release Learning

Track:

- accepted clusters per week
- rejected clusters per week
- split or merged cluster corrections
- spec drafts generated from accepted clusters
- time from signal batch to accepted spec
- manual edits required after spec generation
- model or heuristic cost per cluster
- defect or incident caused by clustering output

The weekly Hermes routine should propose skill improvements only when a repeated failure mode appears.
