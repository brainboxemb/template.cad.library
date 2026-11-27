import unittest
from unittest.mock import patch

from cad_library_ci.history import (
    changed_paths,
    changed_paths_from_base,
    changed_paths_from_parent,
    last_successful_dev_sha,
    reusable_pr_qualification,
)


class HistoryTests(unittest.TestCase):
    @patch("cad_library_ci.history._json")
    def test_last_successful_dev_excludes_pull_request_and_current_target(self, get):
        get.return_value = {
            "workflow_runs": [
                {
                    "id": 20,
                    "event": "pull_request",
                    "status": "completed",
                    "conclusion": "success",
                    "head_sha": "pr",
                },
                {
                    "id": 19,
                    "event": "push",
                    "status": "completed",
                    "conclusion": "success",
                    "head_sha": "target",
                },
                {
                    "id": 18,
                    "event": "push",
                    "status": "completed",
                    "conclusion": "success",
                    "head_sha": "baseline",
                },
            ]
        }
        self.assertEqual(
            last_successful_dev_sha(
                repository="owner/repo",
                branch="dev",
                token="token",
                current_run_id=21,
                target_sha="target",
            ),
            "baseline",
        )

    @patch("cad_library_ci.history._json")
    def test_experimental_history_requests_only_exp(self, get):
        get.return_value = {"workflow_runs": []}
        self.assertIsNone(last_successful_dev_sha(repository="owner/repo", branch="exp", token="token", current_run_id=1, target_sha="new"))
        self.assertIn("branch=exp&", get.call_args.args[0])

    @patch("cad_library_ci.history._json")
    def test_reusable_pr_qualification_requires_exact_tree_and_green_latest_run(
        self,
        get,
    ):
        source = "a" * 40
        head = "b" * 40
        tree = "c" * 40
        get.side_effect = [
            [
                {
                    "number": 12,
                    "state": "closed",
                    "merged_at": "2026-01-01T00:00:00Z",
                    "merge_commit_sha": source,
                    "base": {"ref": "exp"},
                    "head": {
                        "sha": head,
                        "repo": {"full_name": "owner/repo"},
                    },
                }
            ],
            {"tree": {"sha": tree}},
            {"tree": {"sha": tree}},
            {
                "workflow_runs": [
                    {
                        "id": 31,
                        "status": "completed",
                        "conclusion": "success",
                        "head_sha": head,
                        "pull_requests": [{"number": 12}],
                    }
                ]
            },
            {
                "artifacts": [
                    {
                        "id": 99,
                        "name": "cad-qualification",
                        "expired": False,
                    }
                ]
            },
        ]

        evidence = reusable_pr_qualification(
            repository="owner/repo",
            branch="exp",
            token="token",
            source_sha=source,
        )
        self.assertEqual(evidence.pr_number, 12)
        self.assertEqual(evidence.qualified_source_sha, head)
        self.assertEqual(evidence.run_id, 31)
        self.assertEqual(evidence.artifact_id, 99)

    @patch("cad_library_ci.history._json")
    def test_reusable_pr_qualification_rejects_older_green_when_latest_failed(
        self,
        get,
    ):
        source = "d" * 40
        head = "e" * 40
        tree = "f" * 40
        get.side_effect = [
            [
                {
                    "number": 13,
                    "state": "closed",
                    "merged_at": "2026-01-01T00:00:00Z",
                    "merge_commit_sha": source,
                    "base": {"ref": "exp"},
                    "head": {
                        "sha": head,
                        "repo": {"full_name": "owner/repo"},
                    },
                }
            ],
            {"tree": {"sha": tree}},
            {"tree": {"sha": tree}},
            {
                "workflow_runs": [
                    {
                        "id": 42,
                        "status": "completed",
                        "conclusion": "failure",
                        "head_sha": head,
                        "pull_requests": [{"number": 13}],
                    },
                    {
                        "id": 41,
                        "status": "completed",
                        "conclusion": "success",
                        "head_sha": head,
                        "pull_requests": [{"number": 13}],
                    },
                ]
            },
        ]

        self.assertIsNone(
            reusable_pr_qualification(
                repository="owner/repo",
                branch="exp",
                token="token",
                source_sha=source,
            )
        )

    @patch("cad_library_ci.history._json")
    def test_reusable_pr_qualification_rejects_changed_merge_tree(self, get):
        source = "1" * 40
        head = "2" * 40
        get.side_effect = [
            [
                {
                    "number": 14,
                    "state": "closed",
                    "merged_at": "2026-01-01T00:00:00Z",
                    "merge_commit_sha": source,
                    "base": {"ref": "exp"},
                    "head": {
                        "sha": head,
                        "repo": {"full_name": "owner/repo"},
                    },
                }
            ],
            {"tree": {"sha": "3" * 40}},
            {"tree": {"sha": "4" * 40}},
        ]
        self.assertIsNone(
            reusable_pr_qualification(
                repository="owner/repo",
                branch="exp",
                token="token",
                source_sha=source,
            )
        )

    @patch("cad_library_ci.history.subprocess.run")
    def test_non_ancestor_baseline_forces_full_fallback(self, run):
        run.return_value.returncode = 1
        self.assertIsNone(changed_paths(".", "old", "new"))

    @patch("cad_library_ci.history.subprocess.run")
    def test_changed_paths_uses_exact_baseline_and_target(self, run):
        ancestor = type("Result", (), {"returncode": 0})()
        diff = type("Result", (), {"stdout": "modules/build/ci.yml\nmodels/box/model.yml\n"})()
        run.side_effect = [ancestor, diff]
        self.assertEqual(
            changed_paths(".", "aaa", "bbb"),
            ("modules/build/ci.yml", "models/box/model.yml"),
        )
        self.assertEqual(
            run.call_args_list[1].args[0],
            ["git", "-C", ".", "diff", "--name-only", "aaa", "bbb", "--"],
        )


    @patch("cad_library_ci.history.changed_paths")
    @patch("cad_library_ci.history.subprocess.run")
    def test_single_parent_delta_uses_parent_as_baseline(self, run, changed):
        run.return_value.stdout = "target parent\n"
        changed.return_value = ("CHANGELOG.md",)
        self.assertEqual(
            changed_paths_from_parent(".", "target"),
            ("CHANGELOG.md",),
        )
        changed.assert_called_once_with(".", "parent", "target")

    @patch("cad_library_ci.history.subprocess.run")
    def test_merge_commit_is_not_release_only_parent_delta(self, run):
        run.return_value.stdout = "target parent1 parent2\n"
        self.assertIsNone(changed_paths_from_parent(".", "target"))

    @patch("cad_library_ci.history.changed_paths")
    @patch("cad_library_ci.history.subprocess.run")
    def test_pr_delta_uses_remote_base_merge_base(self, run, changed):
        run.return_value.returncode = 0
        run.return_value.stdout = "base-sha\n"
        changed.return_value = ("cadlib/pyproject.toml",)
        self.assertEqual(
            changed_paths_from_base(".", "main", "HEAD"),
            ("cadlib/pyproject.toml",),
        )
        changed.assert_called_once_with(".", "base-sha", "HEAD")

if __name__ == "__main__":
    unittest.main()
