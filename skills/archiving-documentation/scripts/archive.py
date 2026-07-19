#!/usr/bin/env python3
import argparse
import datetime
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import sys
import uuid
import zlib


SCHEMA_VERSION = 1
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SCHEMA_STATEMENTS = (
    """
    CREATE TABLE archive_runs (
        id TEXT PRIMARY KEY,
        archived_at TEXT NOT NULL,
        source_root TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE documents (
        id TEXT PRIMARY KEY,
        archive_run_id TEXT NOT NULL REFERENCES archive_runs(id),
        source_path TEXT NOT NULL,
        title TEXT NOT NULL,
        kind TEXT NOT NULL,
        summary TEXT NOT NULL,
        content_zlib BLOB NOT NULL,
        content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64),
        source_bytes INTEGER NOT NULL CHECK (source_bytes >= 0),
        UNIQUE (source_path, content_sha256)
    )
    """,
    "CREATE INDEX documents_by_run ON documents(archive_run_id)",
    """
    CREATE TABLE document_topics (
        document_id TEXT NOT NULL REFERENCES documents(id),
        topic TEXT NOT NULL CHECK (topic <> ''),
        PRIMARY KEY (document_id, topic)
    )
    """,
    """
    CREATE INDEX document_topics_by_topic
    ON document_topics(topic, document_id)
    """,
    """
    CREATE TABLE document_links (
        from_document_id TEXT NOT NULL REFERENCES documents(id),
        relation TEXT NOT NULL CHECK (relation <> ''),
        to_document_id TEXT NOT NULL REFERENCES documents(id),
        PRIMARY KEY (from_document_id, relation, to_document_id),
        CHECK (from_document_id <> to_document_id)
    )
    """,
    """
    CREATE INDEX document_links_by_target
    ON document_links(to_document_id, relation, from_document_id)
    """,
    """
    CREATE TRIGGER archive_runs_immutable_update
    BEFORE UPDATE ON archive_runs
    BEGIN
        SELECT RAISE(ABORT, 'archive runs are immutable');
    END
    """,
    """
    CREATE TRIGGER archive_runs_no_delete
    BEFORE DELETE ON archive_runs
    BEGIN
        SELECT RAISE(ABORT, 'archive runs cannot be deleted');
    END
    """,
    """
    CREATE TRIGGER documents_payload_immutable
    BEFORE UPDATE OF
        id, archive_run_id, source_path, content_zlib, content_sha256, source_bytes
    ON documents
    BEGIN
        SELECT RAISE(ABORT, 'archived document payload is immutable');
    END
    """,
    """
    CREATE TRIGGER documents_no_delete
    BEFORE DELETE ON documents
    BEGIN
        SELECT RAISE(ABORT, 'archived documents cannot be deleted');
    END
    """,
)
EXPECTED_COLUMNS = {
    "archive_runs": ("id", "archived_at", "source_root"),
    "documents": (
        "id",
        "archive_run_id",
        "source_path",
        "title",
        "kind",
        "summary",
        "content_zlib",
        "content_sha256",
        "source_bytes",
    ),
    "document_topics": ("document_id", "topic"),
    "document_links": ("from_document_id", "relation", "to_document_id"),
}
EXPECTED_OBJECTS = {
    ("index", "documents_by_run"),
    ("index", "document_topics_by_topic"),
    ("index", "document_links_by_target"),
    ("trigger", "archive_runs_immutable_update"),
    ("trigger", "archive_runs_no_delete"),
    ("trigger", "documents_payload_immutable"),
    ("trigger", "documents_no_delete"),
}


class LedgerError(Exception):
    pass


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        fail(message)


def json_success(payload, exit_code=0):
    print(json.dumps(payload, sort_keys=True))
    raise SystemExit(exit_code)


def fail(message):
    print(json.dumps({"error": str(message)}, sort_keys=True), file=sys.stderr)
    raise SystemExit(2)


