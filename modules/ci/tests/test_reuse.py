import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from cad_library_ci.reuse import _rebind_plan, materialize


class ReuseQualificationTests(unittest.TestCase):
    def test_rebind_plan_records_permanent_and_qualified_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp)
            qualified = "a" * 40
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
                pr_number=12,
                run_id=34,
            )
            plan = json.loads((candidate / "build-plan.json").read_text())
            self.assertEqual(plan["source_sha"], source)
            self.assertEqual(plan["qualified_source_sha"], qualified)
            self.assertTrue(plan["qualification_reused"])
            self.assertEqual(plan["qualification_pr"], 12)
            self.assertEqual(plan["qualification_run_id"], 34)

    def test_rebind_plan_rejects_artifact_from_other_head(self):
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
                    pr_number=12,
                    run_id=34,
                )

    @patch("cad_library_ci.reuse._tree_sha", side_effect=["tree", "tree"])
    @patch("cad_library_ci.reuse._download_artifact")
    @patch("cad_library_ci.reuse.reusable_pr_qualification")
    def test_materialize_reuses_tree_identical_green_pr(
        self,
        evidence,
        download,
        _tree,
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "build/qualification"
            qualified = "a" * 40
            source = "b" * 40
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
                qualified_source_sha=qualified,
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
            )

            self.assertTrue(result["reuse"])
            plan = json.loads((candidate / "build-plan.json").read_text())
            self.assertEqual(plan["source_sha"], source)
            self.assertEqual(plan["qualified_source_sha"], qualified)

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
            )
            self.assertFalse(result["reuse"])
            self.assertEqual(result["reason"], "branch-not-configured")


if __name__ == "__main__":
    unittest.main()
