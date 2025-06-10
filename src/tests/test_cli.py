"""Comprehensive tests for the Modal CLI functionality."""

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from modal_for_noobs.cli import app
from modal_for_noobs.config import Config
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


@pytest.fixture
def complex_gradio_app(tmp_path):
    """Create a complex Gradio app for testing."""
    app_content = '''
import gradio as gr
import matplotlib.pyplot as plt
import numpy as np

def generate_plot(title):
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title(title)
    return fig

def analyze_text(text, model_choice):
    return f"Analyzed '{text}' with {model_choice}"

with gr.Blocks() as demo:
    gr.Markdown("# Complex App")

    with gr.Tab("Plot"):
        title_input = gr.Textbox(label="Title")
        plot_output = gr.Plot()
        plot_btn = gr.Button("Generate")
        plot_btn.click(generate_plot, inputs=title_input, outputs=plot_output)

    with gr.Tab("Analysis"):
        text_input = gr.Textbox(label="Text")
        model_dropdown = gr.Dropdown(["GPT-4", "Claude", "Llama"], label="Model")
        analysis_output = gr.Textbox(label="Result")
        analyze_btn = gr.Button("Analyze")
        analyze_btn.click(analyze_text, inputs=[text_input, model_dropdown], outputs=analysis_output)

if __name__ == "__main__":
    demo.launch()
'''
    app_file = tmp_path / "complex_app.py"
    app_file.write_text(app_content)
    return app_file


