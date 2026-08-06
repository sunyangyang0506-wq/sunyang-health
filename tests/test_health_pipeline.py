import unittest

from app.connectors.apple_health import normalize_records
from app.reports.daily_report import generate_daily_report


class HealthPipelineTests(unittest.TestCase):
    def test_normalize_step_record(self):
        records = normalize_records([
            {
                "type": "HKQuantityTypeIdentifierStepCount",
                "value": 8000,
                "unit": "count",
                "start_date": "2026-08-07T06:30:00+08:00",
                "source": "Apple Watch",
            }
        ])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["metric"], "steps")
        self.assertEqual(records[0]["value"], 8000)

    def test_daily_report_handles_missing_data(self):
        report = generate_daily_report({
            "record_date": "2026-08-07",
            "body": {},
            "activity": {},
            "sleep": {},
            "nutrition": {},
            "quality": {"sufficient": False},
            "conflicts": [],
        })
        self.assertEqual(report["record_date"], "2026-08-07")
        self.assertIn("safety", report)
        self.assertTrue(report["core_conclusion"])


if __name__ == "__main__":
    unittest.main()
