#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid


SCHEMA_VERSION = 1


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
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": str(uuid.uuid4()),
        "source_root": target.as_posix(),
        "source_type": source_type,
        "workspace_root": workspace_root.as_posix(),
        "existing_topics": [],
        "documents": documents,
    }


def build_parser():
    parser = JsonArgumentParser(description="Write the Superstore ledger")
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("scan", help="scan one explicit Markdown path")
    scan.add_argument("--db", required=True)
    scan.add_argument("--workspace-root", required=True)
    scan.add_argument("path")
    scan.set_defaults(handler=command_scan)
    return parser


def main():
    arguments = build_parser().parse_args()
    try:
        json_success(arguments.handler(arguments))
    except LedgerError as exc:
        fail(exc)
    except OSError as exc:
        fail(exc)


if __name__ == "__main__":
    main()
