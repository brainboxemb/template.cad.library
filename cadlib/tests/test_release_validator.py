import importlib.util
from pathlib import Path
import tempfile
import tomllib
import unittest


def load_validator():
    path = Path("cadlib/release.py").resolve()
    spec = importlib.util.spec_from_file_location("cadlib_release_validator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def package_version():
    data = tomllib.loads(
        Path("cadlib/pyproject.toml").read_text(encoding="utf-8")
    )
    return str(data["project"]["version"])


class ReleaseValidatorTests(unittest.TestCase):
    def test_template_package_version_and_notes(self):
        validator = load_validator()
        version = package_version()
        with tempfile.TemporaryDirectory() as tmp:
            notes = Path(tmp) / "notes.md"
            name = validator.validate(version, "a" * 40, notes)
            self.assertEqual(name, "cadlib-template")
            text = notes.read_text(encoding="utf-8")
            self.assertIn(f"cadlib-template {version}", text)
            self.assertIn("a" * 40, text)

    def test_rejects_package_version_mismatch(self):
        validator = load_validator()
        version = package_version()
        mismatch = "999.0.0" if version != "999.0.0" else "998.0.0"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(SystemExit, "package version mismatch"):
                validator.validate(mismatch, "a" * 40, Path(tmp) / "notes.md")


if __name__ == "__main__":
    unittest.main()
