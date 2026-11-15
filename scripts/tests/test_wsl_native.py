"""tools/wsl-native.py: which lockfile entries it adds to a Windows-installed node_modules, and that it refuses a
tarball whose bytes do not match the lockfile's integrity hash. Run: python -m unittest discover -s scripts/tests
"""
import base64
import hashlib
import importlib.util
import io
from pathlib import Path
import tarfile
import unittest
from unittest import mock

TOOL = Path(__file__).resolve().parents[2] / "tools" / "wsl-native.py"
spec = importlib.util.spec_from_file_location("wsl_native_under_test", TOOL)
assert spec is not None and spec.loader is not None
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def integrity(data):
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()


def tarball():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        body = b'{"name": "x"}'
        info = tarfile.TarInfo("package/package.json")
        info.size = len(body)
        tar.addfile(info, io.BytesIO(body))
    return buf.getvalue()


class Wanted(unittest.TestCase):
    def test_only_top_level_linux_x64_glibc_entries_with_a_pin(self):
        pin = {"resolved": "https://registry.npmjs.org/x.tgz", "integrity": "sha512-AA=="}
        lock = {"packages": {
            "": {},
            "node_modules/lightningcss-linux-x64-gnu": {"os": ["linux"], "cpu": ["x64"], **pin},
            "node_modules/lightningcss-linux-x64-musl": {"os": ["linux"], "cpu": ["x64"], **pin},
            "node_modules/a-linux-x64": {"os": ["linux"], "cpu": ["x64"], "libc": ["musl"], **pin},
            "node_modules/lightningcss-linux-arm64-gnu": {"os": ["linux"], "cpu": ["arm64"], **pin},
            "node_modules/lightningcss-win32-x64-msvc": {"os": ["win32"], "cpu": ["x64"], **pin},
            "node_modules/x/node_modules/y-linux-x64-gnu": {"os": ["linux"], "cpu": ["x64"], **pin},
            "node_modules/unpinned-linux-x64-gnu": {"os": ["linux"], "cpu": ["x64"]},
        }}
        self.assertEqual([k for k, _ in native.wanted(lock)], ["node_modules/lightningcss-linux-x64-gnu"])

    def test_this_projects_lockfile_pins_the_three_binaries_the_build_needs(self):
        import json
        lock = json.loads((TOOL.parents[1] / "package-lock.json").read_text(encoding="utf-8"))
        names = {k.split("node_modules/", 1)[1] for k, _ in native.wanted(lock)}
        self.assertEqual(names, {"lightningcss-linux-x64-gnu", "@tailwindcss/oxide-linux-x64-gnu",
                                 "@unrs/resolver-binding-linux-x64-gnu"})


class Fetch(unittest.TestCase):
    def fetch_with(self, served, pinned):
        resp = mock.MagicMock()
        resp.__enter__.return_value.read.return_value = served
        with mock.patch.object(native.urllib.request, "urlopen", return_value=resp):
            return native.fetch({"resolved": "https://registry.npmjs.org/x.tgz", "integrity": integrity(pinned)})

    def test_matching_bytes_are_returned(self):
        data = tarball()
        self.assertEqual(self.fetch_with(data, data), data)

    def test_bytes_that_do_not_match_the_lockfile_are_refused(self):
        with self.assertRaises(SystemExit) as caught:
            self.fetch_with(tarball(), b"something else")
        self.assertIn("does not match the lockfile integrity", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
