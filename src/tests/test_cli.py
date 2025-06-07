"""Tests for the Modal CLI functionality."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from modal_for_noobs.cli import app
from modal_for_noobs.modal_deploy import ModalDeployer


@pytest.fixture
def runner():
    """Test runner fixture."""
    return CliRunner()


@pytest.fixture
def sample_gradio_app(tmp_path):
    """Create a sample Gradio app for testing."""
    app_content = '''
import gradio as gr

def greet(name):
    return f"Hello {name}!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

if __name__ == "__main__":
    demo.launch()
'''
    app_file = tmp_path / "test_app.py"
    app_file.write_text(app_content)
    return app_file


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Deploy Gradio apps to Modal" in result.stdout


def test_config_info_command(runner):
    """Test config info command."""
    result = runner.invoke(app, ["config-info"])
    assert result.exit_code == 0
    assert "Current Configuration" in result.stdout


@pytest.mark.asyncio
async def test_modal_deployer_auth_check():
    """Test Modal authentication check."""
    deployer = ModalDeployer()
    
    with patch.dict("os.environ", {"MODAL_TOKEN_ID": "test", "MODAL_TOKEN_SECRET": "test"}):
        assert await deployer.check_modal_auth_async() is True


@pytest.mark.asyncio
async def test_create_deployment_file(sample_gradio_app):
    """Test deployment file creation."""
    deployer = ModalDeployer()
    
    deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "minimum")
    
    assert deployment_file.exists()
    assert deployment_file.name == f"modal_{sample_gradio_app.stem}.py"
    
    content = deployment_file.read_text()
    assert "modal.App" in content
    assert "deploy_gradio" in content
    assert "gradio>=4.0.0" in content


def test_deploy_dry_run(runner, sample_gradio_app):
    """Test deploy command with dry run."""
    result = runner.invoke(app, ["deploy", str(sample_gradio_app), "--dry-run"])
    assert result.exit_code == 0


def test_time_to_get_serious_help(runner):
    """Test time-to-get-serious command help."""
    result = runner.invoke(app, ["time-to-get-serious", "--help"])
    assert result.exit_code == 0
    assert "Migrate HuggingFace Spaces" in result.stdout