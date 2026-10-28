import unittest
from scripts.evaluate_effort import assess_usage


class UsageTests(unittest.TestCase):
    def test_unknown_usage_is_not_zero_cost(self):
        self.assertIsNone(assess_usage(None))

    def test_cumulative_input_does_not_double_count_cached_tokens(self):
        row = assess_usage({'input_tokens': 100, 'cached_input_tokens': 80, 'output_tokens': 10})
        self.assertEqual(row['uncached_input_tokens'], 20)
        self.assertEqual(row['total_tokens'], 110)

    def test_invalid_usage_cannot_appear_as_savings(self):
        for row in ({}, {'input_tokens': 1, 'cached_input_tokens': 2, 'output_tokens': 0},
                    {'input_tokens': True, 'cached_input_tokens': 0, 'output_tokens': 0}):
            with self.subTest(row=row), self.assertRaises(ValueError):
                assess_usage(row)
