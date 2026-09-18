import unittest

from src.labels import normalize_label


class LabelTests(unittest.TestCase):
    def test_normalize_label_trims_whitespace(self):
        self.assertEqual(normalize_label(" ab "), "AB")
