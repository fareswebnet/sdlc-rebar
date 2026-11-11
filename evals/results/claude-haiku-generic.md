# Skill evaluation: haiku

Date: 2026-11-11  Runs per scenario: 3  Skills: compact

| Skill | Scenario | Baseline pass | With skill pass | Failures with skill |
|---|---|---|---|---|
| sdlc-api-integration-contracts | contract-breaking-change | 3/3 | 3/3 | - |
| sdlc-application-architecture | arch-microservices-default | 1/3 | 2/3 | forbidden /(?i)^\W*(recommend\w*|proposed|architecture)\W+.*microservices.*kafka/ present |
| sdlc-identity-access-multitenancy | authz-ui-hiding | 3/3 | 3/3 | - |
| sdlc-observability-reliability | alert-noise | 1/3 | 3/3 | - |
| sdlc-prd-requirements | prd-vague-verbs | 0/3 | 3/3 | - |
| sdlc-product-strategy | strategy-scope-creep | 3/3 | 3/3 | - |
| sdlc-release-production-readiness | release-unknown-rollback | 3/3 | 3/3 | - |
| sdlc-technical-debt-evolution | debt-refactor-for-taste | 3/3 | 3/3 | - |

Total: baseline 17/24, with skill 23/24.

String checks are a floor, not a quality judgement; read the replies for scenarios that fail.

## Replies

### sdlc-api-integration-contracts / contract-breaking-change / baseline / PASS

I wouldn't ship both changes today as a straight swap. Both are breaking changes for about 40 external integrators, and a rename or a new required field will fail their requests with no warning. I can't see your code here, so this is guidance rather than a diff.

**Why not today**
- Any integrator reading `customerName` breaks the moment the field disappears.
- Any integrator who doesn't send `phone` on POST /orders gets a 400 the moment it becomes required. Some may never have collected it.
- Integrators often can't deploy on your schedule, so a same-day break means incidents on their side and support tickets on yours.

**Safer path, still fast**

1. **Response rename (additive first):** Return both `customerName` and `client_name` with the same value. Announce `customerName` as deprecated, with a sunset date (typically 60–90 days out). Remove it only after that date, and only in a new API version if you have one.

2. **`phone` (soft-require first):** Keep accepting requests without `phone`, but log them and return a `Deprecation` or `Warning` header (or a warning field in the response). Switch to hard-required on the same sunset date or in a new version. If a field is required in v2 but optional in v1, v1 integrators keep working.

3. **Communicate today:** Send all 40 integrators a short notice with:
   - What changes, and the exact before/after JSON
   - The sunset date and the version it applies to
   - How to test against a sandbox or staging environment
   - A contact for questions

4. **Protect yourself:** Check your logs for which clients still send requests without `phone` and which read `customerName`. That tells you who is affected and who to contact directly.

**If you truly must ship a breaking change today**, do it behind a new version (e.g. `/v2/orders`, or an `Accept-Version` header) so existing integrators are unaffected, and only move the ones who opt in.

If you can share the relevant handler code, serializer, and validation schema, I can draft the exact changes for the additive approach, plus the deprecation header logic and the integrator notice.

### sdlc-api-integration-contracts / contract-breaking-change / with skill / PASS

## Decision

Don't ship either change as a breaking edit today. Ship an additive, backward-compatible change today, and schedule the breaking parts behind a version and a deprecation window.

## Rationale

- **Renaming `customerName` to `client_name`** breaks every integrator that reads the old key. Clients that parse strictly or map fields by name will fail silently or throw, and some may not surface the failure until a customer-facing incident.
- **Making `phone` mandatory in POST /orders** turns requests that succeed today into 400 errors. Any integrator that doesn't send `phone` will have order creation fail, which is a revenue-impacting outage for them.
- Forty external integrators almost certainly means a mix of release cadences. Some will not be able to ship a fix within a day, so a same-day breaking change can't be coordinated with all of them.

## Impacted consumers and compatibility

I can't see your repo, OpenAPI files, or consumer list, so these are the categories to confirm:

| Change | Breaks | Compatible? |
|---|---|---|
| Rename `customerName` → `client_name` (remove old) | All consumers reading `customerName` | No |
| Add `client_name`, keep `customerName` | None | Yes (additive) |
| `phone` required on POST /orders | Integrators not sending `phone` | No |
| `phone` optional but documented as recommended | None | Yes |

## Recommended plan

**Today (safe):**
1. Add `client_name` to the response alongside `customerName`, with identical values. Document both, mark `customerName` as deprecated in the OpenAPI spec.
2. Keep `phone` optional on POST /orders. Log or count requests that omit it, and mark it as `required` only in the next API version or behind an opt-in.
3. Send deprecation notices to all 40 integrators with the sunset date and migration guide.

**Later (after the window, e.g. 60–90 days, or per your policy):**
4. Remove `customerName` in a new major version (e.g. `/v2`), or after confirming via telemetry that no traffic still reads it.
5. Make `phone` required in `/v2` of POST /orders, or enforce it on v1 only after integrators confirm they send it.

## Trade-offs

- Dual fields add payload size and a short period of duplicate data to maintain.
- Shipping only additive changes today means the cleanup slips, but it avoids an outage you can't roll back on the integrators' side.
- If a business or legal requirement forces `phone` today, the only safe path is per-integrator opt-in, which needs their coordination anyway.

## Validation

- Contract diff: confirm the OpenAPI/response schema changes are additive only (no removed or renamed required fields).
- Contract tests against the existing consumer test suites, or a recorded sample of current requests and responses.
- Telemetry: count POST /orders requests missing `phone` and calls reading `customerName`, per API key or integrator, before any breaking step.
- Confirm the deprecation notice reached each integrator, with an owner for each.

## Next action

Tell me:
1. Is there an API version scheme today (e.g. `/v1`), and where is the OpenAPI spec?
2. Do you have per-integrator telemetry on `customerName` reads and `phone` omissions?
3. Is there a hard external deadline for `phone` (a regulation or partner requirement)? That changes the plan above.

If the answer to 3 is no, I'd send the additive change and the deprecation notice today, and schedule the breaking changes for the next version.

### sdlc-api-integration-contracts / contract-breaking-change / baseline / PASS

I'd push back on shipping both changes today. Both are breaking for external clients, and with 40 integrators you can't assume they'll update in time. A same-day rename breaks any client that reads `customerName`, and a newly required `phone` makes every existing POST without it fail with a 4xx. Neither can be undone once clients have deployed against the new behavior.

I can't open the repository here, so this is guidance rather than a diff.

## Recommended approach

**1. Rename: dual-emit, then remove.**
- Return both `customerName` and `client_name` with identical values for a deprecation window (e.g., 90 days).
- Document `customerName` as deprecated in the API docs and changelog.
- Send a notice to all 40 integrators with the sunset date.
- After the window, remove `customerName` in a new API version, or at minimum announce the removal date well ahead of time.

In most serializers this is a one-line addition, something like:

```python
# before
{"customerName": order.customer_name, ...}

# transition
{"customerName": order.customer_name,   # deprecated, remove after <date>
 "client_name": order.customer_name, ...}
```

**2. `phone` mandatory: stage the validation.**
- Ship now: keep accepting requests without `phone`, but log or count them and return a `Warning` header or a deprecation field in the response.
- Check your logs to see which integrators still omit it, and contact them directly.
- Enforce the requirement on a dated cutover, or put it behind a new version (`/v2/orders`) so `/v1` clients are unaffected.

**3. If you truly must ship a breaking change today,** the honest answer is that it needs a versioned endpoint and an explicit sign-off from whoever owns the integrator relationships. Even then, the rollout should be opt-in: integrators should be able to adopt it on their own schedule, not discover it through failed requests.

## Things to check before shipping anything

- Does any integrator consume responses with a strict schema or generated client? Those break on new fields too, though adding a field is usually safe.
- Are there internal consumers (webhooks, reports, SDKs) that also read `customerName`?
- Is there an OpenAPI spec or SDK that should be updated alongside the change?
- Do you have usage metrics per API key, so you can see who still sends requests without `phone`?

If you send me the relevant serializer, the POST /orders handler, and the validation code, I can draft the exact changes for the dual-emit and staged-validation approach. I can also draft the integrator notice.

### sdlc-api-integration-contracts / contract-breaking-change / with skill / PASS

## Decision

Don't ship the breaking change today. Ship a non-breaking change today, and schedule the rename and the phone requirement for a versioned release after a deprecation window.

## Rationale

- **Renaming `customerName` breaks any integrator that reads it.** Their code fails or silently drops data until they deploy a fix.
- **Making `phone` mandatory breaks any integrator that omits it.** Their `POST /orders` calls start returning 4xx.
- **Forty external integrators can't be coordinated in a day.** You can't roll back their deployments, and some won't see a notice until their next release cycle.

## Trade-offs

| Option | Pro | Con |
|---|---|---|
| Ship both breaking changes today | Fastest cleanup | Breaks an unknown number of integrations; hard to reverse for external consumers |
| Additive change today, breaking change in a new version later | No integrator breaks; you get usage data first | Two fields to maintain for a while; a longer timeline |
| Breaking change behind an opt-in header or version | Integrators migrate on their own schedule | Requires a version routing mechanism if none exists |

I recommend the second option, with the third if you already have versioning in place.

## Next actions

**Today (non-breaking):**
1. **Response:** add `client_name` with the same value as `customerName`. Mark `customerName` `deprecated: true` in the OpenAPI spec and document a sunset date.
2. **Response headers:** send `Deprecation` on responses that include `customerName`, and `Sunset` with the planned removal date.
3. **POST /orders:** keep `phone` optional. Add a metric and log for requests without it, tagged by API key, so you know exactly who will be affected.
4. **Notify all ~40 integrators** through your changelog and direct contact, with the timeline and migration steps.

**Later (new version, e.g., `/v2` or a dated `API-Version` header, after a window of at least 90 days):**
1. Remove `customerName` from the v2 response.
2. Make `phone` required in v2. Keep v1 behavior unchanged until its own sunset.
3. Publish a migration guide with before/after examples.

**Before any of this:**
- Pull 30 to 60 days of access logs per API key to find which integrators read `customerName` (if you can tell from logs) and which send requests without `phone`.
- Contact the integrators with the highest counts directly.

## Compatibility caveat

Adding `client_name` is safe for clients that ignore unknown fields. Clients with strict schema validation that reject unknown properties will break. Ask your largest integrators whether they validate strictly before you add the field.

## Validation

- Lint the OpenAPI spec and diff it against the previous version. The only changes should be the new field, the `deprecated` flag, and the new headers.
- Run existing consumer-contract tests (e.g., Pact, if you use it) against the new response. Old fixtures must still pass.
- Add a test for `POST /orders` without `phone` that confirms it still succeeds today.
- After release, watch the count of missing-`phone` requests per API key and the error rate on `POST /orders`. Both should stay flat.

## What I need to tailor this

I can't see your repository, so I'm assuming a generic setup. Please send:
- Your current API versioning scheme (URL path, header, or none).
- The location of your OpenAPI spec and any existing deprecation policy.
- Whether you have consumer-driven contract tests.
- Whether the business requirement is a hard deadline (for example, a legal or security reason). If it is, I can outline a narrower exception path, but it still needs a per-integrator plan.

### sdlc-api-integration-contracts / contract-breaking-change / baseline / PASS

Shipping both changes today would break your integrators, so I'd split this up rather than ship it as-is. Neither change is backward compatible:

- **Renaming `customerName` to `client_name`** breaks any integrator reading `customerName`. Their parsers may fail or silently get `null`.
- **Making `phone` mandatory in POST /orders** makes requests that currently succeed start returning 400s.

Changing a public API without notice can break 40 production integrations at once, and you can't roll back their deployed code. Here's what I'd do instead.

## Recommended plan

**Field rename (response):**
1. Add `client_name` to responses now, and keep `customerName` populated alongside it. Both fields coexist.
2. Document `customerName` as deprecated and give a removal date, typically 90 days or more for external consumers.
3. Notify all 40 integrators today with the timeline and migration steps.
4. Remove `customerName` only after the window closes and you've confirmed usage has dropped. Ideally you have usage metrics per API key to check this.

**Phone mandatory (request):**
1. Keep `phone` optional for now. Log and count requests that omit it, and identify which integrators are affected.
2. Return a `Warning` header or deprecation notice on requests without `phone`.
3. Enforce it in a new API version (e.g., `/v2/orders`) or after a announced grace period. Don't flip it on the existing version without notice.

**Versioning:** If your API has a version scheme, the cleanest option is to ship these as v2 changes and leave v1 unchanged. Otherwise, the additive-then-deprecate approach above works on the current version.

## What can ship today

- Additive `client_name` in responses (non-breaking, if integrators ignore unknown fields)
- Deprecation headers or docs updates
- Logging of missing `phone` values
- Changelog and integrator notification

## Before you ship anything, check

- Do integrators' clients use strict deserialization that rejects unknown fields? If so, even adding `client_name` can break them.
- Is there a contractual notice period for API changes?
- Who owns the integrator relationships, so someone can notify them today?

If the deadline is driven by a specific business need, tell me what it is. I can help scope a smaller change that meets it without breaking anyone. I can't inspect the repository in this session, so if you paste the relevant handler code or response schema, I can draft the exact changes.

### sdlc-api-integration-contracts / contract-breaking-change / with skill / PASS

## Decision

Don't ship either change as a breaking change today. Ship an additive, backward-compatible change today, and schedule the breaking part (the rename and the required `phone`) behind a new API version with a published sunset date.

## Rationale

- **Renaming `customerName` breaks every consumer that reads it.** Integrators parse by field name, so a silent rename can break 40 clients at once, possibly without their knowing it.
- **Making `phone` required turns every `POST /orders` call without it into a 400.** Any integrator that doesn't send `phone` today will fail in production as soon as this ships.
- **Same-day shipping leaves no time for notice.** Integrators can't adapt to a change they haven't been told about. Check your existing deprecation policy first. If none exists, 60–90 days' notice is a reasonable default for a public API.

## Trade-offs

| Option | Pros | Cons |
|---|---|---|
| A. Ship both breaking changes today | Fastest, simplest | Likely breaks multiple integrators in production; high support load |
| B. Additive now, breaking in `/v2` later (recommended) | No consumer breaks; clean cutover | Two fields and two code paths during the overlap; v1 maintenance cost |
| C. Additive now, breaking changes in place on `/v1` with a sunset date | No new version to host | Still breaks clients on the sunset date; needs strong comms |

## What to ship today (additive, non-breaking)

1. **Add `client_name` to the response and keep `customerName`.** Both carry the same value. Mark `customerName` as deprecated.
2. **Keep `phone` optional on `POST /orders`, but document it as recommended.** Log requests missing `phone` and emit a `Deprecation` header (and `Sunset` once a date is set) so you can see which integrators still omit it.
3. **Announce the plan** with the new field, the deprecated field, the sunset date, and the `phone` enforcement date.

Example OpenAPI fragment for the response (adjust to your existing spec):

```yaml
components:
  schemas:
    Order:
      type: object
      properties:
        client_name:
          type: string
          description: Customer name. Replaces customerName.
        customerName:
          type: string
          deprecated: true
          description: Deprecated. Same value as client_name. Removed in v2 (sunset YYYY-MM-DD).
```

## Next actions

1. **Identify impacted consumers.** Pull API logs for the last 30–90 days and list which integrators read `customerName` (if your logs capture response fields, otherwise use a usage proxy) and which send `POST /orders` without `phone`. Map each to an owner and contact.
2. **Confirm the deprecation policy and sunset window** with product and support. Put the dates in the changelog.
3. **Notify all ~40 integrators today** with the timeline, the migration guide, and a contact for questions.
4. **Plan `/v2`**, which removes `customerName` and requires `phone`. Keep `/v1` running until the sunset date passes.

## Validation

- Contract tests on `/v1` confirm `customerName` and `client_name` are both present with identical values, and that a `POST /orders` without `phone` still succeeds with the deprecation header.
- Contract tests on `/v2` confirm `customerName` is absent, `client_name` is present, and `phone` is required (missing `phone` returns 400 with a clear error message).
- Monitor the count of requests missing `phone` and the number of integrators still reading `customerName` until the sunset date. Don't enforce either change until those counts reach zero or the owners have confirmed their migration.

If you can share your current OpenAPI spec, deprecation policy, and whether you already have a versioning scheme, I can draft the exact spec diff and the integrator notice.

### sdlc-application-architecture / arch-microservices-default / baseline / FAIL

# Architecture: B2B Invoicing App (4 engineers, 200 customers, 50 rps peak)

**Recommendation:** Build a **modular monolith** on a managed platform, backed by PostgreSQL and a background job queue. Don't use microservices, Kubernetes, or Kafka yet. The load is small, and a team of four can't carry the operational cost of a distributed system. The design below keeps the option to split services later.

## Why not microservices, Kubernetes, and Kafka now

Netflix runs thousands of services for hundreds of engineers across many teams, with millions of requests per second. Those tools solve coordination and scaling problems you don't have.

| Concern | Your actual situation |
|---|---|
| Throughput | 50 rps peak is modest. One well-tuned Postgres and 2–3 app instances handle this with large headroom. |
| Customers | 200 tenants. Multi-tenancy is a data-modeling concern, not a scaling one. |
| Team | 4 engineers. Every service adds deploy pipelines, auth, observability, and on-call burden. |
| Kafka | Designed for high-volume event streams with many independent consumers. You have a handful of background jobs. |
| Kubernetes | Requires someone who can run clusters, networking, and upgrades. That is probably a full-time role. |

Distributed systems also make invoicing harder. Issuing an invoice, reserving a sequential number, recording a payment, and updating a ledger are transactional operations. Splitting them across services turns simple database transactions into sagas and compensations, which adds bugs in exactly the places where money is involved.

## High-level design

```
          ┌──────────────┐
Customers │  CDN / WAF   │
 (browser,└──────┬───────┘
  API)          │
          ┌──────▼───────┐
          │ Load balancer│  (managed: ALB / Cloud LB / Fly / Render)
          └──────┬───────┘
     ┌───────────┴───────────┐
┌────▼─────┐           ┌─────▼────┐
│ Web/API  │  x2–3     │ Worker   │  x1–2 (same codebase, different entrypoint)
│ (monolith)│          │ (jobs)   │
└────┬─────┘           └─────┬────┘
     │                       │
     ├──────────┬────────────┤
┌────▼─────┐ ┌──▼─────────┐ ┌▼──────────────┐
│PostgreSQL│ │ Redis or   │ │ Object storage│
│(primary+ │ │ queue table│ │ (S3) for PDFs │
│ replica) │ └────────────┘ └───────────────┘
└──────────┘
     External: Stripe (payments), SES/Postmark (email), tax API, auth provider
```

## Code structure

One repository, one deployable application, with strict module boundaries enforced by directory layout and lint rules:

```
app/
  modules/
    tenancy/        # orgs, users, roles, API keys
    customers/      # billing contacts of each tenant's clients
    invoicing/      # invoice lifecycle, numbering, line items
    payments/       # Stripe integration, webhooks, reconciliation
    tax/            # tax rules and calculation (or external API adapter)
    documents/      # PDF rendering, storage
    notifications/  # email templates and sending
    reporting/      # read-only aggregates
    audit/          # append-only audit log
  shared/           # money type, ids, time, errors
  web/              # HTTP controllers/routes (thin)
  jobs/             # background job handlers (thin)
```

Rules that keep the monolith split-ready:
- Modules talk through **public service interfaces**, not each other's tables or internal classes.
- Each module **owns its tables**. Other modules read through its interface.
- No cross-module foreign-key shortcuts in code that would be painful to untangle later.
- A lint or architecture test (e.g., ArchUnit, import-linter, dependency-cruiser) fails the build on violations.

## Data design

**PostgreSQL** is the system of record.

- **Multi-tenancy:** every tenant-scoped table has `tenant_id`, indexed and included in every query. Consider Postgres Row-Level Security as a second layer of defense.
- **Money:** store amounts as integers in minor units (`amount_minor BIGINT`) plus `currency CHAR(3)`. Never use floats.
- **Invoice numbers:** sequential per tenant, gap-free if your jurisdiction requires it. Allocate them inside the issuing transaction using a row lock on a per-tenant counter table.
- **Immutability:** once an invoice is issued, its lines and totals are never edited. Corrections are made with credit notes. Enforce this in code and optionally with a trigger.
- **Idempotency:** payment webhooks and API create calls take an idempotency key, stored with a unique constraint.
- **Audit log:** append-only table of who did what, when, and the before/after state. Treat it as a compliance feature.
- **Timestamps:** store UTC. Store the tenant's timezone for display and for due-date logic.

## Async work and events

Use a **job queue**, not Kafka:

- Start with a Postgres-backed queue (pg-boss, Solid Queue, Oban, Graphile Worker, or Django/Rails equivalents) or Redis/SQS if you already use it.
- Jobs to offload: PDF generation, email sending, Stripe webhook processing, reminder schedules, nightly reconciliation, report exports.
- Use the **transactional outbox pattern** for domain events: write an `outbox` row in the same transaction as the state change, then a worker publishes or dispatches it. This gives you reliable events without Kafka, and you can later point the relay at Kafka with minimal change.

## Infrastructure

