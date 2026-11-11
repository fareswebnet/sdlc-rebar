# sdlc-api-integration-contracts (compact)

When: Define API, event, webhook, file, and third-party integration contracts using OpenAPI, AsyncAPI, schemas, versioning, idempotence, retries, errors, compatibility, and contract testing.

Goal: Prevent hidden coupling and integration ambiguity.

Steps:
1. Identify producers, consumers, ownership, protocols, auth, data classification, and compatibility needs.
2. Specify request/response, event, webhook, error, retry, pagination, and idempotency behavior.
3. Version contracts and document deprecation policy.
4. Map contracts to bounded contexts, tests, observability, and support impact.
5. Generate or update OpenAPI/AsyncAPI skeletons when useful.

Never:
- Do not change a contract without naming impacted consumers and compatibility behavior.
- Prefer existing repo patterns, local conventions, and versioned artifacts over generic advice.
- Keep outputs actionable: decision, rationale, trade-offs, next action, and validation.