def validate_uuid4(value, field):
    try:
        parsed = uuid.UUID(value)
    except (AttributeError, TypeError, ValueError) as exc:
        raise LedgerError(f"{field} must be a UUID") from exc
    if parsed.version != 4 or str(parsed) != value:
        raise LedgerError(f"{field} must be a canonical UUIDv4")
    return value


def read_markdown(path):
    if path.is_symlink():
        raise LedgerError(f"symlink is not allowed: {path}")
    if not path.is_file() or path.suffix.lower() != ".md":
        raise LedgerError(f"expected a regular .md file: {path}")
    raw = path.read_bytes()
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LedgerError(f"Markdown must be valid UTF-8: {path}") from exc
    return raw


def discover(target):
    if target.is_symlink():
        raise LedgerError(f"symlink is not allowed: {target}")
    if target.is_file():
        read_markdown(target)
        return "file", [target]
    if not target.is_dir():
        raise LedgerError(f"path does not exist or is not a directory: {target}")

    candidates = []
    for current, directory_names, file_names in os.walk(target, followlinks=False):
        current_path = Path(current)
        for name in directory_names:
            candidate = current_path / name
            if candidate.is_symlink():
                raise LedgerError(f"symlink is not allowed: {candidate}")
        for name in file_names:
            candidate = current_path / name
            if candidate.is_symlink():
                raise LedgerError(f"symlink is not allowed: {candidate}")
            if candidate.suffix.lower() == ".md":
                read_markdown(candidate)
                candidates.append(candidate)
    if not candidates:
        raise LedgerError(f"no Markdown files found beneath: {target}")
    return "directory", sorted(candidates, key=lambda item: item.as_posix())


def stored_source_path(path, workspace_root):
    try:
        return path.relative_to(workspace_root).as_posix()
    except ValueError:
        return path.as_posix()


