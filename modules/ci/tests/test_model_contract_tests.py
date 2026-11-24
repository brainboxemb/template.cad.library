from pathlib import Path
from types import SimpleNamespace
import os
import tempfile
import unittest
from unittest.mock import patch

from cad_library_ci.runner import execute_model_tests


class ModelContractTestRunnerTests(unittest.TestCase):
    def test_runs_only_selected_owner_tests_with_library_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = SimpleNamespace(root=root / "cadlib")
            (library.root / "src").mkdir(parents=True)
            (library.root / "pyproject.toml").write_text(
                '[project]\nname="cadlib"\nversion="0"\n'
            )

            tested = root / "models" / "tested"
            skipped = root / "models" / "skipped"
            (tested / "tests").mkdir(parents=True)
            skipped.mkdir(parents=True)
            model_a = SimpleNamespace(
                id="tested", root=tested, needs_cadlib=True
            )
            model_b = SimpleNamespace(
                id="skipped", root=skipped, needs_cadlib=False
            )

            with patch(
                "cad_library_ci.runner.subprocess.run"
            ) as run:
                execute_model_tests((model_a, model_b), library)

            self.assertEqual(run.call_count, 1)
            command = run.call_args.args[0]
            env = run.call_args.kwargs["env"]
            self.assertEqual(
                command[-3:],
                ["-s", str(tested / "tests"), "-v"],
            )
            pythonpath = env["PYTHONPATH"].split(os.pathsep)
            self.assertEqual(
                pythonpath[:2],
                [
                    str((library.root / "src").resolve()),
                    str(tested.resolve()),
                ],
            )

    def test_no_tests_does_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = SimpleNamespace(root=root / "cadlib")
            model = SimpleNamespace(
                id="box",
                root=root / "models" / "box",
                needs_cadlib=True,
            )
            with patch(
                "cad_library_ci.runner.subprocess.run"
            ) as run:
                execute_model_tests((model,), library)
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
