# Requirements Checklist: <domain>

Purpose: test the quality of the written requirements, not the implementation.
Audience: author self-check | peer review | release gate.

## Completeness
- [ ] Are failure and edge-case behaviors specified for each primary flow? [Spec §]
- [ ] Are all actors and their permissions listed? [Spec §]

## Clarity
- [ ] Is every adjective (fast, secure, simple) tied to a measurable target? [Spec §]

## Consistency
- [ ] Do terms match the glossary and the domain model? [Spec §]

## Measurability
- [ ] Can each requirement be verified by a scenario or metric? [Spec §]

## Coverage and Dependencies
- [ ] Are external dependencies and assumptions named with an owner? [Spec §]

## Failures To Resolve
| Item | Gap | Action (clarify, rewrite, defer) |
|---|---|---|
