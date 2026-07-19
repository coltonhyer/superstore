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

    def enriched_manifest(self, scan, metadata):
        for document in scan["documents"]:
            values = metadata[document["source_path"]]
            document.update(
                {
                    "title": values["title"],
                    "kind": values["kind"],
                    "summary": values["summary"],
                    "topics": values.get("topics", []),
                    "links": values.get("links", []),
                }
            )
        path = self.workspace / "archive-manifest.json"
        path.write_text(json.dumps(scan), encoding="utf-8")
        return path


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


class ArchiveTests(CliCase):
    def scan(self, path):
        return self.run_json(
            ARCHIVE,
            "scan",
            "--db",
            self.db,
            "--workspace-root",
            self.workspace,
            path,
        )

    def archive_module(self):
        import importlib.util

        specification = importlib.util.spec_from_file_location(
            "archive_cleanup_test", ARCHIVE
        )
        archive = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(archive)
        return archive

    def test_archive_round_trips_exact_bytes_topics_links_and_removes_empty_root(self):
        docs = self.workspace / "chosen"
        docs.mkdir()
        spec = docs / "spec.md"
        plan = docs / "plan.md"
        spec_bytes = b"# Auth Spec\n\nUse opaque sessions.\r\n"
        plan_bytes = b"# Auth Plan\n\nImplement the spec.\n"
        spec.write_bytes(spec_bytes)
        plan.write_bytes(plan_bytes)
        scan = self.scan(docs)
        ids = {item["source_path"]: item["id"] for item in scan["documents"]}
        manifest = self.enriched_manifest(
            scan,
            {
                "chosen/spec.md": {
                    "title": "Auth Spec",
                    "kind": "spec",
                    "summary": "Defines opaque session authentication and the constraints that later implementation work must preserve.",
                    "topics": ["auth", "session-management"],
                },
                "chosen/plan.md": {
                    "title": "Auth Plan",
                    "kind": "plan",
                    "summary": "Plans the implementation work required to deliver the approved opaque-session authentication design.",
                    "topics": ["auth"],
                    "links": [
                        {
                            "relation": "implements",
                            "to_document_id": ids["chosen/spec.md"],
                        }
                    ],
                },
            },
        )

        result = self.run_json(
            ARCHIVE, "archive", "--db", self.db, "--manifest", manifest
        )

        self.assertEqual(result["inserted_documents"], 2)
        self.assertEqual(result["duplicate_documents"], 0)
        self.assertTrue(result["cleanup"]["complete"])
        self.assertFalse(docs.exists())
        import sqlite3
        import zlib

        with sqlite3.connect(self.db) as connection:
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], 1)
            rows = connection.execute(
                "SELECT source_path, content_zlib, content_sha256, source_bytes "
                "FROM documents ORDER BY source_path"
            ).fetchall()
            restored = {row[0]: zlib.decompress(row[1]) for row in rows}
            self.assertEqual(restored["chosen/spec.md"], spec_bytes)
            self.assertEqual(restored["chosen/plan.md"], plan_bytes)
            self.assertEqual(
                connection.execute(
                    "SELECT relation FROM document_links"
                ).fetchone()[0],
                "implements",
            )
            self.assertEqual(
                {
                    row[0]
                    for row in connection.execute(
                        "SELECT topic FROM document_topics"
                    )
                },
                {"auth", "session-management"},
            )
        connection.close()

    def test_changed_source_or_invalid_manifest_preserves_all_sources(self):
        docs = self.workspace / "chosen"
        docs.mkdir()
        source = docs / "plan.md"
        source.write_text("# Plan\n\nFirst version.\n", encoding="utf-8")
        scan = self.scan(docs)
        manifest = self.enriched_manifest(
            scan,
            {
                "chosen/plan.md": {
                    "title": "Plan",
                    "kind": "plan",
                    "summary": "Captures the first version of the implementation plan.",
                    "topics": ["delivery"],
                }
            },
        )
        source.write_text("# Plan\n\nChanged after scan.\n", encoding="utf-8")

        error = self.run_json(
            ARCHIVE,
            "archive",
            "--db",
            self.db,
            "--manifest",
            manifest,
            expected=2,
        )

        self.assertIn("changed since scan", error["error"].lower())
        self.assertTrue(source.exists())
        self.assertFalse(self.db.exists())

    @unittest.skipIf(os.name == "nt", "dir_fd cleanup is POSIX-only")
    def test_cleanup_parent_swap_retains_outside_file_and_reports_error(self):
        from unittest import mock

        docs = self.workspace / "chosen"
        docs.mkdir()
        source = docs / "plan.md"
        source.write_text("# Selected\n", encoding="utf-8")
        outside = self.workspace / "outside"
        outside.mkdir()
        outside_source = outside / source.name
        outside_source.write_text("# Outside\n", encoding="utf-8")
        manifest_path = self.enriched_manifest(
            self.scan(docs),
            {
                "chosen/plan.md": {
                    "title": "Selected",
                    "kind": "plan",
                    "summary": "Exercises a parent-directory swap between cleanup verification and deletion.",
                }
            },
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        archive = self.archive_module()
        original_sha256 = archive.hashlib.sha256
        moved = self.workspace / "moved"
        swapped = False

        def swap_parent_then_hash(raw):
            nonlocal swapped
            if not swapped:
                docs.rename(moved)
                docs.symlink_to(outside, target_is_directory=True)
                swapped = True
            return original_sha256(raw)

        with mock.patch.object(
            archive.hashlib, "sha256", side_effect=swap_parent_then_hash
        ):
            result = archive.cleanup_sources(manifest)

        self.assertTrue(outside_source.exists())
        self.assertTrue((moved / source.name).exists())
        self.assertFalse(result["complete"])
        self.assertTrue(result["errors"])

    def test_archive_rejects_unsupported_secure_cleanup_before_database_write(self):
        import contextlib
        import io
        from unittest import mock

        source = self.workspace / "plan.md"
        source.write_text("# Plan\n", encoding="utf-8")
        manifest = self.enriched_manifest(
            self.scan(source),
            {
                "plan.md": {
                    "title": "Plan",
                    "kind": "plan",
                    "summary": "Must remain untouched when secure cleanup APIs are unavailable.",
                }
            },
        )
        archive = self.archive_module()
        stdout = io.StringIO()
        stderr = io.StringIO()
        arguments = [
            str(ARCHIVE),
            "archive",
            "--db",
            str(self.db),
            "--manifest",
            str(manifest),
        ]

        with (
            mock.patch.object(archive.os, "supports_dir_fd", set()),
            mock.patch.object(archive.sys, "argv", arguments),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
            self.assertRaises(SystemExit) as raised,
        ):
            archive.main()

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("secure cleanup", json.loads(stderr.getvalue())["error"].lower())
        self.assertEqual(stdout.getvalue(), "")
        self.assertTrue(source.exists())
        self.assertFalse(self.db.exists())

    def test_cleanup_parent_open_failure_closes_accumulated_descriptors(self):
        from unittest import mock

        archive = self.archive_module()
        failure = OSError("nested parent open failed")
        with (
            mock.patch.object(archive.os, "open", side_effect=[10, 11, failure]),
            mock.patch.object(archive.os, "close") as close,
            self.assertRaisesRegex(OSError, "nested parent open failed"),
        ):
            archive.open_cleanup_parent(
                Path("/source/nested/plan.md"), Path("/source"), "directory"
            )

        self.assertEqual(close.call_args_list, [mock.call(11), mock.call(10)])
