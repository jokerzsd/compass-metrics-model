import datetime
import unittest
from unittest.mock import patch

from compass_metrics import contributor_metrics


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


class ContributorFilterMileageTest(unittest.TestCase):
    """filter_mileage 用 == 比较，非字面量字符串也能正确过滤（修复 is 比较导致的 UnboundLocalError）。"""

    def _run(self, filter_mileage):
        date = datetime.datetime(2026, 9, 1)
        from_date = date - datetime.timedelta(days=90)
        source_list = [_make_source("alice", 10), _make_source("bob", 1)]
        with patch.object(contributor_metrics, "get_contributor_list", return_value=source_list):
            return contributor_metrics.contributor_detail_list(
                client=None,
                contributors_enriched_index="test-index",
                date=date,
                repo_list=["demo/repo"],
                from_date=from_date,
                filter_mileage=filter_mileage,
            )

    def test_filter_mileage_core_with_non_interned_string(self):
        # "".join 构造的非字面量字符串，原 `is` 比较会返回 False 并抛 UnboundLocalError
        result = self._run("".join(["c", "o", "r", "e"]))
        self.assertEqual(result["core_count"], 1)
        self.assertEqual(result["regular_count"], 0)
        self.assertEqual(result["casual_count"], 1)
        self.assertEqual(len(result["contributor_detail_list"]), 1)
        self.assertEqual(result["contributor_detail_list"][0]["mileage_type"], "core")

    def test_filter_mileage_casual_with_non_interned_string(self):
        result = self._run("".join(["c", "a", "s", "u", "a", "l"]))
        self.assertEqual(result["casual_count"], 1)
        self.assertEqual(len(result["contributor_detail_list"]), 1)
        self.assertEqual(result["contributor_detail_list"][0]["mileage_type"], "casual")


if __name__ == "__main__":
    unittest.main()
