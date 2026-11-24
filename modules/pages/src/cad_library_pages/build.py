"""Build the library site without executing CAD or library code."""
import argparse
from pathlib import Path
import subprocess

def build(*, source_root: Path, destination: Path, base_url: str):
    source = source_root.resolve() / "site"
    destination = destination.resolve()
    subprocess.run(["hugo", "--source", str(source), "--destination", str(destination), "--baseURL", base_url, "--minify"], check=True)
    if not (destination / "index.html").is_file():
        raise RuntimeError(f"Hugo did not produce index.html: {destination}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()
    build(source_root=args.source_root, destination=args.destination, base_url=args.base_url)

if __name__ == "__main__":
    main()