def connect_writer(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = DELETE")
    return connection


def connect_readonly(path):
    if not path.is_file():
        raise LedgerError(f"ledger does not exist: {path}")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA query_only = ON")
        validate_schema(connection)
        return connection
    except Exception:
        connection.close()
        raise


def validate_schema(connection):
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version != SCHEMA_VERSION:
        raise LedgerError(
            f"unsupported ledger schema version {version}; expected {SCHEMA_VERSION}"
        )
    for table, expected in EXPECTED_COLUMNS.items():
        actual = tuple(
            row[1] for row in connection.execute(f"PRAGMA table_info({table})")
        )
        if actual != expected:
            raise LedgerError(f"ledger schema is missing or invalid table: {table}")
    actual_objects = {
        (row[0], row[1])
        for row in connection.execute(
            """
            SELECT type, name FROM sqlite_schema
            WHERE type IN ('index', 'trigger')
            """
        )
    }
    missing = EXPECTED_OBJECTS - actual_objects
    if missing:
        raise LedgerError(f"ledger schema objects are missing: {sorted(missing)}")


def ensure_schema(connection):
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_schema "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    if version == 0:
        if tables:
            raise LedgerError("refusing a non-empty unversioned SQLite database")
        connection.execute("BEGIN")
        try:
            for statement in SCHEMA_STATEMENTS:
                connection.execute(statement)
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    validate_schema(connection)


def scan_context(database, source_paths):
    if not database.exists():
        return [], {source_path: None for source_path in source_paths}
    connection = connect_readonly(database)
    try:
        topics = [
            row[0]
            for row in connection.execute(
                "SELECT DISTINCT topic FROM document_topics ORDER BY topic"
            )
        ]
        prior = {}
        for source_path in source_paths:
            row = connection.execute(
                """
                SELECT d.id
                FROM documents AS d
                JOIN archive_runs AS r ON r.id = d.archive_run_id
                WHERE d.source_path = ?
                  AND NOT EXISTS (
                      SELECT 1
                      FROM document_links AS newer
                      WHERE newer.relation = 'supersedes'
                        AND newer.to_document_id = d.id
                  )
                ORDER BY r.archived_at DESC, d.id DESC
                LIMIT 1
                """,
                (source_path,),
            ).fetchone()
            prior[source_path] = None if row is None else row[0]
        return topics, prior
    finally:
        connection.close()


def verify_database(connection):
    foreign_keys = list(connection.execute("PRAGMA foreign_key_check"))
    if foreign_keys:
        raise LedgerError(f"foreign key verification failed: {foreign_keys}")
    integrity = [row[0] for row in connection.execute("PRAGMA integrity_check")]
    if integrity != ["ok"]:
        raise LedgerError(f"integrity verification failed: {integrity}")


def manifest_absolute_path(value, field):
    if not isinstance(value, str) or not value or not Path(value).is_absolute():
        raise LedgerError(f"{field} must be an absolute path")
    path = Path(os.path.abspath(value))
    if path.as_posix() != value:
        raise LedgerError(f"{field} must be normalized")
    return path


def read_without_symlinks(path, source_root):
    try:
        relative = path.relative_to(source_root)
    except ValueError as exc:
        raise LedgerError(f"path is outside source root: {path}") from exc
    current = source_root
    for part in (None, *relative.parts):
        if part is not None:
            current /= part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise LedgerError(f"source changed since scan: {path}: {exc}") from exc
        if stat.S_ISLNK(mode):
            raise LedgerError(f"symlink is not allowed: {current}")

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise LedgerError(f"source changed since scan: {path}: {exc}") from exc
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise LedgerError(f"expected a regular .md file: {path}")
        with os.fdopen(descriptor, "rb") as source:
            descriptor = -1
            return source.read()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def load_archive_manifest(path):
    with path.open(encoding="utf-8") as source:
        manifest = json.load(source)
    if not isinstance(manifest, dict):
        raise LedgerError("archive manifest root must be an object")
    if (
        not isinstance(manifest.get("schema_version"), int)
        or isinstance(manifest["schema_version"], bool)
        or manifest["schema_version"] != SCHEMA_VERSION
    ):
        raise LedgerError(
            f"unsupported archive manifest schema version: "
            f"{manifest.get('schema_version')}"
        )
    validate_uuid4(manifest.get("run_id"), "run_id")
    source_root = manifest_absolute_path(manifest.get("source_root"), "source_root")
    workspace_root = manifest_absolute_path(
        manifest.get("workspace_root"), "workspace_root"
    )
    source_type = manifest.get("source_type")
    if source_type not in ("file", "directory"):
        raise LedgerError("source_type must be file or directory")
    documents = manifest.get("documents")
    if not isinstance(documents, list) or not documents:
        raise LedgerError("archive manifest documents must be a non-empty list")

    document_ids = set()
    for item in documents:
        if not isinstance(item, dict):
            raise LedgerError("archive manifest documents must be objects")
        document_id = validate_uuid4(item.get("id"), "document id")
        if document_id in document_ids:
            raise LedgerError(f"duplicate document id: {document_id}")
        document_ids.add(document_id)

    if source_type == "file" and len(documents) != 1:
        raise LedgerError("file source must contain exactly one document")

    prepared = []
    absolute_paths = set()
    source_hashes = set()
    for item in documents:
        candidate = manifest_absolute_path(
            item.get("absolute_path"), "document absolute_path"
        )
        if candidate in absolute_paths:
            raise LedgerError(f"duplicate absolute path: {candidate}")
        absolute_paths.add(candidate)

        try:
            relative = candidate.relative_to(source_root)
        except ValueError as exc:
            raise LedgerError(f"path is outside source root: {candidate}") from exc
        if source_type == "file":
            if candidate != source_root:
                raise LedgerError("file document path must equal source_root")
        elif not relative.parts:
            raise LedgerError("directory documents must be descendants of source_root")

        source_path = item.get("source_path")
        if not isinstance(source_path, str) or not source_path:
            raise LedgerError("document source_path must be non-empty text")
        if source_path != stored_source_path(candidate, workspace_root):
            raise LedgerError(f"source_path does not match absolute_path: {source_path}")
        content_sha256 = item.get("content_sha256")
        source_bytes = item.get("source_bytes")
        if (
            not isinstance(content_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", content_sha256)
            or not isinstance(source_bytes, int)
            or isinstance(source_bytes, bool)
            or source_bytes < 0
        ):
            raise LedgerError(f"invalid source fingerprint: {source_path}")
        source_hash = (source_path, content_sha256)
        if source_hash in source_hashes:
            raise LedgerError(
                f"duplicate source path and content hash: {source_path}"
            )
        source_hashes.add(source_hash)

        title = item.get("title")
        summary = item.get("summary")
        kind = item.get("kind")
        if not isinstance(title, str) or not title.strip():
            raise LedgerError(f"blank title: {source_path}")
        if not isinstance(summary, str) or not summary.strip():
            raise LedgerError(f"blank summary: {source_path}")
        if not isinstance(kind, str) or not SLUG.fullmatch(kind):
            raise LedgerError(f"invalid kind: {kind}")

        topics = item.get("topics")
        if not isinstance(topics, list):
            raise LedgerError(f"topics must be a list: {source_path}")
        if any(not isinstance(topic, str) or not SLUG.fullmatch(topic) for topic in topics):
            raise LedgerError(f"invalid topic: {source_path}")
        if len(topics) != len(set(topics)):
            raise LedgerError(f"duplicate topic: {source_path}")

        links = item.get("links")
        if not isinstance(links, list):
            raise LedgerError(f"links must be a list: {source_path}")
        link_keys = set()
        for link in links:
            if not isinstance(link, dict) or set(link) != {
                "relation",
                "to_document_id",
            }:
                raise LedgerError(f"malformed link: {source_path}")
            relation = link["relation"]
            target = link["to_document_id"]
            if not isinstance(relation, str) or not SLUG.fullmatch(relation):
                raise LedgerError(f"invalid link relation: {source_path}")
            if not isinstance(target, str) or not target.strip():
                raise LedgerError(f"invalid link target: {source_path}")
            if target == item["id"]:
                raise LedgerError(f"self-link is not allowed: {source_path}")
            link_key = (relation, target)
            if link_key in link_keys:
                raise LedgerError(f"duplicate link: {source_path}")
            link_keys.add(link_key)

        if candidate.suffix.lower() != ".md":
            raise LedgerError(f"expected a regular .md file: {candidate}")
        raw = read_without_symlinks(candidate, source_root)
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise LedgerError(f"Markdown must be valid UTF-8: {candidate}") from exc
        if (
            len(raw) != source_bytes
            or hashlib.sha256(raw).hexdigest() != content_sha256
        ):
            raise LedgerError(f"source changed since scan: {source_path}")
        prepared.append((item, raw))
    return manifest, prepared


def command_scan(arguments):
    workspace_root = Path(arguments.workspace_root).expanduser().absolute()
    if workspace_root.is_symlink() or not workspace_root.is_dir():
        raise LedgerError(f"workspace root must be a regular directory: {workspace_root}")
    target = Path(arguments.path).expanduser().absolute()
    source_type, candidates = discover(target)
    documents = []
    for candidate in candidates:
        raw = read_markdown(candidate)
        documents.append(
            {
                "id": str(uuid.uuid4()),
                "absolute_path": candidate.as_posix(),
                "source_path": stored_source_path(candidate, workspace_root),
                "content_sha256": hashlib.sha256(raw).hexdigest(),
                "source_bytes": len(raw),
                "prior_document_id": None,
            }
        )
    existing_topics, prior = scan_context(
        Path(arguments.db).expanduser().absolute(),
        [item["source_path"] for item in documents],
    )
    for item in documents:
        item["prior_document_id"] = prior[item["source_path"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": str(uuid.uuid4()),
        "source_root": target.as_posix(),
        "source_type": source_type,
        "workspace_root": workspace_root.as_posix(),
        "existing_topics": existing_topics,
        "documents": documents,
    }


def same_entry(first, second):
    return (first.st_dev, first.st_ino, stat.S_IFMT(first.st_mode)) == (
        second.st_dev,
        second.st_ino,
        stat.S_IFMT(second.st_mode),
    )


def require_secure_cleanup():
    required_dir_fd = {os.open, os.stat, os.unlink, os.rmdir}
    if (
        os.name != "posix"
        or not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
        or not required_dir_fd <= os.supports_dir_fd
        or os.scandir not in os.supports_fd
        or os.stat not in os.supports_follow_symlinks
    ):
        raise LedgerError("secure cleanup is unsupported on this platform")


def open_cleanup_parent(candidate, source_root, source_type):
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptors = []
    chain = []
    try:
        descriptors.append(
            os.open(source_root.parent, os.O_RDONLY | os.O_DIRECTORY)
        )
        if source_type == "directory":
            relative_parent = candidate.parent.relative_to(source_root)
            parts = (source_root.name, *relative_parent.parts)
            current_path = source_root.parent
            for part in parts:
                parent = descriptors[-1]
                child = os.open(part, directory_flags, dir_fd=parent)
                descriptors.append(child)
                current_path /= part
                chain.append((parent, part, child, current_path))
        return descriptors[-1], descriptors, chain
    except Exception:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise


def verify_cleanup_chain(chain, candidate):
    for parent, name, child, _ in chain:
        current = os.stat(name, dir_fd=parent, follow_symlinks=False)
        if not same_entry(current, os.fstat(child)):
            raise LedgerError(f"source changed since scan: {candidate}")


def cleanup_candidate(item, source_root, source_type):
    candidate = Path(item["absolute_path"])
    parent, descriptors, chain = open_cleanup_parent(
        candidate, source_root, source_type
    )
    file_descriptor = None
    try:
        file_descriptor = os.open(
            candidate.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent
        )
        file_status = os.fstat(file_descriptor)
        if not stat.S_ISREG(file_status.st_mode):
            raise LedgerError(f"expected a regular .md file: {candidate}")
        with os.fdopen(file_descriptor, "rb") as source:
            file_descriptor = None
            raw = source.read()
        if (
            len(raw) != item["source_bytes"]
            or hashlib.sha256(raw).hexdigest() != item["content_sha256"]
        ):
            raise LedgerError(f"source changed since scan: {candidate}")
        verify_cleanup_chain(chain, candidate)
        current = os.stat(
            candidate.name, dir_fd=parent, follow_symlinks=False
        )
        if not same_entry(current, file_status):
            raise LedgerError(f"source changed since scan: {candidate}")
        os.unlink(candidate.name, dir_fd=parent)
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def remove_empty_directories(source_root, removed_directories, errors):
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parent_descriptor = os.open(
        source_root.parent, os.O_RDONLY | os.O_DIRECTORY
    )
    try:
        root_descriptor = os.open(
            source_root.name, directory_flags, dir_fd=parent_descriptor
        )
        root_status = os.fstat(root_descriptor)

        def remove_descendants(descriptor, path):
            with os.scandir(descriptor) as entries:
                directories = [
                    entry.name
                    for entry in entries
                    if entry.is_dir(follow_symlinks=False)
                ]
            for name in directories:
                child_path = path / name
                try:
                    child = os.open(name, directory_flags, dir_fd=descriptor)
                except OSError as exc:
                    errors.append(
                        {"path": child_path.as_posix(), "error": str(exc)}
                    )
                    continue
                child_status = os.fstat(child)
                try:
                    remove_descendants(child, child_path)
                finally:
                    os.close(child)
                try:
                    current = os.stat(
                        name, dir_fd=descriptor, follow_symlinks=False
                    )
                    if not same_entry(current, child_status):
                        raise LedgerError(
                            f"source changed since scan: {child_path}"
                        )
                    os.rmdir(name, dir_fd=descriptor)
                    removed_directories.append(child_path.as_posix())
                except OSError as exc:
                    if exc.errno != errno.ENOTEMPTY:
                        errors.append(
                            {"path": child_path.as_posix(), "error": str(exc)}
                        )
                except LedgerError as exc:
                    errors.append(
                        {"path": child_path.as_posix(), "error": str(exc)}
                    )

        try:
            remove_descendants(root_descriptor, source_root)
        finally:
            os.close(root_descriptor)
        current_root = os.stat(
            source_root.name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        if not same_entry(current_root, root_status):
            raise LedgerError(f"source changed since scan: {source_root}")
        os.rmdir(source_root.name, dir_fd=parent_descriptor)
        removed_directories.append(source_root.as_posix())
    finally:
        os.close(parent_descriptor)


def cleanup_sources(manifest):
    deleted_files = []
    removed_directories = []
    errors = []
    source_root = Path(manifest["source_root"])

    for item in manifest["documents"]:
        candidate = Path(item["absolute_path"])
        try:
            cleanup_candidate(item, source_root, manifest["source_type"])
            deleted_files.append(candidate.as_posix())
        except (LedgerError, OSError) as exc:
            errors.append({"path": candidate.as_posix(), "error": str(exc)})

    if manifest["source_type"] == "directory":
        try:
            remove_empty_directories(source_root, removed_directories, errors)
        except (LedgerError, OSError) as exc:
            errors.append({"path": source_root.as_posix(), "error": str(exc)})

    return {
        "complete": not errors,
        "deleted_files": deleted_files,
        "removed_directories": removed_directories,
        "errors": errors,
    }


def partition_prepared(connection, prepared):
    duplicate_map = {}
    new_documents = []
    for item, raw in prepared:
        row = connection.execute(
            """
            SELECT id FROM documents
            WHERE source_path = ? AND content_sha256 = ?
            """,
            (item["source_path"], item["content_sha256"]),
        ).fetchone()
        if row is None:
            new_documents.append((item, raw))
        else:
            duplicate_map[item["id"]] = row[0]
    return new_documents, duplicate_map


def active_prior_id(connection, source_path):
    row = connection.execute(
        """
        SELECT d.id
        FROM documents AS d
        JOIN archive_runs AS r ON r.id = d.archive_run_id
        WHERE d.source_path = ?
          AND NOT EXISTS (
              SELECT 1 FROM document_links AS newer
              WHERE newer.relation = 'supersedes'
                AND newer.to_document_id = d.id
          )
        ORDER BY r.archived_at DESC, d.id DESC
        LIMIT 1
        """,
        (source_path,),
    ).fetchone()
    return None if row is None else row[0]


def command_archive(arguments):
    require_secure_cleanup()
    manifest, prepared = load_archive_manifest(Path(arguments.manifest))
    database = Path(arguments.db).expanduser().absolute()
    connection = connect_writer(database)
    try:
        ensure_schema(connection)
        connection.execute("BEGIN")
        new_documents, duplicate_map = partition_prepared(connection, prepared)
        compressed_bytes = 0
        source_bytes = 0
        if new_documents:
            archived_at = (
                datetime.datetime.now(datetime.timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z")
            )
            connection.execute(
                "INSERT INTO archive_runs(id, archived_at, source_root) VALUES (?, ?, ?)",
                (manifest["run_id"], archived_at, manifest["source_root"]),
            )
            id_map = {
                **duplicate_map,
                **{item["id"]: item["id"] for item, _ in new_documents},
            }
            prior_ids = {}
            for item, raw in new_documents:
                prior_ids[item["id"]] = active_prior_id(
                    connection, item["source_path"]
                )
                compressed = zlib.compress(raw)
                restored = zlib.decompress(compressed)
                if (
                    restored != raw
                    or len(restored) != item["source_bytes"]
                    or hashlib.sha256(restored).hexdigest()
                    != item["content_sha256"]
                ):
                    raise LedgerError(
                        f"compression verification failed: {item['source_path']}"
                    )
                connection.execute(
                    """
                    INSERT INTO documents(
                        id, archive_run_id, source_path, title, kind, summary,
                        content_zlib, content_sha256, source_bytes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["id"],
                        manifest["run_id"],
                        item["source_path"],
                        item["title"],
                        item["kind"],
                        item["summary"],
                        compressed,
                        item["content_sha256"],
                        item["source_bytes"],
                    ),
                )
                source_bytes += len(raw)
                compressed_bytes += len(compressed)

            known_targets = {
                row[0] for row in connection.execute("SELECT id FROM documents")
            }
            for item, _ in new_documents:
                connection.executemany(
                    "INSERT INTO document_topics(document_id, topic) VALUES (?, ?)",
                    [(item["id"], topic) for topic in item["topics"]],
                )
            for item, _ in new_documents:
                for link in item["links"]:
                    target = id_map.get(
                        link["to_document_id"], link["to_document_id"]
                    )
                    if target not in known_targets:
                        raise LedgerError(f"missing link target: {target}")
                    connection.execute(
                        """
                        INSERT INTO document_links(
                            from_document_id, relation, to_document_id
                        ) VALUES (?, ?, ?)
                        """,
                        (item["id"], link["relation"], target),
                    )
            for item, _ in new_documents:
                prior_id = prior_ids[item["id"]]
                if prior_id is not None and prior_id != item["id"]:
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO document_links(
                            from_document_id, relation, to_document_id
                        ) VALUES (?, 'supersedes', ?)
                        """,
                        (item["id"], prior_id),
                    )
        verify_database(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        connection.close()
        raise
    connection.close()

    cleanup = cleanup_sources(manifest)
    result = {
        "run_id": manifest["run_id"] if new_documents else None,
        "inserted_documents": len(new_documents),
        "duplicate_documents": len(duplicate_map),
        "source_bytes": source_bytes,
        "compressed_bytes": compressed_bytes,
        "database_authoritative": True,
        "cleanup": cleanup,
    }
    if not cleanup["complete"]:
        json_success(result, exit_code=3)
    return result


def load_metadata_manifest(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LedgerError(f"cannot read metadata manifest: {exc}") from exc
    required = {
        "document_id",
        "title",
        "kind",
        "summary",
        "topics",
        "links",
    }
    if not isinstance(data, dict) or set(data) != required:
        raise LedgerError(
            "metadata manifest must contain exactly document_id, title, kind, "
            "summary, topics, and links"
        )
    validate_uuid4(data["document_id"], "document_id")
    if not isinstance(data["title"], str) or not data["title"].strip():
        raise LedgerError("title must be non-empty text")
    if not isinstance(data["summary"], str) or not data["summary"].strip():
        raise LedgerError("summary must be non-empty text")
    if not isinstance(data["kind"], str) or not SLUG.fullmatch(data["kind"]):
        raise LedgerError("kind must be a normalized lowercase slug")
    if (
        not isinstance(data["topics"], list)
        or any(
            not isinstance(value, str) or not SLUG.fullmatch(value)
            for value in data["topics"]
        )
        or len(data["topics"]) != len(set(data["topics"]))
    ):
        raise LedgerError("topics must be unique normalized lowercase slugs")
    if not isinstance(data["links"], list):
        raise LedgerError("links must be a list")
    seen_links = set()
    for link in data["links"]:
        if not isinstance(link, dict) or set(link) != {
            "relation",
            "to_document_id",
        }:
            raise LedgerError("each link must contain relation and to_document_id")
        relation = link["relation"]
        if not isinstance(relation, str) or not SLUG.fullmatch(relation):
            raise LedgerError("metadata links are malformed, duplicate, or self-links")
        target = validate_uuid4(link["to_document_id"], "metadata link target")
        key = (relation, target)
        if target == data["document_id"] or key in seen_links:
            raise LedgerError("metadata links are malformed, duplicate, or self-links")
        seen_links.add(key)
    return data


def editable_state(connection, document_id):
    row = connection.execute(
        "SELECT title, kind, summary FROM documents WHERE id = ?",
        (document_id,),
    ).fetchone()
    if row is None:
        raise LedgerError(f"unknown document: {document_id}")
    return {
        "title": row[0],
        "kind": row[1],
        "summary": row[2],
        "topics": [
            value[0]
            for value in connection.execute(
                """
                SELECT topic FROM document_topics
                WHERE document_id = ? ORDER BY topic
                """,
                (document_id,),
            )
        ],
        "links": [
            {"relation": value[0], "to_document_id": value[1]}
            for value in connection.execute(
                """
                SELECT relation, to_document_id FROM document_links
                WHERE from_document_id = ?
                ORDER BY relation, to_document_id
                """,
                (document_id,),
            )
        ],
    }


def command_metadata(arguments):
    data = load_metadata_manifest(Path(arguments.manifest))
    connection = connect_writer(Path(arguments.db).expanduser().absolute())
    try:
        validate_schema(connection)
        before = editable_state(connection, data["document_id"])
        target_ids = {link["to_document_id"] for link in data["links"]}
        existing = (
            {
                row[0]
                for row in connection.execute(
                    "SELECT id FROM documents WHERE id IN "
                    f"({','.join('?' for value in target_ids)})",
                    tuple(sorted(target_ids)),
                )
            }
            if target_ids
            else set()
        )
        if existing != target_ids:
            raise LedgerError(
                f"missing metadata link targets: {sorted(target_ids - existing)}"
            )
        connection.execute("BEGIN")
        connection.execute(
            """
            UPDATE documents SET title = ?, kind = ?, summary = ? WHERE id = ?
            """,
            (
                data["title"],
                data["kind"],
                data["summary"],
                data["document_id"],
            ),
        )
        connection.execute(
            "DELETE FROM document_topics WHERE document_id = ?",
            (data["document_id"],),
        )
        connection.executemany(
            "INSERT INTO document_topics(document_id, topic) VALUES (?, ?)",
            [(data["document_id"], topic) for topic in data["topics"]],
        )
        connection.execute(
            "DELETE FROM document_links WHERE from_document_id = ?",
            (data["document_id"],),
        )
        connection.executemany(
            """
            INSERT INTO document_links(
                from_document_id, relation, to_document_id
            ) VALUES (?, ?, ?)
            """,
            [
                (
                    data["document_id"],
                    link["relation"],
                    link["to_document_id"],
                )
                for link in data["links"]
            ],
        )
        verify_database(connection)
        after = editable_state(connection, data["document_id"])
        connection.commit()
        return {
            "document_id": data["document_id"],
            "before": before,
            "after": after,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def build_parser():
    parser = JsonArgumentParser(description="Write the Superstore ledger")
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("scan", help="scan one explicit Markdown path")
    scan.add_argument("--db", required=True)
    scan.add_argument("--workspace-root", required=True)
    scan.add_argument("path")
    scan.set_defaults(handler=command_scan)
    archive = commands.add_parser("archive", help="archive a confirmed manifest")
    archive.add_argument("--db", required=True)
    archive.add_argument("--manifest", required=True)
    archive.set_defaults(handler=command_archive)
    metadata = commands.add_parser(
        "metadata", help="replace editable discovery metadata"
    )
    metadata.add_argument("--db", required=True)
    metadata.add_argument("--manifest", required=True)
    metadata.set_defaults(handler=command_metadata)
    return parser


def main():
    arguments = build_parser().parse_args()
    try:
        json_success(arguments.handler(arguments))
    except LedgerError as exc:
        fail(exc)
    except (json.JSONDecodeError, sqlite3.Error, zlib.error) as exc:
        fail(exc)
    except OSError as exc:
        fail(exc)


if __name__ == "__main__":
    main()
