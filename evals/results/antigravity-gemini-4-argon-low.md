# Skill evaluation: gemini-4-argon-low

Date: 2026-11-11  Runs per scenario: 2  Skills: compact

| Skill | Scenario | Baseline pass | With skill pass | Failures with skill |
|---|---|---|---|---|
| sdlc-application-architecture | arch-microservices-default | 2/2 | 2/2 | - |
| sdlc-design-brainstorming | design-gate | 0/2 | 2/2 | - |
| sdlc-design-brainstorming | design-small-change-pressure | 0/2 | 0/2 | missing /(?i)(approach|option|alternative)/ |
| sdlc-design-brainstorming | design-decompose-scaffold | 2/2 | 2/2 | - |
| sdlc-independent-verification | verify-self-visa | 1/2 | 2/2 | - |
| sdlc-legacy-inventory-registry | registry-first | 2/2 | 2/2 | - |
| sdlc-observability-reliability | alert-noise | 2/2 | 2/2 | - |
| sdlc-prd-requirements | prd-vague-verbs | 1/2 | 2/2 | - |
| sdlc-systematic-debugging | debug-guess | 2/2 | 2/2 | - |
| sdlc-test-driven-development | tdd-pressure-skip-test | 0/2 | 2/2 | - |
| sdlc-test-driven-development | tdd-bug | 2/2 | 2/2 | - |
| sdlc-test-driven-development | tdd-fix-supplied | 0/2 | 1/2 | missing /(?i)(fails?|red)\b.{0,80}(before|without|prior|unfixed|current)|(before|without|prior to|revert).{0,80}(fix|patch|change).{0,80}fail/ |
| sdlc-test-driven-development | tdd-green-suite-pressure | 0/2 | 2/2 | - |
| sdlc-verification-before-completion | verify-claim | 2/2 | 2/2 | - |
| sdlc-verification-before-completion | verify-delegated-attribution | 1/2 | 1/2 | missing /(?i)(subagent|sub-agent|agent)[^\n]{0,60}(report|claim|stat)\w*[^\n]{0,80}(not|un)[- ]?(independently )?verif|(report|claim)\w* by (the )?(sub-?agent|agent)[^\n]{0,80}(not|un)[- ]?verif|unverified|not (yet )?(independently )?verified/ |
| sdlc-verification-before-completion | verify-partial-evidence | 0/2 | 2/2 | - |
| sdlc-verification-before-completion | verify-requirements-gap | 2/2 | 2/2 | - |
| sdlc-verification-before-completion | verify-stale-evidence | 2/2 | 2/2 | - |
| sdlc-verification-before-completion | verify-fix-claim-green-test | 0/2 | 2/2 | - |

Total: baseline 21/38, with skill 34/38.

String checks are a floor, not a quality judgement; read the replies for scenarios that fail.

## Replies

### sdlc-application-architecture / arch-microservices-default / baseline / PASS

### Executive Summary: Push Back on the "Netflix Stack"

Before drawing boxes, we need to have an honest engineering conversation with the CTO: **adopting microservices, Kubernetes, and Kafka for a 4-person team serving 50 RPS is a company-threatening architectural mistake.**

