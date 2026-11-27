import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from cad_library_ci.reuse import (
    _rebind_plan,
    _require_same_qualified_tree,
    materialize,
)


class ReuseQualificationTests(unittest.TestCase):
    @patch("cad_library_ci.reuse._commit")
    def test_same_qualified_tree_requires_exact_pr_merge_parents(self, commit):
        base = "d" * 40
        head = "c" * 40
        tree = "e" * 40
        commit.side_effect = [
            {"tree": {"sha": tree}, "parents": [{"sha": base}]},
            {
                "tree": {"sha": tree},
                "parents": [{"sha": base}, {"sha": head}],
            },
        ]
        _require_same_qualified_tree(
            repository="owner/repo",
            source_sha="b" * 40,
            qualified_source_sha="a" * 40,
            base_sha=base,
            head_sha=head,
            token="token",
        )

    @patch("cad_library_ci.reuse._commit")
    def test_same_qualified_tree_rejects_changed_tree(self, commit):
        commit.side_effect = [
            {"tree": {"sha": "1" * 40}, "parents": []},
            {"tree": {"sha": "2" * 40}, "parents": []},
        ]
        with self.assertRaisesRegex(ValueError, "differs"):
            _require_same_qualified_tree(
                repository="owner/repo",
                source_sha="b" * 40,
                qualified_source_sha="a" * 40,
                base_sha="d" * 40,
                head_sha="c" * 40,
                token="token",
            )

    def test_rebind_plan_records_permanent_and_qualified_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp)
            qualified = "a" * 40
            head = "c" * 40
            source = "b" * 40
            (candidate / "build-plan.json").write_text(
                json.dumps(
                    {
                        "schema": 2,
                        "source_sha": qualified,
                        "active": [],
                        "selected": [],
                        "full": False,
                        "library": False,
                    }
                )
            )
            _rebind_plan(
                candidate,
                source_sha=source,
                qualified_source_sha=qualified,
                qualified_head_sha=head,
                pr_number=12,
                run_id=34,
            )
            plan = json.loads((candidate / "build-plan.json").read_text())
            self.assertEqual(plan["source_sha"], source)
            self.assertEqual(plan["qualified_source_sha"], qualified)
            self.assertEqual(plan["qualified_head_sha"], head)
            self.assertTrue(plan["qualification_reused"])
            self.assertEqual(plan["qualification_pr"], 12)
            self.assertEqual(plan["qualification_run_id"], 34)

    def test_rebind_plan_rejects_artifact_from_other_qualified_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp)
            (candidate / "build-plan.json").write_text(
                json.dumps({"schema": 2, "source_sha": "wrong"})
            )
            with self.assertRaisesRegex(ValueError, "provenance mismatch"):
                _rebind_plan(
                    candidate,
                    source_sha="b" * 40,
                    qualified_source_sha="a" * 40,
                    qualified_head_sha="c" * 40,
                    pr_number=12,
                    run_id=34,
                )

    @patch("cad_library_ci.reuse._require_same_qualified_tree")
    @patch("cad_library_ci.reuse._download_artifact")
    @patch("cad_library_ci.reuse.reusable_pr_qualification")
    def test_materialize_reuses_bound_tree_identical_green_pr(
        self,
        evidence,
        download,
        same_tree,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "build/qualification"
            qualified = "a" * 40
            source = "b" * 40
            head = "c" * 40
            base = "d" * 40
            (root / "ci.yml").write_text(
                "schema: 1\n"
                "branches:\n"
                "  stable: main\n"
                "  development: dev\n"
                "roots:\n"
                "  modules: modules\n"
                "  models: models\n"
                "  api_probes: api-probes\n"
                "  output: build\n"
                "qualification:\n"
                "  permanent:\n"
                "    reuse_pr_qualification:\n"
                "      branches: [exp]\n"
            )
            evidence.return_value = SimpleNamespace(
                artifact_id=99,
                head_sha=head,
                base_sha=base,
                pr_number=12,
                run_id=34,
            )
            payload = io.BytesIO()
            with zipfile.ZipFile(payload, "w") as archive:
                archive.writestr(
                    "build-plan.json",
                    json.dumps(
                        {
                            "schema": 2,
                            "source_sha": qualified,
                            "active": [],
                            "selected": [],
                            "full": False,
                            "library": False,
                        }
                    ),
                )
            download.return_value = payload.getvalue()

            result = materialize(
                repo=root,
                repository="owner/repo",
                branch="exp",
                source_sha=source,
                token="token",
                candidate=candidate,
                pr_number=12,
                head_sha=head,
                run_id=34,
            )

            self.assertTrue(result["reuse"])
            plan = json.loads((candidate / "build-plan.json").read_text())
            self.assertEqual(plan["source_sha"], source)
            self.assertEqual(plan["qualified_source_sha"], qualified)
            self.assertEqual(plan["qualified_head_sha"], head)
            same_tree.assert_called_once_with(
                repository="owner/repo",
                source_sha=source,
                qualified_source_sha=qualified,
                base_sha=base,
                head_sha=head,
                token="token",
            )

    def test_materialize_is_disabled_for_unconfigured_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ci.yml").write_text(
                "schema: 1\n"
                "branches:\n"
                "  stable: main\n"
                "  development: dev\n"
                "roots:\n"
                "  modules: modules\n"
                "  models: models\n"
                "  api_probes: api-probes\n"
                "  output: build\n"
            )
            result = materialize(
                repo=root,
                repository="owner/repo",
                branch="exp",
                source_sha="b" * 40,
                token="token",
                candidate=root / "candidate",
                pr_number=12,
                head_sha="c" * 40,
                run_id=34,
            )
            self.assertFalse(result["reuse"])
            self.assertEqual(result["reason"], "branch-not-configured")

    def test_materialize_without_merge_policy_binding_falls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ci.yml").write_text(
                "schema: 1\n"
                "branches:\n"
                "  stable: main\n"
                "  development: dev\n"
                "roots:\n"
                "  modules: modules\n"
                "  models: models\n"
                "  api_probes: api-probes\n"
                "  output: build\n"
                "qualification:\n"
                "  permanent:\n"
                "    reuse_pr_qualification:\n"
                "      branches: [exp]\n"
            )
            result = materialize(
                repo=root,
                repository="owner/repo",
                branch="exp",
                source_sha="b" * 40,
                token="token",
                candidate=root / "candidate",
            )
            self.assertFalse(result["reuse"])
            self.assertEqual(result["reason"], "no-merge-policy-binding")


if __name__ == "__main__":
    unittest.main()
