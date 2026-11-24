from pathlib import Path
import unittest
import yaml

class LibraryLayoutTests(unittest.TestCase):
    def test_library_and_verification_starters(self):
        for root, kind in ((Path("cadlib"), "library"), (Path("verification/_template"), "verification")):
            with self.subTest(root=root):
                self.assertEqual(yaml.safe_load((root / "ci.yml").read_text())["kind"], kind)
                self.assertTrue((root / "pyproject.toml").is_file())
                self.assertTrue(any((root / "src").rglob("*.py")))
                self.assertTrue(any((root / "tests").glob("test_*.py")))
        self.assertTrue(Path("examples/README.md").is_file())
