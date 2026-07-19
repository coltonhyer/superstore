import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "skills/archiving-documentation/scripts/archive.py"
READER = ROOT / "skills/read-archive/scripts/read.py"


class CliCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.db = self.workspace / ".agents/ledger.db"

    def tearDown(self):
        self.temp.cleanup()

    def run_json(self, script, *arguments, expected=0):
        completed = subprocess.run(
            [sys.executable, str(script), *map(str, arguments)],
            cwd=self.workspace,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            expected,
            msg=f"stdout={completed.stdout}\nstderr={completed.stderr}",
        )
        stream = completed.stdout if expected in (0, 3) else completed.stderr
        return json.loads(stream)


class ScanTests(CliCase):
    def test_scan_recurses_markdown_and_ignores_other_regular_files(self):
        docs = self.workspace / "chosen"
        nested = docs / "nested"
        nested.mkdir(parents=True)
        first = docs / "spec.md"
        second = nested / "plan.md"
        first.write_text("# Spec\n\nExact text.\n", encoding="utf-8")
        second.write_text("# Plan\n\nMore text.\n", encoding="utf-8")
        (docs / "notes.txt").write_text("not markdown", encoding="utf-8")

        result = self.run_json(
            ARCHIVE,
            "scan",
            "--db",
            self.db,
            "--workspace-root",
            self.workspace,
            docs,
        )

        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["source_type"], "directory")
        self.assertEqual(result["existing_topics"], [])
        self.assertEqual(
            [item["source_path"] for item in result["documents"]],
            ["chosen/nested/plan.md", "chosen/spec.md"],
        )
        for item in result["documents"]:
            self.assertEqual(uuid.UUID(item["id"]).version, 4)
            raw = Path(item["absolute_path"]).read_bytes()
            self.assertEqual(item["source_bytes"], len(raw))
            self.assertEqual(item["content_sha256"], hashlib.sha256(raw).hexdigest())

    @unittest.skipIf(os.name == "nt", "symlink creation differs on Windows")
    def test_scan_rejects_any_symlink_in_requested_scope(self):
        docs = self.workspace / "chosen"
        docs.mkdir()
        target = self.workspace / "target.md"
        target.write_text("# Outside\n", encoding="utf-8")
        (docs / "linked.md").symlink_to(target)

        error = self.run_json(
            ARCHIVE,
            "scan",
            "--db",
            self.db,
            "--workspace-root",
            self.workspace,
            docs,
            expected=2,
        )

        self.assertIn("symlink", error["error"].lower())

    def test_scan_rejects_empty_directory_invalid_utf8_and_non_markdown_file(self):
        empty = self.workspace / "empty"
        empty.mkdir()
        error = self.run_json(
            ARCHIVE,
            "scan",
            "--db",
            self.db,
            "--workspace-root",
            self.workspace,
            empty,
            expected=2,
        )
        self.assertIn("no markdown", error["error"].lower())

        invalid = self.workspace / "invalid.md"
        invalid.write_bytes(b"\xff")
        error = self.run_json(
            ARCHIVE,
            "scan",
            "--db",
            self.db,
            "--workspace-root",
            self.workspace,
            invalid,
            expected=2,
        )
        self.assertIn("utf-8", error["error"].lower())

        text = self.workspace / "notes.txt"
        text.write_text("plain", encoding="utf-8")
        error = self.run_json(
            ARCHIVE,
            "scan",
            "--db",
            self.db,
            "--workspace-root",
            self.workspace,
            text,
            expected=2,
        )
        self.assertIn(".md", error["error"])
