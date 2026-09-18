import unittest

from src.counts import parse_count


class CountTests(unittest.TestCase):
    def test_parse_count_accepts_zero(self):
        self.assertEqual(parse_count("0"), 0)

    def test_parse_count_rejects_malformed_text(self):
        with self.assertRaises(ValueError):
            parse_count("abc")