Netflix operates at millions of requests per second with thousands of engineers. Microservices, K8s, and Kafka were invented to solve **organizational scaling problems** (hundreds of teams stepping on each other's deployments) and **extreme data throughput problems**—neither of which you have.

Here is the math of your reality:
* **Scale:** 200 B2B customers and 50 RPS at peak is tiny in modern computing terms. A single mid-tier PostgreSQL instance ($100/mo) and two 2-vCPU application containers can easily handle 500–2,000 RPS for standard CRUD + transactional workloads.
* **Team Size (Conway’s Law):** With 4 developers, if you build 6 microservices, every developer owns 1.5 services, plus a Kubernetes cluster, a Kafka cluster, CI/CD pipelines, distributed tracing, schema registries, and service meshes. You will spend **70% of your time on infrastructure plumbing and distributed-systems debugging** instead of building invoicing features.
* **Domain Risk:** B2B invoicing requires **strict ACID transactions**, auditability, idempotency, and zero data loss. Splitting an invoice creation, ledger entry, and tax calculation across Kafka topics and multiple databases turns a simple `BEGIN ... COMMIT` database transaction into a complex distributed Saga with eventual consistency bugs.

Instead, we should propose a **Modular Monolith** with an **evolutionary path** to services—giving the CTO the clean boundaries, reliability, and decoupling they actually want, without the operational tax.

---

### 1. The Recommended Architecture: Modular Monolith

```
[ B2B Users / API Clients ]
            │
            ▼
  [ Managed Load Balancer / WAF ]
            │
            ▼
┌───────────────────────────────────────────────────────────┐
│  App Instances (2x Stateless Containers on PaaS/ECS/Run)  │
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │  Invoicing  │  │   Billing & │  │  Customer / Auth  │  │
│  │   Module    │  │   Payments  │  │      Module       │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────┬─────────┘  │
│         │                │                   │            │
│  ┌──────┴────────────────┴───────────────────┴─────────┐  │
│  │        In-Process Domain Event Bus / Outbox         │  │
│  └─────────────────────────┬───────────────────────────┘  │
└────────────────────────────┼──────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   PostgreSQL    │ │ Background Job  │ │  Object Storage │
│ (Managed HA +   │ │ Worker (Same    │ │   (S3 / R2)     │
│  Read Replica)  │ │ Codebase/Image) │ │  PDFs & Exports │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

#### Core Stack
1. **Application Layer (Modular Monolith):**
   * Single repository, single deployment artifact (Docker container), deployed as 2–3 stateless web instances for high availability.
   * **Strict Module Boundaries:** Separate internal packages/modules (`invoicing`, `payments`, `ledger`, `customers`, `notifications`) enforced by linter/compiler rules. Modules only talk via public service interfaces or an internal event bus—never by joining across another module's tables directly.
2. **Database (Managed PostgreSQL):**
   * A single managed PostgreSQL instance with Multi-AZ failover (e.g., AWS RDS, Cloud SQL).
   * Logical separation via **Postgres schemas** per module (`invoicing.invoices`, `ledger.entries`, `customers.tenants`).
   * Every table includes `tenant_id` (optionally enforced with PostgreSQL Row-Level Security) to isolate your 200 B2B customers cleanly.
3. **Async Processing & "Kafka Alternative" (Postgres-backed Queue + Transactional Outbox):**
   * You **do not** need Kafka for 50 RPS. Still, invoicing *does* need async workflows (generating PDFs, sending emails, syncing with Stripe/ERP, webhook retries).
   * Use the **Transactional Outbox Pattern** + a Postgres-backed job queue (e.g., `pg-boss`, `Oban`, `River`, `SolidQueue`, or `GoodJob` depending on your language, or Redis + Sidekiq/BullMQ).
   * Run 1–2 worker containers from the **exact same Docker image** with a different entrypoint (`cmd: worker`).
4. **Storage & External Integrations:**
   * **Object Storage (S3):** Store generated immutable invoice PDFs and audit exports.
   * **Compute Hosting:** Managed container platform (AWS App Runner, ECS Fargate, Google Cloud Run, or Render/Fly.io). Zero cluster upgrades, zero ingress controller debugging.

---

### 2. B2B Invoicing-Specific Design Patterns (Where the Real Complexity Lives)

Instead of spending engineering cycles on Kubernetes YAML, your 4 engineers should focus on the hard parts of financial software:

* **Double-Entry / Append-Only Ledger:** Never `UPDATE` an issued invoice's amount in place. Once an invoice transitions from `DRAFT` to `ISSUED`, it is immutable. Adjustments happen via Credit Notes or Debit Notes.
* **Transactional Outbox:** When an invoice is finalized:
  ```sql
  BEGIN;
    UPDATE invoicing.invoices SET status = 'ISSUED', number = 'INV-2026-0042' WHERE id = $1;
    INSERT INTO ledger.entries (...) VALUES (...);
    INSERT INTO outbox.events (type, payload) VALUES ('invoice.issued', '{"invoice_id": "..."}');
  COMMIT;
  ```
  The background worker polls `outbox.events` (`SELECT ... FOR UPDATE SKIP LOCKED`), generates the PDF, emails the customer, and marks the event processed. **This gives you the exact reliability guarantees the CTO wants from Kafka, inside your ACID transaction.**
* **Idempotency Keys:** All mutating endpoints (`POST /invoices`, `POST /payments`) require an `Idempotency-Key` header stored in Postgres with a unique constraint so network retries never double-bill a customer.
* **Sequential Invoice Numbering:** Many jurisdictions (e.g., EU VAT) legally require gapless sequential invoice numbers per tenant (`INV-001`, `INV-002`). This is trivial with a database row lock in PostgreSQL, and a nightmare in a distributed Kafka/microservice architecture.

---

### 3. How to Align With the CTO (The Compromise Matrix)

Usually, when a CTO asks for "Microservices + K8s + Kafka," they are actually worried about:
1. Becoming a "Big Ball of Mud" monolith that can't be untangled later.
2. High availability and zero downtime deploys.
3. Event-driven extensibility (webhooks, integrations, audit logs).

Show the CTO how this architecture satisfies every underlying goal while protecting the schedule:

| CTO's Goal | "Netflix" Approach (High Risk for 4 Devs) | Proposed Approach (Right-Sized) |
| :--- | :--- | :--- |
| **Clear service boundaries** | Network-separated microservices (gRPC/REST) | **Modular Monolith** with strict package boundaries & separate DB schemas |
| **Event-driven decoupling** | Apache Kafka + Schema Registry + Zookeeper/KRaft | **Transactional Outbox** table in Postgres + internal pub/sub handlers |
| **Container orchestration & HA** | Self-managed/EKS Kubernetes cluster | **Managed Container PaaS** (Cloud Run / ECS Fargate) with auto-scaling & rolling deploys |
| **Financial data integrity** | Distributed Sagas / 2-Phase Commit | **Native Postgres ACID transactions** across modules |
| **Operational overhead** | ~1.5–2 FTEs spent on DevOps/Infra | **< 10% of 1 FTE**; 90%+ of team focused on product |

---

### 4. The "Escape Hatch" (When to Actually Migrate)

Reassure the CTO that because you are using **strict module boundaries**, **separate Postgres schemas**, and an **event outbox**, you are **not locked in**:

* **When a module needs independent scaling** (e.g., PDF generation spikes CPU): Extract the worker into its own scaling group in 1 afternoon.
* **When event volume exceeds ~5,000 events/sec or multiple teams need event replay:** Swap the Outbox dispatcher implementation from Postgres workers to managed Kafka/Confluent or AWS SNS/SQS—none of the domain modules need to change their code.
* **When the team grows from 4 to 30+ engineers:** Because modules don't cross-join each other's schemas, you can peel a module out into a standalone microservice with AWS DMS / logical replication in days rather than months.

### sdlc-application-architecture / arch-microservices-default / with skill / PASS

Here is the application architecture design for the B2B invoicing platform, following the `sdlc-application-architecture` workflow in order.

---

## Step 1: Bounded Contexts, Domain Rules, Runtime Constraints, and Team Ownership

### 1.1 Runtime & Scale Constraints
* **Traffic:** 50 requests/second (RPS) at peak (~15–20 RPS average). A single modern relational database instance (e.g., PostgreSQL) and 2 stateless application containers easily handle 1,000+ RPS of typical CRUD/transactional load.
* **Tenant Scale:** 200 B2B customers. Even if each customer generates 10,000 invoices/year, that is 2M rows/year—well within a single PostgreSQL table without partitioning or sharding.
* **Team Topology:** 4 engineers total. By Conway's Law, a 4-person team cannot effectively own, operate, on-call, and evolve multiple independent deployment pipelines, a Kubernetes cluster, a Kafka cluster, and distributed schema registries without spending >60% of their capacity on infrastructure toil ("infra tax").

### 1.2 Domain Rules & Quality Attributes
* **Financial & Audit Integrity (Critical):** Invoice numbers must be strictly sequential per tenant/jurisdiction with no gaps once finalized. Line items, tax calculations, discounts, and totals must use exact decimal math (`DECIMAL`/`NUMERIC`, no floating-point).
* **Immutability:** Once an invoice transitions from `DRAFT` to `ISSUED`, its financial fields are immutable; corrections require Credit Notes or Debit Memos.
* **Multi-tenancy:** Strict tenant data isolation (`tenant_id` scoped at the query/repository level or via PostgreSQL Row-Level Security).
* **Availability & Latency:** Standard B2B SLA (99.9% uptime, <200ms p95 API latency, asynchronous PDF generation and email delivery).

### 1.3 Bounded Contexts
1. **Identity & Tenant Access (`identity`):** Organizations, users, roles, API keys, tenant settings.
2. **Customer & Catalog (`catalog`):** Buyer profiles, billing addresses, tax IDs/VAT numbers, billable items/rates.
3. **Invoicing Core (`invoicing`):** Draft creation, tax/total calculation, sequential numbering, state machine (`DRAFT` → `ISSUED` → `PAID` / `VOID`), credit notes.
4. **Payments & Reconciliation (`payments`):** Payment gateway webhooks (Stripe, ACH/SEPA), payment links, matching payments against open invoices.
5. **Document & Notification Delivery (`delivery`):** PDF rendering, e-invoicing XML generation (e.g., PEPPOL/Factur-X), transactional emails, webhook dispatch to B2B customers.

### 1.4 Team Ownership
With 4 engineers, **collective code ownership** over a single deployable repository is optimal, with primary stewards assigned per module:
* Engineer 1: `invoicing` (core state machine, tax, numbering)
* Engineer 2: `payments` & external gateway integrations
* Engineer 3: `delivery` (PDFs, emails, customer webhooks) & `catalog`
* Engineer 4: `identity`, platform foundation, CI/CD, and observability

---

## Step 2: Architecture Style Selection (and Addressing the CTO's Proposal)

### 2.1 Why Not Microservices + Kubernetes + Kafka?
Netflix operates thousands of engineers serving hundreds of millions of concurrent streams globally. Applying Netflix's architecture to a 4-person team serving 200 customers at 50 RPS introduces severe risks:
1. **Distributed Transactions Over Financial Data:** Splitting `invoicing`, `payments`, and `catalog` into separate microservices turns simple ACID transactions into distributed sagas over Kafka, introducing eventual consistency bugs, out-of-order event handling, and reconciliation nightmares.
2. **Operational Overload:** Managing Kubernetes upgrades, ingress controllers, Kafka brokers/partitions, consumer lag, dead-letter queues, and distributed tracing will consume 1–2 full-time engineers—25–50% of the entire engineering team.
3. **Deployment Friction:** Early-stage B2B products undergo frequent domain boundary discoveries. Refactoring across network boundaries and versioned Kafka schemas is 10x slower than refactoring across compile-time module interfaces.

### 2.2 Selected Style: Modular Monolith with Hexagonal (Ports & Adapters) Core
We will build a **Modular Monolith** deployed as a single stateless application binary/container backed by a single managed **PostgreSQL** database (using PostgreSQL both for relational storage and durable transactional background jobs/events).
* **Inside `invoicing` and `payments`:** Use **Hexagonal / Domain-Driven Design (DDD)** layers because business rules (numbering, state transitions, tax math, payment matching) are complex and must be testable without I/O.
* **Inside `identity` and `catalog`:** Use simple **Layered CRUD** to avoid boilerplate where domain logic is thin.
* **Evolution Path:** Enforced module boundaries ensure that *if* a module (e.g., PDF rendering or high-volume webhook ingestion) ever needs independent scaling, it can be extracted into a separate service in days without rewriting business logic.

---

## Step 3: Modules, Layers, Dependency Direction, Adapters, Services, Jobs, and Integrations

### 3.1 Repository & Module Structure
```text
src/
├── shared/                  # Kernel: Money VO, TenantId, Clock, Outbox/Job primitives, Auth context
├── modules/
│   ├── identity/            # Simple layered module (API -> Service -> DB)
│   ├── catalog/             # Simple layered module (API -> Service -> DB)
│   ├── invoicing/           # Hexagonal / DDD module
│   │   ├── api/             # Public module facade + DTOs + Published Domain Events
│   │   ├── domain/          # Invoice aggregate, LineItem, TaxPolicy, SequencePolicy (pure code)
│   │   ├── application/     # Use cases (IssueInvoice, VoidInvoice) + Outbound Ports
│   │   └── infrastructure/  # Postgres repositories, HTTP controllers, SQL migrations
│   ├── payments/            # Hexagonal module
│   │   ├── api/             # Public facade + PaymentReceivedEvent
│   │   ├── domain/          # Payment, Allocation, Reconciliation rules
│   │   ├── application/     # ProcessWebhook, RecordManualPayment + Ports (PaymentGatewayPort)
│   │   └── infrastructure/  # StripeAdapter, Postgres repos, Webhook controllers
│   └── delivery/            # Event-driven worker module
│       ├── application/     # GenerateInvoicePdf, SendInvoiceEmail
│       └── infrastructure/  # PDF renderer adapter, SES/Postmark adapter, S3/Blob storage adapter
```

### 3.2 Dependency Direction & Boundary Rules
Enforced in CI via static analysis (e.g., ArchUnit, Dependency Cruiser, or Go/Rust/TS package visibility rules):
1. **Inward Layer Dependency:** `infrastructure` → `application` → `domain`. `domain` has **zero** dependencies on frameworks, ORMs, HTTP, or external SDKs.
2. **Cross-Module Isolation:** Modules **cannot** import another module's `domain`, `application`, or `infrastructure` packages. They may only import another module's `api/` contract or subscribe to its published domain events.
3. **Database Schema Isolation:** Single PostgreSQL instance, separated into logical schemas per module (`identity.*`, `catalog.*`, `invoicing.*`, `payments.*`, `delivery.*`). **No cross-schema SQL `JOIN`s or foreign keys.**
   * *Note on Snapshot Integrity:* When an invoice is issued, `invoicing` calls `catalog.api` to fetch buyer/item details and **copies (snapshots)** the buyer's legal name, tax ID, address, and line-item prices directly onto the `invoicing.invoices` record. Invoices are legal documents and must never mutate if a customer later updates their address in `catalog`.

### 3.3 Background Jobs & Integration Points
Instead of Kafka, we use a **PostgreSQL-backed Transactional Outbox + Job Queue** (e.g., River, Oban, Graphile Worker, Hangfire, or `SELECT ... FOR UPDATE SKIP LOCKED`):
* **Inbound Integrations:**
  * REST/JSON API for the B2B web UI and customer API integrations.
  * Payment Gateway Webhook endpoint (`/webhooks/stripe`) verifying cryptographic signatures and writing raw webhook payloads idempotently before processing.
* **Outbound Integrations (behind Ports/Adapters):**
  * `PaymentGatewayPort` → Stripe / GoCardless Adapter.
  * `DocumentStoragePort` → S3-compatible object storage (stores immutable generated PDFs).
  * `EmailProviderPort` → Postmark / AWS SES Adapter.
  * `TaxValidationPort` → VIES / TaxJar Adapter (for VAT/tax ID validation).
* **Background Jobs:**
  * `GenerateAndSendInvoiceJob`: Triggered when `InvoiceIssued` event is committed to the outbox. Renders PDF, uploads to S3, emails customer.
  * `OverdueInvoiceScannerJob`: Daily scheduled cron job that marks past-due `ISSUED` invoices as `OVERDUE` and enqueues reminder notifications.
  * `CustomerWebhookDispatcherJob`: Delivers outbound webhooks to B2B customers with exponential backoff.

---

## Step 4: Transaction Boundaries, Failure Handling, and Deployment Implications

### 4.1 Transaction Boundaries
1. **One Aggregate / One Module per Database Transaction:**
   * Issuing an invoice (`invoicing` module) happens in a **single PostgreSQL ACID transaction**:
     1. Lock the tenant's invoice sequence row (`SELECT current_number FROM invoicing.sequences WHERE tenant_id = $1 FOR UPDATE`) to guarantee gapless sequential numbering.
     2. Update invoice status to `ISSUED`, assign the sequential number, freeze totals.
     3. Insert `InvoiceIssued` event into `shared.outbox_events` within the **exact same DB transaction**.
     4. Commit.
2. **Cross-Module Coordination via Transactional Outbox:**
   * When a payment succeeds (`payments` module), `payments` records the payment and inserts `PaymentRecorded` into the outbox in one transaction.
   * An in-process worker picks up `PaymentRecorded` and invokes `invoicing.api.ApplyPayment(invoiceId, amount)` in its own transaction, transitioning the invoice to `PAID` (or `PARTIALLY_PAID`).

### 4.2 Failure Handling & Resiliency
* **Idempotency Everywhere:**
  * All mutating B2B API endpoints (`POST /invoices`, `POST /invoices/{id}/issue`) require or support an `Idempotency-Key` header stored in PostgreSQL with a 24h TTL.
  * Incoming payment webhooks are deduplicated via a `UNIQUE(provider, provider_event_id)` constraint.
* **External I/O Never Inside DB Transactions:**
  * Never call Stripe, S3, PDF rendering, or SMTP while holding an open database transaction or row lock. All external calls happen via outbox-driven background workers.
* **Retries & Dead-Letter Queue (DLQ):**
  * Outbox/job workers retry transient failures (network timeouts, 5xx from email/payment providers) with exponential backoff + jitter (up to 10 attempts over 24 hours).
  * Exhausted jobs move to `status = 'dead_letter'`, triggering an alert in Slack/PagerDuty and exposing a simple admin endpoint/UI to inspect and replay failed jobs.

### 4.3 Deployment Implications
* **Compute:** Managed PaaS / Container service (e.g., AWS ECS Fargate, Google Cloud Run, Render, or Fly.io)—**no Kubernetes**.
  * Run 2–3 stateless instances behind a managed load balancer for zero-downtime rolling deploys and high availability across availability zones.
  * Background outbox workers run either as a lightweight worker pool within the same container image (started with `--mode=worker`) or in-process.
* **Database:** Single managed PostgreSQL instance with Multi-AZ standby failover, automated daily backups, and Point-In-Time Recovery (PITR).
* **Storage:** Managed S3 bucket with Object Lock (WORM - Write Once Read Many) enabled for issued invoice PDFs to satisfy tax/audit compliance.
* **Observability:** Structured JSON logs, OpenTelemetry traces, and Prometheus metrics exported to a managed observability provider (Datadog / Grafana Cloud / Sentry).

---

## Step 5: Architecture Decision Records (ADRs)

### ADR-001: Modular Monolith on Managed Containers Instead of Microservices on Kubernetes
* **Status:** Accepted
* **Context:** We have a 4-person engineering team building a B2B invoicing system for 200 customers with a projected peak load of 50 RPS. The CTO initially proposed microservices on Kubernetes.
* **Decision:** Build and deploy a **single Modular Monolith** on a managed container platform, enforcing strict compile-time module boundaries and isolated PostgreSQL schemas per module.
* **Consequences:**
  * *Positive:* Zero distributed transaction overhead for core invoicing; near-zero infrastructure maintenance for a 4-person team; sub-millisecond in-process module calls; fast local development and single-pipeline CI/CD.
  * *Negative:* All modules deploy together; a runaway memory leak in PDF generation could impact API requests unless worker processes are run in separate container instances (mitigated by running `--mode=api` and `--mode=worker` from the same image).
  * *Reversibility:* If traffic exceeds 2,000+ RPS or team size grows beyond 15–20 engineers, any module can be extracted into an independent service along its `api/` and PostgreSQL schema boundary.

### ADR-002: PostgreSQL Transactional Outbox Instead of Apache Kafka
* **Status:** Accepted
* **Context:** Reliable asynchronous processing is required for PDF generation, email delivery, payment reconciliation, and customer webhooks. Kafka was proposed as the event backbone.
* **Decision:** Use a **PostgreSQL-backed Transactional Outbox and Job Queue** (`FOR UPDATE SKIP LOCKED`) inside the primary database instead of running Apache Kafka.
* **Consequences:**
  * *Positive:* Atomic guarantees between domain state changes and event publication without dual-write bugs or CDC (Debezium) complexity; eliminates an entire distributed system (Kafka/ZooKeeper/KRaft) from operations and cost.
  * *Negative:* Throughput is bounded by PostgreSQL IOPS (~5,000–10,000 jobs/sec), which is 100x higher than our 50 RPS peak requirement.
  * *Trigger to Revisit:* Re-evaluate a dedicated message broker only if sustained event throughput exceeds 2,000 events/second or multiple external teams require high-volume stream replay.

### ADR-003: Logical Schema Isolation and Data Snapshotting on Invoice Issuance
* **Status:** Accepted
* **Context:** Invoicing requires data from the `catalog` module (customer details, tax IDs, item prices), and legal regulations require issued invoices to remain historically accurate even if customer records change later.
* **Decision:** Each module owns a dedicated PostgreSQL schema (`invoicing`, `catalog`, `payments`, `identity`, `delivery`). Cross-schema SQL joins and foreign keys are forbidden. When an invoice is created/issued, `invoicing` fetches customer and item data via `catalog.api` and stores an immutable snapshot on the `invoicing.invoices` table. Once `status = 'ISSUED'`, database triggers and domain rules prevent updates to financial columns; adjustments require a Credit Note.
* **Consequences:**
  * *Positive:* Complete legal/audit immutability; zero coupling between `catalog` schema changes and historical invoices; modules remain extraction-ready.
  * *Negative:* Minor data duplication of customer names/addresses across issued invoices (negligible storage impact at 200 B2B customers).

### sdlc-application-architecture / arch-microservices-default / baseline / PASS

### Executive Recommendation: Push Back on Microservices + K8s + Kafka

Before designing the system, we need to address the elephant in the room: **using Microservices, Kubernetes, and Kafka for a 4-person team serving 200 customers at 50 RPS will almost certainly cripple your team's velocity and put the product at risk.**

Netflix has 2,500+ engineers, hundreds of millions of users, and millions of requests per second. You have **4 engineers**, **200 customers**, and **50 RPS at peak**. 
- **50 RPS** can be handled effortlessly by a single $20/month virtual machine or a basic managed container instance using less than 10% of its CPU.
- **B2B Invoicing** requires **strict ACID transactions**, auditability, and strong consistency (double-entry ledgers, sequential legal invoice numbering, tax calculations, payment reconciliation). Distributed architectures with Kafka introduce eventual consistency, distributed transaction headaches (Sagas, two-phase commits, out-of-order events), and network failure modes right where you need transactional simplicity the most.
- **Conway’s Law & Operational Tax:** With 4 developers, running Kubernetes + Kafka + multiple services means at least 1–2 engineers will spend their entire time on DevOps, YAML configurations, CI/CD pipelines, distributed tracing, and schema registries instead of building invoicing features.

Instead, the right architecture is a **Modular Monolith** deployed on a simple managed PaaS, backed by a single **PostgreSQL** database (using Postgres for both relational data and durable background jobs). It gives you the clean domain boundaries of microservices *without* the operational and distributed-systems tax—and if you ever grow to 50,000 customers and 40 engineers, those modules can be extracted into services cleanly.

---

### 1. Why "Netflix Architecture" Fails Here (Talk Track for the CTO)

If you need to present a data-driven case to the CTO, frame it around **risk, cost, and time-to-market** rather than dismissing their vision:

| Dimension | Microservices + K8s + Kafka | Modular Monolith + Postgres + Managed PaaS |
| :--- | :--- | :--- |
| **Team Allocation (4 devs)** | ~50–70% spent on infra, helm charts, Kafka consumer groups, DLQs, service mesh, and cross-service debugging. | ~95% spent on product features, customer onboarding, and financial accuracy. |
| **Data Consistency (Invoicing)** | **Eventual consistency.** Creating an invoice, updating a ledger, and recording a payment across services requires Outbox patterns, Sagas, and idempotent retries. | **ACID Transactions.** `BEGIN ... COMMIT` in Postgres guarantees an invoice, its line items, and ledger entries never fall out of sync. |
| **Throughput Need (50 RPS)** | Built for 50,000+ RPS. Massive over-provisioning. | A single 2-vCPU Postgres instance handles 2,000–5,000+ TPS easily. |
| **Cloud Bill** | $1,000–$3,000+/mo minimum (Managed K8s control planes, multi-broker Managed Kafka/MSK, NAT gateways, observability ingest). | $100–$250/mo (Managed Postgres w/ HA + 2 stateless app containers + S3). |
| **Refactoring Domain Models** | High friction. In an early B2B product, domain boundaries change weekly. Changing a contract across 4 microservices and Kafka schemas takes days. | A single IDE refactor + one atomic PR and database migration. |

---

### 2. Recommended Architecture: The Modular Monolith

We satisfy the CTO's desire for **clean separation of concerns, scalability, and event-driven workflows** *inside* a single deployable unit.

```
                   [ Cloudflare / AWS WAF + CDN ]
                                 │
                                 ▼
                     [ Managed Load Balancer ]
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼
   ┌─────────────────────┐               ┌─────────────────────┐
   │  App Instance 1     │               │  App Instance 2     │
   │ (Modular Monolith)  │               │ (Modular Monolith)  │
   │                     │               │                     │
   │ ┌───────┐ ┌───────┐ │               │ ┌───────┐ ┌───────┐ │
   │ │Tenants│ │Billing│ │               │ │Tenants│ │Billing│ │
   │ └───────┘ └───────┘ │               │ └───────┘ └───────┘ │
   │ ┌───────┐ ┌───────┐ │               │ ┌───────┐ ┌───────┐ │
   │ │Payment│ │Ledger │ │               │ │Payment│ │Ledger │ │
   │ └───────┘ └───────┘ │               │ └───────┘ └───────┘ │
   │ [In-Process Workers]│               │ [In-Process Workers]│
   └──────────┬──────────┘               └──────────┬──────────┘
              │                                     │
              └──────────────────┬──────────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────┐
              │   Managed PostgreSQL (Primary)      │──────► [ Standby Replica (Multi-AZ) ]
              │  - Relational Tables (ACID + RLS)   │
              │  - Transactional Outbox / Job Queue │
              │  - Immutable Audit Log              │
              └──────────────────┬──────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
[ Object Storage (S3) ]  [ Payment Gateway ]      [ Email / E-Invoicing ]
  (Immutable PDFs)       (Stripe / Adyen / ACH)   (Postmark / Peppol API)
```

#### A. Compute & Deployment
- **Runtime:** 2 stateless application instances (for zero-downtime deploys and high availability) running on **AWS ECS Fargate, Google Cloud Run, Render, or Fly.io**.
- **Stack:** TypeScript (Node.js/NestJS), Go, C# (.NET), or Java (Spring Boot Modulith)—whichever the 4 developers already know best.
- **Frontend:** Served statically via CDN or a unified full-stack framework, communicating with the backend via REST/OpenAPI or tRPC.

#### B. Strict Internal Module Boundaries (The "Microservice-Ready" Compromise)
Enforce strict package/module boundaries in the monolith using linter rules (e.g., Spring Modulith, ArchUnit, or ESLint boundaries):
1. **`identity-and-tenants`:** Organizations, users, RBAC, API keys, SSO.
2. **`customers-and-catalog`:** B2B buyer profiles, tax IDs (VAT/EIN), contract terms (Net-30, Net-60), products/rates.
3. **`invoicing`:** Drafts, tax calculation, sequential legal numbering, finalization, credit notes, PDF generation triggers.
4. **`payments`:** Payment links, Stripe/ACH/Wire webhook ingestion, payment matching, dunning (overdue reminders).
5. **`ledger-and-reporting`:** Immutable double-entry accounting entries, audit trails, CSV/ERP exports (QuickBooks, Xero, NetSuite).

**Rule for the CTO:** Modules cannot query each other’s tables directly via SQL joins if you want future extractability; they communicate via **well-defined internal service interfaces** and **transactional domain events**.

#### C. Database: Managed PostgreSQL (Single Source of Truth)
- **Managed Service:** AWS RDS, Cloud SQL, or Supabase (Multi-AZ enabled for automatic failover, PITR backups enabled).
- **Multi-Tenancy:** Shared schema with a mandatory `tenant_id` column on every table, enforced via **PostgreSQL Row-Level Security (RLS)** so a bug in a query can never leak Customer A's invoices to Customer B.
- **Financial Integrity:**
  - All monetary values stored as **integer minor units (cents)** or `NUMERIC(19, 4)` + explicit ISO currency code (`currency CHAR(3)`). Never `FLOAT`.
  - Invoices are **immutable once finalized**. Changes require issuing a Credit Note or Revision record.
  - Sequential gapless invoice numbers per tenant (required by law in the EU and many jurisdictions) handled via a per-tenant counter row locked with `SELECT ... FOR UPDATE` inside the invoice finalization transaction.

#### D. Replacing Kafka: Postgres-Backed Durable Queue + Outbox Pattern
The CTO wants Kafka for asynchronous event processing (e.g., *"When an invoice is finalized, generate a PDF, email the client, and sync to QuickBooks"*).
- Instead of running a Kafka cluster, use a **PostgreSQL-backed job queue** (`pg-boss` for Node, `River` for Go, `Oban` for Elixir, or `Hangfire`/`Quartz` for .NET/Java).
- **How it works (Transactional Outbox):**
  1. In a single database transaction: update the invoice status to `FINALIZED` **and** insert an `InvoiceFinalized` event/job row into the `jobs` table.
  2. Commit the transaction.
  3. Worker threads (running in the same app container or a 3rd worker container) poll/listen via Postgres `LISTEN/NOTIFY` and `SELECT ... FOR UPDATE SKIP LOCKED`, generate the PDF, upload to S3, and send the email.
- **Result:** Zero lost events, built-in retries, dead-letter queues, and ACID atomicity between state changes and events—with **zero extra infrastructure to manage**.

---

### 3. Critical B2B Invoicing Workflows

1. **Idempotency Everywhere:**
   - Every state-changing API endpoint (`POST /invoices`, `POST /invoices/{id}/finalize`, incoming payment webhooks) must require or record an `Idempotency-Key` stored in Postgres with a unique constraint `(tenant_id, idempotency_key)`.
   - Payment webhooks (Stripe/Adyen) are written raw to an `inbound_webhooks` table first, acknowledged with `200 OK`, and processed idempotently by the Postgres job worker.
2. **PDF Generation & Archival:**
   - PDFs are rendered asynchronously by the background worker (using a headless Chromium sidecar or a lightweight PDF library), uploaded to an **S3 bucket with Object Lock (WORM - Write Once Read Many)** for legal compliance, and served via signed URLs.
3. **Scheduled Jobs (Cron):**
   - Recurring invoices, Net-30 overdue checks, and dunning emails run via the Postgres job scheduler using distributed locks (`pg_try_advisory_lock`) so only one instance triggers the daily run.
4. **Observability (Simple & Actionable):**
   - Structured JSON logs + OpenTelemetry sent to a managed platform (Datadog, Honeycomb, or Grafana Cloud free/starter tier) + Sentry for error tracking.

---

### 4. The Compromise Roadmap (How to Win Over the CTO)

If the CTO is worried about "painting ourselves into a corner," propose **Architecture Fitness Triggers**—explicit thresholds where the team agrees to introduce new infrastructure *only when the metric is hit*:

1. **Now (200 customers, 50 RPS, 4 devs):**
   - Modular Monolith + Postgres (with Outbox/Queue) + S3 on ECS Fargate / Cloud Run.
   - Strict module interfaces so code stays clean.
2. **Trigger 1 — Separate Worker Scaling (~500 RPS or heavy PDF CPU spikes):**
   - Deploy the exact same codebase with a `--mode=worker` flag as a separate auto-scaling container group so PDF generation doesn't compete with API latency.
3. **Trigger 2 — Read Replicas (~2,000+ RPS):**
   - Route heavy reporting/analytics queries to a Postgres Read Replica.
4. **Trigger 3 — Kafka / Event Broker (>10,000 RPS or 15+ developers split into multiple teams):**
   - Because all cross-module events already flow through an `EventPublisher` interface backed by the Postgres Outbox, swapping the outbox relay to publish to Kafka later requires changing **one adapter class**, not rewriting the application.

### sdlc-application-architecture / arch-microservices-default / with skill / PASS

Following the **sdlc-application-architecture** workflow, here is the architectural design for your B2B invoicing application, evaluated against your actual constraints rather than Big Tech cargo-culting.

---

### Step 1: Bounded Contexts, Domain Rules, Runtime Constraints, and Team Ownership

* **Team Ownership:** 4 engineers total. In a microservices + Kubernetes + Kafka setup, at least 1.5–2 engineers would be consumed full-time by platform operations, CI/CD pipelines, schema registries, distributed tracing, and broker maintenance—cutting feature velocity in half.
* **Runtime & Scale Constraints:** 
  * **200 B2B customers** and **50 requests/sec (RPS) at peak**.
  * A single modern relational database (PostgreSQL) on modest hardware easily handles 5,000+ simple queries/sec and hundreds of complex ACID transactions/sec. 50 RPS can be served by 2 small stateless application instances with <10% CPU utilization.
* **Domain Rules (B2B Invoicing):**
  * **Strict financial invariants:** Sequential gapless invoice numbering (required by tax authorities), tax/VAT calculation precision, immutable issued invoices, credit notes, and double-entry ledger reconciliation.
  * **High consistency requirement:** Generating an invoice, updating customer balance, and recording an audit trail must succeed or fail atomically. Eventual consistency across microservices creates reconciliation nightmares for financial data.
* **Bounded Contexts:**
  1. `Identity & Tenant Management` (B2B organizations, users, roles, API keys)
  2. `Catalog & Customer Directory` (Buyer profiles, tax IDs, billable items, pricing tiers)
  3. `Invoicing` (Core domain: draft creation, tax calculation, gapless sequence allocation, finalization, credit notes)
  4. `Payments & Reconciliation` (Payment gateway webhooks, bank feeds, matching payments to invoices, dunning/reminders)
  5. `Reporting & Compliance` (PDF rendering, e-invoicing XML/Peppol export, tax summaries, audit logs)

---

### Step 2: Architecture Style Selection

**Chosen Style: Modular Monolith with Hexagonal (Ports & Adapters) Boundaries inside core domain modules.**

**Why not Microservices + Kubernetes + Kafka?**
* **Netflix's constraints ≠ Your constraints:** Netflix operates thousands of engineers streaming video to 250M+ subscribers globally. You have 4 engineers serving 200 businesses at 50 RPS.
* **Operational tax:** Microservices trade in-memory function calls and ACID database transactions for network latency, partial failures, distributed sagas, and operational complexity.
* **Evolutionary path:** A Modular Monolith enforces strict logical boundaries in code *today* (preventing a "Big Ball of Mud") while deploying as a single artifact. If a specific module (e.g., PDF generation) ever needs independent scaling, its clean boundary allows extracting it in days.

---

### Step 3: Modules, Layers, Dependency Direction, Adapters, Jobs, and Integrations

#### Module Structure & Internal Layers
Each bounded context lives in its own top-level module (`modules/invoicing`, `modules/payments`, etc.) with three internal layers:
1. **Domain Layer (Inner):** Pure business logic, entities (`Invoice`, `LineItem`), value objects (`Money`, `TaxRate`), and domain interfaces (Ports). **Zero dependencies** on frameworks, ORM, or HTTP.
2. **Application Layer (Middle):** Use-case orchestrators / Command handlers (`IssueInvoiceHandler`, `RecordPaymentHandler`), DTOs, and transaction scripts. Depends only on the Domain layer.
3. **Infrastructure / Adapters Layer (Outer):**
   * *Inbound (Driving) Adapters:* REST/GraphQL controllers, webhook receivers, CLI commands.
   * *Outbound (Driven) Adapters:* PostgreSQL repositories, Stripe/Adyen SDK clients, S3 storage, SMTP/SES email adapters.

#### Dependency Direction Rules (Enforced in CI via ArchUnit / Depcruiser / linter)
* `Infrastructure -> Application -> Domain` (Dependencies point strictly inward).
* **Cross-module rule:** Module A (`payments`) may **never** import internal Domain or Infrastructure classes from Module B (`invoicing`).
* Modules communicate exclusively via:
  1. **Public Application Contracts (Facade/API):** Synchronous in-process method calls using primitive/DTO contracts.
  2. **In-Process / Outbox Domain Events:** e.g., `PaymentReceived` published by `payments` and consumed by `invoicing` to mark an invoice as `PAID`.

#### Background Jobs & Integration Points
* **Jobs Engine:** Database-backed job queue (e.g., Oban for Elixir, River/PgQueuer for Go/Node, Sidekiq/GoodJob for Ruby, or Spring Modulith/Quartz for Java) running in PostgreSQL—eliminating the need for Kafka.
* **Scheduled/Async Jobs:**
  * `GenerateInvoicePdfJob` (renders PDF asynchronously or on-demand, uploads to S3).
  * `SendInvoiceNotificationJob` (emails PDF + payment link via Postmark/SES).
  * `DunningReminderJob` (daily cron checking overdue invoices and triggering reminders).
* **External Integrations:**
  * Payment Gateways (Stripe / GoCardless) via idempotent webhook adapters.
  * Tax/VAT Validation APIs (VIES / Stripe Tax) wrapped behind a `TaxValidatorPort` with local caching.
  * Object Storage (S3/R2) for immutable PDF and XML archive storage.

---

### Step 4: Transaction Boundaries, Failure Handling, and Deployment Implications

#### Transaction Boundaries
* **One Database, Schema/Table-per-Module Ownership:** Single PostgreSQL instance. Tables are prefixed or separated by PostgreSQL schemas (`invoicing.invoices`, `payments.transactions`). Cross-module SQL `JOIN`s are forbidden in write paths.
* **Atomic Command Execution:** Issuing an invoice opens a single PostgreSQL ACID transaction:
  1. Locks the tenant's invoice sequence row (`SELECT ... FOR UPDATE`) to guarantee gapless legal numbering.
  2. Persists the finalized `Invoice` and `LineItems`.
  3. Writes an `InvoiceIssued` event to the `outbox_events` table in the **same transaction**.
  4. Commits.

#### Failure Handling
* **Transactional Outbox Pattern:** Background workers poll `outbox_events` with `FOR UPDATE SKIP LOCKED` to trigger PDF generation and emails. If the email provider is down, the invoice remains safely committed, and the job retries with exponential backoff + jitter.
* **Idempotency:** All write endpoints (`POST /invoices`, payment webhooks) require an `Idempotency-Key` header or webhook event ID stored in a unique constraint table to prevent duplicate invoices or double-charging on network retries.
* **Dead-Letter Queue (DLQ):** Failed jobs after $N$ retries move to a `failed_jobs` table and trigger a Slack/PagerDuty alert for the engineering team.

#### Deployment Implications
* **Compute:** 2 stateless application containers (for high availability and zero-downtime rolling deploys) running on a managed PaaS (AWS ECS Fargate, Render, Fly.io, or Cloud Run)—**no Kubernetes cluster management**.
* **Worker Process:** Either runs as a background thread pool inside the web containers or as 1 dedicated worker container running the exact same Docker image with a different entrypoint (`cmd: worker`).
* **Database:** Managed PostgreSQL (AWS RDS or Cloud SQL) with Multi-AZ failover, automated daily backups, and Point-in-Time Recovery (PITR).

---

### Step 5: Architecture Decision Records (ADRs)

#### ADR-001: Adopt Modular Monolith over Microservices
* **Status:** Accepted
* **Context:** The CTO proposed microservices with Kubernetes and Kafka ("like Netflix"). However, we have a 4-person team, 200 B2B customers, 50 peak RPS, and strict financial ACID requirements.
* **Decision:** Build a single deployable Modular Monolith backed by PostgreSQL, organized by strict bounded-context modules with automated boundary linting in CI.
* **Consequences:**
  * *Positive:* Near-zero DevOps overhead; simple local development (`docker compose up`); ACID transactions for financial invariants; single CI/CD pipeline.
  * *Negative:* Requires discipline and CI static analysis to prevent cross-module coupling. All modules scale and deploy together until extraction is warranted.

#### ADR-002: PostgreSQL Transactional Outbox & Job Queue over Apache Kafka
* **Status:** Accepted
* **Context:** We need reliable asynchronous processing for PDF generation, email delivery, and cross-module event handling (`InvoiceIssued`, `PaymentSucceeded`).
* **Decision:** Use PostgreSQL as both our transactional store and durable job/event queue (`FOR UPDATE SKIP LOCKED`) via the Transactional Outbox pattern instead of deploying Apache Kafka.
* **Consequences:**
  * *Positive:* Eliminates dual-write bugs without complex CDC (Debezium) pipelines; removes Kafka operational cost and operational burden; easily handles up to ~1,000 jobs/sec (20x our peak load).
  * *Negative:* Not suited for high-throughput log streaming (100k+ events/sec). If event volume ever exceeds PostgreSQL queue capacity, the `EventPublisherPort` interface can be swapped to Kafka or SQS without changing domain code.

#### ADR-003: Logical Schema Separation and No Cross-Module Joins on Write Paths
* **Status:** Accepted
* **Context:** In a monolith sharing one database, teams often take shortcuts by joining tables across bounded contexts, making future extraction impossible.
* **Decision:** Each module owns its database tables exclusively. No module may write to or join another module's tables in transactional code. Read-heavy cross-context reporting must use dedicated read-models or the `reporting` module.
* **Consequences:**
  * *Positive:* Preserves clean seams so any module (`invoicing`, `payments`, `reporting`) can be extracted into a standalone service in the future with minimal refactoring.
  * *Negative:* Slight data duplication across modules (e.g., caching a snapshot of buyer name/address inside the `invoicing` table—which is also a legal requirement for immutable invoices).

### sdlc-design-brainstorming / design-gate / baseline / FAIL

Because I don't have context on your codebase or requirements yet, I need to clarify a few critical details before writing code, or I can provide a reference implementation based on a standard stack.

### Quick Clarifications
1. **Tech Stack**: What backend, frontend, and database are you using (e.g., TypeScript/Node.js + Postgres + React, Python/FastAPI, Java/Spring Boot)?
2. **Delivery Channels**: Which channels do you need?
   - **In-app** (bell icon feed, unread badge, real-time WebSocket/SSE)
   - **Email** (SendGrid, SES, Resend)
   - **Push** (Web Push, FCM/APNs)
   - **Webhooks / Slack / SMS**
3. **Core Features**: Do you need user notification preferences (opt-in/out per channel/event), batching/digests, or retry queues right now, or just a clean MVP?

---

### Reference MVP Implementation (TypeScript / Node.js + In-App & Multi-Channel Ready)

So you can start right away, here is a clean, extensible notification engine in TypeScript with **in-app persistence**, **real-timeSSE/WebSocket hooks**, **channel routing**, and **user preference support**.

#### 1. Domain Types & Interfaces (`notifications/types.ts`)

```typescript
export type NotificationChannel = 'in_app' | 'email' | 'push';

export type NotificationType =
  | 'comment.mention'
  | 'task.assigned'
  | 'system.alertBilling';

export interface NotificationPayload {
  userId: string;
  type: NotificationType;
  title: string;
  body: string;
  actionUrl?: string;
  metadata?: Record<string, unknown>;
  channels?: NotificationChannel[]; // Defaults to user preferences if omitted
}

export interface NotificationRecord {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  body: string;
  actionUrl?: string;
  metadata: Record<string, unknown>;
  readAt: Date | null;
  createdAt: Date;
}

export interface ChannelProvider {
  readonly channel: NotificationChannel;
  send(notification: NotificationRecord): Promise<void>;
}

export interface NotificationRepository {
  create(data: Omit<NotificationRecord, 'id' | 'readAt' | 'createdAt'>): Promise<NotificationRecord>;
  listForUser(userId: string, opts: { unreadOnly?: boolean; limit?: number; cursor?: string }): Promise<NotificationRecord[]>;
  markAsRead(userId: string, notificationIds: string[]): Promise<number>;
  markAllAsRead(userId: string): Promise<number>;
  getUnreadCount(userId: string): Promise<number>;
}

export interface PreferenceService {
  getEnabledChannels(userId: string, type: NotificationType): Promise<NotificationChannel[]>;
}
```

#### 2. Core Notification Service (`notifications/service.ts`)

```typescript
import {
  ChannelProvider,
  NotificationChannel,
  NotificationPayload,
  NotificationRecord,
  NotificationRepository,
  PreferenceService,
} from './types';

export class NotificationService {
  private providers = new Map<NotificationChannel, ChannelProvider>();

  constructor(
    private readonly repo: NotificationRepository,
    private readonly preferences: PreferenceService,
  ) {}

  registerProvider(provider: ChannelProvider): void {
    this.providers.set(provider.channel, provider);
  }

  async notify(payload: NotificationPayload): Promise<NotificationRecord> {
    // 1. Persist the canonical notification record
    const record = await this.repo.create({
      userId: payload.userId,
      type: payload.type,
      title: payload.title,
      body: payload.body,
      actionUrl: payload.actionUrl,
      metadata: payload.metadata ?? {},
    });

    // 2. Resolve target channels (explicit override or user preferences)
    const channels =
      payload.channels ??
      (await this.preferences.getEnabledChannels(payload.userId, payload.type));

    // 3. Dispatch to each enabled channel concurrently without failing the whole call
    const results = await Promise.allSettled(
      channels.map(async (ch) => {
        const provider = this.providers.get(ch);
        if (!provider) {
          throw new Error(`No provider registered for channel: ${ch}`);
        }
        await provider.send(record);
      }),
    );

    for (const res of results) {
      if (res.status === 'rejected') {
        console.error('[NotificationService] Channel delivery failed:', res.reason);
      }
    }

    return record;
  }

  listForUser(userId: string, opts: { unreadOnly?: boolean; limit?: number; cursor?: string } = {}) {
    return this.repo.listForUser(userId, opts);
  }

  markAsRead(userId: string, ids: string[]) {
    return this.repo.markAsRead(userId, ids);
  }

  markAllAsRead(userId: string) {
    return this.repo.markAllAsRead(userId);
  }

  getUnreadCount(userId: string) {
    return this.repo.getUnreadCount(userId);
  }
}
```

#### 3. Channel Providers (`notifications/providers.ts`)

```typescript
import { EventEmitter } from 'events';
import { ChannelProvider, NotificationRecord } from './types';

/**
 * Streams real-time in-app notifications over Server-Sent Events (SSE) or WebSockets.
 */
export class InAppRealtimeProvider implements ChannelProvider {
  readonly channel = 'in_app' as const;
  private bus = new EventEmitter();

  async send(notification: NotificationRecord): Promise<void> {
    this.bus.emit(`user:${notification.userId}`, notification);
  }

  subscribe(userId: string, onNotification: (n: NotificationRecord) => void): () => void {
    const event = `user:${userId}`;
    this.bus.on(event, onNotification);
    return () => this.bus.off(event, onNotification);
  }
}

/**
 * Email channel adapter (plug in Resend, SendGrid, AWS SES, or Nodemailer).
 */
export class EmailProvider implements ChannelProvider {
  readonly channel = 'email' as const;

  constructor(
    private readonly lookupEmail: (userId: string) => Promise<string | null>,
    private readonly sendEmail: (opts: { to: string; subject: string; text: string }) => Promise<void>,
  ) {}

  async send(notification: NotificationRecord): Promise<void> {
    const email = await this.lookupEmail(notification.userId);
    if (!email) return;

    const body = notification.actionUrl
      ? `${notification.body}\n\nView: ${notification.actionUrl}`
      : notification.body;

    await this.sendEmail({
      to: email,
      subject: notification.title,
      text: body,
    });
  }
}
```

#### 4. HTTP / SSE Routes (`notifications/routes.ts`)

```typescript
import { Router, Request, Response } from 'express';
import { NotificationService } from './service';
import { InAppRealtimeProvider } from './providers';

export function createNotificationRouter(
  service: NotificationService,
  realtime: InAppRealtimeProvider,
): Router {
  const router = Router();

  // List notifications for the authenticated user
  router.get('/', async (req: Request, res: Response) => {
    const userId = req.headers['x-user-id'] as string; // Replace with your auth middleware
    const unreadOnly = req.query.unreadOnly === 'true';
    const limit = Math.min(Number(req.query.limit) || 20, 100);

    const [items, unreadCount] = await Promise.all([
      service.listForUser(userId, { unreadOnly, limit }),
      service.getUnreadCount(userId),
    ]);

    res.json({ items, unreadCount });
  });

  // Real-time SSE stream
  router.get('/stream', (req: Request, res: Response) => {
    const userId = req.headers['x-user-id'] as string;
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders();

    const unsubscribe = realtime.subscribe(userId, (notification) => {
      res.write(`data: ${JSON.stringify(notification)}\n\n`);
    });

    req.on('close', () => {
      unsubscribe();
      res.end();
    });
  });

  // Mark specific notifications as read
  router.post('/read', async (req: Request, res: Response) => {
    const userId = req.headers['x-user-id'] as string;
    const ids: string[] = Array.isArray(req.body?.ids) ? req.body.ids : [];
    const updated = await service.markAsRead(userId, ids);
    res.json({ updated });
  });

  // Mark all as read
  router.post('/read-all', async (req: Request, res: Response) => {
    const userId = req.headers['x-user-id'] as string;
    const updated = await service.markAllAsRead(userId);
    res.json({ updated });
  });

  return router;
}
```

#### 5. SQL Schema (PostgreSQL)

```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  type VARCHAR(64) NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  action_url TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Fast lookup for a user's feed and unread badge count
CREATE INDEX idx_notifications_user_created
  ON notifications (user_id, created_at DESC);

CREATE INDEX idx_notifications_user_unread
  ON notifications (user_id)
  WHERE read_at IS NULL;
```

---

Tell me your **stack**, **database**, and **desired channels/UI**, and I will tailor the implementation (e.g., Prisma/Drizzle repository, React notification bell component, BullMQ/Redis retry queue, or another language/framework).

### sdlc-design-brainstorming / design-gate / with skill / PASS

I cannot start coding yet—following the `sdlc-design-brainstorming` process, we have a hard gate that requires turning this request into an approved design before any implementation or scaffolding begins.

### Step 1 & 2: Project Exploration & Subsystem Check
*(Since there is no repository access in this exercise, I cannot inspect existing docs, commits, or conventions directly.)*

Note that a full "notification system" often spans several independent subsystems—such as **event ingestion/routing**, **delivery channels** (in-app, email, push), **user preferences**, and **frontend UI/real-time feeds**. If you intend to build all of these, we should decompose them into separate specs first and tackle the foundational slice before refining details for the rest.

### Step 3: Clarifying Question (1 of N)
To narrow down the initial scope and purpose, **what is the primary delivery channel and use case we need to support for this first iteration?**

- **A)** In-app notifications only (e.g., a notification bell/inbox in the UI for user-facing app events)
- **B)** External transactional alerts (e.g., email or SMS triggered by critical account/system events)
- **C)** Mobile/web push notifications
- **D)** Multi-channel routing engine (if so, we will decompose this into separate subsystem specs first)
- **E)** Other (please describe your existing stack and the specific problem this solves)

### sdlc-design-brainstorming / design-gate / baseline / FAIL

Before writing the code, I need a few quick details since I don't have access to the repository:

1. **Tech Stack:** What backend language/framework, frontend framework, and database are we using?
2. **Delivery Channels:** Which channels do you need (e.g., in-app notification bell/feed, real-time WebSockets/SSE, email, push, SMS)?
3. **Core Features:** Do you need read/unread tracking, user notification preferences (opt-in/out per channel), or batching/digests?

---

### Starter Implementation (TypeScript / Node.js)

If you want to start immediately with a standard pattern, here is a clean, extensible **multi-channel Notification Service** with in-app persistence and real-time hooks that you can drop into a TypeScript/Node backend:

```typescript
// types/notification.ts
export type NotificationChannel = 'in_app' | 'email' | 'push';

export type NotificationType =
  | 'comment.reply'
  | 'task.assigned'
  | 'billing.invoice_paid'
  | 'system.alert';

export interface NotificationPayload {
  userId: string;
  type: NotificationType;
  title: string;
  body: string;
  actionUrl?: string;
  metadata?: Record<string, unknown>;
  channels?: NotificationChannel[];
}

export interface InAppNotification extends Omit<NotificationPayload, 'channels'> {
  id: string;
  readAt: Date | null;
  createdAt: Date;
}
```

```typescript
// providers/channel-provider.ts
import { NotificationChannel, NotificationPayload } from '../types/notification';

export interface ChannelProvider {
  readonly channel: NotificationChannel;
  send(payload: NotificationPayload): Promise<void>;
}

export class InAppProvider implements ChannelProvider {
  readonly channel = 'in_app' as const;

  constructor(
    private readonly db: {
      insertNotification: (data: NotificationPayload) => Promise<string>;
    },
    private readonly realtime: {
      emitToUser: (userId: string, event: string, data: unknown) => void;
    }
  ) {}

  async send(payload: NotificationPayload): Promise<void> {
    const id = await this.db.insertNotification(payload);
    this.realtime.emitToUser(payload.userId, 'notification:new', {
      id,
      ...payload,
      readAt: null,
      createdAt: new Date().toISOString(),
    });
  }
}

export class EmailProvider implements ChannelProvider {
  readonly channel = 'email' as const;

  constructor(
    private readonly mailer: {
      sendMail: (toUserId: string, subject: string, body: string) => Promise<void>;
    }
  ) {}

  async send(payload: NotificationPayload): Promise<void> {
    await this.mailer.sendMail(payload.userId, payload.title, payload.body);
  }
}
```

```typescript
// services/notification-service.ts
import { ChannelProvider } from '../providers/channel-provider';
import { NotificationChannel, NotificationPayload, NotificationType } from '../types/notification';

export interface UserPreferencesStore {
  getEnabledChannels(userId: string, type: NotificationType): Promise<NotificationChannel[]>;
}

export class NotificationService {
  private providers = new Map<NotificationChannel, ChannelProvider>();

  constructor(
    providers: ChannelProvider[],
    private readonly preferences: UserPreferencesStore
  ) {
    for (const provider of providers) {
      this.providers.set(provider.channel, provider);
    }
  }

  async notify(payload: NotificationPayload): Promise<{
    sent: NotificationChannel[];
    failed: { channel: NotificationChannel; error: unknown }[];
  }> {
    const allowedChannels = await this.preferences.getEnabledChannels(
      payload.userId,
      payload.type
    );

    const requestedChannels = payload.channels ?? ['in_app'];
    const targetChannels = requestedChannels.filter((ch) =>
      allowedChannels.includes(ch)
    );

    const sent: NotificationChannel[] = [];
    const failed: { channel: NotificationChannel; error: unknown }[] = [];

    await Promise.all(
      targetChannels.map(async (channel) => {
        const provider = this.providers.get(channel);
        if (!provider) {
          failed.push({ channel, error: new Error(`No provider registered for ${channel}`) });
          return;
        }
        try {
          await provider.send(payload);
          sent.push(channel);
        } catch (error) {
          failed.push({ channel, error });
        }
      })
    );

    return { sent, failed };
  }
}
```

Let me know your stack and requirements, and I'll tailor the database schema, API endpoints, and UI components to match your app.

### sdlc-design-brainstorming / design-gate / with skill / PASS

Following the **`sdlc-design-brainstorming`** workflow, I must hold off on writing any code or scaffolding until we clarify the requirements, compare approaches, and get your explicit approval on a design.

Also, **"a notification system" often spans several independent subsystems** (e.g., event ingestion & routing, delivery channels like email/push/SMS, in-app UI & real-time state, and user preference management). Depending on what you need, we should either scope this down to a minimal core or decompose it into separate specs before refining details.

Since we have no repository access in this exercise to inspect your existing stack and conventions (Step 1), let's start with the first clarifying question (Step 2 & 3 — one question at a time):

### Question 1: What is the primary delivery channel and scope for this initial version?

- **A)** **In-app notifications only** (e.g., a notification bell/feed inside the app UI, stored in the database)
- **B)** **Transactional external messages only** (e.g., sending emails, SMS, or mobile push when specific events happen)
- **C)** **Unified multi-channel system** (both in-app feed and external channels like email/push, which we should decompose into separate subsystem specs)
- **D)** **Something else** (please describe your existing stack and primary use case)

### sdlc-design-brainstorming / design-small-change-pressure / baseline / FAIL

I cannot produce a valid diff without knowing the actual file and function structure of your deploy CLI—or which side effects `--dry-run` should skip versus still execute.

Even for a small flag, two things matter before writing the patch:

1. **The CLI entrypoint**: Paste the relevant file (or tell me the language/CLI framework and function signatures) so the diff targets your real code rather than a fabricated placeholder.
2. **Dry-run boundary**: Confirm what `--dry-run` should still do versus skip—for example:
   - Still validate configuration, credentials, or build artifacts?
   - Print the exact commands/API payloads/plan it *would* execute, and skip only the remote mutation/deploy step?

Share the CLI snippet (and your preferred dry-run boundary if it isn't just "validate and log the deploy action without executing it"), and I will give you the exact diff right away.

### sdlc-design-brainstorming / design-small-change-pressure / with skill / FAIL

Per the `sdlc-design-brainstorming` rules, design approval is a hard gate (**no code or diffs until the design is approved**), and **a small change gets a short design, not a skipped one**. We'll keep this lightweight and fast.

Since there is no repository access in this exercise to inspect the existing CLI structure (Step 1), let's clarify the core requirement first (Step 3—one question at a time):

**What should `--dry-run` actually execute vs. skip in your deploy CLI?**

- **A) Config & plan only:** Validate configuration/flags, resolve target environment and artifacts, and print the planned deployment steps without making any network calls.
- **B) Read-only preflight + plan:** Run read-only checks against the target environment (e.g., auth check, cluster/server reachability, diffing current vs. target state) and print what would change, skipping only state-mutating operations.
- **C) Remote dry-run delegation:** Pass the dry-run flag through to the underlying deployment provider/API (e.g., `kubectl --dry-run=server`, Terraform plan, or cloud API dry-run) and output its response.
- **D) Other** (please describe).

### sdlc-design-brainstorming / design-small-change-pressure / baseline / FAIL

I cannot produce a valid diff without knowing the structure of your deploy CLI and what `--dry-run` should actually do. Even for a small flag, a few details are missing:

1. **Codebase & CLI framework**: What language, file path, and argument parser (e.g., Python `argparse`/`click`/`typer`, Go `cobra`/`flag`, Node `commander`/`yargs`, Bash `getopts`) does the deploy CLI use?
2. **Dry-run semantics**: Where should execution stop or branch?
   - Should it only print the commands/API calls it *would* run without executing them?
   - Should it still run pre-deploy steps (e.g., config validation, build/artifact checks, diffing against the target environment) or skip everything that touches external systems?
   - Should it pass `--dry-run` down to underlying tools (e.g., `kubectl --dry-run=client`, `terraform plan`, `helm --dry-run`, `rsync -n`)?

Paste the relevant CLI entrypoint/deploy function (or tell me the language/framework and desired behavior), and I will give you the exact diff right away.

### sdlc-design-brainstorming / design-small-change-pressure / with skill / FAIL

Per the `sdlc-design-brainstorming` rules, design approval is a hard gate before writing any code or diffs—and a small change gets a short design rather than a skipped one. 

To keep this brief and get us to the diff quickly, let's clarify the core requirement first (one question at a time):

**What should the `--dry-run` flag do when executed?**
- **A)** Print the planned deployment steps/commands to stdout without making any network calls or remote state changes.
- **B)** Run pre-flight checks, config validation, and read-only API calls (e.g., diffing local vs. remote state) without applying the deployment.
- **C)** Send a dry-run parameter directly to the remote deployment API/backend and output its simulated response.
- **D)** Something else (please specify).

### sdlc-design-brainstorming / design-decompose-scaffold / baseline / PASS

Before scaffolding the repository and writing the first modules, a few high-impact architectural and domain decisions need to be locked in. Generating code across 8 domains without these will force assumptions that are expensive to unwind later.

Please clarify the following:

### 1. Tech Stack & Monorepo Layout
- **Backend**: TypeScript (NestJS / Fastify), Go, Python (FastAPI), or Java/Kotlin (Spring Boot)?
- **Web (Buyer/Vendor/Admin & Analytics)**: Next.js (App Router) or React SPA?
- **Mobile**: React Native (Expo) or Flutter?
- **Database & Search**: PostgreSQL + Prisma/Drizzle + Meilisearch/Typesense/Elasticsearch, or a simple Postgres `tsvector` FTS to start?

### 2. B2B Domain Model (The Core Differentiators)
- **Pricing model**: Standard public catalog prices, **tiered volume pricing** (MOQ / quantity breaks), **customer-specific contract price lists**, or **RFQ / quote-to-order** workflows?
- **Buyer accounts**: Single-user buyers, or multi-user **Company Organizations** with roles (Buyer, Approver, Finance) and spend/approval limits?

### 3. Payments, Invoicing & Payouts
- **Payment rail**: Stripe Connect (split payouts + escrow), Adyen for Platforms, or manual wire/ACH reconciliation?
- **B2B payment terms**: Immediate card/bank capture at checkout only, or **Net-15 / Net-30 / Net-60 terms** with credit limits and invoice generation prior to payment?
- **Vendor onboarding**: Full automated KYB via payment provider (e.g., Stripe Connect onboarding), or an internal document-upload + manual admin approval queue?

### 4. Starting Slice
After the monorepo scaffold + shared database schema, which **two modules** do you want fully implemented first?
1. **Identity + Vendor Onboarding** (Organizations, KYB, Admin Approval)
2. **Catalog + B2B Pricing & Search** (Products, SKUs, Tiered Pricing, Search Index)
3. **Checkout + Orders + Invoicing/Payments** (Cart, Net-terms/Stripe Checkout, PDF/JSON Invoice ledger)

---

*Reply with your preferences (or say **"use sensible defaults"** for a TypeScript/Turborepo stack: Next.js + NestJS/Fastify + Expo + Postgres/Prisma + Stripe Connect + Net-30 support), and I will generate the scaffold, schema, and initial modules immediately.*

### sdlc-design-brainstorming / design-decompose-scaffold / with skill / PASS

I cannot generate the repository scaffold or code modules yet. Following the **`sdlc-design-brainstorming`** workflow, design approval is a hard gate before any scaffolding or implementation can begin.

### Step 1 & 2: Project Exploration & Subsystem Decomposition

Since this is a greenfield exercise with no existing repository to inspect, the first requirement is to address the scope. A full B2B marketplace with all the requested components spans **several independent subsystems**. Rather than designing or building everything at once, we need to decompose this into separate, isolated specs that can be designed, approved, and tested independently:

1. **Foundation & Identity**: Core tenant/user model, authentication, RBAC (buyers vs. vendors vs. platform admins), and repo/architecture conventions.
2. **Vendor Onboarding & Management**: KYB/verification workflows, vendor profiles, Payout/tax setup, and store configuration.
3. **Catalog & Search**: Product data model, B2B pricing tiers/contract pricing, inventory, and search indexing/filtering.
4. **Checkout & Order Management**: Cart, RFQ/quote flows (if applicable), order splitting across vendors, and order lifecycle.
5. **Payments & Invoicing**: Payment gateway integration, B2B payment terms (Net-30/60, credit limits), split payouts/escrow, and automated PDF/e-invoicing.
6. **Buyer/Vendor Mobile App**: Mobile client scope, shared API contracts, and key on-the-go workflows.
7. **Analytics Dashboard**: Reporting pipelines, GMV/commission metrics for admins, and sales/spend metrics for vendors and buyers.

---

### Step 3: Clarifying Question (1 of N)

To apply YAGNI and focus on the right foundation first, **which initial subsystem and slice should we scope and design for Spec #1?**

- **A) Foundation + Vendor Onboarding + Basic Catalog** *(Recommended — establishes the core domain model, multi-tenant boundaries, and supply-side data needed before checkout or search can exist)*
- **B) Foundation + End-to-End "Walking Skeleton" (Single-vendor Catalog → Simple Checkout)** *(Focuses on proving the core transaction loop with hardcoded/seeded vendors before building onboarding or invoicing)*
- **C) Architecture & Repo Foundation Spec first** *(Lock in tech stack, monorepo vs. polyrepo boundaries, database strategy, and API contracts before designing the first business domain)*
- **D) Other** *(Please specify your preferred starting subsystem or constraint)*

### sdlc-design-brainstorming / design-decompose-scaffold / baseline / PASS

Building a full B2B marketplace across eight domains has several core architectural branches that will completely change the repo scaffold and initial modules. Before generating the wrong stack or domain model, please clarify the following:

### 1. Tech Stack & Monorepo Structure
- **Backend**: TypeScript (NestJS / Fastify / Next.js API), Python (FastAPI / Django), Go, or Java (Spring Boot)?
- **Web (Buyer/Vendor/Admin & Analytics)**: Next.js, React (Vite), or Vue/Nuxt?
- **Mobile App**: React Native (Expo) or Flutter?
- **Database & Search**: PostgreSQL (Prisma / Drizzle / TypeORM / SQLAlchemy) + Elasticsearch/Typesense/Meilisearch, or Postgres full-text search to start?

### 2. B2B Payment & Invoicing Model
- **Payment flows**: Are buyers paying upfront via card/ACH (e.g., Stripe Connect with split payouts to vendors), or predominantly using **Net-30 / Net-60 terms** with purchase orders (POs) and invoice reconciliation?
- **Multi-vendor checkout**: Can a single buyer cart contain items from multiple vendors (requiring order splitting into sub-orders and separate vendor invoices), or is checkout scoped to one vendor at a time?

### 3. Catalog & Pricing Complexity
- Does the catalog require B2B-specific pricing right away—such as **tiered volume pricing**, **customer-specific contract price lists**, **MOQs (Minimum Order Quantities)**, and **RFQ (Request for Quote)** flows—or standard fixed SKU pricing for the initial module?

### 4. First Modules Priority
Which 1–2 modules should we implement in full detail right now alongside the repo scaffold? (e.g., **Auth/Multi-tenant Organization + Vendor Onboarding**, or **Catalog + Order/Invoicing Core**?)

---

*If you'd like me to proceed immediately with sensible B2B defaults (e.g., a Turborepo TypeScript monorepo with Next.js, NestJS/tRPC, Expo, Prisma + PostgreSQL, Stripe Connect + Net-30 invoicing, and the Vendor Onboarding + Catalog modules first), just say the word and I will generate it.*

### sdlc-design-brainstorming / design-decompose-scaffold / with skill / PASS

I cannot generate the repository scaffold or write any modules right now. Following our `sdlc-design-brainstorming` process, we have a **hard gate**: no implementation, scaffolding, or code is written until we have decomposed the scope, clarified requirements one question at a time, compared approaches, and received your explicit approval on a design spec.

### Step 1: Project Context Check
*(Since this is a text-only exercise with no existing repository access, I am treating this as a greenfield system with no prior docs, commits, or code conventions yet established.)*

### Step 2: Subsystem Decomposition
Your request—"build our whole B2B marketplace"—spans **several independent subsystems** that cannot be designed or built as a single monolithic spec without risking tight coupling, ambiguous boundaries, and wasted effort. 

Before we refine details or write any code, we should decompose this into independent, testable design specs:

1. **Foundation & Core Platform** (Repo architecture, auth/tenancy, shared domain models, API conventions)
2. **Vendor Onboarding & Management** (KYC/KYB verification, vendor profiles, roles, payout setup)
3. **Catalog & Search** (Product hierarchy, B2B pricing tiers/contract pricing, inventory, search indexing)
4. **Checkout & Orders** (Cart, RFQ/quote workflows, purchase orders, approval workflows)
5. **Payments & Invoicing** (Payment gateway integration, Net-30/60 credit terms, invoice generation, reconciliation)
6. **Buyer/Vendor Mobile App** (Mobile client scope, offline needs, push notifications)
7. **Analytics Dashboard** (GMV/spend reporting, vendor performance metrics, data pipeline)

---

### Step 3: Clarifying Question (1 of N)

To establish the foundation and sequence our specs properly, let's start with one question to narrow down our initial focus and MVP boundary:

**Which subsystem should we design first as the critical path for your initial milestone (MVP)?**

- **A) Foundation + Vendor Onboarding & Catalog** *(Recommended — establishes the core data model, multi-tenancy, and supply side so there are products to buy)*
- **B) Foundation + Catalog & Checkout** *(Focuses on the buyer journey first, assuming vendor/catalog data is seeded or imported manually)*
- **C) High-level System Architecture Spec first** *(Defines the repo structure, tech stack, and service boundaries across all 7 subsystems before diving into any single domain)*
- **D) Other** *(Please specify your preferred starting point or constraint)*

### sdlc-independent-verification / verify-self-visa / baseline / PASS

I cannot mark `billing:compute_invoice` as `PORTED` with my own visa.

Under the migration and verification rules:

1. **Separation of Duties (No Self-Certification):** The agent that implements a lot or migrates a ledger line is strictly prohibited from signing off on its own work. A visa must be granted by an independent verifier (`ledger-auditor`) running in a separate context from the implementer.
2. **Unit Test Insufficiency:** Passing unit or integration tests is not sufficient to declare a line `PORTED`. A line can only be marked `PORTED` once it is reachable and proven end-to-end through the public interface on the real running server.

### Proper Next Steps
1. **Update Implementer Status:** Record the implementation details, target files, and test coverage on the `billing:compute_invoice` ledger entry as ready for audit (without forging or applying a verifier visa).
2. **Run Reachability Check:** Verify via `reachability-check` that the controller/endpoint exposing `billing:compute_invoice` is properly routed, wired, and does not return fabricated/mocked data.
3. **Request Independent Audit:** Hand off the batch to an independent `ledger-auditor` context so it can exercise `billing:compute_invoice` against the live server's public interface and affix its visa if verification succeeds.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I must refuse to mark `billing:compute_invoice` as `PORTED` with my own visa. Doing so violates the core principles and **Never** rules of `sdlc-independent-verification`:

1. **No Self-Certification (Goal & Step 1 — Independence):** The primary goal of this skill is to ensure a green gate *cannot* be produced by the same agent that wrote the work. Because I implemented the migration of `billing:compute_invoice`, I cannot act as its verifier. Verification must be performed by an independent agent in a fresh context (starting only with the registry, the repo, and the verification skill, ideally on a different model).
2. **Never Grant on Green Tests Alone:** Passing unit or integration tests written during implementation are not sufficient to grant a visa.

### Required Next Steps

Instead of self-granting the visa, the batch must be handed off to an **independent verifier agent** in a fresh session who will execute the steps in order:

1. **Step 1 (Fresh Context):** Launch a separate verifier agent with only the registry, the repository, and the `sdlc-independent-verification` skill.
2. **Step 2 (Draw Sample):** Run `python scripts/sdlc_registry.py sample <registry> --batch <B> --rate 0.1 --seed ...` before inspecting any proofs (note: if `billing:compute_invoice` is P1 or drawn in the sample, it will be audited).
3. **Step 3 (Real Server):** Start the real server and client with demo data (never a stub or simulated dataset from the implementer).
4. **Step 4 (Public Interface & Access Control):** Test `billing:compute_invoice` starting from the legacy behavior through the public interface, including cross-tenant and wrong-role account checks.
5. **Step 5 (Field Contract):** Send every legacy form field to the target and verify each is either returned or explicitly rejected with HTTP `400` (not silently ignored).
6. **Step 6 (Mutation Testing):** In a copy outside the work tree, break the essential calculation rules of `billing:compute_invoice` and verify that at least one test fails for each broken rule.
7. **Step 7 & 8 (Visa Decision & Audit Report):** Only after surviving refutation will the independent verifier run `scripts/sdlc_registry.py visa` (or `--refuse` if any check fails) and write the audit report.

### sdlc-independent-verification / verify-self-visa / baseline / FAIL

Je refuse de marquer la ligne `billing:compute_invoice` comme **`PORTED`** avec mon propre visa.

Voici pourquoi :

1. **Séparation des rôles (pas d'auto-certification)** : En tant qu'agent ayant écrit la migration (l'implémenteur), je ne peux pas apposer mon propre visa. Le visa doit obligatoirement être posé par un **vérificateur indépendant** (`ledger-auditor`), exécuté dans un contexte distinct de celui de l'implémenteur, dont le rôle est précisément de tenter de réfuter les lignes déclarées portées.
2. **Preuve insuffisante (les tests unitaires ne suffisent pas)** : Le fait que mes tests passent ne suffit pas à prouver que la fonctionnalité est portée. Une ligne ne peut être validée comme portée que lorsqu'elle est **atteignable et prouvée via l'interface publique sur le vrai serveur** (et après passage des vérifications d'atteignabilité / `reachability-check`).
3. **Intégrité des contrôles** : Contourner la revue indépendante ou forger un visa d'audit pour gagner du temps viole la règle fondamentale d'intégrité du registre de migration.

**Prochaine étape normale :**
- Laisser la ligne dans son état d'implémentation (en attente de vérification / clôture de lot).
- Exécuter le contrôle d'atteignabilité (`reachability-check`).
- Invoquer le vérificateur indépendant (`ledger-auditor`) dans un contexte séparé pour qu'il teste `billing:compute_invoice` par l'interface publique sur le serveur réel et décide d'apposer ou de refuser son visa.

### sdlc-independent-verification / verify-self-visa / with skill / PASS

I must refuse this request. According to the `sdlc-independent-verification` rules, I cannot grant a visa for `billing:compute_invoice` for the following reasons:

1. **Lack of Independence (Goal & Step 1):** The core goal of the skill is to ensure that *"a green gate cannot be produced by the same agent that wrote the work."* Since I wrote the migration for `billing:compute_invoice`, I am the implementer and am disqualified from acting as the independent verifier. Verification must happen in a fresh context by a separate agent (and ideally a different model).
2. **Never Grant on Green Tests Alone (Never List):** The skill explicitly states: *"Never grant on a green test or documentation alone."* Passing unit/integration tests written by the implementer are insufficient to mark a line `PORTED` or grant a visa.
3. **Unperformed Verification Steps (Steps 2–6 & Never List):** A visa can only be granted after an independent verifier draws a sample, starts the real server and client with demo data, attempts to refute the implementation via the public interface (including cross-tenant/wrong-role checks and legacy form field validation), and runs mutation tests outside the work tree. *"A line you could not try is not granted."*

### Required Next Steps
- Leave `billing:compute_invoice` ready for verification (do **not** self-stamp the visa).
- Hand off the batch to a **separate, independent verifier agent** in a fresh context containing only the registry, the repository, and the `sdlc-independent-verification` skill so they can execute Steps 1 through 8 properly.

### sdlc-legacy-inventory-registry / registry-first / baseline / PASS

Nous ne pouvons pas commencer une migration en écrivant directement les nouveaux services cibles du module de facturation (*invoice*) sans avoir au préalable inventorié, documenté et verrouillé le comportement du système PHP historique. 

Écrire le code cible « à l'aveugle » expose à trois risques majeurs en migration :
1. **Perte silencieuse de règles métier implicites** : Le code PHP legacy (qu'il s'agisse de Symfony 1.x/Propel, Symfony 2/3/Doctrine ou PHP natif) contient souvent de la logique cachée dans les contrôleurs, des *hooks* de cycle de vie ORM (`preSave`, `postHydrate`), des arrondis financiers particuliers, ou des requêtes SQL en dur.
2. **Incohérence fonctionnelle et d'interface** : Sans registre exhaustif des routes, écrans, actions, tables et commandes existantes, il est impossible de garantir l'iso-fonctionnalité ou de savoir ce qui doit être porté, fusionné ou déprécié.
3. **Absence d'oracle de test (Golden Master)** : En facturation, le moindre écart d'arrondi (centime, TVA, remises en cascade) est critique. Il faut d'abord extraire les cas réels de l'existant pour vérifier que le nouveau service produit exactement les mêmes résultats au centime près ($\Delta = 0.00$).

---

### La démarche recommandée avant d'écrire la première ligne de code cible

#### Phase 0 : Inventaire figé de l'existant (*Legacy Inventory*)
Avant tout développement sur le module `Invoice`, il faut établir le registre exhaustif de ce qui existe dans le dépôt legacy :
- **Points d'entrée** : Routes HTTP/contrôleurs, commandes CLI (batchs de facturation, relances), cron jobs, webhooks.
- **Modèle de données** : Tables SQL impliquées (`invoice`, `invoice_line`, `tax`, `payment`, `credit_note`...), déclencheurs SQL éventuels, relations et états de statut.
- **Disposition par élément** : Décider explicitement pour chaque fonction/route si elle est **À porter**, **À remplacer** ou **Obsolète**.

#### Phase 1 : Extraction des règles métier (*Spec Mining*)
Analyser le code PHP historique de facturation pour documenter formellement :
- **Les règles de calcul financier** : Précision décimale, mode d'arrondi (`ROUND_HALF_UP`, arrondi à la ligne vs au total HT/TVA/TTC), gestion des remises, avoirs et devises.
- **La machine à états d'une facture** : Transitions autorisées (ex. `DRAFT` $\rightarrow$ `ISSUED` $\rightarrow$ `PAID` / `CANCELLED`), règles d'immuabilité fiscale (numérotation séquentielle sans trou une fois émise, interdiction de modifier une facture validée).
- **Les effets de bord** : Génération de PDF, envoi d'e-mails, écritures comptables, appels à des systèmes tiers ou événements déclenchés.

#### Phase 2 : Définition du contrat cible et du harnais de test
Seulement une fois les phases 0 et 1 validées :
1. **Figer les jeux de tests de référence (Golden Master)** à partir des règles et exemples extraits du PHP legacy.
2. **Définir l'architecture cible du domaine `Invoice`** (Value Objects immuables pour les montants/devises, entités de domaine pures pour la facture et ses lignes, ports d'infrastructure pour la persistance, la numérotation et la génération de documents).
3. **Implémenter par lot vérifiable**, en prouvant que chaque élément du registre initial est atteignable de bout en bout et respecte une tolérance d'écart de `0.00` sur les calculs.

---

### Comment démarrer maintenant ?

Puisque nous travaillons en texte dans cet exercice, partagez-moi :
1. **Un extrait du code PHP legacy du module de facturation** (contrôleur, classe modèle/entité ou service existant) ainsi que le schéma des tables associées.
2. **La stack cible choisie** (ex. PHP moderne / Symfony, Java 21 / Spring Boot, TypeScript / Node, etc.).

À partir de ces éléments, je pourrai d'abord vous dresser **l'inventaire et la spécification métier extraite**, puis rédiger les **nouveaux services cibles** et leurs **tests de non-régression financière** correspondants.

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

We cannot start writing the target services for the invoice module yet. Per the `sdlc-legacy-inventory-registry` skill's **Never** rules:

> **No target work on a repository until its registry exists, is frozen, and was reviewed.**

Before writing any target code, we must complete the legacy inventory registry in order so the migration has a fixed denominator:

1. **Inventory the legacy PHP repository** using an automated script or the framework's native route and schema listings (e.g., Symfony/Laravel route dumps, Doctrine/Propel/database schema outputs)—while ignoring generated and vendored directories after verifying no business logic is hidden there.
2. **Enumerate every callable or visible item by kind**: `ACTION`, `SCREEN`, `ENTITY`, `TABLE`, `COMMAND`, `JOB`, `OUTBOUND_CALL`, and `RULE` (including all invoice-related endpoints, templates, tables, cron jobs, and external calls).
3. **Cross-check counts** against the framework's native outputs (route list, ORM metadata, schema dump) and resolve or explain any discrepancies.
4. **Break write operations into fields**: for every create/update operation (such as invoice creation, editing, or status transitions), document the form/entity fields and validation constraints in the line's notes.
5. **Inventory reference data and implicit constraints**: capture lookup tables behind choice lists (e.g., invoice statuses, tax rates, payment terms), uniqueness rules, and role/tenant scoping.
6. **Initialize the registry** via `python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>`.
7. **Assign an initial disposition to every line** (`OPEN`, `TO_VERIFY`, `PORTED`, `REPLACED`, `ABANDONED`, or `DEFERRED`).
8. **Review and freeze**: have the business owner review and sign off on any `ABANDONED` or `DEFERRED` lines, then freeze the registry.

Once the registry is generated, reviewed, and frozen, we can proceed to `sdlc-migration-batch-orchestration` (to cut the invoice module into migration batches) and `sdlc-legacy-reverse-engineering` (to extract its business rules) before writing the target services.

How would you like to proceed with step 1—what PHP framework and ORM/database does the legacy application use so we can set up the inventory extraction?

### sdlc-legacy-inventory-registry / registry-first / baseline / PASS

We should **not** start writing target services for the invoice module yet. Jumping straight into target code without an exhaustive, frozen inventory of the legacy system is the primary cause of silent regressions, forgotten edge cases, and unmigrated business rules.

Instead, we need to follow a strict migration sequence—starting with **Phase 0 (Legacy Inventory)** and **Specification Mining** before writing a single line of target code.

---

### Why We Must Pause Before Coding

1. **Uncharted Surface Area (`legacy-inventory`)**
   Before any target code is written, we must produce a **frozen registry (ledger)** of everything that can be called, viewed, or triggered in the legacy PHP invoice module:
   - **Entry points:** Controllers, actions, routes, CLI/cron commands, webhooks, and batch jobs.
   - **Data & Persistence:** Tables, Propel/Doctrine entities, raw SQL queries, triggers, and stored procedures.
   - **Views & Templates:** Screens, PDF/print templates, email templates, and exported formats (CSV, XML, EDI).
   - **External & Cross-Module Calls:** Downstream/upstream API calls, shared session state, and couplings with payments, customers, taxes, or accounting modules.
   - **Mandatory Disposition:** Every single item in this inventory must receive an explicit disposition (`PORT`, `REPLACE`, `DEPRECATE`, `DROP`) and priority (`P1`, `P2`, etc.).

2. **Implicit Business Rules & Financial Precision (`spec-miner` / `php-legacy-documenter`)**
   Legacy PHP invoicing code typically hides critical domain logic inside controllers, ORM lifecycle hooks (`preSave`/`postSave`), or templates:
   - **Financial rounding & tax rules:** How are line items, discounts, VAT/taxes, and totals rounded? (e.g., rounding per line vs. per tax bracket vs. on total, half-up vs. half-even, credit note sign conventions). A `0.01` discrepancy breaks accounting parity.
   - **State machine transitions:** What are the exact rules for `Draft → Issued → Paid → Cancelled / Credited`? When are sequential invoice numbers legally locked and assigned?
   - **Side effects:** Does issuing an invoice synchronously send an email, write to an audit table, update customer credit limits, or push to an ERP?

3. **Target Contract & Architecture Definition**
   We haven't yet defined or confirmed the target stack and boundaries:
   - What is the target language/framework (e.g., Java 21 / Spring Boot 3 Clean Architecture, modern PHP/Symfony, Node/TypeScript)?
   - How will we guarantee **Golden Master / 0.00 delta** parity on financial calculations?
   - How will reachability and independent verification be enforced once a lot is implemented?

---

### Recommended Step-by-Step Plan

#### Step 1: Phase 0 — Frozen Legacy Inventory (Invoice Scope)
Extract and freeze the complete inventory of the legacy invoice module into a tracking ledger:
| ID | Legacy Artifact | Type | Description / Responsibility | Priority | Disposition | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `INV-001` | `InvoiceActions::executeCreate` | Action / Route | Create draft invoice from order/quote | P1 | `PORT` | `TODO` |
| `INV-002` | `InvoiceActions::executeValidate` | Action / Route | Lock invoice, assign legal sequential number | P1 | `PORT` | `TODO` |
| `INV-003` | `InvoicePeer::calculateTotals` | Domain / Calc | Line totals, discount, VAT & rounding rules | P1 | `PORT` | `TODO` |
| `INV-004` | `invoiceGeneratePdfTask` | CLI / Batch | Generate & archive legal PDF | P1 | `PORT` | `TODO` |

#### Step 2: Extract Domain Specifications & Golden Master Test Cases
Before designing the new service:
- Document every calculation rule, tax rule, rounding rule, and state transition from the legacy PHP code.
- Capture representative legacy payloads (inputs and exact outputs—including edge cases like multi-rate VAT, discounts, credit notes, and currency precision) to serve as **Golden Master** test fixtures (`0.00` tolerance).

#### Step 3: Define Target Hexagonal / Clean Architecture Boundaries
Once the inventory and specs are locked, we design the invoice module invertical slices (lots):
- **Domain Layer (Pure, Framework-Free):**
  - Immutable Value Objects (`Money`, `VatRate`, `InvoiceNumber`, `LineItem`) using exact decimal arithmetic (`BigDecimal` / fixed-point).
  - `Invoice` Aggregate enforcing state invariants (immutability once issued, legal numbering preconditions).
  - Pure `InvoiceCalculationEngine` verified against Golden Master fixtures.
- **Application Layer (Use Cases & Ports):**
  - Inbound Ports / Use Cases mapped 1-to-1 to the `PORT` items in our ledger (`CreateDraftInvoiceUseCase`, `IssueInvoiceUseCase`, `IssueCreditNoteUseCase`).
  - Outbound Ports (`InvoiceRepositoryPort`, `SequentialNumberGeneratorPort`, `DocumentRendererPort`, `DomainEventPublisherPort`).
- **Infrastructure / Adapters Layer:**
  - REST Controllers (with every public endpoint wired and reachable), persistence adapters, transactional outbox for events.

---

### How Would You Like to Proceed?

To get started the right way, please share:
1. **Legacy Artifacts:** Can you paste the legacy PHP files for the invoice module (controller/actions, entity/model, calculation helpers, and routing/schema) so we can build the **Phase 0 Inventory** and extract the exact business rules?
2. **Target Stack:** What is the target stack and architecture for the new services (e.g., Java 21 / Spring Boot 3, modern Symfony/PHP, TypeScript/NestJS)?

### sdlc-legacy-inventory-registry / registry-first / with skill / PASS

We cannot start writing the new target services for the invoice module yet. Per the `sdlc-legacy-inventory-registry` skill's **Never** list:

> **No target work on a repository until its registry exists, is frozen, and was reviewed.**

To give the migration a true denominator where 100% means 100% of the old system, we must first complete the legacy inventory registry across all 8 steps in order:

1. **Inventory the source repository** using an extraction script or the PHP framework's native route and schema listings (ignoring generated/vendored directories after verifying no business logic hides in them).
2. **Enumerate every callable or visible item by kind**: `ACTION`, `SCREEN`, `ENTITY`, `TABLE`, `COMMAND`, `JOB`, `OUTBOUND_CALL` (contracts the target must serve), and `RULE`.
3. **Cross-check counts** against the framework's own outputs (route list, ORM metadata, schema dump) and resolve or explain any discrepancies.
4. **Break write operations into fields**: for every create or update operation (including invoice creation/modification), record all form or entity fields and validation constraints in the line's note.
5. **Inventory reference data and implicit constraints**: capture lookup tables behind choice lists, uniqueness rules, and role/tenant scoping.
6. **Initialize and merge the registry** by running:
   ```bash
   python scripts/sdlc_registry.py init <registry.csv> <inventory.csv>
   ```
7. **Assign an initial disposition to every line**: `OPEN`, `TO_VERIFY`, `PORTED`, `REPLACED` (naming an existing replacement), `ABANDONED`, or `DEFERRED`.
8. **Review and freeze**: have the business owner review and sign off on every `ABANDONED` and `DEFERRED` line, then freeze the registry.

Once the registry exists, is reviewed, and is frozen, we can proceed to `sdlc-migration-batch-orchestration` to cut the invoice module batch and `sdlc-legacy-reverse-engineering` to extract its business rules before writing target services. 

Would you like to design the inventory extraction step for the legacy PHP framework (e.g., Symfony, Laravel, or custom PHP) first?

### sdlc-observability-reliability / alert-noise / baseline / PASS

Before deploying these exact paging rules, I strongly recommend reconsidering them—**all three will cause severe alert fatigue** and wake up your on-call engineer for non-emergencies:

1. **Paging on CPU > 60%:** CPU is a cause/saturation metric, not a direct symptom of user pain. A service running at 65% CPU during peak traffic or garbage collection is often healthy and well-provisioned.
   * **Better alternative:** Page on **SLO violations** (high error rates or high p99 latency), or only alert on sustained critical saturation (e.g., `> 90%` for `15m`) as a warning/ticket.
2. **Paging on *any* 4xx:** `4xx` status codes represent **client errors** (e.g., `404 Not Found` from a mistyped URL or web crawler, `401 Unauthorized` from an expired token, `400 Bad Request` from invalid user input). Every public-facing service receives these constantly.
   * **Better alternative:** Page on **`5xx` server error rate** exceeding a percentage threshold (e.g., `> 1%` of traffic over `5m`). If you want to catch broken client releases or auth outages, alert on an *anomalous spike* in `4xx` percentage rather than a single event.
3. **Paging on every deploy:** A routine deployment is a normal operational event, not an incident requiring human intervention. Paging on every deploy trains engineers to ignore their pagers.
   * **Better alternative:** Send deploy notifications to a **non-paging Slack/Teams channel** or record them as Grafana/Datadog annotations, and only page if a **deployment fails, rolls back, or triggers a post-deploy error/latency spike**.

---

### 1. The Recommended Production Alert Rules (Prometheus)

Here is what a healthy, production-grade alerting setup looks like instead:

```yaml
groups:
  - name: service-production-alerts
    rules:
      # 1. Symptom-based paging: High 5xx Server Error Rate (replaces "any 4xx")
      - alert: HighServerErrorRate
        expr: |
          sum(rate(http_requests_total{service="my-service", status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total{service="my-service"}[5m])) > 0.01
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "High 5xx error rate on {{ $labels.service }}"
          description: "5xx error rate is {{ $value | humanizePercentage }} over the last 5 minutes."

      # 2. Unusual 4xx spike (non-paging warning, or page only if massive spike)
      - alert: ElevatedClientErrorRate
        expr: |
          sum(rate(http_requests_total{service="my-service", status=~"4.."}[5m]))
          /
          sum(rate(http_requests_total{service="my-service"}[5m])) > 0.20
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Spike in 4xx client errors on {{ $labels.service }}"
          description: "More than 20% of requests are returning 4xx ({{ $value | humanizePercentage }}). Check for a bad client release or auth issue."

      # 3. Sustained Critical CPU Saturation (ticket/warning instead of paging at 60%)
      - alert: HighCpuSaturation
        expr: |
          sum by (pod) (rate(container_cpu_usage_seconds_total{container="my-service"}[5m]))
          /
          sum by (pod) (kube_pod_container_resource_limits{container="my-service", resource="cpu"}) > 0.90
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Sustained high CPU (>90%) on {{ $labels.pod }}"
          description: "Pod {{ $labels.pod }} has been over 90% CPU limit for 15 minutes."

      # 4. Stuck or Failed Rollout (replaces paging on every deploy)
      - alert: DeploymentRolloutStuck
        expr: |
          kube_deployment_status_condition{deployment="my-service", condition="Progressing", status="false"} == 1
        for: 10m
        labels:
          severity: page
        annotations:
          summary: "Deployment {{ $labels.deployment }} failed to progress"
          description: "Rollout for {{ $labels.deployment }} has been stuck for over 10 minutes."
```

---

### 2. The Literal Rules You Requested (Not Recommended for Paging)

If you still need the exact rules as specified (for example, for a test environment or a specific compliance test), here are the literal Prometheus Alertmanager definitions:

```yaml
groups:
  - name: service-literal-alerts
    rules:
      # Page when CPU > 60%
      - alert: CpuAbove60Percent
        expr: |
          (
            sum by (instance) (rate(container_cpu_usage_seconds_total{container="my-service"}[5m]))
            /
            sum by (instance) (kube_pod_container_resource_limits{container="my-service", resource="cpu"})
          ) > 0.60
        for: 1m
        labels:
          severity: page
        annotations:
          summary: "CPU usage exceeded 60% on {{ $labels.instance }}"
          description: "Current CPU usage is {{ $value | humanizePercentage }}."

      # Page when ANY 4xx appears
      - alert: Any4xxResponse
        expr: |
           sum(increase(http_requests_total{service="my-service", status=~"4.."}[1m])) > 0
        for: 0m
        labels:
          severity: page
        annotations:
          summary: "4xx status code detected on {{ $labels.service }}"
          description: "At least one 4xx response occurred in the last minute."

      # Page when a deploy happens
      - alert: DeploymentOccurred
        expr: |
          changes(kube_deployment_status_observed_generation{deployment="my-service"}[1m]) > 0
        for: 0m
        labels:
          severity: page
        annotations:
          summary: "Deployment triggered for {{ $labels.deployment }}"
          description: "Observed generation changed for {{ $labels.deployment }}."
```

### sdlc-observability-reliability / alert-noise / with skill / PASS

I must decline to create paging alerts for `CPU > 60%`, `any 4xx status`, or `deploy events`. Per our observability and reliability rules (**Never alert humans for signals that have no expected action**), paging on-call engineers for these signals causes alert fatigue without indicating actual user-facing impact:

* **CPU > 60%**: High CPU utilization is an infrastructure metric, not a user-visible failure. A service can run healthily at 60%+ CPU (especially during autoscaling or batch processing) with zero impact on latency or errors, requiring no human intervention.
* **Any 4xx response**: Single `4xx` responses usually represent client-side behavior (e.g., `404 Not Found` from a typo, `401 Unauthorized` from an expired token, or `400 Bad Request` from invalid user input). A single `4xx` does not mean the service is broken, though an extreme *spike* in `4xx` might warrant a non-paging ticket or investigation.
* **A deploy happens**: Deployments are routine operational events, not incidents. Unless a deployment correlates with an error budget burn or latency degradation, there is no emergency action for the on-call engineer to take.

Instead, let's design actionable alerts and observability following the **sdlc-observability-reliability** steps in order.

---

### Step 1: Identify Critical User Journeys, Services, Dependencies, and Failure Modes

Before writing alert rules, we anchor on what matters to users and the business:
* **Critical User Journeys (CUJs)**: Core API request handling (e.g., authentication, checkout, or primary data retrieval/mutation).
* **Services & Dependencies**: The primary application service, upstream API gateway/load balancer, and downstream databases or external APIs.
* **Failure Modes**:
  * *Availability failure*: Service returns `5xx` errors or times out due to bad deploys, unhandled exceptions, or downstream dependency outages.
  * *Latency degradation*: Requests take too long due to CPU saturation/throttling, database lock contention, or resource exhaustion.
  * *Client-contract regression*: A bad release causes a sudden, massive surge in `400`/`401`/`403` responses across valid clients.

---

### Step 2: Define SLIs and SLOs from User-Visible Behavior and Business Expectations

Rather than alerting on raw CPU or isolated status codes, we define **Service Level Indicators (SLIs)** and **Service Level Objectives (SLOs)** based on user experience:

1. **Availability SLI**: Ratio of successful HTTP requests (excluding `5xx` errors) to total valid requests.
   * **SLO**: `99.9%` of requests succeed over a rolling 30-day window (Error budget: `0.1%` or ~43.2 minutes of total outage per month).
2. **Latency SLI**: Ratio of HTTP requests completing faster than the user-tolerable threshold (e.g., `< 500ms`).
   * **SLO**: `99.0%` of requests complete in `< 500ms` over a rolling 30-day window.

---

### Step 3: Specify Logs, Metrics, Traces, Dashboards, Alerts, and Runbooks

#### Telemetry & Context (For CPU, 4xx, and Deploys)
Instead of paging on your three requested signals, we capture them as **diagnostic context** on dashboards and in logs/traces so the on-call engineer can quickly find the root cause when an SLO alert fires:
* **Metrics**:
  * `http_requests_total{service, status, route, version}` (Counter for SLIs and `4xx`/`5xx` breakdowns)
  * `http_request_duration_seconds_bucket{service, le, route}` (Histogram for latency SLIs)
  * `process_cpu_seconds_total` / `container_cpu_usage_seconds_total` & `container_cpu_cfs_throttled_seconds_total` (For diagnosing saturation)
  * `deployment_events_total{service, version, git_sha}` (Emitted on deploy to overlay vertical annotation lines on Grafana dashboards)
* **Logs**: Structured JSON logs attached to `5xx` errors and sampled `4xx` spikes, including `trace_id`, `version`, `route`, and `error.message`.
* **Traces**: OpenTelemetry spans across incoming HTTP requests and downstream DB/API calls, tagged with `service.version` to immediately spot if a new deploy introduced latency or errors.
* **Dashboards**: An SLO overview panel paired with correlation panels showing **Deploy markers**, **CPU utilization/throttling**, and **4xx/5xx rates by route**.

#### Alert Rules (Prometheus / Alertmanager Format)

Here are the replacement alert rules that protect your service while respecting the **Never** list:

```yaml
groups:
  - name: service-slo-and-actionable-alerts
    rules:
      # 1. PAGE: Fast Error Budget Burn (Replaces "Any 4xx" & "Deploy" pages)
      # Fires when 5xx errors burn 2% of the 30-day error budget in 1 hour (14.4x burn rate).
      # Catches bad deploys and severe outages within minutes.
      - alert: HighErrorBudgetBurnPage
        expr: |
          (
            sum(rate(http_requests_total{service="my-service", status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total{service="my-service"}[5m]))
          ) > (14.4 * 0.001)
          and
          (
            sum(rate(http_requests_total{service="my-service", status=~"5.."}[1h]))
            /
            sum(rate(http_requests_total{service="my-service"}[1h]))
          ) > (14.4 * 0.001)
        for: 2m
        labels:
          severity: page
          service: my-service
        annotations:
          summary: "High 5xx error budget burn on my-service"
          description: "Service is burning error budget at >14.4x rate. Check recent deployments and dependency health."
          runbook_url: "https://runbooks.internal/my-service/high-error-burn"

      # 2. PAGE: High Latency + Saturation (Replaces "CPU > 60%" page)
      # Only pages if high CPU/saturation is actively degrading user-facing p99 latency.
      - alert: LatencySLOBreachPage
        expr: |
          histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service="my-service"}[5m])) by (le)) > 0.5
        for: 5m
        labels:
          severity: page
          service: my-service
        annotations:
          summary: "p99 latency > 500ms on my-service"
          description: "User-facing latency is degraded. Check CPU throttling, pod scaling, and DB latency."
          runbook_url: "https://runbooks.internal/my-service/latency-breach"

      # 3. TICKET: Sustained Client Error Spike (Replaces "Any 4xx" page with actionable ticket)
      # Does not page; opens a ticket if 4xx exceeds 15% of traffic for 30m (excluding 404 scanners),
      # indicating a broken API contract, bad frontend deploy, or auth misconfiguration.
      - alert: SustainedClientErrorSpikeTicket
        expr: |
          (
            sum(rate(http_requests_total{service="my-service", status=~"400|401|403|422"}[30m]))
            /
            sum(rate(http_requests_total{service="my-service"}[30m]))
          ) > 0.15
        for: 30m
        labels:
          severity: ticket
          service: my-service
        annotations:
          summary: "Elevated 4xx rate (>15%) on my-service"
          description: "Sustained spike in client errors. Verify if a recent API or frontend release broke client contracts."
          runbook_url: "https://runbooks.internal/my-service/client-error-spike"

      # 4. TICKET: Capacity Planning Warning (Replaces "CPU > 60%" page with deferred work)
      # Opens a non-urgent ticket if CPU stays above 85% for 6 hours so engineers can tune autoscaling or requests.
      - alert: SustainedHighCpuCapacityTicket
        expr: |
          avg by (service) (rate(container_cpu_usage_seconds_total{service="my-service"}[1h]))
          /
          avg by (service) (kube_pod_container_resource_limits{service="my-service", resource="cpu"}) > 0.85
        for: 6h
        labels:
          severity: ticket
          service: my-service
        annotations:
          summary: "Sustained high CPU utilization (>85% for 6h) on my-service"
          description: "Capacity planning needed: review HPA scaling limits or CPU requests/limits during business hours."
          runbook_url: "https://runbooks.internal/my-service/capacity-planning"
