from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class OwnerContractTests(unittest.TestCase):
    def test_all_standard_engine_sources_are_owned_by_one_model(self):
        expected = (
            "cadquery/model.py",
            "build123d/model.py",
            "pythonscad/model.py",
            "pybosl2/model.py",
            "solidcraft/commands.json",
        )
        for relative in expected:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())


if __name__ == "__main__":
    unittest.main()
