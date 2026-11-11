# Skill value analysis

What each skill adds over the bare model, what was measured, and what was removed. Date: 2026-11-11.

## What was measured

Claude (Sonnet and Haiku, via the local Claude Code CLI with tools, skills, and MCP connectors disabled) and Gemini through Antigravity (`agy`, model `gemini-4-argon-low`, 2 runs). Codex is not installed here, so **there is no measured data for Codex.** The old Gemini CLI is no longer supported on this account; Gemini means Antigravity throughout.

Antigravity is less isolated than the Claude runs: `agy` cannot disable its tools or set a system prompt, so the skill text is prefixed to the prompt, the run happens in an empty directory, and every prompt states that no tool access exists. The Gemini Flash and GPT-OSS models were out of quota, so only `gemini-4-argon-low` was measured.

Totals over the 19 scenarios of the repository: Sonnet and Haiku about 22/48 and 23/48 baseline versus 44/48 and 43/48 with the skill on the 16 original scenarios; Antigravity 21/38 versus 34/38 on all 19 scenarios (2 runs).

Method: one or more pressure scenarios per skill, 3 runs each, with and without the compact skill, regex checks (a floor, not a quality judgement). Raw replies are in `evals/results/`. Runs are noisy: the three kept generic skills were measured twice and their baselines moved by one run out of three, so differences of one run are not significant.

## Results by skill

| Skill | Scenario | Without skill (Sonnet / Haiku) | Verdict |
|---|---|---|---|
| `sdlc-independent-verification` | refuse a self-issued visa | 0/3 / 0/3 | **Strong gain** |
| `sdlc-legacy-inventory-registry` | registry before target code | 0/3 / 0/3 | **Strong gain** |
| `sdlc-test-driven-development` | test first under time pressure; fix handed over; "suite is green" | 0/3 on all three, both models | **Strong gain** (the plain bug-fix case does not discriminate) |
| `sdlc-design-brainstorming` | "trivial" change; whole-marketplace request | 0/3 / 0/3 | **Strong gain** (the original design gate does not discriminate) |
| `sdlc-systematic-debugging` | patch the symptom | 2/3 / 2/3 | Moderate gain |
| `sdlc-verification-before-completion` | five variants | mostly 3/3; gains on delegated reports and partial evidence | **Small gain** on Claude; core discipline, kept |
| `sdlc-observability-reliability` | noisy paging rules | 1-2/3 / 1-2/3 (two runs) | Moderate gain, 3/3 with skill |
| `sdlc-prd-requirements` | vague verbs | 3/3 / 0-1/3 | Gain on Haiku only |
| `sdlc-application-architecture` | CTO wants microservices | 3/3 / 1-2/3 | Inconclusive: gain on Haiku, one Sonnet miss with the skill (likely a regex false positive) |
| `sdlc-product-strategy`, `sdlc-api-integration-contracts`, `sdlc-identity-access-multitenancy`, `sdlc-release-production-readiness`, `sdlc-technical-debt-evolution` | one pressure scenario each | 3/3 / 3/3 | **No gain measured: removed** |

Pattern: skills that encode a non-obvious discipline against a tempting shortcut (self-approval, test-first, registry-first, hard design gate) change behavior. Skills that restate general engineering knowledge (strategy, contracts, authorization, release checks, debt) do not, because the model already applies it.

## Antigravity (Gemini) results

Baseline versus with skill, 2 runs per scenario: design gate 0/2 to 2/2; TDD under time pressure 0/2 to 2/2; TDD with a fix supplied 0/2 to 1/2; "suite is green" pressure 0/2 to 2/2; verifying a partial result 0/2 to 2/2; unverified fix claim 0/2 to 2/2; self-visa 1/2 to 2/2; PRD vague verbs 1/2 to 2/2. No gain on registry-first, debugging, alert noise, or microservices default (already 2/2). Notably, `sdlc-verification-before-completion` helps Gemini where it barely moves Claude, which supports keeping it. `design-small-change-pressure` failed 0/2 both ways (the model gave the design but the regex found no "approach" wording). The sample is small (2 runs); raw replies are in `evals/results/antigravity-gemini-4-argon-low.md`.

## Removed

| Removed | Why | References now point to |
|---|---|---|
| `sdlc-product-strategy` | 3/3 without skill on both models | `sdlc-idea-framing` |
| `sdlc-api-integration-contracts` | 3/3 on both models | `sdlc-api-versioning-deprecation` |
| `sdlc-identity-access-multitenancy` | 3/3 on both models | `sdlc-security-privacy-compliance` |
| `sdlc-release-production-readiness` | 3/3 on both models | `sdlc-definition-of-done` |
| `sdlc-technical-debt-evolution` | 3/3 on both models | `sdlc-delivery-retrospective` |
| `sdlc-maturity-assessment` | generic scoring rubric, no unique rule | dropped |
| `sdlc-skill-authoring` | meta, unreferenced, overlaps `sdlc-skill-evaluation` | `sdlc-skill-evaluation` |

The scenarios for the five measured skills are kept in `evals/removed/`. The deleted skills remain in git history (commit `c409b2c` and earlier).

## Not decided by data

49 of the remaining 58 skills have no scenario yet: the other generic lifecycle skills (domain modeling, UX, data architecture, ...), and the hand-written migration, merge, and spec-driven ones. They stay, because absence of a test is not evidence of no value, and several are wired into harnesses and agents. The same test applies to them: a skill that does not move a baseline on a realistic pressure scenario is a candidate for removal.

## Size

- `SKILL.md` text: 185 KB to 109 KB. Each file repeated the same Operating Depth, Expected Inputs, Source Guidance, and two generic guardrails, 38% of all text; the depth definitions now live once in `depth-matrix.md`.
- Compact skills: 74 KB.
- Frontmatter descriptions (the part Claude Code always loads): 20.8 KB, then 18.7 KB after removals, now 11.1 KB. Rewritten to one "what" clause plus "Use when" triggers, at most about 230 characters each.

## Description routing test

`python scripts/run_routing.py --model <m> --base-url claude-cli` gives the model all descriptions and 79 realistic requests (59 clear, 20 between neighbouring skills) and checks it picks the right skill.

| Descriptions | Characters | Haiku | Sonnet |
|---|---|---|---|
| Original | 18,654 | 74/79 | 79/79 |
| Rewritten | 11,132 | 74/79 | 79/79 |

Haiku misses move around between runs (invented or truncated skill names, and confusions between neighbours such as task-breakdown / implementation-planning, retrospective / debugging). Seven descriptions were hand-adjusted after a first rewrite scored 72/79, using this same test set, so the result is slightly optimistic.
