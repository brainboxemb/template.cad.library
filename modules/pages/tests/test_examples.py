from pathlib import Path
import json
import tempfile
import unittest
from cad_library_pages.examples import prepare_examples


class ExamplePagesTests(unittest.TestCase):
    def test_public_example_has_evidence_and_fixture_is_not_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for item, purpose in (("box", "[example, verification]"), ("fixture", "verification")):
                owner = root / "examples" / item
                owner.mkdir(parents=True)
                (owner / "model.yml").write_text(f"title: {item}\npurpose: {purpose}\n")
                (owner / "ci.yml").write_text(f"id: {item}\nbuilder: builder-cadquery\nsource: model.py\n")
                (owner / "model.py").write_text("model = 1\n")
            evidence = root / "build" / "examples" / "box"
            (evidence / "verification").mkdir(parents=True)
            (evidence / "result.json").write_text(json.dumps({"id":"box","status":"pass","builder":"cadquery","verification_status":"pass"}))
            (evidence / "source.json").write_text(json.dumps({"source_sha":"test-sha"}))
            (evidence / "model.stl").write_text("mesh")
            (evidence / "verification/verification.json").write_text("{}")
            site = root / "site"
            prepare_examples(root, site, root/"build")
            bundle = site / "content/examples/box"
            data = json.loads((bundle/"index.md").read_text())
            self.assertEqual(data["params"]["provenance"]["source_sha"], "test-sha")
            self.assertTrue((bundle/"model.stl").is_file())
            self.assertTrue((bundle/"source.py").is_file())
            self.assertFalse((bundle/"model.png").exists())
            self.assertFalse((site/"content/examples/fixture").exists())

    def test_no_evidence_does_not_create_a_fake_preview_or_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            owner = root/"examples/box"
            owner.mkdir(parents=True)
            (owner/"model.yml").write_text("title: Box\npurpose: example\n")
            (owner/"ci.yml").write_text("id: box\nbuilder: builder-cadquery\nsource: model.py\n")
            (owner/"model.py").touch()
            prepare_examples(root, root/"site", None)
            bundle = root/"site/content/examples/box"
            self.assertEqual(json.loads((bundle/"index.md").read_text())["params"]["result"]["status"], "unavailable")
            self.assertFalse((bundle/"model.png").exists())
