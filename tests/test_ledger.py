import hashlib
import json
import os
from pathlib import Path
import shutil
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

    def archive_one(
        self,
        database,
        relative_path,
        content,
        title,
        kind,
        topics=(),
        links=(),
        run_id=None,
    ):
        source = self.workspace / relative_path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(content)
        scan = self.run_json(
            ARCHIVE,
            "scan",
            "--db",
            database,
            "--workspace-root",
            self.workspace,
            source,
        )
        if run_id is not None:
            scan["run_id"] = run_id
        manifest = self.enriched_manifest(
            scan,
            {
                Path(relative_path).as_posix(): {
                    "title": title,
                    "kind": kind,
                    "summary": (
                        f"Archives {title} as a deterministic integration-test "
                        "document with grounded metadata."
                    ),
                    "topics": list(topics),
                    "links": list(links),
                }
            },
        )
        result = self.run_json(
            ARCHIVE, "archive", "--db", database, "--manifest", manifest
        )
        return scan, result


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


class RevisionAndMetadataTests(CliCase):
    def rejected_metadata(self, document_id, links):
        metadata = self.workspace / "invalid-metadata.json"
        metadata.write_text(
            json.dumps(
                {
                    "document_id": document_id,
                    "title": "Changed title",
                    "kind": "decision-record",
                    "summary": "Must not replace existing metadata when manifest validation fails.",
                    "topics": ["architecture"],
                    "links": links,
                }
            ),
            encoding="utf-8",
        )
        before = self.db.read_bytes()
        error = self.run_json(
            ARCHIVE,
            "metadata",
            "--db",
            self.db,
            "--manifest",
            metadata,
            expected=2,
        )
        self.assertEqual(self.db.read_bytes(), before)
        return error

    def test_duplicate_retry_deletes_source_without_creating_empty_run(self):
        first_scan, first = self.archive_one(
            self.db,
            "docs/plan.md",
            b"# Plan\n\nStable content.\n",
            "Stable Plan",
            "plan",
            ["delivery"],
        )
        source = self.workspace / "docs/plan.md"
        source.write_bytes(b"# Plan\n\nStable content.\n")
        retry_scan = self.run_json(
            ARCHIVE,
            "scan",
            "--db",
            self.db,
            "--workspace-root",
            self.workspace,
            source,
        )
        manifest = self.enriched_manifest(
            retry_scan,
            {
                "docs/plan.md": {
                    "title": "Stable Plan",
                    "kind": "plan",
                    "summary": "Archives the same stable implementation plan during cleanup retry.",
                    "topics": ["delivery"],
                }
            },
        )

        retry = self.run_json(
            ARCHIVE, "archive", "--db", self.db, "--manifest", manifest
        )

        self.assertEqual(first["inserted_documents"], 1)
        self.assertEqual(retry["inserted_documents"], 0)
        self.assertEqual(retry["duplicate_documents"], 1)
        self.assertIsNone(retry["run_id"])
        self.assertFalse(source.exists())
        import sqlite3

        with sqlite3.connect(self.db) as connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM archive_runs").fetchone()[0],
                1,
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
                1,
            )
        connection.close()
        self.assertEqual(
            retry_scan["documents"][0]["prior_document_id"],
            first_scan["documents"][0]["id"],
        )

    def test_changed_same_path_automatically_supersedes_current_record(self):
        old_scan, unused = self.archive_one(
            self.db,
            "docs/spec.md",
            b"# Spec\n\nVersion one.\n",
            "Spec v1",
            "spec",
            ["auth"],
        )
        new_scan, unused = self.archive_one(
            self.db,
            "docs/spec.md",
            b"# Spec\n\nVersion two.\n",
            "Spec v2",
            "spec",
            ["auth"],
        )

        import sqlite3

        with sqlite3.connect(self.db) as connection:
            edge = connection.execute(
                """
                SELECT from_document_id, relation, to_document_id
                FROM document_links WHERE relation = 'supersedes'
                """
            ).fetchone()
        connection.close()
        self.assertEqual(
            edge,
            (
                new_scan["documents"][0]["id"],
                "supersedes",
                old_scan["documents"][0]["id"],
            ),
        )

    def test_new_link_targeting_duplicate_proposed_id_is_remapped(self):
        old_scan, unused = self.archive_one(
            self.db,
            "docs/stable.md",
            b"# Stable\n\nUnchanged.\n",
            "Stable",
            "spec",
        )
        docs = self.workspace / "docs"
        (docs / "stable.md").write_bytes(b"# Stable\n\nUnchanged.\n")
        (docs / "new.md").write_bytes(b"# New\n\nReferences stable.\n")
        scan = self.scan(docs)
        ids = {item["source_path"]: item["id"] for item in scan["documents"]}
        manifest = self.enriched_manifest(
            scan,
            {
                "docs/stable.md": {
                    "title": "Changed metadata is ignored",
                    "kind": "notes",
                    "summary": "This duplicate must retain the metadata already stored in the ledger.",
                },
                "docs/new.md": {
                    "title": "New",
                    "kind": "plan",
                    "summary": "Links to a duplicate document by the proposed identifier from this scan.",
                    "links": [
                        {
                            "relation": "references",
                            "to_document_id": ids["docs/stable.md"],
                        }
                    ],
                },
            },
        )

        result = self.run_json(
            ARCHIVE, "archive", "--db", self.db, "--manifest", manifest
        )

        import sqlite3

        self.assertEqual(result["inserted_documents"], 1)
        self.assertEqual(result["duplicate_documents"], 1)
        with sqlite3.connect(self.db) as connection:
            self.assertEqual(
                connection.execute(
                    """
                    SELECT to_document_id FROM document_links
                    WHERE from_document_id = ? AND relation = 'references'
                    """,
                    (ids["docs/new.md"],),
                ).fetchone()[0],
                old_scan["documents"][0]["id"],
            )
        connection.close()

    def test_metadata_replaces_discovery_fields_but_triggers_protect_payload(self):
        scan, unused = self.archive_one(
            self.db,
            "docs/spec.md",
            b"# Spec\n\nImmutable source.\n",
            "Original title",
            "spec",
            ["auth"],
        )
        document_id = scan["documents"][0]["id"]
        metadata = self.workspace / "metadata.json"
        metadata.write_text(
            json.dumps(
                {
                    "document_id": document_id,
                    "title": "Corrected title",
                    "kind": "decision-record",
                    "summary": "Corrects discovery metadata while preserving the exact archived source payload.",
                    "topics": ["architecture"],
                    "links": [],
                }
            ),
            encoding="utf-8",
        )

        result = self.run_json(
            ARCHIVE, "metadata", "--db", self.db, "--manifest", metadata
        )
        self.assertEqual(result["document_id"], document_id)
        self.assertEqual(result["after"]["title"], "Corrected title")

        import sqlite3

        with sqlite3.connect(self.db) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT title, kind, summary FROM documents WHERE id = ?",
                    (document_id,),
                ).fetchone()[0:2],
                ("Corrected title", "decision-record"),
            )
            self.assertEqual(
                connection.execute(
                    "SELECT topic FROM document_topics WHERE document_id = ?",
                    (document_id,),
                ).fetchall(),
                [("architecture",)],
            )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "UPDATE documents SET content_zlib = X'00' WHERE id = ?",
                    (document_id,),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "DELETE FROM documents WHERE id = ?", (document_id,)
                )
        connection.close()

    def test_metadata_rejects_non_slug_topic_as_json_error(self):
        scan, unused = self.archive_one(
            self.db,
            "docs/spec.md",
            b"# Spec\n\nImmutable source.\n",
            "Original title",
            "spec",
        )
        metadata = self.workspace / "metadata.json"
        metadata.write_text(
            json.dumps(
                {
                    "document_id": scan["documents"][0]["id"],
                    "title": "Original title",
                    "kind": "spec",
                    "summary": "Preserves metadata when validation rejects a malformed topic.",
                    "topics": [{}],
                    "links": [],
                }
            ),
            encoding="utf-8",
        )

        error = self.run_json(
            ARCHIVE,
            "metadata",
            "--db",
            self.db,
            "--manifest",
            metadata,
            expected=2,
        )

        self.assertIn("topics", error["error"])

    def test_metadata_rejects_non_uuid4_document_id_without_writes(self):
        self.archive_one(
            self.db,
            "docs/spec.md",
            b"# Spec\n\nImmutable source.\n",
            "Original title",
            "spec",
        )

        error = self.rejected_metadata(str(uuid.uuid1()), [])

        self.assertIn("document_id", error["error"])
        self.assertIn("UUIDv4", error["error"])

    def test_metadata_rejects_non_uuid4_link_target_without_writes(self):
        scan, unused = self.archive_one(
            self.db,
            "docs/spec.md",
            b"# Spec\n\nImmutable source.\n",
            "Original title",
            "spec",
        )

        error = self.rejected_metadata(
            scan["documents"][0]["id"],
            [{"relation": "references", "to_document_id": str(uuid.uuid1())}],
        )

        self.assertIn("metadata link target", error["error"])
        self.assertIn("UUIDv4", error["error"])

    def test_metadata_rejects_unhashable_link_target_without_writes(self):
        scan, unused = self.archive_one(
            self.db,
            "docs/spec.md",
            b"# Spec\n\nImmutable source.\n",
            "Original title",
            "spec",
        )

        error = self.rejected_metadata(
            scan["documents"][0]["id"],
            [{"relation": "references", "to_document_id": []}],
        )

        self.assertIn("metadata link target must be a UUID", error["error"])


