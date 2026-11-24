from pathlib import Path
import json
import tempfile
import unittest

from cad_library_pages.models import prepare_models


class ModelPagesTests(unittest.TestCase):
    def test_multiple_purposes_are_public_and_verification_only_is_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for item, purpose in (
                ("box", "[example, verification]"),
                ("fixture", "[verification]"),
            ):
                owner = root / "models" / item
                owner.mkdir(parents=True)
                (owner / "model.yml").write_text(
                    f"title: {item}\npurpose: {purpose}\n"
                )
                (owner / "ci.yml").write_text(
                    f"id: {item}\nprimary: cadquery\n"
                )

            evidence = root / "build" / "models" / "box"
            (evidence / "cadquery/verification").mkdir(parents=True)
            (evidence / "result.json").write_text(json.dumps({
                "id": "box",
                "status": "pass",
                "primary": "cadquery",
                "implementations": {
                    "cadquery": {
                        "builder": "builder-cadquery",
                        "build_status": "pass",
                        "verification_status": "pass",
                    }
                },
            }))
            (evidence / "source.json").write_text(
                json.dumps({"source_sha": "test-sha"})
            )
            (evidence / "model.stl").write_text("mesh")
            (evidence / "cadquery/model.stl").write_text("mesh")
            (evidence / "cadquery/result.json").write_text("{}")
            (evidence / "cadquery/verification/verification.json").write_text("{}")

            site = root / "site"
            prepare_models(root, site, root / "build")
            page = site / "content/models/box/index.md"
            self.assertIn("test-sha", page.read_text())
            self.assertIn("cadquery", page.read_text())
            self.assertTrue((site / "static/models/box/model.stl").is_file())
            self.assertFalse((site / "content/models/fixture").exists())


if __name__ == "__main__":
    unittest.main()
