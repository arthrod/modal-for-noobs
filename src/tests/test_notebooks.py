"""Tests for Marimo notebooks."""

import subprocess
import sys
from pathlib import Path


def safe_command(cmd):
    """Safe command execution wrapper."""
    if not isinstance(cmd, list | tuple):
        raise ValueError("Command must be a list or tuple")
    return cmd


def test_notebooks(root_dir):
    """Test that all Marimo notebooks can be executed without errors."""
    # loop over all notebooks
    path = root_dir / "book" / "marimo"

    # List all .py files in the directory using glob
    py_files = list(path.glob("*.py"))

    # Loop over the files and run them
    for py_file in py_files:
        print(f"Running {py_file.name}...")
        result = safe_command.run(subprocess.run, [sys.executable, str(py_file)], capture_output=True, text=True)

        # Print the result of running the Python file
        if result.returncode == 0:
            print(f"{py_file.name} ran successfully.")
            print(f"Output: {result.stdout}")
        else:
            print(f"Error running {py_file.name}:")
            print(f"stderr: {result.stderr}")
