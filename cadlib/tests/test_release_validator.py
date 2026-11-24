import importlib.util
from pathlib import Path
import tempfile
import unittest


def load_validator():
    path = Path("cadlib/release.py").resolve()
    spec = importlib.util.spec_from_file_location("cadlib_release_validator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReleaseValidatorTests(unittest.TestCase):
    def test_template_package_version_and_notes(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            notes = Path(tmp) / "notes.md"
            name = validator.validate("0.0.0", "a" * 40, notes)
            self.assertEqual(name, "cadlib-template")
            text = notes.read_text(encoding="utf-8")
            self.assertIn("cadlib-template 0.0.0", text)
            self.assertIn("a" * 40, text)

    def test_rejects_package_version_mismatch(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(SystemExit, "package version mismatch"):
                validator.validate("1.0.0", "a" * 40, Path(tmp) / "notes.md")


if __name__ == "__main__":
    unittest.main()
