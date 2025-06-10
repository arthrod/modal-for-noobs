"""Unit tests for ModalDeployer async functionality."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from modal_for_noobs.modal_deploy import ModalDeployer


@pytest.mark.asyncio
class TestModalDeployer:
    """Test suite for ModalDeployer."""

    @pytest.fixture
    def app_file(self, tmp_path):
        """Create a temporary app file."""
        app_file = tmp_path / "test_app.py"
        app_file.write_text("""
import gradio as gr

def greet(name):
    return f"Hello {name}!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
""")
        return app_file

    @pytest.fixture
    def deployer(self, app_file):
        """Create a ModalDeployer instance."""
        return ModalDeployer(app_file, mode="minimum")

    async def test_check_modal_auth_async_with_env_vars(self, deployer):
        """Test modal auth check with environment variables."""
        with patch.dict("os.environ", {"MODAL_TOKEN_ID": "test", "MODAL_TOKEN_SECRET": "secret"}):
            result = await deployer.check_modal_auth_async()
            assert result is True

    async def test_check_modal_auth_async_with_config_file(self, deployer):
        """Test modal auth check with config file."""
        with patch("pathlib.Path.exists", return_value=True):
            result = await deployer.check_modal_auth_async()
            assert result is True

    async def test_check_modal_auth_async_no_auth(self, deployer):
        """Test modal auth check with no authentication."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                result = await deployer.check_modal_auth_async()
                assert result is False

    async def test_setup_modal_auth_async_success(self, deployer):
        """Test successful modal auth setup."""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"Success", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await deployer.setup_modal_auth_async()
            assert result is True

    async def test_setup_modal_auth_async_failure(self, deployer):
        """Test failed modal auth setup."""
        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"Error"))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await deployer.setup_modal_auth_async()
            assert result is False

    async def test_setup_modal_auth_async_file_not_found(self, deployer):
        """Test modal auth setup when modal CLI is not found."""
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
            result = await deployer.setup_modal_auth_async()
            assert result is False

    def test_get_image_config(self, deployer):
        """Test image configuration generation."""
        packages = ["gradio", "fastapi", "uvicorn"]
        config = deployer._get_image_config("minimum", packages)

        assert "modal.Image.debian_slim" in config
        assert 'python_version="3.11"' in config
        assert "gradio" in config
        assert "fastapi" in config
        assert "uvicorn" in config

    async def test_create_modal_deployment_async_minimum(self, deployer, app_file):
        """Test creation of minimum deployment file."""
        deployment_file = await deployer.create_modal_deployment_async(app_file, deployment_mode="minimum")

        assert deployment_file.exists()
        assert deployment_file.name == "modal_test_app.py"

        content = deployment_file.read_text()
        assert "modal.App" in content
        assert "gradio" in content
        assert "gpu=" not in content

    async def test_create_modal_deployment_async_optimized(self, deployer, app_file):
        """Test creation of optimized deployment file with GPU."""
        deployment_file = await deployer.create_modal_deployment_async(app_file, deployment_mode="optimized")

        content = deployment_file.read_text()
        assert 'gpu="any"' in content

    async def test_create_modal_deployment_async_with_requirements(self, deployer, app_file, tmp_path):
        """Test deployment with custom requirements.txt."""
        requirements_file = tmp_path / "requirements.txt"
        requirements_file.write_text("""
# Custom packages
numpy==1.21.0
pandas>=1.3.0
scikit-learn
""")

        deployment_file = await deployer.create_modal_deployment_async(
            app_file, deployment_mode="minimum", requirements_path=requirements_file
        )

        content = deployment_file.read_text()
        assert "numpy" in content
        assert "pandas" in content
        assert "scikit-learn" in content

    async def test_deploy_to_modal_async_success(self, deployer, tmp_path):
        """Test successful deployment to Modal."""
        deployment_file = tmp_path / "test_deployment.py"
        deployment_file.write_text("# Test deployment")

        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"Deployment successful\nhttps://test-app.modal.run\n", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            url = await deployer.deploy_to_modal_async(deployment_file)
            assert url == "https://test-app.modal.run"

    async def test_deploy_to_modal_async_failure(self, deployer, tmp_path):
        """Test failed deployment to Modal."""
        deployment_file = tmp_path / "test_deployment.py"
        deployment_file.write_text("# Test deployment")

        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"Deployment failed"))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            url = await deployer.deploy_to_modal_async(deployment_file)
            assert url is None

    async def test_deploy_full_workflow(self, deployer):
        """Test the full deployment workflow."""
        # Mock auth check to return True
        deployer.check_modal_auth_async = AsyncMock(return_value=True)

        # Mock deployment creation
        mock_deployment_file = Mock(spec=Path)
        deployer.create_modal_deployment_async = AsyncMock(return_value=mock_deployment_file)

        # Mock deployment to Modal
        deployer.deploy_to_modal_async = AsyncMock(return_value="https://test-app.modal.run")

        url = await deployer.deploy()

        assert url == "https://test-app.modal.run"
        deployer.check_modal_auth_async.assert_called_once()
        deployer.create_modal_deployment_async.assert_called_once()
        deployer.deploy_to_modal_async.assert_called_once_with(mock_deployment_file)

    async def test_deploy_with_auth_setup(self, deployer):
        """Test deployment when auth setup is needed."""
        # Mock auth check to return False initially
        deployer.check_modal_auth_async = AsyncMock(return_value=False)
        deployer.setup_modal_auth_async = AsyncMock(return_value=True)

        # Mock deployment creation and deployment
        mock_deployment_file = Mock(spec=Path)
        deployer.create_modal_deployment_async = AsyncMock(return_value=mock_deployment_file)
        deployer.deploy_to_modal_async = AsyncMock(return_value="https://test-app.modal.run")

        url = await deployer.deploy()

        assert url == "https://test-app.modal.run"
        deployer.check_modal_auth_async.assert_called_once()
        deployer.setup_modal_auth_async.assert_called_once()

    async def test_deploy_auth_setup_failure(self, deployer):
        """Test deployment when auth setup fails."""
        deployer.check_modal_auth_async = AsyncMock(return_value=False)
        deployer.setup_modal_auth_async = AsyncMock(return_value=False)

        with pytest.raises(Exception, match="Failed to setup Modal authentication"):
            await deployer.deploy()

    async def test_deploy_deployment_failure(self, deployer):
        """Test deployment when deployment to Modal fails."""
        deployer.check_modal_auth_async = AsyncMock(return_value=True)

        mock_deployment_file = Mock(spec=Path)
        deployer.create_modal_deployment_async = AsyncMock(return_value=mock_deployment_file)
        deployer.deploy_to_modal_async = AsyncMock(return_value=None)

        with pytest.raises(Exception, match="Failed to get deployment URL"):
            await deployer.deploy()
