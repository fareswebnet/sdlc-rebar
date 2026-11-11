#!/usr/bin/env python3
"""Self-test for llm_client, sdlc_runner, run_evals, and compact_skills using a local fake model server."""

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def make_server(responder):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            reply = responder(body["messages"])
            data = json.dumps({"choices": [{"message": {"role": "assistant", "content": reply}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/v1"


def run(*args, cwd=None):
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)


class LlmToolsTests(unittest.TestCase):
    def test_runner_retries_on_failing_gate_and_applies_files(self):
        calls = []

        def responder(messages):
            calls.append(messages)
            if len(calls) == 1:
                return "FILE: result.txt\n```\nwrong\n```"
            return "FILE: result.txt\n```\nright\n```"

        server, url = make_server(responder)
        work = Path(tempfile.mkdtemp())
        (work / "check.py").write_text("import sys; sys.exit(0 if open('result.txt').read().strip()=='right' else 1)\n")
        out = work / "transcript.md"
        result = run(str(SCRIPTS / "sdlc_runner.py"), "--model", "m", "--base-url", url, "--skill", "sdlc-test-driven-development",
                     "--task", "make result.txt say right", "--workdir", str(work), "--apply", "--gate", f"{sys.executable} check.py",
                     "--max-rounds", "3", "--out", str(out))
        server.shutdown()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(calls), 2)
        self.assertIn("sdlc-test-driven-development", calls[0][0]["content"])
        self.assertIn("The gate failed", calls[1][-1]["content"])
        self.assertIn("Round 2 gates", out.read_text())

    def test_runner_refuses_paths_outside_workdir(self):
        server, url = make_server(lambda m: "FILE: ../escape.txt\n```\nx\n```\nFILE: ok.txt\n```\ny\n```")
        base = Path(tempfile.mkdtemp())
        work = base / "work"
        work.mkdir()
        result = run(str(SCRIPTS / "sdlc_runner.py"), "--model", "m", "--base-url", url, "--task", "t", "--workdir", str(work), "--apply")
        server.shutdown()
        self.assertIn("REFUSED", result.stdout)
        self.assertFalse((base / "escape.txt").exists())
        self.assertTrue((work / "ok.txt").exists())

    def test_runner_fails_when_gate_never_passes(self):
        server, url = make_server(lambda m: "nothing useful")
        work = Path(tempfile.mkdtemp())
        result = run(str(SCRIPTS / "sdlc_runner.py"), "--model", "m", "--base-url", url, "--task", "t", "--workdir", str(work),
                     "--gate", f"{sys.executable} -c 'raise SystemExit(1)'", "--max-rounds", "2")
        server.shutdown()
        self.assertEqual(result.returncode, 1)

    def test_evals_show_delta_between_baseline_and_skill(self):
        def responder(messages):
            with_skill = "Skill" in messages[0]["content"] or "(compact)" in messages[0]["content"]
            return "I will write a failing test first, before the implementation." if with_skill else "Sure, tests can be added later. Here is the code."

        server, url = make_server(responder)
        result = run(str(SCRIPTS / "run_evals.py"), "--model", "m", "--base-url", url, "--skill", "sdlc-test-driven-development")
        server.shutdown()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("baseline 0/2, with skill 2/2", result.stdout)

    def test_compact_is_up_to_date(self):
        result = run(str(SCRIPTS / "compact_skills.py"), "--check")
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
