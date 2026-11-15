"""Gemail's additions to the adopted SDK run guard: the CI repair ledger (`repair`) and the text `query stats` reader.

Ported from the self-test cases of Gemail's Photon-era guard (D00 T04 §35, §37 provenance) when the SDK guard replaced
it on 2026-11-15. Run: python -m unittest discover -s scripts/tests -t .
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
GUARD_PY = REPO / "scripts" / "campaign_guard.py"

spec = importlib.util.spec_from_file_location("campaign_guard_repair_under_test", GUARD_PY)
assert spec is not None and spec.loader is not None
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class Repair(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="campaign-repair-")
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        os.makedirs(os.path.join(self.root, "build"))
        os.makedirs(os.path.join(self.root, "docs"))
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
                     ["config", "commit.gpgsign", "false"]):
            git(self.root, *args)
        Path(self.root, ".gitignore").write_text("build/\n", encoding="utf-8")
        self.shas = []
        for n in range(6):
            Path(self.root, "f.txt").write_text(f"{n}\n", encoding="utf-8")
            git(self.root, "add", "-A")
            git(self.root, "commit", "-qm", f"c{n}")
            self.shas.append(git(self.root, "rev-parse", "HEAD"))
        self.run_file = "docs/run.md"
        Path(self.root, self.run_file).write_text("# run\n", encoding="utf-8")
        self.W = ("--workflow", "plan-gates", "--run-file", self.run_file)
        self.episode = Path(self.root, "build", "claude-campaign-repair.json")

    def cli(self, *args):
        return subprocess.run([sys.executable, str(GUARD_PY), "repair", *args, "--root", self.root],
                              capture_output=True, text=True, encoding="utf-8", timeout=120)

    def attempts(self):
        s = self.shas
        return [self.cli("attempt", "--red", s[n - 1], "--commit", s[n], *self.W) for n in (1, 2, 3)]

    def test_attempts_count_across_processes_and_a_fourth_is_refused(self):
        outs = self.attempts()
        self.assertEqual([o.returncode for o in outs], [0, 0, 0], [o.stderr for o in outs])
        self.assertIn("attempt 3 of 3", outs[2].stdout)
        again = self.cli("attempt", "--red", self.shas[1], "--commit", self.shas[2], *self.W)
        self.assertIn("already counted", again.stdout)
        self.assertIn("3 of 3 attempts used", self.cli("status", "--run-file", self.run_file).stdout)
        fourth = self.cli("attempt", "--red", self.shas[3], "--commit", self.shas[4], *self.W)
        self.assertEqual(fourth.returncode, 1)
        self.assertIn("bound is exhausted", fourth.stdout + fourth.stderr)

    def test_a_mismatched_episode_is_refused(self):
        self.attempts()
        other = self.cli("attempt", "--red", self.shas[3], "--commit", self.shas[4], "--workflow", "release",
                         "--run-file", self.run_file)
        self.assertEqual(other.returncode, 1)
        self.assertIn("refusing to mix episodes", other.stderr)

    def test_unreadable_or_malformed_state_refuses_rather_than_resetting(self):
        self.attempts()
        for label, body in (("unreadable", "{not json"), ("malformed", "null")):
            self.episode.write_text(body, encoding="utf-8")
            bad = self.cli("attempt", "--red", self.shas[3], "--commit", self.shas[5], *self.W)
            self.assertEqual(bad.returncode, 1, label)
            self.assertIn("escalate rather than repair", bad.stderr, label)

    def test_close_needs_green_evidence_on_a_descendant(self):
        s = self.shas
        self.cli("attempt", "--red", s[0], "--commit", s[1], *self.W)
        no_ev = self.cli("close", "--green", s[5], *self.W, "--evidence", f"ci-wait: {s[5][:12]} plan-gates started no run")
        self.assertEqual(no_ev.returncode, 1)
        not_desc = self.cli("close", "--green", s[0], *self.W, "--evidence", f"ci-wait: {s[0][:12]} plan-gates success x")
        self.assertEqual(not_desc.returncode, 1)
        self.assertIn("does not descend", not_desc.stderr)
        closed = self.cli("close", "--green", s[5], *self.W, "--evidence", f"ci-wait: {s[5][:12]} plan-gates success https://x")
        self.assertEqual(closed.returncode, 0, closed.stderr)
        fresh = self.cli("attempt", "--red", s[4], "--commit", s[5], *self.W)
        self.assertIn("attempt 1 of 3", fresh.stdout)

    def test_a_lost_episode_is_detected_and_restored_from_the_run_file(self):
        outs = self.attempts()
        with open(os.path.join(self.root, self.run_file), "a", encoding="utf-8") as fh:
            for o in outs:
                fh.write(f"- {o.stdout.strip()}\n")
        self.episode.unlink()
        lost = self.cli("status", "--run-file", self.run_file)
        self.assertEqual(lost.returncode, 1)
        self.assertIn("run repair restore", lost.stderr)
        blocked = self.cli("attempt", "--red", self.shas[5], "--commit", self.shas[3], *self.W)
        self.assertIn("run repair restore first", blocked.stderr)
        self.assertEqual(self.cli("restore", "--run-file", self.run_file).returncode, 1)
        restored = self.cli("restore", *self.W)
        self.assertIn("restored", restored.stdout)
        self.assertIn("3 of 3", restored.stdout)
        retry = self.cli("attempt", "--red", self.shas[2], "--commit", self.shas[3], *self.W)
        self.assertIn("already counted", retry.stdout)

    def test_the_ceiling_allows_one_re_run_per_run(self):
        first, second = self.cli("ceiling", "--run-id", "777"), self.cli("ceiling", "--run-id", "777")
        self.assertEqual((first.returncode, second.returncode), (0, 1))
        self.assertIn("already had its one re-run", second.stderr)


class TextStats(unittest.TestCase):
    """`open_rows` reads Gemail's text `query stats` summary, so `end --reason plan-done` can check every row stamped."""

    def graph(self, body):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        os.makedirs(os.path.join(tmp.name, "scripts"))
        Path(tmp.name, "scripts", "todo-graph.py").write_text(f"print({body!r})\n", encoding="utf-8")
        return tmp.name

    def test_the_text_summary_gives_the_open_rows(self):
        root = self.graph("domains          9\nsections         118\n  done [x]       5\n  open [ ]       113\n")
        self.assertEqual(guard.open_rows(root), 113)

    def test_the_json_summary_still_reads(self):
        self.assertEqual(guard.open_rows(self.graph(json.dumps({"total": 4, "verified": 4}))), 0)

    def test_an_unknown_summary_is_unknown(self):
        self.assertIsNone(guard.open_rows(self.graph("nothing useful")))

    def test_this_projects_graph_is_read(self):
        self.assertIsInstance(guard.open_rows(str(REPO)), int)


if __name__ == "__main__":
    unittest.main()
