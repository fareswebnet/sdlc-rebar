# sdlc-bounded-context-map (compact)

When: Map DDD bounded contexts: which team or module owns which data and capability, upstream/downstream links, anti-corruption layers.

Goal: Prevent one vague model from spreading across unrelated parts of the system.

Steps:
1. Group domain language and behavior into coherent contexts.
2. Define each context's owner, purpose, data ownership, and public contracts.
3. Map upstream/downstream dependencies and translation needs.
4. Choose integration patterns such as direct call, event, ACL, shared kernel, or published language.
5. Record boundary decisions as ADRs when they affect architecture or teams.

Never:
- Do not split by technical layer when the real boundary is business capability or data ownership.
