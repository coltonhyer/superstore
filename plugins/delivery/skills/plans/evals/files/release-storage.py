import json


def save_record(path, record):
    path.write_text(json.dumps(record), encoding="utf-8")


def load_record(path):
    return json.loads(path.read_text(encoding="utf-8"))