class ReplayTests(CliCase):
    def make_three_snapshots(self):
        live = self.workspace / "live.db"
        seed_scan, unused = self.archive_one(
            live,
            "seed.md",
            b"# Seed\n\nCommon ancestor.\n",
            "Seed",
            "notes",
            ["shared"],
        )
        base = self.workspace / "base.db"
        destination = self.workspace / "destination.db"
        source = self.workspace / "source.db"
        shutil.copy2(live, base)
        shutil.copy2(live, destination)
        shutil.copy2(live, source)
        return seed_scan["documents"][0]["id"], base, destination, source

    def test_replay_preserves_destination_and_imports_source_run(self):
        unused, base, destination, source = self.make_three_snapshots()
        self.archive_one(
            destination,
            "destination.md",
            b"# Destination\n\nIntegrated work.\n",
            "Destination",
            "plan",
            ["delivery"],
        )
        self.archive_one(
            source,
            "source.md",
            b"# Source\n\nFeature work.\n",
            "Source",
            "spec",
            ["feature"],
        )
        before_destination = hashlib.sha256(destination.read_bytes()).hexdigest()
        before_source = hashlib.sha256(source.read_bytes()).hexdigest()
        output = self.workspace / "merged.db"
        output.write_bytes(b"stale output")

        result = self.run_json(
            ARCHIVE,
            "replay",
            "--base",
            base,
            "--destination",
            destination,
            "--source",
            source,
            "--output",
            output,
        )

        self.assertEqual(result["imported_runs"], 1)
        self.assertEqual(result["imported_documents"], 1)
        self.assertEqual(
            hashlib.sha256(destination.read_bytes()).hexdigest(),
            before_destination,
        )
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(), before_source
        )
        import sqlite3

        with sqlite3.connect(output) as connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM archive_runs").fetchone()[0],
                3,
            )
            self.assertEqual(
                {
                    row[0]
                    for row in connection.execute(
                        "SELECT source_path FROM documents"
                    )
                },
                {"seed.md", "destination.md", "source.md"},
            )
        connection.close()

    def test_replay_is_idempotent_for_identical_run(self):
        unused, base, destination, source = self.make_three_snapshots()
        self.archive_one(
            source,
            "source.md",
            b"# Source\n\nFeature work.\n",
            "Source",
            "spec",
        )
        first = self.workspace / "first.db"
        second = self.workspace / "second.db"
        self.run_json(
            ARCHIVE,
            "replay",
            "--base",
            base,
            "--destination",
            destination,
            "--source",
            source,
            "--output",
            first,
        )

        result = self.run_json(
            ARCHIVE,
            "replay",
            "--base",
            base,
            "--destination",
            first,
            "--source",
            source,
            "--output",
            second,
        )

        self.assertEqual(result["imported_runs"], 0)
        self.assertEqual(result["identical_runs"], 1)

    @unittest.skipIf(os.name == "nt", "symlink creation differs on Windows")
    def test_replay_rejects_output_symlink_alias_of_input(self):
        unused, base, destination, source = self.make_three_snapshots()
        self.archive_one(
            source,
            "source.md",
            b"# Source\n\nFeature work.\n",
            "Source",
            "spec",
        )
        before = {
            path: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (base, destination, source)
        }
        alias = self.workspace / "alias"
        alias.symlink_to(self.workspace, target_is_directory=True)
        output = alias / base.name
        self.assertEqual(output.resolve(), base.resolve())

        error = self.run_json(
            ARCHIVE,
            "replay",
            "--base",
            base,
            "--destination",
            destination,
            "--source",
            source,
            "--output",
            output,
            expected=2,
        )

        self.assertIn("distinct", error["error"].lower())
        self.assertEqual(
            {
                path: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (base, destination, source)
            },
            before,
        )

    def test_replay_rejects_source_metadata_edit_and_divergent_run_id(self):
        seed_id, base, destination, source = self.make_three_snapshots()
        metadata = self.workspace / "metadata.json"
        metadata.write_text(
            json.dumps(
                {
                    "document_id": seed_id,
                    "title": "Edited on source",
                    "kind": "notes",
                    "summary": "This source-side metadata edit is intentionally ineligible for automatic replay.",
                    "topics": ["shared"],
                    "links": [],
                }
            ),
            encoding="utf-8",
        )
        self.run_json(
            ARCHIVE, "metadata", "--db", source, "--manifest", metadata
        )
        output = self.workspace / "rejected.db"
        error = self.run_json(
            ARCHIVE,
            "replay",
            "--base",
            base,
            "--destination",
            destination,
            "--source",
            source,
            "--output",
            output,
            expected=2,
        )
        self.assertIn(seed_id, error["error"])
        self.assertFalse(output.exists())

        shutil.copy2(base, source)
        destination_scan, unused = self.archive_one(
            destination,
            "destination-only.md",
            b"# Destination\n\nOne run body.\n",
            "Destination only",
            "plan",
        )
        self.archive_one(
            source,
            "source-only.md",
            b"# Source\n\nDifferent run body.\n",
            "Source only",
            "plan",
            run_id=destination_scan["run_id"],
        )
        error = self.run_json(
            ARCHIVE,
            "replay",
            "--base",
            base,
            "--destination",
            destination,
            "--source",
            source,
            "--output",
            output,
            expected=2,
        )
        self.assertIn("divergent", error["error"].lower())
        self.assertFalse(output.exists())

    def test_replay_rejects_schema_mismatch(self):
        unused, base, destination, source = self.make_three_snapshots()
        import sqlite3

        with sqlite3.connect(source) as connection:
            connection.execute("PRAGMA user_version = 2")
        connection.close()
        output = self.workspace / "rejected.db"

        error = self.run_json(
            ARCHIVE,
            "replay",
            "--base",
            base,
            "--destination",
            destination,
            "--source",
            source,
            "--output",
            output,
            expected=2,
        )

        self.assertIn("version 2", error["error"].lower())
        self.assertFalse(output.exists())


