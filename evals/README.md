# Skill evaluations

Scenario files `evals/<skill>.json` hold realistic prompts with deterministic checks (`must` and `forbid` regexes). `scripts/run_evals.py` asks a model each prompt twice, without the skill and with its compact version, and reports the difference.

```bash
python scripts/run_evals.py --model llama3.1 --base-url http://localhost:11434/v1 --runs 3 --out evals/results/llama3.1.md
python scripts/run_evals.py --model gpt-4o --base-url https://api.openai.com/v1 --api-key "$OPENAI_API_KEY" --skill sdlc-test-driven-development
```

`--base-url claude-cli` runs the scenarios through your local Claude Code CLI (`--model sonnet`, `haiku`, or `opus`) with tools and skills disabled. Any OpenAI-compatible endpoint also works (Ollama, vLLM, llama.cpp server, LM Studio, hosted APIs).

## How to read results

- The checks are a floor: they detect whether the key behavior appears, not whether the answer is good. Read the replies behind failures.
- Use `--runs 3` or more; small models vary between runs.
- Record the model name and date (the report does). Results do not transfer across models.
- A skill that does not improve the score on a model is a candidate for simplification, per `sdlc-skill-evaluation`.

## Adding a scenario

1. Observe a real failure without the skill and copy the prompt that provoked it.
2. Add `must` patterns for the behavior you want and `forbid` patterns for the rationalizations you saw.
3. Include a pressure case (deadline, authority, sunk cost).
4. Run `python scripts/test_llm_tools.py` to make sure the harness still passes.

The repository tests use a fake model server, so they verify the harness, not any model's quality. Real results need a real model run.
