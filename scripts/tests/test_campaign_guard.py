"""scripts/campaign_guard.py, the process-plan run guard: the Stop hook against a throwaway workspace, and the
lifecycle commands.

Imported from the Conclave-SDK todo kit (tests/test_campaign_guard.py at SDK c48fd1b, 2026-11-15) with the guard
read from this project's scripts/. Run: python -m unittest discover -s scripts/tests -t .
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import threading
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
GUARD_PY = REPO / "scripts" / "campaign_guard.py"
SDK_ONLY = "needs the Conclave-SDK checkout (its kit templates and fixtures), not this project"
SESSION = "11111111-2222-3333-4444-555555555555"
OTHER = "99999999-8888-7777-6666-555555555555"
RUN_FILE = "docs/phase-runs/2099-01-01-phase-0.md"

spec = importlib.util.spec_from_file_location("campaign_guard_under_test", GUARD_PY)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

# The fake graph answers `query ready` the way the test asks: the SDK's JSON list, or Isotone's text summary.
FAKE_GRAPH = """import json, os, sys
if sys.argv[2:3] == ["stats"]:  # open rows from open.txt (none when absent)
    path = os.path.join(os.path.dirname(__file__), 'open.txt')
    still_open = int(open(path).read()) if os.path.exists(path) else 0
    print(json.dumps({"total": 10, "verified": 10 - still_open}))
    sys.exit(0)
mode, n = open(os.path.join(os.path.dirname(__file__), 'ready.txt')).read().split()
rows = [{"ref": "D00 T01 \\u00a73", "title": "Interface SPEC and screenshots", "phase": 0}] * int(n)
if mode == "mixed":  # this phase's rows, and one ready row of a later phase
    print(json.dumps(rows + [{"ref": "D05 T01 \\u00a71", "title": "Kit manager", "phase": 5}]))
elif mode == "json":
    print(json.dumps(rows, indent=2))
elif mode == "crash":
    sys.exit(1)
elif mode == "sleep":
    import time
    time.sleep(int(n))
else:
    if rows:
        print("00-design/TODO-01.md \\u00a73  Interface SPEC and screenshots")
    print()
    print(f"{n} runnable now, 0 runnable elsewhere")
