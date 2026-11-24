from pathlib import Path
import json
import tempfile
import unittest
from cad_library_pages.verify import verify, SiteVerificationError


class VerifyTests(unittest.TestCase):
    def _fixture(self, root):
        owner = root/"examples/box"
        owner.mkdir(parents=True)
        (owner/"model.yml").write_text("title: Box\npurpose: example\n")
        (owner/"ci.yml").write_text("id: box\nbuilder: builder-cadquery\n")
        evidence = root/"build/examples/box"
        evidence.mkdir(parents=True)
        (evidence/"result.json").write_text(json.dumps({"status":"pass","verification_status":"pass"}))
        (evidence/"source.json").write_text(json.dumps({"source_sha":"abc123"}))
        (evidence/"model.stl").write_text("stl")
        site = root/"site"
        (site/"examples/box").mkdir(parents=True)
        (site/"index.html").write_text("home")
        (site/"examples/index.html").write_text("catalogue")
        (site/"examples/box/index.html").write_text("Box builder-cadquery pass abc123")
        for name in ("model.stl","result.json","verification.json"):
            (site/"examples/box"/name).write_text("x")
        return site, root/"build"

    def test_accepts_matching_public_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            site, build=self._fixture(root)
            verify(root, site, build)

    def test_rejects_published_verification_only_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            site, build=self._fixture(root)
            fixture=root/"examples/fixture"
            fixture.mkdir()
            (fixture/"model.yml").write_text("title: Fixture\npurpose: verification\n")
            (fixture/"ci.yml").write_text("id: fixture\nbuilder: builder-cadquery\n")
            (site/"examples/fixture").mkdir()
            with self.assertRaises(SiteVerificationError):
                verify(root, site, build)
