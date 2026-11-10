# Tasks: <feature name>

Source: spec, plan, BDD scenarios. Format: `- [ ] T### [P] [US#] (FR-001) Action in exact/file/path`; the requirement id lets `scripts/sdlc_trace.py` check coverage.
`[P]` means safe to run in parallel (disjoint files, no unfinished dependency).

## Phase 1: Setup
- [ ] T001 Create project structure per plan
- [ ] T002 [P] Configure lint and test tooling

## Phase 2: Foundations (blocks all stories)
- [ ] T003 Add shared data model and migration in src/models/
- [ ] T004 [P] Add auth and error handling skeleton in src/core/

## Phase 3: User Story 1 - <title> (P1, MVP)
Goal: <independently demonstrable outcome>
Independent test: <how to prove this story alone>
- [ ] T005 [P] [US1] (FR-001) Failing acceptance test in tests/acceptance/us1.test
- [ ] T006 [US1] (FR-001) Implement service in src/services/us1.ext
- [ ] T007 [US1] (FR-001) Expose interface in src/api/us1.ext
Checkpoint: story 1 works and is demonstrable on its own.

## Phase 4: User Story 2 - <title> (P2)
- [ ] T008 [P] [US2] (FR-002) Failing test in tests/acceptance/us2.test
- [ ] T009 [US2] (FR-002) Implement in src/services/us2.ext
Checkpoint: stories 1 and 2 both work independently.

## Final Phase: Polish
- [ ] T010 [P] Update docs and runbook
- [ ] T011 Run full validation and record evidence

## Dependencies
Setup -> Foundations -> stories (by priority) -> Polish. Stories must not depend on later stories.

## Traceability
| Requirement or scenario | Tasks |
|---|---|
| FR-001 | T005, T006 |