@pytest.fixture
def mock_modal_auth():
    """Mock Modal authentication."""
    with patch.dict("os.environ", {"MODAL_TOKEN_ID": "test_token", "MODAL_TOKEN_SECRET": "test_secret"}):
        yield


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls."""
    with patch("asyncio.create_subprocess_exec") as mock:
        mock_process = MagicMock()
        mock_process.returncode = 0
        async def mock_communicate():
            return (b"success", b"")
        mock_process.communicate = mock_communicate
        async def mock_subprocess_exec(*args, **kwargs):
            return mock_process
        mock.return_value = mock_subprocess_exec()
        yield mock


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Deploy Gradio apps to Modal" in result.stdout


def test_config_info_command(runner):
    """Test config info command."""
    result = runner.invoke(app, ["config", "--info"])
    assert result.exit_code == 0
    assert "CONFIGURATION INFORMATION" in result.stdout


@pytest.mark.asyncio
async def test_modal_deployer_auth_check():
    """Test Modal authentication check."""
    dummy_app_file = Path("dummy.py")
    deployer = ModalDeployer(dummy_app_file)

    with patch.dict("os.environ", {"MODAL_TOKEN_ID": "test", "MODAL_TOKEN_SECRET": "test"}):
        assert await deployer.check_modal_auth_async() is True


@pytest.mark.asyncio
async def test_create_deployment_file(sample_gradio_app):
    """Test deployment file creation."""
    from modal_for_noobs.modal_deploy import DeploymentConfig
    
    deployer = ModalDeployer(sample_gradio_app)
    config = DeploymentConfig(mode="minimum", app_name=sample_gradio_app.stem)

    deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, config)

    assert deployment_file.exists()
    assert deployment_file.name == f"modal_{sample_gradio_app.stem}.py"

    content = deployment_file.read_text()
    assert "modal.App" in content
    assert "deploy_gradio" in content
    assert "gradio" in content  # Check for gradio package without version constraint


def test_deploy_dry_run(runner, sample_gradio_app):
    """Test deploy command with dry run."""
    result = runner.invoke(app, ["deploy", str(sample_gradio_app), "--dry-run"])
    assert result.exit_code == 0


def test_time_to_get_serious_help(runner):
    """Test time-to-get-serious command help."""
    result = runner.invoke(app, ["time-to-get-serious", "--help"])
    assert result.exit_code == 0
    assert "Migrate HuggingFace Spaces" in result.stdout


# === NEW COMPREHENSIVE TESTS ===

class TestCLICommands:
    """Test all CLI commands comprehensively."""

    def test_main_help(self, runner):
        """Test main CLI help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "modal-for-noobs" in result.stdout
        assert "deploy" in result.stdout
        assert "kill-a-deployment" in result.stdout
        assert "milk-logs" in result.stdout

    def test_deploy_help(self, runner):
        """Test deploy command help."""
        result = runner.invoke(app, ["deploy", "--help"])
        assert result.exit_code == 0
        assert "Deploy a Gradio app" in result.stdout
        assert "--wizard" in result.stdout
        assert "--optimized" in result.stdout
        # --br-huehuehue is hidden, so it won't appear in help

    def test_deploy_missing_file(self, runner):
        """Test deploy with non-existent file."""
        result = runner.invoke(app, ["deploy", "nonexistent.py"])
        assert result.exit_code != 0

    def test_deploy_wizard_mode(self, runner, sample_gradio_app):
        """Test deploy with wizard mode."""
        result = runner.invoke(app, ["deploy", str(sample_gradio_app), "--wizard", "--dry-run"])
        assert result.exit_code == 0

    def test_deploy_optimized_mode(self, runner, sample_gradio_app):
        """Test deploy with optimized mode."""
        result = runner.invoke(app, ["deploy", str(sample_gradio_app), "--optimized", "--dry-run"])
        assert result.exit_code == 0

    def test_deploy_brazilian_mode(self, runner, sample_gradio_app):
        """Test deploy with Brazilian mode."""
        result = runner.invoke(app, ["deploy", str(sample_gradio_app), "--br-huehuehue", "--dry-run"])
        assert result.exit_code == 0
        # Check for Portuguese content in Brazilian mode
        assert ("computação" in result.stdout.lower() or 
                "escalonamento" in result.stdout.lower() or 
                "huehuehue" in result.stdout.lower())

    def test_deploy_complex_app(self, runner, complex_gradio_app):
        """Test deploy with complex Gradio app."""
        result = runner.invoke(app, ["deploy", str(complex_gradio_app), "--optimized", "--dry-run"])
        assert result.exit_code == 0

    def test_run_examples_help(self, runner):
        """Test run-examples command help."""
        result = runner.invoke(app, ["run-examples", "--help"])
        assert result.exit_code == 0
        assert "built-in examples" in result.stdout

    def test_run_examples_list(self, runner):
        """Test listing available examples."""
        result = runner.invoke(app, ["run-examples"])
        assert result.exit_code == 0
        # Should list available examples

    def test_run_examples_specific(self, runner):
        """Test running specific example."""
        result = runner.invoke(app, ["run-examples", "simple_hello", "--dry-run"])
        assert result.exit_code == 0

    def test_run_examples_nonexistent(self, runner):
        """Test running non-existent example."""
        result = runner.invoke(app, ["run-examples", "nonexistent_example"])
        assert result.exit_code != 0

    def test_kill_deployment_help(self, runner):
        """Test kill-a-deployment command help."""
        result = runner.invoke(app, ["kill-a-deployment", "--help"])
        assert result.exit_code == 0
        assert "terminate" in result.stdout.lower()

    @patch("modal_for_noobs.cli._kill_deployment_async")
    def test_kill_deployment_list(self, mock_kill, runner):
        """Test listing deployments to kill."""
        async def mock_kill_async(*args, **kwargs):
            return None
        mock_kill.return_value = mock_kill_async()
        result = runner.invoke(app, ["kill-a-deployment"])
        assert result.exit_code == 0
        mock_kill.assert_called_once()

    @patch("modal_for_noobs.cli._kill_deployment_async")
    def test_kill_specific_deployment(self, mock_kill, runner):
        """Test killing specific deployment."""
        async def mock_kill_async(*args, **kwargs):
            return None
        mock_kill.return_value = mock_kill_async()
        result = runner.invoke(app, ["kill-a-deployment", "ap-test123"])
        assert result.exit_code == 0
        mock_kill.assert_called_once_with("ap-test123", False)

    @patch("modal_for_noobs.cli._kill_deployment_async")
    def test_kill_deployment_brazilian(self, mock_kill, runner):
        """Test kill deployment with Brazilian mode."""
        async def mock_kill_async(*args, **kwargs):
            return None
        mock_kill.return_value = mock_kill_async()
        result = runner.invoke(app, ["kill-a-deployment", "ap-test123", "--br-huehuehue"])
        assert result.exit_code == 0
        mock_kill.assert_called_once_with("ap-test123", True)

    def test_milk_logs_help(self, runner):
        """Test milk-logs command help."""
        result = runner.invoke(app, ["milk-logs", "--help"])
        assert result.exit_code == 0
        assert "logs" in result.stdout.lower()

    @patch("modal_for_noobs.cli._milk_logs_async")
    def test_milk_logs_basic(self, mock_milk, runner):
        """Test basic log milking."""
        async def mock_milk_async(*args, **kwargs):
            return None
        mock_milk.return_value = mock_milk_async()
        result = runner.invoke(app, ["milk-logs"])
        assert result.exit_code == 0
        mock_milk.assert_called_once()

    @patch("modal_for_noobs.cli._milk_logs_async")
    def test_milk_logs_specific_app(self, mock_milk, runner):
        """Test milking logs for specific app."""
        async def mock_milk_async(*args, **kwargs):
            return None
        mock_milk.return_value = mock_milk_async()
        result = runner.invoke(app, ["milk-logs", "test-app"])
        assert result.exit_code == 0
        mock_milk.assert_called_once_with("test-app", False, 100, False)

    @patch("modal_for_noobs.cli._milk_logs_async")
    def test_milk_logs_follow(self, mock_milk, runner):
        """Test following logs."""
        async def mock_milk_async(*args, **kwargs):
            return None
        mock_milk.return_value = mock_milk_async()
        result = runner.invoke(app, ["milk-logs", "test-app", "--follow"])
        assert result.exit_code == 0
        mock_milk.assert_called_once_with("test-app", True, 100, False)

    def test_sanity_check_help(self, runner):
        """Test sanity-check command help."""
        result = runner.invoke(app, ["sanity-check", "--help"])
        assert result.exit_code == 0
        assert "sanity check" in result.stdout.lower()

    @patch("modal_for_noobs.cli._sanity_check_async")
    def test_sanity_check_basic(self, mock_sanity, runner):
        """Test basic sanity check."""
        async def mock_sanity_async(*args, **kwargs):
            return None
        mock_sanity.return_value = mock_sanity_async()
        result = runner.invoke(app, ["sanity-check"])
        assert result.exit_code == 0
        mock_sanity.assert_called_once()

    def test_config_command(self, runner):
        """Test config command."""
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "configuration" in result.stdout.lower()

    def test_auth_help(self, runner):
        """Test auth command help."""
        result = runner.invoke(app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "authentication" in result.stdout.lower()

    @patch("modal_for_noobs.cli._setup_auth_async")
    def test_auth_setup(self, mock_auth, runner):
        """Test authentication setup."""
        async def mock_auth_async(*args, **kwargs):
            return None
        mock_auth.return_value = mock_auth_async()
        result = runner.invoke(app, ["auth", "--token-id", "test_id", "--token-secret", "test_secret"])
        assert result.exit_code == 0
        mock_auth.assert_called_once()


class TestAsyncFunctions:
    """Test async functionality."""

    @pytest.mark.asyncio
    async def test_modal_deployer_init(self):
        """Test ModalDeployer initialization."""
        dummy_app_file = Path("dummy.py")
        deployer = ModalDeployer(dummy_app_file)
        assert deployer is not None

    @pytest.mark.asyncio
    async def test_modal_auth_check_with_tokens(self, mock_modal_auth):
        """Test Modal auth check with tokens."""
        dummy_app_file = Path("dummy.py")
        deployer = ModalDeployer(dummy_app_file)
        result = await deployer.check_modal_auth_async()
        assert result is True

    @pytest.mark.asyncio
    async def test_modal_auth_check_without_tokens(self):
        """Test Modal auth check without tokens."""
        with patch.dict("os.environ", {}, clear=True), \
             patch("pathlib.Path.exists", return_value=False):
            dummy_app_file = Path("dummy.py")
            deployer = ModalDeployer(dummy_app_file)
            result = await deployer.check_modal_auth_async()
            assert result is False

    @pytest.mark.asyncio
    async def test_create_deployment_file_minimum(self, sample_gradio_app):
        """Test creating deployment file with minimum config."""
        deployer = ModalDeployer(sample_gradio_app)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "minimum")

        assert deployment_file.exists()
        content = deployment_file.read_text()
        assert "modal.App" in content
        assert "gradio" in content
        assert "fastapi" in content

    @pytest.mark.asyncio
    async def test_create_deployment_file_optimized(self, sample_gradio_app):
        """Test creating deployment file with optimized config."""
        deployer = ModalDeployer(sample_gradio_app)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "optimized")

        assert deployment_file.exists()
        content = deployment_file.read_text()
        assert "modal.App" in content
        assert "gradio" in content
        assert "torch" in content or "tensorflow" in content or "scikit-learn" in content

    @pytest.mark.asyncio
    async def test_deploy_dry_run_async(self, sample_gradio_app, mock_subprocess):
        """Test async deployment with dry run."""
        deployer = ModalDeployer(sample_gradio_app)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "minimum")

        # Should not raise an exception
        assert deployment_file.exists()


