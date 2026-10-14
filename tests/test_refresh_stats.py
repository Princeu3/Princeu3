from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scripts.refresh_stats import activity_svg, refresh, validate_svg


VALID = b'<svg xmlns="http://www.w3.org/2000/svg"><text>Current Streak</text></svg>'


class StatsRefreshTests(TestCase):
    def test_activity_totals_and_zero_days(self):
        for theme in ("light", "dark"):
            graph = activity_svg([("2026-10-13", 0), ("2026-10-14", 80)], theme)
            self.assertIn(b"80 contributions", graph)
            self.assertIn(b"1 active days", graph)
            validate_svg(graph, "contributions")
            zero = activity_svg([("2026-10-14", 0)], theme)
            self.assertIn(b"0 contributions", zero)
            self.assertNotIn(b"nan", zero)

    def test_accepts_expected_svg(self):
        self.assertEqual(validate_svg(VALID, "Current Streak"), VALID)

    def test_rejects_error_card_and_active_content(self):
        for data in (
            b'<svg xmlns="http://www.w3.org/2000/svg"><text>Rate limited</text></svg>',
            VALID.replace(b"</svg>", b"<script>alert(1)</script></svg>"),
            VALID.replace(b"<text>", b'<text onclick="alert(1)">'),
        ):
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_svg(data, "Current Streak")

    def test_failed_fetch_preserves_every_snapshot(self):
        with TemporaryDirectory() as directory:
            destination = Path(directory)
            old = destination / "streak-light.svg"
            old.write_bytes(b"previous snapshot")
            with patch("scripts.refresh_stats.download", side_effect=[VALID, OSError("offline")]):
                with self.assertRaises(OSError):
                    refresh(destination)
            self.assertEqual(old.read_bytes(), b"previous snapshot")
            self.assertEqual(list(destination.iterdir()), [old])
