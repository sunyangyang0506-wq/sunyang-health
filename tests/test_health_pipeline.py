import unittest

from app.connectors.apple_health import normalize_records
from app.reports.daily_report import generate_daily_report


class HealthPipelineTests(unittest.TestCase):
    def test_normalize_step_record_uses_device_local_date(self):
        records = normalize_records([
            {
                "metric": "stepCount",
                "value": 8000,
                "unit": "count",
                "recorded_at": "2026-08-07T22:30:00Z",
                "record_date": "2026-08-08",
                "source": "Apple Health",
            }
        ])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["metric"], "steps")
        self.assertEqual(records[0]["value"], 8000)
        self.assertEqual(records[0]["record_date"], "2026-08-08")

    def test_normalize_body_mass_converts_pounds_to_kg(self):
        records = normalize_records([
            {
                "metric": "bodyMass",
                "value": 154.324,
                "unit": "lb",
                "recorded_at": "2026-08-08T07:00:00+09:00",
                "record_date": "2026-08-08",
            }
        ])
        self.assertEqual(records[0]["metric"], "weight_kg")
        self.assertAlmostEqual(records[0]["value"], 70.0, places=1)
        self.assertEqual(records[0]["unit"], "kg")

    def test_normalize_lean_body_mass_is_not_muscle_mass(self):
        records = normalize_records([
            {
                "metric": "leanBodyMass",
                "value": 48.3,
                "unit": "kg",
                "recorded_at": "2026-08-08T07:00:00+09:00",
                "record_date": "2026-08-08",
            }
        ])
        self.assertEqual(records[0]["metric"], "lean_body_mass_kg")
        self.assertEqual(records[0]["value"], 48.3)

    def test_normalize_sleep_uses_canonical_total_sleep_hours(self):
        records = normalize_records([
            {
                "metric": "sleepAnalysis",
                "value": 426,
                "unit": "min",
                "recorded_at": "2026-08-08T06:30:00+09:00",
                "record_date": "2026-08-08",
            }
        ])
        self.assertEqual(records[0]["metric"], "total_sleep_hours")
        self.assertAlmostEqual(records[0]["value"], 7.1, places=2)
        self.assertEqual(records[0]["unit"], "h")

    def test_invalid_record_does_not_abort_batch(self):
        records = normalize_records([
            {"metric": "stepCount", "value": "not-a-number", "recorded_at": "2026-08-08T08:00:00+09:00"},
            {
                "metric": "heartRateVariabilitySDNN",
                "value": 41,
                "unit": "ms",
                "recorded_at": "2026-08-08T08:00:00+09:00",
                "record_date": "2026-08-08",
            },
        ])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["metric"], "hrv_ms")

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