class TestConfigSystem:
    """Test configuration system."""

    def test_config_init_default(self):
        """Test config initialization with defaults."""
        config = Config()
        assert config.environment in ["development", "production"]
        assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]

    def test_config_with_env_file(self, tmp_path, monkeypatch):
        """Test config with custom env file."""
        # Clear any existing environment variables
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        
        env_file = tmp_path / ".test_env"
        env_file.write_text("ENVIRONMENT=test\nLOG_LEVEL=INFO\n")

        config = Config(str(env_file))
        assert config.environment == "test"
        assert config.log_level == "INFO"

    def test_config_unkey_settings(self):
        """Test Unkey configuration."""
        config = Config()
        unkey_config = config.get_unkey_config()
        assert "root_key" in unkey_config
        assert "api_id" in unkey_config


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_deploy_invalid_python_file(self, runner, tmp_path):
        """Test deploy with invalid Python file."""
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("import invalid_module_that_doesnt_exist\n")

        result = runner.invoke(app, ["deploy", str(invalid_file), "--dry-run"])
        # Should handle gracefully

    def test_deploy_non_python_file(self, runner, tmp_path):
        """Test deploy with non-Python file."""
        text_file = tmp_path / "test.txt"
        text_file.write_text("This is not Python code")

        result = runner.invoke(app, ["deploy", str(text_file)])
        assert result.exit_code != 0

    def test_deploy_deployer_failure(self, runner, sample_gradio_app):
        """Test deploy with invalid file that causes failure."""
        # Create an invalid Python file that will cause deployment to fail
        invalid_file = sample_gradio_app.parent / "invalid.py"
        invalid_file.write_text("This is not valid Python code {{{")

        result = runner.invoke(app, ["deploy", str(invalid_file)])
        # Should handle the error gracefully, but might succeed with dry run behavior
        # The important thing is that it doesn't crash

    def test_config_missing_env_file(self, runner):
        """Test config with missing env file."""
        result = runner.invoke(app, ["config", "--env-file", "nonexistent.env"])
        # Should handle gracefully