class ReaderTests(CliCase):
    def create_revision_ledger(self):
        old_scan, unused = self.archive_one(
            self.db,
            "docs/auth.md",
            b"# Auth v1\n\nUse cookies.\n",
            "Auth v1",
            "spec",
            ["auth", "sessions"],
        )
        new_scan, unused = self.archive_one(
            self.db,
            "docs/auth.md",
            b"# Auth v2\n\nUse opaque sessions.\n",
            "Auth v2",
            "spec",
            ["auth", "sessions"],
            [
                {
                    "relation": "references",
                    "to_document_id": old_scan["documents"][0]["id"],
                }
            ],
        )
        plan_scan, unused = self.archive_one(
            self.db,
            "docs/auth-plan.md",
            b"# Auth Plan\n\nImplement opaque sessions.\n",
            "Auth implementation",
            "plan",
            ["auth", "delivery"],
            [
                {
                    "relation": "implements",
                    "to_document_id": new_scan["documents"][0]["id"],
                }
            ],
        )
        return old_scan, new_scan, plan_scan

    def test_topics_and_search_use_metadata_without_returning_content(self):
        old_scan, new_scan, plan_scan = self.create_revision_ledger()

        topics = self.run_json(READER, "topics", "--db", self.db)
        self.assertEqual(
            topics["topics"],
            [
                {"topic": "auth", "document_count": 3},
                {"topic": "delivery", "document_count": 1},
                {"topic": "sessions", "document_count": 2},
            ],
        )
        result = self.run_json(
            READER,
            "search",
            "--db",
            self.db,
            "--topic",
            "auth",
            "--summary",
            "deterministic",
        )
        ids = {item["id"] for item in result["documents"]}
        self.assertNotIn(old_scan["documents"][0]["id"], ids)
        self.assertIn(new_scan["documents"][0]["id"], ids)
        self.assertIn(plan_scan["documents"][0]["id"], ids)
        self.assertTrue(all("content" not in item for item in result["documents"]))

        history = self.run_json(
            READER,
            "search",
            "--db",
            self.db,
            "--path",
            "docs/auth.md",
            "--include-superseded",
        )
        self.assertEqual(len(history["documents"]), 2)

    def test_show_returns_verified_exact_content_and_one_hop_links(self):
        old_scan, new_scan, plan_scan = self.create_revision_ledger()
        document_id = plan_scan["documents"][0]["id"]

        result = self.run_json(READER, "show", "--db", self.db, document_id)

        self.assertEqual(result["document"]["id"], document_id)
        self.assertEqual(
            result["content"], "# Auth Plan\n\nImplement opaque sessions.\n"
        )
        self.assertEqual(
            result["document"]["outgoing_links"][0]["relation"], "implements"
        )
        self.assertEqual(
            result["document"]["outgoing_links"][0]["document_id"],
            new_scan["documents"][0]["id"],
        )
        self.assertEqual(result["document"]["supersedes"], [])
        self.assertEqual(result["document"]["superseded_by"], [])

    def test_reader_rejects_corrupt_payload_and_unsupported_schema(self):
        scan, unused = self.archive_one(
            self.db,
            "doc.md",
            b"# Exact\n\nPayload.\n",
            "Exact",
            "notes",
        )
        document_id = scan["documents"][0]["id"]
        import sqlite3

        with sqlite3.connect(self.db) as connection:
            trigger_sql = connection.execute(
                """
                SELECT sql FROM sqlite_schema
                WHERE type = 'trigger'
                  AND name = 'documents_payload_immutable'
                """
            ).fetchone()[0]
            connection.execute("DROP TRIGGER documents_payload_immutable")
            connection.execute(
                "UPDATE documents SET content_zlib = X'00' WHERE id = ?",
                (document_id,),
            )
            connection.execute(trigger_sql)
        connection.close()
        error = self.run_json(
            READER, "show", "--db", self.db, document_id, expected=2
        )
        self.assertIn("compressed", error["error"].lower())

        with sqlite3.connect(self.db) as connection:
            connection.execute("PRAGMA user_version = 2")
        connection.close()
        error = self.run_json(
            READER, "topics", "--db", self.db, expected=2
        )
        self.assertIn("version 2", error["error"].lower())

    def test_show_rejects_non_blob_payload_as_json_error(self):
        scan, unused = self.archive_one(
            self.db,
            "doc.md",
            b"# Exact\n\nPayload.\n",
            "Exact",
            "notes",
        )
        import sqlite3

        with sqlite3.connect(self.db) as connection:
            trigger_sql = connection.execute(
                """
                SELECT sql FROM sqlite_schema
                WHERE type = 'trigger'
                  AND name = 'documents_payload_immutable'
                """
            ).fetchone()[0]
            connection.execute("DROP TRIGGER documents_payload_immutable")
            connection.execute(
                "UPDATE documents SET content_zlib = 7 WHERE id = ?",
                (scan["documents"][0]["id"],),
            )
            connection.execute(trigger_sql)
        connection.close()

        error = self.run_json(
            READER,
            "show",
            "--db",
            self.db,
            scan["documents"][0]["id"],
            expected=2,
        )

        self.assertIn("compressed", error["error"].lower())

    def test_reader_rejects_unexpandable_database_path_as_json_error(self):
        error = self.run_json(
            READER,
            "topics",
            "--db",
            "~__superstore_user_that_does_not_exist__/ledger.db",
            expected=2,
        )

        self.assertIn("home directory", error["error"].lower())

    def test_search_rejects_non_json_metadata_as_json_error(self):
        self.archive_one(
            self.db,
            "doc.md",
            b"# Exact\n\nPayload.\n",
            "Exact",
            "notes",
        )
        import sqlite3

        with sqlite3.connect(self.db) as connection:
            connection.execute("UPDATE documents SET title = X'80'")
        connection.close()

        error = self.run_json(READER, "search", "--db", self.db, expected=2)

        self.assertIn("serializable", error["error"].lower())
