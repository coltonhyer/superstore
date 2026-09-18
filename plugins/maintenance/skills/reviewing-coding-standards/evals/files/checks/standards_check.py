#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("source")
    args = parser.parse_args()
    rules = json.loads(Path(args.config).read_text(encoding="utf-8"))["rules"]
    lines = Path(args.source).read_text(encoding="utf-8").splitlines()
    found = False
    for number, line in enumerate(lines, 1):
        for rule in rules:
            if rule["token"] in line:
                severity = rule.get("severity", "unspecified")
                print(f'{args.source}:{number}: {rule["code"]} [{severity}]')
                found = True
    return int(found)


if __name__ == "__main__":
    raise SystemExit(main())

