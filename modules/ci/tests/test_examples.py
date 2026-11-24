from pathlib import Path
import unittest
from cad_library_ci.config import load_project
from cad_library_ci.items import discover_modules
from cad_library_ci.examples import discover_examples, select_examples
from cad_library_ci.batch import run_batches
from unittest.mock import patch
import tempfile
import json


class ExampleTests(unittest.TestCase):
    def setUp(self):
        self.repo = Path.cwd()
        self.project = load_project(self.repo)
        self.modules = discover_modules(self.repo, self.project)
        self.examples = discover_examples(self.repo, self.modules)

    def test_discovery_and_dependency_selection(self):
        self.assertEqual([x.id for x in self.examples], ["simple-box"])
        self.assertEqual(len(select_examples(self.examples, explicit=["simple-box"])), 1)
        self.assertEqual(len(select_examples(self.examples, paths=("docs/plan.md",), selected_modules=("verification",))), 1)
        self.assertEqual(len(select_examples(self.examples, paths=("examples/simple-box/cadquery/model.py",))), 1)
        self.assertEqual(select_examples(self.examples, paths=("docs/plan.md",)), ())

    def test_single_docker_invocation_per_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("cad_library_ci.batch.subprocess.run") as run:
                def inspect(command, **kwargs):
                    path = next(x.split(":/manifest.json:ro")[0] for x in command if x.endswith(":/manifest.json:ro"))
                    manifest = json.loads(Path(path).read_text())
                    self.assertEqual(manifest["runtime"], "reference")
                    self.assertEqual(len(manifest["examples"]), 1)
                    self.assertTrue(any("modules/verification/src" in x for x in command))
                    run.return_value.returncode = 0
                    return run.return_value
                run.side_effect = inspect
                run_batches(self.repo, self.project, self.modules, self.examples, Path(tmp))
                run.assert_called_once()
