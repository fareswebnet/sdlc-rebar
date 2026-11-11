# sdlc-domain-modeling (compact)

When: Model the business domain with DDD: ubiquitous language, entities, aggregates, invariants, state transitions.

Goal: Make the business model explicit before the software model hardens.

Steps:
1. Extract domain terms, actors, actions, lifecycle states, and policies.
2. Identify entities, value objects, aggregates, commands, events, and invariants.
3. Separate domain rules from UI, persistence, integration, and reporting concerns.
4. Find ambiguous terms and align them with a ubiquitous language.
5. Feed bounded contexts, BDD scenarios, database design, and API contracts.

Never:
- Do not design tables, APIs, or services before the core domain terms and invariants are clear.