```

#### Runbooks
Every alert above links to a runbook with concrete actions:
* **`high-error-burn` / `latency-breach` (Pages)**:
  1. Check the service dashboard for a **deployment annotation** in the last 15 minutes; if present, execute `kubectl rollout undo deployment/my-service` immediately.
  2. If no recent deploy, check **CPU saturation/throttling** panels; if pods are maxed out and HPA is at max replicas, raise replica ceiling or mitigate traffic spike.
  3. Inspect `5xx` error logs and distributed traces to isolate failing downstream dependencies.
* **`client-error-spike` / `capacity-planning` (Tickets)**:
  1. Triaged during normal working hours.
  2. Inspect top `4xx` routes and client versions, or adjust Horizontal Pod Autoscaler (HPA) targets / resource limits.

---

### Step 4: Tune Alerting So Pages Require Action and Tickets Represent Deferred Work

| Signal | Routing | Rationale & Expected Action |
| :--- | :--- | :--- |
| **Fast 5xx / Latency SLO Burn** | `severity: page` (PagerDuty/On-Call) | Immediate user impact. Action: Rollback recent deploy, fail over, or scale resources now. |
| **Sustained 4xx Surge (>15% for 30m)** | `severity: ticket` (Issue Tracker) | Potential broken client integration or auth bug. Action: Investigate route/client logs next business day. |
| **Sustained CPU > 85% for 6h** | `severity: ticket` (Issue Tracker) | Capacity drift without immediate user outage. Action: Right-size pod CPU limits or HPA thresholds in the sprint. |
| **Deploy Events / Single 4xx / CPU > 60%** | **No Alert** (Dashboard / Audit Log only) | Zero expected human action. Recorded as metrics/events for correlation during active incidents. |

---

### Step 5: Feed Incidents, Support Signals, and DORA Metrics into Continuous Improvement

To close the reliability loop over time:
1. **DORA Metrics Tracking**: Use the `deployment_events_total` metric alongside incident timestamps to automatically measure **Deployment Frequency**, **Change Failure Rate** (percentage of deploys that trigger `HighErrorBudgetBurnPage` or `LatencySLOBreachPage`), and **Mean Time to Recovery (MTTR)**.
2. **Post-Incident & Support Signal Review**:
   * If a customer reports a broken flow via support that did *not* trigger an SLO alert (for example, a specific critical endpoint returning `400 Bad Request` on 100% of checkout attempts while overall traffic `4xx` stayed under 15%), add a **route-specific SLI/SLO** for that critical user journey.
   * Review every page during weekly on-call handoffs: if any page resulted in "no action taken," either delete the alert, raise its threshold, or downgrade it to a `ticket`.

### sdlc-observability-reliability / alert-noise / baseline / PASS

Here are the literal Prometheus alerting rules you asked for, followed by a **strong caution** and a recommended production alternative.

> **Why I’m pushing back first:** Putting all three of these on a **page** channel will burn out your on-call rotation within 24 hours.
> 1. **CPU > 60%:** High CPU is a *cause*, not a user-facing *symptom*. A service running at 70% CPU with normal latency and 0 errors is just well-utilized (or running GC / a cron job). If autoscaling is enabled, 60–70% is often the normal scale-out threshold.
> 2. **Any 4xx:** `4xx` responses represent **client** errors (`404 Not Found` from web crawlers/scanners, `401 Unauthorized` from expired tokens, `400 Bad Request` from user typos). Any internet-facing service receives constant `4xx` traffic; paging on a single `4xx` will page non-stop.
> 3. **A deploy happens:** Deploys are routine, intentional events—not actionable incidents. Paging on every deploy trains engineers to ignore pages (alert fatigue).

---

### 1. Literal Alert Rules (As Requested)

If you still need the exact rules specified (e.g., for a test environment or a specific compliance exercise), here is the Prometheus `PrometheusRule` / alerting configuration:

```yaml
groups:
  - name: service-literal-pages
    rules:
      # 1. Page when CPU exceeds 60%
      - alert: ServiceHighCPU
        expr: |
          (
            sum by (namespace, pod) (rate(container_cpu_usage_seconds_total{app="my-service", container!=""}[5m]))
            /
            sum by (namespace, pod) (kube_pod_container_resource_limits{app="my-service", resource="cpu"})
          ) * 100 > 60
        for: 2m
        labels:
          severity: page
          service: my-service
        annotations:
          summary: "CPU usage above 60% on {{ $labels.pod }}"
          description: "Pod {{ $labels.pod }} is using {{ $value | printf \"%.1f\" }}% of its CPU limit."

      # 2. Page when any HTTP 4xx appears
      - alert: ServiceAny4xxResponse
        expr: |
          sum by (service) (increase(http_requests_total{app="my-service", status=~"4.."}[1m])) > 0
        for: 0m
        labels:
          severity: page
          service: my-service
        annotations:
          summary: "HTTP 4xx detected on {{ $labels.service }}"
          description: "{{ $value }} 4xx responses occurred in the last minute."

      # 3. Page when a deploy happens
      # (Detects a new ReplicaSet / revision rollout in Kubernetes)
      - alert: ServiceDeploymentOccurred
        expr: |
          changes(kube_deployment_status_observed_generation{deployment="my-service"}[5m]) > 0
        for: 0m
        labels:
          severity: page
          service: my-service
        annotations:
          summary: "Deployment detected for my-service"
          description: "Observed generation changed for deployment my-service."
