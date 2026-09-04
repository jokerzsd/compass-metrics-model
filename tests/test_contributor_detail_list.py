import datetime
import unittest
from unittest.mock import patch

from compass_metrics import contributor_metrics
from compass_metrics_v2 import contributor_metrics_v2


def _make_source(contributor, contribution=10):
    return {
        "contributor": contributor,
        "contribution": contribution,
        "contribution_without_observe": contribution,
        "ecological_type": "individual participant",
        "organization": "example-org",
        "is_bot": False,
        "repo_name": "demo/repo",
        "contribution_type_list": [{"contribution_type": "code", "contribution": contribution}],
    }


class ContributorDetailListShortWindowTest(unittest.TestCase):
    """issue #195: 少于四周的分析窗口不应抛 UnboundLocalError。"""

    def _run(self, module):
        date = datetime.datetime(2026, 9, 1)
        from_date = date - datetime.timedelta(days=3)
        source_list = [_make_source("alice")]
        with patch.object(module, "get_contributor_list", return_value=source_list):
            return module.contributor_detail_list(
                client=None,
                contributors_enriched_index="test-index",
                date=date,
                repo_list=["demo/repo"],
                from_date=from_date,
            )

    def test_short_window_v2(self):
        result = self._run(contributor_metrics_v2)
        self.assertEqual(result["core_count"], 1)
        self.assertEqual(result["regular_count"], 0)
        self.assertEqual(result["casual_count"], 0)
        self.assertEqual(len(result["contributor_detail_list"]), 1)

    def test_short_window_v1(self):
        result = self._run(contributor_metrics)
        self.assertEqual(result["core_count"], 1)
        self.assertEqual(result["regular_count"], 0)
        self.assertEqual(result["casual_count"], 0)
        self.assertEqual(len(result["contributor_detail_list"]), 1)


if __name__ == "__main__":
    unittest.main()
