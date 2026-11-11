#!/usr/bin/env python3
"""Routing eval: given every skill description, can a model pick the right skill for a realistic request?

  python scripts/run_routing.py --model haiku --base-url claude-cli --workers 4
  python scripts/run_routing.py --model haiku --base-url claude-cli --descriptions candidate.json   # {skill: description}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_client  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = "You route requests to skills. Reply with exactly one skill name from the list, nothing else."


def load_descriptions(override: Path | None) -> dict[str, str]:
    found = {}
    for path in sorted((ROOT / "skills").glob("sdlc-*/SKILL.md")):
        found[path.parent.name.removeprefix("sdlc-")] = re.search(r"^description:\s*(.+)$", path.read_text(), re.M).group(1).strip()
    if override:
        found.update(json.loads(override.read_text()))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default=llm_client.DEFAULT_BASE_URL)
    parser.add_argument("--api-key")
    parser.add_argument("--descriptions", type=Path, help="JSON {skill: description} overriding SKILL.md descriptions")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    descriptions = load_descriptions(args.descriptions)
    listing = "\n".join(f"- {name}: {text}" for name, text in descriptions.items())
    queries = json.loads((ROOT / "evals" / "routing" / "queries.json").read_text())

    def pick(item):
        reply = llm_client.chat([{"role": "system", "content": f"{SYSTEM}\n\nSkills:\n{listing}"}, {"role": "user", "content": item[0]}], args.model, args.base_url, args.api_key)
        found = [n for n in descriptions if re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", reply)]
        return found[0] if found else reply.strip()[:40]

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        picks = list(pool.map(pick, queries))
    wrong = [(q, want, got) for (q, want), got in zip(queries, picks) if want != got]
    chars = sum(len(t) for t in descriptions.values())
    print(f"routing {args.model}: {len(queries) - len(wrong)}/{len(queries)} correct; descriptions {chars} chars")
    for q, want, got in wrong:
        print(f"  want {want:32s} got {got:32s} | {q[:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