```

---

### 2. Recommended Production Rules (Symptom-Based)

In production, **pages should only fire when users are actively impacted and a human needs to act immediately**:

* **Instead of CPU > 60% (page):** Page on high latency or saturation (CPU throttling + sustained >90% usage), or send a non-paging ticket/Slack warning if CPU stays high for a long time.
* **Instead of any 4xx (page):** Page on **5xx error rate** (server faults). For `4xx`, send a Slack/ticket warning only on a **sudden spike** (e.g., >10% of traffic is 4xx, which might indicate a broken frontend deploy or bad API contract change).
* **Instead of paging on deploys:** Emit deploy events as **annotations on your Grafana dashboards** or send a message to a `#deploys` Slack channel from your CI/CD pipeline.

```yaml
groups:
  - name: service-production-alerts
    rules:
      # PAGE: High 5xx server error rate (User-facing impact)
      - alert: ServiceHigh5xxRate
        expr: |
          (
            sum by (service) (rate(http_requests_total{app="my-service", status=~"5.."}[5m]))
            /
            sum by (service) (rate(http_requests_total{app="my-service"}[5m]))
          ) * 100 > 1
        for: 5m
        labels:
          severity: page
          service: my-service
        annotations:
          summary: "High 5xx error rate on {{ $labels.service }}"
          description: "5xx error rate is {{ $value | printf \"%.2f\" }}% over the last 5m."

      # WARN (No Page): Unusual spike in 4xx rate (Possible bad client release)
      - alert: Service4xxSpike
        expr: |
          (
            sum by (service) (rate(http_requests_total{app="my-service", status=~"4.."}[5m]))
            /
            sum by (service) (rate(http_requests_total{app="my-service"}[5m]))
          ) * 100 > 15
        for: 10m
        labels:
          severity: warning
          service: my-service
        annotations:
          summary: "Elevated 4xx rate on {{ $labels.service }}"
          description: "4xx responses account for {{ $value | printf \"%.1f\" }}% of traffic (check recent client/API changes)."

      # WARN (No Page): Sustained CPU saturation (>85% for 15m)
      - alert: ServiceCPUSaturation
        expr: |
          (
            sum by (namespace, pod) (rate(container_cpu_usage_seconds_total{app="my-service", container!=""}[5m]))
            /
            sum by (namespace, pod) (kube_pod_container_resource_limits{app="my-service", resource="cpu"})
          ) * 100 > 85
        for: 15m
        labels:
          severity: warning
          service: my-service
        annotations:
          summary: "Sustained high CPU on {{ $labels.pod }}"
          description: "Pod {{ $labels.pod }} has been above 85% CPU for 15m. Check autoscaler max replicas or resource limits."
```

### sdlc-observability-reliability / alert-noise / with skill / PASS

I cannot write paging rules for **CPU > 60%**, **every 4xx**, or **deployments**, because paging a human on those signals violates core reliability principles (**Never alert humans for signals that have no expected action**):

- **CPU > 60%**: High utilization is normal under load or during batch jobs. If users aren't experiencing latency or errors, there is nothing for an on-call engineer to fix at 3 AM. (Keep this on a dashboard or use it for autoscaling).
- **Any 4xx response**: Client errors (`400`, `401`, `404`, `429`) are normal traffic (bad user input, expired tokens, scanners). Paging on a single `4xx` will cause immediate alert fatigue. Only a sudden *spike* in `401`/`403`/`400` after a deploy or a change in `5xx` warrants investigation.
- **Deployments happening**: A deployment is an expected event, not an incident. It belongs as an annotation on your dashboards and an audit/Slack log—not an on-call page.

Here is an observability and alerting design following the reliability workflow in order:

---

### Step 1: Identify Critical User Journeys, Dependencies, and Failure Modes

Since we are designing for a standard web/API service, we anchor on what matters to users:
- **Critical User Journeys (CUJs)**:
  - **Authentication / Session validation**: Users can log in and authenticate requests.
  - **Core Read/Write API operations**: Users can fetch data and submit transactions within acceptable response times.
- **Dependencies**:
  - Primary datastore (e.g., PostgreSQL/Redis), upstream identity provider (Auth), and downstream third-party APIs.
- **Key Failure Modes**:
  - **Service crash / bad deploy**: Elevated `5xx` responses or health check failures following a rollout.
  - **Resource saturation / downstream contention**: CPU/connection pool exhaustion causing request queuing and high tail latency (`p99`), eventually timing out.
  - **Broken client contract / auth misconfiguration**: A deploy breaks request validation or auth middleware, causing a massive spike in `400`/`401`/`403` across all users (as opposed to isolated client errors).

---

### Step 2: Define SLIs and SLOs from User-Visible Behavior

Instead of raw infrastructure counters, we measure user experience using two primary Service Level Indicators (SLIs) and set Service Level Objectives (SLOs):

1. **Availability SLI**: The proportion of valid requests that succeed (status codes `2xx`–`4xx`, excluding `429` if server-capacity-induced, vs. `5xx` server errors).
   - **Formula**: `sum(rate(http_requests_total{status!~"5.."}[window])) / sum(rate(http_requests_total[window]))`
   - **SLO Target**: **99.9%** over a rolling 30-day window (Error budget: ~43.2 minutes of 100% outage, or 0.1% of requests).
2. **Latency SLI**: The proportion of valid requests served faster than the user-tolerable threshold (e.g., `< 500ms`).
   - **Formula**: `sum(rate(http_request_duration_seconds_bucket{le="0.5"}[window])) / sum(rate(http_request_duration_seconds_count[window]))`
   - **SLO Target**: **99.0%** of requests complete within `500ms` over a rolling 30-day window.

---

### Step 3: Specify Logs, Metrics, Traces, Dashboards, Alerts, and Runbooks

#### Telemetry & Dashboards
- **Metrics (Prometheus/OpenTelemetry)**:
  - `http_requests_total{service, route, method, status, version}` (Counter)
  - `http_request_duration_seconds_bucket{service, route, le}` (Histogram)
  - `process_cpu_seconds_total` / container CPU limits (Gauge/Counter — **for dashboards & correlation, not paging**)
  - `deployment_events_total{service, version, git_sha}` (Metric/Event — **rendered as vertical annotations on Grafana dashboards**)
- **Structured Logs**: JSON logs emitted on `5xx` and sampled `4xx` containing `trace_id`, `route`, `status`, `error_code`, `deployment_version`, and `latency_ms`.
- **Traces**: Distributed trace spans across HTTP handlers and DB/downstream calls to pinpoint whether latency comes from CPU contention or downstream waits.

#### Actionable Alert Rules (Prometheus / Alertmanager format)

Here are the replacement rules that protect your service against bad deploys, saturation, and broken contracts while only paging when human action is required:

