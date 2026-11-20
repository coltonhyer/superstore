from pathlib import Path
import tempfile
import unittest

from src.release_manifest import load_manifest
from src.release_storage import load_record, save_record


class ReleaseConventionTests(unittest.TestCase):
    def test_manifest_and_storage_conventions(self):
        record = load_manifest({"name": "app", "version": "1.0"})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "release.json"
            save_record(path, record)
            self.assertEqual(load_record(path), record)
