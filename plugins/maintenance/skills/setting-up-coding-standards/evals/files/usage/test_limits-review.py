import unittest

from src.limits import parseLimit


class LimitTests(unittest.TestCase):
    def test_1(self):
        self.assertEqual(parseLimit("10"), 10)