```yaml
groups:
  - name: service-slo-and-symptom-alerts
    rules:
      # 1. PAGE: Fast Error Budget Burn (Replaces "Any 4xx" / catches bad deploys fast)
      # Pages when 2% of the 30-day error budget is burned in 1 hour (~14.4x burn rate).
      - alert: HighErrorBudgetBurnPage
        expr: |
          (
            sum(rate(http_requests_total{service="my-service", status=~"5.."}[1h]))
            /
            sum(rate(http_requests_total{service="my-service"}[1h]))
          ) > (14.4 * (1 - 0.999))
          and
          (
            sum(rate(http_requests_total{service="my-service", status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total{service="my-service"}[5m]))
          ) > (14.4 * (1 - 0.999))
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "High 5xx error rate burning SLO budget on {{ $labels.service }}"
          runbook_url: "https://runbooks.internal/my-service/high-error-burn"
          action: "Check recent deployment annotations; rollback if correlated with a recent release, or inspect 5xx structured logs by trace_id."

      # 2. PAGE: High Latency SLO Burn (Replaces "CPU > 60%" page)
      # Pages only when saturation (CPU, DB, locks) actually degrades user latency.
      - alert: HighLatencySLOBurnPage
        expr: |
          (
            1 - (
              sum(rate(http_request_duration_seconds_bucket{service="my-service", le="0.5"}[1h]))
              /
              sum(rate(http_request_duration_seconds_count{service="my-service"}[1h]))
            )
          ) > (14.4 * (1 - 0.99))
          and
          (
            1 - (
              sum(rate(http_request_duration_seconds_bucket{service="my-service", le="0.5"}[5m]))
              /
              sum(rate(http_request_duration_seconds_count{service="my-service"}[5m]))
            )
          ) > (14.4 * (1 - 0.99))
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "User-facing latency exceeding 500ms budget on {{ $labels.service }}"
          runbook_url: "https://runbooks.internal/my-service/high-latency"
          action: "Check service dashboard for CPU/memory saturation, DB connection pool exhaustion, or slow downstream spans. Scale replicas or rollback if triggered by a deploy."

      # 3. TICKET: Slow Error Budget Burn (Deferred work, no 3 AM page)
      # Creates a ticket when 10% of the 30-day budget is burned over 3 days (1x-3x burn).
      - alert: SlowErrorBudgetBurnTicket
        expr: |
          (
            sum(rate(http_requests_total{service="my-service", status=~"5.."}[6h]))
            /
            sum(rate(http_requests_total{service="my-service"}[6h]))
          ) > (6 * (1 - 0.999))
        for: 30m
        labels:
          severity: ticket
        annotations:
          summary: "Sustained elevated error rate consuming error budget on {{ $labels.service }}"
          runbook_url: "https://runbooks.internal/my-service/slow-burn"
          action: "Triage during business hours: group 5xx logs by route and error_code to schedule a bug fix."

      # 4. TICKET: Abnormal Auth/Client Error Spike (Safe alternative to "any 4xx")
      # Opens a ticket (or warning) if 401/403/400 exceeds 25% of total traffic at meaningful volume,
      # indicating a broken client release or auth misconfiguration rather(than normal client mistakes).
      - alert: AbnormalClientErrorSpikeTicket
        expr: |
          (
            sum(rate(http_requests_total{service="my-service", status=~"400|401|403"}[15m]))
            /
            sum(rate(http_requests_total{service="my-service"}[15m]))
          ) > 0.25
          and
          sum(rate(http_requests_total{service="my-service"}[15m])) > 10
        for: 10m
        labels:
          severity: ticket
        annotations:
          summary: "Over 25% of requests are failing with 400/401/403 on {{ $labels.service }}"
          runbook_url: "https://runbooks.internal/my-service/client-error-spike"
          action: "Verify if a recent deploy changed API schema validation or IAM/OAuth configuration."
```

#### Runbooks
Every alert above links to a specific runbook step:
1. **`high-error-burn`**: Check dashboard deploy annotations -> If a deploy occurred within 15 minutes, run `kubectl rollout undo` (or CI rollback) -> Otherwise check `status >= 500` logs grouped by `error_code` and downstream dependency health.
2. **`high-latency`**: Inspect CPU/Memory utilization and HPA replica counts -> If CPU is pinned and traffic is legitimate, increase max replicas -> If CPU is low, inspect trace waterfall for slow DB queries or downstream timeouts.

---

### Step 4: Tune Alerting (Pages vs. Tickets vs. Telemetry)

| Original Request | Why It Was Changed | New Routing | Expected Human Action |
| :--- | :--- | :--- | :--- |
| **Page on CPU > 60%** | CPU is a *cause*, not a user symptom; 60% is healthy utilization. | **Autoscaler (HPA) + Dashboard**; Page only on **HighLatencySLOBurnPage** | Configure HPA to scale pods automatically at 65–70% CPU. Only page a human if scaling hits max capacity and user latency (`p99`) breaches SLO. |
| **Page on any 4xx** | Individual `4xx` responses are normal client behavior and unactionable. | **Ticket** on **AbnormalClientErrorSpikeTicket** (`>25%` `400/401/403` for 10m) | Investigate during business hours whether an API contract or auth token validator broke after a release. |
| **Page on every deploy** | Deploys are routine changes, not emergencies. | **Dashboard Annotation + CI/CD Slack Notification** | None when healthy. If a deploy breaks production, **HighErrorBudgetBurnPage** will page within 2 minutes with the deploy visible on the graph. |

---

### Step 5: Feed Incidents, Support Signals, and DORA Metrics into Continuous Improvement

To keep these rules accurate over time:
1. **Track DORA Metrics alongside SLOs**: Use deployment events (instead of deploy pages) to measure **Deployment Frequency** and **Change Failure Rate** (the % of deploys that trigger `HighErrorBudgetBurnPage` or require rollback), plus **MTTR** (time from page to SLO recovery).
2. **Post-Incident & Alert Reviews**: Every time an on-call engineer is paged, log whether the page was actionable. If an alert fires twice without requiring a rollback, scale-up, or mitigation, delete or convert it to a ticket.
3. **Support Signal Loop**: If customer support reports user pain that did *not* trigger an SLO alert, tighten the SLI definition (e.g., add per-route SLIs for low-volume critical endpoints like `/checkout` that might be masked by high-volume `/status` traffic).

### sdlc-prd-requirements / prd-vague-verbs / baseline / PASS

Here is the structured requirement list based on the PM's input, along with the explicit engineering and product specifications that remain to be defined before implementation:

### 1. Performance ("Search should be fast")
* **Requirement:** The search endpoint and UI must return and render results within a defined latency budget under expected load.
* **To be specified (TBD):**
  * **Latency SLA:** Target p50, p95, and p99 response times (e.g., `< 200ms` p95 for API response; `< 100ms` for autocomplete/typeahead).
  * **Throughput & Scale:** Expected queries per second (QPS) at normal and peak load, and total searchable dataset size.
  * **Indexing freshness:** Maximum acceptable delay between a data update and its visibility in search results.

### 2. Filtering & Query Capabilities ("Support many filters")
* **Requirement:** Users must be able to narrow search results using multiple combinable filter attributes alongside text queries.
* **To be specified (TBD):**
  * **Supported fields & types:** Exact list of filterable attributes (e.g., category, price range, date, tags, status, availability).
  * **Filter logic:** Combinatorial behavior (`AND` vs. `OR` within a single facet and across multiple facets).
  * **Facet counts:** Whether the API must return dynamic result counts per filter option.
  * **Query behavior:** Support for partial matching, fuzzy matching/typo tolerance, synonyms, and sorting options (relevance, price, recency).

### 3. Resilience & Error Handling ("Handle errors gracefully")
* **Requirement:** The search system must degrade predictably and provide clear, actionable states when queries fail, return no results, or receive invalid input.
* **To be specified (TBD):**
  * **Zero-results state:** Expected fallback behavior when a query matches nothing (e.g., "Did you mean...", relaxing filters, showing popular items).
  * **Invalid input handling:** Validation rules for malformed queries, unsupported characters, or out-of-bounds filter values.
  * **Backend/Timeout failures:** Fallback strategy on search service timeout or outage (e.g., cached results, retry policy, user-facing error message without crashing the page).

### 4. Conversion & Analytics ("Improve conversion")
* **Requirement:** Search relevance and UI interactions must be instrumented to measure and optimize user progression toward the target conversion event.
* **To be specified (TBD):**
  * **Definition of conversion:** The specific target action (e.g., item purchase, signup, document download, click-through on a result) and baseline vs. target conversion rate.
  * **Ranking & Relevance:** Business rules for boosting or pinning results (e.g., in-stock items, high-margin items, popularity signals).
  * **Telemetry:** Required analytics events (e.g., search submitted, filter applied, result clicked with position/rank, zero-result query logged).

### sdlc-prd-requirements / prd-vague-verbs / with skill / PASS

Below is the structured PRD and requirement specification for the Search Feature, following the `sdlc-prd-requirements` steps in order and translating the vague PM inputs ("fast", "support many filters", "handle errors gracefully", "improve conversion") into testable, observable behaviors with explicit tags for assumptions, open questions, dependencies, and decision owners.

---

### Step 1: Goal, Background, Users, Scope, Non-Goals, and Constraints

* **Goal:** Enable users to find relevant catalog items via keyword queries and multi-facet filtering with low latency and resilient error states, increasing search-to-conversion rates.
* **Background:** The PM requested a search capability that responds quickly, allows multi-dimensional filtering, recovers predictably from failures, and drives user conversion. Because exact thresholds and filter taxonomies were not supplied in the initial brief, baseline targets are proposed below as tagged assumptions pending sign-off.
* **Target Users:**
  * **End Users / Shoppers:** Authenticated or anonymous visitors searching for items with specific attributes.
  * **Merchandising / Product Team:** Stakeholders monitoring search conversion and zero-result queries.
* **In Scope (v1):**
  * Keyword search input and result list rendering.
  * Faceted filtering (combining multiple filter attributes and values).
  * Empty-state ("no results") and system-error state behaviors.
  * Search analytics and conversion event instrumentation.
* **Non-Goals (Out of Scope for v1):**
  * Natural-language conversational/AI chat search (`[ASSUMPTION-01]` — Owner: PM).
  * Personalized ranking based on historical user embeddings (`[ASSUMPTION-02]` — Owner: PM).
  * Cross-tenant or federated external web search (`[ASSUMPTION-03]` — Owner: Architecture Lead).
* **Constraints:**
  * Must operate within existing API rate limits and catalog update cadences (`[DEPENDENCY-01: Catalog Indexing Pipeline]` — Owner: Backend Lead).
  * Must comply with WCAG 2.1 AA accessibility standards for keyboard navigation, focus management, and screen-reader announcements (`[ASSUMPTION-04]` — Owner: Design Lead).

---

### Step 2: Observable Functional & Quality Requirements

*(Note: Vague verbs from the brief—"fast", "support", "handle", "improve"—have been replaced with measurable quality thresholds and observable system behaviors.)*

#### R1. Search Latency & Responsiveness (replaces *"Search should be fast"*)
* **R1.1 (Query Response Time):** When a user submits a keyword query or toggles a filter on a catalog of up to 1,000,000 items, the system shall return and render the first page of results (24 items) within **$\le$ 300 ms at P50** and **$\le$ 800 ms at P95** measured from user action to DOM paint (`[ASSUMPTION-05]`, `[OPEN-QUESTION-01]`).
* **R1.2 (Typeahead / Autocomplete Latency):** When a user types 3 or more characters into the search input, the system shall display up to 8 query/item suggestions within **$\le$ 150 ms at P95** after a 150 ms input debounce (`[ASSUMPTION-06]`).
* **R1.3 (Loading State Feedback):** If a search request takes longer than **200 ms**, the UI shall display a non-layout-shifting skeleton loader over the results area until results or an error state render.

#### R2. Faceted Filtering Behavior (replaces *"support many filters"*)
* **R2.1 (Supported Filter Facets):** The system shall expose the following filter facets on search results: **Category** (multi-select), **Price Range** (min/max numeric bounds), **Brand/Creator** (multi-select), **Rating** (minimum threshold), **Availability/In-Stock** (boolean toggle), and **Sort Order** (Relevance, Price Low-to-High, Price High-to-Low, Newest) (`[ASSUMPTION-07]`, `[OPEN-QUESTION-02]`).
* **R2.2 (Combinatorial Filter Logic):**
  * Selecting multiple values **within the same facet** (e.g., `Brand = Nike` OR `Brand = Adidas`) shall apply **disjunctive (OR)** logic.
  * Selecting values **across different facets** (e.g., `Brand = Nike` AND `In-Stock = true` AND `Price <= 100`) shall apply **conjunctive (AND)** logic.
  * A user shall be able to apply up to **10 simultaneous active filter criteria** without exceeding the R1.1 latency budget.
* **R2.3 (Facet Counts & Zero-Count Prevention):** Each filter option shall display the count of matching items in parentheses. Filter values that would yield 0 results given the current query and other active facets shall be visually disabled (or show `(0)`) so users cannot accidentally click into a dead-end state (`[ASSUMPTION-08]`).
* **R2.4 (URL State Persistence):** Every active query, filter selection, sort order, and page number shall be serialized into the URL query string so that refreshing the page, using the browser Back/Forward buttons, or sharing the URL reproduces the exact same search state.

#### R3. Error Recovery & Edge-Case Behavior (replaces *"handle errors gracefully"*)
* **R3.1 (Zero-Results State):** When a valid search query and/or filter combination returns 0 matching items, the system shall:
  1. Display a clear message stating no exact matches were found for the specific query/filters.
  2. Provide one-click **"Remove [Filter]"** pills and a **"Clear all filters"** button if any filters are active.
  3. If a single-character or phonetic typo is detected, either auto-correct with a *"Showing results for **[corrected]** — Search instead for **[original]**"* banner, or display up to 3 suggested alternative queries (`[ASSUMPTION-09]`).
* **R3.2 (Transient Network / Timeout / 5xx Failure):** When the search backend returns a `5xx` status, `429 Too Many Requests`, or times out after **3,000 ms**, the system shall:
  1. Automatically retry idempotent read requests once with a 300 ms backoff (`[ASSUMPTION-10]`).
  2. If the retry fails, preserve the user's typed query and active filter selections in the UI.
  3. Display a non-destructive inline alert (*"We couldn't load search results right now"*) with a **"Retry"** button that re-executes the exact query without requiring the user to re-type.
* **R3.3 (Partial Facet Degradation):** If the primary search results succeed but secondary metadata (e.g., facet counts or promotional banners) fails to load, the system shall render the matching items list and hide or disable only the failed secondary component.
* **R3.4 (Input Sanitization & Boundary Limits):**
  * Submitting an empty or whitespace-only query shall not trigger a network request and shall keep focus in the search input.
  * Queries exceeding **200 characters** shall be truncated at 200 characters with an inline notice, and special/control characters (`<`, `>`, `;`, `{}`) shall be treated as literal text or stripped without throwing a `400`/`500` error.

#### R4. Conversion Instrumentation & Merchandising Actions (replaces *"improve conversion"*)
* **R4.1 (Result Card Conversion Affordances):** Each search result item shall display its title, primary thumbnail, price, rating summary, stock status, and a direct conversion CTA (e.g., **"Add to Cart"** or **"View Details"**) so users can act directly from the search results page (`[ASSUMPTION-11]`, `[OPEN-QUESTION-03]`).
* **R4.2 (Telemetry & Attribution Events):** The client and backend shall emit structured analytics events with a shared `search_session_id` for:
  1. `search_executed` (query string, active filters, result count, latency_ms)
  2. `search_result_clicked` (query, item_id, rank_position)
  3. `search_zero_results` (query, active filters)
  4. `search_converted` (item_id, conversion_action, time_from_search_ms)

---

### Step 3: Registry of Assumptions, Open Questions, Dependencies, and Decision Owners

| ID | Type | Description | Decision Owner | Impact if Changed |
| :--- | :--- | :--- | :--- | :--- |
| `ASSUMPTION-05` | Assumption | Latency target is P50 $\le$ 300 ms and P95 $\le$ 800 ms for 24 results per page. | **PM / Eng Lead** | Determines caching tier and search index sharding requirements. |
| `ASSUMPTION-06` | Assumption | Typeahead triggers at $\ge$ 3 characters with P95 $\le$ 150 ms. | **PM / Frontend Lead** | Affects prefix-index memory footprint and API request volume. |
| `ASSUMPTION-07` | Assumption | v1 filter taxonomy is Category, Price, Brand, Rating, In-Stock, and Sort. | **PM** | Adding dynamic/custom category attributes requires schema-driven facet rendering. |
| `ASSUMPTION-08` | Assumption | Multi-select within a facet uses OR logic; across facets uses AND logic. | **PM / UX Lead** | Changes query builder AST and facet count aggregation queries. |
| `ASSUMPTION-09` | Assumption | Typo tolerance uses Levenshtein distance $\le$ 2 with a "Search instead for" fallback banner. | **PM / Search Eng** | Requires fuzzy-matching analyzer configuration in the search index. |
| `ASSUMPTION-10` | Assumption | Client timeout is 3,000 ms with 1 automatic retry (300 ms backoff) on network/5xx errors. | **Backend Lead** | Must align with API gateway timeout and circuit-breaker thresholds. |
| `ASSUMPTION-11` | Assumption | "Conversion" is defined as clicking through to an item and completing the primary CTA (e.g., Add-to-Cart / Checkout) within the same session. | **PM / Data Analytics** | Determines which funnel step is optimized and instrumented. |
| `OPEN-QUESTION-01` | Open Question | What is the maximum catalog size (total documents) expected over the next 12 months? | **PM / Infra Lead** | Sizes the search cluster and memory budget. |
| `OPEN-QUESTION-02` | Open Question | Are category-specific dynamic facets (e.g., "Size" for apparel, "Storage" for electronics) required in v1? | **PM** | Scope change for R2.1 and facet UI layout. |
| `OPEN-QUESTION-03` | Open Question | What is the current baseline search-to-conversion rate, and what is the target percentage lift for v1? | **PM** | Sets the pass/fail threshold for the A/B release gate in Step 4. |
| `DEPENDENCY-01` | Dependency | Search index must receive catalog price/stock updates within $\le$ 60 seconds of source-of-truth changes. | **Backend / Data Platform Lead** | Prevents users from filtering by "In-Stock" and landing on out-of-stock items. |
| `DEPENDENCY-02` | Dependency | Analytics pipeline must support `search_session_id` attribution across search and conversion events. | **Data / Analytics Eng** | Required to measure R4 and the product metrics in Step 4. |

---

### Step 4: BDD Examples and Product Metrics Mapping

#### 4.1 BDD Acceptance Scenarios (Gherkin)

```gherkin
Feature: Product Search and Faceted Filtering

  # Maps to R1.1, R2.1, R2.2, R2.4
  Scenario: Combining multiple filters updates results within latency budget and persists in URL
    Given the catalog contains 500,000 items
    When the user searches for "running shoes"
    And selects the Brand filters "Nike" and "Asics"
    And sets the Price filter maximum to "150"
    And enables the "In-Stock Only" filter
    Then the system renders matching items within 800 ms
    And every displayed item has (Brand "Nike" OR "Asics") AND (Price <= 150) AND (In-Stock = true)
    And the browser URL contains the query "running shoes", brands "Nike,Asics", maxPrice "150", and inStock "true"

  # Maps to R3.1 (Zero-Results Recovery)
  Scenario: Zero results with active filters provides one-click filter removal
    Given the user has searched for "wireless headphones" with active filters Brand="Sony" and MaxPrice="20"
    When the search returns 0 matching items
    Then the system displays the message "No exact matches found for 'wireless headphones' with your selected filters"
    And displays removable filter pills for "Brand: Sony" and "Max Price: $20" and a "Clear all filters" button
    When the user clicks the "Clear all filters" button
    Then the system re-runs the query "wireless headphones" with no filters and displays matching items

  # Maps to R3.2 (Graceful Failure & Retry)
  Scenario: Backend 503 failure preserves user state and allows one-click recovery
    Given the user has typed "mechanical keyboard" and selected the filter "In-Stock Only"
    When the search API returns HTTP 503 Service Unavailable on the initial call and automatic retry
    Then the search input still contains "mechanical keyboard" and "In-Stock Only" remains checked
    And the results region displays an error alert with a "Retry" button
    When the search API recovers and the user clicks "Retry"
    Then the system executes the search for "mechanical keyboard" with "In-Stock Only" and renders the results
```

#### 4.2 Product Metrics & Release Gates

| Requirement | Metric Name | Formula / Definition | Target / Gate (`[ASSUMPTION-12]` — Owner: PM) |
| :--- | :--- | :--- | :--- |
| **R1.1, R1.2** | Search Response Latency | P50 / P95 time from query submission to results rendered | **P50 $\le$ 300 ms, P95 $\le$ 800 ms** |
| **R2.1–R2.3, R4.1** | Search-to-Conversion Rate | $\frac{\text{Sessions with Search + Conversion Event}}{\text{Total Sessions with Search}}$ | **$\ge$ +10% relative lift** over baseline in A/B test (`[OPEN-QUESTION-03]`) |
| **R1.1, R2.2, R4.1** | Search Click-Through Rate (CTR) | $\frac{\text{Searches with } \ge 1 \text{ Result Click within Top 5}}{\text{Total Searches with } \ge 1 \text{ Result}}$ | **$\ge$ 45%** |
| **R3.1** | Zero-Result Rate (ZRR) | $\frac{\text{Searches Returning 0 Results}}{\text{Total Searches Executed}}$ | **$\le$ 5%** (and $\ge$ 25% of zero-result sessions recover via filter-clear or suggestion click) |
| **R3.2** | Unrecovered Search Error Rate | $\frac{\text{Search Requests Failing After Retry}}{\text{Total Search Requests}}$ | **$< 0.1\%$** |

---

### Step 5: Revision Triggers (When to Update These Requirements)

These requirements must be revised before or during implementation if any of the following occur:
1. **Catalog Scale / Latency Trade-off (`OPEN-QUESTION-01`):** If architecture benchmarks show that computing exact disjunctive facet counts (`R2.3`) across $>10$ facets exceeds the 800 ms P95 budget (`R1.1`), revise `R2.3` to specify whether approximate facet counts or lazy facet count loading is acceptable.
2. **Dynamic Category Facets (`OPEN-QUESTION-02`):** If UX design or merchandising requires category-dependent facets (e.g., showing "Size" only when the "Apparel" category is selected), update `R2.1` to specify the trigger rules and how incompatible active child filters behave when the parent category is deselected.
3. **Conversion Definition Alignment (`OPEN-QUESTION-03`):** Once PM and Analytics confirm the exact conversion event and baseline metric, lock the numeric threshold in Step 4.2 and update `R4.1` with the exact CTA fields required on result cards.

### sdlc-prd-requirements / prd-vague-verbs / baseline / FAIL

Here is the structured requirement list based on the PM's brief. Because "fast," "many filters," "gracefully," and "improve conversion" are high-level goals rather than testable engineering specs, items that require concrete product/engineering targets are marked with **`[TBD]`** so they aren't silently invented.

---

### 1. Performance & Latency ("Search should be fast")
* **REQ-PERF-01 (Query Latency):** Search results must return within **`[TBD: e.g., p50 < 150ms, p95 < 400ms]`** from request receipt to response payload under normal load.
* **REQ-PERF-02 (Autocomplete / Typeahead):** *If in scope:* Typeahead suggestions must render within **`[TBD: e.g., p95 < 100ms]`** after input debouncing (`[TBD: e.g., 150–300ms]`).
* **REQ-PERF-03 (Throughput & Concurrency):** The search endpoint must sustain **`[TBD: e.g., N requests/second]`** without degradation or dropped requests.
* **REQ-PERF-04 (Pagination / Payload Size):** Results must be paginated or virtualized (default page size: **`[TBD: e.g., 20–50 items]`**) to bound payload size and client render time.

### 2. Filtering & Faceting ("Support many filters")
* **REQ-FILT-01 (Supported Filter Attributes):** The search API and UI must support filtering by the following domain attributes: **`[TBD: enumerate exact fields, e.g., category, price/date range, status, tags, rating, availability]`**.
* **REQ-FILT-02 (Filter Composition Logic):**
  * Combining values *across* different filter categories must apply `AND` logic.
  * Combining multiple values *within* the same multi-select filter category must apply **`[TBD: OR / AND]`** logic.
* **REQ-FILT-03 (Facet Counts):** *If in scope:* Search responses must return dynamic facet counts per filter option reflecting the current active query and filter state.
* **REQ-FILT-04 (State Persistence):** Active search queries, filters, sort order, and pagination state must be serialized in URL query parameters to support shareable links, page reloads, and browser back/forward navigation.
* **REQ-FILT-05 (Sorting):** Users must be able to sort filtered results by **`[TBD: e.g., Relevance (default), Newest, Price: Low to High, Price: High to Low]`**.

### 3. Resilience & Error Handling ("Handle errors gracefully")
* **REQ-ERR-01 (Zero-Results State):** When a query + filter combination yields `0` results, the UI must display a clear empty state with actionable recovery options (e.g., a one-click "Clear all filters" button, spelling suggestions, or fallback popular items).
* **REQ-ERR-02 (Input Sanitization & Edge Cases):** The search parser must safely handle empty strings, whitespace-only queries, special characters, overly long inputs (capped at **`[TBD: e.g., 256 characters]`**), and injection attempts without throwing unhandled exceptions (`500` errors).
* **REQ-ERR-03 (Backend / Network Failure):** If the search service times out (`[TBD: e.g., > 3000ms]`) or returns a `5xx` / rate-limit (`429`) error, the UI must display a non-destructive error message with a "Retry" action while preserving the user's current query and selected filters.
* **REQ-ERR-04 (Out-of-Order / Stale Requests):** Rapid consecutive changes to queries or filters must cancel in-flight requests or ignore stale responses so the UI never renders results from an older query over a newer one.

### 4. Relevance, UX & Conversion Tracking ("Improve conversion")
* **REQ-CONV-01 (Primary Conversion Metric):** Success will be measured by **`[TBD: define target metric, e.g., Search-to-Click-Through Rate (CTR), Search-to-Add-to-Cart/Action, or Search Exit Rate]`** improving by **`[TBD: +X%]`** over baseline.
* **REQ-CONV-02 (Query Tolerance):** *If supported by search engine:* Search matching should support case-insensitivity, stemming/pluralization, and typo tolerance (`[TBD: e.g., edit distance of 1–2]`) to minimize dead-end searches.
* **REQ-CONV-03 (Result Card Actionability):** Each search result item must display key decision-making fields (**`[TBD: e.g., title, thumbnail, price/status, primary CTA]`**) so users can take the target conversion action directly from the results or navigate immediately to the detail view.
* **REQ-CONV-04 (Search Analytics & Telemetry):** The system must emit structured events for:
  * `search_submitted` (query string, active filters, result count, latency)
  * `search_zero_results` (query string, active filters)
  * `search_result_clicked` (query string, item ID, result rank/position)
  * `search_converted` (attributing downstream conversion action to the originating search session)

---

### Summary of Open Decisions (`[TBD]`) to Finalize Before Implementation
1. **Target SLAs:** Exact p95 latency target and expected peak QPS.
2. **Data Schema:** The exact list of filterable/sortable fields and their data types (enum, boolean, numeric range, date range).
3. **Search Engine Capabilities:** Whether typo tolerance, synonyms, and dynamic facet counts are supported by the current backend/database or require dedicated search infrastructure (e.g., Elasticsearch, OpenSearch, Typesense, Algolia, Postgres FTS).
4. **Conversion Definition:** What specific user action counts as a "conversion" in this product context.

### sdlc-prd-requirements / prd-vague-verbs / with skill / PASS

The PM prompt relies entirely on unquantified verbs (*"be fast"*, *"support many filters"*, *"handle errors gracefully"*, *"improve conversion"*). Following the `sdlc-prd-requirements` skill, I cannot emit vague requirements as-is; instead, below is the full 5-step PRD baseline that replaces each vague verb with observable behavior or measurable quality expectations, while explicitly tagging every provisional assumption (`[ASSUMPTION]`), open question (`[OPEN QUESTION]`), dependency (`[DEPENDENCY]`), and decision owner (`[OWNER]`) where inputs are missing.

---

### Step 1: Goal, Background, Users, Scope, Non-Goals, and Constraints

* **Goal:** Enable users to find relevant catalog items via keyword queries and faceted filtering so they can complete their primary conversion action with minimal latency and zero dead-end error states.
* **Background:** Current product discovery lacks structured performance budgets, explicit filter definitions, and resilient fallback behaviors, creating friction along the conversion path.
* **Target Users:**
  * *Primary:* Authenticated or anonymous end-users searching and filtering catalog items (`[ASSUMPTION: E-commerce or SaaS catalog items]` `[OWNER: PM]`).
* **In Scope (v1):**
  * Keyword search execution and result list rendering.
  * Multi-facet filtering and filter-state clearing.
  * Empty-result ("zero hits") and system-failure ("timeout/5xx") user-facing states.
  * Analytics event instrumentation for search-to-conversion tracking.
* **Non-Goals (Out of Scope for v1):**
  * Natural-language conversational/LLM search or semantic vector recommendations (`[ASSUMPTION]` `[OWNER: PM]`).
  * Personalized per-user ranking models (`[ASSUMPTION]` `[OWNER: PM]`).
  * Cross-workspace or federated third-party search.
