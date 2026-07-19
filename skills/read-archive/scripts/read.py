#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import zlib


SCHEMA_VERSION = 1
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
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


def fail(message):
    print(json.dumps({"error": str(message)}, sort_keys=True), file=sys.stderr)
    raise SystemExit(2)


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        fail(message)


def slug_argument(value):
    if not SLUG.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "value must be a normalized lowercase slug"
        )
    return value


def rfc3339_argument(value):
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "archive dates must be RFC 3339 timestamps"
        ) from exc
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError(
            "archive dates must include a timezone"
        )
    return (
        parsed.astimezone(datetime.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def escape_like(value):
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def connect_readonly(path):
    if not path.is_file():
        raise LedgerError(f"ledger does not exist: {path}")
    connection = None
    try:
        connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA query_only = ON")
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if version != SCHEMA_VERSION:
            raise LedgerError(
                f"unsupported ledger schema version {version}; "
                f"expected {SCHEMA_VERSION}"
            )
        for table, expected in EXPECTED_COLUMNS.items():
            actual = tuple(
                row[1] for row in connection.execute(f"PRAGMA table_info({table})")
            )
            if actual != expected:
                raise LedgerError(
                    f"ledger schema is missing or invalid table: {table}"
                )
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
            raise LedgerError(
                f"ledger schema objects are missing: {sorted(missing)}"
            )
        return connection
    except LedgerError:
        if connection is not None:
            connection.close()
        raise
    except sqlite3.Error as exc:
        if connection is not None:
            connection.close()
        raise LedgerError(f"ledger is not a valid SQLite database: {exc}") from exc


def topics_for(connection, document_id):
    return [
        row[0]
        for row in connection.execute(
            """
            SELECT topic FROM document_topics
            WHERE document_id = ? ORDER BY topic
            """,
            (document_id,),
        )
    ]


def links_for(connection, document_id, direction):
    if direction == "outgoing":
        sql = """
            SELECT l.relation, d.id, d.title, d.kind, d.source_path
            FROM document_links AS l
            JOIN documents AS d ON d.id = l.to_document_id
            WHERE l.from_document_id = ?
            ORDER BY l.relation, d.title, d.id
        """
    else:
        sql = """
            SELECT l.relation, d.id, d.title, d.kind, d.source_path
            FROM document_links AS l
            JOIN documents AS d ON d.id = l.from_document_id
            WHERE l.to_document_id = ?
            ORDER BY l.relation, d.title, d.id
        """
    return [
        {
            "relation": row[0],
            "document_id": row[1],
            "title": row[2],
            "kind": row[3],
            "source_path": row[4],
        }
        for row in connection.execute(sql, (document_id,))
    ]


def document_projection(connection, row):
    return {
        "id": row["id"],
        "title": row["title"],
        "kind": row["kind"],
        "source_path": row["source_path"],
        "archived_at": row["archived_at"],
        "summary": row["summary"],
        "topics": topics_for(connection, row["id"]),
        "outgoing_links": links_for(connection, row["id"], "outgoing"),
        "incoming_links": links_for(connection, row["id"], "incoming"),
    }


def command_topics(arguments):
    connection = connect_readonly(Path(arguments.db).expanduser().absolute())
    try:
        rows = connection.execute(
            """
            SELECT topic, COUNT(*) AS document_count
            FROM document_topics
            GROUP BY topic
            ORDER BY topic
            """
        )
        return {
            "topics": [
                {"topic": row[0], "document_count": row[1]} for row in rows
            ]
        }
    finally:
        connection.close()


def command_search(arguments):
    if not 1 <= arguments.limit <= 200:
        raise LedgerError("limit must be between 1 and 200")
    clauses = []
    parameters = []
    for column, value in (
        ("d.title", arguments.title),
        ("d.source_path", arguments.path),
        ("d.summary", arguments.summary),
    ):
        if value is not None:
            clauses.append(f"{column} LIKE ? ESCAPE '\\'")
            parameters.append(f"%{escape_like(value)}%")
    if arguments.kind is not None:
        clauses.append("d.kind = ?")
        parameters.append(arguments.kind)
    if arguments.archived_after is not None:
        clauses.append("r.archived_at >= ?")
        parameters.append(arguments.archived_after)
    if arguments.archived_before is not None:
        clauses.append("r.archived_at <= ?")
        parameters.append(arguments.archived_before)
    for topic in arguments.topic:
        clauses.append(
            """
            EXISTS (
                SELECT 1 FROM document_topics AS selected_topic
                WHERE selected_topic.document_id = d.id
                  AND selected_topic.topic = ?
            )
            """
        )
        parameters.append(topic)
    if not arguments.include_superseded:
        clauses.append(
            """
            NOT EXISTS (
                SELECT 1 FROM document_links AS newer
                WHERE newer.relation = 'supersedes'
                  AND newer.to_document_id = d.id
            )
            """
        )
    where = " AND ".join(f"({clause})" for clause in clauses) or "1"
    parameters.append(arguments.limit)
    connection = connect_readonly(Path(arguments.db).expanduser().absolute())
    try:
        rows = connection.execute(
            f"""
            SELECT d.id, d.title, d.kind, d.source_path, d.summary, r.archived_at
            FROM documents AS d
            JOIN archive_runs AS r ON r.id = d.archive_run_id
            WHERE {where}
            ORDER BY r.archived_at DESC, d.title, d.id
            LIMIT ?
            """,
            parameters,
        )
        return {
            "documents": [
                document_projection(connection, row) for row in rows
            ],
            "limit": arguments.limit,
            "include_superseded": arguments.include_superseded,
        }
    finally:
        connection.close()


def command_show(arguments):
    connection = connect_readonly(Path(arguments.db).expanduser().absolute())
    try:
        row = connection.execute(
            """
            SELECT d.id, d.title, d.kind, d.source_path, d.summary,
                   d.content_zlib, d.content_sha256, d.source_bytes,
                   r.archived_at
            FROM documents AS d
            JOIN archive_runs AS r ON r.id = d.archive_run_id
            WHERE d.id = ?
            """,
            (arguments.document_id,),
        ).fetchone()
        if row is None:
            raise LedgerError(f"unknown document: {arguments.document_id}")
        try:
            raw = zlib.decompress(row["content_zlib"])
        except (TypeError, zlib.error) as exc:
            raise LedgerError(
                f"invalid compressed payload: {row['source_path']}"
            ) from exc
        if len(raw) != row["source_bytes"]:
            raise LedgerError(
                f"payload byte length mismatch: {row['source_path']}"
            )
        if hashlib.sha256(raw).hexdigest() != row["content_sha256"]:
            raise LedgerError(f"payload SHA-256 mismatch: {row['source_path']}")
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise LedgerError(
                f"archived payload is not UTF-8: {row['source_path']}"
            ) from exc
        document = document_projection(connection, row)
        document["supersedes"] = [
            link
            for link in document["outgoing_links"]
            if link["relation"] == "supersedes"
        ]
        document["superseded_by"] = [
            link
            for link in document["incoming_links"]
            if link["relation"] == "supersedes"
        ]
        return {"document": document, "content": content}
    finally:
        connection.close()


def build_parser():
    parser = JsonArgumentParser(description="Read the Superstore ledger")
    commands = parser.add_subparsers(dest="command", required=True)

    topics = commands.add_parser("topics", help="list topic counts")
    topics.add_argument("--db", required=True)
    topics.set_defaults(handler=command_topics)

    search = commands.add_parser("search", help="search discovery metadata")
    search.add_argument("--db", required=True)
    search.add_argument("--title")
    search.add_argument("--kind", type=slug_argument)
    search.add_argument("--path")
    search.add_argument(
        "--topic", action="append", default=[], type=slug_argument
    )
    search.add_argument("--summary")
    search.add_argument("--archived-after", type=rfc3339_argument)
    search.add_argument("--archived-before", type=rfc3339_argument)
    search.add_argument("--include-superseded", action="store_true")
    search.add_argument("--limit", type=int, default=20)
    search.set_defaults(handler=command_search)

    show = commands.add_parser("show", help="show one verified document")
    show.add_argument("--db", required=True)
    show.add_argument("document_id")
    show.set_defaults(handler=command_show)
    return parser


def main():
    arguments = build_parser().parse_args()
    try:
        print(json.dumps(arguments.handler(arguments), sort_keys=True))
    except (LedgerError, OSError, RuntimeError, TypeError, sqlite3.Error) as exc:
        fail(exc)


if __name__ == "__main__":
    main()