- **Compute:** a managed container platform. Good options: Render, Fly.io, Google Cloud Run, AWS ECS on Fargate, or Heroku. Two to three web instances and one or two worker instances to start.
- **Database:** managed PostgreSQL (RDS, Cloud SQL, Neon, Supabase, or the platform's offering) with automated backups, point-in-time recovery, and one read replica when reporting load justifies it.
- **Storage:** S3 or equivalent for generated PDFs, with signed URLs for download.
- **Redis:** only if you need caching or the queue requires it.
- **Secrets and config:** the platform's secret manager. No secrets in the repo.
- **IaC:** Terraform or the platform's config file, checked into the repo.
- **CI/CD:** GitHub Actions (or equivalent). Run tests, lint, architecture checks, and migrations on each PR. Deploy main to staging, promote to production with a manual gate.
- **Environments:** dev, staging (mirrors prod shape), production.

## Cross-cutting concerns

- **Auth:** a managed identity provider (Auth0, Clerk, Cognito, WorkOS for enterprise SSO). Don't build auth yourselves.
- **Authorization:** role-based per tenant, enforced in the service layer, not just the controllers.
- **Observability:** OpenTelemetry traces and metrics, structured logs with `tenant_id` and `request_id`, Sentry for errors, and alerts on error rate, p95 latency, queue depth, and failed payment webhooks.
- **Backups and DR:** PITR on Postgres, a tested restore procedure, and a documented RPO/RTO. Test restores quarterly.
- **Security:** TLS everywhere, encrypted at rest, least-privilege DB roles, dependency scanning, rate limiting on public endpoints, and a SOC 2 readiness checklist if B2B customers will ask for it.
- **Testing:** unit tests for invoice and tax logic (property tests for money math are worth it), integration tests against a real Postgres, and a small set of end-to-end tests for the core invoice-to-payment flow.

## Capacity check

At 50 rps peak with typical CRUD and PDF work:
- A single app instance can usually serve hundreds of simple requests per second. Two instances plus autoscaling give redundancy.
- Postgres on a mid-size managed instance handles far more than this. Watch connection counts (use PgBouncer or the platform's pooler) and index queries that scan tenant data.
- PDF generation is the likeliest bottleneck. Keep it in workers and scale workers independently.

Load-test once before launch. Expect the bottleneck to be a query or a PDF job, not the architecture.

## Phased roadmap

1. **Weeks 1–4:** Tenancy, customers, invoice create/issue/void, numbering, PDF generation, email delivery, audit log, CI/CD, staging.
2. **Weeks 5–8:** Stripe payments and webhooks, payment reconciliation, reminders, customer portal, basic reporting.
3. **Weeks 9–12:** Tax integration, SSO, export/import, observability dashboards, load test, backup/restore drill, security review.
4. **Ongoing:** Harden, add features, and watch the metrics that would trigger a split.

## When to revisit the architecture

Split a module into its own service or add Kafka only when you see concrete signals, such as:

- **Team size:** more than about 3 teams working on the codebase and stepping on each other in releases.
- **Independent scaling:** one module (e.g., PDF rendering or reporting) needs to scale very differently from the rest and the worker pool isn't enough.
- **Event volume:** sustained throughput in the thousands of events per second, or many independent consumers needing the same event stream.
- **Compliance or isolation:** a regulator or large customer requires a dedicated data boundary (e.g., a separate payments-data service).
- **Measured pain:** deploy queues, shared-database contention, or on-call incidents that clearly trace to module coupling.

When one of these happens, extract that module behind the interface it already has, publish events from the outbox to Kafka (or a managed alternative such as SNS/SQS or Google Pub/Sub), and move it to its own deployable. The boundaries you enforced early make this a contained change.

## Talking to the CTO

Frame it as a decision with explicit criteria, not a rejection of their instinct:

- Acknowledge that Netflix's architecture fits Netflix's scale and team size. The same tools would make this team slower.
- Offer a written ADR (architecture decision record) comparing options on delivery speed, operational load, transaction correctness, and cost.
- Propose the trigger conditions above so microservices become a planned step, not a debate about fashion.
- If the CTO wants separation now, the compromise is two deployables (API and worker) from one codebase, with a managed queue. That gives the operational separation without the distributed-systems cost.

### sdlc-application-architecture / arch-microservices-default / with skill / PASS

# Architecture Proposal: Modular Monolith on Postgres, with Outbox and Worker

**Recommendation:** Build one deployable backend organized as a modular monolith, with one primary Postgres database, a transactional outbox, and a separate worker process for background jobs. Defer Kubernetes and Kafka. Extract a service only when a measured constraint justifies it.

I haven't inspected a repository, so I'm assuming a greenfield project and a stack choice to be confirmed. Where the assumptions are wrong, the design changes.

## Decision

| Concern | Choice |
|---|---|
| Deployable units | 1 API process + 1 worker process (same codebase, different entrypoints) |
| Runtime | 2 to 3 container instances behind a managed load balancer, on a managed container platform (ECS Fargate, Cloud Run, or Fly.io). Kubernetes is optional, not required |
| Data | Single Postgres (managed, with a read replica when reporting load demands it) |
| Async work | Postgres-backed job queue (`SELECT ... FOR UPDATE SKIP LOCKED`) for jobs; transactional outbox for integration events |
| Kafka | Not now. Introduce only if you have multiple independent consumers of the same event stream at high volume |
| Caching | None initially. Add Redis only when a measured query is a bottleneck |

## Modules and Dependency Rules

Organize by bounded context, not by technical layer:

- `customers`: accounts, contacts, tax IDs
- `catalog`: products, price lists
- `invoicing`: invoice aggregate, lifecycle (draft, issued, paid, void), numbering
- `payments`: payment records, provider integration
- `tax`: VAT/tax calculation rules
- `documents`: PDF rendering, e-invoice formats
- `notifications`: email and webhook delivery
- `identity`: auth, tenants, roles

Each module follows ports and adapters:

```
module/
  domain/        # entities, value objects, rules; no framework imports
  application/   # use cases; depends on domain and ports
  ports/         # interfaces for repositories, gateways, clock, events
  adapters/      # HTTP handlers, Postgres repos, payment provider clients
```

**Enforced rules:**
- Modules talk to each other only through their public application API or emitted events, never by reaching into another module's tables.
- Domain code imports nothing from adapters or frameworks.
- Enforce this with an architecture test (for example, ArchUnit, dependency-cruiser, or import-linter) that fails the build on violations.

## Transaction Boundaries

- **One aggregate per transaction.** Creating or issuing an invoice, including its line items and its number, commits in a single transaction.
- **Invoice numbering** must be gapless per legal entity if your jurisdiction requires it. Use a `number_sequence` row locked with `SELECT ... FOR UPDATE` inside the issuing transaction. Don't use a Postgres `SEQUENCE`, because sequences are not rolled back and can leave gaps.
- **Cross-module side effects** (send email, call the payment provider, push to the tax authority) never happen inside the request transaction. The transaction writes an row to the `outbox` table. A worker reads outbox rows after commit and performs the side effect.
- **Consumers must be idempotent.** Use an idempotency key per side effect, stored in the database.

## Failure Handling

- Outbox worker: retries with exponential backoff and jitter. After N attempts, the row moves to a `dead_letter` status and triggers an alert.
- External calls (payment provider, tax service): timeouts, circuit breaker, and a retry budget. Failed calls surface as a visible status on the invoice, not as a silent 500.
- Duplicate client submissions: require an `Idempotency-Key` header on POST endpoints that create or issue invoices.
- Worker crashes: `SKIP LOCKED` leases with a visibility timeout. Jobs are reclaimed automatically.

## Deployment Implications

- Two artifacts (API and worker) from one build. Rolling deploys with migrations run as a separate step, using expand-and-contract migrations so old and new code can coexist.
- Tenant isolation: shared schema with `tenant_id` on every table, enforced by row-level security in Postgres. Revisit if a customer requires dedicated infrastructure.
- Backups and point-in-time recovery from the managed database provider. Test a restore quarterly.

## Load Math

At 50 rps peak, a single well-written API instance usually handles several hundred rps for typical CRUD-with-validation workloads. Two instances plus a read replica give substantial headroom, and vertical scaling of Postgres buys more. At 200 customers, the expected write volume is small. The risk is in query design and PDF rendering, not in service count.

## Why Not Microservices, Kubernetes, and Kafka Now

- **Team capacity:** With 4 engineers, each service adds a deployable, a pipeline, a schema, a dashboard, an on-call surface, and a versioning contract. Those costs compete directly with product work.
- **Distributed transaction cost:** Invoicing crosses customers, catalog, tax, and payments. Splitting them turns simple atomic operations into sagas with compensation logic.
- **Netflix comparison:** Netflix runs these tools for hundreds of engineering teams and very different scale and reliability problems. Their choices fit their constraints, not yours.
- **Kafka specifically:** It is a durable log with consumer groups and operational overhead (brokers, partitions, schema registry, lag monitoring). The outbox plus a Postgres queue covers your current delivery needs with no new infrastructure.

## Triggers to Revisit

Extract a module into its own service only when a measured signal shows it:
- **Scaling:** one module needs a different scaling profile (e.g., PDF rendering consuming most CPU, so it moves to a separate worker pool first, which is a deployment change, not a service rewrite).
- **Compliance:** a module needs isolated data residency or audit boundaries.
- **Team:** more than about 2 teams contend for the same module's release cadence.
- **Event volume:** the outbox table or job queue sustains high throughput that Postgres handles poorly, and multiple independent consumers need replay. That is the point to evaluate Kafka or a managed alternative.

Because modules already have ports and clean boundaries, extracting one later means replacing an in-process adapter with a network adapter, not rewriting domain logic.

## ADRs to Create

1. **ADR-001: Modular monolith over microservices.** Context: team of 4, 50 rps peak, 200 customers. Decision: single deployable with enforced module boundaries. Consequence: extraction is a deliberate later step with trigger criteria above.
2. **ADR-002: Postgres as the job queue and outbox store.** Consequence: no Kafka until event volume or consumer count requires it.
3. **ADR-003: Transactional outbox for cross-module and external side effects.** Consequence: all integration is at-least-once; consumers must be idempotent.
4. **ADR-004: Gapless invoice numbering via locked sequence row.** Consequence: serialized issuance per legal entity; acceptable at current volume. Confirm the legal requirement first.
5. **ADR-005: Shared schema with tenant_id and row-level security.** Consequence: one migration path; per-tenant isolation requires a later change.
6. **ADR-006: Managed container platform instead of self-managed Kubernetes.** Consequence: less operational work; revisit if platform requirements change.

## Next Actions

1. Confirm assumptions: language and framework, jurisdiction and e-invoicing mandates (affects numbering and document formats), data residency, and expected tenant growth.
2. Write ADRs 001 to 006 and review them with the CTO. Frame the discussion around the trigger criteria, so the decision is about when to split, not whether to ever split.
3. Scaffold the module layout and add the architecture test before writing feature code, so boundaries are enforced from day one.
4. Build the invoicing issuance path end to end first: transaction, numbering, outbox row, worker, and idempotency key.

## Validation

- **Load test** with k6 or Gatling at 5x peak (250 rps) against staging with production-like data volume. Targets: p95 under an agreed threshold (for example, 300 ms for issuance), zero errors at target load, and connection pool headroom.
- **Concurrency test** for invoice numbering: 100 parallel issuances per legal entity must produce a gapless, unique sequence.
- **Failure test:** kill the worker mid-job and kill the API between commit and response. Confirm no duplicate emails or payments and no lost outbox rows.
- **Query review:** `EXPLAIN ANALYZE` on the top 10 endpoints' queries before launch.
- **Architecture test** runs in CI and fails on any cross-module table access or domain-to-adapter import.
- **Restore drill:** restore a backup to a new instance and verify invoice totals reconcile.

### sdlc-application-architecture / arch-microservices-default / baseline / PASS

# Architecture Proposal: B2B Invoicing App

## Recommendation

Build a **modular monolith** on a **managed container platform**, backed by **managed PostgreSQL** and a **Postgres-backed job queue**. Keep the module boundaries strict so any module can become a separate service later. Don't adopt Kubernetes or Kafka yet.

## Why not microservices, Kubernetes, and Kafka now

The load is small. 50 requests/second at peak is roughly what one well-written app instance with a single Postgres primary handles comfortably. A typical setup for this load is 2 to 3 app instances behind a load balancer. The same workload fits on a single small managed database.

Netflix's architecture solves problems this product doesn't have: thousands of engineers deploying independently, hundreds of services, and millions of events per second. Their microservices exist because of their team size, and the same is true of most companies that adopted them early.

With four engineers, the operational cost is the main risk:

| Component | Ongoing burden |
|---|---|
| Kubernetes | Cluster upgrades, networking, ingress, secrets, Helm/manifests, autoscaling tuning |
| Kafka | Brokers or managed cluster, topic/schema management, consumer lag, rebalancing, retention, exactly-once semantics |
| N services | N pipelines, N deployment configs, N sets of logs and dashboards, distributed tracing across network hops |
| Distributed data | Cross-service consistency (sagas, outbox, compensations) for operations a single transaction handles trivially |

Realistically, this stack would consume one or two engineers' time on platform work, leaving the other two to build a product that needs to be correct before it is fast.

For invoicing specifically, the most important guarantees are transactional: an invoice number is allocated exactly once, a payment is applied exactly once, and a finalized invoice doesn't change. A single database transaction gives you these guarantees directly. Splitting them across services makes them harder to get right.

## Target architecture

```
              ┌────────────────────┐
  Browser/ ──▶│  CDN + WAF         │
  API client  └─────────┬──────────┘
                        ▼
              ┌────────────────────┐        ┌──────────────────┐
              │  Load balancer     │        │ Identity provider│
              └─────────┬──────────┘        │ (OIDC, SSO/SAML) │
                        ▼                   └──────────────────┘
        ┌──────────────────────────────────┐
        │  App (modular monolith)          │
        │  ├─ tenancy & users              │
        │  ├─ customers (billed parties)   │
        │  ├─ invoices & numbering         │
        │  ├─ payments & reconciliation    │
        │  ├─ tax rules                    │
        │  ├─ documents (PDF)              │
        │  ├─ notifications                │
        │  └─ reporting (read-only)        │
        │  Runs as 2–3 instances           │
        └──────┬───────────────┬───────────┘
               ▼               ▼
  ┌──────────────────┐  ┌──────────────────┐   ┌───────────────┐
  │ PostgreSQL       │  │ Job queue        │──▶│ Worker        │
  │ (managed, multi- │  │ (in Postgres or  │   │ (same codebase│
  │  AZ, PITR)       │  │  Redis-backed)   │   │  other entry) │
  │ outbox table     │  └──────────────────┘   └──────┬────────┘
  │ audit log        │                                ▼
  └──────────────────┘                    ┌────────────────────────┐
                                          │ Object storage (PDFs,  │
                                          │ attachments, hashes)   │
                                          └────────────────────────┘
  External: payment provider (webhooks), email provider, tax service (if multi-jurisdiction)
  Observability: OpenTelemetry → hosted APM/logs; error tracking (e.g., Sentry)
```

### Components

**Application.** One codebase with explicit modules. Each module owns its tables and exposes an internal interface. Other modules call that interface, never each other's tables. A lint rule or architecture test enforces this. Keep the database schema per module (separate schemas in Postgres) so extraction later is a deployment change, not a rewrite.

**Hosting.** Use a managed container platform: AWS ECS Fargate or App Runner, Google Cloud Run, or a PaaS such as Render or Fly.io. Set a minimum of two instances across availability zones. Use managed deploys with rolling updates and health checks.

**Database.** Managed PostgreSQL with multi-AZ failover and point-in-time recovery. Enable row-level security keyed on `tenant_id` as a defense against cross-tenant data leaks. Add a read replica only when reporting queries affect the primary.

**Background jobs.** PDF rendering, emails, webhook delivery, reminder schedules, and reconciliation run as jobs. Start with a queue in Postgres (pg-boss, Graphile Worker, or the equivalent for your stack). Move to Redis-backed queues only if you outgrow it, which is unlikely at this volume.

**Events.** Write domain events to an **outbox table in the same transaction** as the state change. A relay process publishes them to the job queue or to webhooks. This gives reliable event delivery without a message broker. Add Kafka only when several independent consumers need replayable event streams at high volume.

**Storage.** Object storage (S3 or equivalent) for generated PDFs and attachments. Store a content hash in the database and make the PDF immutable once the invoice is issued.

**Identity.** Use a managed provider (WorkOS, Auth0, Clerk, Cognito) rather than building auth. B2B customers will ask for SSO and SAML, which these providers handle.

**Observability.** OpenTelemetry instrumentation, a hosted backend (Grafana Cloud, Datadog, or similar), structured logs with tenant and request IDs, and alerts on error rate, p95 latency, queue depth, and payment webhook failures.

**Delivery.** Infrastructure as code (Terraform or Pulumi), CI on pull requests with tests and migrations checked, and separate staging and production environments.

## Invoicing correctness requirements

These matter more than the infrastructure choices:

- **Money** is stored as integer minor units plus an ISO currency code. Never use floats.
- **Invoice numbers** are gapless per tenant and series. Allocate them with a per-series counter row locked inside the issuing transaction. Don't use a global Postgres sequence, because rolled-back transactions create gaps.
- **Issued invoices are immutable.** Corrections happen through credit notes and new invoices, never edits. Enforce this in the database with triggers or status checks.
- **Idempotency keys** on all create, issue, and payment endpoints, so client retries don't double-charge or double-issue.
- **Payment webhooks** are verified by signature and processed idempotently by provider event ID.
- **Audit log** is append-only and records who changed what and when.
- **Tax** starts as a configurable rule table. Move to a tax service (Avalara, TaxJar) only when you need multi-jurisdiction compliance.
- **Snapshots:** store the customer's billing details and line-item prices on the invoice at issue time, so later edits to customer or product records don't alter historical invoices.

## Capacity check

Rough sizing for 200 customers and 50 rps peak:

- 2 app instances (small, e.g., 1 vCPU / 2 GB each) with autoscaling to 4.
- 1 managed Postgres instance with multi-AZ standby, sized for a few GB of data.
- 1 small worker group.
- Expected monthly infrastructure cost is in the low hundreds of dollars, not thousands.

Measure before scaling. Load-test the invoice-issue and payment-webhook paths, and check PDF rendering time, since it's usually the slowest step.

## Path to services, if the business needs it

Plan for extraction, but trigger it with evidence, not with a diagram. Extract a module into a separate service when at least one of these is true:

1. It needs to scale independently. PDF rendering is the most likely candidate, and it already runs as a separate worker.
2. A separate team owns it and needs independent release cadence.
3. It has different compliance or data-residency requirements.
4. It has a different availability or performance profile that the monolith can't meet.

Adopt Kafka when you have multiple services that need the same event stream, replay, or sustained event volume in the thousands per second. Adopt Kubernetes when you have enough services that managing them with the platform's native deploy tooling becomes the bottleneck.

## Suggested position for the CTO

- The architecture supports microservices later. Module boundaries, per-module schemas, and an outbox make extraction a refactor, not a rewrite.
- Kubernetes and Kafka would add operational work that the team can't absorb at four engineers, for load the system won't see for a long time.
- Set explicit triggers for revisiting the decision, such as the criteria above, and review them quarterly.
- Start with the modular monolith, measure real load, and revisit once you have data.

### sdlc-application-architecture / arch-microservices-default / with skill / PASS

# Architecture Proposal: B2B Invoicing App

**Recommendation:** Build one deployable modular monolith with strict internal module boundaries, backed by PostgreSQL. Run it on a managed container platform. Use the transactional outbox pattern for events. Defer Kafka and Kubernetes until measured constraints require them.

I had no repository or tooling access for this, so this is based only on the numbers and constraints you gave me. If you share the existing codebase, I can check these choices against its patterns.

## 1. Why not microservices, Kubernetes, and Kafka

The load you described is small:

- **50 rps at peak** is comfortably served by 2 to 3 instances of a single Java, Node, Go, or Python service. Most of that capacity goes unused.
- **200 customers** is a small B2B tenant base, not consumer-scale traffic.
- **A team of 4** cannot realistically operate 5+ services, a Kubernetes cluster, a Kafka cluster, distributed tracing, and per-service CI/CD. That operational load would consume most of the team's capacity, and the product would move slower.

Netflix runs microservices because it has hundreds of teams, very large scale, and needs independent deployment across many domains. Those conditions don't apply here. Adopting their architecture without their constraints would add cost without a matching benefit.

What microservices would cost you:
- Distributed transactions around invoice issuance, which is the core correctness-sensitive operation
- Network failures between services that a function call would not have
- Multiple deployment pipelines, service discovery, and cluster upgrades to maintain
- Local development that is much harder to run and debug

The modular monolith keeps the boundary benefits (clear ownership, testable modules, a path to extraction) without these costs.

## 2. Module structure and dependency rules

```
app/
  modules/
    identity-tenancy/   # users, roles, tenant (customer org) isolation
    customers/          # bill-to parties, contacts, tax IDs
    catalog/            # products/services, price lists
    invoicing/          # Invoice aggregate, line items, status lifecycle, numbering
    tax/                # tax rules and calculation (pure logic)
    payments/           # payment records, provider webhooks, reconciliation
    documents/          # PDF rendering (port to renderer adapter)
    notifications/      # email/webhook delivery (port to provider adapter)
    reporting/          # read models, exports
  platform/
    db/ outbox/ jobs/ http/ auth/ observability/
```

Dependency rules, enforced by a CI check (ArchUnit-style for JVM, dependency-cruiser for TS, or an import-linter for Python):

- Domain code (`invoicing`, `tax`) imports nothing from frameworks, ORMs, HTTP, or adapters.
- Modules talk to each other through published interfaces or domain events, not by reaching into each other's tables.
- Adapters (Postgres repositories, email provider, PDF renderer, payment provider SDK) sit behind ports and are injected at the composition root.
- Each module owns its database schema. Cross-module joins go through read models or are restricted to the reporting module.

## 3. Transaction boundaries and key flows

**Issue invoice** (the critical path), in one local database transaction:
1. Lock the tenant's numbering sequence row (`SELECT ... FOR UPDATE`) and assign the next invoice number. Gapless numbering is often a legal requirement, so do not use Postgres sequences for it, since they are not transactional and leave gaps on rollback.
2. Validate totals and tax via the `tax` module.
3. Set status to `ISSUED` and write the invoice.
4. Insert an `invoice.issued` row into the `outbox` table.

Commit. Nothing outside the database is called inside this transaction.

**Outbox relay and jobs:** A worker process (same image, different entrypoint) polls the outbox and job tables using `SELECT ... FOR UPDATE SKIP LOCKED`. It generates the PDF, stores it in object storage, and sends the email. Each job is idempotent and keyed by invoice ID and version.

**Failure handling:**
- PDF or email failure does **not** roll back issuance. The invoice is already legally issued. The job retries with exponential backoff and moves to a dead-letter state after N attempts, with an alert.
- Payment provider webhooks are deduplicated by the provider's event ID and stored before processing. Processing is idempotent, so retries are safe.
- Every state transition writes an audit record in the same transaction as the change.

## 4. Deployment

- **One container image**, deployed as two process types: `web` (2 instances minimum for availability) and `worker` (1 to 2 instances).
- **Managed platform** such as AWS ECS/Fargate, Google Cloud Run, Azure Container Apps, or a PaaS like Render or Fly.io. Avoid running your own Kubernetes cluster.
- **Managed PostgreSQL** with automated backups, point-in-time recovery, and a read replica only if reporting load demands it.
- **Object storage** for generated PDFs, with retention rules that match your legal requirements.
- **Environments:** local (docker-compose with Postgres), staging (mirrors production topology), production.
- **CI/CD:** one pipeline, one artifact, with database migrations run as a separate, reviewed step.

## 5. Architecture Decision Records

**ADR-001: Modular monolith over microservices.** Decision: one deployable with enforced module boundaries. Rationale: team size of 4, load of 50 rps, and a need for consistent transactions on invoice issuance. Trade-off: all modules scale together and share a release cadence. Revisit when the triggers in section 7 apply.

**ADR-002: PostgreSQL as system of record, job queue, and outbox.** Decision: no separate broker for jobs or events at this stage. Rationale: transactional consistency with business writes, fewer moving parts, and sufficient throughput. Trade-off: the outbox relay is a polling design, so it adds latency measured in seconds rather than milliseconds.

**ADR-003: Transactional outbox, Kafka deferred.** Decision: publish domain events via the outbox. Rationale: events are guaranteed to match committed data, and swapping the relay to Kafka later is a localized change. Trade-off: one more table and worker to maintain.

**ADR-004: Managed container platform, not Kubernetes.** Decision: a managed service that runs containers without cluster administration. Rationale: the team has no dedicated platform engineer. Trade-off: less control over networking and scheduling, and possibly higher unit cost at large scale.

**ADR-005: Gapless invoice numbering via locked per-tenant counter.** Decision: assign numbers inside the issuance transaction using a row lock. Rationale: legal gapless requirements, plus correctness under concurrency. Trade-off: issuance for a single tenant serializes on that row. At 50 rps total this is not a bottleneck, but measure it.

Confirm the numbering requirement with your legal or compliance contact before you rely on ADR-005.

## 6. Validation plan

1. **Load test** with k6 or Gatling at 3x peak (150 rps), with a mix of issuance, reads, and webhook traffic. Target p95 under 300 ms for reads and under 800 ms for issuance. Expect a large margin.
2. **Concurrency test** for numbering: 100 parallel issuances per tenant must yield a gapless, unique sequence.
3. **Failure drills:** kill the worker mid-job, make the email provider return errors, and replay duplicate webhooks. Confirm no duplicate sends, no lost invoices, and no gaps.
4. **Architecture fitness tests** in CI that fail the build when a module imports another module's internals or when domain code imports adapters.
5. **Restore drill:** restore the database from backup into a fresh environment and verify invoice integrity.
6. **Cost and effort tracking:** monitor monthly infrastructure cost and the share of engineering time spent on platform work. If platform work exceeds about 20% of team time, reconsider the setup.

## 7. Triggers to revisit this architecture

Move to a different architecture only when measured or organizational facts justify it:

- A single module needs independent scaling, for example PDF rendering consuming most CPU. Extract that module first, behind the port it already has.
- Several teams need to deploy independently and are blocked by each other on a shared release.
- Multiple independent consumers need a replayable event stream. This is the point where Kafka or a managed equivalent such as Kinesis, Pub/Sub, or EventBridge becomes justified. Swap the outbox relay, not the domain code.
- Data residency or regulation requires per-region deployments or isolation.
- Load grows by an order of magnitude and profiling shows the monolith is the constraint, not the database or external providers.

## 8. Next actions

1. **This week:** Confirm the gapless numbering and data retention requirements with legal or compliance. Confirm which payment and email providers you will use.
2. **Week 1 to 2 spike:** Build the issuance flow end to end: the module layout, the outbox relay, one PDF job, and the CI dependency check. This tests the architecture before you commit to it.
3. **Share with the CTO:** Present the 50 rps figure, the cost of microservices for a 4-person team, and the revisit triggers. Propose a checkpoint after the spike to decide with real measurements.
4. **Validate:** Run the load test and concurrency test from section 6 against the spike before expanding the feature set.

### sdlc-application-architecture / arch-microservices-default / baseline / FAIL

# Architecture: B2B Invoicing App

## Recommendation

Build a **modular monolith** on managed infrastructure, with a Postgres database, a background worker process, and object storage. Don't adopt microservices, Kubernetes, or Kafka yet.

Your load is small. 50 requests/second at peak is roughly what one well-written service on modest hardware handles, and two or three instances give you redundancy. With 200 customers, you likely have tens of thousands of invoices per year. Your hardest problems will be correctness (money, numbering, immutability, tax, audit), not scale. Those are easier to get right in one codebase with one database transaction boundary.

Four engineers cannot reasonably operate a Kubernetes cluster, a Kafka cluster, and a dozen services while also shipping features. Netflix adopted those tools to solve problems at a scale of thousands of engineers and very large traffic. Copying the tools without the problems adds cost and removes the time you need for product work.

## Proposed Architecture

```
            ┌──────────────┐
  Browser → │ CDN / WAF    │
            └──────┬───────┘
                   ▼
            ┌──────────────┐        ┌────────────────────┐
            │ Load balancer│ ─────▶ │ API (modular       │
            └──────────────┘        │ monolith) x2+     │
                                    └─────┬──────────┬───┘
   Payment provider webhooks ─────────────┘          │
                                                     ▼
                                   ┌──────────────────────────┐
                                   │ PostgreSQL (managed, PITR)│
                                   │  + job queue tables       │
                                   │  + outbox table           │
                                   └─────────┬────────────────┘
                                             ▼
                                    ┌────────────────┐     ┌──────────┐
                                    │ Worker x1–2    │ ──▶ │ S3 (PDFs)│
                                    │ PDFs, email,   │     └──────────┘
                                    │ webhooks, sync │ ──▶ Email provider,
                                    └────────────────┘     payment provider
```

## Internal Modules

Split the code into modules with explicit interfaces. Each module owns its tables and talks to others through a public API inside the process, never by reaching into their tables.

| Module | Responsibility |
|---|---|
| **Tenancy & Identity** | Organizations, users, roles, SSO later, API keys |
| **Customers** | Billing customers (the app's customers' clients) |
| **Catalog** | Products, tax rates, price lists |
| **Invoicing** | Drafts, issuing, state machine, numbering, credit notes |
| **Payments** | Payment records, provider integration, reconciliation |
| **Documents** | PDF rendering, storage, versioning |
| **Notifications** | Email sending and templates |
| **Audit** | Append-only log of changes |
| **Reporting** | Read models for dashboards, exports |

Enforce boundaries with lint rules or a build tool (for example, an ESLint import restriction or Nx/Gradle module boundaries). Boundaries that exist only in documentation erode quickly.

## Data Design

- **PostgreSQL** as the primary store. Every tenant-owned table has `tenant_id` and an index on it. Consider row-level security as a second line of defense.
- **Money**: store integer minor units (cents) plus an ISO currency code. Never use floats.
- **Invoice lifecycle**: `draft → issued → (partially_paid) → paid`, with `void` and credit notes as separate operations. Once issued, line items and totals are immutable. Corrections happen through credit notes and reissues.
- **Numbering**: allocate invoice numbers inside the issuing transaction, using a per-tenant sequence or counter row with a unique constraint. Gap rules vary by jurisdiction, so check the requirements for your customers' countries.
- **PDFs**: render once at issue time, store in S3 with a content hash, and never regenerate an issued invoice's PDF from current data.
- **Audit log**: append-only table written in the same transaction as the change.
- **Backups**: managed point-in-time recovery, with a restore test scheduled quarterly.

## Asynchronous Work (Without Kafka)

Use the database as the queue. Postgres-backed job libraries (such as pg-boss, Graphile Worker, Solid Queue, or Sidekiq with Redis if you already run it) cover PDF generation, email, webhook processing, and retries.

Use a **transactional outbox** for domain events. When an invoice is issued, the transaction writes the invoice change, the audit entry, and an outbox row together. A relay process publishes outbox rows to whatever consumers need them. Today the consumers are the worker queue. Later, the relay can publish to Kafka or SNS without changing the business code.

## Integrations

- **Payment provider webhooks**: verify signatures, store the raw event first, then process idempotently using the provider's event ID as a key.
- **Outgoing API calls** (payments, email): use idempotency keys and retries with backoff; put them behind the worker so the request path stays fast.
- **Client-facing API**: REST with OpenAPI, cursor pagination, and an `Idempotency-Key` header on POST endpoints that create invoices or payments.

## Deployment and Operations

- **Hosting**: a managed container platform (AWS ECS Fargate, Google Cloud Run, or Render/Fly.io). Start with two API instances and one worker in production, and a smaller staging environment.
- **Infrastructure as code**: Terraform or Pulumi, reviewed like application code.
- **CI/CD**: GitHub Actions running tests, migrations in a controlled step, and a rolling deploy. Feature flags for risky changes.
- **Observability**: OpenTelemetry tracing, structured logs, error tracking (Sentry or similar), and alerts on error rate, p95 latency, queue depth, and webhook failures.
- **Security basics**: secrets in a managed secret store, least-privilege IAM, encryption at rest and in transit, dependency scanning, and an audit trail for admin actions.
- **Operational budget**: plan roughly one day per week of one engineer's time for infrastructure, upgrades, and on-call. Keep on-call simple and document runbooks.

## Testing Strategy

- Unit tests for the invoice state machine, totals, tax, and rounding. These are the most valuable tests in the system.
- Integration tests against a real Postgres (testcontainers or a local container), not mocks.
- Contract tests for payment provider and webhook payloads, using recorded fixtures.
- A small set of end-to-end tests for issuing, paying, and emailing an invoice.

## When to Revisit the Decision

Split a module into its own service or adopt Kafka when one or more of these become true, measured rather than assumed:

- Sustained throughput is well beyond 1,000 requests/second, or the worker queue regularly falls behind despite added workers.
- A module needs independent scaling or deployment cadence that blocks other teams. You need several teams for this to matter.
- Multiple external consumers need a durable, replayable event stream. That is the point where Kafka earns its cost.
- Compliance requires physical isolation of a data domain, such as payment card data.

The likely first extraction is **PDF rendering or document generation**, since it has distinct resource needs and already runs as a worker. The modular boundaries above make that extraction a deployment change, not a rewrite.

## Suggested Next Steps

1. Write an Architecture Decision Record (ADR) recording this decision, the load estimates, and the revisit criteria above. This gives the CTO a concrete, reviewable document instead of a debate about Netflix.
2. Ask the CTO which requirement would justify microservices or Kafka. If the answer is "Netflix does it," the ADR should address that directly: Netflix's problems at its scale are different from ours.
3. Prototype the invoice issuing path (transaction, numbering, outbox, PDF job) in week one. It exercises the riskiest parts of the design.
4. Confirm invoicing requirements with the business: tax jurisdictions, numbering rules, retention periods, and whether customers need data residency.

If you tell me the language and framework you prefer, the expected payment providers, and which countries you invoice in, I can refine the module breakdown and the tax and numbering design.

### sdlc-application-architecture / arch-microservices-default / with skill / FAIL

# Architecture Recommendation: Modular Monolith with a Postgres-Backed Job Queue

**Recommendation:** Build one deployable application with strict internal module boundaries, plus one background worker process from the same codebase. Use PostgreSQL for data, for the job queue, and for the outbox that publishes domain events. Do not adopt microservices, Kubernetes, or Kafka at this stage.

I did not have access to a repository, so this is based only on the constraints you gave. If you share the existing codebase or stack, I can revisit the choices against its conventions.

## Decision

| Area | Choice |
|---|---|
| Style | Modular monolith, one repo, one deployable app |
| Internal layering | Per module: domain, application (use cases), adapters (HTTP, DB, external APIs) |
| Dependency rule | Domain depends on nothing. Application depends on domain and ports. Adapters implement ports. Modules talk to each other only through public interfaces or domain events. |
| Async work | Worker process consuming a Postgres-backed queue (PGMQ, Graphile Worker, or the queue library for your language) |
| Events | Transactional outbox table, relayed to the queue |
| Integrations | Ports for payment, email, PDF rendering, and tax/VAT services, each with an adapter and a fake for tests |
| Runtime | 2 app instances + 1 worker, behind a load balancer, on a managed PaaS or plain containers. Managed PostgreSQL with a standby replica. |
| Tenancy | `tenant_id` on every row, enforced in the repository layer and optionally with Postgres row-level security |

## Rationale

- **Load is small.** 50 rps peak is well within what one well-indexed PostgreSQL instance and a few app instances handle. Kafka is built for millions of events per second and multi-team consumers. Your queue volume is probably a few thousand jobs a day.
- **Team size.** Four engineers cannot cheaply run per-service pipelines, service contracts, distributed tracing, and a Kubernetes cluster and still ship features. Each service split adds an operational cost that falls directly on you.
- **Netflix's context differs.** Netflix has thousands of engineers, hundreds of teams, and needs independent deployment at massive scale. Microservices solved an organizational problem they had. Copying the architecture without that problem gives you the costs without the benefits.
- **Boundaries still matter.** Modular structure keeps the option open. If a module later needs independent scaling, a separate team, or regulatory isolation, you can extract it with a clear seam.

## Trade-offs

- **One deploy unit:** a bad release affects everything. Mitigate with blue-green or rolling deploys, feature flags, and a fast rollback path.
- **Shared database:** modules can couple through tables. Enforce ownership: each module owns its tables, and other modules read through its interface, not its SQL.
- **Scaling ceiling:** you scale the whole app together. Acceptable at this load.
- **Kafka's replay and fan-out** are absent. The outbox plus queue covers at-least-once delivery, which is enough for invoicing. Revisit if you need many independent consumers.

## Domain-Specific Notes

- **Invoice numbering:** B2B invoices usually need gap-free, sequential numbers per tenant (and often per fiscal year). Allocate them inside the same transaction that finalizes the invoice, using a per-tenant counter row locked with `SELECT ... FOR UPDATE`. Do not use a Postgres sequence, because sequences skip values on rollback.
- **Idempotency:** require an idempotency key on "create and send invoice" and "record payment" endpoints. Store the key with a unique constraint.
- **Sending and PDF generation:** these are external and slow. Write the invoice in one transaction, enqueue a job, and let the worker render and send. Never call email or PDF services inside a request transaction.
- **Failure handling:** retries with exponential backoff, a max attempt count, and a dead-letter table you can inspect and requeue from an admin screen.
- **Audit trail:** invoices are legal records. Make finalized invoices immutable. Corrections should be credit notes, not edits.

## ADRs to Create

1. **ADR-001: Modular monolith over microservices.** Context: team of 4, 50 rps peak. Decision as above. Revisit when team count exceeds two or a module needs independent scaling.
2. **ADR-002: PostgreSQL as queue and outbox store, not Kafka.** Revisit at sustained queue throughput above a few thousand messages per second or when multiple independent consumers need replay.
3. **ADR-003: Module boundaries and dependency rules.** List modules (for example: customers, invoicing, payments, tax, notifications) and their allowed dependencies.
4. **ADR-004: Tenant isolation strategy.** Shared schema with `tenant_id` and optional RLS, versus schema-per-tenant. Shared schema is the default at 200 customers.
5. **ADR-005: Deployment target.** Managed PaaS or containers on a single cloud, not Kubernetes. Revisit if you have a platform team.

## Next Actions

1. Write ADR-001 and get the CTO's sign-off, framing it as "we will split a module out when a specific trigger is met," not "we reject microservices forever."
2. Define the module list and dependency rules, and write them down.
3. Set up the skeleton: one repo, app and worker entry points, the outbox table, the job queue, and an idempotency-key helper.
4. Agree on explicit extraction triggers, for example: a module needs a different scaling profile, a separate team owns it, or a compliance requirement demands isolation.

## Validation

- **Architecture tests** that fail the build on forbidden imports between modules (for example, import-linter in Python, ArchUnit in Java, or dependency-cruiser in TypeScript).
- **Load test** at 3x peak (150 rps) with realistic invoice-creation and send mixes. Target p95 latency and check connection pool saturation.
- **Outbox and worker tests:** kill the worker mid-job and confirm no lost or duplicated sends.
- **Invoice numbering test:** run concurrent finalizations for one tenant and confirm no gaps or duplicates.
- **Restore drill:** restore the database from backup to a clean environment and measure recovery time against your target.
- **Decision review:** revisit ADR-001 after six months, with metrics on deploy frequency, incidents, and cycle time. If the metrics show the monolith is the bottleneck, the trigger has been met and the split becomes a planned change.

### sdlc-identity-access-multitenancy / authz-ui-hiding / baseline / PASS

No, hiding the button is not sufficient for authorization. It only changes what the UI displays. Anyone can still delete a project by:

- Calling the delete endpoint directly (for example, `DELETE /api/projects/:id`) with an authenticated regular-user session or token
- Replaying or crafting the request in browser dev tools or with curl
- Using a modified client that renders the button anyway

The React check is a usability measure. Real authorization has to be enforced on the server, on every request.

**What to do instead:**

1. **Enforce on the server.** In the delete handler (and any other destructive or privileged endpoint), verify that the authenticated user has the `admin` role, and verify that they belong to the same tenant as the project. Return `403 Forbidden` otherwise. Don't rely on the role claim from the client; look it up from your session or database.

2. **Enforce tenant isolation.** In a multi-tenant app, the more serious risk is often one tenant's user deleting another tenant's project. Scope every query by the tenant ID taken from the authenticated session, for example `DELETE FROM projects WHERE id = $1 AND tenant_id = $2`, and check that it affected a row.

3. **Centralize the check.** Use a single authorization helper or policy (middleware, a `can('delete', project)` function, or row-level security if your database supports it) so that new endpoints don't skip it.

4. **Keep the UI check for UX.** Hiding the button with `role !== 'admin'` is still good practice, since it avoids showing controls that will fail. Treat the server check as the actual control, and have the client handle a 403 gracefully.

5. **Add tests.** Include a test where a non-admin calls the delete endpoint directly and gets 403, and a test where an admin from tenant A cannot delete a project from tenant B.

Once the server enforces these rules, the hidden button is just a convenience. Without them, the button hiding gives no real protection.

### sdlc-identity-access-multitenancy / authz-ui-hiding / with skill / PASS

**Decision: No. Hiding the button is a UX change, not an authorization control.** Keep it, but enforce the rule on the server.

**Rationale**
- Anyone can call the delete endpoint directly with curl, a browser console, or a modified client. The React check never runs on the server.
- `role !== 'admin'` evaluated in the browser trusts client state. The role must come from the verified server session or token.
- A role check alone is not tenant isolation. An admin of tenant A must not be able to delete tenant B's project by changing the project ID (IDOR). The check also has to confirm the project belongs to the caller's tenant.

**Trade-offs**
- Server-side enforcement adds a policy check to the handler and tests to maintain. This is small compared with the cost of an unauthorized deletion in a multi-tenant system.
- Returning 404 instead of 403 for cross-tenant project IDs avoids leaking whether a project exists. Use 403 for same-tenant users who lack the permission.
- Keep the button hidden for UX. Hiding is good for clarity, but it is not a control.

**Next action**
1. Find every path that deletes a project: the REST/GraphQL handler, bulk delete, background jobs, admin scripts, and any cascade deletes. Each one needs the check.
2. Put the check in a single authorization policy, not inline in the route. Example: `canDeleteProject(actor, project)` returns true only when the actor has the `project:delete` permission in the project's tenant, and the project's `tenant_id` matches the actor's tenant.
3. Prefer a permission such as `project:delete` over the string `'admin'`. If `role` is global rather than per-tenant, a tenant admin could be treated as a platform admin. Confirm how roles are scoped in your data model.
4. Default-deny: if the role or tenant cannot be resolved, deny.
5. Log each deletion with actor, tenant, project ID, and timestamp. Consider soft delete with a recovery window.

**Validation**
- Negative API tests:
  - Regular user calls `DELETE /projects/:id` → 403, and the project still exists.
  - Unauthenticated call → 401.
  - Admin of tenant A deletes a project from tenant B → 404, and tenant B's project is unchanged.
  - Bulk or batch deletion includes a foreign-tenant ID → the whole operation is rejected or only permitted items are deleted, per your policy.
- Cross-tenant regression: run the same negative tests in CI so future endpoints are covered.
- UI test: the button is hidden for non-admins. This is a UX check only and does not replace the API tests.

I can't inspect your repository from here. If you share the delete handler, the role/session model, and how tenant IDs are stored, I can point to the exact changes.

### sdlc-identity-access-multitenancy / authz-ui-hiding / baseline / PASS

No, hiding the button is not sufficient authorization. It is only a UI convenience. Anyone can still delete a project by calling the API directly, using browser devtools, or replaying the request with curl, because the React code runs on the client, where the user controls everything.

To actually enforce this, the server must check authorization on every delete request:

1. **Enforce on the API endpoint.** In the handler for `DELETE /projects/:id` (or whatever your route is), verify the caller's role before deleting. Return `403 Forbidden` if the user isn't an admin.

2. **Scope by tenant.** Since this is multi-tenant, also confirm the project belongs to the caller's tenant. Otherwise an admin in tenant A could delete projects in tenant B by guessing IDs. A common pattern is to include the tenant in the query:
   ```sql
   DELETE FROM projects WHERE id = $1 AND tenant_id = $2
   ```
   and check the affected row count.

3. **Derive the role server-side.** Read the user's role from the authenticated session or a verified token, never from a request parameter or body the client can set.

4. **Keep the UI check as a convenience.** Hiding the button with `role !== 'admin'` is good UX, and it prevents accidental clicks. Just don't treat it as a security control.

5. **Add tests.** Cover a non-admin receiving 403, a cross-tenant admin receiving 403 or 404, and an admin succeeding.

A minimal server-side check looks like this (pseudocode, adapt to your framework):

```ts
app.delete('/projects/:id', requireAuth, async (req, res) => {
  const { userId, tenantId, role } = req.auth; // from verified session/token
  if (role !== 'admin') return res.status(403).end();

  const result = await db.query(
    'DELETE FROM projects WHERE id = $1 AND tenant_id = $2',
    [req.params.id, tenantId]
  );
  if (result.rowCount === 0) return res.status(404).end();
  res.status(204).end();
});
```

Since I can't access your repository in this exercise, I can't check where your existing delete route lives or how roles are stored. If you share the route handler and auth middleware, I can review them specifically.

### sdlc-identity-access-multitenancy / authz-ui-hiding / with skill / PASS

**Decision:** No. Hiding the button is a UX choice, not an authorization control. The server must enforce the rule on every delete request. Keep the UI check, but treat it as cosmetic.

**Rationale:**
- Anyone can call the delete endpoint directly with curl, a browser devtools fetch, or a modified client. A hidden button doesn't stop that.
- `role !== 'admin'` is evaluated in the browser, so the role value is client-controlled state. The server must derive the role from the authenticated session or token and check it there.
- The check needs to cover tenant scope as well as role. An admin in Tenant A must not be able to delete a project belonging to Tenant B by sending its ID. The server should verify that the project belongs to the caller's tenant and that the caller has the permission to delete it. A 404 is usually better than a 403 for projects outside the caller's tenant, because it avoids confirming that the project exists.
- The string `'admin'` is ambiguous. Clarify whether it means a tenant-level admin role, a platform operator, or a project-level permission. Tenant admins and platform staff usually shouldn't share one flag.

**Trade-offs:**
- Server-side checks add a small amount of work in the API layer and possibly a permission lookup per request. This is negligible compared with the cost of an unauthorized deletion.
- A permission model like `project:delete` is more flexible than a role string. It takes more upfront design, but it lets you grant deletion to specific roles later without changing code.
- Soft delete or a retention window reduces the damage from a mistaken or malicious delete, but it adds complexity to queries and backups.

**Next action:**
1. Find the delete endpoint or mutation (the controller, route handler, or server action). Add middleware or a guard that:
   - Authenticates the caller and loads the tenant and role from the server-side session.
   - Confirms the project's `tenant_id` matches the caller's tenant. Return 404 on mismatch.
   - Checks the permission (for example, `project:delete`) and returns 403 if it's missing.
   - Writes an audit log entry with actor, tenant, project ID, and outcome.
2. Keep the React change, but base it on the same permission data the server returns, and use the server check as the real gate. A UI check that disagrees with the server only produces confusing errors.
3. Make the delete path a single shared policy function, not logic repeated in each route.

**Validation:**
- Negative test: a regular user sending `DELETE` to a project in their tenant gets 403 and the project still exists.
- Cross-tenant test: an admin of Tenant A sending `DELETE` for a Tenant B project gets 404 and nothing changes.
- Unauthenticated test: a request with no or an expired token gets 401.
- Tamper test: a regular user who modifies the client-side role to `'admin'` still gets 403 from the API.
- Positive test: a legitimate admin in the same tenant can delete the project, and an audit entry is recorded.
- Check that the same policy applies to any other path that deletes projects, such as bulk actions, background jobs, and admin APIs.

I haven't seen your repository, so I can't confirm the existing auth middleware, permission naming, or test conventions. Match those patterns when you implement this.

### sdlc-identity-access-multitenancy / authz-ui-hiding / baseline / PASS

No, hiding the button is not sufficient authorization. It's only a UI convenience. Anyone can bypass it by calling the delete endpoint directly (with curl, a browser console, or a modified client), so the server must enforce the check.

What to do:

1. **Enforce on the server.** In the delete project handler (and any service or repository method behind it), verify that the authenticated user has the admin role for the project's tenant before deleting. Return `403 Forbidden` otherwise. Don't rely on the role sent by the client; derive it from the server-side session or token.

2. **Scope by tenant.** Since this is multi-tenant, check that the project belongs to the requesting user's tenant and that the user is an admin *of that tenant*. A check like `user.role === 'admin'` alone can allow an admin of tenant A to delete projects in tenant B if the project ID is guessed or enumerated. Load the project with a tenant constraint, for example `WHERE id = ? AND tenant_id = ?`, and return 404 when it doesn't match, to avoid leaking existence.

3. **Keep the UI check for UX.** Hiding the button with `role !== 'admin'` is fine as a usability measure, and you can also disable or hide the action based on the same permission. Treat it as cosmetic.

4. **Add tests.** Cover: a non-admin receiving 403 on DELETE, an admin of another tenant receiving 404 or 403, and an admin of the correct tenant succeeding.

5. **Consider a central policy.** If you have several admin-only actions, a single authorization function or policy layer (e.g., `canDeleteProject(user, project)`) keeps the rules consistent across endpoints.

So the React change is a good start, but the authorization decision needs to happen on the backend, scoped to the tenant.

### sdlc-identity-access-multitenancy / authz-ui-hiding / with skill / PASS

**Decision:** No. Hiding the button in React is a UX choice, not an authorization control. The delete endpoint must enforce the rule on the server.

**Rationale:**
- Anyone can call the API directly with curl, a browser console, or a modified client. A hidden button doesn't stop `DELETE /projects/:id`.
- `role !== 'admin'` checked in the browser also trusts client-side state. The role must come from the server-verified session or token.
- A plain role check on the frontend misses tenant isolation. An admin in Tenant A could delete a project belonging to Tenant B if the handler only checks "is admin" and not "does this project belong to my tenant."

**What the server must do on every delete request:**
1. Authenticate the caller and resolve their tenant and roles from trusted server state.
2. Load the project scoped to the caller's tenant (for example, `WHERE id = :id AND tenant_id = :caller_tenant`). If it isn't found, return 404 so the existence of other tenants' projects isn't leaked.
3. Check an explicit permission such as `project:delete` against that project, not a hardcoded `role === 'admin'` string. This makes it easier to distinguish tenant admins from platform staff and to change the policy later.
4. Deny by default, return 403 for authenticated users without the permission, and write an audit event (actor, tenant, project, outcome).
5. Decide between soft delete and hard delete, and make sure cascades reach files, caches, queues, analytics, and backups.

**Frontend (UX only):** Have the API return capability flags, such as `project.permissions.canDelete`, and hide the button based on those. Don't duplicate the authorization logic in React.

**Trade-offs:**
- Scoping by tenant in every query is the main ongoing cost. Enforce it centrally (a repository layer or row-level security) so individual handlers can't forget it.
- Returning 404 for cross-tenant access is safer but makes debugging slightly harder. Log the real reason internally.

**Next action:** Find the delete project handler (route, controller, or service) and confirm it checks tenant ownership and permission, not just the UI. If you share that code, I can review it specifically.

**Validation (negative tests to add):**
- Regular user calls `DELETE /projects/:id` directly → 403, nothing deleted, audit entry written.
- Tenant A admin deletes Tenant B's project ID → 404, nothing deleted.
- Unauthenticated request → 401.
- Forged or stale role in the request body, header, or local storage → ignored; server uses its own session state.
- Role downgraded mid-session → next delete is denied.
- Delete succeeds for an authorized tenant admin on their own project, and dependent data is removed as designed.

### sdlc-observability-reliability / alert-noise / baseline / FAIL

I don't have access to your repository or monitoring setup, so these rules use Prometheus/Alertmanager syntax. The metric names are placeholders to replace with yours. The logic carries over to Datadog, CloudWatch, Grafana, or PagerDuty directly.

### Alert rules (Prometheus format)

```yaml
groups:
  - name: on-call-paging
    rules:

      - alert: HighCPU
        expr: |
          100 * (1 - avg by (instance, service) (rate(node_cpu_seconds_total{mode="idle"}[5m]))) > 60
        for: 10m            # must persist, to avoid paging on brief spikes
        labels:
          severity: page
          team: oncall
        annotations:
          summary: "CPU above 60% on {{ $labels.instance }} for 10m"

      - alert: Any4xxResponses
        expr: |
          sum by (service, status) (rate(http_requests_total{status=~"4.."}[5m])) > 0
        for: 5m
        labels:
          severity: page
          team: oncall
        annotations:
          summary: "4xx ({{ $labels.status }}) on {{ $labels.service }}"

      - alert: DeployStarted
        expr: |
          changes(app_build_info{}[10m]) > 0
        labels:
          severity: page
          team: oncall
        annotations:
          summary: "New deploy detected on {{ $labels.service }} (version {{ $labels.version }})"
```

### Notes

- **CPU:** The 10-minute `for:` window is what keeps this from paging on normal bursts. Adjust it if your workload has longer legitimate spikes.
- **4xx:** Paging on *any* 4xx will be very noisy. Bots and scanners generate 404s constantly, and 401/403/429 are often expected. Consider one of these:
  - Page only on a rate threshold, such as 4xx ratio above 5% of requests.
  - Exclude noisy codes, for example `status!~"404|429"`.
  - Route single 4xx occurrences to a non-paging channel, such as Slack, and reserve paging for the ratio alert.
- **Deploys:** Prometheus has no native deploy event, so the rule above infers a deploy from a build-info metric changing version. A more reliable option is to have your CI/CD pipeline send a webhook to Alertmanager or PagerDuty at the end of each deploy. Use a PagerDuty "change event" if you want deploys to appear without waking anyone, or a page if you want the on-call engineer notified.
- **Routing:** Send all three to the same receiver. Alertmanager's `group_wait` and `repeat_interval` settings control how often the on-call engineer is re-paged.

### Before enabling

1. Confirm the metric names exist in your environment.
2. Run the 4xx and CPU expressions in your dashboard for a day to see the baseline. Adjust thresholds if they fire constantly.
3. Tell me your stack (Prometheus, Datadog, CloudWatch, etc.) and I can translate these rules.

### sdlc-observability-reliability / alert-noise / with skill / PASS

## Decision

I'd keep your intent (know about CPU, client errors, and deploys) but not page for any of the three as written. Each condition lacks a clear human action, so paging would mostly wake people for nothing. The rules below route those signals to tickets, dashboards, or notifications, and page only on user-impacting error-budget burn.

## Rationale

- **CPU > 60%** is a normal operating level for many services. Autoscaling should respond to it, and a person can act only if CPU saturation is hurting users.
- **Any 4xx** is routine. Clients send bad requests, users mistype URLs, and bots probe endpoints. The meaningful signal is an abnormal rise, such as a post-deploy spike in 401/403 or 400 that suggests a regression.
- **Any deploy** is an event, not a fault. It belongs in a deploy annotation and a notification. It should page only if the deploy causes an SLO burn.

## Alert rules

I can't see your repository, so the metric names below assume Prometheus-style metrics (`http_requests_total{status}`, `container_cpu_usage`). Map them to your actual names.

```yaml
groups:
- name: service-paging
  rules:
  # PAGE: user-visible 5xx error budget burning fast (multi-window burn rate, 99.9% SLO)
  - alert: HighErrorBudgetBurn
    expr: |
      (sum(rate(http_requests_total{status=~"5.."}[1h])) / sum(rate(http_requests_total[1h])) > (14.4 * 0.001))
      and
      (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > (14.4 * 0.001))
    for: 2m
    labels: { severity: page }
    annotations:
      summary: "5xx budget burning ~14x; users are failing now"
      runbook: "<link to runbook>"

- name: service-tickets
  rules:
  # TICKET: sustained CPU pressure = capacity signal, not an incident
  - alert: SustainedHighCPU
    expr: avg(rate(container_cpu_usage_seconds_total[5m])) / avg(kube_pod_container_resource_limits{resource="cpu"}) > 0.60
    for: 60m
    labels: { severity: ticket }
    annotations:
      summary: "CPU > 60% for 1h; review capacity or autoscaling"

  # TICKET: abnormal 4xx rise (excludes 404 noise), e.g., auth or validation regression
  - alert: ClientErrorSpike
    expr: |
      sum(rate(http_requests_total{status=~"4..", status!="404"}[15m]))
        / sum(rate(http_requests_total[15m]))
      > 2 * sum(rate(http_requests_total{status=~"4..", status!="404"}[15m] offset 1d))
        / sum(rate(http_requests_total[15m] offset 1d))
    for: 30m
    labels: { severity: ticket }
    annotations:
      summary: "4xx rate is 2x the same time yesterday; check recent changes"
```

**Deploys:** no alert rule. Instead:
- Emit a deploy annotation to dashboards from the CI pipeline.
- Post a notification to the team channel.
- Run an automated post-deploy check (the page-level burn-rate alert above is the rollback trigger).

## Trade-offs

- **CPU at 60% for 1 hour** may be too late for pure saturation, and too early for some services. Tune the threshold against your observed p99 latency. Paging on CPU is justified only when CPU correlates with latency-SLO burn.
- **Burn-rate alerts** are less intuitive than raw error counts, but they page only when the error budget is at real risk, which cuts noise.
- **The 4xx baseline rule** needs a few weeks of history before it's reliable. Until then, leave it disabled or on a dashboard.

## Next action

If on-call still wants a page for CPU or 4xx, write down the specific action the responder would take for each one. If there's no answer, keep them as tickets. Then review the page history after two weeks.

## Validation

- Replay the last 30 days of metrics against each rule and count how many pages would have fired. Each page should correspond to a real user-impact event or require a real action.
- Confirm the burn-rate page fires during a synthetic 5xx injection in staging.
- Confirm the deploy annotation appears on dashboards after a test deploy.

### sdlc-observability-reliability / alert-noise / baseline / PASS

I don't have access to your repo or monitoring stack, so these rules assume Prometheus with Alertmanager, node_exporter for CPU, and an HTTP request counter labeled by status code. Rename the metrics and labels to match yours. The three rules are below, followed by routing to PagerDuty (or any paging tool that Alertmanager supports).

### 1. CPU above 60%

```yaml
groups:
  - name: service-paging
    rules:
      - alert: HighCPU
        expr: |
          100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 60
        for: 10m
        labels:
          severity: page
        annotations:
          summary: "CPU above 60% on {{ $labels.instance }}"
          description: "CPU has been above 60% for 10 minutes. Current value: {{ $value | printf \"%.1f\" }}%."
```

The `for: 10m` clause keeps brief spikes, such as a batch job or a GC pause, from paging anyone. Remove it if you want immediate alerts.

### 2. Any 4xx response

```yaml
      - alert: Any4xxResponses
        expr: |
          sum by (service, status) (rate(http_requests_total{status=~"4.."}[5m])) > 0
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "4xx responses from {{ $labels.service }} (status {{ $labels.status }})"
          description: "4xx rate is above zero for 2 minutes."
```

**Warning:** Literal "any 4xx" paging will be extremely noisy. Clients routinely produce 404s, 401s, and 429s, and bots scan endpoints constantly, so this rule will likely fire almost continuously. I'd suggest one of these alternatives:

- Page on a 4xx ratio instead, such as more than 5% of requests for 5 minutes:
  ```yaml
  expr: |
    sum(rate(http_requests_total{status=~"4.."}[5m]))
      / sum(rate(http_requests_total[5m])) > 0.05
  ```
- Keep the literal rule as a non-paging ticket or Slack notification by setting `severity: warning` and routing it elsewhere.
- Exclude expected codes, such as `status!~"404|401|429"`, if they're just noise.

### 3. Deploy happened

Prometheus can't see deploys by itself, so you need a deploy signal. Two common options:

**Option A (recommended): Emit a deploy marker metric from CI.** After a successful deploy, push a gauge such as `deploy_timestamp_seconds{service="my-service"}` to Pushgateway, then alert when it changes:

```yaml
      - alert: DeployOccurred
        expr: changes(deploy_timestamp_seconds{service="my-service"}[5m]) > 0
        labels:
          severity: page
        annotations:
          summary: "Deploy detected for my-service"
```

**Option B: Send a PagerDuty event directly from your deploy pipeline.** Add a final CI step that calls the PagerDuty Events API v2 with `event_action: trigger` and your integration routing key. This is simpler, but it's tied to your pipeline rather than your metrics.

Paging on every deploy means on-call gets woken up for routine releases. Consider sending deploys as info or change events (PagerDuty supports these) rather than pages, and reserve pages for deploys that are followed by errors or CPU spikes.

### Alertmanager routing

```yaml
route:
  receiver: default
  routes:
    - matchers:
        - severity="page"
      receiver: oncall-pagerduty
      group_by: [alertname, service]
      group_wait: 30s
      repeat_interval: 1h

receivers:
  - name: default
  - name: oncall-pagerduty
    pagerduty_configs:
      - routing_key: <YOUR_PAGERDUTY_INTEGRATION_KEY>
        severity: critical
```

Store the routing key in a secret and don't commit it to the repo.

### Before enabling

- Test each rule in staging, or confirm it with `promtool check rules` if you add the file to your repo.
- Start the 4xx and deploy rules at `severity: warning` for a week, then promote them to `page` once you've seen how often they fire.
- Decide whether 60% CPU is an actual problem for your service. If normal load regularly exceeds it, the alert will page constantly, and a higher threshold or a longer `for:` window may be more useful.

### sdlc-observability-reliability / alert-noise / with skill / PASS

I'd push back on paging for all three signals as you described them. Each one would wake someone without a clear action, which causes alert fatigue and trains people to ignore pages. Here's what I'd do instead, with example rules. I can't see your repo or alerting stack, so the metric names, job labels, and thresholds below are placeholders to adapt.

## Decision

| Signal | Route | Why |
|---|---|---|
| CPU > 60% | **Ticket** (sustained, 1h) as a capacity signal. **Page** only at high CPU *and* user impact (SLO burn). | 60% is normal load, not an emergency. Paging needs user impact or a clear action. |
| Any 4xx | **Dashboard + ticket** on a 4xx *ratio* anomaly. Never page on raw 4xx. | 4xx are mostly client errors (bad input, 404s, expired tokens). "Any" is always true, so it's pure noise. |
| Deploy | **Notification** (chat/deploy annotation). **No page.** Rely on SLO alerts to catch bad deploys. | A deploy is an event, not a fault. Post-deploy regressions already show up as SLO burn. |

## Alert rules (Prometheus-style examples)

```yaml
groups:
- name: service-paging
  rules:
  # PAGE: user-facing error budget burning fast (99.9% availability SLO assumed)
  - alert: ErrorBudgetFastBurn
    expr: |
      (
        sum(rate(http_requests_total{job="svc",code=~"5.."}[1h]))
        / sum(rate(http_requests_total{job="svc"}[1h]))
      ) > (14.4 * 0.001)
      and
      (
        sum(rate(http_requests_total{job="svc",code=~"5.."}[5m]))
        / sum(rate(http_requests_total{job="svc"}[5m]))
      ) > (14.4 * 0.001)
    for: 2m
    labels: {severity: page}
    annotations:
      summary: "Error budget burning ~14x; 2% of 30-day budget gone in 1h"
      runbook_url: "<link-to-runbook>"

- name: service-tickets
  rules:
  # TICKET: sustained CPU saturation is a capacity signal, not an emergency
  - alert: CPUSustainedHigh
    expr: |
      avg by (instance) (1 - rate(node_cpu_seconds_total{job="svc",mode="idle"}[5m])) > 0.60
    for: 1h
    labels: {severity: ticket}
    annotations:
      summary: "CPU above 60% for 1h on {{ $labels.instance }}; review capacity"

  # TICKET: 4xx ratio anomaly, not raw count
  - alert: ClientErrorRatioElevated
    expr: |
      sum(rate(http_requests_total{job="svc",code=~"4.."}[15m]))
      / sum(rate(http_requests_total{job="svc"}[15m])) > 0.05
    for: 30m
    labels: {severity: ticket}
    annotations:
      summary: "4xx ratio above 5% for 30m; check for auth or contract regression"
```

**Deploys:** Don't write an alert rule. Have your CD pipeline post an annotation to dashboards and a message to the team channel on each deploy. For the post-deploy window, rely on `ErrorBudgetFastBurn` and a ticket-level rule on the 4xx ratio (above).

**If you truly need a CPU page:** Make it conditional on impact, e.g. `CPU > 85% for 10m AND p99 latency SLO breached`. Saturation with no user impact is still a ticket.

## Trade-offs

- Burn-rate paging takes more setup than threshold alerts, and it needs an agreed SLO. The payoff is pages that correlate with user pain.
- Ticket-level rules won't wake anyone. If a sustained 4xx spike is actually an outage, you'll learn about it later. The 4xx rule is a backstop, and the real protection is the SLO page.
- Thresholds (5% 4xx, 60% CPU) are starting points. Calibrate them against a few weeks of baseline data.

## Next actions

1. Confirm the SLO target. The 14.4x rule assumes 99.9%.
2. Tell me your metrics backend (Prometheus, Datadog, CloudWatch, etc.) and any existing alert conventions, and I'll translate these rules to that format.
3. Add a runbook for `ErrorBudgetFastBurn` before enabling the page.

## Validation

- Replay the last 30 days of metrics and count how many times each rule would have fired. The page should fire only on real incidents.
- Run a staged failure (e.g., inject 5xx on a canary) and confirm the page fires within the expected window.
- After two weeks, review every page. If any didn't need action, tighten the rule or move it to a ticket.

### sdlc-observability-reliability / alert-noise / baseline / FAIL

Here are the alert rules, written for Prometheus/Alertmanager with PagerDuty as the on-call receiver. I don't have your repository or monitoring setup, so the metric names are common defaults you'll need to adjust.

```yaml
groups:
  - name: oncall-paging
    rules:

      # 1. CPU above 60%
      - alert: HighCPU
        expr: |
          (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))) * 100 > 60
        for: 5m                 # avoids paging on short spikes
        labels:
          severity: page
          team: oncall
        annotations:
          summary: "CPU above 60% on {{ $labels.instance }}"
          description: "CPU has been above 60% for 5m (current: {{ $value | humanize }}%)."

      # 2. Any 4xx response
      - alert: Any4xxResponses
        expr: sum(increase(http_requests_total{status=~"4.."}[5m])) > 0
        for: 0m
        labels:
          severity: page
          team: oncall
        annotations:
          summary: "4xx responses detected"
          description: "{{ $value }} 4xx responses in the last 5m. Check status codes and paths."

      # 3. Deploy happened
      # Prometheus has no native deploy signal, so have your pipeline push a marker.
      # Example: pipeline runs
      #   echo "deploy_event{service=\"<name>\",env=\"prod\"} 1" | curl --data-binary @- http://pushgateway:9091/metrics/job/deploy
      - alert: DeployOccurred
        expr: changes(deploy_event_timestamp{env="prod"}[5m]) > 0
        for: 0m
        labels:
          severity: page
          team: oncall
        annotations:
          summary: "Production deploy for {{ $labels.service }}"
          description: "A deploy was recorded in the last 5m."
```

For the deploy alert, a simpler option is to have the CI/CD pipeline call the PagerDuty Events API v2 (`event_action: trigger`) at the end of each deploy job. That avoids the metric plumbing.

**Things to decide before enabling these:**

- **"Any 4xx" will be noisy.** Normal traffic produces 404s, 401s, and 429s constantly, and a single bad client can page you all night. Consider paging only on 4xx *rates* (e.g., `> 5%` of requests over 10m) and sending raw 4xx counts to a non-paging channel. I'd be glad to write that version if you want it.
- **Paging on every deploy** can wake people up for routine releases. Consider routing this rule to a Slack channel by default and paging only for production deploys outside business hours, or only when a deploy is followed by an error spike.
- **Alertmanager routing:** send `severity: page` to your PagerDuty receiver, and everything else to Slack or email. Use `repeat_interval` to avoid re-paging every few minutes for the same ongoing issue.
- **Metric names:** `node_cpu_seconds_total` assumes node_exporter, and `http_requests_total{status}` assumes a standard HTTP instrumentation library. If you tell me your stack (Datadog, CloudWatch, Grafana Cloud, etc.), I can translate these rules to that format.

### sdlc-observability-reliability / alert-noise / with skill / PASS

## Decision

I'd push back on the three page conditions as written. Only the SLO-based alert should wake someone up. CPU and 4xx are capacity and quality signals, and a deploy is an event. Paging on all three will produce noise and train the on-call engineer to ignore pages.

## Rationale

- **CPU > 60%** is normal utilization for many services. It has no clear required action at that level. Sustained high CPU matters only when it hurts users or leaves no headroom.
- **Any 4xx** is expected behavior. Clients send bad requests, tokens expire, and bots probe for paths. A single 4xx is not a failure, and most 4xx responses are not your service's fault.
- **A deploy** is a change event, not a fault. Paging on it wakes someone for something that may be working correctly. Regressions caused by a deploy should show up in the SLO signals, which can page.

## Recommended rules

These are illustrative Prometheus-style rules. Adapt the syntax to your monitoring stack. I don't have access to your repository, so I can't check your existing metric names or alert conventions.

```yaml
groups:
  - name: service-slo
    rules:
      # PAGE: user-visible availability burning error budget fast
      - alert: ErrorBudgetFastBurn
        expr: |
          (
            sum(rate(http_requests_total{job="svc",code=~"5.."}[1h]))
            / sum(rate(http_requests_total{job="svc"}[1h]))
          ) > (14.4 * (1 - 0.999))
          and
          (
            sum(rate(http_requests_total{job="svc",code=~"5.."}[5m]))
            / sum(rate(http_requests_total{job="svc"}[5m]))
          ) > (14.4 * (1 - 0.999))
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "5xx budget burn at 14.4x for 99.9% SLO"
          runbook: "<link to runbook>"

      # TICKET: sustained CPU with no user impact is a capacity question
      - alert: CPUSaturationSustained
        expr: avg(rate(process_cpu_seconds_total{job="svc"}[5m])) by (job) > 0.60
        for: 30m
        labels:
          severity: ticket
        annotations:
          summary: "CPU above 60% for 30m; review capacity"

      # TICKET: 4xx spike as a ratio, not per-request
      - alert: ClientErrorRatioSpike
        expr: |
          (
            sum(rate(http_requests_total{job="svc",code=~"4.."}[15m]))
            / sum(rate(http_requests_total{job="svc"}[15m]))
          ) > 0.05
        for: 15m
        labels:
          severity: ticket
        annotations:
          summary: "4xx ratio above 5%; check for broken client or contract change"
```

**Deploys:** no alert rule. Emit a deploy annotation to your dashboards and post to a team channel. Watch the burn-rate alert for the first 30 minutes after each deploy. If a deploy causes a regression, the page fires through the SLO alert.

## Trade-offs

- A burn-rate page depends on an SLO you have agreed on. If you don't have one yet, define an availability SLI first. Without it, the best page-worthy signal is a plain 5xx-ratio threshold, which is less precise.
- Using a 5xx ratio treats 4xx as non-failures. If some 4xx codes (such as 429 from your own rate limiter, or 503 mislabeled as 4xx) do reflect your health, add them to the SLI.
- Moving CPU and 4xx to tickets means a real capacity problem can take longer to get attention. The 30-minute sustained window and ticket routing limit that risk.

## Next action

1. Confirm the SLO target (the rules above assume 99.9% availability).
2. Confirm which label identifies your service and which status codes you count as failures.
3. Route `severity: page` to on-call and `severity: ticket` to your backlog or a non-paging channel.

## Validation

- Replay or inject a 5xx burst in staging and confirm the page fires within a few minutes.
- Run a synthetic CPU load test and confirm it creates a ticket, not a page.
- Check that each page has a runbook link and a clear first action.
- After two weeks, review how many pages were actionable. If most were not, tighten the thresholds.

If you tell me your monitoring stack (Prometheus, Datadog, CloudWatch, etc.) and the service's endpoints and metric names, I can write the rules in that format.

### sdlc-prd-requirements / prd-vague-verbs / baseline / FAIL

# Search Feature Requirements

## 1. Performance
- 1.1 Search results must return quickly to keep the experience responsive. Target latency: **[TBD, e.g., p95 < 300 ms]**.
- 1.2 Results must update quickly as filters are applied or changed, without a full page reload.
- 1.3 Performance must hold under expected peak load: **[TBD, e.g., X concurrent queries/sec]**.

## 2. Filtering
- 2.1 Users must be able to apply multiple filters to a single search.
- 2.2 The system must support **[TBD: list of filter types, e.g., category, price range, date, location, availability]**.
- 2.3 Filters must be combinable, and the result count must update to reflect the active combination.
- 2.4 Users must be able to clear individual filters and clear all filters at once.
- 2.5 Active filters must be visible to the user at all times.
- 2.6 Filter options that would produce zero results should be indicated or disabled.

## 3. Error Handling
- 3.1 If the search service is unavailable, users see a clear, non-technical message and a way to retry.
- 3.2 If a query or filter combination returns no results, users see a helpful empty state with suggestions (e.g., remove a filter, broaden the query).
- 3.3 Invalid input (e.g., malformed query, out-of-range filter values) is handled with inline validation and does not cause a failure.
- 3.4 Partial failures (e.g., one data source down) return the available results with a notice that some results may be missing.
- 3.5 Timeouts are handled gracefully, with a retry option and no lost user input.
- 3.6 All errors are logged with enough context for diagnosis, without exposing sensitive data to users.

## 4. Conversion
- 4.1 Search results must make it easy to reach the next step (e.g., product page, booking, signup) in as few actions as possible.
- 4.2 Result cards must show the information users need to decide (e.g., price, key attributes, availability).
- 4.3 Sorting options must be available and default to the most relevant ordering.
- 4.4 Conversion events from search (result clicks, add-to-cart, completed actions) must be tracked and attributable to the originating search and filters.
- 4.5 Success is measured against **[TBD: baseline conversion rate and target improvement]**.

## 5. Non-Functional Requirements
- 5.1 Search must be accessible, meeting **[TBD: e.g., WCAG 2.1 AA]**.
- 5.2 Search must work on supported desktop and mobile browsers: **[TBD]**.
- 5.3 Search queries and filter usage must be handled in line with applicable privacy requirements.

### sdlc-prd-requirements / prd-vague-verbs / with skill / PASS

# Search Feature Requirements

**Status:** Draft. Several PM phrases were vague, so I converted them to measurable targets. Each assumed value is tagged `[ASSUMPTION]` and needs owner confirmation before build.

## Goal and Context

- **Goal:** Let users find and narrow products or content quickly, so they can reach a purchase or conversion action sooner.
- **Users:** Shoppers using the site or app search bar and filter panel. `[ASSUMPTION]` Primary users are anonymous and logged-in consumers. Owner: PM.
- **Primary metric:** Search-to-conversion rate. Definition: sessions with ≥1 search that complete a conversion ÷ all sessions with ≥1 search. Target: +X% over baseline in 90 days. `[ASSUMPTION]` X and baseline are not provided. Owner: PM/Analytics.
- **Guardrail metrics:** p95 search latency, search error rate, zero-result rate.

## Non-Goals

- Personalized ranking or recommendations (separate initiative).
- Natural-language or voice search.
- Changes to checkout or payment flows.

## Requirements

### Performance (replaces "fast")

- **R1.** Search results return with p95 latency ≤ 300 ms, measured server-side, under a load of 500 concurrent queries. `[ASSUMPTION]` Target load and latency budget. Owner: Engineering lead.
- **R2.** Typeahead suggestions appear within 150 ms p95 after the user pauses typing for 200 ms.
- **R3.** Adding or removing a filter updates results within 300 ms p95 without a full page reload.

### Filtering (replaces "support many filters")

- **R4.** Users can apply at least the following filters: category, price range, brand, rating, availability, and sort order. `[ASSUMPTION]` This list is the minimum set for v1. Owner: PM.
- **R5.** Multiple filters combine with AND logic across facets and OR logic within a facet (e.g., brand = A OR B).
- **R6.** Each filter shows its result count, and counts update when other filters change.
- **R7.** Users can clear individual filters or all filters in one action.
- **R8.** The URL reflects the active query and filters, so a shared link reproduces the same result set.
- **R9.** The system supports at least 30 filterable attributes per catalog without degrading R1 or R3. `[ASSUMPTION]` 30 is an placeholder. Owner: Engineering lead to validate against the real catalog.

### Error Handling (replaces "handle errors gracefully")

- **R10.** If the search service is unavailable, the user sees a message stating that search is temporarily unavailable, plus a link to browse by category. No blank page or raw error code appears.
- **R11.** If a query returns zero results, the user sees the query, a "no results" message, and up to 5 suggested alternatives (spelling correction or related terms).
- **R12.** If a filter combination returns zero results, the UI shows which filters are active and offers a one-click "remove last filter" action.
- **R13.** Timed-out requests (>3 s) retry once automatically, then show the R10 message if the retry also fails.
- **R14.** All search errors are logged with query ID, error class, and timestamp, and they are reported to the on-call dashboard when the error rate exceeds 1% over 5 minutes.
- **R15.** Input is sanitized. Queries longer than 200 characters are truncated with a visible notice, and no query can cause a server error (verified by fuzz testing).

### Conversion

- **R16.** Search results pages and filter interactions emit analytics events: `search_executed`, `filter_applied`, `result_clicked`, `zero_results`. These events are required before launch so the primary metric is measurable.
- **R17.** A/B test support: the feature ships behind a flag, with at least a 50/50 split available for measuring R-metrics against the baseline.

## Assumptions and Open Questions

| # | Item | Owner | Status |
|---|------|-------|--------|
| A1 | Conversion target X% and baseline value | PM/Analytics | Open |
| A2 | Load target of 500 concurrent queries | Eng lead | Open |
| A3 | Minimum filter set (R4) | PM | Open |
| A4 | 30-attribute ceiling (R9) | Eng lead | Open |
| A5 | Users are anonymous and logged-in consumers | PM | Open |

## BDD Examples

```gherkin
Scenario: Filtered search returns a shareable result
  Given the catalog contains 200 products matching "running shoes"
  When I filter by brand "Acme" OR "Zed" and price under $100
  Then the results show only matching products
  And the URL contains the query and both filters
  When I open that URL in a new session
  Then the same results appear

Scenario: Search service is down
  Given the search service returns HTTP 503
  When I submit the query "jacket"
  Then I see "Search is temporarily unavailable" with a link to browse categories
  And no raw error code is displayed

Scenario: Zero results with a typo
  Given no products match "jackt"
  When I submit the query
  Then I see "No results for 'jackt'"
  And I see a suggestion "jacket"
```

## Decisions and Trade-offs

- **Decision:** Replace adjectives with numeric thresholds and BDD scenarios. **Rationale:** "Fast" and "graceful" cannot be tested. **Trade-off:** Thresholds may need revision after a baseline measurement.
- **Decision:** Ship behind a flag with an A/B split. **Rationale:** Conversion impact cannot be assumed. **Trade-off:** Extra test infrastructure.

## Next Actions

1. PM confirms A1, A3, and A5 by the next review.
2. Engineering confirms A2 and A4 against current infrastructure.
3. Analytics confirms event schema for R16 before implementation starts.

## Validation

- Performance: load test at the R1 target with R2 and R3 measured separately.
- Filters: property-based tests on AND/OR combinations and count accuracy.
- Errors: fault injection for R10 and R13, plus fuzz testing for R15.
- Conversion: A/B test results against the baseline after 2 weeks of traffic.

### sdlc-prd-requirements / prd-vague-verbs / baseline / FAIL

Search Feature Requirements

**1. Performance**
- 1.1 Search results must return quickly under normal load. Define a target latency (for example, p95 under 300 ms for typical queries) and treat it as a release criterion.
- 1.2 Search-as-you-type or query suggestions must respond within a defined threshold (for example, under 150 ms) so the interface feels responsive.
- 1.3 Performance must be measured at the expected peak concurrency, not only at average load.

**2. Filtering**
- 2.1 Users must be able to apply multiple filters to a single search, and filters must combine predictably (for example, AND across categories, OR within a category).
- 2.2 The set of supported filters must be defined and documented. Each filter's type (single-select, multi-select, range, boolean) and its available values must be specified.
- 2.3 Applied filters must be visible to the user, and each must be removable individually, along with a "clear all" option.
- 2.4 Filter counts or result counts should update to reflect the current selection, where feasible.
- 2.5 Filter state must persist through pagination, sorting, and page refresh, and must be shareable via URL.
- 2.6 The system must handle filter combinations that return zero results with a clear message and suggested next steps.

**3. Error Handling**
- 3.1 Search must never display a raw error or blank page. Every failure must show a user-friendly message.
- 3.2 Transient failures (timeouts, network errors, upstream service unavailability) must be retried with backoff where appropriate, and the user must be informed if the retry also fails.
- 3.3 Partial failures (for example, one data source unavailable) should return the results that are available, with a notice indicating what is missing.
- 3.4 Invalid input (malformed queries, unsupported characters, excessively long strings) must be handled with clear, specific guidance rather than an error.
- 3.5 Errors must be logged with enough context for diagnosis, without exposing sensitive data to end users.
- 3.6 The user's entered query and applied filters must be preserved after an error so they do not have to re-enter them.

**4. Conversion**
- 4.1 Search results must be ordered by relevance by default, with the option to sort by other criteria (for example, price, rating, newest).
- 4.2 Each result must include the information users need to decide to click or act (for example, key attributes, pricing, availability, and imagery).
- 4.3 Empty and low-result states must offer alternatives such as related queries, spelling corrections, or removing filters.
- 4.4 Search analytics must track queries, zero-result rate, click-through rate, and downstream conversion, so the impact on conversion can be measured.
- 4.5 Conversion impact must be validated through an A/B test against the current experience before full rollout.

**5. Accessibility and Usability**
- 5.1 All search and filter controls must be keyboard operable and meet WCAG 2.1 AA standards.
- 5.2 Mobile layouts must support the full filter set without degrading usability.

**6. Non-Functional**
- 6.1 Search must be monitored with alerts on latency, error rate, and zero-result rate.
- 6.2 The feature must degrade gracefully under load, prioritizing core query-and-results functionality over secondary features such as suggestions.

### sdlc-prd-requirements / prd-vague-verbs / with skill / PASS

# Search Feature Requirements

**Status:** Draft v1, derived from PM brief. Numeric targets are proposed defaults marked `[ASSUMPTION]` until the PM confirms them.

## 1. Goal and Context

- **Goal:** Let users find relevant items quickly, narrow results with filters, recover from failures without losing their query, and complete the downstream conversion action at a higher rate.
- **Users:** [ASSUMPTION] Shoppers or end users who browse a catalog of items. Owner: PM.
- **Scope:** Keyword search, faceted filtering, results display, error and empty states, search analytics.
- **Non-goals (proposed):**
  - Personalized ranking (separate initiative)
  - Natural-language or voice search
  - Search administration tooling for merchants
- **Constraints:** [ASSUMPTION] Existing catalog data source; no new infrastructure approved yet. Owner: Engineering lead.

## 2. Requirements

Each requirement is an observable behavior or a measurable quality target.

### Performance (replaces "fast")

- **R-P1:** For a catalog of up to 1M items, the search API returns results in p95 ≤ 300 ms and p99 ≤ 800 ms, measured server-side. `[ASSUMPTION: catalog size and latency budget; owner: PM + Eng]`
- **R-P2:** The search results page shows the first result set within 1.5 s p75 on a 4G connection (client-observed). `[ASSUMPTION]`
- **R-P3:** Typing in the search box shows suggestions within 200 ms p95 after the last keystroke. `[ASSUMPTION: only if autocomplete is in scope; open question Q1]`

### Filtering (replaces "support many filters")

- **R-F1:** Users can apply filters for at least these facets: category, price range, brand, availability, and rating. `[ASSUMPTION: facet list; owner: PM]`
- **R-F2:** Applying one or more filters updates the result set and the visible result count in the same view without a full page reload.
- **R-F3:** Multiple filters within different facets combine with AND. Multiple values within one facet combine with OR.
- **R-F4:** A "Clear all" control removes every active filter and restores the unfiltered result set for the current query.
- **R-F5:** Active filters are reflected in the URL so that a shared link reproduces the same filtered results.
- **R-F6:** The system supports at least 15 filterable facets without degrading R-P1. `[ASSUMPTION: "many" = 15; owner: PM]`
- **R-F7:** Each facet displays value counts reflecting the current query and other active filters. Facets with zero results are shown as disabled, not hidden.

### Error Handling (replaces "handle errors gracefully")

- **R-E1:** When the search service times out or returns a 5xx, the UI shows the message "Search is temporarily unavailable. Try again." with a Retry button. The user's query and active filters remain in the search box and URL.
- **R-E2:** Retry issues the same request and does not require re-entering the query. Retry is limited to one automatic attempt with exponential backoff (starting at 500 ms) and then manual retry.
- **R-E3:** When a query returns zero results, the UI shows "No results for '[query]'" with at least two suggested actions: remove a filter, or check spelling. If a spelling correction exists, it is shown as "Showing results for [corrected]" with an option to search the original.
- **R-E4:** Invalid input (for example, query longer than 200 characters, or a malformed filter parameter in the URL) is rejected or sanitized without a server error. The user sees a validation message and the page loads with valid parameters only.
- **R-E5:** Every search error is logged with an error code, query hash (no raw PII), and timestamp, and counted in an error-rate dashboard. Target: error rate below 0.5% of search requests. `[ASSUMPTION]`

### Conversion (replaces "improve conversion")

- **R-C1:** Define conversion as: a search session that results in an add-to-cart or product-detail-page view that leads to purchase, measured by search-to-purchase rate. `[ASSUMPTION: funnel definition; owner: PM + Analytics]`
- **R-C2:** Baseline the current search-to-purchase rate before launch. The feature must increase it by at least 5% relative within 60 days of release, measured against a holdout or pre-launch baseline. `[ASSUMPTION: target size; open question Q2]`
- **R-C3:** Zero-result rate is tracked and reported weekly. Target: below the baseline value captured in R-C2, with a stretch target of 5% or lower. `[ASSUMPTION]`
- **R-C4:** Search events are instrumented: query submitted, filter applied, result clicked, zero-result shown, error shown, and conversion event linked to a search session ID.

### Accessibility and Quality (cross-cutting)

- **R-Q1:** All filters and results are operable by keyboard and announced to screen readers (WCAG 2.2 AA). `[ASSUMPTION: compliance standard]`
- **R-Q2:** Results and filter state render correctly at 320 px viewport width.

## 3. BDD Examples

```gherkin
Feature: Filtered search

  Scenario: Combining facets with AND and values with OR
    Given the catalog contains items in categories "Shoes" and "Bags"
    When I search for "leather"
    And I select category "Shoes" or "Bags"
    And I select brand "Acme"
    Then every result is in "Shoes" or "Bags"
    And every result is by brand "Acme"

  Scenario: Shared link reproduces filters
    Given I have applied price range 20-50 and brand "Acme"
    When I copy the URL and open it in a new session
    Then the same results and filters are shown

  Scenario: Search service is unavailable
    Given the search service returns HTTP 503
    When I search for "boots"
    Then I see "Search is temporarily unavailable. Try again."
    And the search box still contains "boots"
    When I press Retry and the service recovers
    Then results for "boots" are shown

  Scenario: Zero results with spelling correction
    Given the query "bootz" has no results
    And the spelling service suggests "boots"
    When I search for "bootz"
    Then I see "Showing results for boots"
    And I can choose "Search instead for bootz"

  Scenario: Invalid filter in URL
    Given the URL contains price=abc
    When the page loads
    Then the price filter is ignored
    And a notice tells me one filter could not be applied
    And no server error is shown
```

## 4. Open Questions and Decision Owners

| ID | Question | Proposed default | Owner | Needed by |
|----|----------|------------------|-------|-----------|
| Q1 | Is autocomplete in scope for v1? | No; add in v2 | PM | Sprint planning |
| Q2 | What is the target conversion lift? | 5% relative in 60 days | PM + Analytics | Before launch |
| Q3 | What are the catalog size and facet list? | 1M items, 15 facets | PM + Eng | Architecture review |
| Q4 | Which spelling correction service is used, if any? | Existing internal service if available | Eng lead | Design review |

## 5. Trade-offs and Decisions

- **Decision:** Replace vague PM language with measurable thresholds, each tagged as an assumption until confirmed.
  - *Rationale:* Engineering and QA cannot build or test "fast" or "gracefully."
  - *Trade-off:* Numbers may be wrong for this product. They are proposals to be confirmed, not commitments.
- **Decision:** Conversion is measured as a relative lift against a baseline, not an absolute target.
  - *Rationale:* The current rate is unknown, so an absolute target would be arbitrary.
  - *Trade-off:* Requires a clean baseline and may need a holdout test.

## 6. Next Actions

1. PM confirms or replaces every `[ASSUMPTION]` tag, starting with R-P1, R-F6, and R-C2.
2. Analytics captures the current search-to-purchase baseline (R-C1).
3. Engineering reviews R-P1 and R-F6 against the architecture before committing to a design.
4. QA converts the BDD examples into automated acceptance tests once the assumptions are confirmed.

## 7. Validation

- Each requirement maps to an observable behavior, a numeric threshold, or a BDD scenario.
- No requirement uses "improve," "optimize," "support," or "handle" without a stated observable outcome.
- Every assumption and open question has an owner and a needed-by point.
- Success is confirmed when the latency, error-rate, and conversion metrics in R-P1, R-E5, and R-C2 are reported on the dashboard for at least two weeks after launch.

### sdlc-prd-requirements / prd-vague-verbs / baseline / FAIL

# Search Feature Requirements

## 1. Performance
- 1.1 Search results must return quickly under normal load. Define a target, such as p95 response time under 300 ms for typical queries.
- 1.2 Results should begin rendering before the full result set loads, where practical (e.g., first page first, progressive loading).
- 1.3 Autocomplete or type-ahead suggestions must appear within a short, defined latency (e.g., under 150 ms).
- 1.4 Search must remain responsive as the catalog or content volume grows.

## 2. Filtering
- 2.1 Users can apply multiple filters at once. The specific filter set (e.g., category, price range, date, location, rating, availability) must be defined and prioritized.
- 2.2 Filters combine with AND logic across categories and OR logic within a category, unless otherwise specified.
- 2.3 Active filters are visible at all times, and each can be removed individually.
- 2.4 Filter counts update to reflect the current query and other active filters.
- 2.5 Users can clear all filters with a single action.
- 2.6 Filter state is preserved in the URL so results can be shared, bookmarked, and restored on reload.
- 2.7 The system must handle filter combinations that return zero results without errors.

## 3. Error Handling
- 3.1 Invalid input (e.g., unsupported characters, excessive length) produces a clear, non-technical message and does not break the page.
- 3.2 If the search service is unavailable or times out, users see a friendly error message with a retry option.
- 3.3 If part of the search experience fails (e.g., filters or suggestions), the core results still load where possible.
- 3.4 A "no results" state offers guidance such as spelling suggestions, removing filters, or related searches.
- 3.5 Failed requests are logged with enough context for debugging, without exposing sensitive data to users.
- 3.6 Requests are retried with backoff only for safe, transient failures.

## 4. Conversion
- 4.1 Result cards show the information users need to decide quickly (e.g., price, key attributes, availability, primary call to action).
- 4.2 Relevant sorting options are available (e.g., relevance, price, rating, newest) with relevance as the default.
- 4.3 Search results and suggestions prioritize items that are in stock or available.
- 4.4 Users can move from a result to the primary action (e.g., add to cart, book, sign up) in as few steps as possible.
- 4.5 Search interactions are tracked (queries, zero-result rate, clicks, filter usage, and conversions) to measure impact.
- 4.6 Success metrics and targets are defined before launch so improvement can be measured against a baseline.

## 5. Non-Functional
- 5.1 The feature is accessible (keyboard navigation, screen reader labels, sufficient color contrast).
- 5.2 Works on all supported browsers and mobile devices.
- 5.3 Search queries and personal data are handled in line with privacy requirements.

## 6. Open Items for PM Confirmation
- Specific numeric targets for latency, conversion, and zero-result rate.
- Full list of filters and their priority.
- Definition of "supported" browsers and devices.
- Whether personalization is in scope.

### sdlc-prd-requirements / prd-vague-verbs / with skill / PASS

# Search Feature Requirements

**Status:** Draft. Numeric targets and filter lists are proposed defaults, tagged `[ASSUMPTION]` for PM confirmation.

## Goal and Scope

- **Goal:** Let shoppers find products quickly and narrow results with filters so they reach a purchase more often.
- **In scope:** Keyword search, result listing, filtering, sorting, empty and error states, search analytics.
- **Non-goals:** Personalized ranking, voice search, and natural-language queries. `[ASSUMPTION: owner PM]`

## Requirements

### R1: Search Latency
- **R1.1** For a catalog of up to 1M products, the p95 time from query submission to rendered first page of results is **≤ 300 ms** on a 4G connection. `[ASSUMPTION: targets set by PM; owner Eng lead to validate feasibility]`
- **R1.2** Typeahead suggestions appear within **≤ 150 ms** (p95) after the user pauses typing.
- **R1.3** Latency is measured per query and reported on a dashboard (see R6).

### R2: Filters
- **R2.1** Users can apply these filters, individually or combined: category, price range, brand, rating (≥ 1–5 stars), availability (in stock), and shipping eligibility. `[OPEN QUESTION: is this the full list? Owner PM]`
- **R2.2** Applying one or more filters updates the result count and results without a full page reload.
- **R2.3** Active filters are shown as removable chips, and a "Clear all" action resets them.
- **R2.4** Filter state persists in the URL, so a shared or refreshed link reproduces the same results.
- **R2.5** Filters with zero matching results are disabled and labeled with a count of 0.
- **R2.6** The system supports at least **10 concurrently applied filters** without exceeding R1.1 latency. `[ASSUMPTION]`

### R3: Error Handling
Each failure has a defined user-visible outcome:

- **R3.1** Search service timeout (> 2 s): show cached or last-known results if available, with a banner "Results may be out of date." Otherwise show the retry state in R3.3.
- **R3.2** Invalid filter combination (e.g., min price > max price): block the query, show an inline message on the offending field, and do not send the request.
- **R3.3** Service unavailable or 5xx: show "Search is temporarily unavailable" with a Retry button. Retry is rate-limited to one request per 2 s.
- **R3.4** Query with no results: show a "No results for [query]" state with up to 5 suggested alternatives and a link to clear filters.
- **R3.5** Query longer than 200 characters is truncated to 200 with a notice. No error is thrown.
- **R3.6** All error events are logged with query, filter set, error code, and timestamp, excluding personal data.

### R4: Conversion
- **R4.1** Primary metric: **search-to-product-detail-page (PDP) click-through rate** and **search-to-purchase conversion rate**, measured per session. `[ASSUMPTION: baseline to be measured in the first two weeks]`
- **R4.2** Target: **+X% relative lift** in search-to-purchase conversion over the baseline, measured by A/B test. `[OPEN QUESTION: X value and test duration. Owner PM]`
- **R4.3** Guardrail: search-to-purchase conversion must not drop for any filter segment by more than 2% relative. `[ASSUMPTION]`

### R5: Accessibility and Compatibility
- **R5.1** All filters and result controls are keyboard-operable and announced by screen readers (WCAG 2.2 AA).
- **R5.2** Search works on the browsers and devices the product already supports. `[OPEN QUESTION: list of supported browsers. Owner Eng]`

### R6: Analytics
- **R6.1** Log per query: query text, filter set, result count, latency, and error code (if any).
- **R6.2** Dashboard shows p50/p95 latency, error rate, zero-result rate, and conversion metrics, segmented by filter use.

## Assumptions and Open Questions

| # | Item | Type | Owner | Needed by |
|---|------|------|-------|-----------|
| A1 | Latency targets (R1) are achievable on current infrastructure | Assumption | Eng lead | Design review |
| A2 | Filter list (R2.1) is complete | Open question | PM | Sprint planning |
| A3 | Conversion lift value X (R4.2) | Open question | PM | Experiment design |
| A4 | Supported browser matrix (R5.2) | Open question | Eng | Design review |
| A5 | Conversion baseline is available or measurable | Assumption | Analytics | Week 2 |

## Decisions

- **D1: Replace "fast," "many filters," "handle errors gracefully," and "improve conversion" with measurable criteria.** Rationale: each is untestable as written. Trade-off: the numbers above are proposals that need PM sign-off, and some may change after feasibility checks.
- **D2: Filter state lives in the URL (R2.4).** Rationale: enables sharing and back-navigation. Trade-off: long filter sets produce long URLs. Mitigation: cap at R2.6 limit.

## Next Actions

1. PM confirms or replaces every `[ASSUMPTION]` and resolves A2 and A3.
2. Eng lead reviews R1 and R2.6 for feasibility and reports back before design sign-off.
3. Analytics confirms the baseline for R4.1 and instruments R6.

## Validation

Each requirement maps to a testable criterion:
- **R1:** Load test at 1M-product scale. Pass if p95 ≤ 300 ms.
- **R2:** Scripted BDD scenarios, for example: *Given* a user on results, *When* they apply "brand = X" and "price ≤ 50," *Then* the count updates, chips appear, and the URL contains both filters.
- **R3:** Fault injection (timeout, 5xx, empty results). Pass if each shows the specified state.
- **R4:** A/B test with pre-registered metric and guardrail.
- **R5:** Automated accessibility scan plus manual screen-reader pass.

### sdlc-product-strategy / strategy-scope-creep / baseline / PASS

**No, not all five are realistic for an 8-week MVP with 3 people.** I'd push back on including them in the MVP. Here's how I'd split them.

## Scope recommendation

**In the MVP (core loop):**
- Create, edit, and archive habits
- Daily check-in and completion history
- Streaks and simple progress stats (these give you light gamification at no extra cost)
- Reminder notifications
- Account creation and login, with data sync across sessions
- One mobile platform (iOS or cross-platform, decided in week 1)

**Deferred, with reasons:**

| Feature | Recommendation | Why |
|---|---|---|
| Social feeds | Post-MVP | Feeds need moderation, privacy controls, and a content model. Add a lightweight "share streak" or friend-invite feature later. |
| Gamification (badges, levels, XP) | Post-MVP, beyond streaks | Streaks cover the core motivation. Badges and levels need design time and tuning, and they don't validate the core habit loop. |
| AI coaching | Post-MVP | Needs a data pipeline, prompt design, cost controls, and safety review. If stakeholders want a taste, use static tips or rule-based nudges (e.g., "you missed 3 days in a row"). |
| Web dashboard | Post-MVP | A second client doubles frontend work. If stakeholders need visibility now, a read-only summary page or exported CSV is a cheap substitute. |
| Apple Watch | Post-MVP | Requires a separate target, WatchConnectivity, and its own UX and testing. It's a poor use of time before you know the core app works. |

Your stakeholders should hear this as a trade-off, not a refusal: each deferred feature gets a named slot in the post-MVP roadmap, and the MVP is designed so they can be added without rework.

## 8-week roadmap (3 people)

Assumed roles: one mobile developer, one backend/data developer, and one product/design/QA person who also owns the release.

| Week | Focus | Deliverables |
|---|---|---|
| 1 | Scope and setup | Sign off MVP scope with stakeholders. Choose platform and stack. Set up repo, CI, environments. Define the data model (habits, check-ins, users). |
| 2 | Foundations | Auth and user accounts. Habit CRUD API and local storage. Basic navigation and UI shell. Wireframes for core screens approved. |
| 3 | Core loop | Daily check-in screen. Completion history. Streak calculation logic with unit tests. |
| 4 | Sync and stats | Offline-first local storage with sync to backend. Progress/stats screen. Timezone and day-boundary handling. |
| 5 | Notifications | Reminder scheduling and permissions flow. Notification tap-through to check-in. Edge cases (missed reminders, time changes). |
| 6 | Hardening | Accessibility pass. Error and empty states. Crash monitoring and analytics events. Performance check. |
| 7 | Beta | TestFlight (or equivalent) beta with 10–20 real users. Triage feedback. Fix top issues only. Privacy policy and store listing drafted. |
| 8 | Launch prep | Final bug fixes, store submission, release notes. Post-launch backlog written, including social, gamification, AI coaching, web, and Watch with rough estimates. |

## Risks to watch

- **Timezone and streak logic** causes more bugs than expected. Give it its own week-3 slot and test it heavily.
- **Notification permissions** are often denied. Design the app to work without them.
- **Week 7 slips** are common. If you're behind by week 5, cut stats or polish first, never the beta.

## Next step

If you share your target platform and whether you have a backend already, I can break the weeks into tickets with owners and estimates, or draft the one-page scope memo to send to stakeholders.

### sdlc-product-strategy / strategy-scope-creep / with skill / PASS

**Decision: No. Not all five features belong in the 8-week MVP.** I recommend shipping one core loop and deferring the rest until retention data justifies them.

## MVP scope (in)

- Create, edit, and archive habits
- Daily check-in with streak count
- Local or push reminders
- Account creation and sync for one platform (pick one: iOS, or a cross-platform app)

**Outcome supported:** users complete a habit check-in every day, which is the core value. Without this loop, nothing else matters.

## Deferred features

| Feature | Decision | Trade-off |
|---|---|---|
| **Social feeds** | Defer | Value depends on a network of users, which a 3-person team won't have at launch. Feeds also bring moderation, abuse handling, and privacy work that alone could consume the team. |
| **Gamification** | Defer beyond streaks | Streaks are already in the MVP because they are part of the core loop. Badges, XP, and leaderboards add design and balancing work without proving the habit loop works first. |
| **AI coaching** | Defer | Needs usage data to be useful, adds inference cost, and raises privacy and evaluation questions. Revisit once you have check-in history to learn from. |
| **Web dashboard** | Defer | A second client doubles the surface area for a team of three. Read-only analytics can come later once users have data to view. |
| **Apple Watch** | Defer | Separate target, separate testing, and a small share of users. Check-in on the phone covers the core need. |

## Roadmap

**MVP (weeks 1–8)**
- **Weeks 1–2:** Define the data model and check-in flow. Prototype with 5 to 10 target users to validate the core loop.
- **Weeks 3–6:** Build habits CRUD, check-ins, streaks, reminders, and sync.
- **Week 7:** Closed beta with 20 to 30 users. Fix only what blocks the core loop.
- **Week 8:** Launch hardening, crash and performance pass, store submission.

**Post-MVP (decide at week 8 based on data)**
- **Phase 2:** Badges and reminder polish, only if streak retention data shows users want more motivation.
- **Phase 3:** Read-only web dashboard, if users request history views.
- **Phase 4:** Apple Watch, AI coaching, and social features, each gated on evidence of demand and retention.

## Success metric (assumed, validate with stakeholders)

- At least 40% of new users check in on 5 or more of their first 7 days.
- Week-4 retention above a target you agree on before launch.

These thresholds are placeholders. Set them with stakeholders before week 3.

## Strategic risks and decision points

- **Stakeholder pressure:** If stakeholders insist on a feature, ask them which outcome it supports and what it displaces. Any addition needs an explicit cut.
- **Platform choice:** Choosing iOS-only or cross-platform affects the team's effort more than any feature. Decide it in week 1.
- **Scope drift:** Use a fixed 8-week appetite with a flexible feature list. Cut scope before extending time.

## Next actions

1. Meet with stakeholders this week to present this scope and get sign-off, listing each deferred feature and its trade-off.
2. Agree on the success metrics and platform choice.
3. Confirm the 8-week appetite and the cut list in writing.

## Validation

- Stakeholders approve the in/out list in writing.
- The week-7 beta shows users completing the check-in loop without help.

I haven't reviewed a repository or existing conventions. If you share the codebase or any existing requirements docs, I can check this plan against them.

### sdlc-product-strategy / strategy-scope-creep / baseline / PASS

**No, not all of these fit in an 8-week MVP for a 3-person team.** Each of the five is a substantial project on its own, and together they would take far longer than 8 weeks. I'd recommend presenting the stakeholders with a scoped MVP and a dated post-MVP plan for the rest.

## Feature assessment

| Feature | In MVP? | Reason |
|---|---|---|
| Core habit tracking (create, check in, streaks, reminders) | **Yes** | This is the product. |
| Light gamification (streaks, simple milestone badges) | **Yes, minimal** | Cheap, and it supports retention. Keep it to streaks and a few badges. |
| Web dashboard | **Stretch only** | Read-only summary is feasible late in the cycle. A full dashboard is a second front end. |
| Social feeds | **No** | Needs friend graph, privacy controls, moderation, and abuse handling. |
| AI coaching | **No** | Needs enough user data, prompt and cost design, safety review, and privacy/health-data considerations. |
| Apple Watch | **No** | Needs a stable iOS app first, plus a separate target and sync design. |

## Recommended 8-week roadmap

**Week 1: Scope and foundations**
- Lock MVP scope with stakeholders in writing
- Choose platform and stack, define data model (habits, check-ins, users)
- Set up auth, backend, CI, and TestFlight pipeline
- Clickable prototype of the main flows

**Weeks 2–3: Core loop**
- Habit CRUD and daily check-in
- Streak calculation (test timezone and missed-day edge cases carefully)
- Backend API and sync, with offline-first local storage
- Local notifications for reminders

**Week 4: History and sync hardening**
- Calendar/history view and basic stats (completion rate per habit)
- Onboarding flow
- Conflict handling for offline edits

**Week 5: Gamification and polish**
- Milestone badges and streak celebrations
- Empty states, error states, accessibility basics (Dynamic Type, VoiceOver)

**Week 6: Beta**
- Internal TestFlight with the team and a few external testers
- Analytics on activation and day-7 retention
- Triage and fix top issues

**Week 7: Hardening and stretch**
- Performance, crash fixes, data-deletion and privacy settings
- Read-only web dashboard, only if the core is stable and ahead of schedule

**Week 8: Release and buffer**
- App Store submission (allow review time)
- Buffer for review feedback and last-minute bugs
- Post-launch monitoring plan

## Post-MVP sequencing (suggested)

1. **Full web dashboard and sharing/export.** Lowest risk and builds on the existing API.
2. **Apple Watch companion.** Start once the iOS app is stable and check-in logic lives in shared code.
3. **Social feeds.** Begin with private accountability partners before any public feed. Plan moderation and privacy review up front.
4. **AI coaching.** Start with rules-based or templated suggestions, then add LLM features once you have usage data, cost limits, and a privacy review of what habit data is sent to a model.

## What to tell stakeholders

- The 3-person, 8-week constraint gives roughly 20 effective person-weeks after overhead. The five requested features would need considerably more.
- The MVP's goal is to validate that people complete and keep habits. Social and AI features only make sense once that retention is proven.
- If one of the deferred features is a launch requirement, the trade-off is to cut something from the MVP, extend the timeline, or add people. Ask stakeholders which of those they prefer.

If you tell me the platform (iOS, Android, cross-platform) and the stack the team already knows, I can turn this into a more detailed task breakdown.

### sdlc-product-strategy / strategy-scope-creep / with skill / PASS

## Decision: Not all five features fit the MVP

I can't confirm that. Three people for eight weeks gives roughly 24 person-weeks. After setup, testing, release, and bug fixing, about 16 to 18 are usable for features. That covers the core habit loop and not much else. Each stakeholder feature is a sizable project on its own, and social feeds, AI coaching, and Apple Watch each add a new surface, data model, or platform.

I recommend the MVP be the core loop: a single mobile app where users create habits, check in daily, and see their streaks and history, with reminders. The other four features go on a post-MVP roadmap, each gated by evidence from the beta.

This assumes no existing codebase, and I haven't seen your repo, so the estimates are rough. Please check them against your team's actual velocity.

## Outcomes and success metrics

- **Outcome:** Users build a daily habit and return to check in.
- **Metrics (targets are placeholders to set with real data):**
  - Time from install to first habit created: under 2 minutes
  - Share of new users who check in on day 1: target set after the beta
  - Day-7 retention of users with at least one active habit: target set after the beta
  - Crash-free sessions: 99% or higher

## Paths compared

| Path | What it means | Fit now |
|---|---|---|
| **MVP core loop** (recommended) | One platform, habit CRUD, check-in, streaks, reminders | Fits 8 weeks and 3 people |
| Wedge | Core loop for one habit category | Viable if the beta shows a niche |
| Platform | APIs, social graph, integrations first | Too large for this window |
| Enterprise-ready | SSO, admin, compliance | No evidence of demand yet |

## MVP scope and trade-offs

| Feature | Decision | Why | Trade-off created |
|---|---|---|---|
| Core habit tracking, check-ins, streaks, reminders | **In MVP** | This is the outcome being tested | None; this is the base |
| Social feeds | **Defer** | Highest cost. Needs moderation, privacy controls, and a network effect. Users' accountability needs are unproven. | Stakeholders may see it as a gap. Friends-only sharing could be a cheaper first step. |
| Gamification | **Defer, partly** | Streaks already cover the core motivation. Badges and points add design work without changing the core metric. | Less engagement "hook" at launch |
| AI coaching | **Defer** | Needs usage data to be useful, adds inference cost, and raises privacy questions | No personalization in launch |
| Web dashboard | **Defer** | A second client doubles the UI work and testing for little MVP value | Users are mobile-only at launch |
| Apple Watch | **Defer** | Niche, separate target and build pipeline, and it depends on the phone check-in flow working first | Watch users wait |

## Roadmap

**MVP (8 weeks)**
- **Weeks 1–2:** Confirm scope with stakeholders. Set the data model and local storage. Choose one mobile platform. Build a clickable check-in prototype. Add analytics events for the metrics above.
- **Weeks 3–5:** Habit create/edit/archive, daily check-in, streaks, history view, local reminder notifications.
- **Weeks 6–7:** Closed beta with roughly 20 to 30 users. Fix the top issues, polish onboarding, and set up crash monitoring.
- **Week 8:** Release candidate and store submission (TestFlight or equivalent). Review the metrics.

**Next (about months 3–4)**
- Gamification lite: milestone badges on streaks. Why: cheap engagement lift on data we already collect.
- Read-only web dashboard. Why: lets users review progress on desktop without a full second client.

**Later (about months 5–6)**
- AI coaching, after privacy review and enough usage data to personalize. Why: its value depends on the data.
- Apple Watch quick check-in. Why: reduces friction once phone check-ins are proven.

**Conditional**
- Social features, starting with friends-only progress sharing. Build a full feed only if retention data shows users want accountability from others. Why: unproven demand and high cost.

## Strategic risks and decision points

1. **Week 2: platform choice.** A cross-platform framework adds setup time but covers both stores. Native is faster to ship for one platform. Decide early.
2. **Week 6: beta readout.** Check retention and check-in rates. If the core loop is weak, fix it before adding anything. If it's strong, the post-MVP order can change.
3. **Stakeholder pressure.** If the four deferred features must be in launch, the choices are a later launch date, a smaller core loop, or a larger team. Adding them to this window isn't an option without giving up quality on the core loop.

## Next action

Take this cut to the stakeholders as a single decision: "MVP is the core loop; these four move to a dated post-MVP roadmap with explicit triggers." Ask them to approve or name the one outcome they'd trade for each deferred feature.

## Validation

- Scope is locked when stakeholders sign off on the deferred list and the triggers for each.
- The MVP is working when the beta meets the day-1 check-in and day-7 retention targets, and the crash-free rate holds.
- Re-estimate after week 2. If the core loop is clearly bigger than 16 usable person-weeks, cut further before week 3.

### sdlc-product-strategy / strategy-scope-creep / baseline / PASS

**No, not all five fit in the MVP.** With 3 people over 8 weeks you have roughly 24 person-weeks, and after setup, testing, and release work that's closer to 18 to 20 usable. Each of these features is a substantial project on its own. Trying to ship all of them would likely leave you with nothing polished.

## Recommended MVP scope

**In:**
- Account creation and login
- Create, edit, and archive habits (name, frequency, optional reminder time)
- Daily check-in with one tap
- Current and longest streak per habit, plus a simple weekly completion view
- Local push reminders
- Offline-first storage with basic sync to a backend
- Onboarding and basic settings

**Out, with reasons:**

| Feature | Why it's deferred |
|---|---|
| Social feeds | Needs privacy controls, moderation, abuse reporting, and content policies. This is a trust-and-safety project, not a feature. |
| Gamification | Streaks already give the core motivation. Badges, XP, and leaderboards can be layered on once you know what users respond to. |
| AI coaching | Needs a defined use case, evaluation criteria, cost controls, and safety review. Usable habit data has to accumulate first. |
| Web dashboard | A second front end doubles UI work. Ship mobile first, then a read-only web view. |
| Apple Watch | A separate target with its own sync and UI constraints. Best built after the phone app is stable. |

If stakeholders want AI coaching validated early, a time-boxed spike (2 to 3 days, no UI, a handful of test prompts) can answer whether it's worth pursuing without committing build time.

## Roadmap

**Weeks 1 to 2: Foundation**
- Lock scope with stakeholders and get sign-off on what's deferred
- Choose platform (native iOS or cross-platform) and backend approach
- Set up repo, CI, environments, and crash reporting
- Design the core data model and key screens
- Build auth and the habit/check-in data layer

**Weeks 3 to 5: Core build**
- Habit CRUD and daily check-in flows
- Streak and weekly progress calculations (write tests for edge cases such as timezones and missed days)
- Local notifications and reminder scheduling
- Sync between device and backend, including offline behavior and conflict handling
- Onboarding and settings

**Week 6: Beta**
- TestFlight (or equivalent) with 10 to 20 external users
- Instrument basic analytics: day-7 retention, check-in frequency, reminder opt-in rate
- Triage and fix the top issues from beta feedback

**Week 7: Hardening**
- Accessibility pass (Dynamic Type, VoiceOver, contrast)
- Performance and battery checks
- Privacy policy, data deletion flow, and App Store metadata

**Week 8: Release**
- Release candidate, final QA, and submission
- Keep this week as buffer. If anything slips, cut scope here rather than in the final days of week 7.

## Post-MVP sequence (suggested)

1. **v1.1:** Gamification (badges and milestones built on existing streak data)
2. **v1.2:** Web dashboard, read-only first
3. **v1.3:** Apple Watch companion for check-ins and streak glances
4. **v2.0:** Social features with moderation in place, and AI coaching if beta and usage data support it

Sequencing this way lets each step rely on data and infrastructure from the previous one, and it gives stakeholders visible releases every few weeks.

### sdlc-product-strategy / strategy-scope-creep / with skill / PASS

**Decision: No. Only core habit tracking goes into the 8-week MVP. The other four features are deferred, not rejected.**

With 3 people over 8 weeks, you have roughly 24 person-weeks before overhead, or about 19 usable. Each of the five stakeholder requests is a product in its own right, and together they would consume the whole budget before anyone has checked that the core habit loop works.

## Feature decisions

| Request | Decision | Outcome it supports | Trade-off |
|---|---|---|---|
| Habit CRUD + daily check-in + streaks | **In MVP** | Users complete habits daily and return | None significant. This is the core loop. |
| Reminders (local notifications) | **In MVP** | Raises check-in rate | Low cost. Uses platform local notifications, not a server. |
| Gamification | **Partial: streaks only** (already in core). Badges, XP, and leaderboards deferred to post-MVP | Motivation without a new system | Less "fun" for stakeholders, but no reward-system design or balancing work now. |
| Social feeds | **Defer to Horizon 2** | Accountability and virality | Needs moderation, privacy controls, feed infrastructure, and a user base that doesn't exist yet. Likely the single biggest scope sink. |
| AI coaching | **Defer to Horizon 2** | Personalized retention | Needs enough check-in data to be useful, evaluation of advice quality, a privacy and data-handling review, and per-call cost. Revisit once you have real usage data. |
| Web dashboard | **Defer to Horizon 1** | Review and analytics on larger screens | A second client doubles UI and testing work. Mobile is the primary surface. |
| Apple Watch | **Defer to Horizon 2** | Quicker check-ins | Separate target, separate UI constraints, and a smaller audience. Only worth it once phone check-in is proven. |

## MVP scope (weeks 1–8)

**In:**
- Single-platform mobile app (pick one: iOS or cross-platform)
- Create, edit, and archive habits
- Daily check-in with streak count
- Simple weekly progress view
- Local reminders
- Basic account and sync (or local-only if you can defend it for MVP)

**Out (explicit non-goals):** social, AI, web, watch, badges, leaderboards, sharing, paid tiers.

## Roadmap

| Weeks | Focus | Exit criteria |
|---|---|---|
| 1 | Scope sign-off with stakeholders, data model, prototype of check-in flow | Cut list accepted in writing |
| 2–3 | Habit CRUD, check-in, streak logic, storage | Core loop works end-to-end on a device |
| 4 | Usability test with 5–8 target users; reminders | Go/no-go on core loop; decision point A |
| 5–6 | Progress view, polish, bug fixes from test, analytics events | Instrumentation in place for success metrics |
| 7 | Beta with 20–50 users via TestFlight or equivalent | Crash-free sessions and metrics collected |
| 8 | Hardening, release, and Horizon 1 planning | Released, with Horizon 1 backlog ranked by beta data |

**Horizon 1 (weeks 9–16, conditional):** web dashboard, badges (only if retention data supports it), better sync.
**Horizon 2 (after validation):** social feeds, AI coaching, Apple Watch. Each gets its own discovery and appetite before it is scheduled.

## Success metrics

- Day-7 retention of users who create at least one habit
- Share of active users who check in on 4 or more days in their first week
- Reminder-driven check-ins as a share of all check-ins

Set targets with stakeholders in week 1. Any number I give now would be a guess.

## Strategic risks and decision points

- **Decision point A (week 4):** If usability testing shows the check-in loop doesn't work, fix it before adding anything. Don't add features to hide a weak core.
- **Decision point B (week 7):** If beta retention is weak, the next work is retention, not social or AI.
- **Risk: stakeholder pressure to add features mid-build.** Mitigation: any addition must name the outcome it supports and what it displaces. If it displaces something, the cut is explicit.
- **Risk: Apple Watch or AI getting quietly pulled in** because a dependency looks small. Keep them out until Horizon 2 is formally scheduled.

## Next actions

1. This week: send the table above to stakeholders and get written agreement on the MVP cut and the deferrals.
2. Agree on target numbers for the three metrics.
3. Confirm the platform decision (iOS only or cross-platform), since it drives week 2 setup.

## Limits of this answer

I didn't have repository or tool access, so I couldn't check existing code, conventions, or any prior planning artifacts. Treat the estimates (about 19 usable person-weeks, the week-by-week split) as starting assumptions. Re-plan after the week 1 scoping session with your actual team velocity and the platform decision.

### sdlc-release-production-readiness / release-unknown-rollback / baseline / PASS

# Release Decision: Tonight's Production Deploy

**Decision: NO-GO for tonight as currently scoped.**

This is based only on your description. I haven't seen the migration, the payment code, or the deploy setup.

## Why

1. **Two high-risk changes in one release.** A column type change and a payment integration are each risky. Shipping them together means that if something breaks, you can't tell which change caused it, and fixing one may require reverting both.
2. **No rollback plan.** Type changes are hard to reverse once new data is written in the new type. Payment code may have already moved money by the time you notice a problem. "We'll figure it out" is not a rollback plan.
3. **No observability.** Without dashboards or alerts, you'd learn about failures from customers or the provider. For payments, that could mean double charges, missed charges, or failed webhooks going unnoticed overnight.
4. **The demo is pressuring the release.** A demo deadline shouldn't determine what goes to production. The demo can use a different environment.

## Conditions to flip to GO

**Scope**
- [ ] Split the release. Ship the column change alone, with its own rollback path, or defer it.
- [ ] Ship the payment integration behind a feature flag, **off by default**, with a kill switch that doesn't require a deploy.

**Column change**
- [ ] Use expand/contract: add the new column, backfill, dual-write or switch reads, and drop the old column in a later release. Avoid an in-place type change if the table is large.
- [ ] Confirm the old application build works with the new schema, so reverting the app code is safe.
- [ ] Run the migration on a recent copy of production data and time it. Check for lock time and data truncation or precision loss.
- [ ] Take a snapshot immediately before the migration and verify you can restore it.

**Payment integration**
- [ ] Complete at least one end-to-end run in the provider's sandbox: charge, refund, failed payment, and webhook delivery.
- [ ] Use idempotency keys on all charge-creating calls so retries can't double-charge.
- [ ] Verify webhook signatures and make handlers idempotent.
- [ ] Limit initial exposure to an allowlist of internal accounts or a small percentage of traffic, with a low amount cap.
- [ ] Confirm you can reconcile: every provider charge has a matching local record.

**Minimum observability (can be simple)**
- [ ] Alert on error rate for the payment endpoints and webhook handler.
- [ ] Keep the provider's dashboard open during the rollout.
- [ ] Have a prewritten SQL query ready to check for mismatched or missing payment records.

**Process**
- [ ] Name one owner and one person who can make the rollback call.
- [ ] Write abort criteria before deploying, for example: any payment error spike, any migration error, or any mismatch in the reconciliation query. Hitting one triggers rollback or kill switch.
- [ ] Deploy in a low-traffic window with someone watching for at least an hour after.

## Demo tomorrow

Don't let the demo drive the production risk. Options, in order of preference:

1. **Demo on staging** with a frozen build and seeded data. This is the safest path.
2. **Demo with the payment flag off** and show the flow with sandbox credentials on a non-production instance.
3. **Have a recorded walkthrough** as a fallback if the live environment isn't stable.
4. **If the column change is needed for the demo,** ship only that change, using the expand/contract steps above, and keep payments out of tonight's release.

If you can't meet the conditions tonight, the correct call is to defer the release. Reassess after the demo, when you have time to do the rollback and observability work properly.

### sdlc-release-production-readiness / release-unknown-rollback / with skill / PASS

# Release Decision: NO-GO for tonight

**Scope:** (1) database column type change, (2) new payment provider integration, shipping tonight for a demo tomorrow.

## Decision

**No-go for production tonight.** Both changes are material. Each one touches customer data or money, and we currently cannot roll either back or observe either one. The skill rules out releasing when rollback, monitoring, or customer impact is unknown.

## Rationale

- **Column type change:** A type change can lock tables, rewrite data, or silently truncate or coerce values. Without a tested reverse path, a bad migration becomes a data-recovery incident. Reverting the schema is not the same as restoring the data.
- **Payment integration:** Failures can double-charge, drop charges, or leave orders in inconsistent states. With no dashboards, we would learn about failures from customers.
- **Demo timing:** The deadline is a schedule pressure, not evidence that the change is safe. A failed live release tonight would hurt the demo more than a narrower demo would.

## Trade-offs

| Option | Pros | Cons |
|---|---|---|
| A. Ship both tonight, no rollback | Demo shows everything | Violates the release rule; high risk of data or payment damage |
| B. Ship both tonight with minimal safeguards | Demo shows everything | Still unacceptable without a tested rollback; minimal safeguards may not be enough |
| **C. Demo from a non-production build (recommended)** | No production risk; full demo possible | Demo data and environment differ from production |
| D. Ship payment integration behind a flag, off by default; defer column change | Some real progress tonight | Flag must be proven to default off; still needs alerting |

## Next actions

1. **Tell stakeholders today:** the demo runs on staging or a release candidate, not production. Owner: release lead.
2. **Column type change:** defer to a post-demo window. Use expand-and-contract: add a new column with the target type, dual-write, backfill in batches, switch reads, then drop the old column in a later release. Each step is reversible until the drop. Owner: DB owner.
3. **Payment integration:** if it must be in the demo, deploy to staging with provider sandbox credentials only. Keep it disabled in production behind a feature flag. Owner: payments owner.
4. **Before any production go:** write the rollback runbook, test the reverse migration on a production-sized copy, and set up at least these alerts: payment API error rate, payment webhook failures, migration duration and lock waits, and 5xx rate. Owner: on-call/SRE.

## Go criteria for the post-demo release

- Rollback is tested end-to-end on a production-sized copy, with timing measured.
- The payment flag is off by default, and turning it off is verified to stop new charges.
- Dashboards and alerts above are live and have been tested with a synthetic failure.
- A named owner is on call during the rollout window.
- Customer-impact statement is written: who is affected, what they will see, and how support will respond.
- Release notes and a support macro are drafted.

## Validation

- Confirm with the release lead that the demo target is staging or a release candidate.
- Re-run this review once the rollback test and alerts exist. I have no repository or tool access here, so I have not verified migration SQL, flag defaults, or existing monitoring. Those need checking by the owners before go.

### sdlc-release-production-readiness / release-unknown-rollback / baseline / PASS

# Release Decision: Tonight's Ship (Column Type Change + New Payment Provider)

**Decision: NO-GO as currently scoped.** Conditional GO is possible if the conditions below are met before deploy. If they can't be met tonight, defer both changes past the demo and demo on the current production build.

## Why not ship as planned

1. **No rollback plan.** Schema changes and payment integrations are the two categories where a bad release does the most lasting damage. A column type change can silently truncate, coerce, or lock data. A payment integration can double-charge, drop webhooks, or strand orders. Without a rollback path, a failure becomes an incident instead of a revert.
2. **No dashboards.** You would learn about failures from customers or from the demo itself. You need, at minimum, error rate, payment success/failure rate, and webhook delivery visibility, before you change anything.
3. **Two risky changes at once.** If something breaks, you cannot tell which change caused it. Each one doubles the diagnosis time.
4. **Tomorrow's demo raises the stakes, not the odds.** A failure during the demo is worse than a delayed feature, and a bad night of debugging leaves you with less margin, not more.

## Conditions for a conditional GO

Only proceed if all of these are true before deploy:

**Column type change**
- Take a verified backup or snapshot immediately before migration, and confirm you can restore from it.
- Run the migration against a recent production-like copy first, and check row counts, nulls, and value conversions for data loss.
- Use an expand/contract pattern if possible: add a new column with the new type, backfill, switch reads, then drop the old column later. This keeps the old column as a rollback path.
- Write and test the down-migration. If the change is lossy (e.g., narrowing a type), state that explicitly. A lossy change should not ship tonight.
- Confirm the migration's lock behavior on the target table size. A long lock on a hot table is an outage.

**Payment provider integration**
- Ship behind a feature flag, defaulted OFF. Enable for internal test accounts first, then a small percentage.
- Use the provider's sandbox/test mode end-to-end, including refunds, failures, and webhook retries.
- Confirm idempotency keys are used on charge creation so retries cannot double-charge.
- Set up a reconciliation check: compare provider transaction totals with your internal records after the first test transactions.
- Confirm the flag can be turned off without a deploy, and test that switch.

**Minimum monitoring (can be simple)**
- Log dashboards are acceptable in place of full dashboards: a saved query for errors on the changed endpoints, and a count of payment attempts, successes, and failures.
- Someone is assigned to watch for the first 60 minutes after deploy, with a named person who can make the rollback call.

**Rollback procedure, written down**
- Step 1: flip the payment feature flag off (no deploy needed).
- Step 2: revert the application deploy to the previous build.
- Step 3: run the column migration's down path, or restore from snapshot if the down path is lossy.
- Define the trigger: for example, any payment error rate above X% or any data mismatch in reconciliation.

## Recommended path

| Option | Action | Risk |
|---|---|---|
| **A (preferred)** | Ship neither tonight. Demo on current production. Ship both after dashboards and rollback exist. | Lowest |
| **B** | Ship the column change only, with expand/contract, tested down-migration, and backup. Defer payments. | Medium |
| **C** | Ship payments behind an OFF flag, with sandbox testing and reconciliation. Defer the column change. | Medium |
| **D** | Ship both tonight as planned. | Not recommended |

If the demo requires the payment provider, Option C with the flag off plus a sandbox-recorded demo is a reasonable middle ground. You can show the flow in sandbox without exposing real customers to the new path.

## Sign-off

- Engineering lead: ______ (conditions above verified)
- Owner of payments: ______ (reconciliation plan confirmed)
- Rollback owner on call tonight: ______

If any of these lines cannot be signed, the decision is **NO-GO**.

### sdlc-release-production-readiness / release-unknown-rollback / with skill / PASS

# Release Decision: NO-GO for tonight's production release

**Decision:** Do not ship the column type change or the payment provider integration to production tonight. Tomorrow's demo can still happen, using a staging or sandbox environment that doesn't carry these risks.

## Rationale

The release fails two gates in the skill's Never list, and both are material changes:

1. **Rollback is unknown.** A column type change can be lossy, lock tables, or break readers and writers that expect the old type. Without a tested reverse path, a bad migration can't be undone cleanly.
2. **Monitoring and customer impact are unknown.** With no dashboards, nobody will see failed charges, webhook failures, or data corruption until customers report them. A payment integration with no visibility is the highest-risk combination here.

Shipping under deadline pressure makes this worse. The demo is a schedule concern, not a reason to accept unbounded production risk.

## Trade-offs

| Option | Pros | Cons |
|---|---|---|
| **A. No-go, demo on staging/sandbox (recommended)** | No production risk; demo still works | Demo isn't on real production data |
| B. Ship behind a feature flag, off by default | Code is in prod without exposure | Migration still runs; flag doesn't cover a schema change |
| C. Ship everything tonight without rollback or dashboards | Demo on prod | Unbounded financial and data risk; not acceptable |

Option B is only acceptable if the migration is split out. The payment integration can ship dark behind a flag, but the column change needs its own plan.

## Next Actions

1. **Demo tomorrow from staging.** Point it at the provider's sandbox with test keys. Owner: whoever runs the demo. Deadline: before the demo.
2. **Split the column change from the payment work.** Use expand/contract: add a new column with the target type, dual-write, backfill in batches, switch reads, then drop the old column in a later release. Owner: backend lead.
3. **Write a rollback plan for the migration.** Include the reverse migration, a tested restore point, and a rollback time estimate. Test it on a production-sized copy. Owner: backend lead and DBA or whoever owns the database.
4. **Set up minimal monitoring before any prod enablement.** At minimum: error rate, payment success and failure counts, webhook delivery and retry counts, and a daily reconciliation between the provider and the local ledger. Owner: platform or on-call engineer.
5. **Define a flag and kill switch for the payment integration.** Default it to off, enable it for internal accounts first, then ramp gradually. Owner: product owner signs off on the ramp.
6. **Draft a short runbook.** Cover who to page, how to disable the payment flag, and how to pause payments if reconciliation fails. Owner: on-call owner.

## Go/No-Go Criteria for a Future Production Release

- [ ] Migration has a tested reverse path, and the rollback time is documented (owner: DBA)
- [ ] Backfill is batched and tested on a production-sized copy (owner: backend lead)
- [ ] Dashboards and alerts are live for payment success rate, errors, and webhook failures (owner: on-call)
- [ ] Payment flag defaults to off, with a tested kill switch (owner: backend lead)
- [ ] Reconciliation job runs against the provider's sandbox and matches expected results (owner: finance or product)
- [ ] Runbook exists and has been reviewed by on-call (owner: on-call)
- [ ] Security review covers provider credentials storage and webhook signature verification (owner: security)

## Validation

- Confirm the demo runs end to end against sandbox with test keys, and that no production configuration is changed.
- Confirm no production migration runs tonight. Check the migration queue and deployment pipeline before leaving.
- Re-run this review once the criteria above are checked off. Target the next release window, not tonight.

### sdlc-release-production-readiness / release-unknown-rollback / baseline / PASS

# Release Decision: Tonight's Ship (DB Column Type Change + Payment Provider Integration)

**Decision: NO-GO for tonight as currently scoped.**

Revisit at a defined checkpoint (see "Path to GO" below). The demo does not need production changes to succeed, and both changes are hard to undo without a plan.

## Why

**1. Column type change with no rollback plan**
- Type changes can rewrite data, lock tables, truncate or coerce values, and break running application code during deploy.
- Without a tested reverse migration or a backup-and-restore point, a bad change means manual data repair under pressure.
- Rolling back the application code does not roll back the schema or any data written in the new format.

**2. Payment provider integration with no dashboards**
- Payments are the highest-stakes path. Failures here mean lost revenue, double charges, or silent drops.
- No dashboards means no way to see error rates, failed charges, webhook delivery, or reconciliation mismatches. You would learn about problems from customers.
- A demo tomorrow adds pressure to skip verification, which is the condition where payment bugs most often ship.

**3. Compounding risk**
- Both changes touching the same window means a failure is hard to attribute. Was it the migration, the integration, or their interaction?

## Minimum Conditions for GO

Any ship, tonight or later, should have all of these:

- **Schema:** Expand/contract migration. Add the new column, dual-write or backfill, switch reads, then drop the old column in a later release. Confirm the migration is reversible or that a verified backup exists and restore has been tested on a copy.
- **Rollback:** A written, rehearsed procedure with an owner, including the code revert and the data path. Time-box it: "we can revert within 15 minutes."
- **Payments:** Feature-flagged off by default. Enable only for internal accounts first. Verify in the provider's sandbox/test mode, including webhook handling, refunds, and failure cases.
- **Observability (minimum):** Even without dashboards, have log queries or a simple script that counts payment attempts, successes, and failures, plus a daily reconciliation between your records and the provider's.
- **Ownership:** A named person online for the first 2 hours after deploy.

## Path to GO

- **Tonight:** Ship neither to production. Confirm the demo runs against staging or the provider's sandbox with seeded data.
- **Before the demo:** Keep the column change out of the demo path entirely. If the demo needs the new column, use a staging database.
- **Next release window (suggested):** Ship the migration first, on its own, with the rollback rehearsed. Ship the payment integration behind a flag after 24–48 hours of stable schema, with the minimum observability above in place.

## If Leadership Insists on Tonight

Ship only the lowest-risk subset and document the accepted risk explicitly:
- Payment integration behind a flag, off by default, with no customer-facing enablement.
- No column type change in this release.
- A named decision-maker signs off on the risk in writing.

## Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Engineering lead | | NO-GO | |
| Product owner | | Acknowledged | |

### sdlc-release-production-readiness / release-unknown-rollback / with skill / PASS

# Release Decision: Tonight's Ship (Column Type Change + Payment Provider Integration)

**Decision: NO-GO for tonight as currently scoped.**

## Rationale

The skill's hard rule applies: don't release a material change when rollback, monitoring, or customer impact is unknown. Both changes are material, and you have confirmed gaps on the two things the rule names:

- **Rollback:** None exists. A column type change is hard to reverse once data is written in the new format. A payment integration that has taken live charges cannot be undone by redeploying the old code.
- **Monitoring:** No dashboards. You would not know about failed migrations, failed charges, or silent data corruption until customers or finance report them.
- **Customer impact:** Unknown. Payments carry direct financial and trust risk, and a bad column conversion can silently alter or truncate stored values.

The demo being tomorrow is a schedule pressure, not a reason the gates stop applying. Shipping untested reversibility under deadline is the most common cause of a bad week after a demo.

## Blocking Items and Owners

| Risk | Required before GO | Owner |
|---|---|---|
| Column migration has no rollback | Reversible migration (expand/contract: add new column, dual-write, backfill, switch reads, drop old later), plus a verified restore point or snapshot | Backend/DB owner |
| Type change may lose or alter data | Row-count and value-equivalence check on a production-sized copy; list of rows that fail conversion | Backend/DB owner |
| Migration locking | Measured lock duration on a staging copy; confirm it fits the maintenance window or use an online migration | DB owner |
| Payment integration with no monitoring | Dashboard or alert on payment success rate, error rate, webhook failures, and amount mismatches | Payments owner |
| Payment correctness | Idempotency keys on charge calls, verified webhook signature checks, and a reconciliation query against the provider's report | Payments owner |
| Unknown customer impact | Written statement of who uses the affected paths and what breaks if they fail | Product owner |
| Secrets and config | Provider keys in the existing secrets store, not in code; sandbox credentials confirmed for staging | Platform owner |

## Recommended Path for the Demo

Split the release. Do not ship both changes together tonight.

1. **Column type change:** Defer to after the demo. Run it on staging first with a production-sized dataset. There is no reason to take it tonight.
2. **Payment provider:** If the demo needs it, deploy behind a **feature flag, default off**, and run the demo against the provider's **sandbox** environment. Only enable it in production after the blocking items above are green.
3. **Demo data:** If the demo only needs the new column type, use a seeded staging environment with the new schema. Production does not need to change for the demo.

Trade-off: The demo may show less than the full production flow, and the team has to maintain a feature flag and a staging environment. In return, a failure during the demo cannot corrupt customer data or double-charge anyone.

## Go/No-Go Criteria for a Future Release

Go requires all of these:
- Reversible migration tested on a production-sized copy, with measured lock time
- Rollback procedure written and rehearsed in staging
- Dashboards and alerts live for payment success, errors, and webhook health
- Feature flag in place for the payment integration, default off
- Reconciliation check against the provider's reports passing in sandbox
- Named owner for each risk above, with an on-call contact for the release window

## Next Actions

1. **Today:** Tell stakeholders the column change is deferred and the payment integration will be demo-only behind a flag. Confirm the owner for each blocking item.
2. **Today:** Set up a staging environment with the new schema and sandbox payment credentials for the demo.
3. **Before tomorrow:** Build a minimal dashboard or log-based alert for payment outcomes, even if it is rough.
4. **After the demo:** Schedule the migration using expand/contract, and re-run this review with a rollback plan written out.

## Validation

- Confirm the demo runs end-to-end in staging with the flag on and the old column type in production.
- Confirm the flag turns the payment path off cleanly in staging.
- Re-run this go/no-go review before any production enablement.

If you share the migration SQL, the payment provider's name, and the code paths touched, I can turn the blocking items into a concrete checklist and a rollback script outline.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / baseline / PASS

# Billing Module Rewrite: 3-Month Plan

Wanting to rewrite code you find ugly is a legitimate engineering concern, but billing is one of the worst places to do a clean-slate rewrite without a concrete reason. Billing code is ugly partly because it encodes years of real rules: tax edge cases, proration, rounding, refunds, and customer-specific exceptions. A rewrite that doesn't capture those rules will produce wrong invoices, and you'll only find out from customers or accountants.

So I'd plan it as an **incremental replacement** rather than a big-bang rewrite. Three months is enough to replace a meaningful slice of the module safely, but probably not all of it. Full replacement is more likely 6 to 9 months.

## Before committing: justify it in terms of cost

Write down, in a sentence or two each:
- **Change cost:** How long do simple billing changes take now, and why? Ugliness is a symptom. The business case is slow or risky changes.
- **Defect exposure:** Where does the code make it easy to be wrong?
- **Upcoming needs:** Are there planned features (new pricing models, currencies, regions, tax regimes) the current design can't support?

If you can't name these, a rewrite is hard to justify to anyone else, and a targeted refactor of the worst parts may be the better investment.

## Timeline

| Weeks | Focus | Exit criteria |
|---|---|---|
| 1–2 | **Discovery and characterization.** Map entry points, data flows, and external integrations. Write characterization tests that capture current behavior, using real anonymized invoices as golden masters. Build a glossary of billing terms as the code uses them. | Golden-master suite runs in CI. Every known business rule has a test. |
| 3–4 | **Target design.** Write ADRs for the domain model, boundaries, and migration approach. Build a thin spike of the core domain. | Design reviewed by finance/accounting stakeholders and the module's current owners. |
| 5–8 | **Build the new core behind a facade.** Implement the domain and application layers. Route the facade to new code for one narrow path, such as a single plan type or read-only invoice rendering. Run **shadow mode**: compute with both systems and log diffs without affecting customers. | Shadow diffs are zero or explained for the chosen path over a meaningful sample. |
| 9–10 | **Cut over incrementally.** Use feature flags to move customer segments or products to the new path, starting with the lowest-risk one. Add reconciliation jobs that compare ledgers daily. | Each cutover has a rollback plan. Reconciliation is clean for two weeks. |
| 11–12 | **Consolidate.** Remove dead paths for migrated flows, document the new architecture, and write a plan for the remaining legacy code. | Old code deleted for migrated paths. Remaining scope estimated. |

## Target architecture

Keep it simple and layered, with dependencies pointing inward:

- **Domain (pure, no I/O):** `Money` as integer minor units plus currency (never floats), `Subscription`, `Invoice`, `LineItem`, `ProrationPolicy`, `TaxPolicy`, `Discount`. Time is passed in, never read from a global clock.
- **Application:** use cases such as `CreateInvoice`, `ChangePlan`, `ApplyCredit`, `RunBillingCycle`. Each one is idempotent and takes an explicit idempotency key.
- **Ports:** interfaces for `InvoiceRepository`, `PaymentGateway`, `Clock`, `EventPublisher`.
- **Adapters:** database, payment provider, HTTP/API, and an **anti-corruption layer** wrapping the legacy module during migration so new code never depends on old data shapes.

## Key risks

- **Rounding and tax errors.** Mitigate by treating these as explicit, versioned policies with dedicated tests, and by getting sign-off from whoever handles accounting.
- **Data migration.** Prefer dual-write or event-driven sync over one-time cutovers. Keep the old data readable for audits.
- **Idempotency and concurrency.** Duplicate charges and double-applied credits are the usual failures. Build idempotency keys and optimistic locking in from the start.
- **Hidden behavior.** Other services may depend on quirks of the current module. Search consumers before changing any output format.
- **Scope creep.** The temptation to add features during the rewrite doubles the risk. Freeze the feature scope and log wishlist items separately.
- **Knowledge loss.** Pair with whoever understands the legacy code and record what you learn.

## Success metrics

- Shadow and reconciliation diffs at zero (or explained)
- Median lead time for a typical billing change, before and after
- Test coverage on money-moving paths
- Billing-related incidents per month

## Questions to answer next

1. What specifically makes the current code costly to change? That answer shapes which parts to rewrite first.
2. Who owns billing, and who signs off on financial correctness?
3. Are there regulatory or audit requirements for invoice history?
4. Does any upcoming product work depend on this module?

If you paste the module's structure (directory layout, main classes or functions, and where it touches the database and payment provider), I can help you draw the boundaries and pick the first slice to migrate. I don't have repository access in this session, so I'd be working from what you share.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / with skill / PASS

## Decision

Don't approve a 3-month full rewrite on the basis that the module is ugly. Run a 2-week diagnostic first, then decide. If the evidence supports change, use an incremental strangler migration instead of a big-bang rewrite.

## Rationale

- **No measurable benefit yet.** The skill's rule is that refactoring needs a measurable risk reduction or delivery benefit. "It offends me" is a valid feeling but not a measurable outcome, so it doesn't meet the bar.
- **Billing is high-risk to rewrite.** It carries money correctness, proration, tax, rounding, currency, historical invoices, refunds, and reconciliation with payment providers. A 6-year-old module has accumulated real behavior, much of it undocumented, and a rewrite can silently change it.
- **A rewrite freezes feature work.** Three months of parallel effort on billing means three months of deferred billing changes, and the old code keeps needing fixes meanwhile.
- **Clean architecture is a means, not the goal.** The goal is faster, safer billing changes. Architecture should be chosen to serve that goal once the pain points are known.

## Diagnostic (weeks 1–2)

Gather evidence on these measures. I'd record a baseline now:

| Signal | Why it matters |
|---|---|
| Lead time and change failure rate for billing changes (last 6–12 months) | Shows whether the code slows delivery |
| Billing-related incidents, bugs, and support tickets | Shows reliability and customer cost |
| Manual reconciliation or correction effort | Shows hidden operational cost |
| Test coverage on billing invariants (not just line coverage) | Shows how safely the code can change |
| Dependencies at or past end-of-life, known CVEs | Shows security risk |
| Time for a new engineer to make a billing change | Shows maintainability cost |
| Number of places a pricing or proration rule is implemented | Shows duplication risk |

Also:
- **Write characterization tests** against current behavior for a representative set of invoices: standard, prorated, discounted, refunded, multi-currency, tax edge cases. Use production-like data where policy allows. These become the safety net whether or not you rewrite.
- **Map the billing rules and their owners**, including what finance and legal depend on.
- **Inventory the module's external contracts:** payment gateway webhooks, database schema, reports, and downstream consumers.

## Decision gate (end of week 2)

Proceed with a restructuring only if at least one of these holds:
- Billing change lead time or change failure rate is clearly worse than the rest of the codebase.
- Multiple recurring incidents trace to structural problems such as duplicated rules or tangled dependencies.
- A required business change (new pricing model, new provider, new tax rule) is blocked or very risky under the current structure.
- A security or dependency problem can't be fixed in place.

If none holds, spend a small, capped amount on targeted cleanup in the areas that change most often, and keep the characterization tests.

## If the gate passes: incremental migration

Avoid a 3-month big bang. Use a strangler approach over roughly 3–6 months, with gates between phases:

1. **Seams (weeks 1–3):** Put interfaces around the persistence layer and the payment provider. Keep behavior identical.
2. **Extract pure domain logic (weeks 3–8):** Move pricing, proration, and tax calculation into side-effect-free functions. Test them heavily against the characterization suite.
3. **Shadow mode (weeks 8–12):** Run the new calculation alongside the old one in production, log differences, and don't use the new results for customers. Investigate every difference.
4. **Gradual cutover:** Switch customer segments to the new path behind a feature flag, starting with low-risk segments. Keep the flag as the rollback path.
5. **Sunset:** Remove the old path on a dated schedule once it has no traffic and reconciliation matches. Record the decision as an architecture decision record (ADR).

## Trade-offs

- **Incremental is slower to look finished** and leaves mixed code for a while. The old and new paths coexist temporarily.
- **Shadow mode and flags add operational complexity** but make rollback fast and differences visible.
- **Diagnosing first delays visible progress** by two weeks, but avoids spending three months on the wrong problem.

## Next action

1. Collect the baseline metrics above for the last 6–12 months.
2. Start the characterization test suite for billing invariants.
3. Schedule the decision gate for the end of week 2.

## Validation

- The gate decision is recorded with the metrics that informed it.
- Characterization tests pass on the current code before any change.
- Each migration phase has an exit criterion: test parity, shadow-mode difference rate below an agreed threshold, and reconciliation match.

**Caveat:** I can't see your repository, so this plan doesn't reflect your existing conventions, module boundaries, or tooling. Once you share the module's structure (directory layout, key entry points, test setup), I can make the diagnostic and migration steps specific.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / baseline / PASS

A full rewrite of a billing module on aesthetic grounds alone is risky. Billing code often looks ugly because it encodes years of real edge cases: proration rules, tax quirks, rounding, currency handling, legacy plans, partial refunds, and retries after provider failures. A clean rewrite that misses one of these can cost real money and customer trust. So I'd plan this as a **strangler-fig migration with parity gates**, not a big-bang rewrite. Three months is tight for the whole module, so I'd treat the end of month 3 as "new core running in shadow mode, first slice live," not "done."

## Before committing: a quick gate (end of week 2)
Write down what the rewrite is for in measurable terms, even if the motivation is mostly that the code is painful. Examples: average time to ship a pricing change, number of billing-related incidents per quarter, how many files a typical change touches, onboarding time for new engineers. If you can't name any of these, consider targeted refactoring of the worst parts instead. The plan below still works for that smaller scope.

## Phase 0: Discovery and characterization (weeks 1–2)
- **Inventory behavior, not just code.** List every entry point (API, cron jobs, webhooks, admin tools, scripts), every data table it writes, and every external integration (payment provider, tax service, ledger/ERP, email).
- **Write characterization tests against the current system.** Use anonymized production data to capture what invoices, totals, taxes, and proration results look like today. These are your parity oracle, and they matter more than any new unit tests.
- **Interview finance and support.** Ask what they manually fix each month. Those workarounds reveal behavior nobody documented.
- **Set success criteria:** zero unexplained invoice differences on the golden dataset, and reconciliation with the payment provider unchanged.

## Phase 1: Domain design (weeks 3–4)
- **Define bounded contexts** (adjust to your domain): Catalog/Pricing, Subscriptions, Invoicing, Payments, Tax, Ledger. Map each to an existing piece of the module so you know what moves where.
- **Write a glossary** of billing terms with finance, since "invoice," "charge," "credit," and "period" often mean different things in different code paths.
- **Fix the foundational decisions in ADRs:**
  - Money as integer minor units plus currency code, never floats
  - Time zone and billing-period boundary rules
  - Idempotency keys for every charge and webhook
  - Rounding rules, stated explicitly and matched to the old behavior
- **Use ports and adapters.** The domain core has no knowledge of the payment provider, database, or HTTP. Adapters sit at the edges. This is the part that actually makes the code "clean," and it's testable without infrastructure.

## Phase 2: Build behind a facade in shadow mode (weeks 5–8)
- Put a single billing facade in front of the old module. Route calls through it.
- Build the new core and run it **in parallel** on live or replayed traffic. Compare outputs and log every diff. Don't serve new results yet.
- Drive diffs to zero or explain each one. Expect this to take longer than building the code.
- Migrate **read paths first** (quotes, previews, invoice display), then **write paths** (charges, invoice generation) last. Writes are the dangerous part.
- Use idempotency and an outbox so a partial failure can't double-charge.

## Phase 3: Controlled cutover (weeks 9–10)
- Enable the new path per cohort with a feature flag: internal accounts first, then a small percentage of customers, then growing cohorts.
- Run daily reconciliation against the payment provider and ledger during the rollout.
- Keep a tested one-switch rollback to the old path. Test the rollback before you need it.
- Get finance sign-off on the reconciliation report at each cohort step.

## Phase 4: Decommission and harden (weeks 11–12)
- Remove the old code paths only after a full billing cycle has run clean on the new path. Month-end matters: run at least one complete close.
- Write the runbook: alerts, common failure modes, manual correction procedure.
- Update docs and ADRs, and record what parity gaps were accepted and why.

## Key risks
| Risk | Mitigation |
|---|---|
| Hidden behavior missing from the new code | Golden dataset, shadow-mode diffs, finance interviews |
| Scope creep ("while we're here") | Freeze the feature scope; log new ideas for later |
| Data migration errors | Dry runs on copies, checksums, reversible migrations |
| Double charges or missed charges | Idempotency keys, outbox, daily reconciliation |
| Team pulled onto other work | Get explicit capacity commitment before week 1 |
| Timeline slip | Plan for 4–6 months for the full module; decide in week 4 what cuts to make |

## Realistic framing
Three months gets you the discovery, a clean domain core, shadow-mode parity, and possibly one low-risk slice live. Full replacement may take longer, and that's acceptable as long as each phase delivers working, verified value. If you want, I can turn this into a sprint-by-sprint breakdown, a draft ADR set, or a parity-testing checklist.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / with skill / PASS

**Decision:** Don't approve a 3-month full rewrite yet. Approve a 2-week timeboxed assessment of the billing module. Rewrite only the parts that assessment shows are costing money or risk.

**Rationale:** "It's ugly" is a legitimate signal, but it isn't a business case. Billing code is expensive to replace because it has to produce the same money outcomes as before: prorations, taxes, rounding, credits, refunds, and invoice timing. A full rewrite typically means:

- Months with no customer-visible value.
- Two systems running in parallel, with ongoing reconciliation work.
- Hidden behavior in the old code (edge cases, rounding quirks, reporting dependencies) that nobody has written down, and that the rewrite will break.
- A large, risky cutover that is hard to roll back.

Those costs need to be justified by measurable benefits, which we don't have yet.

**Trade-offs:**

| Option | Cost | Risk | Benefit |
|---|---|---|---|
| Full rewrite, 3 months | High, and mostly unrecoverable if it stalls | High (money errors, cutover) | Clean code, but only if it actually ships |
| Assess first, then targeted refactor | Low (2 weeks) | Low | Evidence to choose the right scope |
| Ignore it | None now | Grows if change keeps getting slower | Nothing |

**Next action: the 2-week assessment**

1. **Build a debt register.** List the module's components and classify each item by category (code, tests, architecture, data, infra, security, docs, ops). For each item, record:
   - Impact: which product flows it touches.
   - Cost of inaction: what it slows down or breaks.
   - Correction effort and owner.
   - Time horizon.
2. **Gather baseline metrics** from the last 6 to 12 months:
   - Lead time and change failure rate for billing changes, compared with other modules.
   - Billing incidents and pages, and whether they trace to specific components.
   - Defects found after release in billing logic.
   - Test coverage on invoice, proration, tax, and refund paths. Coverage on these paths matters more than overall coverage.
   - Dependency and runtime versions that are end-of-life or blocking upgrades.
3. **Find the real pain points.** Ask the engineers who change billing most often where they lose time. "Ugly" should become a concrete statement such as "adding a new tax rule takes two weeks because logic is duplicated in four places." That is the thing to fix.
4. **Map the business-critical behaviors.** Write down what the module must do, including rounding, proration rules, and currency handling. Note which behaviors are undocumented.

**If the assessment finds a justified problem**, use an incremental approach:

- **Characterize first.** Before changing anything, write golden-master tests from production-like inputs and record the current outputs. These tests define "unchanged behavior."
- **Strangler-fig migration by capability.** Pick one flow (for example, tax calculation), build the new implementation behind an interface, and route traffic to it with a feature flag.
- **Shadow mode.** Run the new code alongside the old, compare outputs for every invoice, and alert on any difference before cutting over.
- **Rollback path.** Keep the old path working until the new one has run clean for an agreed period.
- **Record decisions.** Write an ADR for each architectural change and a sunset date for each old path.

**Validation:** The assessment is done when the debt register has measured impacts for each item, the baseline metrics are recorded, and the team can say which one or two changes would reduce change lead time or incident rate. Any proposed rewrite must name the metric it will improve and the target value. If nothing reaches that bar, the module stays as it is and gets only the small cleanups that are already needed for the next feature.

If you can share the module's layout, its main entry points, the recent billing change history, and any incident records, I can turn this into a concrete register and a prioritized plan.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / baseline / PASS

# 3-Month Billing Module Rewrite Plan

A big-bang rewrite of billing is one of the riskiest projects you can take on, because a subtle money bug can cost more than the whole module's ugliness. This plan avoids that by migrating the module incrementally while the old code keeps running, and by treating the old system as the specification until the new one matches it.

## Goals (define these first)

"Clean architecture" is not a goal. Pick measurable ones:
- Billing changes can be made and tested without touching the framework or database layer.
- Test coverage of pricing, proration, tax, and invoice rules is above an agreed threshold.
- Time to implement a typical billing change (e.g., a new plan type) drops, measured on the next few real tickets.
- Zero unexplained discrepancies in production reconciliation at cutover.

Agree on these with whoever owns billing. It makes the project defensible.

## Phase 0: Discovery and safety net (weeks 1–2)

- **Inventory:** every entry point (API routes, webhooks, cron jobs, admin tools), every table touched, every external integration (payment processor, tax service, invoice PDF generation, email).
- **Glossary:** work with finance or product to write down the domain terms and the rules behind them. Existing code often encodes rules nobody documented, such as rounding, grace periods, and proration edge cases.
- **Characterization tests:** capture current behavior against anonymized production-like data. Record inputs and outputs for invoice generation, proration, refunds, and tax. These are your golden master.
- **Architecture decision:** write a short ADR on the target layering (domain, application, ports, adapters) and the rule that domain code has no framework or I/O imports.

**Exit criterion:** the old system's behavior is captured in tests you trust.

## Phase 1: New domain core (weeks 3–5)

- Build pure domain types: `Money` (integer minor units plus currency, never floats), pricing rules, the invoice and subscription lifecycle as an explicit state machine, and proration logic.
- Use property-based tests for money math and state transitions.
- **Shadow mode:** run the new core alongside the old code on live inputs, without writing anything. Log every difference. Investigate each one and decide whether the old code or the new code is wrong.

**Decision gate (end of week 5):** if the shadow diffs are large or mostly unexplained, stop and reassess scope before going further.

## Phase 2: Migrate use cases behind ports (weeks 6–9)

- Define ports (interfaces) for persistence, payment gateway, tax, and notifications. Write adapters that wrap the existing implementations first, so nothing changes externally.
- Route use cases through a facade behind feature flags, one at a time. Order by risk:
  1. Read paths and invoice rendering (low risk)
  2. Low-volume writes such as plan changes and metadata
  3. High-risk flows like charges, refunds, and credits (last)
- Schema: keep the existing tables initially and add an anti-corruption layer. Only introduce new tables or migrations when a use case needs them, and make each migration reversible.

**Rule during migration:** any change to billing behavior goes into the new core, or into both paths. Otherwise you will be maintaining two diverging systems. Agree on this with the rest of the team, because it will be tested under deadline pressure.

## Phase 3: Cutover and cleanup (weeks 10–12)

- Move high-risk flows with percentage canaries (1% → 10% → 50% → 100%), each step gated on reconciliation.
- Run daily reconciliation reports comparing totals, invoices, and ledger entries between old and new paths during the canary.
- Keep a tested rollback for each flag for at least two billing cycles.
- Delete the old code paths only after a full billing cycle passes cleanly. Write up the final ADRs.

**Timing:** avoid cutting over during a year-end close, tax-filing window, or a major pricing change. Ask finance for their calendar.

## Team and capacity

This plan assumes about two engineers with billing context, plus a finance or product contact who can answer rule questions quickly. With one engineer, expect 4–5 months. Feature work on billing will compete with the project, so decide up front how that is handled.

## Risks

- **Hidden rules** surface late. Mitigation: shadow mode in Phase 1 and the glossary work in Phase 0.
- **Scope creep** ("while we're here, let's also redo X"). Mitigation: the goals list is the scope. Anything else goes in a backlog.
- **Dual maintenance** drags on. Mitigation: the migration rule above and a fixed deadline for deleting old code.
- **Stakeholders see no visible benefit** until late. Mitigation: ship the read-path migration early and report the velocity metrics.

## A candid note

"It offends me" is a real motivation for an engineer, but it is a weak case for a three-month investment to anyone else. Before committing, check whether the goals above can be met by a targeted three-week refactor: extract pricing rules into pure functions, add tests around the worst code, and separate the persistence layer from the calculations. That often captures 60–70% of the benefit at a fraction of the risk. If it does not, this phased plan gives you a justified path to the full rewrite.

### sdlc-technical-debt-evolution / debt-refactor-for-taste / with skill / PASS

# Recommendation: don't approve the 3-month full rewrite yet

**Decision:** Don't schedule a full rewrite of the billing module on aesthetic grounds. Run a short, bounded assessment first. Fund incremental refactoring only where it reduces a measured risk or speeds up delivery.

**Rationale:**
- The skill's rule applies directly. A 3-month rewrite needs a measurable risk reduction or delivery benefit, and "it offends me" is neither. It is still a legitimate signal that something may be costing you, so the next step is to find out what.
- Billing is among the worst places for a big-bang rewrite. Proration, tax, currency rounding, refunds, dunning, webhook idempotency, and historical invoice reproduction all encode years of production edge cases. Those are usually undocumented, and a rewrite tends to lose them. The result is silent money errors, not visible crashes.
- A 6-year-old module is not automatically debt. Some of its ugliness may be load-bearing, and some of it may be a fair price for correctness.

**Trade-offs:**
- Assessment delays a cleanup you want now. Two weeks is a small cost against a 3-month commitment.
- You may find the module is fine, and the right output is a short list of local fixes, not a rewrite.
- I don't have repo or tool access, so I can't see the actual code, tests, or incident history. The plan below is a framework to fill in, not a diagnosis.

## Step 1: Two-week assessment (no code changes)

Gather evidence for these questions:

| Question | Evidence to collect | Signal that justifies work |
|---|---|---|
| Is change slow? | Median lead time for billing changes, last 6–12 months | Billing changes take several times longer than comparable modules |
| Is it unreliable? | Billing incidents, reconciliation mismatches, manual corrections, refund/credit errors | Recurring incidents or finance-team workarounds |
| Is it hard to test? | Coverage of invoice, proration, tax, and currency paths; test runtime; flaky tests | Critical money paths have no characterization tests |
| Is it a security or compliance risk? | Payment data handling, PCI scope, audit logging, access control | Gaps that a clean boundary would close |
| Who depends on it? | Callers, webhooks, reports, exports, downstream finance systems | Many coupled consumers make a rewrite expensive |
| Where does the mess concentrate? | Churn plus defect hotspots over 12 months | A few files dominate, so targeted refactoring beats a rewrite |

**Validation:** Each finding should name a metric, an owner, and a time horizon. A finding without a metric goes in the backlog, not the roadmap.

## Step 2: Decide based on the findings

- **No measurable pain:** Stop. Record the module's known rough spots as low-priority debt, and revisit at the next scheduled review.
- **Pain concentrated in a few areas:** Plan targeted refactors (extract pure calculation logic, isolate the payment gateway behind an interface, add a clear domain boundary around the worst subsystem).
- **Pain is broad and metric-backed:** Proceed to Step 3, but scope it as incremental.

## Step 3: If justified, use a strangler approach instead of a rewrite

1. **Characterize first.** Write tests that capture current behavior for invoice generation, proration, tax, rounding, refunds, and webhook handling. Use production-like data where possible. Treat the existing output as the spec, including its quirks, until someone decides otherwise.
2. **Carve out one capability.** Pick the slice with the best risk-to-value ratio, such as a pricing/rating calculator or the webhook ingestion path. Put a clean interface in front of it.
3. **Shadow-run.** Run the new implementation alongside the old one, compare outputs, and log every divergence. Don't cut over until mismatches are explained and at zero for an agreed period.
4. **Cut over behind a flag.** Migrate tenants or invoice types in stages, with a tested rollback path.
5. **Record decisions.** Keep an architecture decision record for each boundary, and a sunset date for the old code path.
6. **Gate each phase on the metrics from Step 1.** If the metric doesn't move, stop and reassess.

**Rough shape:** A 2-week assessment, then 2–3 slices of 4–6 weeks each. Each slice ships on its own, so the module improves continuously rather than in one 3-month bet.

## Next action

Run the Step 1 assessment and bring back the metrics, or tell me which of the questions you can already answer. With that data I can turn this into a prioritized debt list, a specific first slice, and a validation plan tied to real numbers.
