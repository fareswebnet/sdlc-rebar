# Skill evaluation: sonnet

Date: 2026-11-11  Runs per scenario: 3  Skills: compact

| Skill | Scenario | Baseline pass | With skill pass | Failures with skill |
|---|---|---|---|---|
| sdlc-api-integration-contracts | contract-breaking-change | 3/3 | 3/3 | - |
| sdlc-application-architecture | arch-microservices-default | 3/3 | 3/3 | - |
| sdlc-identity-access-multitenancy | authz-ui-hiding | 3/3 | 3/3 | - |
| sdlc-observability-reliability | alert-noise | 1/3 | 3/3 | - |
| sdlc-prd-requirements | prd-vague-verbs | 3/3 | 3/3 | - |
| sdlc-product-strategy | strategy-scope-creep | 3/3 | 3/3 | - |
| sdlc-release-production-readiness | release-unknown-rollback | 3/3 | 3/3 | - |
| sdlc-technical-debt-evolution | debt-refactor-for-taste | 3/3 | 3/3 | - |

Total: baseline 22/24, with skill 24/24.

String checks are a floor, not a quality judgement; read the replies for scenarios that fail.

## Replies

### sdlc-api-integration-contracts / contract-breaking-change / baseline / PASS

Both changes are breaking for external clients, so I'd split "ship today" into a safe part that goes out today and a enforcement part that follows after a notice window.

## What breaks if shipped as-is
- **Rename:** any integrator reading `customerName` gets `undefined`/null, often failing silently (blank names in invoices, emails, etc.).
- **Mandatory `phone`:** any integrator not sending it starts getting 400/422 on POST /orders, which means lost orders and revenue for them and support load for you.

## Ship today (non-breaking)

**1. Rename: additive, then deprecate**
- Return both fields in responses:
  ```json
  { "client_name": "Ada Lovelace", "customerName": "Ada Lovelace" }
  ```
- If `customerName` is also accepted on input, accept both, prefer `client_name`, and reject only if they conflict.
- Mark `customerName` deprecated in the OpenAPI spec and add headers: `Deprecation: true` and `Sunset: <date>` (e.g., 90 days out).
- Remove the old field only after the sunset date, once usage metrics show it's safe.

**2. `phone`: soft enforcement first**
- Add validation, but in log/warn-only mode today:
  - Don't reject. Log the integrator (API key/client ID) for each request missing `phone`.
  - Return a response header like `Warning: 299 - "phone will be required starting <date>"`.
- Put enforcement behind a feature flag or config (`REQUIRE_PHONE_ON_ORDERS`), ideally switchable per API key so you can turn it on for integrators who've already adapted.
- Check that existing downstream code (DB column NOT NULL, fulfillment, SMS) copes with null phone until enforcement is on. If you add a NOT NULL constraint, do it only after enforcement and a backfill plan for existing rows.

**3. Communicate today**
- Email all 40 integrators: what changes, exact dates (deprecation, enforcement, removal), before/after examples, and a contact for questions.
- Update the changelog, docs, and OpenAPI spec.

## Later (after the notice window)
- Use the logs to identify integrators still omitting `phone` or still reading `customerName`, and contact them directly.
- Flip the flag to enforce `phone` (error should be a clear 422 with `{"field":"phone","message":"required"}`).
- Drop `customerName` from responses after the sunset date.

## If you truly must enforce today
- Put the breaking behavior under a new version (`/v2/orders` or `Accept-Version` header) and keep v1 unchanged, or
- Enable it only for integrators who've confirmed readiness, using the per-key flag.
- Have a rollback ready (flag off or revert deploy) and watch 4xx rates on POST /orders closely after release.

## Tests to add
- Response contains both `client_name` and `customerName` with equal values.
- POST without `phone`: succeeds with warning header when flag off; returns 422 when flag on.
- POST with `phone`: succeeds in both modes.
- Contract/snapshot tests so the response shape changes are deliberate.

If you share the serializer/DTO and the order validation code, I can write the concrete diff for your stack.

### sdlc-api-integration-contracts / contract-breaking-change / with skill / PASS

# Decision

Don't ship both as hard breaking changes today. Ship the compatible versions today and enforce the breaking behavior after a notice period.

Both changes are breaking for external consumers:
- **Rename:** any integrator parsing `customerName` will get null or an error, silently or loudly.
- **Mandatory `phone`:** any integrator that doesn't send it will get failed order creation, which is a revenue-impacting path.

I have no repo access, so I'm assuming the API is unversioned and that you can't yet tell which integrators send `phone`. Please correct me if either is wrong.

## What to ship today

**1. Rename (response, additive)**
- Return both `customerName` and `client_name` with the same value.
- Mark `customerName` as `deprecated: true` in OpenAPI.
- Add `Deprecation` and `Sunset` response headers, plus a `Link` header pointing to the migration doc.
- Check the naming convention first. If the rest of the API is camelCase, `client_name` introduces inconsistency, and `clientName` may be the better target. Decide this now, because you can't rename twice cheaply.

**2. `phone` in POST /orders (request, non-enforcing)**
- Keep it accepted but optional, and document it as "required from <date>".
- If it's missing, return a `Warning` header or a response `warnings[]` entry, and emit a metric tagged by API key or integrator.
- This tells you which of the 40 integrators will break, so you can contact them directly.
- Don't tighten the phone format (such as E.164) in the same release.

## Enforcement plan

| Step | Timing | Action |
|---|---|---|
| Announce | Today | Email and changelog to all 40 integrators, with the exact dates and examples |
| Enforce `phone` | Date minus 30 to 60 days, per-key flag | Reject missing `phone` with `422` and a problem+json body (`code: phone_required`, pointer `/phone`). Start with integrators already sending it |
| Remove `customerName` | At least 90 to 180 days, or in `/v2` | Remove only after usage of the old field in traffic or logs drops to zero or the sunset passes |

Choose the notice windows to match any contractual or SLA terms you have. Where contracts allow, `/v2` is cleaner than in-place removal.

## Trade-offs

- **Both fields in the response:** a slightly larger payload and a temporary duplicate. That's cheap compared with 40 simultaneous breakages.
- **Delayed enforcement of `phone`:** you don't get the data guarantee today. If it's urgent for a business reason, use a per-key feature flag and enforce for new integrators first.
- **Hard cutover today:** the only upside is speed, and the downside is unbounded support load and failed orders. I wouldn't recommend it.

## Contract updates

- **OpenAPI:** add `client_name`, mark `customerName` deprecated, and keep `phone` out of `required` until enforcement. Make `phone` nullable in the response schema, since existing orders may lack it.
- **Errors:** document the `422` shape before enabling it.

## Validation

- Add an OpenAPI diff check in CI (such as oasdiff) so breaking changes fail the build unless explicitly approved.
- Add contract tests: a response containing both fields, a POST without `phone` returning success plus a warning, and a POST without `phone` after the flag returning `422`.
- Dashboard: the share of POSTs missing `phone` by integrator, and reads of the deprecated field if you can track them.
- Roll out behind a flag with a rollback path, and watch the 4xx rate on POST /orders after each step.

## Next actions

1. Confirm the field naming convention (`client_name` vs `clientName`).
2. Pull the integrator list from API keys or gateway logs and assign an owner for each.
3. Decide the enforcement and sunset dates, and send the announcement today.
4. Ship the additive changes and the telemetry today.

If you tell me which of these constraints are fixed (a hard business deadline for `phone`, or no versioning mechanism), I can adjust the plan and draft the OpenAPI diff and the integrator notice.

### sdlc-api-integration-contracts / contract-breaking-change / baseline / PASS

Both changes are breaking for external clients, so shipping them as-is today will likely break some of your 40 integrators. You can still ship today if you split each change into a safe step now and the breaking step later.

## 1. Rename `customerName` to `client_name`

**Today (non-breaking):** return both fields in responses.

```json
{
  "client_name": "Acme Corp",
  "customerName": "Acme Corp"
}
```

- Mark `customerName` as deprecated in the OpenAPI spec and changelog.
- Add a `Deprecation` header, and a `Sunset` header with a date, on responses that include the old field.
- If POST/PUT bodies also accept this field, accept both names. If both are sent and differ, return a 400.

**Later (breaking):** remove `customerName` after the sunset date. 90 days is typical for external integrators. Before removing it, check logs or analytics for which API keys still read or send the old field, and contact those integrators directly.

## 2. Make `phone` mandatory in POST /orders

Making a field required rejects requests that worked yesterday, so it's the riskier change.

**Safer rollout:**
1. **Today:** keep `phone` optional, but return a warning header (e.g. `Warning` or a custom `X-API-Warn: phone will be required from <date>`) when it's missing. Log which API keys omit it.
2. **Announce:** email all integrators with the enforcement date and an example payload.
3. **Enforcement date:** return `422` with a clear error body, such as `{"error":"validation_failed","field":"phone","message":"phone is required"}`.

If you must enforce today, gate it by API version or by key. For example, enforce it only for keys created after today, or for clients sending `API-Version: 2026-11-11`. Existing integrators stay on the old behavior until they opt in.

## What to do before deploying

- Check the last 7–30 days of POST /orders logs for the share of requests without `phone`. That tells you how many integrators you'd break.
- Update the OpenAPI spec, SDKs, docs, and any example payloads or webhooks that use `customerName`.
- Check internal consumers too, such as webhooks, exports, and dashboards, which often read the same field.
- Add contract tests asserting that both fields are present during the deprecation period.
- Put the change behind a feature flag so you can roll back quickly.
- Pick validation rules for `phone` (E.164 or looser) and document them. Stricter format validation is another breaking change if you add it at the same time.

## Suggested changelog and announcement

> **Deprecation:** `customerName` is renamed to `client_name`. Both fields are returned until <sunset date>, after which `customerName` is removed.
> **Upcoming change:** `phone` becomes required on POST /orders on <date>. Requests without it will receive HTTP 422.

If you share the framework (Express, Django, Spring, etc.) and the serializer or schema code, I can write the exact changes for the dual-field response and the phased validation.

### sdlc-api-integration-contracts / contract-breaking-change / with skill / PASS

# Decision

**Don't ship both changes as hard breaks today.** Both are breaking for external consumers. Ship a backward-compatible version today and enforce the breaking behavior after a notice window.

## Impact (no repo access, so this is inferred)

| Change | Who breaks | How |
|---|---|---|
| Rename `customerName` to `client_name` in responses | All ~40 integrators that read the field | Parsers get null/undefined, and strict deserializers may fail |
| `phone` mandatory in POST /orders | Every integrator that doesn't already send it | Orders fail with 4xx, which means lost revenue and support load |

I can't see who sends `phone` today, so check order logs for the share of requests that omit it.

## What to ship today (non-breaking)

**1. Rename (expand/contract)**
- Return **both** `customerName` and `client_name` with identical values.
- Mark `customerName` as `deprecated: true` in OpenAPI.
- Add `Deprecation` and `Sunset` response headers (RFC 8594) on affected endpoints.
- Contract phase: remove `customerName` only after the sunset date, ideally in `/v2` or behind a version header.

**2. Mandatory `phone`**
- Keep it optional at the schema level today.
- Log and meter requests that omit it, tagged by API key/integrator.
- Return a warning header, such as `Warning` or a custom `X-API-Deprecation`, on those requests.
- Enforce later with a 422 and a clear error body, per integrator or globally after the window.

## Proposed timeline (adjust to your contracts and SLAs)
- **Day 0:** dual fields, warnings, and metrics ship. Email all 40 integrators with a changelog and migration notes.
- **Day 30:** reminder to integrators still sending requests without `phone` or reading `customerName`, identified from metrics.
- **Day 60-90:** enforce `phone`, and remove `customerName` in the new version.

## OpenAPI sketch

```yaml
components:
  schemas:
    Order:
      properties:
        client_name:
          type: string
        customerName:
          type: string
          deprecated: true
          description: Deprecated. Use client_name. Removed on <SUNSET_DATE>.
    CreateOrderRequest:
      properties:
        phone:
          type: string
          description: Will become required on <ENFORCE_DATE>.
```

For the enforce phase, move `phone` into `required` and document the error:

```json
{"type":"…/validation","title":"Validation failed","status":422,
 "errors":[{"field":"phone","code":"required"}]}
```

## Trade-offs
- **Dual fields:** slightly larger payloads and a temporary duplicate to maintain, but zero consumer breakage.
- **Delayed enforcement:** data quality for `phone` improves later. If `phone` is needed today for a business reason, make it required only for new API keys, or for a new version.
- **Hard break today:** the only upside is simplicity. The downside is up to 40 simultaneous incidents and no rollback path for consumers.

## Open questions
- Does `customerName` also appear in **requests**, webhooks, events, or exports? Those need the same dual-accept treatment.
- Is snake_case the convention for the rest of the API? Mixing `client_name` with camelCase fields creates inconsistency, so confirm it's intentional.
- Do you have a versioning policy or contractual notice period for the public API?

## Validation
- Contract tests: a response contains both fields with equal values, and a POST without `phone` still returns 201 plus the warning.
- Run an OpenAPI diff (e.g. oasdiff) in CI to confirm no breaking changes are reported for today's release.
- Test against one or two real integrator SDKs or sample clients, including strict deserializers.
- Add dashboards for per-integrator usage of `customerName` and of missing `phone`, plus alerts on 4xx rate after enforcement.
- Have support and docs ready with the changelog, migration guide, and an integrator contact list.

## Next action
Confirm the open questions above. Then I can draft the integrator announcement, the full OpenAPI diff, and the middleware for dual fields and warning headers.

### sdlc-api-integration-contracts / contract-breaking-change / baseline / PASS

Both changes are breaking for external clients, so I'd split them into a part that is safe to ship today and a part that needs a transition window. I can't see your repo, so this is stack-agnostic. Tell me the framework and I'll write the actual diff.

## What to ship today

**1. Rename: add `client_name` and keep `customerName`**

Return both fields in every response that currently has `customerName`:

```json
{
  "id": "ord_123",
  "client_name": "Ada Lovelace",
  "customerName": "Ada Lovelace"
}
```

- Mark `customerName` as deprecated in the OpenAPI spec and docs.
- Add `Deprecation: true` and `Sunset: <date>` headers. Something like 90 days out is typical for external integrators.
- If `customerName` is also accepted in request bodies, accept both there too. If both are sent and differ, return 400.
- Remove `customerName` only after the sunset date, and only once usage is near zero.

**2. `phone` mandatory: warn first, enforce later**

Making it required today would turn every integrator that omits `phone` into a wave of 4xx errors, and with 40 integrators some almost certainly do. Instead:

- Today, accept orders without `phone`, but:
  - Log and emit a metric per API key or client ID when `phone` is missing, so you know exactly who will break.
  - Return a response header such as `Warning: 299 - "phone will be required starting 2026-12-15"`.
- Enforce on a fixed date, after you've contacted the affected integrators. Return `422` with a clear body:
  ```json
  {"error": "validation_failed", "details": [{"field": "phone", "message": "phone is required"}]}
  ```
- Optionally gate enforcement with a per-client flag so you can turn it on for integrators who are ready and for all new keys immediately.

**Check before enforcing:**
- What format counts as valid (E.164 or free text)? Don't tighten format rules in the same release.
- Do downstream systems (DB column `NOT NULL`, CRM, fulfillment) need a backfill for existing orders? Don't add the DB constraint until the API enforcement is live and old rows are handled.
- Do PUT/PATCH endpoints need the same rule?

## Rollout checklist

1. Update the OpenAPI spec, SDKs, and examples.
2. Add tests:
   - Responses contain both fields with equal values.
   - POST without `phone` succeeds in warn mode and logs a metric.
   - POST without `phone` returns 422 in enforce mode.
3. Publish a changelog entry and email the integrators today, with dates for the sunset and enforcement.
4. Watch the missing-`phone` metric and `customerName` usage before each cutoff.

## If leadership insists on a hard cutover today

The alternative is versioning: put the new shape under `/v2/orders` (or a version header) and leave v1 unchanged. That gives you the exact behavior you want without breaking anyone, and integrators migrate on their own schedule.

Which framework and language are you using, and is the response serialization centralized (DTO/serializer) or spread across handlers? With that I can write the code.

### sdlc-api-integration-contracts / contract-breaking-change / with skill / PASS

# Decision: don't ship either change as a hard break today. Ship the compatible versions today and enforce later.

I have no repo or tool access, so I can't see the consumers, the current OpenAPI spec, or your versioning conventions. Treat this as a plan to check against those.

## Why

Both changes are breaking for the ~40 external integrators:

| Change | Who breaks | How |
|---|---|---|
| Rename `customerName` to `client_name` (response) | Every consumer that reads the field | Parsers get `undefined`/null or fail deserialization in strict typed clients. Failures are often silent, e.g. blank names in their UI or records. |
| `phone` becomes required (POST /orders) | Every consumer that doesn't send it today | Orders start failing with 4xx. That means lost revenue for them and a support spike for you. Retry logic may also hammer you on a non-retryable error. |

Since the consumers are external and you don't control their deploy cycles, "ship it today" has no safe rollback once they hit it.

## What can ship today

**1. Rename: additive, not a replace**
- Return both `customerName` and `client_name` with the same value.
- Mark `customerName` as `deprecated: true` in OpenAPI.
- Add `Deprecation` and `Sunset` (RFC 8594) headers, plus a `Link: rel="deprecation"` pointing to the migration note.
- Choose a sunset date based on your integrators' realities, typically 90 to 180 days for external partners.
- Check your repo's naming convention first. The mix of `customerName` (camelCase) and `client_name` (snake_case) suggests either a convention shift or a new inconsistency. Confirm it's intentional before it becomes public contract.

**2. Phone: phased enforcement**
- Today: keep `phone` optional in validation. Document it as "required from <date>". If missing, accept the order but add a `Warning` header and a response `warnings[]` entry.
- Log which API keys omit `phone`. That gives you the real list of at-risk integrators.
- Enforce later, either for new API keys or integrators created after today immediately, and for everyone after the notice period. Alternatively, enforce in `/v2`.
- When enforced, return a consistent `422` with a machine-readable code (e.g. `phone_required`) and field pointer. Make it clearly non-retryable.
- Define the format now (E.164?) so integrators don't send "required" junk to satisfy validation.

## Trade-offs
- **Additive and phased:** a bigger payload and two fields to maintain temporarily, but zero breakage and the migration is measurable.
- **Hard cutover today:** cleaner contract, but expect broken integrations, emergency support, and likely a rollback that breaks things a second time.
- **New `/v2`:** the cleanest, but heavier to run in parallel. It's worth it if more breaking changes are coming.

## OpenAPI sketch

```yaml
components:
  schemas:
    Order:
      properties:
        client_name:
          type: string
        customerName:
          type: string
          deprecated: true
          description: Deprecated, use client_name. Removal on <sunset-date>.
    CreateOrderRequest:
      properties:
        phone:
          type: string
          description: E.164. Optional until <enforce-date>, then required.
          example: "+14155550123"
```

## Next actions
1. Confirm consumers: pull the list of 40 integrators and their API keys from your gateway/auth system, and identify owners and contacts.
2. Ship the additive response and the optional-with-warning phone behavior today.
3. Email integrators today with the change, dates, and migration steps. Update the changelog and docs.
4. Add metrics: usage of `customerName` consumers (if you can tell) and the count of requests missing `phone`, by API key.
5. Set the enforcement date, then notify the integrators still missing `phone` before enforcing.

## Validation
- Contract tests: the response includes both fields with equal values, and old-shape POSTs without `phone` still return 2xx with a warning.
- Run the existing consumer or integration tests against the new build unchanged. They should pass.
- Add a schema diff check (e.g. `oasdiff`) in CI that fails on breaking changes without a version bump.
- Verify the `Deprecation`/`Sunset` headers in staging.
- After release, watch the 4xx rate on POST /orders and support tickets.

If you really do need the hard break today (e.g. a legal or compliance driver for `phone`), tell me. I'd then scope it to a `/v2` or a feature flag per API key, with a direct heads-up to the affected integrators first.

### sdlc-application-architecture / arch-microservices-default / baseline / PASS

# Recommended architecture: a modular monolith on managed services

## Why not microservices, Kubernetes, and Kafka (yet)

- **Load:** 50 req/s peak is small. One modest app instance with a Postgres database handles that, and two instances give you redundancy.
- **Team size:** Microservices solve organizational scaling, meaning many teams deploying independently. Netflix has thousands of engineers and hundreds of millions of users. With 4 engineers, you'd pay the costs (distributed transactions, service-to-service auth, versioned APIs, tracing, per-service CI/CD) without the benefit.
- **Domain:** Invoicing needs strong consistency (totals, tax, numbering sequences, payment state). Splitting it across services turns simple ACID transactions into sagas and eventual consistency, which is a common source of billing bugs.
- **Operations:** Kubernetes and Kafka each need dedicated operational expertise. For a team of 4, that could consume 25-50% of engineering time that should go to product.

## Proposed design

**Application**
- One deployable codebase (Rails, Django, Laravel, Spring Boot, or .NET, whichever the team knows best), structured as **modules with enforced boundaries**: Customers/Tenants, Catalog, Invoicing, Payments, Tax, Notifications, Reporting, Auth.
- Modules talk through explicit internal interfaces, not by reaching into each other's tables. Use lint or architecture-test rules to enforce this.
- Run 2+ instances behind a load balancer for availability and zero-downtime deploys.

**Data**
- **PostgreSQL** (managed: RDS, Cloud SQL, or similar) with automated backups, point-in-time recovery, and a read replica if reporting gets heavy.
- Multi-tenancy: a `tenant_id` column on every table, enforced in the data layer, optionally backed by Postgres row-level security. 200 tenants doesn't justify schema-per-tenant or database-per-tenant unless a customer contractually requires it.
- Gapless, per-tenant invoice numbering via a transactional sequence table, which is easy in a single database and painful across services.
- Append-only audit log table for invoice and payment state changes.

**Async work**
- A background job system (Sidekiq, Celery, BullMQ, or a Postgres-backed queue like River or pg-boss) for PDF generation, email delivery, webhooks, and scheduled or recurring invoices.
- Use the **transactional outbox** pattern for reliable event delivery to external systems. That gives you most of what you'd want Kafka for, with no extra infrastructure.

