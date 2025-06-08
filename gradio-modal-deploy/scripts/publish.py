#!/usr/bin/env python3
"""
🚀💚 Publishing script for gradio-modal-deploy 💚🚀
Automates the process of building and publishing to PyPI with uv.

Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"🔥 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        sys.exit(1)

    if result.stdout:
        print(result.stdout.strip())

    return result


def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("🔍 Checking prerequisites...")

    # Check uv
    result = run_command("uv --version", check=False)
    if result.returncode != 0:
        print("❌ uv is not installed. Please install it first:")
        print("curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    # Check git
    result = run_command("git --version", check=False)
    if result.returncode != 0:
        print("❌ git is not installed. Please install git first.")
        sys.exit(1)

    print("✅ All prerequisites are installed!")


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    run_command("uv run pytest")
    print("✅ All tests passed!")


def run_linting():
    """Run linting and formatting checks."""
    print("🎨 Running linting...")
    run_command("uv run ruff check")
    run_command("uv run ruff format --check")
    print("✅ Linting passed!")


def build_package():
    """Build the package."""
    print("📦 Building package...")

    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info/")

    # Build with uv
    run_command("uv build")

    print("✅ Package built successfully!")


def publish_to_pypi(test: bool = False):
    """Publish to PyPI."""
    repository = "testpypi" if test else "pypi"
    print(f"🚀 Publishing to {'Test PyPI' if test else 'PyPI'}...")

    if test:
        run_command("uv publish --repository testpypi")
    else:
        run_command("uv publish")

    print(f"✅ Published to {'Test PyPI' if test else 'PyPI'} successfully!")


def update_version(version: str):
    """Update version in pyproject.toml."""
    print(f"📝 Updating version to {version}...")

    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Replace version line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('version = '):
            lines[i] = f'version = "{version}"'
            break

    pyproject_path.write_text('\n'.join(lines))
    print(f"✅ Version updated to {version}")


def create_git_tag(version: str):
    """Create and push git tag."""
    print(f"🏷️ Creating git tag v{version}...")

    run_command(f"git add pyproject.toml")
    run_command(f'git commit -m "Bump version to {version}"')
    run_command(f"git tag v{version}")
    run_command("git push")
    run_command("git push --tags")

    print(f"✅ Git tag v{version} created and pushed!")


def main():
    """Main publishing workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="Publish gradio-modal-deploy to PyPI")
    parser.add_argument("--version", help="Version to publish (e.g., 0.1.0)")
    parser.add_argument("--test", action="store_true", help="Publish to Test PyPI")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-tag", action="store_true", help="Skip creating git tag")

    args = parser.parse_args()

    print("🚀💚 GRADIO MODAL DEPLOY PUBLISHING SCRIPT 💚🚀")
    print("=" * 50)

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

    print("\n🎉 Publishing completed successfully!")

    if args.test:
        print("📦 Package published to Test PyPI:")
        print("https://test.pypi.org/project/gradio-modal-deploy/")
        print("\n🧪 To install from Test PyPI:")
        print("uv add --index https://test.pypi.org/simple/ gradio-modal-deploy")
    else:
        print("📦 Package published to PyPI:")
        print("https://pypi.org/project/gradio-modal-deploy/")
        print("\n📦 To install:")
        print("uv add gradio-modal-deploy")

    print("\n💚 Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨")


if __name__ == "__main__":
    main()
