#!/usr/bin/env python3
"""🚀💚 Publishing script for gradio-modal-deploy 💚🚀
Automates the process of building and publishing to PyPI with uv.

Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨
"""

import subprocess
import sys
from pathlib import Path
from security import safe_command


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    result = safe_command.run(subprocess.run, cmd, shell=False, capture_output=True, text=True, check=False)

    if check and result.returncode != 0:
        sys.exit(1)

    if result.stdout:
        pass

    return result


def check_prerequisites() -> None:
    """Check if all prerequisites are installed."""
    # Check uv
    result = run_command("uv --version", check=False)
    if result.returncode != 0:
        sys.exit(1)

    # Check git
    result = run_command("git --version", check=False)
    if result.returncode != 0:
        sys.exit(1)


def run_tests() -> None:
    """Run the test suite."""
    run_command("uv run pytest")


def run_linting() -> None:
    """Run linting and formatting checks."""
    run_command("uv run ruff check")
    run_command("uv run ruff format --check")


def build_package() -> None:
    """Build the package."""
    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info/")

    # Build with uv
    run_command("uv build")


def publish_to_pypi(test: bool = False) -> None:
    """Publish to PyPI."""
    if test:
        run_command("uv publish --repository testpypi")
    else:
        run_command("uv publish")


def update_version(version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Replace version line
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("version = "):
            lines[i] = f'version = "{version}"'
            break

    pyproject_path.write_text("\n".join(lines))


def create_git_tag(version: str) -> None:
    """Create and push git tag."""
    run_command("git add pyproject.toml")
    run_command(f'git commit -m "Bump version to {version}"')
    run_command(f"git tag v{version}")
    run_command("git push")
    run_command("git push --tags")


def main() -> None:
    """Main publishing workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="Publish gradio-modal-deploy to PyPI")
    parser.add_argument("--version", help="Version to publish (e.g., 0.1.0)")
    parser.add_argument("--test", action="store_true", help="Publish to Test PyPI")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-tag", action="store_true", help="Skip creating git tag")

    args = parser.parse_args()

    # Check prerequisites
    check_prerequisites()

    # Update version if provided
    if args.version:
        update_version(args.version)

    # Run tests unless skipped
    if not args.skip_tests:
        run_tests()
        run_linting()

    # Build package
    build_package()

    # Create git tag unless skipped
    if args.version and not args.skip_tag:
        create_git_tag(args.version)

    # Publish
    publish_to_pypi(test=args.test)

    if args.test:
        pass
    else:
        pass


if __name__ == "__main__":
    main()
