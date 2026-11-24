"""Execute internal module and selected model-owner tests directly from source."""
import os
import subprocess
import sys
import tomllib


def selected_dependencies(modules):
    dependencies = []
    for module in modules:
        with (module.root / "pyproject.toml").open("rb") as stream:
            project = tomllib.load(stream)["project"]
        dependencies.extend(project.get("dependencies", []))
    return tuple(dict.fromkeys(dependencies))


def install_dependencies(modules):
    dependencies = selected_dependencies(modules)
    if dependencies:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                *dependencies,
            ],
            check=True,
        )


def execute(modules):
    install_dependencies(modules)
    for module in modules:
        env = dict(os.environ)
        source = str((module.root / "src").resolve())
        previous = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = source + (
            os.pathsep + previous if previous else ""
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(module.root / "tests"),
                "-v",
            ],
            env=env,
            check=True,
        )


def execute_model_tests(models, library):
    """Run optional owner-local source/compiler contract tests.

    Model tests intentionally run on the host from source. They do not build CAD
    artifacts and do not install reference CAD engines.
    """
    selected = tuple(
        model for model in models
        if (model.root / "tests").is_dir()
    )
    if not selected:
        return

    if any(model.needs_cadlib for model in selected):
        install_dependencies((library,))

    library_source = str((library.root / "src").resolve())
    for model in selected:
        env = dict(os.environ)
        paths = [library_source, str(model.root.resolve())]
        previous = env.get("PYTHONPATH", "")
        if previous:
            paths.append(previous)
        env["PYTHONPATH"] = os.pathsep.join(paths)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(model.root / "tests"),
                "-v",
            ],
            env=env,
            check=True,
        )