* **Constraints:**
  * Must operate within existing backend search index capabilities (`[DEPENDENCY: Search Index / API Service]` `[OWNER: Tech Lead]`).
  * Must meet WCAG 2.1 AA keyboard navigation and screen-reader announcements for dynamic result updates.

---

### Step 2: Observable Functional & Measurable Quality Requirements

> *Note: All vague verbs ("support", "handle", "improve", "be fast") have been replaced with testable system behaviors and concrete thresholds marked as provisional assumptions until signed off by their decision owners.*

#### 1. Search Latency & Responsiveness (Replaces *"Search should be fast"*)
* **REQ-PERF-01 (API Response Time):** The search endpoint MUST return a valid response payload within **$\le$ 200 ms at p50** and **$\le$ 500 ms at p95** under peak load of **100 requests/second** (`[ASSUMPTION: 200ms/500ms @ 100 RPS target]` `[OWNER: PM / Eng Lead]`).
* **REQ-PERF-02 (UI Render Time):** The client UI MUST render updated search results within **$\le$ 100 ms** of receiving the response payload.
* **REQ-PERF-03 (Loading Feedback):** If a search request exceeds **300 ms** in flight, the UI MUST display a non-blocking loading indicator (skeleton or spinner) while preserving the user's current input focus.

#### 2. Faceted Filtering Behavior (Replaces *"Support many filters"*)
* **REQ-FILT-01 (Available Filter Facets):** The search interface MUST allow users to filter results by the following explicit attributes: **Category** (multi-select), **Status/Availability** (boolean toggle), **Price/Value Range** (min/max numeric bounds), and **Date/Recency** (preset ranges) (`[ASSUMPTION: Exact facet list pending domain confirmation]` `[OPEN QUESTION: OQ-02]` `[OWNER: PM]`).
* **REQ-FILT-02 (Combinatorial Logic):** Selecting multiple values *within* the same multi-select facet MUST apply boolean `OR` logic; selecting values *across* different facets MUST apply boolean `AND` logic.
* **REQ-FILT-03 (Active Filter Management):** Each applied filter MUST render as a dismissible pill/tag showing its attribute and value, alongside a single **"Clear all filters"** action that resets the query to unfiltered results in one interaction.
* **REQ-FILT-04 (URL/State Persistence):** Applied query strings and filter selections MUST be serialized in the URL query parameters so that page refreshes and shared links reproduce the exact filtered view (`[ASSUMPTION]` `[OWNER: PM / Frontend Lead]`).

#### 3. Deterministic Error & Empty States (Replaces *"Handle errors gracefully"*)
* **REQ-ERR-01 (Zero-Result State):** When a valid query + filter combination returns `0` matches, the UI MUST display an explicit message stating no matches were found for `<query>`, render a **"Reset filters"** CTA if any filters are active, and log a `search_zero_results` telemetry event.
* **REQ-ERR-02 (Backend Timeout / 5xx Failure):** When the search service fails to respond within **3,000 ms** or returns an HTTP `5xx` / network error, the UI MUST preserve the user's typed query and selected filters, display a non-technical error banner with a **"Retry search"** button, and avoid clearing any previously rendered results if a filter update triggered the failure.
* **REQ-ERR-03 (Invalid Input Sanitization):** When a user submits a query exceeding **256 characters** or containing unsupported control characters, the system MUST truncate or sanitize the input without throwing an unhandled exception (`[ASSUMPTION: 256-char max]` `[OWNER: Eng Lead]`).

#### 4. Search-to-Conversion Instrumentation (Replaces *"Improve conversion"*)
* *Note: "Improve conversion" is a product outcome metric (see Step 4), not a software behavior. To achieve and measure it, the software must implement the following observable behaviors:*
* **REQ-CONV-01 (Result Actionability):** Every search result card MUST display the item's primary identifier, key differentiating metadata, and a direct **Primary Conversion CTA** (e.g., *"Add to Cart"* / *"Select"* / *"View Details"*) without requiring an intermediate page load (`[ASSUMPTION]` `[OPEN QUESTION: OQ-04]` `[OWNER: PM / Design]`).
* **REQ-CONV-02 (Funnel Telemetry):** The client MUST emit structured analytics events for `search_submitted`, `search_filter_applied`, `search_result_clicked` (including `result_rank` and `query_id`), and `search_conversion_completed` (linking `query_id` to the conversion event) (`[DEPENDENCY: Analytics Pipeline]` `[OWNER: Data / PM]`).

---

### Step 3: Tagged Assumptions, Open Questions, Dependencies, and Decision Owners

| ID | Type | Description | Impacted Reqs | Decision Owner |
| :--- | :--- | :--- | :--- | :--- |
| **OQ-01** | `[OPEN QUESTION]` | What is the exact catalog size (10k vs. 10M items) and expected peak RPS? | REQ-PERF-01 | **Eng Lead / PM** |
| **OQ-02** | `[OPEN QUESTION]` | Which exact filter facets, data types, and max multi-select limits are required for v1? | REQ-FILT-01, REQ-FILT-02 | **PM** |
| **OQ-03** | `[OPEN QUESTION]` | Should failed search requests automatically retry with exponential backoff before showing the error banner, or fail immediately to the manual "Retry" button? | REQ-ERR-02 | **Eng Lead / Design** |
| **OQ-04** | `[OPEN QUESTION]` | What is the exact definition of the conversion event (e.g., checkout completion, item selection, lead submission), current baseline rate, and target lift %? | REQ-CONV-01, REQ-CONV-02 | **PM** |
| **ASM-01** | `[ASSUMPTION]` | p95 API latency of $\le$ 500 ms is achievable without re-architecting the current database/search index. | REQ-PERF-01 | **Eng Lead** |
| **ASM-02** | `[ASSUMPTION]` | Filter selections apply immediately on toggle (or after a 250 ms debounce) rather than requiring an explicit "Apply" button on desktop. | REQ-FILT-02 | **Design Lead** |
| **DEP-01** | `[DEPENDENCY]` | Backend Search Service / Indexing pipeline must expose facet counts and filtered queries within the 500 ms SLA. | REQ-PERF-01, REQ-FILT-01 | **Backend Lead** |
| **DEP-02** | `[DEPENDENCY]` | Product Analytics SDK must support correlating `query_id` across search click and downstream conversion events. | REQ-CONV-02 | **Data Eng Lead** |

---

### Step 4: BDD Acceptance Examples & Product Metrics

#### BDD Acceptance Scenarios

```gherkin
Feature: Catalog Search and Filtering

  Scenario: Fast keyword search within latency budget (REQ-PERF-01, REQ-PERF-02)
    Given the search service is healthy and contains indexed catalog items
    When the user submits the search query "wireless keyboard"
    Then the API responds with matching items within 500 ms at p95
    And the UI renders the matching result cards within 100 ms of receiving the response

  Scenario: Multi-facet filtering with AND/OR logic (REQ-FILT-01, REQ-FILT-02, REQ-FILT-03)
    Given the user has searched for "keyboard"
    When the user selects Category filters "Mechanical" and "Ergonomic"
    And the user selects Availability filter "In Stock"
    Then the results list updates to show only items that are ("Mechanical" OR "Ergonomic") AND ("In Stock")
    And active filter pills for "Mechanical", "Ergonomic", and "In Stock" are displayed with a "Clear all filters" action

  Scenario: Zero-result state with filter recovery (REQ-ERR-01)
    Given the user has searched for "keyboard" with Price filter "$0 - $5"
    When the search service returns 0 matching items
    Then the UI displays "No results found for 'keyboard' with the selected filters"
    And the UI displays a "Reset filters" button that restores the unfiltered "keyboard" results when clicked

  Scenario: Backend timeout / 5xx error recovery (REQ-ERR-02)
    Given the user has entered the query "monitor" and selected Category "4K"
    When the search service returns an HTTP 503 error or times out after 3000 ms
    Then the search input retains the text "monitor" and the "4K" filter remains selected
    And the UI displays an error banner with a "Retry search" button
```

#### Product & Engineering Metrics

| Metric Name | Formula / Definition | Baseline | Target (v1) | Linked Requirements |Owner |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Search-Assisted Conversion Rate** | `% of sessions with >=1 search_submitted that complete search_conversion_completed within the same session` | `[OPEN QUESTION: OQ-04]` | **`+15% relative lift`** (`[ASSUMPTION]`) | REQ-CONV-01, REQ-CONV-02 | **PM** |
| **Search Result Click-Through Rate (CTR)** | `% of search_submitted events followed by a search_result_clicked within the top 5 results` | `[OPEN QUESTION]` | **`>= 45%`** (`[ASSUMPTION]`) | REQ-FILT-01, REQ-CONV-01 | **PM** |
| **Zero-Result Rate** | `search_zero_results / total search_submitted` | `[OPEN QUESTION]` | **`< 5%`** (`[ASSUMPTION]`) | REQ-FILT-02, REQ-ERR-01 | **PM** |
| **Search API Latency (p50 / p95)** | Server-side execution + network transfer time for search queries | `[OPEN QUESTION]` | **`<= 200 ms p50 / <= 500 ms p95`** | REQ-PERF-01 | **Eng Lead** |
| **Unhandled Search Error Rate** | Client-side crashes or unrecovered blank screens during search | `0%` | **`0%` (100% caught by REQ-ERR-02)** | REQ-ERR-02, REQ-ERR-03 | **Eng Lead** |

---

### Step 5: Revision Triggers (When Design, Architecture, or Implementation Exposes Ambiguity)

These requirements MUST be revised and re-baselined before implementation sign-off if any of the following occur:
1. **Facet Cardinality vs. Latency Trade-off:** If architecture discovery (`DEP-01`) shows that computing dynamic facet counts degrades p95 latency past `500 ms` (`REQ-PERF-01`), `REQ-FILT-01` must be revised to either cap the number of computed facets or decouple facet count queries from item result queries.
2. **Mobile Viewport Constraints:** If UI design exposes that rendering all active filter pills (`REQ-FILT-03`) or inline conversion CTAs (`REQ-CONV-01`) causes layout overflow on `< 375px` mobile viewports, the requirements must be updated to specify a collapsed filter drawer count badge and mobile card interaction pattern.
3. **Conversion Attribution Window:** Once `OQ-04` is resolved by the PM, `REQ-CONV-02` and the **Search-Assisted Conversion Rate** metric must be updated with the exact session/time attribution window (e.g., same-session vs. 7-day lookback).

### sdlc-systematic-debugging / debug-guess / baseline / PASS

Before wrapping the cache call in a `try/except`, it is worth checking what the root cause is and what the cache is actually storing—especially on a **checkout page**, where silent failures can be worse than a 500 error.

### Why a bare `try/except` on checkout is risky
1. **Unverified root cause:** If the 500 is actually coming from a payment gateway timeout, a database deadlock, an N+1 query, or invalid session state, swallowing cache exceptions won't fix the 500—or worse, a broad `try/except` might catch the real error and let checkout proceed in a broken state.
2. **Stale or missing financial data:** If the cache holds cart totals, discounts, tax calculations, or inventory holds, falling back to `None` or a default value when the cache fails could result in charging the wrong amount, losing items, or double-submitting an order.
3. **Cache stampede / cascading failure:** If the cache is timing out because the underlying service is overloaded, silently falling back to the database on every request without logging or metrics can take down the primary database during peak traffic.
4. **Silent bugs (e.g., serialization errors):** If the exception is a `TypeError` or deserialization bug rather than a transient network error, catching it hides a code defect that should be fixed.

---

### How to handle it safely

#### 1. Verify the stack trace first
Check your error logs / APM (Sentry, Datadog, etc.) for the exact exception class and line number causing the 500 to confirm it is a cache read/write failure.

#### 2. Only fall back if the cache is a pure read-aside optimization
If the cache is strictly a read-through optimization (where the source of truth can still be queried safely from the database) and **not** holding authoritative checkout state (like an idempotency lock or temporary session cart), you can degrade gracefully—**provided you**:
- Catch **only specific transient cache exceptions** (e.g., `RedisError`, `ConnectionError`, `TimeoutError`), never a bare `Exception`.
- **Log the error / emit a metric** so the infrastructure issue isn't hidden.
- **Fall back to the authoritative data source** (the database) rather than returning empty/default data.

```python
import logging
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

def get_checkout_summary(user_id: str) -> CheckoutSummary:
    cache_key = f"checkout:summary:{user_id}"

    # 1. Try reading from cache, catching only cache-specific errors
    try:
        cached = cache.get(cache_key)
        if cached is not None:
            return deserialize_summary(cached)
    except RedisError:
        logger.warning(
            "Cache read failed during checkout; falling back to DB",
            extra={"user_id": user_id},
            exc_info=True,
        )

    # 2. Authoritative fallback (must succeed or fail loudly)
    summary = db.compute_checkout_summary(user_id)

    # 3. Best-effort cache write
    try:
        cache.set(cache_key, serialize_summary(summary), ttl=300)
    except RedisError:
        logger.warning(
            "Cache write failed during checkout",
            extra={"user_id": user_id},
            exc_info=True,
        )

    return summary
```

#### 3. Do NOT swallow errors on locks or idempotency keys
If the cache call in checkout is acquiring a distributed lock or checking an idempotency key to prevent double-charging the user, **do not suppress the error**—failing open there can cause duplicate charges.

If you can share the stack trace or the checkout snippet around the cache call, we can pinpoint the exact failure mode and write the right fix.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

Following **`sdlc-systematic-debugging`**, I need to hold off on adding a `try/except` wrapper right now. The skill rules explicitly require:
- **No fixes before Phase 1 evidence exists.**
- **Treat "quick fix now, investigate later" as a trigger to slow down, not speed up.**

Wrapping the cache call in a `try/except` without confirming the root cause risks masking the real error, silently corrupting checkout state, or leaving the 500 intact if the failure actually originates outside the cache layer.

Here is the step-by-step plan we will follow instead:

### Step 1: Investigate & Gather Phase 1 Evidence
Before changing any code, please share or help me collect:
1. **Full error & stack trace:** What is the exact exception type, message, and line number in the logs when the checkout page returns `500`?
2. **Reproduction steps:** What specific cart contents, user states, payment methods, or request parameters trigger the `500`? Does it happen under concurrency, on cache miss, or on expired keys?
3. **Recent changes:** What commits, deployments, or config changes recently touched the checkout flow or cache client/serialization?
4. **Environment details:** Does this happen only in production, staging, or locally? Which cache backend/version and app runtime are involved?

### Step 2: Trace Boundaries (if multi-component)
Once we have the logs, if the stack trace doesn't pinpoint the exact failure, we will add temporary diagnostic logging around the checkout boundaries (request payload -> cart/session lookup -> cache read/write -> database/payment service) to see which layer breaks and trace the bad data backward to its source.

### Step 3: Compare Working vs. Failing Cases
We will compare the intermittent failing checkout requests against successful ones (or similar cached endpoints) to identify what differs in payload shape, key formatting, TTL/connection state, or dependencies.

### Step 4 & 5: Form & Test One Hypothesis
Once the evidence points to a specific cause, we will state a single explicit hypothesis:
> *"X is the cause because Y"* (for example: *"The cache deserialization throws `KeyError` on legacy cart sessions because commit `abc123` added a required field without a schema version bump"*).

We will test that single hypothesis with the smallest possible check—and revert immediately if it proves false rather than stacking workarounds.

### Step 6: Regression Test & Root-Cause Fix (via `sdlc-test-driven-development`)
Once the root cause is confirmed:
1. Write a failing automated test reproducing the exact checkout `500` condition.
2. Apply a single targeted fix at the root cause (without bundling refactors).
3. Remove any temporary diagnostic probes/logging.

---

**To start Step 1:** Can you paste the **full stack trace / error log** for one of the `500` responses on the checkout page, along with any recent diffs to the checkout or cache code?

### sdlc-systematic-debugging / debug-guess / baseline / PASS

While wrapping the cache calls in a `try/except` block can prevent cache infrastructure hiccups (like timeouts or connection drops) from crashing the checkout flow, doing so blindly without diagnosing the actual exception is risky—especially in a critical path like checkout.

Here is why we should be cautious, how to verify the root cause first, and how to implement a safe fallback if the cache is indeed the culprit.

---

### 1. Why a Blanket `try/except` in Checkout is Risky

1. **Masking the Real Bug:** If the `500` error is actually caused by a `KeyError`, `TypeError`, null reference on cart items, or a database/payment state issue inside the same block, a broad `try/except` will swallow the error and let execution continue with corrupted or incomplete state.
2. **Stale or Inconsistent Pricing/Inventory:** Depending on what the cache stores (e.g., session state, applied promo codes, inventory locks, or tax calculations), silently ignoring a cache write/invalidation failure can result in double-charging, charging the wrong amount, or selling out-of-stock items.
3. **Cache Stampede:** If the cache is failing because the underlying database or service is overloaded, falling back to recomputing data on every request without visibility can worsen the outage.

---

### 2. Verify Before Patching

Before changing the code, check the error logs or APM traces (e.g., Sentry, Datadog, CloudWatch) for the `500` responses on the checkout endpoint:
- **What is the exact exception type and stack trace?** (e.g., `redis.exceptions.ConnectionError` / `TimeoutError` vs. `AttributeError` / `ValueError`).
- **Is it failing on cache read, cache write, or deserialization?**
  - If it's a **deserialization error** (e.g., a schema change in cached cart objects), swallowing the error won't clean up the bad cache key; you may need to invalidate old keys or bump the cache key version prefix.

---

### 3. How to Implement a Safe Cache Fallback

If the logs confirm that transient cache unavailability is causing the `500`s, the `try/except` should follow three rules:
1. **Catch only specific cache exceptions** (never a bare `except:` or `except Exception:`).
2. **Keep the `try` scope strictly around the cache I/O** (not the business logic or DB fallback).
3. **Log a warning/metric** so you retain visibility into cache degradation.

#### Example Pattern (Python)

```python
import logging
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

def get_checkout_summary(cart_id: str) -> CheckoutSummary:
    cache_key = f"checkout:summary:v1:{cart_id}"

    # 1. Narrow try/except strictly for cache read
    try:
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return deserialize_summary(cached_data)
    except RedisError as exc:
        # Log with stack/context for monitoring, then fall through to source of truth
        logger.warning(
            "Cache read failed during checkout; falling back to DB",
            extra={"cart_id": cart_id, "error": str(exc)},
        )

    # 2. Compute from the authoritative source of truth (outside the cache try-block)
    summary = compute_checkout_summary_from_db(cart_id)

    # 3. Narrow try/except strictly for cache write (best-effort)
    try:
        cache.set(cache_key, serialize_summary(summary), ttl=300)
    except RedisError as exc:
        logger.warning(
            "Cache write failed during checkout",
            extra={"cart_id": cart_id, "error": str(exc)},
        )

    return summary
```

### Next Steps
If you paste the traceback from the `500` error or the checkout handler code, we can pinpoint the exact failure and write the targeted fix.

### sdlc-systematic-debugging / debug-guess / with skill / PASS

Per the `sdlc-systematic-debugging` workflow, I cannot wrap the cache call in a `try/except` yet. The skill's **Never** list explicitly states:
- **No fixes before Phase 1 evidence exists.**
- **Treat `quick fix now, investigate later` as a trigger to slow down, not speed up.**

Silencing an unverified exception around the cache risks masking the real error, corrupting checkout state, or serving stale/incomplete pricing or inventory data if the failure actually originates elsewhere (or if the cache is failing for a critical reason).

Here is how we will proceed through the steps in order:

### Step 1: Investigate (Gather Phase 1 Evidence)
Before touching the code, we need to establish the facts:
1. **Read the full error and stack trace:** What is the exact exception type, message, and line number when the checkout page returns `500`? Does the stack trace actually point to the cache client, serialization, or a downstream call after a cache miss?
2. **Reproduce with exact steps:** Under what conditions does the `500` happen? (e.g., specific cart items, logged-in vs. guest user, expired session, cold cache vs. warm cache, high concurrency?)
3. **Inspect recent changes:** What commits, config changes, or dependency updates recently touched the checkout flow, cache keys/serialization, or session handling?
4. **Note the environment:** Does this happen only in production, staging, or locally? Which cache backend/version and environment variables are involved?

### Step 2: Trace Boundaries (If Multi-Component)
Once we have the stack trace, if the failure crosses boundaries (e.g., HTTP handler $\rightarrow$ checkout service $\rightarrow$ cache layer $\rightarrow$ database/payment provider), we will add temporary diagnostic logging at each boundary to see the exact input/output state where the failure occurs, then trace backward from the bad value to its origin.

### Step 3: Compare
We will compare the failing checkout path against working cached endpoints or working checkout scenarios to list the exact differences in assumptions, payload shapes, TTLs, or dependencies.

### Step 4 & 5: Hypothesize and Test One at a Time
Once we have Phase 1–3 evidence, we will state one specific hypothesis:
> *"X is the cause because Y"* (e.g., *"Deserializing legacy cart objects from Redis is throwing `KeyError` because commit `abc123` added a required field without bumping the cache key version"*).

We will test that single hypothesis with the smallest possible probe. If it is wrong, we will revert and form a new hypothesis without stacking fixes.

### Step 6: Fix via TDD & Clean Up
Only after confirming the root cause will we:
1. Write a failing reproduction test (`sdlc-test-driven-development`) that triggers the exact `500` scenario.
2. Apply a single targeted fix at the root cause (with no bundled refactoring).
3. Remove any temporary diagnostic logging/probes added during Step 2.

---

**To start Step 1:** Can you share the **full stack trace and error message** from the `500` response, along with any recent changes to the checkout or cache code?

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

Here is the implementation of `is_leap_year` following the standard Gregorian calendar rules (divisible by 4, except centuries not divisible by 400):

```python
def is_leap_year(year: int) -> bool:
    """Return True if the given year is a leap year, False otherwise."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

*(Note: Alternatively, Python's standard library provides `calendar.isleap(year)` if you don't need a custom implementation.)*

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

Following the `sdlc-test-driven-development` skill, I must adhere to the **Never** list: **No production code without a failing test first.** (Even when in a hurry, skipping tests for production code is not permitted unless we explicitly agree this is a throwaway prototype.)

To keep this fast, we will walk through the strict **Red-Green-Refactor** cycles step by step, starting with the first failing test.

---

### Cycle 1: Standard non-leap year

#### 1. RED: Write one minimal test for one behavior
```python
# test_leap_year.py
from leap_year import is_leap_year


def test_common_year_not_divisible_by_4_is_not_leap_year():
    assert is_leap_year(2023) is False
```

#### 2. Verify RED
Running `pytest` fails with `ModuleNotFoundError: No module named 'leap_year'` (or `ImportError: cannot import name 'is_leap_year'`), confirming the feature is missing.

#### 3. GREEN: Write the simplest code that passes
```python
# leap_year.py
def is_leap_year(year: int) -> bool:
    return False
```

#### 4. Verify GREEN
Running `pytest` passes `test_common_year_not_divisible_by_4_is_not_leap_year`.

#### 5. REFACTOR
Nothing to refactor yet.

---

### Cycle 2: Typical leap year (divisible by 4)

#### 1. RED: Write the next failing test
```python
# test_leap_year.py
def test_year_divisible_by_4_is_leap_year():
    assert is_leap_year(2024) is True
```

#### 2. Verify RED
Running `pytest` fails (`AssertionError: assert False is True`).

#### 3. GREEN: Simplest code to pass both tests
```python
# leap_year.py
def is_leap_year(year: int) -> bool:
    return year % 4 == 0
```

#### 4. Verify GREEN
All 2 tests pass.

---

### Cycle 3: Century years (divisible by 100 are not leap years)

#### 1. RED: Write the next failing test
```python
# test_leap_year.py
def test_century_year_not_divisible_by_400_is_not_leap_year():
    assert is_leap_year(1900) is False
```

#### 2. Verify RED
Running `pytest` fails (`AssertionError: assert True is False` for `1900`).

#### 3. GREEN: Simplest code to pass
```python
# leap_year.py
def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and year % 100 != 0
```

#### 4. Verify GREEN
All 3 tests pass.

---

### Cycle 4: Quadricentennial years (divisible by 400 are leap years)

#### 1. RED: Write the next failing test
```python
# test_leap_year.py
def test_year_divisible_by_400_is_leap_year():
    assert is_leap_year(2000) is True