**Storage and edge**
- Object storage (S3 or equivalent) for generated PDFs and attachments, served via short-lived signed URLs.
- CDN/WAF in front of the app. Redis only if you need caching or rate limiting.

**Integrations**
- Payment provider (e.g., Stripe) via webhooks with idempotency keys.
- Accounting/ERP exports (CSV, API) as background jobs.
- Public API with per-tenant API keys and rate limits.

**Deployment and operations**
- Containerize with Docker and deploy to a managed platform (AWS ECS Fargate, Cloud Run, Fly.io, Render, or similar). This gives container benefits without running a cluster.
- CI/CD with automated tests and migrations, and infrastructure as code (Terraform or Pulumi).
- Observability: structured logs, error tracking (Sentry), metrics and alerting (Datadog, Grafana Cloud, or CloudWatch), and uptime checks.
- Security: SSO/SAML or OIDC for B2B customers (often asked for), RBAC per tenant, encryption at rest and in transit, secrets manager, and regular dependency scanning. Plan for SOC 2 if customers ask.

## Capacity sanity check

50 req/s is about 4.3M requests/day at sustained peak, and real traffic will be far lower. A single small Postgres instance handles thousands of simple transactions per second. The likely bottlenecks are PDF generation and report queries, both of which are handled by background workers and a read replica, not by service decomposition.

## Addressing the CTO's concerns

Frame it as sequencing rather than rejection:

1. **Design for extraction.** Module boundaries, an outbox, and no cross-module table access mean any module can become a service later with limited rework.
2. **Define triggers for splitting.** For example: a module needs a different scaling profile, a separate team owns it, or its release cadence is blocked by the others. Reporting or PDF rendering are the likeliest first candidates.
3. **Define triggers for Kafka.** Multiple independent consumers needing replayable event streams, or sustained throughput in the thousands of events per second. Neither is close at this scale.
4. **Define triggers for Kubernetes.** Many services, a dedicated platform engineer, or workloads that outgrow managed container platforms.
5. **Make the cost visible.** Estimate the engineering time the distributed setup would take (likely months of the 4-person team's capacity) versus shipping features to the first 200 customers.

If the CTO's real goals are reliability, scalability, and a modern stack, this design delivers them: horizontally scalable stateless app instances, managed HA database, async processing, and containerized deployments. It avoids paying for scale you don't have.

## Suggested phasing

1. **Months 0-3:** Core monolith with tenants, auth, invoices, PDF, email, and payments, deployed to a managed container platform with CI/CD and monitoring.
2. **Months 3-6:** Recurring billing, API and webhooks, audit and reporting, SSO, and load testing at 5x expected peak.
3. **Later:** Revisit extraction based on measured bottlenecks and team growth.

If you tell me the team's primary language and cloud provider, I can turn this into a concrete stack, module layout, and schema outline.

### sdlc-application-architecture / arch-microservices-default / with skill / PASS

# Recommendation: modular monolith on managed PostgreSQL, with no Kubernetes or Kafka for now

## Decision

- **One deployable codebase** with strict internal module boundaries, plus a **separate worker process** built from the same code.
- **PostgreSQL** as the system of record and the job queue (outbox plus `SELECT ... FOR UPDATE SKIP LOCKED`).
- A **managed container platform** (ECS Fargate, Cloud Run, Azure Container Apps, or similar) instead of self-run Kubernetes.
- **No Kafka.** Use a transactional outbox for domain events and in-process handlers.

## Rationale

- **Load:** 50 rps peak is small. One modest instance can serve it, and we'd run 2 for availability, not for capacity. Even 10x growth stays within a single well-indexed Postgres.
- **Team:** With 4 engineers, each microservice means its own pipeline, on-call surface, versioned contracts, and distributed debugging. That cost would come straight out of feature delivery.
- **Domain:** Invoicing needs strong consistency. Gapless per-tenant numbering, immutable issued invoices, and ledger/payment state changes are easy in one ACID transaction. Across services they require sagas and compensation.
- **The Netflix comparison:** Netflix adopted microservices to scale thousands of engineers and hundreds of millions of users independently. Our constraints are the opposite. The goal is the same one Netflix had, a structure the team can build and evolve, but for us that means a monolith.

## Structure

**Modules** (each owns its own Postgres schema, and no module reads another's tables):

| Module | Responsibility |
|---|---|
| Identity & Tenancy | users, roles, tenant config |
| Parties | customers, billing contacts |
| Catalog & Tax | products, prices, tax rules |
| Invoicing (core) | draft, issue, void, credit note, numbering |
| Payments | gateway integration, reconciliation, dunning |
| Documents | PDF rendering, storage |
| Notifications | email, webhooks |
| Integrations | accounting/ERP, e-invoicing |
| Reporting | read models and queries |
| Audit | append-only trail |

**Layers inside each module (hexagonal):** `api` (public interface) → `application` (use cases) → `domain` (pure rules) ← `adapters` (DB, gateways, email, storage). Dependencies point inward only.

**Dependency rules, enforced in CI by an architecture test** (ArchUnit, import-linter, or dependency-cruiser, depending on the stack):
- Modules call each other only through their `api` package or via events.
- No cross-schema joins, and the domain layer has no framework or I/O imports.

**Multi-tenancy:** `tenant_id` on every row, with Postgres row-level security as a backstop to application checks.

**CQRS:** Use it lightly. Reporting gets its own query models and read-optimized views, but the same database. Add a replica later if needed.

## Transactions, failure handling, jobs

- **Issuing an invoice** is one DB transaction: validate, allocate number from a per-tenant counter row, set status to `issued`, write the audit entry, and write an outbox event. Issued invoices are immutable, and corrections are done through credit notes.
- **Outbox:** a relay publishes events to in-process handlers and the job queue. Handlers must be idempotent.
- **Background jobs** (in the worker): PDF generation, email, recurring invoices, payment webhooks, dunning, exports. Use retries with exponential backoff, a dead-letter table with alerting, and per-job idempotency keys.
- **External calls** (gateway, ERP): timeouts, circuit breakers, and idempotency keys on every API and webhook. Webhooks are deduplicated by event ID.
- **Degradation:** if email, PDF, or the gateway is down, invoicing keeps working and the jobs queue up.

## Deployment

- 2+ app instances behind a load balancer, 1–2 workers, managed Postgres with HA and point-in-time recovery, and object storage for PDFs.
- Containerized from day one, so a later move to Kubernetes or service extraction is cheap.
- CI/CD with automated migrations (expand/contract), OpenTelemetry tracing, structured logs, and alerts on queue depth, error rate, and p95 latency.
- Starting targets are RPO ≤ 5 min and RTO ≤ 1 hr. Confirm them with the business.

## Trade-offs

- **Shared release and blast radius:** a bad deploy affects everything. Mitigate with feature flags, canary or rolling deploys, and the separate worker process.
- **Coarser scaling:** the whole app scales together. At 50 rps that is irrelevant.
- **Boundary erosion:** the main risk of a monolith. The CI architecture tests and schema ownership mitigate it.
- **Single database as a bottleneck:** unlikely at this scale. Add indexes, a replica, and partitioning by tenant before anything else.

## When to revisit (extraction triggers)

- PDF rendering or imports contend for CPU, so extract Documents as a worker service first.
- Payments needs PCI or regulatory isolation.
- More than ~3 independent teams are blocked by shared releases.
- A module needs a different scaling profile or release cadence.
- Sustained load beyond what a vertically scaled Postgres and a few app instances can handle.

Adopt Kafka when multiple independent consumers need replayable event streams, and Kubernetes when you run enough services to justify the platform team.

## ADRs to write now

1. Modular monolith over microservices.
2. PostgreSQL as the single datastore, with schema-per-module and RLS for tenancy.
3. Transactional outbox and Postgres-backed job queue instead of Kafka.
4. Managed container platform instead of Kubernetes.
5. Invoice immutability and gapless numbering strategy.
6. Module dependency rules and their CI enforcement.

## Talking to the CTO

Frame this as sequencing, not rejection: "We're designing for easy extraction, with clear boundaries, an event outbox, and containers. We'll split services when a measured trigger fires, not before." This keeps the option open without paying the cost up front.

## Next actions

1. Run a 1-hour event-storming session to confirm module boundaries.
2. Write the ADRs above and get CTO sign-off on the extraction triggers.
3. Build a walking skeleton: one module, CI with architecture tests, the deploy pipeline, and the worker.
4. Implement the invoice-issue transaction first, since it is the riskiest consistency path.

## Validation

- Load test at 250 rps (5x peak) with realistic tenant data, and check p95 latency and queue drain times.
- Run failure drills: kill the worker mid-job, fail the gateway, replay duplicate webhooks, and restore from backup.
- Test concurrent issuing for one tenant to verify numbering has no gaps or duplicates.
- Write RLS tests proving that tenant A can never read tenant B's data.
- Track the architecture-test violation count and the extraction-trigger metrics quarterly.

### sdlc-application-architecture / arch-microservices-default / baseline / PASS

# Recommendation: a modular monolith on managed infrastructure

At 50 req/s peak, 200 tenants, and 4 engineers, microservices + Kubernetes + Kafka would cost you far more than it gives you. I'd propose an architecture that can grow into that later, and give the CTO a reasoned case rather than a flat "no."

## Why not the Netflix stack

- **Scale mismatch.** 50 req/s is well within what a single modest app instance and one Postgres database handle. Netflix runs microservices because of thousands of engineers and millions of req/s, and the architecture mirrors their org structure (Conway's law). You have one team.
- **Operational load.** Kubernetes, a Kafka cluster, service meshes, distributed tracing, and per-service CI/CD would consume a large share of 4 people's time, and that time would not go to invoicing features.
- **Correctness risk.** Invoicing is accounting-adjacent. You want ACID transactions, gapless invoice numbering, and simple audit trails. Splitting this across services forces sagas, eventual consistency, and idempotency work in places where a single DB transaction would do.
- **Cost of mistakes.** A distributed monolith (microservices that must deploy together) is the common failure mode for small teams.

## Proposed architecture

**Application**
- One deployable app (e.g. Django, Rails, Spring Boot, or NestJS, whichever the team knows best), run as 2–3 stateless instances behind a load balancer for availability, not for capacity.
- Internally organized as modules with enforced boundaries: `customers`, `invoicing`, `billing/payments`, `tax`, `notifications`, `reporting`, `identity/tenancy`. Modules talk through explicit interfaces, not by reaching into each other's tables. This is what makes later extraction possible.

**Data**
- Managed PostgreSQL (RDS, Cloud SQL, etc.) with a primary and a read replica or standby, point-in-time recovery, and automated backups.
- Multi-tenancy: a shared schema with `tenant_id` on every table, enforced with Postgres row-level security. 200 tenants doesn't justify database-per-tenant.
- Invoice numbering via per-tenant sequences or a counter row updated in the same transaction.
- Append-only audit log table for invoice state changes.
- Money as integer minor units or `numeric`, with the currency stored alongside it. Never floats.

**Async work**
- A background job queue for PDF generation, emails, webhooks, and scheduled/recurring invoices. Options: a Postgres-backed queue (e.g. Sidekiq-alternatives like GoodJob, Solid Queue, Oban, pg-boss, or Procrastinate) or SQS. Use the transactional outbox pattern so jobs are enqueued atomically with the data change.
- Make all jobs idempotent.

**Storage and edge**
- Object storage (S3 or equivalent) for generated PDFs and attachments.
- CDN/WAF in front. Redis only if you actually need caching or rate limiting.

**Integrations**
- Payment provider (Stripe, etc.), email provider, and accounting/ERP exports behind adapter interfaces. Outbound webhooks with retries and signatures. Inbound webhooks are processed via the queue.

**Hosting**
- A managed PaaS or container service (ECS Fargate, Cloud Run, Fly, Render, App Runner). You get rolling deploys, autoscaling, and health checks without running a cluster.
- Infrastructure as code (Terraform/Pulumi), with staging and production environments.

**Operations**
- CI/CD with automated tests and one-click rollback, plus migrations that are backward compatible (expand/contract).
- Structured logs, metrics, error tracking (Sentry), uptime checks, and alerts on latency, error rate, queue depth, and replication lag.
- Security basics: SSO/SAML option for B2B customers, RBAC per tenant, encryption at rest and in transit, secrets manager, and regular dependency scanning.

## Capacity sanity check

50 req/s at peak is about 3,000 req/min. If an average request takes about 50 ms of DB time, a single Postgres instance handles this with large headroom. The heavy work (PDF rendering, batch invoice runs at month end) moves to the queue, so it doesn't compete with interactive traffic. Load test at 5–10× peak before launch to confirm.

## Talking to the CTO

Frame it as sequencing rather than rejection:

1. **Netflix's path was monolith first.** They moved to microservices after hitting scaling and organizational limits that you don't have.
2. **The modular monolith preserves the option.** Clear module boundaries and an outbox/event pattern let you extract a service later when there's evidence, such as a module needing independent scaling, a different team owning it, or a different release cadence.
3. **Define extraction triggers up front**, for example: sustained load beyond what vertical scaling and replicas can handle, more than ~15–20 engineers stepping on each other, or a component with very different scaling or compliance needs (PDF rendering is the likeliest first candidate).
4. **Kafka:** revisit if you need high-throughput event streaming, replay, or many independent consumers. Until then, a job queue and the outbox cover it. If the CTO wants event-driven design, you can emit domain events internally now and swap the transport later.
5. **Kubernetes:** if the company has a platform team or a strategic reason (customer on-prem deployments, existing standardization), revisit. Otherwise, managed containers give 90% of the benefit at a fraction of the effort.

## Suggested phasing

1. **Months 0–3:** core domain (customers, invoices, line items, tax, PDFs, payments), tenancy, auth, audit log, CI/CD.
2. **Months 3–6:** recurring invoices, integrations/webhooks, reporting, SSO, load testing, and DR drills.
3. **Later:** extract a service only when a defined trigger is hit.

If you tell me the team's primary language and cloud provider, I can narrow this to concrete stack choices and sketch the data model.

### sdlc-application-architecture / arch-microservices-default / with skill / PASS

# Architecture recommendation: modular monolith, not microservices

## Decision
Build **one deployable modular monolith** with a separate worker process from the same codebase. Use **PostgreSQL** as the system of record and a Postgres-backed job queue and transactional outbox. Run it containerized on a managed platform (ECS/Fargate, Cloud Run, or similar). Skip Kubernetes and Kafka for now, and write down the conditions that would make us adopt them.

## Rationale (from the constraints, not from habit)
- **Load:** 50 rps peak across 200 tenants is small. One modest app instance and one Postgres primary handle it, and we'd run 2+ instances for availability, not capacity.
- **Team:** 4 engineers can't absorb the cost of running a service mesh, per-service pipelines, distributed tracing, and cross-service data consistency while also shipping product.
- **Domain:** Invoicing needs strong consistency: gapless per-tenant numbering, immutable issued invoices, and totals that match ledger entries. That is far easier with local ACID transactions than with sagas.
- **The Netflix comparison:** Microservices there solve an *organizational* scaling problem (thousands of engineers, independent deploy cadences) and a traffic scale many orders of magnitude above ours. We have neither problem, but we would pay all the costs.

## Structure
**Modules** (each owns its tables and exposes a narrow public interface):
1. Identity & Tenancy (users, roles, tenant config)
2. Customers (the tenants' clients)
3. Catalog (products, prices, tax rules)
4. Invoicing (drafts, issuing, numbering, credit notes)
5. Payments (payment records, reconciliation, provider adapters)
6. Documents & Delivery (PDF, email, webhooks)
7. Reporting (read models, exports)

**Inside each module:** hexagonal layout with domain, application (use cases), and adapters (HTTP, DB, payment provider, email, PDF).

**Dependency rules:**
- Domain depends on nothing.
- Application depends on domain and port interfaces.
- Adapters depend inward.
- Modules call each other only through public interfaces or in-process domain events, never another module's tables.
- Enforce this with architecture tests or lint rules (e.g., ArchUnit, dependency-cruiser, import-linter, depending on the stack) in CI.

**Data:** a single Postgres with a schema per module and `tenant_id` on every row, protected by row-level security. Use PITR backups, and add a read replica for reporting only if needed.

## Transactions, failure handling, background work
- **Issuing an invoice** is one DB transaction: validate, assign the next number (per-tenant sequence row with locking), freeze the invoice, and write an outbox event. PDF, email, and webhooks happen afterward, asynchronously.
- **Outbox + worker:** the worker polls with `SELECT … FOR UPDATE SKIP LOCKED`. Jobs are idempotent, retried with backoff, and dead-lettered after N attempts, with alerts.
- **API idempotency:** require idempotency keys on create/issue/payment endpoints.
- **External calls** (payment provider, email, tax) get timeouts, retries, and circuit breakers. They never sit inside a DB transaction.
- **Corrections** to issued invoices go through credit notes, never edits.

## Deployment
- One image, two process types: `web` (2+ instances behind a load balancer) and `worker` (1–2).
- Managed Postgres with multi-AZ, plus CI/CD with migrations (expand/contract), structured logs, metrics, and tracing via OpenTelemetry.
- Per-tenant rate limiting to contain noisy neighbors.

## Trade-offs
- **Gains:** fast delivery, simple debugging, atomic consistency, low operational cost, and easy local development.
- **Costs:** a single deploy unit means a bad release affects everything (mitigate with feature flags, canary or blue/green deploys, and fast rollback). Module boundaries rely on discipline and tooling, not the network. One database is a shared scaling ceiling, which is far from reachable at this load.

## ADRs to write
1. Modular monolith as the architectural style
2. Postgres as the single store, with multi-tenancy via RLS
3. Transactional outbox and Postgres-backed jobs instead of Kafka
4. Invoice numbering and immutability rules
5. Managed container platform instead of Kubernetes
6. Module boundary enforcement and public-interface rules

## Revisit triggers (what would change the answer)
- **Kafka:** multiple independent consumers needing replayable event streams, or sustained event volume beyond what Postgres queues handle (thousands per second).
- **Extract a service:** a module with a distinctly different scaling or runtime profile (e.g., PDF rendering or bulk import), a separate team owning it, or regulatory isolation needs.
- **Kubernetes:** many services, specialized scheduling needs, or a platform engineer on staff.
- **Team growth:** more than ~15–20 engineers with deployment contention.

Because modules already own their data and talk through interfaces, extraction later is a refactor, not a rewrite.

## Handling the CTO conversation
Frame it as "microservices-ready, not microservices-first." Present the revisit triggers as an explicit, agreed roadmap, so the decision is about timing and evidence rather than a rejection. The ADR gives the CTO measurable conditions under which we'd adopt the heavier stack.

## Next action
Draft ADRs 1, 3, and 5 and review them with the CTO. Then spike the vertical slice "create → issue → PDF → email" end to end.

## Validation
- Load test at 5× peak (250 rps) with realistic tenant mixes. Target p95 latency under 300 ms for API calls.
- Concurrency test: parallel invoice issuance per tenant yields gapless, unique numbers.
- Failure drills: kill a worker mid-job, take the email provider down, and verify retries, no duplicates, and alerting.
- Restore a Postgres backup to a point in time and measure RTO/RPO.
- Cross-tenant isolation tests in CI (RLS) and architecture tests that fail the build on forbidden module dependencies.

### sdlc-application-architecture / arch-microservices-default / baseline / PASS

# Recommendation: modular monolith on managed services

I'd push back on microservices + Kubernetes + Kafka for this workload. The load doesn't need them, and a team of 4 would pay heavily for them.

## Why not "what Netflix does"

- **Load:** 50 req/s peak is small. One modest app instance plus a Postgres database handles that with a lot of headroom. Netflix handles millions of req/s.
- **Why Netflix uses microservices:** they let thousands of engineers deploy independently. That's an organizational scaling problem, and you don't have it with 4 people.
- **The cost for you:**
  - Distributed transactions: an invoice, its ledger entries, and its tax calculation need to be consistent. In a monolith that's one DB transaction. Across services it becomes sagas and reconciliation.
  - Operations: Kubernetes and Kafka each need real expertise. Realistically that's 20-25% of your team's capacity going to platform work instead of product.
  - Debugging, local dev, contract versioning, and integration testing all get harder.
- **Risk:** invoicing is a correctness-critical domain. Simplicity is a feature.

## Proposed architecture

**Application:** one deployable codebase, split into strictly separated modules with explicit internal interfaces:
- Identity and tenancy (orgs, users, RBAC, SSO)
- Customers and contacts
- Catalog (products, prices, tax rules)
- Invoicing (drafts, issuing, credit notes, numbering)
- Payments and reconciliation
- Notifications (email, webhooks)
- Reporting and exports
- Integrations (accounting, ERP, payment providers)

Rules: modules talk only through their public interface, never into each other's tables. Enforce this in CI with a dependency-check tool.

**Runtime:**
- 2+ stateless app instances behind a load balancer (for availability, not capacity) on a managed container platform (ECS Fargate, Cloud Run, Azure Container Apps, or similar).
- A separate worker process from the same codebase for background jobs.

**Data:**
- Managed PostgreSQL with multi-AZ, point-in-time recovery, and tested restores. Add a read replica for reporting only if needed.
- Multi-tenancy: shared schema with `tenant_id` on every table, enforced with Postgres row-level security. 200 customers doesn't justify schema-per-tenant or DB-per-tenant, unless a few enterprise customers contractually demand isolation.
- Object storage (S3 or equivalent) for generated PDFs and attachments, with encryption and versioning.

**Async work (no Kafka):**
- Use a transactional outbox: write the event row in the same transaction as the business change, and workers process it.
- A Postgres-backed job queue, or SQS if you prefer managed, handles PDF generation, emails, webhooks with retries, scheduled recurring invoices, and accounting syncs.
- This gives you reliable at-least-once delivery. Make handlers idempotent.

**Cache:** none at first. Add Redis only if profiling shows a need (sessions, rate limiting).

## Invoicing-specific design points

- **Money:** integer minor units or decimal types plus an explicit currency. Never floats.
- **Immutability:** once issued, an invoice is immutable. Corrections happen via credit notes. Keep an append-only audit log.
- **Numbering:** gapless, sequential per tenant and per series where the law requires it. Allocate numbers at issue time inside a transaction with a per-tenant counter row lock.
- **Idempotency keys** on all mutating API endpoints, especially issue and payment operations.
- **Tax and compliance:** isolate tax logic in its own module. Check early whether your markets require e-invoicing (Peppol, Factur-X, and so on), since it affects the data model.
- **Webhooks:** signed, retried with backoff, with a delivery log customers can see.
- **Rate limiting** per tenant, to protect against one noisy customer.

## Operations

- CI/CD with automated tests and migrations, and zero-downtime deploys (expand/contract migrations).
- Observability: structured logs, metrics, tracing via OpenTelemetry, and error tracking. Alert on job queue depth, failed webhooks, and p95 latency.
- Security: SSO/SAML option for B2B customers, encryption at rest and in transit, secrets manager, least-privilege IAM, and dependency scanning. SOC 2 readiness will probably come up from customers.
- Environments: dev, staging, and prod, all provisioned with Terraform or similar.
- Cost estimate: likely low hundreds of dollars a month, versus several times that (plus engineer time) for a K8s + Kafka setup.

## Capacity sanity check

Even if 50 req/s were sustained, that's about 4.3M requests/day. With typical indexed queries at 5-20 ms each, one instance has plenty of capacity. Load test at 5-10x peak before launch to confirm.

## Making the CTO's path available later

You can offer the CTO a credible route rather than a flat no:

1. **Design for extraction:** module boundaries, the outbox event contract, and no cross-module table access mean any module can become a service later with limited rework.
2. **Define explicit triggers** for revisiting the decision:
   - **Extract a service:** a module needs very different scaling (for example PDF rendering or bulk imports), a different tech stack, or an independent team owns it.
   - **Adopt Kafka:** you need durable event streams with multiple independent consumers, replay, or sustained throughput well beyond what Postgres/SQS queues handle (think thousands of events/s).
   - **Adopt Kubernetes:** you're running many services, have a dedicated platform person, or need portability that your managed platform can't give.
3. **Revisit** at team size around 12-15 or at sustained load roughly 10x today's.

## Summary

Build a well-structured modular monolith on managed Postgres and a managed container platform, with an outbox and job queue for async work. This ships faster, is easier to keep correct, and costs less. It still leaves a clean path to services, Kafka, and Kubernetes if the business actually grows into needing them.

### sdlc-application-architecture / arch-microservices-default / with skill / PASS

# Architecture recommendation: modular monolith on managed services

## Decision
Build one deployable application, structured as a modular monolith with strict module boundaries. Use PostgreSQL as the system of record, and run a background worker from the same codebase as a second process. Deploy to a managed container platform (ECS/Fargate, Cloud Run, or similar) with at least 2 app instances, not self-managed Kubernetes. Use a transactional outbox in Postgres, not Kafka.

## Rationale
- **Load is small.** 50 rps at peak across 200 customers is well within what one modest instance and one Postgres database handle for CRUD-style workloads. Two instances give availability, not capacity.
- **Team size is the real constraint.** Four engineers can't staff per-service pipelines, observability, and on-call, plus Kubernetes and Kafka operations, while also shipping product. That operational cost would come straight out of feature delivery.
- **The domain needs strong consistency.** Invoicing needs gapless per-tenant numbering, immutable issued documents, and audit trails. These are easy with one ACID database and hard with distributed sagas and eventual consistency.
- **The Netflix comparison doesn't transfer.** Microservices there address organizational scaling (hundreds of teams) and extreme traffic. Neither applies here.

## Structure

**Modules** (each owns its tables and exposes a small public API):
- Identity & Tenancy
- Customers
- Catalog & Pricing
- **Invoicing** (core: drafts, issuing, numbering, credit notes)
- Tax
- Payments
- Documents (PDF rendering)
- Notifications
- Reporting
- Audit

**Dependency rules:**
- Modules call each other only through public interfaces or published domain events, never through another module's tables.
- Use a separate Postgres schema per module and no cross-schema joins in application code. Reporting reads through views or its own read models.
- Dependencies point inward: `api → application → domain ← adapters`. Use hexagonal ports and adapters only where there are real external edges: payment providers, tax engines, email, accounting exports, and storage.
- Enforce these rules with architecture tests in CI (ArchUnit, import-linter, or the equivalent for your stack), not just convention.

**Multi-tenancy:** shared schema with `tenant_id` on every table, backed by Postgres row-level security as a safety net.

## Transactions, failure handling, and jobs
- **Issuing an invoice is one DB transaction.** It covers the state change to `issued`, allocation of the tenant's number from a sequence table, the audit record, and an outbox row. After that the invoice is immutable, and corrections happen through credit notes.
- **Background jobs** (PDF generation, email, payment webhooks, accounting sync) are driven by the outbox and a Postgres-backed queue, which is simple and transactionally consistent. Use at-least-once delivery, idempotent handlers, exponential backoff, and a dead-letter table with an alert.
- **API idempotency keys** on all mutating endpoints, especially issue and payment.
- **External calls** (tax, payments) never happen inside the DB transaction. Use timeouts and circuit breakers, and record the outcome.
- **Money** is stored as integer minor units or fixed decimals with an explicit currency, never floats.

## Deployment
- 2+ stateless app instances behind a load balancer, plus 1 worker process.
- Managed Postgres with HA, point-in-time recovery, and tested restores.
- Object storage for PDFs, plus centralized logs, metrics, and tracing (OpenTelemetry).
- One CI/CD pipeline, with migrations run as a controlled step.

## Trade-offs
- **Gain:** one deploy, one debugging surface, local transactions, fast iteration, low ops cost.
- **Cost:** a shared release train, a shared failure domain (mitigated by the separate worker process), and discipline required to keep module boundaries from eroding.
- **Not chosen:** microservices, Kubernetes, Kafka. They add distributed-systems failure modes and operational load with no current benefit.

## Revisit triggers
Reconsider extraction only on measured evidence:
- A module needs independent scaling, for example PDF rendering saturating CPU. Extract it as a worker first.
- The team grows past roughly 12–15 engineers and deploy contention appears.
- Regulation requires isolating a data domain.
- Sustained load outgrows a vertically scaled primary plus read replicas.

Because the outbox and module events already exist, moving to a broker like Kafka later means changing the transport, not redesigning.

## Handling the CTO conversation
Frame this as "microservices-ready, not microservices-first." The module boundaries, events, and outbox preserve the option at near-zero cost, while avoiding a year of platform work before the first customer invoice. Propose the revisit triggers above as agreed, measurable criteria, so the decision isn't a permanent no.

## ADRs to write now
1. Modular monolith as the deployment architecture, with revisit triggers
2. PostgreSQL as the single system of record, with shared-schema multi-tenancy and RLS
3. Module boundary and dependency rules, enforced by CI tests
4. Transactional outbox and a Postgres-backed job queue, with an idempotency policy
5. Invoice immutability, numbering strategy, and credit-note corrections
6. Money and currency representation
7. Managed container platform instead of Kubernetes

## Next actions
1. Get the CTO to agree on the revisit triggers and write ADRs 1 and 2.
2. Run a short event-storming session to confirm module boundaries and ownership (roughly one module owner per engineer).
3. Build a thin vertical slice: create a draft, issue it (numbering plus outbox), render a PDF in the worker, and email it. Deploy it end to end.

## Validation
- **Load test** at 3–5× peak (150–250 rps) on the planned instance size. Expect p95 latency to hold and the DB to stay well below saturation.
- **Failure drills:** kill the worker mid-job, restart the app mid-issue, and replay duplicate requests and webhooks. Expect no duplicate or skipped invoice numbers and no lost emails.
- **Restore test:** recover Postgres from backup to a point in time.
- **Boundary tests** in CI fail on any cross-module access.
- **Tenant isolation tests** confirm no cross-tenant reads, including with RLS enabled.

### sdlc-identity-access-multitenancy / authz-ui-hiding / baseline / PASS

No, hiding the button is only a UX nicety, not authorization. Anyone can call `DELETE /api/projects/:id` directly with curl, the browser console, or a modified client, and `role` in the React app is client-side state the user can tamper with. The server has to enforce the rule.

## 1. UI (hide the button)

```tsx
function ProjectActions({ project, user }: Props) {
  const isAdmin = user.role === 'admin';

  return (
    <>
      {/* other actions */}
      {isAdmin && (
        <button onClick={() => deleteProject(project.id)}>
          Delete project
        </button>
      )}
    </>
  );
}
```

Take `user.role` from the authenticated session or `/me` response, not from something like localStorage that the user can edit. Even so, treat it purely as a display hint.

## 2. Server (the actual authorization)

Here's an Express-style example. The same idea applies to any framework.

```ts
app.delete('/api/projects/:id', requireAuth, async (req, res) => {
  const { userId, tenantId, role } = req.auth; // from verified session/JWT, never from the request body

  if (role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }

  // Tenant scoping: the project must belong to the caller's tenant
  const project = await db.project.findFirst({
    where: { id: req.params.id, tenantId },
  });
  if (!project) {
    return res.status(404).json({ error: 'Not found' });
  }

  await db.project.delete({ where: { id: project.id } });
  res.status(204).end();
});
```

## Multi-tenant points to check

- **Role is per tenant.** A user may be an admin in tenant A but a regular user in tenant B. Look up the role for the tenant that owns the resource, not a global `role` field.
- **Tenant scoping on every query.** Filtering by `tenantId` prevents an admin of one tenant from deleting another tenant's project by guessing IDs (an IDOR/BOLA vulnerability). Returning 404 rather than 403 for cross-tenant IDs avoids leaking which IDs exist.
- **Trust only server-verified identity.** Derive the role and tenant from the verified session or token, never from request parameters or headers the client controls.
- **Centralize the check.** Use a policy layer or middleware (e.g. `requireRole('admin')`, CASL, Oso, or a `can(user, 'delete', project)` function) so new endpoints don't forget it.
- **Defense in depth.** If you can, add database-level protection such as Postgres row-level security keyed on tenant.
- **Cover other paths to the same action.** Check GraphQL mutations, bulk-delete endpoints, background jobs, and admin or internal APIs.
- **Tests and audit logs.** Add tests that a non-admin gets 403, that an admin from another tenant gets 404, and that an admin of the right tenant succeeds. Log deletions with the actor and tenant.

In short, keep the UI check for a clean experience, but make the server check the real gate.

### sdlc-identity-access-multitenancy / authz-ui-hiding / with skill / PASS

# No, hiding the button is not authorization

Hiding the button is a UX nicety. Anyone can call `DELETE /api/projects/:id` directly with curl, devtools, or a replayed request, and `role` in the client is just data the user can alter. In a multi-tenant system there is a second risk: even an admin must only delete projects in their own tenant.

## Decision
Keep the UI hiding, but enforce authorization on the server, on every delete path.

## Rationale
- The UI is untrusted. The server is the only enforcement point.
- Role alone isn't enough. You need role **and** tenant scope: "admin of tenant A" must not delete tenant B's project (an IDOR/BOLA risk).
- Take the role and tenant from the verified session or token server-side, never from the request body or client-supplied headers.

## Implementation sketch

**Frontend (UX only):**
```tsx
{can('project:delete') && <DeleteProjectButton id={project.id} />}
```
Prefer a `can(permission)` helper over scattered `role !== 'admin'` checks, so the rule lives in one place.

**Backend (the real control):**
```ts
router.delete('/projects/:id', requireAuth, async (req, res) => {
  const { userId, tenantId, role } = req.auth;          // from verified session/JWT
  if (!hasPermission(role, 'project:delete')) return res.sendStatus(403);

  const result = await db.project.deleteMany({
    where: { id: req.params.id, tenantId }              // tenant scoping in the query
  });
  if (result.count === 0) return res.sendStatus(404);   // don't leak cross-tenant existence

  audit.log({ actor: userId, tenantId, action: 'project.delete', target: req.params.id });
  res.sendStatus(204);
});
```

Also check for other routes that can delete projects: bulk endpoints, GraphQL mutations, admin or internal APIs, background jobs, and tenant-deletion cascades.

## Trade-offs
- Returning 404 for cross-tenant IDs hides existence but makes debugging slightly harder. Log the real reason server-side.
- Centralized permission checks (middleware or policy layer) take more upfront work than inline `if` checks, but they prevent drift between routes.
- Consider soft delete with a retention window, since project deletion is destructive. This also helps with recovery if an admin account is compromised.

## Validation (negative tests)
1. A regular user calling `DELETE /projects/:id` directly gets **403**, and the project still exists.
2. An admin of tenant A deleting a tenant B project gets **404/403**, and the project is unchanged.
3. An unauthenticated request gets **401**.
4. A forged role (modified JWT payload, a `role: admin` field in the body or header) is rejected.
5. Every alternate delete path (bulk, GraphQL, internal) passes the same tests.
6. An audit record is written on success, and none on denied attempts (or a separate "denied" event, if you track those).
7. A UI test that the button is hidden for non-admins, as a secondary check only.

## Next action
Add the server-side permission and tenant-scoped delete first, write tests 1–4, then refactor the UI check into a shared `can()` helper.

### sdlc-identity-access-multitenancy / authz-ui-hiding / baseline / PASS

No, hiding the button is a UX nicety, not authorization. Anyone can call your API directly with curl, Postman, or the browser console, or edit client state to set `role = 'admin'`. The server must enforce the rule.

## 1. UI (the part you asked for)

```tsx
function ProjectActions({ project }: { project: Project }) {
  const { user } = useAuth();

  return (
    <>
      {/* other actions */}
      {user.role === 'admin' && (
        <button onClick={() => deleteProject(project.id)}>Delete project</button>
      )}
    </>
  );
}
```

Conditionally render the button rather than hiding it with CSS, so it isn't in the DOM at all. This is still only cosmetic.

## 2. Server-side enforcement (required)

Example in Express-style pseudocode:

```ts
app.delete('/api/projects/:id', requireAuth, async (req, res) => {
  const { userId, tenantId, role } = req.auth; // from verified session/JWT, NOT the request body

  if (role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }

  // Tenant scoping: the project must belong to the caller's tenant
  const result = await db.project.deleteMany({
    where: { id: req.params.id, tenantId },
  });

  if (result.count === 0) {
    return res.status(404).json({ error: 'Not found' });
  }
  res.status(204).end();
});
```

## Key points for a multi-tenant app

- **Derive identity and role on the server.** Take them from the verified session or token, never from a client-supplied field or header like `x-role`.
- **Check role and tenant.** An admin in tenant A must not be able to delete tenant B's project by guessing an ID (a classic IDOR). Always include `tenantId` in the query, or verify ownership first.
- **Return 404 vs 403 deliberately.** Returning 404 for cross-tenant resources avoids leaking that the ID exists.
- **Centralize the check.** Use middleware or a policy layer (e.g. `can(user, 'project:delete', project)`) so every destructive endpoint uses the same logic, and the UI can reuse the same permission definitions.
- **Defense in depth.** Consider database-level protections such as Postgres row-level security keyed on tenant, plus audit logging for deletes. For high-value data, consider soft-delete with a recovery window.
- **Test it.** Add API tests that a non-admin gets 403, an admin from another tenant gets 404, and an admin in the right tenant succeeds.

In short, hide the button for a better experience, and enforce the permission on the server for security.

### sdlc-identity-access-multitenancy / authz-ui-hiding / with skill / PASS

# No, hiding the button is not authorization

**Decision:** Keep the UI hiding as a UX nicety, but enforce authorization on the server for every delete path. Anyone can call `DELETE /projects/:id` directly with curl, the browser console, or a modified client, regardless of what React renders.

## Rationale
- **UI hiding is not a control.** The client is untrusted, and `role` in client state can be edited or bypassed.
- **Multi-tenancy adds a second check.** Being an admin isn't enough: the admin must be an admin **of the tenant that owns the project**. Without that check, an admin in tenant A could delete tenant B's project by guessing or enumerating IDs (an IDOR / cross-tenant flaw).
- **The check should be a business rule, not route glue.** Something like `can(actor, 'project:delete', project)` should be evaluated server-side and default to deny.

## What to implement
1. **Server-side check (the actual control).** In the delete handler or service layer:
   - Authenticate the caller and derive `userId` and `tenantId` from the session or token, never from the request body.
   - Load the project **scoped by tenant** (`WHERE id = :id AND tenant_id = :tenantId`). Return 404 if not found, so you don't leak existence across tenants.
   - Check that the actor's role in that tenant grants `project:delete`. Return 403 otherwise.
   - Prefer a permission (`project:delete`) over a raw `role === 'admin'` string so roles can evolve.
2. **Centralize it.** Use a policy function or middleware shared by all entry points (REST, GraphQL, background jobs, admin tools, bulk delete endpoints) rather than checking in one route.
3. **UI (secondary).** Hide or disable the button based on a permission the server returns (e.g., `can.deleteProject`), not a hardcoded `role !== 'admin'`, so UI and server don't drift.
4. **Audit.** Log who deleted what, in which tenant, and the outcome (including denied attempts). Consider soft delete with a retention window for recovery.
5. **Related surfaces.** Check that caches, search indexes, files, and queues for the project are also tenant-scoped and cleaned up properly on delete.

## Trade-offs
- Tenant-scoped queries and a policy layer cost a bit more upfront than a UI conditional, but they are the only thing that actually stops attacks.
- Returning 404 vs 403 for cross-tenant IDs: 404 leaks less; 403 is clearer for debugging within a tenant. Use 404 for cross-tenant and 403 for same-tenant insufficient permission.

## Validation (negative tests)
- Regular user in the correct tenant calls `DELETE /projects/:id` → **403**, project still exists.
- Admin of tenant A deletes a project in tenant B → **404/403**, project untouched.
- Unauthenticated request → **401**.
- Forged or tampered `role` or `tenantId` in the body, headers, or JWT payload (unsigned or modified) → rejected.
- Bulk or alternate endpoints (batch delete, GraphQL mutation, admin API) get the same denial tests.
- Positive case: tenant admin can delete their own tenant's project, and an audit record is written.
- UI test: button hidden for non-admins, but a regression test confirms the API still denies them when the call is made directly.

**Next action:** Add the server-side policy check and tenant-scoped lookup to the delete endpoint first, write the negative tests above, then wire the UI to a server-provided permission flag.

### sdlc-identity-access-multitenancy / authz-ui-hiding / baseline / PASS

No, hiding the button is a UX nicety, not authorization. Anyone can call `DELETE /api/projects/:id` directly with curl, the browser devtools, or a modified client, and the UI never gets a say. In a multi-tenant app, you also need to make sure an admin in tenant A can't delete tenant B's project.

## 1. UI: hide the button (fine, but cosmetic)

```tsx
function ProjectActions({ project }: { project: Project }) {
  const { user } = useAuth();

  return (
    <>
      {user.role === 'admin' && (
        <button onClick={() => deleteProject(project.id)}>Delete project</button>
      )}
    </>
  );
}
```

Treat `user.role` on the client as untrusted. It's only used to decide what to render.

## 2. Server: enforce authorization (required)

The role must come from the verified session or token on the server, never from a request body, header, or client-supplied field.

```ts
// Express-style example
function requireRole(role: 'admin') {
  return (req, res, next) => {
    if (!req.user) return res.status(401).end();
    if (req.user.role !== role) return res.status(403).end();
    next();
  };
}

app.delete('/api/projects/:id', requireAuth, requireRole('admin'), async (req, res) => {
  const result = await db.project.deleteMany({
    where: {
      id: req.params.id,
      tenantId: req.user.tenantId,   // tenant scoping
    },
  });

  if (result.count === 0) return res.status(404).end(); // not found *in this tenant*
  res.status(204).end();
});
```

Key points:

- **Role check on the endpoint**: return 403 for non-admins.
- **Tenant scoping in the query**: include `tenantId` in the `WHERE` clause, so an admin can't delete another tenant's project by guessing an ID (this is an IDOR/BOLA vulnerability otherwise).
- **Return 404, not 403, for cross-tenant IDs**, so you don't leak whether a resource exists.
- **Derive identity server-side** from the session or JWT, and re-check the role against your source of truth if roles can change while tokens are still valid.

## 3. Defense in depth (recommended for multi-tenant)

- **Database-level isolation**, such as Postgres Row-Level Security keyed on tenant ID, so a missed `WHERE` clause doesn't become a cross-tenant leak.
- **Centralized policy** (middleware, or a library like CASL or Casbin) so permissions aren't scattered across handlers.
- **Audit logging** for destructive actions: who, which tenant, which project, when.
- **Consider soft delete** or a confirmation step for destructive operations.
- **Tests**: a non-admin gets 403, an admin from another tenant gets 404, and an admin from the same tenant gets 204.

In short, the UI check makes the app look right, and the server check makes it be right. Ship both, but only the server check counts as authorization.

### sdlc-identity-access-multitenancy / authz-ui-hiding / with skill / PASS

# No, hiding the button is not authorization

**Decision:** Hide the button for UX, but enforce the delete rule on the server, on every path that can delete a project.

## Rationale
- Anyone can call `DELETE /api/projects/:id` directly with curl, devtools, or a replayed request. The UI is not a trust boundary.
- `role !== 'admin'` on the client reads state the client controls. A user can edit it in memory, and a stale or tampered token or store changes what the UI shows.
- In a multi-tenant system, "is admin" is not enough. You also need "admin **of the tenant that owns this project**". Without that check, an admin in tenant A can delete tenant B's project by guessing or enumerating an ID (an IDOR / cross-tenant bug).
- Other entry points may reach the same operation: GraphQL mutations, bulk endpoints, background jobs, admin tools, and internal APIs.

## What to implement
1. **Server-side check on the delete handler.** Resolve the caller's identity and tenant from the verified session or token, never from request body fields. Load the project scoped by tenant (`WHERE id = :id AND tenant_id = :callerTenant`). Then require the permission (e.g. `project:delete`), not a hard-coded role string.
2. **Explicit deny by default.** No permission means 403. If the project isn't in the caller's tenant, return 404 so you don't leak that it exists.
3. **Permissions, not role names, in the UI.** Have the API return the user's effective permissions, or a per-resource `canDelete` flag, and render the button from that. This keeps UI and server logic from drifting apart. It is still only a UX hint.
4. **Defense in depth on tenant isolation.** Consider row-level security or a tenant-scoped repository layer so a forgotten `tenant_id` filter can't cause a leak. Check caches, queues, files, and search indexes for the same scoping.
5. **Audit the action.** Log who deleted which project, in which tenant, and when. Consider soft delete with a retention window, and a confirmation or re-auth step for such a destructive action.

## Trade-offs
- Hiding the button costs almost nothing and avoids confusing users, but it adds no security.
- Per-resource `canDelete` flags add a little payload and server work, but they remove duplicated role logic in the client.
- Row-level security adds setup and testing overhead, but it protects against a whole class of missed-filter bugs.

## Next action
Add the permission and tenant check to the delete endpoint (and any other route that deletes projects). Then switch the React condition to use the server-provided permission.

## Validation (negative tests)
- A regular user calls `DELETE /projects/:id` for a project in their own tenant → **403**, and the project still exists.
- An admin of tenant A deletes a project in tenant B → **404/403**, and the project is unchanged.
- An unauthenticated request, or one with an expired or tampered token → **401**.
- A user with a modified client role (`role = 'admin'` set locally) → still **403**.
- The same checks against every alternate path (bulk delete, GraphQL, jobs).
- A positive test: an admin of the owning tenant can delete, and an audit record is written.
- A cross-tenant regression test in CI that iterates over destructive endpoints with a user from a different tenant.

### sdlc-observability-reliability / alert-noise / baseline / FAIL

I don't know your monitoring stack, so these are Prometheus/Alertmanager rules with PagerDuty routing. The metric and label names (`http_requests_total`, `status`, `job`, and so on) are assumptions to adjust.

## Prometheus alert rules

```yaml
groups:
  - name: service-paging
    rules:
      - alert: HighCPU
        expr: |
          100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))) > 60
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "CPU above 60% on {{ $labels.instance }}"
          description: "CPU is {{ $value | printf \"%.1f\" }}% for 5+ minutes."

      - alert: Http4xxDetected
        expr: |
          sum by (job) (increase(http_requests_total{status=~"4.."}[5m])) > 0
        for: 0m
        labels:
          severity: page
        annotations:
          summary: "4xx responses from {{ $labels.job }}"
          description: "{{ $value | printf \"%.0f\" }} 4xx responses in the last 5m."

      - alert: DeployHappened
        expr: |
          changes(kube_deployment_status_observed_generation{namespace="prod"}[5m]) > 0
        for: 0m
        labels:
          severity: page
        annotations:
          summary: "Deploy detected: {{ $labels.deployment }}"
```

The deploy rule assumes Kubernetes with kube-state-metrics. If you deploy another way, have your CI/CD emit a metric or send an event straight to PagerDuty instead.

## Alertmanager routing

```yaml
route:
  receiver: default
  routes:
    - matchers: ['severity="page"']
      receiver: pagerduty-oncall
      group_by: [alertname, job]
      group_wait: 30s
      repeat_interval: 4h

receivers:
  - name: default
  - name: pagerduty-oncall
    pagerduty_configs:
      - routing_key: <PAGERDUTY_INTEGRATION_KEY>
        send_resolved: true
```

## Caveats

Paging on all three conditions as written will likely cause alert fatigue:

- **Any 4xx:** these are usually client errors (bad requests, 404s from bots, expired tokens) and rarely need a human at 3am. Consider paging on a rate or ratio instead, such as `4xx / total > 5%` for 10m, or on specific codes like 401/403 spikes.
- **Every deploy:** a deploy is an event, not a fault. It's better as a Slack notification or a Grafana annotation. If you do want a page, route it with lower urgency (`severity="info"`) so it doesn't wake anyone.
- **CPU > 60%:** that's a fairly low threshold for a page. The `for: 5m` clause avoids paging on brief spikes, and you might page at 85–90% and warn at 60%.

If you tell me your stack (Datadog, CloudWatch, Grafana, and so on), I can rewrite these in that format.

### sdlc-observability-reliability / alert-noise / with skill / PASS

# Alert rules: what I'd change and why

**Decision:** I wouldn't page on any of the three triggers as written. Here is what I'd do with each, plus rules you can adapt. I had no repo access, so I assumed Prometheus/Alertmanager and common metric names (`http_requests_total`, `container_cpu_usage_seconds_total`). Swap in your own conventions.

| Your trigger | Problem | Replacement |
|---|---|---|
| CPU > 60% | 60% is normal headroom use and has no single expected action. It will page constantly. | Ticket on sustained high CPU. Page only on user-visible symptoms (latency or errors). |
| Any 4xx | 4xx are mostly client behavior (404s from bots, 401s from expired tokens). Paging on one is pure noise. | Ticket on a high 4xx ratio. Page only if a 4xx spike coincides with a deploy or a critical endpoint breaks. |
| Every deploy | A deploy is an event, not a failure. | Send it to a chat channel and a dashboard annotation. Page only if the SLO burns after a deploy. |

## Rules

```yaml
groups:
- name: service-slo
  rules:
  # PAGE: user-facing 5xx burn (fast burn, 2% of a 30d 99.9% budget in 1h)
  - alert: HighErrorBudgetBurn
    expr: |
      (sum(rate(http_requests_total{service="my-service",code=~"5.."}[5m]))
        / sum(rate(http_requests_total{service="my-service"}[5m]))) > (14.4 * 0.001)
      and
      (sum(rate(http_requests_total{service="my-service",code=~"5.."}[1h]))
        / sum(rate(http_requests_total{service="my-service"}[1h]))) > (14.4 * 0.001)
    for: 2m
    labels: {severity: page}
    annotations:
      summary: "Fast error-budget burn on my-service"
      runbook_url: "<link>/runbooks/high-error-burn"

  # PAGE: latency SLO breach
  - alert: HighLatencyP99
    expr: |
      histogram_quantile(0.99,
        sum by (le) (rate(http_request_duration_seconds_bucket{service="my-service"}[5m]))) > 1
    for: 10m
    labels: {severity: page}
    annotations:
      runbook_url: "<link>/runbooks/high-latency"

  # PAGE: bad deploy (errors rising shortly after a release)
  - alert: PostDeployRegression
    expr: |
      (time() - max(deploy_timestamp_seconds{service="my-service"})) < 1800
      and
      (sum(rate(http_requests_total{service="my-service",code=~"5.."}[5m]))
        / sum(rate(http_requests_total{service="my-service"}[5m]))) > 0.02
    for: 3m
    labels: {severity: page}
    annotations:
      summary: "Error rate >2% within 30m of deploy; consider rollback"
      runbook_url: "<link>/runbooks/rollback"

  # TICKET: sustained CPU
  - alert: SustainedHighCPU
    expr: |
      avg(rate(container_cpu_usage_seconds_total{pod=~"my-service.*"}[5m]))
        / avg(kube_pod_container_resource_limits{resource="cpu",pod=~"my-service.*"}) > 0.8
    for: 30m
    labels: {severity: ticket}
    annotations:
      summary: "CPU >80% of limit for 30m; review capacity or autoscaling"

  # TICKET: elevated 4xx ratio on non-404 codes
  - alert: ElevatedClientErrors
    expr: |
      sum(rate(http_requests_total{service="my-service",code=~"4..",code!="404"}[15m]))
        / sum(rate(http_requests_total{service="my-service"}[15m])) > 0.05
    for: 30m
    labels: {severity: ticket}
```

**Deploy notification (non-paging):** have CI/CD post to a chat channel and create a Grafana annotation. Don't route it through Alertmanager's pager receiver.

Routing: `severity=page` goes to the on-call receiver and `severity=ticket` goes to the ticket or chat receiver.

## Trade-offs
- Fewer pages means a slow CPU creep won't wake anyone. The ticket alert plus saturation signals (throttling, queue depth) cover that.
- The post-deploy rule needs a `deploy_timestamp_seconds` metric emitted by your pipeline.
- If a specific endpoint's 4xx truly matters (for example, a payments 403 or 422 spike), add a per-endpoint rule for it rather than alerting on all 4xx.

## Next actions
1. Confirm your real SLOs (availability and latency targets) and adjust the thresholds above.
2. Write the runbooks the alerts link to, each with a first action, such as rollback, scale out, or check a dependency.
3. Emit the deploy marker metric from CI/CD.

## Validation
- Backtest the expressions against the last 30 days and count how many pages each would have produced. Target a handful per week at most, each with a clear action.
- Run `promtool check rules` and `promtool test rules` with synthetic series.
- Fire a test alert in staging to confirm the routing.
- After two weeks, review each page. Demote or delete any that didn't need a human.

If you tell me your stack (Datadog, CloudWatch, etc.) and your SLO targets, I can convert these to your format with real numbers.

### sdlc-observability-reliability / alert-noise / baseline / FAIL

I don't know your stack, so I've assumed Prometheus + Alertmanager + PagerDuty on Kubernetes. The metric names and labels are placeholders to adjust. The same logic ports to Datadog, CloudWatch, and others.

## Prometheus rules (`service-alerts.yml`)

```yaml
groups:
  - name: service-paging
    rules:
      - alert: HighCPU
        expr: |
          sum by (namespace, pod) (rate(container_cpu_usage_seconds_total{container!="", namespace="my-ns"}[5m]))
          /
          sum by (namespace, pod) (kube_pod_container_resource_limits{resource="cpu", namespace="my-ns"})
          > 0.60
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "CPU above 60% on {{ $labels.pod }}"
          description: "CPU usage is {{ $value | humanizePercentage }} of limit for 5m."

      - alert: Http4xxDetected
        expr: |
          sum by (service) (increase(http_requests_total{service="my-service", status=~"4.."}[1m])) > 0
        for: 0m
        labels:
          severity: page
        annotations:
          summary: "4xx responses from {{ $labels.service }}"
          description: "{{ $value }} 4xx responses in the last minute."

      - alert: DeployHappened
        expr: |
          changes(kube_deployment_status_observed_generation{namespace="my-ns", deployment="my-service"}[5m]) > 0
        for: 0m
        labels:
          severity: page
        annotations:
          summary: "Deploy detected for {{ $labels.deployment }}"
```

## Alertmanager routing

```yaml
route:
  receiver: default
  routes:
    - matchers: [ severity="page" ]
      receiver: pagerduty-oncall
      group_by: [alertname, service]
      group_wait: 30s
      repeat_interval: 1h

receivers:
  - name: pagerduty-oncall
    pagerduty_configs:
      - routing_key: <PAGERDUTY_INTEGRATION_KEY>
        send_resolved: true
  - name: default
```

## Things to check before enabling

- **Deploy detection:** the `observed_generation` approach needs kube-state-metrics. If you deploy another way, emit a deploy event or counter from CI/CD and alert on that instead.
- **4xx metric:** change `http_requests_total` and `status` to match your instrumentation. `increase(...) > 0` fires on a single request, so one 404 from a bot will page someone.
- **CPU:** if pods have no CPU limits, the denominator is empty and the rule never fires. Use node-level or request-based ratios instead.

## Noise warning

Paging on every deploy and on any single 4xx will likely cause alert fatigue within days. Consider these adjustments:

- **Deploys:** send them to Slack, or make them a `severity: info` notification rather than a page. Page only if a deploy is followed by elevated errors.
- **4xx:** page on a rate or ratio (e.g. 4xx > 5% of requests for 5m), or exclude expected codes like 404 and 401.
- **CPU:** the `for: 5m` already filters short spikes. Tune it to your traffic pattern.

I can adapt these to a different tool (Datadog, Grafana, CloudWatch) or add the softer thresholds if you tell me your stack.

### sdlc-observability-reliability / alert-noise / with skill / PASS

# Alert rules (revised from your request)

I'd push back on paging for those three signals as stated. Each one would page with no clear action, which produces alert fatigue and makes real pages easier to ignore. Below is what I'd implement instead, and what each of your three triggers becomes.

| Your trigger | Problem | Replacement |
|---|---|---|
| CPU > 60% | 60% is normal headroom use, with no user impact | Ticket on sustained high CPU. Page only on user-visible symptoms (errors, latency) or near-saturation |
| Any 4xx | Mostly client behavior (bad input, expired tokens, bots), so there is nothing for on-call to fix | Ticket on anomalous 4xx ratios. Page on 5xx SLO burn |
| Every deploy | An event, not a fault | Dashboard annotation and chat notification. Page only if a post-deploy regression is detected |

I'm assuming Prometheus/Alertmanager and the metric names `http_requests_total{code}`, `http_request_duration_seconds_bucket`, and `container_cpu_usage_seconds_total`. Adjust them to your stack, since I can't see your repo.

## Pages (action required now)

```yaml
groups:
- name: slo-pages
  rules:
  # Availability SLO 99.9%: fast burn (budget gone in ~2 days)
  - alert: HighErrorBudgetBurn
    expr: |
      (sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) > (14.4 * 0.001)
      and
      (sum(rate(http_requests_total{code=~"5.."}[1h])) / sum(rate(http_requests_total[1h]))) > (14.4 * 0.001)
    for: 2m
    labels: {severity: page}
    annotations:
      summary: "5xx error budget burning fast"
      runbook_url: "<link>/runbooks/high-5xx"

  # Latency SLO: p99 < 500ms
  - alert: HighLatencyP99
    expr: |
      histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m]))) > 0.5
    for: 10m
    labels: {severity: page}
    annotations:
      runbook_url: "<link>/runbooks/latency"

  # CPU only pages when saturated AND users are affected
  - alert: CPUSaturationWithLatency
    expr: |
      avg(rate(container_cpu_usage_seconds_total{container="app"}[5m])
          / on(pod) group_left kube_pod_container_resource_limits{resource="cpu",container="app"}) > 0.9
      and
      histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m]))) > 0.5
    for: 10m
    labels: {severity: page}

  # Deploy-related page: regression right after a release
  - alert: PostDeployRegression
    expr: |
      (time() - max(deploy_timestamp_seconds) < 1800)
      and
      (sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.02)
    for: 3m
    labels: {severity: page}
    annotations:
      summary: "Error rate >2% within 30m of deploy. Consider rollback."
```

## Tickets (deferred work, no page)

```yaml
- name: ticket-alerts
  rules:
  - alert: SustainedHighCPU
    expr: |
      avg(rate(container_cpu_usage_seconds_total{container="app"}[5m])
          / on(pod) group_left kube_pod_container_resource_limits{resource="cpu",container="app"}) > 0.6
    for: 1h
    labels: {severity: ticket}
    annotations:
      summary: "CPU >60% for 1h. Review capacity or autoscaling targets."

  - alert: Elevated4xxRatio
    expr: |
      sum(rate(http_requests_total{code=~"4.."}[15m])) / sum(rate(http_requests_total[15m])) > 0.10
    for: 30m
    labels: {severity: ticket}

  - alert: AuthFailureSpike   # 401/403 anomaly, possible abuse or broken client
    expr: |
      sum(rate(http_requests_total{code=~"401|403"}[10m]))
      > 3 * sum(rate(http_requests_total{code=~"401|403"}[10m] offset 1d))
    for: 15m
    labels: {severity: ticket}
```

## Deploys (notification, not alert)

- Emit a `deploy_timestamp_seconds` metric and a Grafana annotation from the CI/CD pipeline on each release.
- Post to a `#deploys` channel with version, author, and a link to the dashboard.
- No paging. The `PostDeployRegression` rule above covers the case where a deploy goes wrong.

## Trade-offs

- **Fewer pages, slightly slower detection** of gradual issues. Multi-window burn rates keep this small.
- **Thresholds are starting points.** The 99.9% SLO, 500ms p99, and 10%/2% ratios are placeholders. Replace them with your real SLOs.
- If you truly want a page on any 4xx, I'd need to know what action on-call would take. If there is one (for example, a specific endpoint that should never return 4xx), scope the rule to that endpoint.

## Validation

1. Backtest each expression against the last 30 days in Prometheus and count how many times it would have fired.
2. Confirm every page rule has a runbook link and a clear first action.
3. Trigger a synthetic 5xx burst in staging and verify routing: `severity=page` goes to the pager and `severity=ticket` goes to the ticket queue.
4. Review after two weeks: any page with no action taken gets tuned or demoted.

**Next action:** share your SLO targets and metric names, and I'll tailor the expressions and the Alertmanager routing config.

### sdlc-observability-reliability / alert-noise / baseline / PASS

I don't know your monitoring stack, so these are Prometheus + Alertmanager + PagerDuty rules. Metric and label names are assumptions you'll need to match to your setup.

## Prometheus rules (`alerts.yml`)

```yaml
groups:
  - name: service-paging
    rules:
      - alert: HighCPU
        expr: |
          100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))) > 60
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "CPU above 60% on {{ $labels.instance }}"
          description: "CPU has been {{ $value | printf \"%.1f\" }}% for 5m."

      - alert: Http4xxDetected
        expr: |
          sum by (service) (increase(http_requests_total{status=~"4.."}[5m])) > 0
        for: 0m
        labels:
          severity: page
        annotations:
          summary: "4xx responses on {{ $labels.service }}"
          description: "{{ $value | printf \"%.0f\" }} 4xx responses in the last 5m."

      # Kubernetes example: fires when a Deployment's generation changes (rollout started)
      - alert: DeployHappened
        expr: |
          changes(kube_deployment_status_observed_generation[10m]) > 0
        for: 0m
        labels:
          severity: page
        annotations:
          summary: "Deploy detected for {{ $labels.deployment }}"
```

If you're not on Kubernetes, don't use a metric for deploys. Have your CI/CD pipeline send the event directly, for example with the PagerDuty Events API v2 at the end of the deploy job:

```bash
curl -X POST https://events.pagerduty.com/v2/enqueue \
  -H 'Content-Type: application/json' \
  -d '{
    "routing_key": "'"$PD_ROUTING_KEY"'",
    "event_action": "trigger",
    "payload": {
      "summary": "Deploy: '"$SERVICE"' '"$VERSION"'",
      "source": "ci",
      "severity": "info"
    }
  }'
```

## Alertmanager routing (`alertmanager.yml`)

```yaml
route:
  receiver: default
  routes:
    - matchers: [severity="page"]
      receiver: pagerduty-oncall
      group_by: [alertname, service]
      group_wait: 30s
      repeat_interval: 1h

receivers:
  - name: default
  - name: pagerduty-oncall
    pagerduty_configs:
      - routing_key_file: /etc/alertmanager/secrets/pd_routing_key
```

## Things to consider before enabling

- **Any 4xx will page constantly.** Bots, expired tokens, bad client input, and 404s on scanners all produce 4xx. Consider a rate or ratio threshold (e.g. 4xx > 5% of requests for 5m), or exclude 401/404, or page only on 4xx you consider abnormal for your service.
- **Deploys aren't failures.** Paging a human on every deploy will cause alert fatigue and get the on-call to ignore pages. A Slack notification or a PagerDuty low-urgency event is usually better, with a page only if a deploy is followed by elevated errors or latency.
- **CPU at 60%** is fairly low for many workloads. The `for: 5m` clause avoids paging on brief spikes, but you may want to tune it, or use a higher paging threshold with 60% as a warning.

If you tell me your stack (Datadog, CloudWatch, Grafana Alerting, etc.), I can rewrite these for it.

### sdlc-observability-reliability / alert-noise / with skill / PASS

# Alert rules: what I'd ship instead of the three requested

I haven't seen your stack, so I assumed Prometheus/Alertmanager with common metric names (`http_requests_total`, `http_request_duration_seconds_bucket`, `node_cpu_seconds_total`). Adjust names and labels to match yours.

## Decision

I'd implement all three signals, but only one of them should page by default.

| Requested | Proposed | Why |
|---|---|---|
| Page on CPU > 60% | Ticket at 60% sustained; page only at saturation with user impact | 60% is healthy headroom, with no action to take. Paging on it trains people to ignore pages. |
| Page on any 4xx | Ticket on an abnormal 4xx ratio; page only if a critical journey is failing | 4xx is mostly client behavior (404 from bots, 401 from expired tokens). One 4xx has no action. |
| Page on deploy | Notify a channel and annotate dashboards; page only on post-deploy SLO burn | A deploy is an event, not a failure. Someone should be paged when it breaks something. |

## Rules

```yaml
groups:
- name: slo-pages
  rules:
  # PAGE: fast burn of 99.9% availability SLO (5xx = server fault)
  - alert: HighErrorBudgetBurn
    expr: |
      (
        sum(rate(http_requests_total{job="my-service",code=~"5.."}[5m]))
        / sum(rate(http_requests_total{job="my-service"}[5m])) > 14.4 * 0.001
      ) and (
        sum(rate(http_requests_total{job="my-service",code=~"5.."}[1h]))
        / sum(rate(http_requests_total{job="my-service"}[1h])) > 14.4 * 0.001
      )
    for: 2m
    labels: {severity: page}
    annotations:
      summary: "Fast error-budget burn on my-service"
      runbook_url: "https://<runbooks>/my-service/high-error-burn"

  # PAGE: p99 latency on a critical journey
  - alert: CriticalLatencySLOBreach
    expr: |
      histogram_quantile(0.99,
        sum by (le) (rate(http_request_duration_seconds_bucket{job="my-service",route="/checkout"}[5m]))) > 1.5
    for: 10m
    labels: {severity: page}
    annotations:
      runbook_url: "https://<runbooks>/my-service/latency"

- name: capacity
  rules:
  # TICKET: CPU above 60% sustained (capacity planning)
  - alert: CPUHighSustained
    expr: avg(1 - rate(node_cpu_seconds_total{mode="idle",job="my-service"}[5m])) > 0.60
    for: 6h
    labels: {severity: ticket}
    annotations:
      summary: "CPU >60% for 6h: review scaling/capacity"

  # PAGE: CPU saturated AND users affected
  - alert: CPUSaturationWithImpact
    expr: |
      avg(1 - rate(node_cpu_seconds_total{mode="idle",job="my-service"}[5m])) > 0.90
      and
      histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket{job="my-service"}[5m]))) > 1.5
    for: 10m
    labels: {severity: page}
    annotations:
      runbook_url: "https://<runbooks>/my-service/cpu-saturation"

- name: client-errors
  rules:
  # TICKET: abnormal 4xx ratio, excluding noisy codes
  - alert: Elevated4xxRatio
    expr: |
      sum(rate(http_requests_total{job="my-service",code=~"4..",code!~"401|404"}[15m]))
      / sum(rate(http_requests_total{job="my-service"}[15m])) > 0.05
    for: 30m
    labels: {severity: ticket}

  # PAGE: 4xx surge on a critical endpoint right after a deploy (likely a contract break)
  - alert: Post​DeployClientErrorSurge
    expr: |
      (
        sum(rate(http_requests_total{route="/checkout",code=~"4.."}[5m]))
        / sum(rate(http_requests_total{route="/checkout"}[5m])) > 0.20
      )
      and on() (time() - max(deploy_timestamp_seconds{job="my-service"}) < 3600)
    for: 5m
    labels: {severity: page}

- name: deploys
  rules:
  # NOTIFY (not page): record every deploy
  - alert: DeployOccurred
    expr: changes(deploy_timestamp_seconds{job="my-service"}[5m]) > 0
    labels: {severity: info}
```

Alertmanager routing:

```yaml
route:
  receiver: slack-deploys
  routes:
  - matchers: [severity="page"]
    receiver: pagerduty-oncall
  - matchers: [severity="ticket"]
    receiver: ticket-queue
  - matchers: [severity="info"]
    receiver: slack-deploys
```

Also emit a deploy annotation from CI/CD, such as a Grafana annotation, so graphs show deploy markers.

## Trade-offs

- **Less noise, slower detection of slow problems.** CPU creep surfaces as a ticket, not a page. That's intended, but check that the ticket queue is actually triaged.
- **Burn-rate alerts need a defined SLO.** I assumed 99.9% availability and a 1.5s p99 on `/checkout`. Replace these with your real targets.
- **Excluding 401/404 can hide real problems** such as a broken auth flow. The post-deploy critical-endpoint rule covers part of that.

## Next actions

1. Confirm your SLOs, critical journeys, and monitoring stack, and I'll adapt the rules.
2. Add a runbook for each paging alert, covering first checks, rollback criteria, and owner.
3. Emit `deploy_timestamp_seconds` from your pipeline.

## Validation

- Replay the last 30–90 days of metrics (`promtool test rules` or a backtest) and count how many pages each rule would have produced. Aim for every page to be actionable.
- Trigger each paging alert in staging, using load for CPU/latency and fault injection for 5xx, and confirm routing and runbook links.
- After two weeks, review the pages. Tune or demote any that ended with "no action taken".

If you still want the literal versions, such as page at CPU > 60%, change the `severity` label to `page`. I'd advise against it, because the first busy afternoon will page someone for nothing.

### sdlc-prd-requirements / prd-vague-verbs / baseline / PASS

# Search Feature Requirements

*Where the PM's wording was vague, I've proposed concrete, testable targets. These numbers are placeholders to confirm with the PM and engineering, not agreed values.*

## 1. Performance

- **FR-1.1** Search results return within **300 ms at p95** and **800 ms at p99**, measured server-side under expected peak load.
- **FR-1.2** Type-ahead/autosuggest suggestions appear within **150 ms at p95** of a keystroke (after debounce).
- **FR-1.3** The UI shows a loading indicator if results take longer than 500 ms.
- **FR-1.4** Performance targets hold at the projected peak concurrent query volume (to be specified) without degradation.

## 2. Filtering

- **FR-2.1** Users can filter results by multiple attributes at once (e.g., category, price range, availability, rating, brand, date). The final attribute list is to be defined per product catalog.
- **FR-2.2** Filters combine with AND logic across different attributes; multi-select within a single attribute uses OR logic.
- **FR-2.3** Each filter option displays the count of matching results, updated as other filters change.
- **FR-2.4** Applied filters are visible, individually removable, and clearable with a single "Clear all" action.
- **FR-2.5** Filter state is reflected in the URL so filtered searches can be shared, bookmarked, and restored via browser back/forward.
- **FR-2.6** Users can sort results (e.g., relevance, price, newest, rating) in combination with filters.
- **FR-2.7** Applying or changing a filter updates results without a full page reload.

## 3. Error Handling

- **FR-3.1** If the search service fails or times out, the user sees a clear, non-technical message and a retry option. No raw errors or stack traces are exposed.
- **FR-3.2** Zero-result searches show helpful guidance: spelling suggestions, relaxed-filter suggestions, and popular or related items.
- **FR-3.3** Invalid or malicious input (empty queries, overlong strings, special characters, injection attempts) is validated and sanitized without breaking the page.
- **FR-3.4** If a non-critical component fails (e.g., suggestions or facet counts), core search results still display.
- **FR-3.5** All search errors are logged with enough context (query, filters, error type, request ID) to diagnose, and alerts trigger when the error rate exceeds a defined threshold.
- **FR-3.6** Search is available at **99.9%** uptime (target to be confirmed).

## 4. Conversion Improvement

- **FR-4.1** Results are ranked by relevance, with support for typo tolerance, synonyms, and partial matching.
- **FR-4.2** Each result shows the information needed to decide (image, title, price, availability) and links directly to the item page.
- **FR-4.3** The search experience is fully usable on mobile and meets WCAG 2.1 AA accessibility standards.
- **FR-4.4** Search events are instrumented: queries, filter usage, result clicks, zero-result rate, add-to-cart, and purchase, attributed to the originating search.
- **FR-4.5** The feature supports A/B testing of ranking and UI changes.
- **FR-4.6** Success is measured against a baseline. Proposed metrics: search-to-purchase conversion rate, search click-through rate, and zero-result rate. Target improvement (e.g., **+X%** over baseline) is to be set by the PM.

## 5. Open Items to Confirm

- Exact performance thresholds and peak load assumptions
- Final list of filterable attributes
- Conversion baseline and target uplift
- Uptime/SLA target
- Scope of data covered by search (products only, or also content/help pages)

### sdlc-prd-requirements / prd-vague-verbs / with skill / PASS

# Search Feature Requirements (Draft v0.1)

All numeric targets below are **proposed defaults**, tagged `[A]` (assumption), because the PM's brief gave no numbers. Each needs confirmation by its owner (see Assumptions and Open Questions).

## Goal
Help users find relevant items quickly so more search sessions end in a conversion.

## Scope
- In: keyword search, filtering, result display, error and empty states, search analytics events.
- Out (non-goals, `[A]`): personalization or ML ranking, voice or image search, search-as-you-type suggestions, and admin tooling for synonyms.

## Requirements

### Performance (replaces "fast")
- **SRCH-1:** Search results return in ≤ 500 ms at p95 and ≤ 1.5 s at p99, measured server-side at the expected peak load. `[A]`
- **SRCH-2:** Applying or removing a filter updates results in ≤ 500 ms at p95. `[A]`
- **SRCH-3:** The UI shows a loading indicator if results take longer than 300 ms. `[A]`

### Filters (replaces "support many filters")
- **SRCH-4:** Users can apply filters from this initial set: `[category, price range, availability, rating, …]` (**list TBD, owner: PM**).
- **SRCH-5:** Multiple filters combine with AND across filter types. Multiple values within one type combine with OR. `[A]`
- **SRCH-6:** The result count and the list of applied filters are visible, and each filter can be removed individually or all at once.
- **SRCH-7:** Filter state is reflected in the URL so a filtered search can be shared and restored with the back button. `[A]`
- **SRCH-8:** Filter options that would produce zero results are shown disabled or with a count of 0. `[A]`

### Error handling (replaces "handle errors gracefully")
- **SRCH-9:** If the search service fails or times out (> 5 s), the user sees a plain-language error message with a Retry action. No stack traces or raw error codes are shown.
- **SRCH-10:** The user's query and applied filters are preserved after an error.
- **SRCH-11:** A query with no matches shows a "no results" state that names the query and offers at least one next step (remove filters, check spelling, browse categories). `[A]`
- **SRCH-12:** Empty or whitespace-only queries do not call the backend. The UI prompts the user to enter a term.
- **SRCH-13:** Special characters and queries longer than 200 characters are sanitized or rejected with a message. They never cause a server error. `[A]`
- **SRCH-14:** Every failure is logged with a request ID, and an alert fires if the search error rate exceeds 1% over 5 minutes. `[A]`

### Conversion (replaces "improve conversion")
- **SRCH-15:** Emit analytics events for: search submitted, results viewed, filter applied, result clicked, no-results shown, error shown, and conversion (add-to-cart or equivalent) attributed to a search session.
- **SRCH-16:** Success target: search-to-conversion rate improves by ≥ X% relative to baseline within N weeks of launch, validated by A/B test. **X, N, and the definition of "conversion" are TBD (owner: PM).**
- **SRCH-17:** Guardrail metrics: zero-result rate does not rise above baseline, and p95 latency stays within SRCH-1.

## BDD Examples

```gherkin
Scenario: Filtered search returns quickly
  Given a catalog of production size
  When the user searches "red shoes" and applies price "$20–$50"
  Then results matching both appear within 500 ms (p95)
  And the applied filters are shown and removable

Scenario: Backend failure
  Given the search service is returning errors
  When the user submits "red shoes"
  Then a friendly error message with a Retry button is shown
  And the query "red shoes" remains in the search box

Scenario: No results
  When the user searches "xqzzv"
  Then a "no results for 'xqzzv'" message is shown with suggested next steps
```

## Assumptions, Open Questions, Owners

| ID | Type | Item | Owner |
|---|---|---|---|
| A1 | Assumption | Latency targets in SRCH-1 to 3 are acceptable | Eng lead / PM |
| A2 | Assumption | Filter combination logic (SRCH-5) | PM / UX |
| Q1 | Open question | Which filters are in the initial release? | PM |
| Q2 | Open question | Definition of "conversion" and the baseline rate | PM / Analytics |
| Q3 | Open question | Target uplift (X%) and measurement window (N weeks) | PM |
| Q4 | Open question | Expected peak query load and catalog size | Eng lead |
| D1 | Dependency | Analytics pipeline and A/B testing capability | Analytics / Platform |
| D2 | Dependency | Search backend or index supports the chosen filter fields | Eng lead |

## Next Action
Confirm Q1 to Q4 with the PM. Until then, SRCH-4 and SRCH-16 remain blocked, and the rest can proceed to design and estimation.

## Validation
Each requirement maps to a testable check: load tests for SRCH-1 to 3, fault injection for SRCH-9 to 14, E2E tests for the filter behavior, and an A/B experiment for SRCH-16.

### sdlc-prd-requirements / prd-vague-verbs / baseline / PASS

# Search Feature Requirements

*Where the PM's input gave no specific numbers, I've proposed placeholder targets in [brackets]. Confirm or adjust them with the PM and engineering before sign-off.*

## 1. Performance
- **FR-1.1** Search results return within [300 ms] at p95 and [800 ms] at p99 under normal load.
- **FR-1.2** Type-ahead suggestions appear within [150 ms] of a keystroke (debounced).
- **FR-1.3** Performance targets hold at [N] concurrent users and a catalog of [N] items.
- **FR-1.4** Applying or removing a filter updates results within [500 ms] without a full page reload.

## 2. Search Functionality
- **FR-2.1** Users can search by free-text keyword across [name, description, category, SKU, tags].
- **FR-2.2** Results are ranked by relevance by default.
- **FR-2.3** Search tolerates minor typos and handles common synonyms and plurals.
- **FR-2.4** Results are paginated (or infinitely scrolled) with a total result count shown.
- **FR-2.5** Users can sort results by [relevance, price, newest, rating].

## 3. Filtering
- **FR-3.1** Users can filter by [category, price range, brand, rating, availability, date, location], with the final list defined per product.
- **FR-3.2** Multiple filters can be combined (AND across filter types, OR within a single filter type).
- **FR-3.3** Each filter option shows the number of matching results, and options that would yield zero results are disabled or flagged.
- **FR-3.4** Active filters are clearly displayed and can be removed individually or cleared all at once.
- **FR-3.5** Filter and query state is reflected in the URL so searches can be shared and bookmarked, and the back button works as expected.

## 4. Error Handling and Resilience
- **FR-4.1** If a search has no results, show a helpful empty state with suggestions (spell-correction, broader filters, popular items).
- **FR-4.2** If the search service fails or times out, show a clear, non-technical error message with a retry option. Never show a blank page or raw error.
- **FR-4.3** Invalid or malicious input (special characters, overlong queries, injection attempts) is sanitized and handled safely.
- **FR-4.4** Where possible, degrade gracefully (e.g., fall back to basic search if filters or suggestions are unavailable).
- **FR-4.5** All errors are logged with enough context for diagnosis, and alerts fire when the error rate exceeds [X%].

## 5. Conversion Optimization
- **FR-5.1** Results display the information needed to decide (image, title, price, availability, rating) and link directly to the item or allow a quick action such as add to cart.
- **FR-5.2** Search relevance can be tuned (boosting, merchandising rules) without a code deployment.
- **FR-5.3** The system supports A/B testing of ranking and layout changes.
- **FR-5.4** Analytics capture searches, zero-result queries, filter usage, click-through, and search-to-purchase conversion.
- **FR-5.5** Recent searches and popular or recommended queries are offered to users.

## 6. Non-Functional Requirements
- **NFR-1** Search is usable on mobile and desktop and meets WCAG [2.1 AA] (keyboard navigation, screen reader support).
- **NFR-2** Availability target of [99.9%] for the search service.
- **NFR-3** Search index freshness: catalog changes appear in results within [N minutes].
- **NFR-4** Search data handling complies with applicable privacy regulations (e.g., GDPR/CCPA) for stored query history.

## 7. Success Metrics
| Metric | Target |
|---|---|
| Search p95 latency | [≤ 300 ms] |
| Search error rate | [< 0.5%] |
| Zero-result rate | [reduce by X%] |
| Search click-through rate | [increase by X%] |
| Search-to-purchase conversion | [increase by X% vs. baseline] |

## Open Items to Confirm
1. The exact filter list and which are launch-critical (MVP) vs. later.
2. Baseline conversion and latency measurements, so targets can be set against them.
3. Catalog size and expected traffic, to validate the performance targets.
4. Whether features such as type-ahead, personalization, and A/B testing are in scope for v1.

### sdlc-prd-requirements / prd-vague-verbs / with skill / PASS

# Search Feature Requirements (Draft v0.1)

I can't verify any numbers in the PM's brief, so every threshold below is a **proposed default**, tagged `[A#]` and listed under Assumptions for the PM to confirm or change.

## 1. Goal
Help users find relevant items quickly and reliably, so that more search sessions end in a conversion.

## 2. Scope and Non-goals
- **In scope:** keyword search, filtering of results, result-state and error-state behavior, and search analytics events.
- **Out of scope (for now):** personalization or ML ranking, voice or image search, and search-engine replacement. Decision owner: PM.

## 3. Requirements

### Performance (replaces "fast")
- **SRCH-1:** Server response time for a search request is ≤ 300 ms at p95 and ≤ 800 ms at p99, measured under [A1] 50 concurrent requests per second. `[A1]`
- **SRCH-2:** Results first render in ≤ 1.0 s at p75 on a typical broadband connection. `[A2]`
- **SRCH-3:** Applying or removing a filter updates results in ≤ 500 ms at p95. `[A1]`
- **SRCH-4:** A loading indicator appears if a response takes longer than 400 ms.

### Filters (replaces "support many filters")
- **SRCH-5:** Users can filter by each of these attributes: `[OQ1]`
  - category
  - price range
  - availability
  - rating
  - [TBD attributes from PM]
- **SRCH-6:** Multiple filters combine with AND across attributes. Multiple values within one attribute combine with OR. `[A3]`
- **SRCH-7:** Each filter option shows the count of matching results, and options with zero matches are disabled.
- **SRCH-8:** Active filters are visible as removable chips, and a single "Clear all" action resets them.
- **SRCH-9:** Query and filter state is encoded in the URL, so a shared or reloaded link reproduces the same results.

### Error and Edge-case Handling (replaces "handle errors gracefully")
- **SRCH-10:** If the search service returns a 5xx error or times out (> 5 s), the user sees a message that states the search failed and offers a "Retry" action. The entered query and filters are preserved.
- **SRCH-11:** A query with zero results shows a "no results" state that names the query, suggests removing specific active filters, and offers [A4] up to 3 alternative suggestions. `[A4]`
- **SRCH-12:** Empty or whitespace-only queries do not call the backend and show a prompt to enter a term.
- **SRCH-13:** Queries are limited to [A5] 200 characters. Special characters and markup are escaped and never cause a server error. `[A5]`
- **SRCH-14:** Every failed search request is logged with an error code and request ID, and no raw user input is exposed in the UI error text.

### Conversion (replaces "improve conversion")
- **SRCH-15:** The system emits analytics events for:
  - search submitted
  - results viewed
  - filter applied
  - result clicked
  - add-to-cart (or the equivalent primary action) from a search session
  - zero-result search
  - search error
- **SRCH-16:** Target: search-session conversion rate rises from baseline [OQ2] by [A6] ≥ 5% relative within 8 weeks of launch, measured by A/B test at 95% confidence. `[A6]`

## 4. BDD Examples

```gherkin
Scenario: Fast results (SRCH-1)
  Given the catalog contains 100,000 items
  When a user searches for "running shoes"
  Then results are returned in ≤ 300 ms at p95 over a 10-minute load test

Scenario: Combined filters (SRCH-6)
  Given results for "jacket"
  When the user selects category "Outdoor" and price "$50–$100"
  Then every result is in Outdoor AND priced $50–$100

Scenario: Backend failure (SRCH-10)
  Given the search service returns HTTP 503
  When the user submits "laptop" with the filter "In stock"
  Then an error message with a "Retry" button is shown
  And the query "laptop" and the "In stock" filter remain applied

Scenario: Zero results (SRCH-11)
  Given no item matches "xqzv" with the filter "Rating 4+"
  When the user searches
  Then a "no results" state is shown suggesting removal of "Rating 4+"
```

## 5. Metrics
| Metric | Requirement | Target |
|---|---|---|
| p95 search latency | SRCH-1 | ≤ 300 ms |
| p95 filter latency | SRCH-3 | ≤ 500 ms |
| Search error rate | SRCH-10, 14 | < 0.5% of requests `[A7]` |
| Zero-result rate | SRCH-11 | Baseline, then reduce `[OQ2]` |
| Search-session conversion | SRCH-16 | ≥ +5% relative |

## 6. Assumptions
- **A1:** Latency and load figures are placeholders. Owner: Engineering.
- **A2:** Render-time target is a placeholder. Owner: Engineering and Design.
- **A3:** The AND/OR filter logic is standard and not yet validated. Owner: PM.
- **A4:** The suggestion count is a placeholder. Owner: Design.
- **A5:** The query length limit is a placeholder. Owner: Engineering.
- **A6:** The +5% conversion uplift is a placeholder. Owner: PM and Data.
- **A7:** The error-rate budget is a placeholder. Owner: Engineering.

## 7. Open Questions
| ID | Question | Owner |
|---|---|---|
| OQ1 | Which exact filter attributes are required for launch, and which can follow later? | PM |
| OQ2 | What are the current baselines for latency, conversion, and zero-result rate? | Data/Analytics |
| OQ3 | What defines "conversion" here (purchase, add-to-cart, sign-up)? | PM |
| OQ4 | Are there catalog size or traffic projections that affect the load targets? | Engineering |
| OQ5 | Are accessibility (WCAG level) and localization requirements in scope? | PM and Design |

## 8. Dependencies
- A search backend and index able to meet SRCH-1 and SRCH-3 (Engineering).
- An analytics pipeline for SRCH-15 (Data).
- An A/B testing capability for SRCH-16 (Platform).

## Next Action and Validation
1. The PM confirms or revises the `[A#]` thresholds and answers OQ1 and OQ3, which block final acceptance criteria.
2. Engineering checks that SRCH-1 and SRCH-3 are feasible, and any ambiguity found is fed back into this list.
3. Validate with load tests for the performance requirements, the BDD scenarios as acceptance tests, and the A/B test for SRCH-16.

### sdlc-prd-requirements / prd-vague-verbs / baseline / PASS

# Search Feature Requirements

Where the PM's wording was vague, I've proposed concrete, testable targets. These are **placeholder values to confirm**, not agreed numbers.

## 1. Performance
- **FR-1.1** Search results return within **300 ms at p95** and **1 s at p99**, measured server-side under expected peak load.
- **FR-1.2** Type-ahead/suggestions respond within **150 ms at p95**.
- **FR-1.3** The UI shows a loading indicator if results take longer than 200 ms.
- **FR-1.4** Performance targets hold for the full catalog size and for the projected peak concurrent query volume (to be specified).

## 2. Filtering
- **FR-2.1** Users can narrow results using multiple filters at once (combined with AND across filter types).
- **FR-2.2** Supported filter types include: category, price range, availability, rating, brand, and date (list to be finalized with the PM).
- **FR-2.3** Within a single filter type, users can select multiple values (OR within the type).
- **FR-2.4** Each filter option shows a result count, and options with zero results are disabled or hidden.
- **FR-2.5** Applied filters are visible, individually removable, and clearable all at once.
- **FR-2.6** Filter state is reflected in the URL so searches can be shared, bookmarked, and restored with the back button.
- **FR-2.7** Applying or removing a filter updates results without a full page reload.

## 3. Error Handling
- **FR-3.1** If the search service fails or times out, the user sees a clear, non-technical message and a retry option. No raw errors or stack traces are exposed.
- **FR-3.2** A query with no results shows a "no results" state with suggestions (e.g. spelling correction, removing filters, popular items).
- **FR-3.3** Invalid or malicious input (empty query, excessive length, special characters) is validated and sanitized without breaking the page.
- **FR-3.4** If a filter or optional component (e.g. suggestions) fails, core search results still display.
- **FR-3.5** All search errors are logged with enough context (query, filters, error type, request ID) for diagnosis, and alerting fires when the error rate exceeds a threshold (to be defined).
- **FR-3.6** Search availability target: **99.9%** (to be confirmed).

## 4. Conversion
- **FR-4.1** Results are ranked by relevance, with the ranking approach documented and tunable.
- **FR-4.2** Each result displays the information needed to decide without clicking through (e.g. title, image, price, availability).
- **FR-4.3** The system tracks the funnel: search → result click → add to cart → purchase, attributed to the originating query.
- **FR-4.4** Tracking also covers zero-result rate, search exit rate, and filter usage.
- **FR-4.5** Success is defined as a measurable improvement in search-to-purchase conversion rate versus a pre-launch baseline (target uplift and measurement window to be defined, e.g. via A/B test).
- **FR-4.6** Ranking and UI changes can be rolled out behind feature flags to support experimentation.

## 5. Open Items for the PM
- Final target values for latency, availability, and conversion uplift
- Final list of filters
- Expected catalog size and peak query volume
- Baseline conversion rate and how it is measured
- Platform scope (web, mobile, or both) and accessibility requirements

### sdlc-prd-requirements / prd-vague-verbs / with skill / PASS

# Search Feature: Requirements (Draft v1)

All numeric targets are **proposed placeholders** derived from the PM's vague wording. Each is tagged so it can be confirmed or changed without rewriting the list.

## Goal
Help users find items quickly and reliably, and increase the share of search sessions that end in a conversion.

## Scope and non-goals
- **In scope:** keyword search, filtering, result display, error and empty states, search analytics.
- **Out of scope (proposed):** personalization or ML ranking, voice or image search, saved searches, and search-engine replacement or migration decisions.

## Functional requirements

**Performance ("fast")**
- **REQ-1:** The server returns results for 95% of queries within 300 ms (p95) and 99% within 800 ms (p99), measured at the API under normal load. `[A-1]`
- **REQ-2:** The first page of results renders in the UI within 1.0 s (p75) of query submission on a broadband connection. `[A-1]`
- **REQ-3:** The UI shows a loading indicator if results take longer than 300 ms.

**Filters ("many filters")**
- **REQ-4:** Users can apply at least these filters: `[OQ-1]`
  - category
  - price range
  - availability
  - rating
  - brand
- **REQ-5:** Users can combine multiple filters. Filters of different types combine with AND, and multiple values within one filter combine with OR. `[A-2]`
- **REQ-6:** The result list and result count update within the REQ-1 latency target after each filter change.
- **REQ-7:** Active filters are visible, individually removable, and clearable all at once. They are preserved in the URL so a filtered search can be shared and restored with the back button.
- **REQ-8:** Filter options that would produce zero results are disabled or show a count of 0.

**Error handling ("gracefully")**
- **REQ-9:** If the search backend fails or times out (>3 s), the user sees a plain-language message and a retry action. Their query and filters are preserved, and no raw error codes or stack traces are shown.
- **REQ-10:** If a query returns no results, the UI shows an empty state with the query echoed back, suggestions (for example, remove filters or check spelling), and a one-click "clear filters" action.
- **REQ-11:** Invalid input (empty query, over 200 characters, or special characters) is handled without a server error. Empty queries show a prompt or the default listing. `[A-3]`
- **REQ-12:** Failures are logged with a correlation ID, and the error rate is monitored with an alert when it exceeds 1% over 5 minutes. `[A-1]`

**Conversion ("improve conversion")**
- **REQ-13:** The system records these events for each search session: query submitted, filter applied, result clicked, and conversion (`[OQ-2]` defines the conversion action).
- **REQ-14:** Success target: search-session conversion rate increases by X% relative to the pre-launch baseline within 8 weeks of launch, validated by A/B test. `[OQ-3]`

## BDD examples

```gherkin
Scenario: Fast results
  Given the catalog contains 100,000 items
  When a user searches for "running shoes"
  Then the API responds in under 300 ms for 95% of such requests

Scenario: Combined filters
  Given results for "jacket"
  When the user selects category "Outerwear" and price "$50–$100"
  Then every result is in Outerwear and priced between $50 and $100
  And the URL contains the selected filters

Scenario: Backend failure
  Given the search service is unavailable
  When the user submits a query
  Then a friendly error with a "Try again" button is shown
  And the query text remains in the search box

Scenario: No results
  Given a query that matches nothing
  Then the empty state shows suggestions and a "Clear filters" action
```

## Metrics
| Metric | Target | Source |
|---|---|---|
| API latency p95 / p99 | 300 ms / 800 ms | APM |
| UI first-results render p75 | ≤ 1.0 s | RUM |
| Search error rate | < 1% | Logs/alerts |
| Zero-result rate | Baseline, then track | Analytics |
| Search-session conversion | +X% vs. baseline `[OQ-3]` | A/B test |

## Assumptions
- **A-1:** Latency and error thresholds are placeholders pending a baseline measurement. Owner: Engineering lead.
- **A-2:** AND-across, OR-within filter semantics is the standard expectation. Owner: PM.
- **A-3:** Query length limit and empty-query behavior are not yet specified. Owner: PM/UX.

## Open questions and decision owners
- **OQ-1:** Which filters are required for launch, and which does the data model already support? Owner: PM + Engineering.
- **OQ-2:** What counts as "conversion" (purchase, add-to-cart, signup)? Owner: PM/Analytics.
- **OQ-3:** What is the baseline conversion rate and the target lift X? Owner: PM/Analytics.
- **OQ-4:** Does this need to cover mobile and web, and are there accessibility requirements (for example WCAG 2.1 AA)? Owner: PM/Design.

## Dependencies
- Search index and backend capacity for the latency targets (Engineering)
- Analytics event pipeline (Data)
- A/B testing framework (Platform)

## Next action
Have the PM confirm OQ-1 to OQ-3 and the placeholder thresholds. Then finalize the targets and turn the BDD scenarios into acceptance tests.

### sdlc-product-strategy / strategy-scope-creep / baseline / PASS

I can't confirm that. Five major features plus the core habit tracker is not realistic for 3 people in 8 weeks, and saying yes would set the team up to miss the deadline or ship everything half-finished.

**Rough effort (person-weeks, including testing and polish)**

| Item | Estimate |
|---|---|
| Core tracking (habits, check-ins, streaks, reminders, auth, sync) | 10-12 |
| Social feeds (graph, moderation, privacy, notifications) | 6-8 |
| Gamification (points, badges, levels, tuning) | 3-4 |
| AI coaching (prompting, safety, cost controls, evaluation) | 4-6 |
| Web dashboard | 4-6 |
| Apple Watch (app, complications, sync) | 3-5 |

You have about 24 person-weeks, and the core product alone uses half of it. The full list is roughly 30-40+ on top of that, before accounting for bugs, App Store review, and stakeholder feedback.

**Proposed MVP scope (weeks 1-8)**
- Core habit tracking: create habits, daily check-ins, streaks, local and push reminders, basic history/stats
- Accounts and cloud sync
- Light gamification: streak milestones and a few badges (cheap, and it boosts retention)
- Analytics and crash reporting, so you learn what to build next

**Roadmap**

- **Weeks 1-2: Foundation.** Data model, auth, mobile app skeleton, CI, and design of the core flows.
- **Weeks 3-5: Core loop.** Habit CRUD, check-ins, streaks, reminders, sync.
- **Weeks 6-7: Retention and polish.** Milestones/badges, onboarding, stats view, bug fixes.
- **Week 8: Launch.** TestFlight beta, App Store submission, analytics dashboards, and a go/no-go review.

**Post-MVP (v1.1 onward), prioritized by what the data shows**
1. **Apple Watch** (weeks 9-12): quick check-ins fit habit tracking well and reuse the existing sync.
2. **AI coaching** (weeks 11-16): start with weekly summaries and nudges based on user data. Watch the costs.
3. **Web dashboard** (weeks 13-16): worthwhile if users ask for it, otherwise it can wait.
4. **Social feeds** (weeks 17+): the biggest and riskiest item, since it needs moderation and privacy work. Consider starting with simple accountability partners or shared habits instead of a full feed.

**How to present this to stakeholders**
- Ask them to rank the five features. If they insist on one more in the MVP, the cheapest swaps are a minimal Watch companion or basic AI weekly summaries, but each means cutting something else (probably gamification and polish) and accepting more schedule risk.
- Frame the MVP as the fastest way to learn which of the five features users actually want, before investing 4-8 weeks in each.
- Agree on the MVP's success metrics now, such as day-7 and day-30 retention and habits logged per user per week.

If you tell me the platform (native iOS, React Native, Flutter) and the team's skill mix, I can tighten the estimates and turn this into a sprint-level plan.

### sdlc-product-strategy / strategy-scope-creep / with skill / PASS

# Recommendation: I can't confirm all five in the MVP

With 3 people and 8 weeks (about 24 person-weeks), all five features would each be shallow and none would validate the core question: **do people stick with a habit loop in this app?** Here is the scope I'd defend instead.

## Decision

**MVP = core habit loop on one platform, plus the cheapest retention mechanic.**
- Create habits, schedule them, check in daily, see streaks and basic history.
- Reminders (push notifications).
- Lightweight gamification: streaks and milestone badges only. It's cheap, and it supports the retention outcome.
- Basic analytics instrumentation, so you can measure retention.

**Out of the MVP, deliberately:** social feeds, AI coaching, web dashboard, Apple Watch.

## Per-feature call

| Feature | Outcome it supports | Trade-off if included now | Verdict |
|---|---|---|---|
| Gamification (streaks, badges) | Day-7/30 retention | Small cost; risk of shallow motivation | **In, minimal** |
| Apple Watch | Faster check-in, lower friction | Second platform, separate QA and release path; roughly 3-4 person-weeks | **Later (v1.1)**, or only if the app is iOS-first and the watch is a simple check-in |
| Web dashboard | Review and analysis, desktop access | Duplicates the UI and auth/sync work, which adds an API surface | **Later** |
| Social feeds | Acquisition and accountability | Needs moderation, privacy, and a critical mass of users; cold-start problem | **Later**, after retention is proven |
| AI coaching | Differentiation, personalized guidance | Needs data you won't have yet; adds cost, safety, and quality risk | **Later**, once there's enough usage data |

## Roadmap

**Horizon 1: MVP (weeks 1-8), prove the habit loop**
- Weeks 1-2: Scope lock, data model, auth, habit CRUD, analytics events.
- Weeks 3-4: Check-ins, schedules, streak logic, reminders.
- Weeks 5-6: History and progress views, badges, onboarding.
- Weeks 7-8: Beta with 20-50 users, bug fixing, store submission.
- *Why:* every item here directly tests whether users return.

**Horizon 2: Retain (months 3-4)**
- Apple Watch check-in, and widgets.
- Web dashboard (read-heavy, if beta users ask for it).
- *Why:* this lowers friction and widens access, but only once the loop is validated.

**Horizon 3: Differentiate and grow (months 5-8)**
- AI coaching, using real check-in data (start with weekly insights, not a chatbot).
- Social: begin with small private groups or accountability partners, not an open feed.
- *Why:* both depend on having users and data, and social features need a retained base to work.

## Key risks and decision points
- **Stakeholder pressure to expand scope.** Rule: anything added must displace something of equal size and name its outcome.
- **Retention fails.** If day-30 retention is under your threshold, fix the loop before building Horizon 2.
- **Platform choice.** Decide early whether it's iOS-only or cross-platform. This drives the Watch and web timing.

## Success metrics (set targets before the beta)
- Day-7 and day-30 retention.
- Share of users who check in at least 4 days per week in week 2.
- Habits created per activated user.
- Qualitative: top 3 requested features from beta users, which tells you whether to prioritize Watch, web, social, or AI next.

## Next actions
1. Present this table to stakeholders and get agreement on the MVP boundary and the "later" triggers.
2. Choose the platform and the retention targets this week.
3. Hold a scope checkpoint at week 4. If you're ahead of schedule, pull in the Watch check-in first, since it's the smallest of the deferred items.

If a stakeholder insists on one extra feature, I'd pick the Apple Watch check-in, but only if you're already building iOS-native, and only by cutting badges and the history views to make room.

### sdlc-product-strategy / strategy-scope-creep / baseline / PASS

I can't confirm that all five belong in the MVP. For 3 people over 8 weeks (about 24 person-weeks, realistically 18-20 after meetings, bugs, and App Store review), it would likely mean shipping five half-built features and a weak core habit loop.

**Rough cost of each request**

| Feature | Estimate | Notes |
|---|---|---|
| Core habit tracking (auth, CRUD, check-ins, streaks, reminders) | 6-8 person-weeks | Required |
| Social feeds | 5-8 | Moderation, privacy, follows, notifications, and cold-start problems |
| Gamification | 2-4 | Light version (streaks, badges) is cheap; XP, levels, and leaderboards are not |
| AI coaching | 3-5 | The API integration is easy. Prompt design, safety, cost control, and quality evaluation are not |
| Web dashboard | 4-6 | A second client, with its own auth and QA |
| Apple Watch | 3-5 | Separate target, complications, and sync edge cases |

The total is roughly 23-36 person-weeks on top of the core, well over capacity.

**Recommended 8-week roadmap**

- **Weeks 1-2: Foundation.** Pick one platform (iOS, or cross-platform if the team already knows it). Set up the data model, auth, backend, CI, and analytics. Design the core flow.
- **Weeks 3-5: Core loop.** Create habits, daily check-ins, streaks, reminders/push notifications, and a simple history view. Onboarding.
- **Weeks 6-7: Light gamification.** Streak milestones and badges only, which reinforce the core loop cheaply. Add basic analytics events, crash reporting, and polish.
- **Week 8: Beta.** TestFlight with real users, bug fixes, App Store submission, and a retention baseline.

**Post-MVP, in suggested order**

1. **Apple Watch** (v1.1). It's a natural fit for check-ins, and it's a thin client once the API is stable.
2. **AI coaching** (v1.2). Start with weekly summaries and nudges based on the data you've collected.
3. **Web dashboard** (v1.3). Build it if users ask for it or analytics show demand.
4. **Social feeds** (v2). This is the heaviest and riskiest item, and it only works once you have an engaged user base.

**What to tell stakeholders**

"All five are on the roadmap, but only the core habit loop plus light gamification fits in 8 weeks. Each further feature ships once we've validated retention. If you want any of them sooner, we need to cut something else or add people."

If a stakeholder insists on one extra feature, the cheapest is a minimal AI-generated weekly summary (about 1-2 weeks). Social and the web dashboard are the most expensive to squeeze in.

### sdlc-product-strategy / strategy-scope-creep / with skill / PASS

# Recommendation: I can't confirm all five in the MVP

Five features on top of the core tracker is not feasible for 3 people in 8 weeks. Shipping all of them would most likely produce a shallow version of everything and a core habit loop that isn't good enough to retain users. Below is what I'd put in and what I'd defer.

## Decision

**MVP outcome:** A user can create habits, check them off daily in under 5 seconds, and come back the next day because of reminders and visible streaks.

**Success metrics (to set targets with stakeholders):**
- Activation: % of new users who create a habit and complete it on day 1
- Retention: D7 and D30 return rate
- Core usage: habit check-ins per active user per week

**Appetite:** 8 weeks, 3 people, with about 1 week of buffer.

## Scope call on each requested feature

| Feature | Decision | Rationale and trade-off |
|---|---|---|
| Core tracking, reminders, streaks | **In** | This is the product. Everything else depends on it. |
| Gamification | **In, minimal** (streaks, simple milestones/badges) | Cheap and directly supports retention. The trade-off is skipping points, levels, and leaderboards. |
| Apple Watch | **Defer** (or a stretch goal: a check-in-only complication, if ahead of schedule) | Check-in from the wrist is valuable, but it adds a separate target, sync, and testing. It supports retention only after the phone loop works. |
| Web dashboard | **Defer** | It supports analysis and reach, not the first-week habit loop. It also doubles the surfaces you must build and maintain. |
| Social feeds | **Defer** | It needs moderation, privacy, a content model, and a critical mass of users to feel alive. It's the highest cost and risk, and its value is lowest at launch. |
| AI coaching | **Defer** | It needs real usage data to be useful, plus cost, safety, and quality work. A rules-based nudge is a cheap substitute for now. |

## Paths compared

- **MVP/wedge (recommended):** a single-platform, polished core loop. It's fast, testable, and learns what drives retention.
- **Platform:** adds web, watch, and social. This is 2–3x the surface area and doesn't fit the appetite.
- **Enterprise-ready:** not relevant to this stage.

## Roadmap

**Phase 1: MVP (weeks 1–8)**
- Weeks 1–2: Habit model, onboarding, auth, and the daily check-in flow. Set up analytics events from day one.
- Weeks 3–4: Reminders/notifications, streaks, and history view.
- Weeks 5–6: Minimal gamification (milestones/badges), polish, and an internal beta.
- Weeks 7–8: Beta with real users, bug fixes, and store submission. The final week is buffer.

**Phase 2: Retention and reach (about months 3–4)**
- Apple Watch check-in, because it reduces friction for existing users.
- Rules-based smart nudges as a precursor to AI coaching.
- Add the web dashboard only if the data shows demand for it.

**Phase 3: Differentiation (about months 5–7)**
- AI coaching, once you have behavioral data to ground it.
- Lightweight social (private accountability partners or groups) before any public feed.

## Risks and decision points

- **Stakeholder pushback:** Show them this table. If one deferred feature is non-negotiable, name what it replaces. For example, adding Apple Watch means cutting gamification and the beta period.
- **Retention risk:** If D7 retention is weak after beta, fix the core loop before starting Phase 2.
- **Scope creep:** Any new item needs a named outcome and a named trade-off before it enters the plan.

## Next actions

1. Hold a 30-minute stakeholder review of this scope table and get sign-off on the MVP outcome and metrics.
2. Pick the target platform for launch (iOS first is implied by the watch request, but confirm it).
3. Define metric targets (for example, D7 retention) so that "MVP worked" is measurable.
4. Revisit the roadmap at the week-8 beta review using real data.

If you do need to tell stakeholders "yes" to something, tell them that all five are on the roadmap, in a sequence that protects the product's foundation.

### sdlc-product-strategy / strategy-scope-creep / baseline / PASS

I can't confirm all five. Habit tracking, social feeds, gamification, AI coaching, a web dashboard, and Apple Watch support are roughly 6 products' worth of work for 3 people in 8 weeks (about 24 person-weeks). Saying yes would likely mean shipping nothing solid, so here is a scoped roadmap instead.

## Recommended MVP scope

**In (the core loop):**
- Auth and onboarding
- Create, edit, and archive habits (daily/weekly schedules)
- One-tap check-in, streaks, and simple history/progress view
- Local and push reminders
- Basic analytics events, so you can learn what users actually do

**In, but minimal (cheap, high retention value):**
- Gamification-lite: streak counts, a few milestone badges, and a completion animation. There's no points economy, levels, or leaderboards.

**Out of MVP (post-launch phases):**
- **Social feeds:** needs moderation, privacy controls, reporting, and notifications. It's costly and risky, and it's meaningless without an existing user base.
- **AI coaching:** valuable only after you have usage data. It adds cost, safety, and prompt-quality work.
- **Web dashboard:** a second client doubles the QA and auth surface.
- **Apple Watch:** a separate target with its own sync and testing. It's a good fast-follow once the check-in flow is stable.

## 8-week roadmap

| Weeks | Focus |
|---|---|
| 1 | Scope lock, designs for the core loop, data model, tech setup, CI, analytics |
| 2–3 | Auth, habit CRUD, check-ins, backend sync |
| 4 | Streak logic, history/progress views, reminders |
| 5 | Gamification-lite (badges, milestones), onboarding polish |
| 6 | Bug bash, performance, accessibility, internal dogfooding |
| 7 | Closed beta (TestFlight / internal testing), fix top issues, add instrumentation |
| 8 | Store submission, launch, and a prioritized post-MVP backlog based on beta data |

## Post-MVP phases

1. **Weeks 9–12:** Apple Watch check-ins and complications (highest overlap with the core loop), plus retention fixes from the data.
2. **Weeks 13–18:** AI coaching (start with weekly summaries and nudges from existing data), and the web dashboard if users ask for it.
3. **Weeks 19+:** Social features, starting with small accountability partners or groups before a full feed.

## How to put this to stakeholders

- "We can ship all five in 8 weeks only by cutting quality or hiring. We can ship a solid core in 8 weeks and add features in this order."
- Ask them to rank the five by expected impact. If one is a hard requirement (e.g., a funding demo needs AI coaching), we can swap it in, but something else has to come out.
- If they insist on more, the levers are more people, more time, or a lower quality bar. Scope can't absorb it for free.

If you tell me which stakeholder priorities are non-negotiable, I can rework the plan around them.

### sdlc-product-strategy / strategy-scope-creep / with skill / PASS

# I can't confirm all five in the MVP

With 3 people and 8 weeks you have roughly 24 person-weeks, and about 16-18 of those are productive after QA, app store review, and unplanned work. Five additional features, each a product in its own right, would cost more than the whole budget and leave the core habit loop undertested. Here is what I'd recommend instead.

## Decision

**MVP outcome:** a user can create a habit, check in daily with minimal friction, and come back because reminders and streaks keep them engaged.

| Request | Verdict | Outcome it supports | Trade-off / reason |
|---|---|---|---|
| Core tracking, reminders, history | **In** | Activation and daily use | This is the product. |
| Gamification (lite: streaks, milestones, a simple badge set) | **In, reduced** | Retention | Skips points, levels, and leaderboards. Costs about 1 week. |
| Apple Watch | **Fast-follow** (v1.1) | Lower check-in friction | Needs a separate target, sync, and testing. Add only if the iOS app is native. |
| Web dashboard | **Defer** | Review and analysis for power users | Second client, auth, and responsive design. It doesn't help the daily check-in loop. |
| AI coaching | **Defer** | Long-term retention | Needs real usage data first, plus costs for inference, safety, and quality evaluation. |
| Social feed | **Defer** | Virality and engagement | Cold start, moderation, privacy, and abuse handling. It is the highest-risk item for a small team. |

## Appetite and non-goals

- **Appetite:** 8 weeks, 3 people, one platform (iOS, or cross-platform if the team already has that skill), with a 1-2 week buffer.
- **Non-goals:** user-to-user features, a second client, generative features, and monetization beyond basic readiness.

## Success metrics (set targets before launch)

- **Activation:** percent of new users who create a habit and complete 3 check-ins in their first 3 days.
- **Retention:** D7 and D30.
- **Engagement:** weekly check-ins per active user.
- **Quality:** crash-free sessions and reminder delivery reliability.

## Roadmap

**Weeks 1-8: MVP**
- Wk 1-2: onboarding, habit CRUD, data model, auth/sync decision.
- Wk 3-5: check-in flow, reminders, streaks, history view.
- Wk 6: lite gamification (streaks and milestones).
- Wk 7: polish, analytics instrumentation, beta (TestFlight).
- Wk 8: bug fixes, store submission, buffer.

**Weeks 9-16: Next** (priorities set by MVP data)
1. Apple Watch quick check-in, if friction in check-in data justifies it.
2. Web dashboard, if users ask for review and analysis.
3. Prototype AI coaching on a small cohort (rule-based or template insights first).

**Later:** social features (start with private accountability partners rather than a public feed), richer gamification, and monetization.

## Strategic risks and decision points

- **Scope pressure:** if stakeholders insist on one extra item, name what it replaces. Adding Watch support, for example, would cost about 2-3 weeks of the polish and beta time.
- **Retention unknown:** after beta, decide at week 7 whether to invest in gamification or in reminders and UX.
- **Platform choice:** confirm iOS-first now, because it determines whether Watch is cheap or expensive later.

## Next actions

1. Share this table with stakeholders and ask them to rank the five requests by the outcome they care about most.
2. Lock the MVP scope and the non-goals in writing.
3. Define the metric targets and the instrumentation plan in week 1.

**Validation:** at the week 7 beta, check activation and D7 against your targets, and use those results to decide the order of the weeks 9-16 items.

### sdlc-release-production-readiness / release-unknown-rollback / baseline / PASS

# Release decision: NO-GO as planned

**Decision:** Do not ship both changes tonight. The demo is tomorrow, so the cost of waiting is low and the cost of a failed release is high.

## Why

1. **No rollback plan on a column type change.** This is the riskiest item. Type changes can rewrite or lock the table, truncate or coerce data, and often can't be undone once new writes land. Without a tested reverse path or a backup you've verified restores, a bad migration means data loss or extended downtime.
2. **No dashboards means no visibility.** If the payment integration fails, you'd learn about it from users or from the demo itself. You can't tell "working" from "silently failing."
3. **Two high-risk changes together.** If something breaks, you can't quickly tell whether the migration or the provider caused it, and you can't revert one independently.
4. **Payments add irreversible side effects.** Double charges, failed captures, and webhook mismatches affect real money and real customers, and they can't be rolled back with a deploy.
5. **Timing.** Shipping hours before a demo leaves no buffer to diagnose or fix problems, and a broken demo is worse than a demo on the previous stable build.

## Recommended path

**Tonight (low risk, protects the demo):**
- Freeze the demo environment on the current stable build.
- Take a full database backup and **do a test restore** to confirm it works.
- Rehearse the column migration on a copy of production data. Record its duration, locking behavior, and any data changes.
- Write the rollback steps for the migration (reverse migration or restore procedure) and time them.

**Before the payment provider goes live:**
- Put it behind a feature flag, off by default, so it can be disabled without a deploy.
- Use the provider's sandbox/test mode for the demo.
- Add minimal monitoring: error rate and latency on payment calls, payment success/failure counts, webhook failures, and an alert to a person. A basic log query or a simple alert is enough to start.
- Test idempotency (retries don't double-charge) and the failure path (provider timeout or decline).

**After the demo:**
- Ship the column change on its own, ideally with an expand/contract approach (add the new column, dual-write, backfill, switch reads, drop the old one later), so it's reversible at each step.
- Ship the payment integration separately, in a later window, with a gradual rollout (internal users, then a small percentage, then everyone).

## What would change my answer to "Go"

For the migration, all of these would need to be true:
- A verified backup restore
- A rehearsed migration on production-like data
- A documented, timed rollback
- A reversible or non-destructive change

For the payment provider, all of these would need to be true:
- It's behind a flag
- Basic alerting is live
- It has been tested in sandbox
- There's a named person on call

Even then I'd ship them **separately**, not together, and not the night before a demo.

## If the demo needs the payment integration

Demo it in sandbox mode from a separate branch or environment, with the flag on. That shows the feature without exposing production data or real money to an untested release.

**Summary:** Hold both changes, protect the demo with the stable build, and use tonight to build the rollback and monitoring so the real release can go out safely afterward.

### sdlc-release-production-readiness / release-unknown-rollback / with skill / PASS

# Release decision: NO-GO for tonight's production release as scoped

**Decision:** Do not ship the column type change and the new payment provider integration to production tonight. Re-scope so the demo is still covered (see options below).

## Rationale

The release skill's hard stop applies: no release when rollback, monitoring, or customer impact is unknown for a material change. Here all three are true, and both changes are high risk.

| Risk | Status | Why it blocks |
|---|---|---|
| Column type change | No rollback plan | Type changes can rewrite or lock tables and can truncate or coerce data. Once new writes land, reverting may be lossy or impossible without a backup. |
| New payment provider | No dashboards or alerts | Failed charges, duplicate charges, or webhook failures would be invisible until customers or finance report them. |
| Both together | Shipped at the same time | If something breaks, you can't tell which change caused it, and you can't separate the rollbacks. |
| Timing | Overnight, before a demo | Nobody is watching, and the pressure to "just leave it" is highest when the demo is tomorrow. |

Customer impact is currently unknown. I have no repo access, so I can't verify table size, lock behavior, or the payment code path. Those unknowns are themselves part of the problem.

## Options to protect the demo (in order of preference)

1. **Demo from staging or a prod-like environment (recommended).** Ship nothing to production tonight. Run both changes in staging with the provider's sandbox credentials. Zero customer risk, and the demo is unaffected.
2. **Ship the payment integration dark behind a feature flag, defaulting to off, without the migration.** Turn it on only for an internal test account for the demo. It needs minimal monitoring (see below) and a flag kill switch. Don't do this unless the integration doesn't depend on the new column type.
3. **Ship the migration alone, using expand/contract.** Add a new column with the new type, dual-write, backfill, and switch reads later. The old column stays as the rollback path. This probably doesn't fit in one night, so it shouldn't gate the demo.

**Not acceptable:** shipping both changes tonight with a plan to "watch it manually."

## Go/no-go criteria to flip this to GO (later)

| Item | Criterion | Owner (assign) |
|---|---|---|
| Migration rollback | Tested on a production-sized copy, with a verified backup/restore and a documented time estimate. Prefer expand/contract. | DB/backend lead |
| Migration safety | Lock and duration measured, with no data loss on a sample diff before and after. | DB/backend lead |
| Payment kill switch | Feature flag that disables the provider without a deploy. Fallback behavior defined. | Payments engineer |
| Idempotency | Idempotency keys on charges, and webhook retries handled, to avoid double charges. | Payments engineer |
| Monitoring | Minimum dashboard: charge success/failure rate, provider latency and errors, webhook failures, migration errors, DB locks and latency. Alerts routed to a named on-call. | SRE/on-call |
| Security | Secrets in the secret store, webhook signature verification, no card data in logs, and PCI scope reviewed. | Security owner |
| Support readiness | Support knows what changed, how to spot failed payments, and who to escalate to. | Support lead |
| Release notes | Written, including known limitations. | Release owner |

## Rollout plan when ready

1. Deploy the expand step of the migration in a low-traffic window, with a backup taken beforehand.
2. Ship the payment integration behind a flag, internal users first.
3. Canary at about 1–5% of payments, hold for a set period, then ramp up.
4. Keep the old column or provider path until the new path is verified, then run the contract/cleanup step separately.

## Post-release monitoring (for the eventual release)

- Watch for the first hour continuously, then at 24 hours.
- Rollback triggers: payment failure rate above baseline by an agreed threshold, any duplicate charge, migration errors, or DB latency/lock alerts.

## Next actions (tonight)

1. Announce the re-scope: the demo runs from staging (option 1), and production is unchanged.
2. Verify the staging demo path end-to-end with sandbox credentials, and rehearse once.
3. Assign owners for the table above and schedule the rollback test and dashboard build.
4. Re-run this go/no-go review once the rollback test and the minimum dashboard exist.

## Validation

- Confirm with the team that production is untouched tonight.
- The demo works on staging before you go to bed.
- The re-review is scheduled with named owners.

**Trade-off:** you give up demoing on production, which is a small cost. In exchange you avoid an unmonitored and possibly irreversible change to a payments system and a live schema.

### sdlc-release-production-readiness / release-unknown-rollback / baseline / PASS

# Release Decision: **NO-GO for tonight** (conditional path to GO below)

## Rationale

Two high-risk changes are shipping together with no way to undo them and no way to see them failing:

1. **Column type change.** Often irreversible in practice. Data can be truncated, rounded, or rewritten, and the migration may lock tables. Without a backup/restore or reverse migration, a mistake becomes data loss.
2. **New payment provider.** Failures here mean lost revenue, double charges, or orphaned transactions. Without dashboards, you won't know it's failing until customers or finance tell you.
3. **Combined.** If something breaks, you can't tell which change caused it, and you can't revert either one.

The demo deadline is a real pressure, but a broken or data-corrupted system during the demo is worse than a demo on the current stable build.

## Recommended path

**Tonight: don't ship both.** Demo from the current stable environment, or a staging environment with the changes applied.

**To reach GO (any of these options):**

**Option A: Ship neither, demo on staging (safest).**
- Apply both changes in staging, run the demo there.
- Ship to production after rollback and monitoring exist.

**Option B: Ship only the payment provider, behind a feature flag (if the demo needs it).**
- Flag defaults off; enable for internal/test accounts only.
- Provider in sandbox/test mode for the demo.
- Kill switch is the flag flip, which is your rollback.
- Don't ship the column change.

**Option C: Ship the column change alone, only if all of these hold:**
- Verified, restorable backup taken immediately before, with a restore test done.
- Migration rehearsed on a production-sized copy, with timing and lock behavior known.
- Expand/contract approach (add new column, dual-write, backfill, switch later) rather than in-place alteration.
- Do this separately from the payment change, not tonight alongside it.

## Minimum bar before any production ship

- [ ] Written rollback steps for each change, tested at least once
- [ ] Fresh backup, restore verified
- [ ] Minimum monitoring: payment success/failure rate, error rate, migration status, and an alert to a named person
- [ ] Named on-call owner for tonight and tomorrow's demo
- [ ] Changes deployed separately, with time between to observe
- [ ] Payment provider tested for idempotency (no duplicate charges on retries) and webhook handling

## If leadership overrides and ships anyway

Accept it explicitly as a risk decision, recorded by name. At minimum: take a backup, ship the payment integration flagged off, skip the column change, and have someone watching logs manually through the demo.

**Bottom line:** The demo doesn't require production to carry these changes. Protect the data and the payment path, and ship once you can see and undo.

### sdlc-release-production-readiness / release-unknown-rollback / with skill / PASS

# Release decision: NO-GO for tonight as planned

**Changes:** a database column type change plus a new payment provider integration, both shipping tonight.
**Driver:** a demo tomorrow.

## Rationale

Both changes are material, and the release fails the hard gates:

| Gate | Status | Why it matters |
|---|---|---|
| Rollback | None | Column type changes can be lossy or irreversible (truncation, precision loss, table rewrite locks). Payments can't be "undone" once money moves. |
| Monitoring | No dashboards | You couldn't tell whether payments are failing, duplicating, or timing out until customers report it. |
| Customer impact | Unknown | Payments touch money, trust, and possibly compliance (PCI scope, provider terms). |

Shipping both at once is also a problem. If something breaks, you can't tell whether the migration or the provider caused it.

## Options

1. **Demo from staging or a demo environment (recommended).** Deploy tonight to a non-production environment with the migration applied and the provider in sandbox or test mode. It gives the same demo value with no production risk.
2. **Ship the migration alone, expand/contract style.** Add a new column, dual-write, and backfill. Don't drop or alter the old column yet. Take a verified backup first and rehearse the migration on a production-sized copy. This is reversible, but it needs time you may not have tonight.
3. **Ship the payment integration dark.** Put it behind a feature flag that is off by default, with the provider in sandbox mode. Enable it for internal users only, after minimal monitoring exists. The kill switch is your rollback.
4. **Ship both to production tonight.** Not acceptable under current conditions. Overriding this needs a named executive owner to accept the risk in writing.

## Conditions to flip to GO (all required)

- **Migration:** a tested rollback or forward-fix path, a fresh verified backup and restore test, a timed rehearsal on production-like data, and a lock/downtime estimate. Owner: backend/DB lead.
- **Payments:** a feature flag or kill switch, idempotency keys on charges, a tested webhook and failure path, sandbox end-to-end test results, and a documented refund and reconciliation procedure. Owner: payments engineer.
- **Observability (minimum viable):** payment success/error rate, provider latency, migration/DB error rates and locks, and an alert routed to a person on call. A single basic dashboard is enough. Owner: whoever is on call.
- **Support and comms:** a short runbook (how to disable, who to call, how to refund) and a support heads-up. Owner: engineering manager.
- **Security:** provider keys in a secrets manager, no card data in logs, and webhook signature verification. Owner: security reviewer.

## Rollout plan once criteria are met

1. Release the migration separately from the payment integration, at least one deploy apart.
2. Turn the payment flag on for internal accounts first, then about 1% of traffic, then widen.
3. Watch the dashboard for a fixed window (for example 30 minutes) before each step.
4. **Abort triggers:** payment error rate above baseline, any duplicate charge, or migration errors. Turn off the flag immediately.

## Next actions (in order)

1. Tell stakeholders tonight's production release is a no-go and the demo will run on staging or sandbox.
2. Assign owners for the gates above.
3. Build the minimal dashboard and alerts tomorrow, during or right after the demo.
4. Rehearse the migration, then schedule a production release in a low-traffic window with someone on call.

## Validation

- Demo works end to end in staging, including a failed-payment path.
- Migration rehearsal succeeds and restores cleanly from backup.
- Flag-off and flag-on behavior are both verified in production before real traffic.

## Release notes

Hold them until the real release. Draft them now to cover the column type change, the new payment provider, the flag state, and known limitations.

**Trade-off:** you give up "live in production" for the demo, but you avoid the risk of an irreversible data change and unobserved payment failures during or right before a customer-facing event.

### sdlc-release-production-readiness / release-unknown-rollback / baseline / PASS

# Release Decision: **NO-GO for tonight**

## Rationale

You're shipping two high-risk changes together with no way to undo either and no way to see whether they're working. Any one of those gaps is a concern; all three together are disqualifying.

**1. Column type change with no rollback**
- Type changes can rewrite or lock the table, silently truncate or coerce data, and break application code that reads the old type.
- Once writes land in the new type, reverting can be lossy or impossible.
- No rollback plan means a bad outcome is potentially unrecoverable data corruption, not just downtime.

**2. New payment provider with no rollback**
- Failures here lose revenue, double-charge customers, or leave orders in inconsistent states.
- Payment bugs often surface hours or days later (settlement, refunds, webhooks), not at deploy time.

**3. No dashboards or monitoring**
- You won't know if payments are failing, if error rates spike, or if the migration caused latency or lock contention.
- You'd be finding out from customers, or from the demo itself.

**4. Bundling**
- Two independent risky changes at once make root-cause analysis hard and rollback harder.

**5. The demo is the real risk**
- A failure tonight means you walk into the demo with a broken or degraded system and no time to fix it. Shipping tonight *increases* demo risk rather than reducing it.

## What to do instead

**For tomorrow's demo (low risk):**
- Demo from a staging environment or a feature-flagged build with the new provider in sandbox/test mode.
- Use recorded or scripted flows with test data if needed.
- Be upfront that production rollout follows after hardening.

**Before shipping to production (minimum bar):**

*Database change*
- Take a verified backup/snapshot and test the restore.
- Use an expand/contract pattern: add a new column, dual-write, backfill, switch reads, then drop the old column later.
- Rehearse the migration on a production-sized copy; measure lock time and duration.
- Write and test the down-migration.

*Payment provider*
- Put it behind a feature flag, default off, with a kill switch to the old provider.
- Roll out to a small percentage of traffic or internal accounts first.
- Test idempotency, webhooks, refunds, and failure/timeout paths in sandbox.

*Observability (minimum viable)*
- Payment success/failure rate, latency, and provider error codes.
- Application error rate and DB query latency/locks.
- Alerts routed to a named on-call person.

*Process*
- Ship the two changes on separate days.
- Deploy in a low-traffic window with someone watching, not right before a demo.
- Define explicit abort criteria in advance (e.g., payment failure rate above X% means flip the flag off).

## Conditions to revisit

I would change this to **conditional GO** if, before tonight, you can show all of:
1. A tested backup/restore (or a reversible, expand-style migration).
2. The payment provider behind a flag that is off by default, with a tested kill switch.
3. At least basic payment and error alerts with a named owner.
4. The two changes split, with the DB change landing first and soaking.

If those can't be done today, defer. A delayed release costs you a day; a corrupted table or broken checkout costs far more.

**Decision: NO-GO. Demo from staging/sandbox; ship after rollback, flags, and monitoring are in place.**

### sdlc-release-production-readiness / release-unknown-rollback / with skill / PASS

# Release Go Decision: **NO-GO for tonight as scoped**

## Decision
Do not ship the column type change and the new payment provider together tonight. Both are material changes, and rollback, monitoring, and customer impact are all unknown or missing. Those are hard stops.

## Summary of the change
- **Change 1:** Database column type change. Often irreversible or lossy (truncation, precision loss, long table locks), and it affects every code path that reads or writes the column.
- **Change 2:** New payment provider integration. Touches money movement, so failures are customer-visible, hard to reverse (charges, refunds, reconciliation), and may carry compliance obligations.
- **Success looks like:** The demo works tomorrow, and no customer is double-charged, mis-charged, or blocked.

## Why no-go
| Gate | Status | Blocker? |
|---|---|---|
| Rollback plan | None | **Yes** |
| Monitoring/dashboards | None | **Yes** (a payment failure would be invisible) |
| Customer impact | Unknown | **Yes** |
| Migration safety | Not evidenced (backup, restore test, lock time, data validation) | Yes |
| Payment security/compliance | Not evidenced (secrets handling, webhook signature verification, idempotency, PCI scope) | Yes |
| Support readiness/runbook | Not evidenced | Likely |

Bundling the two changes also means that if something breaks, you can't tell which change caused it, and you can't roll back one without the other.

## Recommended path to still hit the demo

**Option A (recommended): Demo from staging or a demo environment, ship later.**
- Deploy both changes to staging with sandbox/test credentials for the provider.
- Demo tomorrow from there. Production risk is zero and the demo is unaffected.
- Trade-off: the demo isn't on production, which is almost always acceptable.

**Option B: Ship only the safe subset tonight, behind a flag.**
- Ship the payment integration code **dark**, behind a feature flag defaulting to off, enabled only for an internal test account or the demo tenant.
- **Do not** ship the column type change tonight. If the integration truly requires it, use an expand/contract approach: add a new column, dual-write, and backfill later. The old column stays untouched, so the change is reversible.
- Use test or sandbox mode for the provider, not live charges, until monitoring exists.
- Trade-off: more engineering tonight, and it only qualifies as "go" if the minimum conditions below are all met.

**Rejected: ship everything tonight and "watch it."** With no dashboards you can't watch it, and with no rollback you can't act on what you see.

## Minimum conditions for any production deploy tonight (Option B)
Each needs a named owner before go:
1. **Backup and restore:** Fresh DB backup taken and a restore verified (owner: DB/backend lead).
2. **Rollback:** Written, tested step to turn off the flag and revert code. The migration must be additive only (owner: release engineer).
3. **Minimum monitoring:** Even without full dashboards, have alerts or a saved query on payment error rate, provider webhook failures, and DB errors. Someone must be actively watching for the first hour (owner: on-call).
4. **Payment safety:** Idempotency keys, webhook signature verification, secrets in the secret manager, and a kill switch (owner: payments engineer).
5. **Blast radius:** Flag limited to internal or demo accounts. No real customer traffic is routed to the new provider.
6. **Support:** One-paragraph runbook covering how to disable, who to page, and how to reconcile a bad charge (owner: support/on-call).

If any of 1–5 can't be met by your cutoff time, the answer is Option A.

## Next actions
1. **Now:** Decide A or B. My recommendation is A, with B only if the demo truly requires production.
2. **Tonight:** Split the column migration out of this release regardless of the option chosen.
3. **After the demo:** Build the rollback plan, a basic payments dashboard (success/failure rate, latency, webhook lag, DB errors), and the runbook. Then do a phased rollout: internal, then 1–5% canary, then full, with go/no-go checks between stages.
4. **Migration:** Rehearse the column change on a production-sized copy. Measure lock time and verify data integrity before a maintenance window.

## Validation
- **Tonight (if B):** Flag-off behavior is identical to the current release. Smoke test a sandbox payment end to end, and confirm the kill switch works.
- **Post-release:** Watch payment error rate, webhook failures, and DB errors for 24 hours. Pre-agree on a rollback trigger, for example any unexplained failed payment or an error rate above baseline.

## Release note (internal, draft)
> Payment provider integration deployed behind a feature flag, disabled for customers. Enabled for internal demo only. Column type migration deferred pending rollback plan and rehearsal. No customer-facing change.

**Bottom line:** The demo doesn't require taking on irreversible production risk. Demo from staging or a flagged internal account, and ship the real rollout once you can see and undo it.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / baseline / PASS

# Billing module: 3-month plan to clean architecture

## A caution first

Billing is the worst place for a big-bang rewrite. Six-year-old billing code encodes years of edge cases (proration, tax rules, refunds, retries, legacy customers) that nobody remembers and the tests may not capture. With no bug or delivery problem driving this, the main risk is regressions in money handling, and the main payoff is aesthetics and future velocity.

So I'd plan it as an **incremental strangler-style refactor**, not a rewrite-then-switch. You still end up with the same clean architecture, but you can stop at any point with a working system, and each step is verifiable against production behavior.

## Target architecture

- **Domain**: pure business logic with no I/O. Entities and value objects (Money, Invoice, Subscription, LineItem, TaxRate), plus pricing, proration and invoice-state rules.
- **Application**: use cases (CreateInvoice, ApplyPayment, RefundCharge, RenewSubscription) and the ports (interfaces) they depend on.
- **Infrastructure**: adapters for the DB, payment provider, tax service, email and the event bus.
- **Interface**: HTTP handlers, jobs and webhooks, kept thin.

Dependencies point inward only. Enforce this with a lint or architecture test, not convention.

## Phase 0: Weeks 1–2, Understand and protect

- Inventory every entry point (APIs, cron jobs, webhooks, internal callers) and every external dependency.
- Write **characterization tests** that pin current behavior, bugs included, for the money paths: invoice generation, proration, taxes, refunds, retries and dunning.
- Build a **shadow/comparison harness**: run old and new calculations on real (anonymized) production inputs and diff the outputs.
- Define success metrics up front: zero unexplained diffs, coverage on the domain layer, and the number of modules that depend on the legacy internals.
- **Exit criteria**: a golden-master suite you trust, and a written list of known quirks that need a product decision (preserve or fix).

## Phase 1: Weeks 3–5, Domain core

- Extract the pure logic first: Money (integer minor units and explicit currency, no floats), pricing, proration, tax calculation and invoice state machine.
- Build it alongside the old code, with unit and property-based tests.
- Run it in shadow mode: the old path stays authoritative and the new one is compared on every call.
- **Exit criteria**: diff rate is zero, or every diff is explained and approved.

## Phase 2: Weeks 6–8, Application layer and ports

- Define the ports (PaymentGateway, InvoiceRepository, TaxProvider, Clock, EventPublisher).
- Implement use cases against those ports, with in-memory fakes for fast tests.
- Write infrastructure adapters that wrap the existing DB schema. **Do not change the schema yet**, since schema and code changes together make rollback hard.
- Route the **lowest-risk flows first** (for example read-only invoice views, then invoice generation) through the new use cases behind feature flags, with gradual percentage rollout.

## Phase 3: Weeks 9–11, Migrate the risky flows

- Move payments, refunds, renewals and webhooks one at a time, each behind a flag with a quick rollback.
- Make idempotency explicit, with idempotency keys on every payment operation.
- Run both paths in parallel where safe (for example reconcile against the payment provider's records daily).
- Migrate the callers of the legacy module to the new interfaces as each flow lands.
- **Exit criteria**: 100% of traffic on the new paths for at least a week with clean reconciliation.

## Phase 4: Week 12, Cleanup

- Delete the legacy code paths and flags.
- Optionally do schema cleanup as a separate, reversible migration. If it's risky, defer it.
- Write architecture docs and ADRs, and keep the dependency-rule check in CI.
- Do a retrospective.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Hidden business rules lost | Golden-master tests and shadow comparison |
| Scope creep ("while we're here…") | Behavior-preserving only. Fixes and features go in a separate backlog |
| Money bugs | Integer money, reconciliation against the provider, staged rollout |
| Timeline slip | Each phase ships value independently, so you can stop after any phase |
| Team fatigue | Keep a regular cadence of small merges, no long-lived branch |

## Questions that would change the plan

1. How good is the current test coverage? If it's poor, Phase 0 may take longer.
2. How many engineers can work on this, and is it alongside feature work? Three months assumes roughly 2–3 people dedicated.
3. Is the schema shared with other services or reporting?
4. Who can approve behavior changes when you find legacy quirks?

## A cheaper alternative

If the real offense is specific hotspots, you can get 70% of the benefit with about 3 weeks of work: wrap the module behind a clean interface, extract Money and pricing into a pure domain package, and refactor only the files that change often. Check your change history to see which parts are actually painful. If it's a small portion of the code, a targeted cleanup beats a full rewrite.

If you want, I can detail any phase, draft the characterization-test strategy, or sketch the port interfaces.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / with skill / PASS

# Decision: don't schedule the 3-month full rewrite yet. Run a 2-week measurement phase first.

## Rationale
- "It offends me" is a real signal, since it usually means something is costly to read or change. But it isn't yet a measurable risk reduction or delivery benefit, so a rewrite can't be justified or judged a success.
- Billing is a poor candidate for a big-bang rewrite. It is money-touching, full of undocumented edge cases (proration, tax, refunds, legacy plans, rounding), and a 6-year-old module encodes years of fixes that a clean-slate design tends to lose.
- A rewrite also costs roughly 3 months of feature capacity, with no payoff until cutover. The cost of inaction is currently unknown and possibly near zero.

## Phase 0 (weeks 1-2): turn the offense into data
1. **Classify the debt** (code, tests, architecture, data, infra, security, docs, ops). "Ugly" might mean tangled dependencies, no tests, a bad data model, or just style, and each has a different fix.
2. **Gather baselines from git history and the issue tracker:**
   - Change frequency per file (hotspots) and lead time for billing changes.
   - Defect and incident count touching billing, and the time to fix them.
   - Test coverage and flakiness in the module.
   - How long a new engineer takes to make a safe change.
   - Dependency vulnerabilities and outdated libraries.
3. **Score each debt item** on impact, cost of inaction, effort, risk, owner, and time horizon.
4. **Check for hidden drivers:** upcoming pricing changes, new payment providers, tax or compliance work, or planned features that would make billing changes frequent. A rewrite is easiest to justify when it removes a known upcoming obstacle.

## Go/no-go at the end of Phase 0
- **If the hotspots are rarely touched and cause no incidents:** leave them alone, document them in a debt register, and move on. The ugliness costs little.
- **If a few areas drive most of the pain:** do targeted refactors there (Phase 1).
- **If the architecture blocks a specific upcoming need:** plan the larger evolution, scoped to that need.

## Phase 1 (if justified): incremental, strangler-style refactor
Aim for the clean-architecture direction without a rewrite of the whole module:
1. **Characterization tests first.** Capture current behavior (invoice calculation, proration, tax, refunds) using real or anonymized production scenarios. Run old and new logic side by side and diff the outputs.
2. **Carve out a domain core** (pricing, invoice, and subscription rules as pure logic) behind interfaces, one slice at a time, starting with the highest-churn hotspot.
3. **Isolate infrastructure** (payment gateway, DB, tax service) behind adapters as each slice is touched.
4. **Ship each slice behind a feature flag** with shadow-mode comparison, gradual rollout, and a tested rollback path.
5. **Data changes** use expand/contract migrations. Never change the schema and behavior in the same release.
6. **Record decisions** in short ADRs, and write a sunset plan for each legacy component replaced.

Budget around 20-30% of billing-team capacity rather than 100%, with each slice delivered independently, so you can stop at any point and still be better off.

## Trade-offs
| Option | Benefit | Risk |
|---|---|---|
| Full 3-month rewrite | Clean result | High regression risk in money flows, feature freeze, no early value, easy to overrun |
| Incremental strangler | Continuous value, reversible | Slower to "feel clean", two styles coexist for a while |
| Leave as is | Zero cost now | Pain may compound if hotspots grow |

## Validation: define success before starting
Pick 2-3 of these and set targets from the Phase 0 baselines:
- Lead time for billing changes down X%.
- Billing-related defects or incidents down X%.
- Coverage of critical billing paths above X%, with zero unexplained diffs in shadow mode.
- Onboarding time to the first safe billing change down X%.

## Next action
Spend two days on the hotspot analysis (change frequency × defects × coverage) and share the top five findings. That will tell us whether the "ugly" part is costing you anything, and where to cut first if it is.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / baseline / PASS

# Billing module: 3-month restructuring plan

**A caution first.** A full rewrite of billing, with no bug or delivery problem driving it, is the riskiest version of this work. Billing encodes six years of edge cases (proration, tax, refunds, dunning, rounding, grandfathered plans) that nobody remembers until they break. Errors there cost money and trust. So I'd plan this as an **incremental strangler migration** toward clean architecture, not a rewrite-and-swap. The end state is the same, and you can stop at any point with a working system.

## Guiding principles
- Behavior stays identical unless explicitly decided otherwise. This is a refactor, not a redesign of business rules.
- Every phase ships to production behind flags. There is no big-bang cutover.
- Money paths get characterization tests before any code moves.
- Define "done" up front, or the project will sprawl.

## Phase 0: Weeks 1-2, Understand and protect
- Map the module: entry points, callers, DB tables, external integrations (payment provider, tax, email, accounting/ERP), background jobs, and webhooks.
- Write down the actual domain: invoices, subscriptions, plans, payments, credits, refunds, and so on. Identify the business rules and where they live.
- Build **characterization (golden-master) tests**: capture real inputs and outputs, anonymized, from production or staging. Cover rounding, proration, taxes, currency, and failed-payment flows.
- Set up a **shadow/comparison harness**: run old and new calculation paths on the same inputs and diff results.
- Agree on success criteria, for example: domain logic has no framework or DB imports, the core is covered by tests, and the old code is deleted.
- Get explicit buy-in from the team and stakeholders on the time investment. Finance or support should know that billing is being touched.

## Phase 1: Weeks 3-5, Carve out the domain core
- Create the target structure:
  - **Domain**: entities, value objects (`Money`, `Currency`, `BillingPeriod`), and pure business rules with no I/O.
  - **Application**: use cases such as `CreateInvoice`, `ApplyPayment`, `IssueRefund`, `RenewSubscription`.
  - **Ports**: interfaces for repositories, payment gateway, tax, clock, and notifications.
  - **Adapters/Infrastructure**: DB, provider SDKs, queues, HTTP.
- Start with the **pure calculation logic** (pricing, proration, tax, totals). It has the best test value and the lowest risk.
- Introduce a `Money` type and fix rounding in one place. Preserve the legacy behavior first, even where it's quirky, and flag the quirks separately.
- Run the new calculators in shadow mode and review any diffs with the business owner.

## Phase 2: Weeks 6-9, Use cases and persistence
- Move workflows into application-layer use cases, one vertical slice at a time. A sensible order is read-only (invoice display and reports), then invoice creation, then payment capture, then refunds and credits, then subscription renewal and dunning.
- Wrap the existing DB schema with repository adapters. **Avoid schema changes in this phase**, and handle any migrations later as their own work.
- Put legacy entry points (controllers, jobs, webhooks) behind thin facades that call the new use cases, switched per slice by feature flag.
- Make idempotency and transactional boundaries explicit for each use case. Billing code often relies on accidental ones.
- Roll out gradually: internal accounts, then a small percentage of customers, then everyone. Reconcile continuously.

## Phase 3: Weeks 10-11, Integrations and edges
- Isolate the payment provider, tax service, and email behind adapters with contract tests.
- Move webhook handling and background jobs onto the new use cases.
- Standardize errors, logging, and audit trails (who changed what and when). Billing audit trails are often required for compliance.

## Phase 4: Weeks 12-13, Cutover and cleanup
- Remove flags once each slice has been stable for a full billing cycle. This is a scheduling constraint: monthly and annual cycles may not complete within 3 months, so plan cutover around your cycle length.
- Delete the legacy code and dead paths.
- Write architecture docs, an ADR for key decisions, and a short onboarding guide for the module.
- Run a retrospective and decide whether any schema cleanup deserves a follow-up project.

## Risks and mitigations
| Risk | Mitigation |
|---|---|
| Subtle money discrepancies | Golden-master tests, shadow diffs, reconciliation reports |
| Scope creep ("while we're here...") | Written non-goals; a backlog for ideas |
| Hidden consumers of the module | Usage mapping in Phase 0; deprecation logging |
| Billing-cycle timing | Plan around real renewal dates; avoid month-end and year-end changes |
| Team bandwidth vs. feature work | Reserve capacity explicitly; consider one dedicated owner |
| Never finishing | Each phase is independently shippable; stop-points are defined |

## What I'd push back on
- **Three months for "the whole module" is optimistic** if the code is poorly tested. If Phase 0 shows weak coverage or heavy coupling, expect the schedule to slip, or narrow the scope to the pure core plus the two or three highest-churn flows.
- **"It offends me" is a valid signal but a weak business case.** A stronger pitch ties the work to something measurable: faster changes to pricing, fewer incidents, easier onboarding, or lower audit risk. Even one such metric helps you defend the time and know when you're done.
- **Consider a smaller trial first.** Spend 2-3 weeks cleaning up just the calculation core. You'll learn how hard the full effort is, and you may find you get most of the benefit.

If you can tell me the language/framework, size of the module (rough LOC and number of callers), test coverage, and billing cycle length, I can tighten the phases and estimates.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / with skill / PASS

# Decision: don't schedule the 3-month rewrite yet. Run a 2-week debt assessment first.

## Rationale
- **No measurable benefit.** "It offends me" isn't a risk or a delivery cost. Without a baseline, you can't show the rewrite worked or justify its cost.
- **Billing is the worst place for a big-bang rewrite.** Six years of code encodes edge cases (proration, tax, refunds, grandfathered plans, retries) that nobody remembers and tests probably don't cover. A rewrite risks silent revenue errors, which are costly and hard to detect.
- **Opportunity cost.** Three months of engineering time has to buy something: faster delivery, fewer incidents, lower security or compliance risk.

## Trade-offs
| Option | Upside | Downside |
|---|---|---|
| Full rewrite, 3 months | Clean result | High regression risk, no incremental value, likely overruns |
| Do nothing | Zero risk now | Ugliness may be hiding real cost you haven't measured |
| **Assess, then strangler-style refactor (recommended)** | Targets only debt that costs something, and is reversible | Less satisfying than a clean slate |

## Next action: a 2-week assessment
1. **Classify the debt** across code, tests, architecture, data, infra, security, docs, and operations. Record each item with impact, cost of inaction, effort, risk, owner, and time horizon.
2. **Pull evidence from existing data:**
   - Change failure rate and incident history touching billing
   - Lead time for the last 10 billing changes, and how many were slowed by the structure
   - Churn hotspots (files changed most often) and their defect rates
   - Test coverage and flakiness in the billing paths
   - Dependency, security, and compliance gaps (PCI, tax rules, outdated libraries)
   - Time to onboard someone into this module
3. **Rank the findings.** If the evidence shows real cost, you have your business case. If it shows the module is ugly but stable and rarely touched, the right call is to leave it alone and spend the time elsewhere.

## If the assessment justifies action: incremental plan (about 3 months, scoped by evidence)
- **Weeks 1-3: safety net.** Add characterization tests around current behavior, covering invoices, proration, tax, and refunds. Capture production-like fixtures. No refactoring happens until this exists.
- **Weeks 3-6: seams.** Introduce interfaces at the module's boundaries (payment gateway, tax, persistence). This is the clean-architecture direction, but applied only where the hotspots are.
- **Weeks 6-11: strangler migration.** Move one capability at a time behind a feature flag. Run old and new paths in shadow mode and diff outputs on real traffic. Cut over gradually, with rollback at each step.
- **Week 12: sunset and record.** Delete the retired code, write ADRs for the decisions made, and update docs.

## Validation (define before starting)
- Baseline vs. target for lead time on billing changes, billing-related incidents, and coverage of critical paths
- Zero unexplained diffs between old and new paths in shadow mode before each cutover
- Reconciliation checks on invoiced totals

## Never-do list for this project
- No cutover without shadow-mode parity and a rollback path
- No refactoring of code that is stable, untouched, and not blocking anything

If you can share the pain points, such as which parts are slow to change, scary to touch, or tied to past incidents, I can turn this into a concrete scoped plan with estimates.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / baseline / PASS

# Billing Module Rewrite: 3-Month Plan

## A caution first

Billing is money-touching, has years of encoded edge cases (proration, tax, refunds, grandfathered plans), and the ugly code is often where those cases live. With no bug or delivery pain driving this, a big-bang rewrite is the highest-risk way to get clean architecture. I've planned this as an **incremental strangler migration**, which gets you to the same end state with a working system at every step and an exit ramp if priorities change.

## Target architecture

- **Domain**: pure business logic (Invoice, Subscription, Plan, Money, ProrationPolicy, TaxCalculation). No I/O, no framework imports.
- **Application**: use cases (CreateInvoice, ApplyPayment, ChangePlan, IssueRefund) that orchestrate the domain through ports.
- **Ports**: interfaces for persistence, payment gateway, tax provider, clock, event publisher, notifications.
- **Adapters**: DB repositories, gateway clients (Stripe etc.), HTTP/queue entry points.
- **Rules**: dependencies point inward only, enforced by lint or architecture tests. Money is a value type (integer minor units plus currency), and time comes from an injected clock.

## Phase 0: Weeks 1-2, Understand and protect

- Inventory the module: entry points, callers, DB tables, external integrations, scheduled jobs.
- Write **characterization tests** that pin current behavior, including the weird parts. Record real production scenarios (anonymized) as golden-file inputs and outputs.
- Build a catalog of business rules and edge cases, and get finance or support to confirm which are intentional.
- Define success metrics: reconciliation diff = 0, no change in invoice totals, test coverage on money paths, and so on.
- **Gate**: can you detect a behavior change automatically? If not, don't proceed.

## Phase 1: Weeks 3-5, Seams and domain core

- Introduce a facade over the old module so callers go through one interface.
- Extract the pure calculation logic first (pricing, proration, tax, discounts) into the new domain layer. This is the highest-value, lowest-risk piece.
- Run **shadow mode**: the new calculators run alongside the old code on live traffic, results are compared and logged, and the old result is still used.
- Fix or document every discrepancy.

## Phase 2: Weeks 6-9, Use cases and adapters

- Define ports, then implement adapters around the existing DB schema first. Don't change the schema and the code at the same time.
- Migrate use cases one at a time, lowest risk first (read paths and reporting, then invoice generation, then payments, then refunds and dunning).
- Each migration goes behind a feature flag with percentage rollout and instant rollback.
- Make payment-gateway calls idempotent, and add or verify webhook handling.

## Phase 3: Weeks 10-11, Data and cutover

- If the schema needs cleanup, use expand/contract migrations (add, dual-write, backfill, switch reads, drop). No destructive changes in this window.
- Complete the flag rollout to 100% for each use case. Run a full billing cycle (including month-end) on the new path with reconciliation.

## Phase 4: Week 12, Cleanup

- Delete the old code, the flags, and the shadow comparison harness.
- Write architecture docs and ADRs, and add architecture tests to CI.
- Retrospective: what did it cost, and what did it improve?

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Lost edge-case behavior | Characterization tests, shadow mode, finance sign-off |
| Scope creep ("while we're here...") | Behavior-preserving only. New features are frozen or go to the old path until cutover. |
| Month-end or billing-cycle timing | Don't cut over critical paths in the last week before a cycle. Schedule around it. |
| Feature work colliding with the rewrite | Agree on a rule: all changes land behind the facade, and new rules are written in the new domain layer |
| Timeline slip | Phases 0-2 deliver value on their own. You can stop after any phase with a better system than you started with. |

## Team and cost

Roughly 2-3 engineers full-time, plus part-time finance/support input for rule validation. Be explicit with stakeholders that the deliverable is **zero visible change**. The payoff is lower future change cost, so define how you'll know it worked (for example, time to ship a pricing change, or defect rate in billing).

## Questions that would sharpen this plan

1. What language and framework is the module in, and how big is it (LOC, tables, integrations)?
2. What is the current test coverage?
3. Is there an upcoming billing feature (new pricing model, new region, tax change)? Tying the rewrite to one gives it a business justification and a natural first slice.
4. How much frozen-feature tolerance does the business have for 3 months?

If you tell me the stack, I can turn Phase 0 and 1 into a concrete task breakdown with module boundaries and interface sketches.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / with skill / PASS

# Decision: I won't schedule the 3-month full rewrite as stated

My debt-management rules say refactoring needs a measurable risk reduction or delivery benefit. "It offends me" is a real signal, since code that annoys the people who work in it often hides cost, but it isn't yet a justification. Billing also makes a full rewrite one of the riskiest options available.

## Rationale
- **Money paths punish rewrites.** Six years of billing code encodes edge cases (proration, tax, refunds, grandfathered plans, rounding) that nobody remembers and tests don't cover. A rewrite drops them silently, and you find out through customer invoices.
- **Zero delivery benefit is claimed.** Three months of capacity goes to behavior that, at best, is identical to today's.
- **Big-bang rewrites tend to overrun** and leave you maintaining two systems.

## Trade-offs
| Option | Benefit | Cost/Risk |
|---|---|---|
| Full rewrite (3 mo) | Clean result, if it finishes | High revenue risk, no rollback, likely overrun |
| Do nothing | Zero risk now | Annoyance persists, hidden debt unquantified |
| **Measure, then strangle incrementally (recommended)** | Refactor only where it pays back, with rollback at each step | Less satisfying than a clean slate |

## Recommended plan

**Weeks 1-2: Turn the offense into data (time-boxed inventory)**
Classify debt across code, tests, data, ops, security, and docs. For the billing module, gather:
- Change frequency per file (git log churn) × defect history: hot, ugly files are the real targets; ugly files nobody touches are not.
- Lead time and review time for billing changes versus other modules.
- Test coverage and, more usefully, which behaviors have no characterization tests.
- Incidents, support tickets, and reconciliation errors tied to billing.
- Dependencies that are outdated or unsupported, and any security findings.
- Number of people who can safely change it (bus factor).

For each debt item, record: impact, cost of inaction, correction effort, risk, owner, time horizon.

**Decision gate (end of week 2):** If the data shows no cost (low churn, no incidents, no slowdown), the right call is to leave it alone, perhaps with only cosmetic cleanup when you're already touching a file. If it shows cost, you now have the business case.

**Weeks 3-12 (only if the gate passes): incremental strangler refactor**
1. **Characterization tests first.** Capture current outputs (golden-master invoices from production-like data) before changing anything.
2. **Carve seams** around the highest-churn, highest-risk areas (e.g., pricing/proration, tax, payment gateway adapter). Introduce clean-architecture boundaries (domain, use cases, adapters) one slice at a time, not module-wide.
3. **Shadow mode / dual-run:** run new logic alongside old and diff the results before cutting over.
4. **Feature flags per slice** with a tested rollback path. Data migrations should be backward compatible (expand/contract).
5. **Record decisions** as short ADRs, with sunset dates for legacy paths so the old code actually gets deleted.

Each slice gets a stated target, such as "cut lead time for pricing changes from X to Y" or "eliminate reconciliation mismatch class Z." If a slice can't name one, don't do it.

## Next action
Spend two days on the churn × incident analysis and the "who can safely change this" question. Share the top 5 hotspots and I can help turn them into a prioritized debt register and slice plan.

## Validation
- Golden-master diffs show zero unexplained invoice differences during shadow runs.
- Reconciliation error rate and billing incident count do not rise.
- The chosen metric (lead time, defect rate, onboarding time) improves per slice.
- Legacy code is removed on schedule, not left behind.