"""


def alive(pid):
    """Whether process `pid` still runs (tasklist on Windows, signal 0 elsewhere)."""
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self._tmp.name, "ws")
        for folder in ("scripts", "build", "docs/phase-runs"):
            os.makedirs(os.path.join(self.root, folder))
        shutil.copy(GUARD_PY, os.path.join(self.root, "scripts", "campaign_guard.py"))
        self.write("scripts/todo-graph.py", FAKE_GRAPH)
        self.write(".gitignore", "build/\nscripts/ready.txt\nscripts/open.txt\n")
        self.ready(3)
        self.write(RUN_FILE, "# Phase run: Phase 0\n\n## Critical events\n")
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
                     ["config", "commit.gpgsign", "false"], ["add", "-A"], ["commit", "-qm", "seed"]):
            subprocess.run(["git", *args], cwd=self.root, capture_output=True, check=True)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text, mode="w"):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode, encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    def ready(self, n, mode="json"):
        self.write("scripts/ready.txt", f"{mode} {n}")

    def acquire(self, session=SESSION, **kw):
        cron_id = kw.pop("cron_id", "job-1")
        return guard.acquire(self.root, session, 0, RUN_FILE, cron_id, **kw)

    def run_id(self):
        return guard.read_guard(self.root)["run_id"]

    def hook(self, session=SESSION, payload=None):
        code, out = guard.stop_hook(payload if payload is not None else
                                    json.dumps({"session_id": session, "cwd": self.root, "hook_event_name": "Stop"}),
                                    self.root)
        self.assertEqual(code, 0, "the hook always exits 0")
        return json.loads(out) if out else None

    def state(self):
        return guard._read_state(self.root)


class StopHook(Workspace):
    @unittest.skip(SDK_ONLY)
    def real_graph(self, needs):
        """The kit's own graph in the workspace, over one open section with `needs`."""
        sys.path.insert(0, str(REPO / "tests"))
        from test_todo_graph import todo_file  # the graph tests' fixture writer
        kit = REPO / "kits" / "todo" / "templates" / "scripts"
        shutil.copytree(kit, os.path.join(self.root, "scripts"), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "tests", "campaign_guard.py"))
        self.write("todo/00-workspace/TODO-01-a.md", todo_file([(1, "Needs a GPU", 0, needs, "--")]))
        self.write("todo/00-workspace/INDEX.md", "# Index\n- TODO-01-a.md\n")
        self.write("todo/TODO-00-INDEX.md", "# Index\n- 00-workspace/TODO-01-a.md\n")
        self.write("todo/plan.json", json.dumps({"needs": ["gpu"]}))

    def test_a_row_needing_a_host_this_session_lacks_does_not_hold_the_turn(self):
        # D03 T01 §10: the Stop hook counts with the session's set (`--have auto`), so a host-bound row lets it end.
        self.acquire()
        self.real_graph("gpu")
        with mock.patch.dict(os.environ, {"CONCLAVE_HAVE": ""}):
            self.assertEqual(guard.ready_rows(self.root), (0, ""))
            self.assertIsNone(self.hook())
        with mock.patch.dict(os.environ, {"CONCLAVE_HAVE": "gpu"}):  # the session declares it: the row holds the turn
            self.assertEqual(guard.ready_rows(self.root)[0], 1)
            self.assertEqual(self.hook()["decision"], "block")

    def test_a_graph_without_have_is_asked_without_it(self):
        self.write("scripts/todo-graph.py", "import json, sys\n"
                   "if '--have' in sys.argv:\n"
                   "    print('todo-graph.py: error: unrecognized arguments: --have auto', file=sys.stderr)\n"
                   "    sys.exit(2)\n"
                   "print(json.dumps([{'ref': 'D00 T01 \\u00a71', 'title': 'Old', 'phase': 0}]))\n")
        self.assertEqual(guard.ready_rows(self.root), (1, "D00 T01 §1  Old"))

    def test_a_probe_the_real_graph_runs_ends_with_the_stop_hooks_query(self):
        # D03 T01 §10 (completion): the actual path, the kit's graph running a project's probe that starts a child.
        self.real_graph("gpu")
        pid_file = os.path.join(self.root, "child.pid")
        probe = ("import subprocess, sys, time; "
                 "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); "
                 f"open(r'{pid_file}', 'w').write(str(p.pid)); time.sleep(60)")
        self.write("todo/plan.json", json.dumps({"needs": ["gpu"], "probes": {"gpu": [sys.executable, "-c", probe]}}))
        self.assertEqual(guard.ready_rows(self.root, timeout=4), (None, ""))
        child = int(open(pid_file).read())
        for _ in range(80):
            if not alive(child):
                break
            time.sleep(0.1)
        self.assertFalse(alive(child), "the probe's child outlived the Stop hook's query")

    def test_a_graph_past_its_timeout_is_ended_with_its_children(self):
        pid_file = os.path.join(self.root, "child.pid")
        self.write("scripts/todo-graph.py", "import subprocess, sys, time\n"
                   "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
                   f"open(r'{pid_file}', 'w').write(str(p.pid))\n"
                   "time.sleep(60)\n")
        started = time.monotonic()
        self.assertEqual(guard.ready_rows(self.root, timeout=3), (None, ""))
        self.assertLess(time.monotonic() - started, 30)
        child = int(open(pid_file).read())
        for _ in range(50):
            if not alive(child):
                break
            time.sleep(0.1)
        self.assertFalse(alive(child), "a probe the graph started outlived the Stop hook's query")

    def test_no_guard_another_session_or_an_empty_payload_allows(self):
        self.assertIsNone(self.hook())
        self.acquire()
        self.assertIsNone(self.hook(session=OTHER))
        self.assertIsNone(self.hook(payload=""))

    def test_an_open_run_blocks_and_names_the_next_ready_row(self):
        self.acquire()
        decision = self.hook()
        self.assertEqual(decision["decision"], "block")
        self.assertIn("Next ready row: D00 T01 §3  Interface SPEC and screenshots.", decision["reason"])
        self.assertIn(f"## Closeout run={self.run_id()}", decision["reason"])
        self.assertEqual(self.state()["blocks"], 1)

    def test_a_text_summary_graph_is_read_too(self):
        self.acquire()
        self.ready(2, "text")
        self.assertIn("Next ready row: 00-design/TODO-01.md", self.hook()["reason"])
        self.ready(0, "text")
        self.assertIsNone(self.hook())

    def test_nothing_runnable_allows(self):
        self.acquire()
        self.ready(0)
        self.assertIsNone(self.hook())

    def test_an_unreadable_graph_still_blocks(self):
        self.acquire()
        self.ready(0, "crash")
        self.assertEqual(self.hook()["decision"], "block")

    def test_only_this_runs_markers_end_it(self):
        self.acquire()
        self.write(RUN_FILE, "## Closeout run=abcdef123456\nPARKED 2099-01-01T00:00:00Z run=abcdef123456 old\n", "a")
        self.assertEqual(self.hook()["decision"], "block", "an old run's markers ended this run")
        self.write(RUN_FILE, f"PARKED 2099-01-02T00:00:00Z run={self.run_id()} blocked here\n", "a")
        self.assertIsNone(self.hook())

    def test_a_closeout_with_this_runs_id_allows(self):
        self.acquire()
        self.write(RUN_FILE, f"\n## Closeout run={self.run_id()}\n\nShipped.\n", "a")
        self.assertIsNone(self.hook())

    def test_the_breaker_trips_after_three_blocks_without_progress(self):
        self.acquire()
        for push in (1, 2, 3):
            self.assertEqual(self.hook()["decision"], "block", push)
        self.assertIsNone(self.hook(), "the fourth stop without progress must be allowed")
        self.assertEqual((self.state()["trips"], self.state()["stalled"]), (1, True))

    def test_bookkeeping_is_not_progress_and_real_work_is(self):
        self.acquire()
        for _ in range(3):
            self.hook()
        self.write(RUN_FILE, "- bookkeeping: heartbeat resumed 2099-01-01T00:00:00Z\n", "a")
        self.assertIsNone(self.hook(), "a bookkeeping line reset the breaker")
        for change in (lambda: self.write("notes.txt", "new untracked file\n"),
                       lambda: self.write("notes.txt", "same file, new content\n"),
                       lambda: self.write(RUN_FILE, "- Section D00 T01 §3 shipped\n", "a")):
            for _ in range(3):
                self.hook()
            change()
            decision = self.hook()
            self.assertIsNotNone(decision, "real progress did not reset the breaker")
            self.assertEqual(self.state()["blocks"], 1)

    def test_a_failure_fails_open_and_is_recorded_for_the_heartbeat(self):
        self.acquire()
        os.unlink(os.path.join(self.root, RUN_FILE))
        os.makedirs(os.path.join(self.root, RUN_FILE))  # opening the run file now raises
        self.assertIsNone(self.hook())
        line = guard.hook_error(self.root, SESSION)
        self.assertTrue(line.startswith("campaign-stop hook failed at "), line)
        with self.assertRaises(guard.GuardError):
            guard.hook_error(self.root, OTHER)
        with self.assertRaises(guard.GuardError):
            guard.hook_error(self.root, SESSION, ack="not the line")
        self.assertIn("acknowledged and cleared", guard.hook_error(self.root, SESSION, ack=line))
        self.assertEqual(guard.hook_error(self.root, SESSION), "")

    def test_a_malformed_guard_fails_open_into_its_own_error_file(self):
        self.write("build/claude-campaign-guard.json", "{not json")
        self.assertIsNone(self.hook())
        line = guard.hook_error(self.root)
        self.assertIn("recorded without the lock", line)
        guard.hook_error(self.root, ack=line)
        self.assertEqual(os.listdir(os.path.join(self.root, "build", "claude-campaign-hook-errors")), [])

    def test_the_breaker_trips_where_build_is_not_ignored(self):
        # The guard's own state writes must never pass for progress, whatever the project ignores.
        self.write(".gitignore", "scripts/ready.txt\n")
        subprocess.run(["git", "commit", "-qam", "stop ignoring build"], cwd=self.root, capture_output=True, check=True)
        self.acquire()
        for push in (1, 2, 3):
            self.assertEqual(self.hook()["decision"], "block", push)
        self.assertIsNone(self.hook(), "the hook's own state file reset the breaker")

    def test_tracked_copies_of_the_guards_files_are_not_progress_either(self):
        self.write(".gitignore", "scripts/ready.txt\n")
        self.acquire()
        self.hook()
        subprocess.run(["git", "add", "-A"], cwd=self.root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-qm", "track build"], cwd=self.root, capture_output=True, check=True)
        for push in (1, 2, 3):
            self.assertEqual(self.hook()["decision"], "block", push)
        self.assertIsNone(self.hook(), "a tracked state file reset the breaker")

    def test_a_phase_run_reads_and_pushes_only_its_phase(self):
        self.acquire(scope="phase")
        self.ready(1, "mixed")
        decision = self.hook()
        self.assertIn("of Phase 0 only", decision["reason"])
        self.assertNotIn("then the next phase", decision["reason"])
        self.assertIn("Next ready row: D00 T01 §3", decision["reason"])
        self.ready(0, "mixed")
        self.assertIsNone(self.hook(), "another phase's ready row held a phase-only run open")
        self.acquire(scope="plan")
        decision = self.hook()
        self.assertIn("Next ready row: D05 T01 §1", decision["reason"])
        self.assertIn("then the next phase", decision["reason"])

    def test_a_phase_run_on_a_text_graph_ends_only_on_its_marker(self):
        # A text summary names no phase: its count and rows belong to the whole plan, so a phase run ignores both.
        self.acquire(scope="phase")
        self.ready(1, "text")
        decision = self.hook()
        self.assertEqual(decision["decision"], "block")
        self.assertNotIn("Next ready row", decision["reason"], "a phase run was pointed at a row of unknown phase")
        self.ready(0, "text")
        self.assertEqual(self.hook()["decision"], "block", "another phase's empty count ended a phase run")
        self.write(RUN_FILE, f"## Closeout run={self.run_id()}\n", "a")
        self.assertIsNone(self.hook())

    def test_an_unacknowledged_hook_error_survives_a_later_stop(self):
        self.acquire()
        guard._record_hook_error(self.root, guard.read_guard(self.root), "OSError: transient")
        self.assertEqual(self.hook()["decision"], "block")
        line = guard.hook_error(self.root, SESSION)
        self.assertIn("OSError: transient", line)
        guard.hook_error(self.root, SESSION, ack=line)
        self.assertEqual(self.hook()["decision"], "block")
        self.assertEqual(guard.hook_error(self.root, SESSION), "")

    def test_the_hook_decides_inside_its_own_time_budget(self):
        self.acquire()
        self.ready(30, "sleep")
        os.environ["CAMPAIGN_HOOK_BUDGET_SECONDS"] = "4"
        try:
            started = __import__("time").monotonic()
            decision = self.hook()
            elapsed = __import__("time").monotonic() - started
        finally:
            del os.environ["CAMPAIGN_HOOK_BUDGET_SECONDS"]
        self.assertLess(elapsed, 12, "the hook waited on the graph past its budget")
        self.assertEqual(decision["decision"], "block", "an unreadable graph still blocks an open run")

    def test_the_configured_command_runs_the_hook_from_any_shell(self):
        settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        command = settings["hooks"]["Stop"][0]["hooks"][0]["command"]
        self.acquire()
        # Claude Code runs hooks through Git Bash on Windows; `bash` on PATH there is often WSL's, which would not
        # carry CLAUDE_PROJECT_DIR into Linux.
        bash = "bash"
        if os.name == "nt" and shutil.which("git"):
            bash = str(Path(shutil.which("git")).resolve().parents[1] / "bin" / "bash.exe")
        shells = [[bash, "-c"]] + ([["powershell.exe", "-NoProfile", "-Command"]] if os.name == "nt" else [])
        ran = 0
        for shell in shells:
            if not shutil.which(shell[0]):
                continue
            with self.subTest(shell=shell[0]):
                env = dict(os.environ, CLAUDE_PROJECT_DIR=self.root)
                payload = json.dumps({"session_id": SESSION, "cwd": self.root, "hook_event_name": "Stop"})
                proc = subprocess.run([*shell, command], input=payload, capture_output=True, text=True,
                                      encoding="utf-8", env=env, cwd=self._tmp.name, timeout=120)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(json.loads(proc.stdout)["decision"], "block", proc.stderr)
                ran += 1
        self.assertGreater(ran, 0, "no shell could run the configured hook")


class AntigravityPayload(Workspace):
    """Antigravity's Stop payload: `conversationId` and `workspacePaths`, answered `continue`. These call the hook with
    no `project_dir`, as Antigravity's wiring does, so the workspace comes from the payload."""

    def agy(self, session=SESSION, workspace=None, **extra):
        payload = {"conversationId": session, "workspacePaths": [workspace or self.root], **extra}
        code, out = guard.stop_hook(json.dumps(payload), None)
        self.assertEqual(code, 0, "the hook always exits 0")
        return json.loads(out) if out else None

    def raw(self, payload, project_dir=None):
        code, out = guard.stop_hook(json.dumps(payload), project_dir)
        self.assertEqual(code, 0, "the hook always exits 0")
        return out

    def test_a_guarded_conversation_is_found_through_its_workspace(self):
        self.acquire()
        here = os.getcwd()
        self.assertNotEqual(os.path.normcase(os.path.abspath(here)), os.path.normcase(os.path.abspath(self.root)))
        decision = self.agy()
        self.assertIsNotNone(decision, "an Antigravity payload for the guarded session was let through")
        self.assertEqual(self.state()["blocks"], 1)

    def test_an_explicit_project_dir_comes_before_the_payloads_workspace(self):
        self.acquire()
        elsewhere = os.path.join(self._tmp.name, "elsewhere")
        os.makedirs(elsewhere)
        out = self.raw({"conversationId": SESSION, "workspacePaths": [elsewhere]}, self.root)
        self.assertEqual(json.loads(out)["decision"], "continue")
        self.assertEqual(self.agy(workspace=elsewhere), None, "a workspace with no guard held the stop")

    def test_antigravity_is_answered_continue_and_claude_code_block(self):
        self.acquire()
        agy = self.agy()
        claude = self.hook()
        self.assertEqual(agy["decision"], "continue")
        self.assertEqual(claude["decision"], "block")
        self.assertEqual(agy["reason"].split(" (this is push")[0], claude["reason"].split(" (this is push")[0])
        self.assertEqual(self.state()["blocks"], 2)

    def test_the_guards_lifecycle_holds_for_antigravity(self):
        self.assertIsNone(self.agy(), "no guard held the stop")
        self.acquire()
        self.assertIsNone(self.agy(session=OTHER), "another conversation was held")
        for push in (1, 2, 3):
            self.assertEqual(self.agy()["decision"], "continue", push)
            self.assertEqual(self.state()["blocks"], push)
        self.assertIsNone(self.agy(), "the breaker did not let the fourth stop through")
        self.assertEqual((self.state()["trips"], self.state()["stalled"]), (1, True))
        self.ready(0)
        self.assertIsNone(self.agy(), "a run with nothing ready was held")
        self.ready(3)
        self.write("notes.txt", "progress\n")
        self.assertEqual(self.agy()["decision"], "continue")
        self.write(RUN_FILE, f"PARKED 2099-01-02T00:00:00Z run={self.run_id()} blocked here\n", "a")
        self.assertIsNone(self.agy(), "a parked run was held")

    def test_session_id_comes_before_conversation_id(self):
        self.acquire()
        both = {"session_id": SESSION, "conversationId": OTHER, "workspacePaths": [self.root]}
        self.assertEqual(json.loads(self.raw(both))["decision"], "continue")
        self.assertEqual(self.raw({**both, "session_id": OTHER, "conversationId": SESSION}), "")

    def test_this_runs_closeout_releases_an_antigravity_session(self):
        self.acquire()
        self.write(RUN_FILE, f"\n## Closeout run={self.run_id()}\n", "a")
        self.assertIsNone(self.agy())

    def test_a_cancel_or_a_busy_agent_ends_the_turn_without_a_block(self):
        self.acquire()
        for extra in ({"terminationReason": "USER_CANCELED"}, {"fullyIdle": False}):
            self.assertIsNone(self.agy(**extra), extra)
            self.assertEqual(self.state().get("blocks", 0), 0, extra)
        self.assertEqual(self.agy(fullyIdle=True)["decision"], "continue")

    def recorded(self):
        line = guard.hook_error(self.root, SESSION)
        self.assertTrue(line.startswith("campaign-stop hook failed at "), line)
        guard.hook_error(self.root, SESSION, ack=line)
        return line

    def test_a_missing_session_is_an_error_only_while_a_run_is_open(self):
        self.assertEqual(self.raw({"cwd": self.root, "hook_event_name": "Stop"}), "")
        self.assertFalse(os.path.exists(os.path.join(self.root, "build", "claude-campaign-hook-errors")))
        self.assertEqual(self.state(), {})
        self.acquire()
        self.assertEqual(self.raw({"cwd": self.root, "hook_event_name": "Stop"}), "")
        self.assertIn("names no session", self.recorded())

    def test_a_workspace_that_is_not_a_list_of_paths_is_recorded_in_the_cwd_workspace(self):
        self.acquire()
        for paths in ("not a list", [7]):
            self.assertEqual(self.raw({"conversationId": SESSION, "workspacePaths": paths, "cwd": self.root}), "")
            self.assertIn("workspacePaths is not a list of paths", self.recorded())
        self.assertEqual(self.raw({"conversationId": SESSION, "workspacePaths": "x"}), "", "no workspace at all")
        self.assertEqual(self.raw({"conversationId": SESSION, "workspacePaths": ["\0"], "cwd": self.root}), "")
        self.assertIn("workspacePaths is not a list of paths", self.recorded())

    def test_a_workspace_no_path_can_use_still_fails_open_through_the_command(self):
        payload = json.dumps({"conversationId": SESSION, "workspacePaths": ["\0"]})
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        proc = subprocess.run([sys.executable, str(GUARD_PY), "stop-hook"], input=payload, capture_output=True,
                              text=True, env=env, timeout=60)
        self.assertEqual((proc.returncode, proc.stdout), (0, ""), proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        # A root that cannot be used to record in: the recording fails, and the hook still fails open.
        with mock.patch.object(guard, "_record_hook_error", side_effect=ValueError("embedded null byte")):
            self.assertEqual(self.raw([1], self.root), "")

    def test_the_payload_antigravity_really_sends_is_held(self):
        """The Stop payload agy 1.5.5 sent to a probe hook (tests/fixtures/agy-stop-payload.json), paths filled in."""
        recorded = json.loads((Path(__file__).resolve().parent / "fixtures" / "agy-stop-payload.json").read_text(encoding="utf-8"))
        forward = self.root.replace("\\", "/")  # agy sends workspacePaths with forward slashes
        unguarded = os.path.join(self._tmp.name, "agent-cwd")  # only workspacePaths leads to the guard
        os.makedirs(unguarded)
        payload = {**recorded, "cwd": unguarded, "workspacePaths": [forward]}
        guard.acquire(self.root, recorded["conversationId"], 0, RUN_FILE, "job-1")
        self.assertEqual(json.loads(self.raw(payload))["decision"], "continue")
        self.assertEqual(self.raw({**payload, "workspacePaths": [], "cwd": ""}), "", "no workspace was held")

    def test_a_payload_that_is_not_an_object_fails_open(self):
        self.acquire()
        self.assertEqual(self.raw([1, 2], self.root), "")
        self.assertIn("not a JSON object", self.recorded())


class HeartbeatStill(Workspace):
    """`heartbeat-still`: a heartbeat resumption that found nothing changed, for a harness no Stop hook holds. It
    shares the Stop hook's fingerprint and trips, so the two observers agree on progress."""

    def still(self, session=SESSION):
        return guard.heartbeat_still(self.root, session)

    def commit(self, name):
        self.write(name, f"{name}\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-qm", name], cwd=self.root, capture_output=True, check=True)

    def test_the_first_call_sets_the_baseline_and_each_still_counts(self):
        self.acquire()
        self.assertIn("progress", self.still())
        self.assertEqual(self.state()["hb_still"], 0)
        self.assertIn("still 1 of", self.still())
        self.assertIn("still 2 of", self.still())
        self.assertEqual(self.state()["hb_still"], 2)

    def test_progress_resets_the_count_and_the_shared_trips(self):
        self.acquire()
        self.still()
        for _ in range(3):
            self.still()
        self.assertEqual(self.state()["hb_still"], 3)
        self.commit("first-work.txt")
        self.assertIn("progress", self.still())
        self.assertEqual(self.state()["hb_still"], 0, "progress left the still count")
        for _ in range(guard.MAX_HEARTBEAT_STILLS):
            self.still()
        self.assertEqual(self.state()["trips"], 1)
        self.commit("real-work.txt")
        self.assertIn("progress", self.still())
        self.assertEqual((self.state()["hb_still"], self.state()["trips"]), (0, 0))
        for _ in range(guard.MAX_HEARTBEAT_STILLS):
            self.still()
        self.assertIsNotNone(guard.read_guard(self.root), "a trip from before the progress ended the run")
        self.assertEqual(self.state()["trips"], 1)

    def test_held_through_eleven_stills_and_released_at_the_twelfth(self):
        self.acquire()
        self.still()  # the baseline
        for n in range(1, 2 * guard.MAX_HEARTBEAT_STILLS):
            line = self.still()
            self.assertIsNotNone(guard.read_guard(self.root), f"released at still {n}")
            expected = (1, 0) if n == guard.MAX_HEARTBEAT_STILLS else (
                (0, n) if n < guard.MAX_HEARTBEAT_STILLS else (1, n - guard.MAX_HEARTBEAT_STILLS))
            self.assertEqual((self.state()["trips"], self.state()["hb_still"]), expected, (n, line))
        line = self.still()
        self.assertIn("second trip", line)
        self.assertIn("end: stall", line)
        self.assertIsNone(guard.read_guard(self.root), "two trips left the guard held")
        self.assertIn("job-1", Path(self.root, "build", "claude-campaign-pending-cancel.json").read_text(encoding="utf-8"))

    def test_the_stop_hook_and_the_heartbeat_share_progress_and_trips(self):
        self.acquire()
        self.still()
        self.still()
        self.assertEqual(self.state()["hb_still"], 1)
        for push in (1, 2, 3):
            self.hook()
            self.assertEqual((self.state()["blocks"], self.state()["hb_still"]), (push, 1), "the hook dropped the count")
        self.assertIsNone(self.hook(), "the breaker did not trip")
        self.assertEqual((self.state()["trips"], self.state()["hb_still"]), (1, 1))
        print_ = self.state()["fingerprint"]
        for n in range(2, guard.MAX_HEARTBEAT_STILLS):
            self.still()
            self.assertEqual((self.state()["fingerprint"], self.state()["hb_still"]), (print_, n))
        self.assertIn("end: stall", self.still(), "the hook's trip did not count toward the heartbeat's release")
        # A change the Stop hook sees resets the heartbeat's count too.
        self.acquire(session=OTHER, cron_id="job-2")
        guard.heartbeat_still(self.root, OTHER)
        guard.heartbeat_still(self.root, OTHER)
        self.commit("seen-by-the-hook.txt")
        self.hook(session=OTHER)
        self.assertEqual((self.state()["hb_still"], self.state()["trips"]), (0, 0))

    def test_a_second_trip_the_stop_hook_counts_ends_the_run_at_the_next_heartbeat(self):
        self.acquire()
        self.still()  # the baseline
        for _ in range(guard.MAX_HEARTBEAT_STILLS):
            self.still()
        self.assertEqual(self.state()["trips"], 1)
        for _ in range(3):
            self.hook()
        self.assertIsNone(self.hook(), "the hook's breaker did not trip")
        self.assertEqual(self.state()["trips"], 2)
        self.assertIsNotNone(guard.read_guard(self.root))
        line = self.still()
        self.assertIn("end: stall", line)
        self.assertIsNone(guard.read_guard(self.root), "two trips left the guard held")

    def run_cli(self, session):
        return subprocess.run([sys.executable, os.path.join(self.root, "scripts", "campaign_guard.py"),
                               "heartbeat-still", "--root", self.root, "--session", session],
                              capture_output=True, text=True, timeout=120)

    def test_the_command_line_counts_releases_and_refuses(self):
        state_path = guard._paths(self.root)[1]
        result = self.run_cli(SESSION)
        self.assertEqual(result.returncode, 1, "no guard: refused")
        self.assertFalse(os.path.exists(state_path))
        self.acquire()
        self.assertEqual(self.run_cli(SESSION).returncode, 0)
        self.assertIn("still 1 of", self.run_cli(SESSION).stdout)
        self.assertEqual(self.state()["hb_still"], 1)
        before = Path(state_path).read_bytes()
        result = self.run_cli(OTHER)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(Path(state_path).read_bytes(), before)
        last = None
        for _ in range(2 * guard.MAX_HEARTBEAT_STILLS - 1):  # stills 2 to 12 after the baseline and still 1
            last = self.run_cli(SESSION)
        assert last is not None
        self.assertIn("end: stall", last.stdout)
        self.assertIsNone(guard.read_guard(self.root))


# The SDK todo kit's hook files for all three agents, kept as fixtures so the self-test is exercised in every
# format; the guard under test is always this project's own.
TEMPLATES = Path(__file__).resolve().parent / "fixtures" / "todo-kit"
FAKE_HOOK = """import subprocess, sys, time
mode, pid_file = sys.argv[1], sys.argv[2]
if mode == "empty":
    print("{}")
elif mode == "text":
    print("not json at all")
elif mode in ("block", "continue"):
    print('{"decision": "%s", "reason": "a reason"}' % mode)
elif mode == "chatty":  # a diagnostic line before an otherwise valid answer: stdout is not one JSON object
    print("diagnostic: starting")
    print('{"decision": "continue", "reason": "a reason"}')
elif mode == "sleep":  # a hook that starts a child and outlives its limit
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    open(pid_file, "w").write(str(child.pid))
    time.sleep(120)
"""


def process_alive(pid):
    """Whether a process id is still running, asked of the OS; a process that cannot be inspected raises."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = wintypes.HANDLE
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            if ctypes.get_last_error() == 87:  # no process has this id
                return False
            raise OSError(ctypes.get_last_error(), f"cannot inspect process {pid}")
        try:
            code = wintypes.DWORD()
            kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
            return code.value == 259  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def end_process(pid):
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    else:
        try:
            os.kill(pid, 9)
        except ProcessLookupError:
            pass


class SelfTest(unittest.TestCase):
    """`--self-test`: each hook file's own command, run as its harness runs it, against a throwaway guarded run."""

    FILES = (".claude/settings.json", ".agents/hooks.json", ".codex/hooks.json")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.project = Path(self._tmp.name) / "project"
        for rel in ("scripts/campaign_guard.py", "scripts/codex-campaign-hook.py", *self.FILES):
            (self.project / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(GUARD_PY if rel == "scripts/campaign_guard.py" else TEMPLATES / rel, self.project / rel)
        self.fake = Path(self._tmp.name) / "fake_hook.py"
        self.fake.write_text(FAKE_HOOK, encoding="utf-8")
        self.pid_file = Path(self._tmp.name) / "child.pid"

    def run_self_test(self, limit=60, only=None):
        code, lines = guard._self_test(str(self.project), limit, only)
        workspace = lines[0].split("workspace ", 1)[1]
        self.assertFalse(os.path.exists(workspace), "the self-test left its workspace behind")
        return code, lines

    def test_one_hook_file_is_tested_alone_and_another_agents_broken_file_does_not_count(self):
        # D02 T02 §3: the unattended preflight checks the one agent a run uses.
        (self.project / ".agents/hooks.json").write_text("{not json", encoding="utf-8")
        code, lines = self.run_self_test()
        self.assertEqual(code, 1)
        code, lines = self.run_self_test(only=".claude/settings.json")
        self.assertEqual(code, 0, lines)
        self.assertEqual([line for line in lines[1:]], ["self-test: .claude/settings.json: ok (block)"])
        (self.project / ".codex/hooks.json").unlink()
        code, lines = self.run_self_test(only=".codex/hooks.json")
        self.assertEqual((code, lines[1:]), (1, ["self-test: FAIL .codex/hooks.json: absent"]))

    def test_a_hook_that_failed_open_on_a_stalled_fingerprint_gets_one_more_try(self):
        # The quick suite on a loaded machine (2026-11-12): one untracked read in the self-test's workspace took over
        # FILE_SECONDS, the hook failed open, and the self-test called a sound hook broken.
        real = guard._run_wired
        calls = []

        def stalled_once(command, hook_file, workspace, payload, limit):
            calls.append(hook_file)
            if len(calls) == 1:
                guard._record_hook_error(workspace, None, f"GuardError: {guard.STALL_REASON}")
                return 0, ""
            return real(command, hook_file, workspace, payload, limit)
        with mock.patch.object(guard, "_run_wired", stalled_once):
            code, lines = self.run_self_test(only=".claude/settings.json")
        self.assertEqual(code, 0, lines)
        self.assertEqual(calls, [".claude/settings.json"] * 2)

    def test_a_hook_that_failed_open_for_another_reason_fails_at_once_naming_it(self):
        calls = []

        def broken(command, hook_file, workspace, payload, limit):
            calls.append(hook_file)
            guard._record_hook_error(workspace, None, "GuardError: the run file is unreadable")
            return 0, ""
        with mock.patch.object(guard, "_run_wired", broken):
            code, lines = self.run_self_test(only=".claude/settings.json")
        self.assertEqual(code, 1)
        self.assertEqual(len(calls), 1, "a non-transient failure was retried")
        self.assertIn("(it failed open: GuardError: the run file is unreadable", lines[-1])
    def test_the_command_line_takes_one_known_hook_file(self):
        for argv in (["--self-test", "--hook-file"], ["--self-test", "--hook-file", "other.json"],
                     ["--self-test", "--root", "x"]):
            with self.subTest(argv=argv):
                self.assertEqual(guard.main(argv), 2)
    def fake_command(self, mode, markers="campaign_guard.py stop-hook"):
        return f"{Path(sys.executable).as_posix()} {self.fake.as_posix()} {mode} {self.pid_file.as_posix()} {markers}"

    def set_command(self, hook_file, command):
        path = self.project / hook_file
        doc = json.loads(path.read_text(encoding="utf-8"))
        if hook_file.startswith(".agents"):
            doc["campaign-guard"]["Stop"][0]["command"] = command
        else:
            handler = doc["hooks"]["Stop"][0]["hooks"][0]
            handler["command"] = command
            if "commandWindows" in handler:
                handler["commandWindows"] = command
        path.write_text(json.dumps(doc), encoding="utf-8")

    def test_a_seeded_install_runs_three_hooks_each_in_its_own_format(self):
        code, lines = self.run_self_test()
        self.assertEqual(code, 0, lines)
        self.assertEqual(lines[1:], ["self-test: .claude/settings.json: ok (block)",
                                     "self-test: .agents/hooks.json: ok (continue)",
                                     "self-test: .codex/hooks.json: ok (block)"])

    def test_this_projects_own_checkout_passes_through_the_command_line(self):
        proc = subprocess.run([sys.executable, str(REPO / "scripts" / "campaign_guard.py"), "--self-test"],
                              capture_output=True, text=True, timeout=300)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        # Gemail wires Claude Code only: its settings file is tested, the other agents' files are absent.
        self.assertIn("self-test: .claude/settings.json: ok (block)", proc.stdout)

    def test_a_broken_settings_file_in_a_scratch_sdk_copy_fails_through_the_command_line(self):
        sdk = Path(self._tmp.name) / "sdk"
        for rel in ("scripts/campaign_guard.py", ".claude/settings.json"):
            (sdk / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / rel, sdk / rel)
        settings = sdk / ".claude" / "settings.json"
        broken = settings.read_text(encoding="utf-8").replace("'campaign_guard.py'", "'campaign_guard_gone.py'")
        self.assertNotEqual(broken, settings.read_text(encoding="utf-8"), "the settings file names no script to break")
        settings.write_text(broken, encoding="utf-8")
        proc = subprocess.run([sys.executable, str(sdk / "scripts" / "campaign_guard.py"), "--self-test"],
                              capture_output=True, text=True, timeout=300)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertTrue([line for line in proc.stdout.splitlines() if "FAIL .claude/settings.json" in line], proc.stdout)

    @unittest.skipUnless(os.name == "nt", "Claude Code runs hooks through Git Bash on Windows only")
    def test_no_git_bash_fails_the_claude_hook_rather_than_using_another_shell(self):
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_GIT_BASH_PATH": ""}), \
                mock.patch.object(guard.shutil, "which", return_value=None):
            code, lines = self.run_self_test()
        self.assertEqual(code, 1, lines)
        self.assertTrue([line for line in lines if "FAIL .claude/settings.json" in line and "Git Bash" in line], lines)
        missing = str(Path(self._tmp.name) / "no-bash.exe")
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_GIT_BASH_PATH": missing}):
            code, lines = self.run_self_test()
        self.assertEqual(code, 1, lines)
        self.assertTrue([line for line in lines if "FAIL .claude/settings.json" in line and "not a file" in line], lines)

    def test_a_hook_file_the_project_lacks_is_absent_not_a_failure(self):
        (self.project / ".codex/hooks.json").unlink()
        code, lines = self.run_self_test()
        self.assertEqual(code, 0, lines)
        self.assertIn("self-test: .codex/hooks.json: absent", lines)

    def test_each_broken_seed_fails_naming_its_file(self):
        for hook_file in self.FILES:
            with self.subTest(hook_file):
                original = (self.project / hook_file).read_text(encoding="utf-8")
                broken = original.replace("campaign_guard.py", "campaign_guard.py.missing") if "codex" not in hook_file \
                    else original.replace("codex-campaign-hook.py", "codex-campaign-hook.py.missing")
                # The marker still names the campaign command; the script it points at does not exist.
                (self.project / hook_file).write_text(broken, encoding="utf-8")
                code, lines = self.run_self_test()
                (self.project / hook_file).write_text(original, encoding="utf-8")
                self.assertEqual(code, 1, lines)
                failures = [line for line in lines if "FAIL" in line]
                self.assertEqual(len(failures), 1, lines)
                self.assertIn(hook_file, failures[0])

    def test_an_answer_that_is_not_this_agents_decision_fails(self):
        for mode in ("empty", "text", "block", "chatty"):  # {}, not JSON, Claude Code's decision, a line before the JSON
            with self.subTest(mode):
                self.set_command(".agents/hooks.json", self.fake_command(mode))
                code, lines = self.run_self_test()
                self.assertEqual(code, 1, lines)
                self.assertTrue([line for line in lines if "FAIL .agents/hooks.json" in line and "continue" in line], lines)
        self.set_command(".codex/hooks.json", self.fake_command("empty", "codex-campaign-hook.py"))
        self.set_command(".agents/hooks.json", self.fake_command("continue"))
        code, lines = self.run_self_test()
        self.assertEqual(code, 1, lines)
        self.assertTrue([line for line in lines if "FAIL .codex/hooks.json" in line], lines)
        self.assertIn("self-test: .agents/hooks.json: ok (continue)", lines)

    def test_a_file_with_no_enabled_campaign_command_fails_with_its_reason(self):
        seed = json.loads((self.project / ".agents/hooks.json").read_text(encoding="utf-8"))
        hook = seed["campaign-guard"]
        cases = {
            "only disabled": ({"campaign-guard": {**hook, "enabled": False}}, 1, "only disabled"),
            "no campaign command": ({"lint": {"Stop": [{"command": "./lint.sh"}]}}, 1, "no campaign Stop command"),
            "disabled beside enabled": ({"off": {**hook, "enabled": False}, "on": hook}, 0, "ok (continue)"),
        }
        for name, (doc, expected, text) in cases.items():
            with self.subTest(name):
                (self.project / ".agents/hooks.json").write_text(json.dumps(doc), encoding="utf-8")
                code, lines = self.run_self_test()
                self.assertEqual(code, expected, lines)
                self.assertTrue([line for line in lines if ".agents/hooks.json" in line and text in line], lines)
        (self.project / ".agents/hooks.json").write_text("{not json", encoding="utf-8")
        code, lines = self.run_self_test()
        self.assertEqual(code, 1)
        self.assertTrue([line for line in lines if "FAIL .agents/hooks.json" in line and "does not parse" in line], lines)

    def test_an_interrupt_ends_the_running_hook_and_its_child(self):
        self.set_command(".agents/hooks.json", self.fake_command("sleep"))
        real = subprocess.Popen.communicate
        calls = []

        def interrupted(proc, *args, **kwargs):
            calls.append(1)
            if len(calls) == 1:  # the first wait is the hook; the interrupt lands while it runs
                deadline = time.monotonic() + 30
                while not self.pid_file.exists() and time.monotonic() < deadline:
                    time.sleep(0.1)
                raise KeyboardInterrupt
            return real(proc, *args, **kwargs)

        with mock.patch.object(subprocess.Popen, "communicate", interrupted), self.assertRaises(KeyboardInterrupt):
            guard._run_wired(self.fake_command("sleep"), ".agents/hooks.json", str(self.project), "{}", 60)
        child = int(self.pid_file.read_text())
        self.addCleanup(end_process, child)
        deadline = time.monotonic() + 10
        while process_alive(child) and time.monotonic() < deadline:
            time.sleep(0.2)
        self.assertFalse(process_alive(child), "an interrupt left the hook's child running")

    def test_a_hook_that_outlives_its_limit_is_ended_with_its_child(self):
        self.set_command(".agents/hooks.json", self.fake_command("sleep"))
        began = time.monotonic()
        code, lines = self.run_self_test(limit=5)
        elapsed = time.monotonic() - began
        if self.pid_file.exists():
            self.addCleanup(end_process, int(self.pid_file.read_text()))
        self.assertEqual(code, 1, lines)
        self.assertTrue([line for line in lines if "FAIL .agents/hooks.json" in line and "ran past 5 seconds" in line], lines)
        self.assertTrue(self.pid_file.exists(), "the fake hook never started its child")
        self.assertFalse(process_alive(int(self.pid_file.read_text())), "the hook's child outlived the self-test")
        # Ending only the direct child leaves the rest holding the pipes until their own 120 second sleep ends.
        self.assertLess(elapsed, 90, "the self-test waited on a process tree it should have ended")


class Lifecycle(Workspace):
    def test_acquire_is_exclusive_and_a_handover_is_recorded(self):
        self.assertIn("guard created", self.acquire())
        rid = self.run_id()
        with self.assertRaises(guard.GuardError):
            self.acquire(session=OTHER, cron_id="job-2")
        self.assertIn("handed over", self.acquire(session=OTHER, cron_id="job-2", handover="session died"))
        doc = guard.read_guard(self.root)
        self.assertEqual((doc["handover_from"], doc["run_id"], doc["cron_id"]), (SESSION, rid, "job-2"))
        self.assertIn("re-pointed", self.acquire(session=OTHER, cron_id="job-3"))
        self.assertEqual(self.run_id(), rid, "a re-point of the same run keeps its id")

    def test_the_guard_keeps_the_unattended_runs_tag(self):
        # D02 T02 §6: Codex and Antigravity choose their own session ids, so the launcher knows its run's guard by tag.
        with mock.patch.dict(os.environ, {"CONCLAVE_UNATTENDED_TAG": "tag-1"}):
            self.acquire()
        self.assertEqual(guard.read_guard(self.root)["launch_tag"], "tag-1")
        env = {k: v for k, v in os.environ.items() if k != "CONCLAVE_UNATTENDED_TAG"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.acquire(session=OTHER, cron_id="job-2", handover="restart")
        self.assertNotIn("launch_tag", guard.read_guard(self.root), "an untagged acquire kept another run's tag")
    def test_end_records_how_the_run_ended(self):
        # D02 T02 §7: the heartbeat polls, so a run that ends between two ticks is known only by this record.
        with mock.patch.dict(os.environ, {"CONCLAVE_UNATTENDED_TAG": "tag-7"}):
            self.acquire()
        rid = self.run_id()
        self.write(RUN_FILE, f"# Run\n\nPARKED 2026-11-12T00:00:00Z run={rid} nothing runnable\n")
        guard.end(self.root, SESSION, "park")
        ended = json.loads(Path(self.root, "build", guard.ENDED_FILE).read_text(encoding="utf-8"))
        self.assertEqual((ended["run_id"], ended["session_id"], ended["launch_tag"], ended["reason"]),
                         (rid, SESSION, "tag-7", "park"))
    def test_a_torn_guard_needs_a_handover_and_the_scope_is_kept(self):
        self.write("build/claude-campaign-guard.json", "")
        with self.assertRaises(guard.GuardError):
            self.acquire()
        self.assertIn("handed over", self.acquire(handover="torn guard after a crash", scope="phase"))
        self.assertEqual(guard.read_guard(self.root)["handover_from"], "<unreadable guard>")
        self.acquire(cron_id="job-2")
        self.assertEqual(guard.read_guard(self.root)["scope"], "phase", "a re-point dropped the scope")
        self.assertTrue(guard.whoami(self.root, SESSION).endswith("scope=phase"))
        with self.assertRaises(guard.GuardError):
            self.acquire(scope="everything")
        self.acquire(session=OTHER, cron_id="job-3", handover="resumed in a new session")
        self.assertEqual(guard.read_guard(self.root)["scope"], "phase", "a handover widened a phase run to the plan")

    def test_a_guard_write_that_fails_part_way_leaves_nothing_behind(self):
        real_dump = guard.json.dump

        def torn(doc, fh, **kw):
            fh.write('{"runner": "cla')
            raise OSError(28, "No space left on device")

        guard.json.dump = torn
        try:
            with self.assertRaises(OSError):
                self.acquire()
        finally:
            guard.json.dump = real_dump
        self.assertEqual(sorted(os.listdir(os.path.join(self.root, "build"))), ["claude-campaign-guard.lock"])
        self.assertIn("guard created", self.acquire())

    def test_a_failed_update_keeps_the_existing_guard_byte_for_byte(self):
        self.acquire()
        path = os.path.join(self.root, "build", "claude-campaign-guard.json")
        with open(path, "rb") as fh:
            before = fh.read()
        real_dump, real_replace, replaced = guard.json.dump, guard.os.replace, []

        def torn(doc, fh, **kw):
            fh.write('{"runner": "cla')
            raise OSError(28, "No space left on device")

        def spy(src, dst):
            replaced.append((src, dst))
            return real_replace(src, dst)

        guard.json.dump = torn
        try:
            with self.assertRaises(OSError):
                self.acquire(cron_id="job-2")
        finally:
            guard.json.dump = real_dump
        with open(path, "rb") as fh:
            self.assertEqual(fh.read(), before, "a failed re-point damaged the live guard")
        self.assertEqual(sorted(os.listdir(os.path.join(self.root, "build"))),
                         ["claude-campaign-guard.json", "claude-campaign-guard.lock"])
        guard.os.replace = spy
        try:
            self.acquire(cron_id="job-2")
        finally:
            guard.os.replace = real_replace
        (src, dst), = replaced
        self.assertEqual((os.path.dirname(src), dst), (os.path.dirname(path), path),
                         "the guard is not published by a rename from beside it")

    def test_the_lock_is_exclusive_and_a_dead_holder_releases_it(self):
        with guard._Lock(self.root):
            with self.assertRaises(guard.GuardError):
                guard._Lock(self.root, wait=0.2).__enter__()
        holder = subprocess.Popen([sys.executable, "-c", (
            "import importlib.util, sys, time\n"
            f"s = importlib.util.spec_from_file_location('g', {str(GUARD_PY)!r})\n"
            "g = importlib.util.module_from_spec(s); s.loader.exec_module(g)\n"
            f"l = g._Lock({self.root!r}); l.__enter__(); print('held', flush=True); time.sleep(60)\n")],
            stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(holder.stdout.readline().strip(), "held")
            with self.assertRaises(guard.GuardError):
                guard._Lock(self.root, wait=0.2).__enter__()
        finally:
            holder.kill()
            holder.wait(timeout=30)
            holder.stdout.close()
        self.assertIn("guard created", self.acquire(), "a dead holder's lock was not released")

    def test_acquire_refuses_a_run_file_outside_the_workspace(self):
        for bad in ("../outside.md", os.path.abspath("x.md")):
            with self.subTest(bad=bad), self.assertRaises(guard.GuardError):
                guard.acquire(self.root, SESSION, 0, bad, "job-1")

    def test_every_end_checks_its_marker_and_leaves_the_job_to_cancel(self):
        self.acquire()
        with self.assertRaises(guard.GuardError):
            guard.end(self.root, SESSION, "closeout")
        with self.assertRaises(guard.GuardError):
            guard.end(self.root, OTHER, "operator-stop")
        with self.assertRaises(guard.GuardError):
            guard.end(self.root, SESSION, "plan-done")
        with self.assertRaises(guard.GuardError):
            guard.end(self.root, SESSION, "stall")
        self.write(RUN_FILE, f"## Closeout run={self.run_id()}\n", "a")
        self.assertIn("CronDelete job-1", guard.end(self.root, SESSION, "closeout"))
        self.assertIsNone(guard.read_guard(self.root))
        self.assertIn("CronDelete job-1", guard.pending_cancel(self.root))
        with self.assertRaises(guard.GuardError):
            guard.cancel_confirmed(self.root, "job-9")
        self.assertIn("nothing pending", guard.cancel_confirmed(self.root, "job-1"))
        self.acquire(cron_id="job-4")
        self.ready(0)
        self.write("scripts/open.txt", "1")  # nothing ready, but a blocked row is still open: a park, not done
        with self.assertRaises(guard.GuardError) as ctx:
            guard.end(self.root, SESSION, "plan-done")
        self.assertIn("still open", str(ctx.exception))
        self.write("scripts/open.txt", "0")
        self.assertIn("plan-done", guard.end(self.root, SESSION, "plan-done"))

    def test_a_re_point_without_a_phase_keeps_the_phase(self):
        guard.acquire(self.root, SESSION, 4, RUN_FILE, "job-1")
        guard.acquire(self.root, SESSION, None, RUN_FILE, "job-2")  # a new heartbeat job, no --phase
        self.assertEqual(guard.read_guard(self.root)["phase"], 4)
        with self.assertRaises(guard.GuardError):  # another session's guard is never taken without its phase
            guard.acquire(self.root, OTHER, None, RUN_FILE, "job-3", handover="test")
        self.assertEqual(guard.read_guard(self.root)["phase"], 4)
        self.assertEqual(guard.main(["acquire", "--session", SESSION, "--run-file", RUN_FILE, "--cron-id", "job-4",
                                     "--root", self.root]), 0)
        self.assertEqual(guard.read_guard(self.root)["phase"], 4)

    def test_a_fresh_guard_needs_a_phase(self):
        with self.assertRaises(guard.GuardError):
            guard.acquire(self.root, SESSION, None, RUN_FILE, "job-1")
        self.assertIsNone(guard.read_guard(self.root))

    def test_an_interrupted_end_leaves_no_run_to_resume(self):
        self.acquire()
        self.write(RUN_FILE, f"## Closeout run={self.run_id()}\n", "a")
        real = guard._write_json

        def die_on_pending(path, doc):
            if path.endswith("pending-cancel.json"):
                raise KeyboardInterrupt
            return real(path, doc)

        with mock.patch.object(guard, "_write_json", side_effect=die_on_pending):
            with self.assertRaises(KeyboardInterrupt):
                guard.end(self.root, SESSION, "closeout")
        self.assertIsNone(guard.read_guard(self.root))  # the heartbeat finds no guard and deletes itself
        self.assertEqual(guard.whoami(self.root, SESSION), "NO GUARD")

    def test_the_fingerprint_never_reads_a_link_or_a_special_file(self):
        self.write("notes.txt", "x\n")
        self.write("fifo-standin", "")
        real_lstat = os.lstat

        def as_fifo(path, *a, **k):
            info = real_lstat(path, *a, **k)
            if os.path.basename(path) == "fifo-standin":
                fields = list(info)
                fields[0] = stat.S_IFIFO | 0o644
                return os.stat_result(fields)
            return info

        read = []
        real_read = guard._read_regular
        with mock.patch.object(guard.os, "lstat", side_effect=as_fifo), \
                mock.patch.object(guard, "_read_regular", side_effect=lambda p, n, seen=None: read.append(p) or real_read(p, n, seen)):
            first = guard.fingerprint(self.root, RUN_FILE, "")
        self.assertEqual([os.path.basename(p) for p in read], ["notes.txt"])  # the FIFO is named, never opened
        with mock.patch.object(guard.os, "lstat", side_effect=as_fifo):
            self.assertEqual(guard.fingerprint(self.root, RUN_FILE, ""), first)
        # A regular file swapped for something else after the lstat is not read either: a directory, or another file
        # (what following a link swapped in would open) whose identity differs from what the lstat saw.
        self.assertIsNone(guard._read_regular(os.path.join(self.root, "build"), 10))
        self.write("other.txt", "secret\n")
        seen = os.lstat(os.path.join(self.root, "notes.txt"))
        self.assertIsNone(guard._read_regular(os.path.join(self.root, "other.txt"), 100, seen))
        self.assertEqual(guard._read_regular(os.path.join(self.root, "notes.txt"), 100, seen), b"x\n")

    def test_a_real_link_is_opened_as_itself_never_followed(self):
        target = os.path.join(self.root, "target.txt")
        self.write("target.txt", "secret\n")
        link = os.path.join(self.root, "link.txt")
        try:
            os.symlink(target, link)
        except OSError:
            self.skipTest("this account cannot create symbolic links")
        self.assertIsNone(guard._read_regular(link, 100, os.lstat(link)))
        self.assertEqual(guard._read_regular(target, 100, os.lstat(target)), b"secret\n")
        # A dangling link proves the open never follows: following would fail on the missing target.
        dangling = os.path.join(self.root, "dangling.txt")
        os.symlink(os.path.join(self.root, "nowhere.txt"), dangling)
        if os.name == "nt":
            fd = guard._open_no_follow(dangling)  # the link itself opens
            try:
                self.assertTrue(os.fstat(fd).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
            finally:
                os.close(fd)
        else:
            with self.assertRaises(OSError):  # O_NOFOLLOW refuses the link instead of following it
                guard._open_no_follow(dangling)

    def test_a_stalled_path_is_outwaited_and_later_paths_count_by_name(self):
        for name in ("a-stalls.txt", "b.txt", "c.txt"):
            self.write(name, "x\n")
        release = threading.Event()
        seen = []
        real = guard._untracked_line

        def line(full, path, *rest):
            seen.append(path)
            if path == "a-stalls.txt":
                release.wait(30)  # a call that never returns in time, like a read through a stalled share
            return real(full, path, *rest)

        started = time.monotonic()
        try:
            with mock.patch.object(guard, "_untracked_line", side_effect=line), \
                    mock.patch.object(guard, "FILE_SECONDS", 0.3), self.assertRaises(guard.GuardError):
                guard.fingerprint(self.root, RUN_FILE, "")
        finally:
            release.set()
        self.assertLess(time.monotonic() - started, 5)
        self.assertNotIn("b.txt", seen)  # after the stall no further path is touched
        self.assertNotIn("c.txt", seen)
        # An incomplete observation is an error: the hook fails open and records it, and the breaker's counters stay
        # where they were (neither progress nor a stall).
        self.acquire()
        before = guard._read_state(self.root)
        release.clear()
        try:
            with mock.patch.object(guard, "_untracked_line", side_effect=line), \
                    mock.patch.object(guard, "FILE_SECONDS", 0.3):
                self.assertIsNone(self.hook())  # fails open
        finally:
            release.set()
        after = guard._read_state(self.root)
        self.assertIn("a path stalled", after.get("hook_error", ""))  # recorded for the heartbeat
        self.assertEqual({k: after.get(k) for k in ("blocks", "trips", "fingerprint")},
                         {k: before.get(k) for k in ("blocks", "trips", "fingerprint")})

    def test_whoami_names_what_a_heartbeat_is_to_the_run(self):
        self.assertEqual(guard.whoami(self.root, SESSION), "NO GUARD")
        self.acquire(generation="gen000000001")
        self.assertEqual(guard.whoami(self.root, SESSION, "gen000000001"), f"OWNER run={self.run_id()} scope=plan")
        self.assertEqual(guard.whoami(self.root, SESSION, "gen000000000"), "NOT THE CURRENT JOB")
        self.assertEqual(guard.whoami(self.root, OTHER), "NOT THE OWNER")
        self.write("build/claude-campaign-guard.json", "{not json")
        self.assertEqual(guard.whoami(self.root, SESSION), "MALFORMED GUARD")

    def test_reconcile_health_and_expiry(self):
        self.assertEqual(guard.reconcile(self.root, SESSION, ["job-7"]),
                         ["reconcile: orphan job job-7 has no guard: CronDelete it"])
        self.acquire()
        self.assertEqual(guard.reconcile(self.root, SESSION, ["job-1"]), ["reconcile: consistent (guard and job job-1)"])
        self.assertIn("start nothing", guard.reconcile(self.root, OTHER, ["job-1"])[0])
        self.assertEqual(guard.health(self.root, SESSION, ["job-1"])[0], 0)
        self.assertEqual(guard.health(self.root, SESSION, [])[0], 1)
        created = guard.read_guard(self.root)["job_created_at"]
        self.assertEqual(guard.expiry(self.root, SESSION, now=created)[0], 0)
        import datetime
        later = (datetime.datetime.strptime(created, guard.UTC_FORMAT) + datetime.timedelta(days=6, hours=13))
        code, line = guard.expiry(self.root, SESSION, now=later.strftime(guard.UTC_FORMAT))
        self.assertEqual(code, 1)
        self.assertIn("replace due", line)

    def test_reset_state_rechecks_ownership_under_the_lock(self):
        self.acquire()
        self.hook()
        with self.assertRaises(guard.GuardError):
            guard.reset_state(self.root, OTHER)
        with self.assertRaises(guard.GuardError):
            guard.reset_state(self.root, expect_no_guard=True)
        self.assertEqual(guard.reset_state(self.root, SESSION), "reset-state: state deleted")

    def test_the_command_line_runs_against_a_fixture_root(self):
        def cli(*args):
            return subprocess.run([sys.executable, "-B", str(GUARD_PY), *args, "--root", self.root],
                                  capture_output=True, text=True, timeout=120)

        self.assertEqual(len(subprocess.run([sys.executable, "-B", str(GUARD_PY), "mint-generation"],
                                            capture_output=True, text=True).stdout.strip()), 12)
        result = cli("acquire", "--session", SESSION, "--phase", "0", "--run-file", RUN_FILE, "--cron-id", "job-1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(cli("whoami", "--session", SESSION).stdout.startswith("OWNER run="))
        self.assertEqual(cli("end", "--session", SESSION, "--reason", "nonsense").returncode, 1)
        self.assertEqual(cli("frobnicate").returncode, 2)


if __name__ == "__main__":
    unittest.main()