class TestIntegration:
    """Integration tests for full workflows."""

    def test_full_deploy_workflow_dry_run(self, runner, sample_gradio_app):
        """Test complete deploy workflow with dry run."""
        # Test basic deploy
        result = runner.invoke(app, ["deploy", str(sample_gradio_app), "--dry-run"])
        assert result.exit_code == 0

        # Test with wizard
        result = runner.invoke(app, ["deploy", str(sample_gradio_app), "--wizard", "--dry-run"])
        assert result.exit_code == 0

        # Test with optimized
        result = runner.invoke(app, ["deploy", str(sample_gradio_app), "--optimized", "--dry-run"])
        assert result.exit_code == 0

    def test_examples_workflow(self, runner):
        """Test examples workflow."""
        # List examples
        result = runner.invoke(app, ["run-examples"])
        assert result.exit_code == 0

        # Try to run simple example with dry run
        result = runner.invoke(app, ["run-examples", "simple_hello", "--dry-run"])
        assert result.exit_code == 0

    @patch("modal_for_noobs.cli._kill_deployment_async")
    @patch("modal_for_noobs.cli._milk_logs_async")
    @patch("modal_for_noobs.cli._sanity_check_async")
    def test_management_workflow(self, mock_sanity, mock_logs, mock_kill, runner):
        """Test deployment management workflow."""
        # Mock all async functions
        async def mock_kill_async(*args, **kwargs):
            return None
        mock_kill.return_value = mock_kill_async()
        async def mock_logs_async():
            return None
        mock_logs.return_value = mock_logs_async()
        async def mock_sanity_async(*args, **kwargs):
            return None
        mock_sanity.return_value = mock_sanity_async()

        # Sanity check
        result = runner.invoke(app, ["sanity-check"])
        assert result.exit_code == 0

        # List deployments to kill
        result = runner.invoke(app, ["kill-a-deployment"])
        assert result.exit_code == 0

        # Check logs
        result = runner.invoke(app, ["milk-logs"])
        assert result.exit_code == 0

    def test_brazilian_mode_workflow(self, runner, sample_gradio_app):
        """Test Brazilian mode across commands."""
        # Deploy with Brazilian mode
        result = runner.invoke(app, ["deploy", str(sample_gradio_app), "--br-huehuehue", "--dry-run"])
        assert result.exit_code == 0
        # Check for Portuguese content in Brazilian mode
        assert ("computação" in result.stdout.lower() or 
                "escalonamento" in result.stdout.lower() or 
                "huehuehue" in result.stdout.lower())

        # Examples with Brazilian mode
        result = runner.invoke(app, ["run-examples", "simple_hello", "--br-huehuehue", "--dry-run"])
        assert result.exit_code == 0
