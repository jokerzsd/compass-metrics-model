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


class OpenharmonyCiExclusionTest(unittest.TestCase):
    """CI bot 排除用精确匹配，不再把 openharmony_ci 的子串误当作 bot 排除。"""

    def _run(self, module, names):
        date = datetime.datetime(2026, 9, 1)
        from_date = date - datetime.timedelta(days=90)
        source_list = [_make_source(n) for n in names]
        with patch.object(module, "get_contributor_list", return_value=source_list):
            return module.contributor_detail_list(
                client=None,
                contributors_enriched_index="test-index",
                date=date,
                repo_list=["demo/repo"],
                from_date=from_date,
            )

    def test_substring_contributor_not_excluded_v2(self):
        # "openharmony" 是 "openharmony_ci" 的子串，不应被当作 bot 排除
        result = self._run(contributor_metrics_v2, ["openharmony"])
        self.assertEqual(result["core_count"], 1)

    def test_substring_contributor_not_excluded_v1(self):
        result = self._run(contributor_metrics, ["openharmony"])
        self.assertEqual(result["core_count"], 1)

    def test_exact_ci_bot_excluded_v2(self):
        result = self._run(contributor_metrics_v2, ["openharmony_ci"])
        self.assertEqual(result["core_count"], 0)
        self.assertEqual(result["regular_count"], 0)
        self.assertEqual(result["casual_count"], 0)

    def test_exact_ci_bot_excluded_v1(self):
        result = self._run(contributor_metrics, ["openharmony_ci"])
        self.assertEqual(result["core_count"], 0)
        self.assertEqual(result["regular_count"], 0)
        self.assertEqual(result["casual_count"], 0)


if __name__ == "__main__":
    unittest.main()
