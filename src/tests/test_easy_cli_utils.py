"""Unit tests for easy_cli_utils module."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from modal_for_noobs.utils.easy_cli_utils import (
    check_modal_auth,
    create_modal_deployment,
    setup_modal_auth,
    setup_modal_auth_async,
)


class TestModalAuth:
    """Test suite for Modal authentication functions."""

    def test_check_modal_auth_with_env_vars(self):
        """Test auth check with environment variables."""
        with patch.dict("os.environ", {"MODAL_TOKEN_ID": "test", "MODAL_TOKEN_SECRET": "secret"}):
            assert check_modal_auth() is True

    def test_check_modal_auth_with_config_file(self):
        """Test auth check with config file."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch.dict("os.environ", {}, clear=True):
                assert check_modal_auth() is True

    def test_check_modal_auth_no_auth(self):
        """Test auth check with no authentication."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                assert check_modal_auth() is False

    def test_check_modal_auth_exception(self):
        """Test auth check with exception."""
        with patch("os.getenv", side_effect=Exception("Test error")):
            assert check_modal_auth() is False

    def test_setup_modal_auth_success(self):
        """Test successful modal auth setup."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Setup successful"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            assert setup_modal_auth() is True

    def test_setup_modal_auth_failure(self):
        """Test failed modal auth setup."""
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "modal")):
            assert setup_modal_auth() is False

    def test_setup_modal_auth_file_not_found(self):
        """Test modal auth setup when modal CLI is not found."""
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            assert setup_modal_auth() is False

    def test_setup_modal_auth_unexpected_error(self):
        """Test modal auth setup with unexpected error."""
        with patch("subprocess.run", side_effect=Exception("Unexpected")):
            assert setup_modal_auth() is False

    @pytest.mark.asyncio
    async def test_setup_modal_auth_async_success(self):
        """Test successful async modal auth setup."""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"Success", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            assert await setup_modal_auth_async() is True

    @pytest.mark.asyncio
    async def test_setup_modal_auth_async_failure(self):
        """Test failed async modal auth setup."""
        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"Error"))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            assert await setup_modal_auth_async() is False

    @pytest.mark.asyncio
    async def test_setup_modal_auth_async_file_not_found(self):
        """Test async modal auth setup when modal CLI is not found."""
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
            assert await setup_modal_auth_async() is False

    @pytest.mark.asyncio
    async def test_setup_modal_auth_async_subprocess_error(self):
        """Test async modal auth setup with subprocess error."""
        with patch("asyncio.create_subprocess_exec", side_effect=OSError()):
            assert await setup_modal_auth_async() is False


class TestCreateModalDeployment:
    """Test suite for deployment file creation."""

    def test_create_modal_deployment_minimum(self, tmp_path):
        """Test creation of minimum deployment file."""
        app_file = tmp_path / "test_app.py"
        app_file.write_text("import gradio as gr\ndemo = gr.Interface(lambda x: x, 'text', 'text')")

        deployment_file = create_modal_deployment(app_file, deployment_mode="minimum")

        assert deployment_file.exists()
        assert deployment_file.name == "modal_test_app.py"

        content = deployment_file.read_text()
        assert "modal.App" in content
        assert "gradio>=4.0.0" in content
        assert "gpu=" not in content
        assert "import test_app as target_module" in content

    def test_create_modal_deployment_optimized(self, tmp_path):
        """Test creation of optimized deployment file."""
        app_file = tmp_path / "test_app.py"
        app_file.write_text("import gradio as gr\ndemo = gr.Interface(lambda x: x, 'text', 'text')")

        deployment_file = create_modal_deployment(app_file, deployment_mode="optimized")

        content = deployment_file.read_text()
        assert "gpu='any'" in content
        assert "torch>=2.0.0" in content
        assert "transformers>=4.20.0" in content

    def test_create_modal_deployment_with_path_string(self, tmp_path):
        """Test deployment creation with string path."""
        app_file = tmp_path / "test_app.py"
        app_file.write_text("import gradio as gr\ndemo = gr.Interface(lambda x: x, 'text', 'text')")

        deployment_file = create_modal_deployment(str(app_file), deployment_mode="minimum")

        assert deployment_file.exists()
        assert isinstance(deployment_file, Path)

    def test_deployment_template_structure(self, tmp_path):
        """Test the structure of the generated deployment template."""
        app_file = tmp_path / "test_app.py"
        app_file.write_text("import gradio as gr\ndemo = gr.Interface(lambda x: x, 'text', 'text')")

        deployment_file = create_modal_deployment(app_file)
        content = deployment_file.read_text()

        # Check for required imports
        assert "import modal" in content
        assert "from fastapi import FastAPI" in content
        assert "import gradio as gr" in content
        assert "from gradio.routes import mount_gradio_app" in content

        # Check for Modal app configuration
        assert "@app.function" in content
        assert "@modal.concurrent(max_inputs=100)" in content
        assert "@modal.asgi_app()" in content

        # Check for Gradio interface detection logic
        assert "for attr in ['demo', 'app', 'interface', 'iface']:" in content
        assert "if hasattr(target_module, attr):" in content
        assert "demo.queue(max_size=10)" in content

        # Check for FastAPI integration
        assert "fastapi_app = FastAPI" in content
        assert "mount_gradio_app(fastapi_app, demo, path='/')" in content


# Add this import at the top of the file
import subprocess
