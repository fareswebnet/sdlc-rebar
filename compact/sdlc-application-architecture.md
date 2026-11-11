# sdlc-application-architecture (compact)

When: Design application architecture including modular monoliths, layered architecture, hexagonal ports/adapters, clean architecture, services, background jobs, CQRS, event-driven flows, dependency rules, and module…

Goal: Choose a structure the team can build, test, and evolve.

Steps:
1. Start from bounded contexts, domain rules, runtime constraints, and team ownership.
2. Choose the simplest architecture style that satisfies quality attributes and change pressure.
3. Define modules, layers, dependency direction, adapters, services, jobs, and integration points.
4. Document transaction boundaries, failure handling, and deployment implications.
5. Create ADRs for choices that constrain future code.

Never:
- Default to modular monolith plus clear boundaries unless scale, teams, regulation, or runtime constraints…
