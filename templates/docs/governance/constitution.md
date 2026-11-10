# Project Constitution

Version: 1.0.0
Ratified: YYYY-MM-DD
Last amended: YYYY-MM-DD

## Principles

### 1. Tests precede implementation
- Rule: MUST write a failing test before production code for any behavior change.
- Rationale: tests that never failed prove nothing.
- Check: CI coverage gate and review checklist item.

### 2. Secrets and customer data stay out of the repository
- Rule: MUST NOT commit secrets, tokens, or real customer data.
- Rationale: leaks are irreversible once pushed.
- Check: secret scanning in CI.

### 3. Every public interface has a contract
- Rule: MUST publish an OpenAPI/AsyncAPI or typed schema for each public API or event.
- Rationale: consumers need a stable, testable surface.
- Check: contract tests in CI.

## Governance

- Amendments: proposal, rationale, human approval, version bump (MAJOR removes or redefines, MINOR adds, PATCH rewords).
- Compliance review: every plan and PR states which principles it touches.

## Amendment Log

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0.0 | YYYY-MM-DD | Initial ratification | Name |