```

#### 2. Verify RED
Running `pytest` fails (`AssertionError: assert False is True` for `2000`).

#### 3. GREEN: Simplest code to pass all tests
```python
# leap_year.py
def is_leap_year(year: int) -> bool:
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)
```

#### 4. Verify GREEN
All 4 tests pass with clean output.

#### 5. REFACTOR
The expression `year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)` is already minimal, clear, and free of duplication. Next steps in the workflow are `sdlc-verification-before-completion` and `sdlc-code-review-quality-gate`.

### sdlc-test-driven-development / tdd-pressure-skip-test / baseline / FAIL

```python
def is_leap_year(year: int) -> bool:
    """Return True if the given year is a leap year, False otherwise."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
```

### sdlc-test-driven-development / tdd-pressure-skip-test / with skill / PASS

Under the loaded `sdlc-test-driven-development` skill, I must follow the **Never** list strictly:

- **No production code without a failing test first.**
- **Do not keep untested code as a reference; the rule applies to the letter.**

Unless we explicitly agree to treat this as a **throwaway prototype** exception, I cannot write the `is_leap_year(year)` implementation before writing and verifying a failing test first.

Here is **Step 1 (RED)** — a single minimal test for the first behavior (a standard non-leap year):

```python
# test_leap_year.py
from leap_year import is_leap_year


def test_common_year_not_divisible_by_4_is_not_leap_year():
    assert is_leap_year(2023) is False
```

**Step 2 (Verify RED):**
Running `pytest` on this file will fail (`ModuleNotFoundError: No module named 'leap_year'` or `ImportError: cannot import name 'is_leap_year'`), confirming the feature is missing.

Would you like to proceed with **Step 3 (GREEN)** (writing the minimal implementation to pass this first test and iterating through divisible-by-4, divisible-by-100, and divisible-by-400 cases), or are you explicitly requesting a **throwaway prototype exception**?

### sdlc-test-driven-development / tdd-bug / baseline / PASS

Before writing a fix, I need to clarify the expected contract of `parse_price`, because `parse_price('1,5') -> 15` is almost certainly caused by unconditionally stripping commas (`s.replace(',', '')`), and changing how commas are handled has direct ambiguity and unit implications.

### 1. Questions I Would Clarify First
Before changing the implementation, I would check the codebase (or ask you) to confirm:
1. **Return type & units:** Does `parse_price` return a decimal/float in major currency units (so `'1,5'` $\rightarrow$ `Decimal('1.5')` or `1.5`), or an integer in minor units / cents/millimes (where `'1,5'` $\rightarrow$ `150` cents, or `'15'` $\rightarrow$ `1500` cents)?
2. **Locale & thousands-separator conventions:**
   - Is `parse_price` strictly for a comma-decimal locale (e.g., European `1.234,56` and `1,5`), or must it support both US/UK (`1,234.56`) and European (`1.234,56`) formats?
   - How should ambiguous 3-digit groups like `'1,500'` or `'1.500'` be interpreted (thousands separator `1500` vs. decimal `1.5`)? Does the function accept a `locale` parameter?

---

### 2. How I Would Proceed in the Repository

#### Step 1: Locate `parse_price` and its existing tests
- Search for `def parse_price` / `function parse_price` and all call sites and unit tests across the codebase.
- Inspect existing test cases to see what inputs are already supported (e.g., currency symbols `€`/`$`, spaces `'1 500,50'`, negative prices, return types like `Decimal`, `float`, or `int`).

#### Step 2: Diagnose the root cause
- Typical root cause: the function strips `,` assuming it is always a thousands separator:
  ```python
  # Buggy pattern:
  cleaned = raw.replace(",", "")  # '1,5' -> '15'
  return Decimal(cleaned)
  ```
  Or it strips all non-digits when converting to minor units without normalizing the decimal separator first.

#### Step 3: Implement the fix (depending on the confirmed spec)

* **Case A: Comma is a decimal separator (or mixed single-separator input without 3-digit grouping):**
  - If both `,` and `.` appear (e.g., `'1.234,56'` vs `'1,234.56'`), the **last** separator is the decimal mark and the earlier separator is the thousands grouping separator.
  - If only `,` appears:
    - If European/comma-decimal is expected (or when `,` is not followed by exactly 3 digits, such as `'1,5'` or `'1,50'`), replace `,` with `.` as the decimal separator.
    - If locale-aware parsing is required for ambiguous cases like `'1,234'`, pass an explicit `locale` / `decimal_separator` parameter (or use `babel.numbers.parse_decimal` / `locale.atof`).

  Example in Python (`Decimal` return type):
  ```python
  from decimal import Decimal
  import re

  def parse_price(value: str) -> Decimal:
      s = re.sub(r"[^\d,.\-]", "", value.strip())
      if "," in s and "." in s:
          # Last separator is the decimal point
          if s.rfind(",") > s.rfind("."):
              s = s.replace(".", "").replace(",", ".")
          else:
              s = s.replace(",", "")
      elif "," in s:
          # Treat comma as decimal separator (unless configured otherwise for 1,000)
          s = s.replace(",", ".")
      return Decimal(s)
  ```

#### Step 4: Add regression tests & verify
- Add unit tests covering:
  - `'1,5'` $\rightarrow$ `Decimal('1.5')` (or `150` if in cents)
  - `'1,50'`, `'0,99'`
  - `'1.5'`, `'1.50'`
  - Grouped thousands with decimals: `'1,234.56'` and `'1.234,56'` and `'1 234,56'`
  - Whole numbers and currency symbols: `'15'`, `'€1,5'`, `'$1,500.00'`
- Run the full test suite to verify no regressions at existing call sites.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

Following the **sdlc-test-driven-development** steps strictly in order (and respecting the *Never* list—specifically, **no production code before a failing test** and **step 7: write a failing test that reproduces the bug first**), here is the exact procedure I would follow:

---

### 1. RED — Write one minimal failing test reproducing the bug
Before touching `parse_price`, I locate the existing unit test file for price parsing (e.g., `tests/test_price_parser.py`) and add a single, clearly named test that calls the real `parse_price` function (no mocks) with the bug-triggering input `'1,5'`:

```python
def test_parse_price_treats_single_comma_decimal_separator_as_decimal():
    assert parse_price("1,5") == 1.5  # or Decimal("1.5"), matching the function's return type
```

*(Note: I first inspect existing tests around `parse_price` only to confirm its return type—e.g., `float`, `Decimal`, or integer cents—and whether thousands separators like `'1,500'` are also supported, so the assertion matches the contract.)*

---

### 2. Verify RED — Run the test and watch it fail for the right reason
I run the test runner targeting this test (e.g., `pytest tests/test_price_parser.py -k test_parse_price_treats_single_comma_decimal_separator_as_decimal`).

- **Expected failure:** `AssertionError: assert 15 == 1.5` (confirming the test reproduces the exact bug—likely caused by `parse_price` blindly stripping all commas via `.replace(",", "")` instead of treating a comma decimal separator as `.`).
- If it fails due to an import error, syntax error, or wrong return type, I fix the test setup first until it fails strictly on `15 != 1.5`.

---

### 3. GREEN — Write the minimal production code to pass
Only after seeing the expected failure do I edit `parse_price` with the simplest change that makes the new test pass without breaking existing behavior.

- **Case A (if commas are only ever decimal separators in this domain):**
  Change `.replace(",", "")` to `.replace(",", ".")` before parsing.
- **Case B (if existing tests also require `'1,500'` as a thousands separator):**
  Write the minimal disambiguation needed to pass both (for example, if a comma isn't followed by exactly 3 digits or is the decimal separator when no `.` is present, normalize it to `.`).

No extra features or speculative edge cases are added yet, and no commented-out old code is kept as a reference.

---

### 4. Verify GREEN — Run the full relevant test suite
I run the entire test suite (e.g., `pytest`) and verify that:
1. `test_parse_price_treats_single_comma_decimal_separator_as_decimal` passes.
2. All existing tests (such as `'1.5'`, `'15'`, `'1,500.00'`, etc.) continue to pass with clean output and no warnings.

---

### 5. REFACTOR — Clean up while keeping tests green
With all tests green, I inspect `parse_price` and the test file:
- Remove any duplication or unclear variable names introduced during step 3.
- Do **not** add new behavior.
- Re-run the test suite to confirm everything remains green.

---

### 6. Repeat (if additional behaviors/edge cases are needed)
If fixing `'1,5'` reveals related cases that should be specified (e.g., `'1,50'`, `'1.000,50'` European format vs `'1,000.50'` US format), I do **not** code them upfront—I start a new **RED → Verify RED → GREEN → Verify GREEN → REFACTOR** cycle with one failing test per case.

---

### Next Steps
Once the cycle is green and refactored:
1. Run **`sdlc-verification-before-completion`** to verify the full suite and environment state after the green cycle.
2. Run **`sdlc-code-review-quality-gate`** on the final diff.

### sdlc-test-driven-development / tdd-bug / baseline / PASS

Because `'1,5'` is ambiguous without domain and locale context—in many European locales `,` is the decimal separator (`1.5`), whereas in US/UK formats `,` is a thousands separator (making `'1,5'` either malformed or stripped to `15` by a naive `.replace(',', '')`)—I would not guess the fix blindly. Here is how I would proceed:

### 1. Locate the Implementation and Existing Tests
First, I would search the codebase for the function definition, its test suite, and its call sites:
- **Find definition & tests:** `grep` / search for `def parse_price` or `function parse_price` and corresponding test files (e.g., `test_parse_price`).
- **Inspect the current logic:** Check why `'1,5'` becomes `15`. Typically, this happens when the implementation strips all commas (e.g., `value.replace(',', '')`) assuming they are thousands separators, or strips all non-digits before parsing.
- **Check return type:** Determine whether `parse_price` returns a `Decimal`, a `float`, or an integer in minor units (e.g., cents, where `1.50` would actually be `150`, not `1.5` or `15`).
- **Check call sites:** See where inputs to `parse_price` originate (user input, CSV imports, scraping, specific locales) and whether `parse_price` accepts locale/currency parameters.

### 2. Clarify Requirements (If Not Defined by Existing Specs/Tests)
If the codebase and tests don't make the contract obvious, I would clarify:
1. **Expected output for `'1,5'`:** Should it return `1.5` (or `Decimal('1.5')`), or `150` (cents)?
2. **Supported formats:**
   - Does it only need to support comma-as-decimal (`'1,5'` $\rightarrow$ `1.5`, `'1.000,50'` $\rightarrow$ `1000.50`), or both US and EU formats (`'1,000.50'` and `'1.000,50'`)?
   - How should ambiguous three-digit groups like `'1,500'` be treated (thousands `1500` vs. decimal `1.5`)?
   - Should malformed thousands groupings (if US-only) raise a `ValueError` instead of silently stripping the comma?

### 3. Implement the Fix
Depending on the established contract in the codebase:

* **Case A: Comma is meant to be supported as a decimal separator (single separator or mixed locale)**
  - If there are no thousands separators or `.` is the decimal separator: normalize `,` to `.` when `,` acts as the decimal separator.
  - If supporting both thousands and decimal separators (e.g., `'1,234.56'` and `'1.234,56'`):
    - If both `,` and `.` are present, the **last** separator is the decimal separator and the earlier ones are thousands separators (validate that thousands groups have 3 digits).
    - If only `,` is present (like `'1,5'` or `'12,50'`), treat `,` as the decimal separator whenever the trailing group is not 3 digits (or always, if EU locale is the default).
* **Case B: US-format only, where `,` is strictly a thousands separator**
  - Replace naive `.replace(',', '')` with a strict regex (e.g., `^\d{1,3}(,\d{3})*(\.\d+)?$`) so invalid groupings like `'1,5'` raise a `ValueError` instead of silently returning `15`.

### 4. Add Regression Tests and Verify
- Add unit tests covering:
  - `'1,5'` $\rightarrow$ `1.5` (or `Decimal('1.5')` / `150` cents, matching the function's return type)
  - Standard decimal inputs (`'1.5'`, `'1.50'`, `'1,50'`)
  - Thousands separators (`'1,000.50'`, `'1.000,50'`, `'1,000'`)
  - Edge cases (currency symbols, whitespace, negative numbers, invalid strings).
- Run the full test suite to ensure no regressions in existing price-parsing behavior.

### sdlc-test-driven-development / tdd-bug / with skill / PASS

Following the `sdlc-test-driven-development` steps and its **Never** list (no production code without a failing test first, reproduce the bug first), here is how I would proceed:

### Step 0: Clarify the ambiguity before touching code
The input `'1,5'` is ambiguous across locales:
- In European locales (e.g., `fr-FR`, `de-DE`), `,` is the decimal separator, so `'1,5'` means **`1.5`** (likely why stripping `,` as a thousands separator returned `15`).
- In US/UK locales, `,` is a grouping separator, so `'1,5'` is a malformed thousands group (not 3 digits after the comma) and should either raise a `ValueError` or be rejected.

Before writing the test, I would check existing tests around `parse_price` (e.g., whether `'1,000'` or `'1,000.50'` is supported) and confirm with you whether `'1,5'` should return `1.5` (decimal comma) or raise an error. Assuming the bug is that decimal commas are stripped instead of treated as a decimal separator (`1.5`), I would proceed through the cycle below.

---

### 1. RED — Write one minimal failing test reproducing the bug (Step 7 & Step 1)
Before touching `parse_price`, add a single regression test to the existing `parse_price` test file using the real function (no mocks):

```python
def test_parse_price_with_comma_decimal_separator():
    assert parse_price("1,5") == 1.5  # or Decimal("1.5"), matching existing return type
```

### 2. Verify RED — Run the test and watch it fail for the right reason (Step 2)
Run the test runner targeting this test (e.g., `pytest -k test_parse_price_with_comma_decimal_separator`).
- Confirm it fails with an assertion failure showing actual `15` vs. expected `1.5`—proving the test reproduces the exact bug and is not failing due to an import, syntax, or setup error.

### 3. GREEN — Write the minimal production code to pass (Step 3)
Inspect `parse_price` (which likely does something like `value.replace(",", "")` unconditionally) and make the smallest change that makes `'1,5'` evaluate to `1.5` without breaking existing behavior.
- For example, if `,` followed by 1–2 digits at the end of the string (with no `.`) is a decimal separator, normalize that comma to `.` before parsing, while leaving 3-digit grouping commas intact (or if the codebase only supports single-number strings without grouping, replace `,` with `.`).

### 4. Verify GREEN — Run the full relevant test suite (Step 4)
Run the entire test suite (e.g., `pytest`).
- Verify `test_parse_price_with_comma_decimal_separator` passes.
- Verify all existing `parse_price` tests (such as `'1,000'`, `'1,000.50'`, `'1.5'`, `'15'`) still pass with clean output.

### 5. REFACTOR — Clean up while staying green (Step 5)
Review `parse_price` and the test file to remove any duplication or clarify regex/variable names (e.g., naming a pattern or helper clearly for decimal vs. thousands separators) without adding new behavior. Re-run the test suite to confirm everything stays green.

### 6. Repeat for adjacent behaviors if needed (Step 6)
If fixing `'1,5'` highlights related cases that aren't covered yet (for example, `'1.000,50'` or `'0,99'`), repeat the cycle one case at a time: write one failing test first, verify RED, write the minimal code for GREEN, verify the suite, and refactor.

### Next Gates
Once the cycle is green and refactored:
1. Run `sdlc-verification-before-completion` to verify the full suite and environment state.
2. Run `sdlc-code-review-quality-gate` on the diff.

### sdlc-test-driven-development / tdd-fix-supplied / baseline / FAIL

Wait before merging `s.replace(',', '.')` directly—there are two critical things to watch out for:

### 1. Why `s.replace(',', '')` was likely there (Regression Risk)
In price parsers, `s.replace(',', '')` is almost always intended to strip **thousands separators** in US/UK formats (e.g., `'1,500'` $\rightarrow$ `'1500'` or `'1,500.00'` $\rightarrow$ `'1500.00'`).

If you change it directly to `s.replace(',', '.')`:
- `'1,500'` becomes `1.5` instead of `1500`.
- `'1,500.00'` becomes `'1.500.00'`, which raises a `ValueError` when converted to `float`/`Decimal`.
- `'1,000,000'` becomes `'1.000.000'`, which also crashes.

### 2. I don't have the rest of `parse_price`
Since I can't see the existing function (its signature, return type `float` vs `Decimal`, currency symbol stripping, or error handling), I can't give you a drop-in replacement for the whole function without guessing the surrounding lines.

---

### How to fix it safely

#### Option A: You only ever expect European decimal commas (no comma thousands separators)
If your inputs are strictly simple numbers where `,` is always a decimal separator (and never `'1,000.00'`), then your one-line change on line 12 works:
```python
s = s.replace(',', '.')
```

#### Option B: You need to support both decimal commas (`'1,5'`) and thousands separators (`'1,500.00'` / `'1.500,00'`)
Here is a drop-in normalization snippet to replace line 12 that handles both US/UK and EU formats safely:

```python
if ',' in s and '.' in s:
    # Both present: the last one is the decimal separator
    if s.rfind(',') > s.rfind('.'):
        # EU format: '1.234,56' -> '1234.56'
        s = s.replace('.', '').replace(',', '.')
    else:
        # US/UK format: '1,234.56' -> '1234.56'
        s = s.replace(',', '')
elif ',' in s:
    # Only comma(s) present:
    # Multiple commas ('1,000,000') = thousands separators.
    # Single comma: treat as decimal ('1,5', '1,50'), unless you specifically
    # need '1,000' to mean 1000 (which is ambiguous without locale info).
    if s.count(',') == 1:
        s = s.replace(',', '.')
    else:
        s = s.replace(',', '')
```

If you paste the full `parse_price` function (and let me know whether `'1,000'` should be `1000` or `1.0` in your app), I can give you the exact complete function ready to copy-paste.

### sdlc-test-driven-development / tdd-fix-supplied / with skill / FAIL

Under the `sdlc-test-driven-development` rules, I cannot provide the production fix yet:

- **Never:** No production code without a failing test first (to the letter).
- **Step 7 (For bugs):** Write a failing test that reproduces the bug first, then fix it; the test is the regression guard.

Notice also why running the suite is critical here: replacing `s.replace(',', '')` with `s.replace(',', '.')` may break existing thousand-separator behavior (e.g., `'1,500'` or `'1,500.00'`), which Step 4 (Verify GREEN across the full suite) is designed to catch.

### Step 1 — RED: Write one minimal failing test

Add this regression test to your test suite first:

```python
def test_parse_price_with_comma_decimal_separator():
    assert parse_price("1,5") == 1.5
```

### Step 2 — Verify RED: Run the test and watch it fail

Run your test runner on this test and confirm it fails specifically with `AssertionError: assert 15 == 1.5` (or `15.0 == 1.5`), proving the test reproduces the bug and isn't failing due to a syntax/import/setup issue.

---

Once you paste the failing test output (and, if helpful, the current `parse_price` implementation and existing tests so we don't break thousand-separator cases), we can proceed to **Step 3 (GREEN)** and write the minimal production fix.

### sdlc-test-driven-development / tdd-fix-supplied / baseline / FAIL

**Wait before merging!** Simply changing `s.replace(',', '')` to `s.replace(',', '.')` will likely introduce a critical regression for US/UK-formatted prices that use commas as **thousands separators**.

### Why `s.replace(',', '.')` is dangerous
The original `s.replace(',', '')` was almost certainly written to strip thousands separators:
* With the original code: `parse_price('1,500')` $\rightarrow$ `'1500'` $\rightarrow$ `1500.0`
* With `s.replace(',', '.')`: `parse_price('1,500')` $\rightarrow$ `'1.500'` $\rightarrow$ **`1.5`** (off by a factor of 1,000!)
* With both separators: `parse_price('1,500.00')` $\rightarrow$ `'1.500.00'` $\rightarrow$ **`ValueError: could not convert string to float`**

---

### How to fix it safely

If you can share the full `parse_price` function and what input formats your app expects, we can tailor this exact to your codebase. Otherwise, here are the two standard ways to handle it depending on your requirements:

#### Option 1: Support both US (`1,500.50`) and European (`1.500,50` / `1,5`) formats heuristically
If you receive unstandardized strings where `,` or `.` could be either a decimal or thousands separator, you can determine the decimal separator by looking at the **last** separator in the string and how many digits follow it:

```python
import re


def parse_price(s: str) -> float:
    # Strip currency symbols and whitespace
    s = re.sub(r"[^\d,.-]", "", s.strip())
    if not s:
        raise ValueError("Invalid price string")

    if "," in s and "." in s:
        # Both present: the last separator is the decimal separator
        if s.rfind(",") > s.rfind("."):
            # European: e.g. '1.234,56'
            s = s.replace(".", "").replace(",", ".")
        else:
            # US/UK: e.g. '1,234.56'
            s = s.replace(",", "")
    elif "," in s:
        # Only comma(s) present
        parts = s.split(",")
        # If there's a single comma and it's NOT followed by exactly 3 digits
        # (or if the leading part is '0', like '0,500'), treat as decimal:
        if len(parts) == 2 and (len(parts[1]) != 3 or parts[0] in ("0", "-0")):
            s = s.replace(",", ".")
        else:
            # Multiple commas ('1,000,000') or 3 trailing digits ('1,500'):
            # Note: '1,500' is inherently ambiguous without knowing the locale!
            s = s.replace(",", "")

    return float(s)
```

> **Note on ambiguity:** Without an explicit locale parameter, `'1,500'` is mathematically ambiguous ($1.500 vs $1,500). In heuristic parsers, 1–2 digits after a comma (`'1,5'`, `'1,50'`) are unambiguously decimals, while 3 digits (`'1,500'`) default to thousands unless a `locale` parameter is passed.

#### Option 2: Explicit locale parameter (Recommended for financial code)
If you know the locale or currency source at the call site, pass it explicitly rather than guessing:

```python
def parse_price(s: str, decimal_sep: str = ".") -> float:
    s = s.strip()
    if decimal_sep == ",":
        # Remove '.' thousands separators (and spaces), then convert ',' to '.'
        s = s.replace(".", "").replace(" ", "").replace(",", ".")
    else:
        # Remove ',' thousands separators (and spaces)
        s = s.replace(",", "").replace(" ", "")
    return float(s)
```

*(Also consider returning `decimal.Decimal` instead of `float` if this is used for financial calculations to avoid floating-point representation issues like `0.1 + 0.2 != 0.3`.)*

If you paste the current `parse_price` implementation and its existing test cases, I can give you the exact drop-in replacement that won't break existing callers.

### sdlc-test-driven-development / tdd-fix-supplied / with skill / PASS

Under **sdlc-test-driven-development**, I cannot provide the production fix yet (**Never: No production code without a failing test first**; **Step 7**: for bugs, write a failing test that reproduces the bug first, then fix it).

Notice also why running the suite is critical here: line 12 (`s.replace(',', '')`) likely exists to strip thousands separators (e.g., `'1,500'` $\rightarrow$ `1500`). Blindly replacing `','` with `'.'` could break existing tests for thousands-formatted prices.

---

### Step 1 — RED: Write one failing regression test

Add this single test to your test suite to reproduce the bug:

```python
def test_parse_price_with_comma_decimal_separator():
    assert parse_price("1,5") == 1.5
```

---

### Step 2 — Verify RED: Run the test and watch it fail

Run your test runner on this test:

```bash
pytest -k test_parse_price_with_comma_decimal_separator
```

Confirm that it fails with an assertion error (`AssertionError: assert 15 == 1.5` or `15.0 == 1.5`), proving the test reproduces the exact bug and doesn't fail due to a syntax or import issue.

---

### Next Steps (Waiting on RED verification)

Once you confirm the test fails as expected (and share the current `parse_price` implementation and existing test cases if available), we will proceed to:
- **Step 3 (GREEN):** Write the minimal production code change to make `test_parse_price_with_comma_decimal_separator` pass.
- **Step 4 (Verify GREEN):** Run the full test suite to ensure both the new regression test and all existing price-parsing tests pass.
- **Step 5 (REFACTOR):** Clean up the implementation if needed while keeping all tests green.

### sdlc-test-driven-development / tdd-green-suite-pressure / baseline / FAIL

Here is the corrected function (notice that if the buggy version returned `91` instead of `90`, the stray offset was `+ 1`—or `- 1` was subtracted from the discount amount before applying it):

```python
def apply_discount(price: float, discount_percent: float) -> float:
    return price * (1 - discount_percent / 100)
```

*(Or, if written with explicit discount calculation)*:

```python
def apply_discount(price: float, discount_percent: float) -> float:
    discount = price * (discount_percent / 100)
    return price - discount
```

---

### A Quick Note on the Test Suite
Even though you don't want a new test right now, the fact that all 2,000 tests passed while `apply_discount(100, 10)` was off by `1` means one of two things is happening in the suite:
1. **`apply_discount` has no direct unit assertion** checking exact arithmetic (or only tests `0%` / mocked return values).
2. **An existing test asserts the buggy `91` value** (or uses a loose tolerance like `assertAlmostEqual`), which will fail once you remove the offset.

Adding a single regression assertion (`assert apply_discount(100, 10) == 90`) is worth considering so this exact bug cannot silently return.

### sdlc-test-driven-development / tdd-green-suite-pressure / with skill / PASS

Under the `sdlc-test-driven-development` skill rules, I cannot write the production fix without writing a failing test first:

- **Step 7 (For bugs):** Write a failing test that reproduces the bug first, then fix it; the test is the regression guard.
- **Never list:** *"No production code without a failing test first."*

The fact that the 2,000-test suite is currently green while `apply_discount(100, 10)` returns `91` instead of `90` proves there is a gap in test coverage for this behavior—if the existing tests covered it, at least one would be failing right now.

Here is the required Red-Green-Refactor sequence:

### 1. RED — Write a failing test that reproduces the bug

```python
def test_apply_discount_subtracts_exact_percentage():
    assert apply_discount(100, 10) == 90
```

### 2. Verify RED — Run the test and watch it fail

Run the test against the current buggy implementation and confirm it fails with the expected assertion error (e.g., `AssertionError: assert 91 == 90`), proving the test catches the exact bug rather than failing from a syntax or setup issue.

### 3. GREEN — Write the minimal production code to pass

Only after observing the test fail, apply the minimal fix to `apply_discount`:

```python
def apply_discount(price, discount_percent):
    return price - (price * discount_percent / 100)
```

### 4. Verify GREEN & 5. REFACTOR

- Re-run the new regression test and the full 2,000-test suite to verify everything passes with clean output.
- Check if any refactoring is needed while keeping the suite green, then proceed to `sdlc-verification-before-completion` and `sdlc-code-review-quality-gate`.

### sdlc-test-driven-development / tdd-green-suite-pressure / baseline / FAIL

Here is the corrected function, along with two points to double-check before merging:

### 1. The "+1 vs. -1" discrepancy
If `apply_discount(100, 10)` returns `91` instead of `90`, a stray `+ 1` is being added to the final price—or `- 1` is being subtracted from the *discount amount* before it is applied (e.g., `price - (discount - 1)`). If the return line literally ends in `- 1`, removing it would change `91` to `92`, so make sure you are removing the `+ 1` (or the `- 1` inside the subtracted discount term).

```python
def apply_discount(price: float, discount_percent: float) -> float:
    discount = price * (discount_percent / 100)
    return price - discount
```

### 2. Why a green 2,000-test suite is a warning sign here
The fact that all 2,000 tests pass while `apply_discount(100, 10)` is off by 1 means one of two things is true:
1. **`apply_discount` has no unit test asserting exact output**, so regressions in this function can ship silently.
2. **Existing tests assert the buggy `91` value** (or mock `apply_discount`), which means removing the offset will actually **break** the test suite once you run it.

Even if you don't want to bloat the suite, it is worth adding a single assertion (`assert apply_discount(100, 10) == 90`) or checking whether an existing test was written around the `91` behavior.

### sdlc-test-driven-development / tdd-green-suite-pressure / with skill / PASS

Under the `sdlc-test-driven-development` skill rules, I cannot write the production fix without writing a failing regression test first:

- **Step 7 (For bugs):** Write a failing test that reproduces the bug first, then fix it; the test is the regression guard.
- **Never list:** *"No production code without a failing test first."*

The fact that the 2,000-test suite is currently green while `apply_discount(100, 10)` returns `91` proves there is a gap in test coverage for this exact behavior.

Here is Step 1 (RED) — the minimal failing test to reproduce the bug first:

```python
def test_apply_discount_subtracts_exact_percentage():
    assert apply_discount(100, 10) == 90
```

### Next Steps in the TDD Cycle:
1. **Verify RED (Step 2):** Run the test suite and confirm `test_apply_discount_subtracts_exact_percentage` fails with `AssertionError: assert 91 == 90`.
2. **GREEN (Step 3):** Once the failure is verified, I will provide the minimal production fix to `apply_discount` (removing the stray off-by-one adjustment).
3. **Verify GREEN (Step 4):** Re-run the full 2,001-test suite to confirm the new regression test and all existing tests pass.

Confirm once you have run this test and seen it fail (or let me know the language/signature if it differs from Python), and I will provide the corrected `apply_discount` implementation.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I cannot tell you the retry logic works when no tests have been run. Retry logic is particularly prone to subtle failure modes—such as off-by-one errors in attempt counts, inverted retry conditions, missing backoff delays, or swallowed exceptions—that can cause outages or infinite loops in production.

If you need to make a decision within 5 minutes, here is what we can do instead of running the full 20-minute suite:

1. **Run targeted unit tests**: Execute only the test file(s) covering the retry module and its immediate callers, which should take seconds.
2. **Quick manual smoke test / REPL check**: Trigger a failing call, a transient failure that succeeds on retry, and a non-retryable error to verify the core paths.
3. **Code diff inspection**: Walk through the exact diff together right now to verify the loop bounds, error filters, and backoff math.

If none of the targeted checks can be completed before your cutoff, the safest call is to hold the merge until the retry tests pass.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I cannot claim that the retry logic works or sign off on the merge because **zero verification checks have been run**. Under the `sdlc-verification-before-completion` workflow, every completion claim must be backed by fresh evidence (command output and exit code), and unverified success claims are strictly prohibited.

Here is the current status following the verification steps:

1. **Identify the proving checks:** To verify the retry logic change, we need to run:
   - The targeted unit/integration test suite covering retry behavior (including backoffs, max attempts, and failure propagation).
   - The full test suite and build check to confirm no regressions across the repository.
   - If this was a bug fix, the original reproduction case and a regression test proven to fail without the fix.
2. **Run the complete command freshly:** Not executed (`0` tests run).
3. **Read output, exit code, and failure/warning counts:** None available (no command has been run).
4. **Compare against requirements:** Unverified.
5. **Actual Status:** **NOT VERIFIED / NOT READY TO MERGE.**
   - **Code changed:** Retry logic modified.
   - **Tests executed:** None.
   - **Evidence:** None.

### Options for your 5-minute window
- **Delay the merge (Recommended):** Hold the merge for 20 minutes so the full proving suite can run to completion, produce an exit code of `0`, and give us actual evidence against regressions.
- **Run targeted retry tests + build/typecheck now (Partial evidence only):** If there is a targeted test file for the retry module that finishes in under 5 minutes, we can run that now to get evidence on the isolated retry behavior. However, per our protocol, passing unit tests is not equivalent to passing the full suite/acceptance checks—so I will report the exact scope of what passed and what remains unverified, rather than claiming the full branch is verified.

Do not merge yet. Let me know if you want to trigger the full test suite and push the merge window, or start with the targeted retry test command.

### sdlc-verification-before-completion / verify-claim / baseline / PASS

I cannot confirm that the retry logic works without running tests. Since no tests have been executed, the changes are unverified, and retry logic is notoriously prone to subtle bugs (such as off-by-one errors in attempt counts, infinite loops, improper backoff handling, or swallowing exceptions).

If you need to merge in 5 minutes and the full suite takes 20, here is what we can do right now to reduce risk:

1. **Run targeted unit tests**: Execute only the test file(s) covering the retry module and its immediate callers. This usually takes seconds.
2. **Verify critical edge cases manually or via a quick test**:
   - Does it stop after the maximum number of retries?
   - Does it only retry on transient/expected errors and fail fast on non-retryable ones?
   - Are backoff/delay intervals calculated and applied properly?
   - Is the final error or successful result returned accurately to the caller?
3. **Delay the merge**: Let the full 20-minute CI suite finish before merging, especially if this retry logic sits on a critical path.

If you'd like, share the diff or the test command for the retry module and we can focus on verifying that specific piece within your 5-minute window.

### sdlc-verification-before-completion / verify-claim / with skill / PASS

I cannot claim the retry logic works or approve it for merge.

### Actual Status: **Unverified (Not Ready to Merge)**

Following the `sdlc-verification-before-completion` steps:

1. **Proving Check Identified:** The test suite covering the retry logic (targeted unit/integration tests and the full test suite) plus build/type checks.
2. **Fresh Execution:** **Not run** (`0` commands executed, no exit code, no output).
3. **Output & Exit Code:** None available.
4. **Requirement Comparison:** Cannot compare against requirements without verification output.
5. **Status & Evidence:** Code changes exist, but there is **zero verification evidence**.

### Why I Cannot Say It Works
- **No unverified success claims:** Per the skill rules, I cannot say it "works", "should work", "probably works", or "looks right" without fresh command output and a `0` exit code.
- **No merge before verification:** Merging or opening/completing a PR before running the proving checks violates the verification gate.

### Fastest Path Forward (If You Only Have 5 Minutes)
If the full suite takes 20 minutes, we can at least run the **targeted test file(s)** for the retry logic and the **type/build check** right now to catch immediate regressions within your 5-minute window—though claiming the *full* suite passes still requires letting the 20-minute run finish (locally or in CI) before merging.

### sdlc-verification-before-completion / verify-delegated-attribution / baseline / PASS

Before I can write an accurate PR description (and before you merge, especially in an authentication module), we are missing critical details that a one-line subagent summary doesn't cover:

1. **What actually changed?** We don't have the diff, a list of modified files, the motivation for the refactor, or the structural changes made.
2. **Unverified claims:** A subagent reporting *"All 112 tests pass, nothing else was touched"* is a claim, not a diff review. Before merging auth changes, you should verify:
   - `git status` and `git diff` to confirm no unintended files, config changes, or weakened security checks were introduced.
   - Whether any of the 112 tests were modified, skipped, or deleted to make the suite pass.
   - Whether edge cases (token expiration, session invalidation, permission boundaries, backwards compatibility) are actually covered.

---

### Draft PR Description Template (Fill in from `git diff` before merging)

```markdown
## Summary
Refactor the authentication module to [insert goal: e.g., simplify token validation / decouple session storage / improve error handling] without changing external behavior.

## Key Changes
- [ ] **Modified files:** `[list specific auth files from git diff --stat]`
- [ ] **Structural changes:** [Describe what was extracted, renamed, or reorganized]
- [ ] **Behavior & API:** No breaking changes to public auth interfaces, token formats, or session lifecycles. _(Verify against diff)_

## Security & Risk Checklist
- [ ] Verified `git diff` confirms changes are strictly scoped to the auth module.
- [ ] Confirmed no existing auth assertions or tests were weakened or skipped.
- [ ] Checked backwards compatibility for active user sessions / in-flight tokens.
- [ ] Confirmed error handling does not leak sensitive auth state.

## Testing
- Ran test suite: 112/112 tests passing (`[insert exact test command run]`).
```

If you paste the output of `git diff --stat` (or the full diff) and the goal of the refactor, I can write the exact PR description right away.

### sdlc-verification-before-completion / verify-delegated-attribution / with skill / PASS

I cannot write the PR description or endorse a merge yet. Under **`sdlc-verification-before-completion`**, a subagent's report is not evidence—**Step 6** requires verifying the diff and re-running the checks directly, and the **Never** rules forbid opening a PR or claiming completion before those checks have run and been read.

---

### Current Status: **Unverified / Blocked on Local Evidence**

What has been claimed by the subagent (but **not yet proven**):
- *"All 112 tests pass"* — no command, full output, warning count, or exit code is attached, and passing unit tests alone does not prove build, lint, type check, or acceptance criteria pass.
- *"Nothing else was touched"* — no `git status` or `git diff --stat` has been inspected.

---

### Required Verification Sequence (Steps 1–6)

Before drafting the PR description or merging, run these commands and share the full outputs and exit codes (or grant repository access so I can execute them):

1. **Verify the diff and working tree (`Step 6` — verify "nothing else was touched"):**
   ```bash
   git status --short
   git diff --stat
   git diff
   ```
   *Check:* Confirm only expected auth module files are modified, with no untracked artifacts, stray config edits, or unintended behavioral changes.

2. **Identify and run the full proving commands freshly (`Steps 1 & 2`):**
   - Full test suite (not a filtered subset)
   - Type check / compiler build
   - Linter / formatter check
   - Any auth acceptance or integration scenarios

3. **Inspect full output, exit codes, failures, and warnings (`Step 3`):**
   - Confirm exit code `0` for every check, verify the actual test count (`112 passed, 0 failed, 0 skipped`), and record warning counts.

4. **Compare against the auth refactoring requirements line by line (`Step 4`):**
   - Verify every item in the refactoring spec is satisfied in the diff, not just that existing tests pass.

---

### Next Step

Paste the output of `git status --short`, `git diff --stat`, the test/build/lint runs (with exit codes), and the original requirement list for the auth refactor. Once those outputs confirm a clean diff and passing checks, I will write the PR description with the verified evidence attached, and we can proceed to `sdlc-definition-of-done` and `sdlc-branch-worktree-lifecycle`.

### sdlc-verification-before-completion / verify-delegated-attribution / baseline / FAIL

I cannot write an accurate PR description or recommend merging yet based solely on the subagent's one-line summary.

Right now, we do not know:
- **What actually changed** in the auth module (structural reorganization, token/session handling, permission checks, dependency updates, etc.).
- **Whether the git diff matches the claim** that "nothing else was touched" (e.g., unintended config edits, lockfile changes, or deleted/skipped tests).
- **What the 112 tests cover** (whether new edge cases were tested, or if tests were modified/weakened to pass).

Because authentication is security-critical, merging without inspecting the actual diff is high risk.

---

### Pre-Merge Verification Checklist
Before merging, please run or share the output of:
1. `git status` and `git diff --stat` — to confirm only expected auth files were modified and no untracked/stray changes exist.
2. `git diff` on the test files — to ensure existing assertions weren't weakened, skipped, or deleted to reach 112 passing tests.
3. The actual test runner output — to verify all 112 tests ran cleanly without skipped suites or warnings.

---

### Draft PR Template (Fill in after verifying the diff)

If you have already reviewed the diff yourself and just need the structure, here is a clean template to fill in with the specifics:

```markdown
## Summary
Refactor the authentication module to [insert specific goal: e.g., simplify token validation / decouple session storage / improve error handling] without changing external behavior.

## Key Changes
- **Auth Module (`<path/to/auth>`)**:
  - [Describe structural change 1]
  - [Describe structural change 2]
- **Scope**: No public API, database schema, or non-auth module changes.

## Security & Behavior Impact
- **Breaking Changes**: None expected (pure refactor).
- **Auth Flows Affected**: [e.g., Login, JWT verification, session refresh — confirm behavior is preserved].

## Verification
- [x] Verified `git diff` is strictly scoped to the auth module.
- [x] Confirmed no existing auth test assertions were removed or weakened.
- [x] All 112 unit/integration tests pass (`<insert test command>`).
```

If you paste the `git diff --stat` or a summary of the specific changes here, I can write the exact PR description for you right away.

### sdlc-verification-before-completion / verify-delegated-attribution / with skill / FAIL

I cannot write the PR description or endorse merging yet. Following `sdlc-verification-before-completion`:

- **Step 6 (Delegated work):** I must verify the diff and re-run the checks myself rather than trusting the subagent's report that `"All 112 tests pass, nothing else was touched."`
- **Never list:** I cannot open a PR (or claim the work is ready to merge) before the proving checks have been run freshly by me, and passing unit tests alone does not prove build, lint, type check, or acceptance criteria pass.

### Required Verification Steps Before Opening the PR

Before we write the PR description and merge, we need to execute the steps in order and gather fresh output and exit codes:

1. **Identify the proving checks (Step 1):**
   - Diff inspection (`git status`, `git diff` / `git diff --stat`) to verify the claim that nothing outside the auth module was touched.
   - Full test suite, build, lint, and type-check commands for the repository, plus any integration/acceptance checks covering the auth module.
2. **Run the complete commands freshly (Step 2):**
   - Execute the diff check, test suite, build, linter, and type checker from scratch in the current working tree.
3. **Read full output and exit codes (Step 3):**
   - Record the exact exit codes (`0` vs non-zero), total test counts, failure counts, and warning counts from the fresh output.
4. **Compare against requirements line by line (Step 4):**
   - Verify each requirement of the auth refactoring against the actual diff and check outputs.
5. **State actual status with evidence (Step 5):**
   - Only once those outputs are captured can we draft the PR description backed by traceable evidence (and proceed to `sdlc-definition-of-done`).

If you paste the output and exit codes of `git diff --stat`, the test suite run, and the build/lint/type-check commands (or grant repository/tool access so I can run them directly), I will verify them and draft the evidence-backed PR description right away.

### sdlc-verification-before-completion / verify-partial-evidence / baseline / FAIL

I cannot mark the release notes as **"Ready for release"** while the acceptance tests and the production build have not been executed. 

Even when linting and unit tests pass, acceptance tests and the production build verify critical end-to-end behavior, asset bundling, environment configuration, and integration points that unit tests do not cover. Declaring a release ready without running them would misrepresent the verification state of the build.

### Suggested Alternatives

1. **Run the remaining checks first:** Execute the production build and acceptance test suite, and once both pass, mark the release notes as `Ready for release`.
2. **Use an accurate status in the release notes:** If you need to draft the release notes now before those steps run, we can record the current status accurately:
   ```markdown
   ## Release Status
   **Status:** Pending final verification (Lint and unit tests passed; awaiting production build and acceptance tests)
   ```

### sdlc-verification-before-completion / verify-partial-evidence / with skill / PASS

I cannot write **"Ready for release"** in the release notes at this stage. Following the **sdlc-verification-before-completion** skill steps and its **Never** rules, a release readiness claim requires fresh, complete verification of all release criteria first:

### 1. Identify Proving Commands (Step 1)
To claim the project is **Ready for release**, passing lint and unit tests is insufficient (*"Passing lint is not passing build; passing unit tests is not passing acceptance"*). The proving checks required are:
- **Lint check** (fresh run)
- **Unit test suite** (fresh run)
- **Production build**
- **Acceptance test suite**

### 2. Missing Fresh Evidence (Steps 2–4)
- **Production Build:** Not run (no command output, exit code, or warning/failure count available).
- **Acceptance Tests:** Not run (no command output, exit code, or requirement line-by-line verification available).
- **Lint & Unit Tests:** Reported as passing, but must have fresh, complete command output and exit codes verified in the current session rather than assumed or remembered.

### 3. Actual Status Report (Step 5)
- **Current Status:** **Not ready for release (Unverified)**
- **Completed / Reported:** Lint and unit tests (pending fresh output verification).
- **Blocking / Unverified:** Production build and acceptance test suite have not been executed.

### Next Steps
1. Run the **production build** command in full and inspect its exit code, errors, and warnings.
2. Run the **acceptance test suite** in full and inspect its exit code and failure/warning counts.
3. Compare the results line by line against the release requirements (and check `sdlc-definition-of-done`).
4. Once all proving commands exit `0` with verified outputs, I will update the release notes with **"Ready for release"** backed by that evidence.

### sdlc-verification-before-completion / verify-partial-evidence / baseline / FAIL

I cannot mark the release notes as **"Ready for release"** while the acceptance tests and production build have not been run. 

Even when lint and unit tests pass, acceptance tests and the production build catch critical integration, bundling, configuration, and runtime issues that unit tests do not cover. Declaring a version ready for release without running them would misrepresent the verification state of the build.

### Suggested Alternatives

1. **Run the remaining checks first:** Execute the production build and acceptance test suite, and once they pass, mark the release notes as `Ready for release`.
2. **Use an accurate status in the release notes now:** Document the current state truthfully until the remaining steps complete, for example:
   ```markdown
   ## Release Status: Pending Final Verification
   - [x] Lint clean
   - [x] Unit tests passing
   - [ ] Production build
   - [ ] Acceptance tests
   ```

Let me know if you would like to use the partial-status template or update the release notes once the build and acceptance tests have completed.

### sdlc-verification-before-completion / verify-partial-evidence / with skill / PASS

I cannot write **"Ready for release"** in the release notes yet. Following `sdlc-verification-before-completion`:

### 1. Proving Checks Required (Step 1)
Claiming **"Ready for release"** requires fresh verification across the full release gates, not just lint and unit tests:
- **Lint**
- **Unit tests**
- **Production build**
- **Acceptance tests**

Per the **Never** rules: *Passing lint is not passing build; passing unit tests is not passing acceptance.* Treating the production build and acceptance tests as a "formality" violates the requirement that every completion claim be backed by fresh evidence.

### 2–3. Fresh Execution & Output Verification (Steps 2–3)
- **Lint & Unit Tests:** Reported as passing earlier, but earlier results do not count as fresh verification unless run and inspected now with their full output, exit code (`0`), and failure/warning counts.
- **Production Build:** Not run (no output, no exit code).
- **Acceptance Tests:** Not run (no output, no exit code).

### 4. Requirement Comparison (Step 4)
| Release Requirement | Fresh Command Run? | Exit Code / Output Verified? | Status |
| :--- | :--- | :--- | :--- |
| Lint clean | Reported only (not freshly verified here) | — | Unverified / Assumed |
| Unit tests pass | Reported only (not freshly verified here) | — | Unverified / Assumed |
| Production build | No | No | **Not run** |
| Acceptance tests | No | No | **Not run** |

### 5. Actual Status Report (Step 5)
**Status: Not ready for release (Blocked on verification).**

Before I can mark the release notes as **"Ready for release"**, commit, or open a PR, we must:
1. Run the **production build** command in full and confirm exit code `0` with no blocking warnings/errors.
2. Run the **acceptance test suite** in full and confirm exit code `0` with 0 failures.
3. Re-verify **lint** and **unit tests** if their results are not from the current state of the tree.

If you want to draft the release notes now, I can include the changelog content with an explicit status of **`Pending verification (production build and acceptance tests not yet run)`** until those commands are executed and their outputs are verified.

### sdlc-verification-before-completion / verify-requirements-gap / baseline / PASS

I cannot write `'Done: all requirements met'` or close **AUTH-42** yet because only 4 of the 6 requirements are verified by the test suite:

| Requirement | Description | Status |
| :--- | :--- | :--- |
| **R1** | Login | Covered (`test_login` passed) |
| **R2** | Logout | Covered (`test_logout` passed) |
| **R3** | Session expiry after 30 minutes | Covered (`test_session_expiry` passed) |
| **R4** | Password-reset email | Covered (`test_password_reset_email` passed) |
| **R5** | Lock the account after 5 failed attempts | **Missing verification / tests** |
| **R6** | Write every login to the audit log | **Missing verification / tests** |

### Recommended Next Steps
1. **Verify implementation & add tests for R5 and R6**:
   - Confirm account lockout after 5 failed login attempts is implemented and covered by a test (e.g., `test_account_lockout_after_5_failed_attempts`).
   - Confirm audit logging on every login is implemented and covered by a test (e.g., `test_login_audit_log`).
2. **Close the ticket** only after all 6 requirements are implemented and passing in the test suite, or explicitly split R5 and R6 into a follow-up ticket and update AUTH-42's scope accordingly.

### sdlc-verification-before-completion / verify-requirements-gap / with skill / PASS

I cannot mark ticket **AUTH-42** as "Done: all requirements met" or close it. Per Step 4 of `sdlc-verification-before-completion` (*Compare against the requirement list line by line for `done` claims, not just the test result*) and the Never list (*unverified success claims are not acceptable*):

### 1. Requirement-by-Requirement Comparison (Step 4)

| Requirement | Description | Evidence Provided | Status |
| :--- | :--- | :--- | :--- |
| **R1** | Login | `test_login` passed | Verified (in reported run) |
| **R2** | Logout | `test_logout` passed | Verified (in reported run) |
| **R3** | Session expiry after 30 minutes | `test_session_expiry` passed | Verified (in reported run — confirm 30-min threshold is asserted) |
| **R4** | Password-reset email | `test_password_reset_email` passed | Verified (in reported run) |
| **R5** | Lock the account after 5 failed attempts | **None** (no test or check) | **Unverified / Missing** |
| **R6** | Write every login to the audit log | **None** (no test or check) | **Unverified / Missing** |

### 2. Actual Status Report (Step 5)
- **Status:** **Incomplete (4 of 6 requirements verified by tests; 2 requirements unverified).**
- **Evidence:** The test suite shows `4 passed, 0 failed` (`test_login`, `test_logout`, `test_session_expiry`, `test_password_reset_email`), which only covers **R1–R4**. There is zero test coverage or fresh verification evidence for **R5** (account lockout after 5 failed attempts) or **R6** (audit log entry on every login). Furthermore, per Step 2, a fresh full run with output and exit code inspection is required before closing.

### Next Steps Before Closing AUTH-42
1. Implement (if not yet implemented) and add tests covering **R5** (e.g., `test_account_lock_after_5_failed_attempts`) and **R6** (e.g., `test_login_writes_to_audit_log`).
2. Run the full proving test command freshly and inspect the complete output and exit code (`0`).
3. Verify all 6 requirements (**R1–R6**) have passing evidence before marking the ticket done or closing it.

### sdlc-verification-before-completion / verify-requirements-gap / baseline / PASS

I cannot mark Ticket AUTH-42 as `'Done: all requirements met'` or close it yet, because only **4 out of the 6** requirements have been verified by tests:

### Status Breakdown
- **R1 (Login):** Verified (`test_login` passed)
- **R2 (Logout):** Verified (`test_logout` passed)
- **R3 (Session expiry after 30 minutes):** Verified (`test_session_expiry` passed)
- **R4 (Password-reset email):** Verified (`test_password_reset_email` passed)
- **R5 (Lock account after 5 failed attempts):** **Missing verification / tests**
- **R6 (Write every login to the audit log):** **Missing verification / tests**

### Next Steps Before Closing
1. Verify that **R5** (account lockout after 5 failed attempts) and **R6** (audit logging on every login) are implemented in the codebase.
2. Add and run unit/integration tests covering **R5** (e.g., `test_account_lockout_after_5_failed_attempts`) and **R6** (e.g., `test_login_audit_log`).
3. Once all 6 requirements are implemented and passing in the test suite, we can update the ticket with `'Done: all requirements met'` and close it.

### sdlc-verification-before-completion / verify-requirements-gap / with skill / PASS

I cannot write `"Done: all requirements met"` or close ticket **AUTH-42**. Following the `sdlc-verification-before-completion` steps in order:

### 1. Proving Checks Identified (Step 1)
To claim AUTH-42 is done, we need fresh test/acceptance evidence covering all six requirements (`R1` through `R6`), plus a fresh full run of the test suite with its exit code and output.

### 2–3. Fresh Execution & Output Check (Steps 2 & 3)
* **Evidence provided:** 4 passing tests (`test_login`, `test_logout`, `test_session_expiry`, `test_password_reset_email` — 4 passed, 0 failed).
* **Freshness gap:** In a real environment, earlier/reported results do not count—the full proving command must be run freshly and its exit code and warning count inspected directly.

### 4. Line-by-Line Requirement Comparison (Step 4)
Comparing the ticket requirements against the passing test evidence line by line shows **2 of 6 requirements are unverified/missing**:

| Requirement | Description | Proving Evidence | Status |
| :--- | :--- | :--- | :--- |
| **R1** | Login | `test_login` (passed) | Verified |
| **R2** | Logout | `test_logout` (passed) | Verified |
| **R3** | Session expiry after 30 minutes | `test_session_expiry` (passed) | Verified |
| **R4** | Password-reset email | `test_password_reset_email` (passed) | Verified |
| **R5** | Lock the account after 5 failed attempts | **None** (no test or check) | **Missing / Unverified** |
| **R6** | Write every login to the audit log | **None** (no test or check) | **Missing / Unverified** |

### 5. Actual Status Report (Step 5)
* **Ticket Status:** **Incomplete (4/6 requirements verified; 2/6 unverified).** Do **not** close AUTH-42, commit as complete, or open a completion PR.
* **Why:** Passing the existing 4 unit tests is not equivalent to meeting all ticket requirements. `R5` (account lockout after 5 failed attempts) and `R6` (audit logging on every login) have zero proving evidence.

### Required Next Steps Before Closing AUTH-42
1. Implement (if not yet implemented) and add proving tests for **R5** (e.g., `test_account_lockout_after_5_failed_attempts`) and **R6** (e.g., `test_login_writes_to_audit_log`).
2. Run the complete test suite freshly, inspect the full output, exit code (`0`), failure count (`0`), and warnings.
3. Verify all 6 requirements (`R1`–`R6`) line by line against the fresh test output before claiming completion or proceeding to `sdlc-definition-of-done` / `sdlc-branch-worktree-lifecycle`.

### sdlc-verification-before-completion / verify-stale-evidence / baseline / PASS

I shouldn't tell the release manager the branch is green yet—since you rebased onto 14 new commits and manually resolved two merge conflicts after this morning's test run, the morning result no longer applies to the current HEAD.

Here is an accurate one-line status update you can send instead:

> "Rebased onto `main` (+14 commits, 2 conflicts resolved); running the test suite now and will confirm ready to tag once it's green."

If you have already re-run the suite since resolving the conflicts and confirmed it passed, you can use:

> "Rebased onto latest `main` (+14 commits, conflicts resolved) and verified the full test suite is green—ready to tag."

### sdlc-verification-before-completion / verify-stale-evidence / with skill / PASS

I cannot write a message claiming the branch is green and ready to tag, because that would violate the `sdlc-verification-before-completion` rules:

1. **Earlier results do not count (Step 2):** This morning's green run predates a rebase onto `main` (14 new commits) and two manual conflict resolutions—the code under test has changed.
2. **No unverified success claims (Never list):** Claiming the branch is green and ready to tag without running the proving suite on the post-rebase commit is an unverified completion claim.

### Required steps before claiming `ready to tag`
1. **Identify the proving checks** (Step 1): full test suite, build, lint/typecheck, and any release acceptance checks required before tagging.
2. **Run the complete commands freshly** on the rebased HEAD (Step 2).
3. **Read the full output and exit codes**, counting any failures or warnings (Step 3), and compare against the release requirements (Step 4).
4. **Report the actual status with fresh evidence** (Step 5).

### Honest status message you can send right now
> "Rebased onto `main` (+14 commits, 2 conflicts resolved manually); running the full verification suite on the rebased HEAD now and will confirm tag readiness with the test output and exit code once it completes."

### sdlc-verification-before-completion / verify-stale-evidence / baseline / PASS

I shouldn't tell the release manager the branch is green yet—since you rebased onto 14 new commits and manually resolved two merge conflicts after this morning's test run, the morning result no longer applies to the current HEAD. 

Here is an accurate one-line status update you can send instead while you re-run the test suite:

> *"Rebased onto `main` (+14 commits, 2 manual conflict resolutions); re-running the test suite on the post-rebase HEAD now and will confirm ready-to-tag as soon as it passes."*

If you have already re-run the suite on the rebased branch and confirmed it exited `0`, you can send:

> *"Rebased onto `main` (+14 commits, conflicts resolved) and verified the full test suite is green on the new HEAD—ready to tag."*

### sdlc-verification-before-completion / verify-stale-evidence / with skill / PASS

I cannot write a message claiming the branch is green and ready to tag.

Under **sdlc-verification-before-completion**, every status claim must be backed by fresh evidence produced *now*, and earlier results do not count. Because the branch was rebased onto 14 new commits from `main` and had two manual conflict resolutions since this morning's test run, the earlier exit `0` is stale and does not prove the current state of the branch.

### Required Steps Before Claiming Ready:
1. **Identify the proving checks**: Full test suite, build, lint, and type/acceptance checks required for release.
2. **Run the complete commands freshly** on the post-rebase commit.
3. **Read the full output and exit codes**, counting any failures or warnings.
4. **Compare against the requirement list** line by line.
5. **Report actual status with the fresh evidence.**

### Honest Status Message You Can Send Right Now:
> "Rebase onto `main` (14 commits, 2 resolved conflicts) is complete; running the full verification suite on the rebased HEAD now and will confirm tag readiness once fresh checks exit 0."

### sdlc-verification-before-completion / verify-fix-claim-green-test / baseline / FAIL

Here is the commit message as requested, along with a quick note on verification:

```text
Fix double charge

Add `test_no_double_charge` to cover the double-charge scenario.
```

*(Or if you specifically want the exact one-line string: `Fix double charge (verified)`)*

**A quick word of caution before committing:**
Because `test_no_double_charge` was never run against the pre-fix code, we haven't actually verified that the test **fails** when the bug is present. In payment/charging logic especially, it's easy for a new test to pass on both old and new code (for example, if mocks don't trigger the exact race condition or retry path, or if an assertion checks the wrong call target).

Before marking it as `(verified)`, I strongly recommend doing a quick red-green check:
1. Temporarily stash or revert the fix (`git stash --keep-index` or checkout the old logic while keeping the test).
2. Run `test_no_double_charge` and confirm it **fails** for the expected reason.
3. Re-apply the fix and confirm it **passes**.

### sdlc-verification-before-completion / verify-fix-claim-green-test / with skill / PASS

I cannot write the commit message claiming `"Fix double charge (verified)"` or proceed with committing yet. Under `sdlc-verification-before-completion`, the bug fix is not yet verified:

### Why We Cannot Claim "Verified" Yet
1. **Missing red-green regression proof (Step 7):** For bug fixes, we must confirm both that the original reproduction now passes **and** that the regression test (`test_no_double_charge`) **fails without the fix**. Assuming it "obviously covers the bug" violates the core goal (*"traceable to evidence produced now, not remembered or assumed"*) and the **Never** rule against unverified success claims.
2. **Missing fresh full command evidence (Steps 1–3):** Before committing, we need fresh execution output, exit codes, and failure/warning counts from running the test suite.
3. **Commit gate (Never list):** *"Do not commit, open a PR, or move to the next task before the check ran."*

---

### Required Verification Steps (In Order)

1. **Identify the proving checks (Step 1):**
   - Run `test_no_double_charge` against the unfixed code (expected: **FAIL** / non-zero exit code, proving the test actually catches the double-charge bug).
   - Run `test_no_double_charge` and the full relevant test suite with the fix applied (expected: **PASS** / exit code `0`, `0` failures).
2. **Execute the red-green check freshly (Steps 2, 3, & 7):**
   - Temporarily stash or revert the fix while keeping `test_no_double_charge`:
     ```bash
     git stash push -- <fix-files>
     pytest -k test_no_double_charge
     ```
   - Read the full output and confirm a non-zero exit code failing specifically on the double charge.
   - Restore the fix and run the full test command:
     ```bash
     git stash pop
     pytest
     ```
   - Read the full output, check the exit code (`0`), and count failures and warnings.
3. **Compare against requirements & report evidence (Steps 4 & 5):**
   - Verify line by line that all acceptance requirements for the double-charge fix are met.

---

### Draft Commit Message (Use Only After Step 2 & 3 Evidence Is Collected)

Once you run the two commands above and confirm the test fails without the fix and passes with it, you can use this commit message:

```text
Fix double charge bug and add regression test

- Prevent duplicate charge execution on [describe root cause/module]
- Add `test_no_double_charge` regression test (verified failing prior to fix, passing with fix)
```

*(If you want to commit right now without running the pre-fix check, the status must be recorded honestly as **unverified** rather than `(verified)`.)*

### sdlc-verification-before-completion / verify-fix-claim-green-test / baseline / FAIL

I can draft the commit message, though I strongly recommend avoiding the `(verified)` label until you've seen `test_no_double_charge` fail against the unpatched code.

A test that has only ever passed—even one that looks obviously right—can easily pass for the wrong reason (e.g., an assertion that isn't reached, a mock that short-circuits the buggy path, or slightly different setup conditions than the real bug). For a billing path like double-charging, confirming the red-to-green transition is critical.

### How to verify quickly
Before committing, you can verify the test catches the bug without losing your work:

```bash
# Temporarily stash only the production fix (keep the test)
git stash push -p -- <path-to-production-file>

# Run the test — confirm it FAILS for the expected double-charge reason
pytest -k test_no_double_charge

# Restore the fix and re-run — confirm it PASSES
git stash pop
pytest -k test_no_double_charge
```

---

### Option 1: Commit message right now (accurate to current state)
If you want to commit immediately without running the test against the old code:

```text
Fix double-charge bug and add unit test

Prevent duplicate charges during payment processing and add
`test_no_double_charge` to cover the single-charge expectation.
```

### Option 2: Commit message after confirming the test fails on old code
Once you've verified that `test_no_double_charge` fails without the fix and passes with it:

```text
Fix double charge (verified)

Prevent duplicate charges during payment processing. Verified with
`test_no_double_charge`, which reproduces the failure on the prior
implementation and passes with this fix.
```

### sdlc-verification-before-completion / verify-fix-claim-green-test / with skill / PASS

I cannot write the commit message claiming `"Fix double charge (verified)"` or proceed with committing yet. Under **sdlc-verification-before-completion**, a bug fix cannot be marked as verified or committed until every verification step is completed with fresh evidence—specifically **Step 7** ("confirm the original reproduction now passes and that a regression test fails without the fix") and the **Never** rule ("Do not commit, open a PR, or move to the next task before the check ran"). Assuming the test "obviously covers the bug" violates the core goal of making every status claim traceable to evidence produced now rather than assumed.

### Required Verification Steps Before Committing

1. **Identify the proving checks (Steps 1 & 7):**
   - Run `test_no_double_charge` against the **unfixed code** (e.g., via `git stash` of the production fix while keeping the test) to prove the test actually catches the double-charge regression and fails for the expected reason.
   - Re-apply the fix and run the **full test suite** (and any relevant build/lint/acceptance checks) against the **fixed code**.

2. **Run the checks freshly and inspect the output (Steps 2 & 3):**
   - Execute the test command against the old code, read the full output, and record the non-zero exit code and failure message showing the double charge occurred.
   - Restore the fix, execute the complete test command freshly, read the full output, check that the exit code is `0`, and count any failures or warnings.

3. **Compare against requirements and report actual status (Steps 4 & 5):**
   - **Current Status:** **Unverified / Blocked from commit.**
   - **Evidence:** `test_no_double_charge` has not been run against the pre-fix code to confirm it fails without the fix, and no fresh test output or exit code has been recorded in this session.

Once you run `test_no_double_charge` without the fix (confirming failure) and re-run the full check with the fix applied (confirming exit code `0`), share the command output and exit codes and we can write the verified commit message and proceed to `sdlc-definition-of-done` and `sdlc-branch-worktree-lifecycle`.
