"""Tests for Modal deployment functionality."""

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modal_for_noobs.modal_deploy import DeploymentConfig, ModalDeployer


@pytest.fixture
def sample_gradio_app(tmp_path):
    """Create a sample Gradio app for testing."""
    app_content = """
import gradio as gr

def greet(name):
    return f"Hello {name}!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

if __name__ == "__main__":
    demo.launch()
"""
    app_file = tmp_path / "test_app.py"
    app_file.write_text(app_content)
    return app_file


@pytest.fixture
def sample_app_with_dependencies(tmp_path):
    """Create a sample app with various dependencies."""
    app_content = """
import gradio as gr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch
import transformers

def process_data(file):
    df = pd.read_csv(file)
    return df.head()

def generate_plot():
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    return fig

def ai_analysis(text):
    # Simulate AI processing
    return f"Analysis: {text} (processed with transformers)"

with gr.Blocks() as demo:
    with gr.Tab("Data"):
        file_input = gr.File(label="Upload CSV")
        data_output = gr.Dataframe()
        file_input.upload(process_data, inputs=file_input, outputs=data_output)

    with gr.Tab("Plot"):
        plot_btn = gr.Button("Generate Plot")
        plot_output = gr.Plot()
        plot_btn.click(generate_plot, outputs=plot_output)

    with gr.Tab("AI"):
        text_input = gr.Textbox(label="Text to analyze")
        ai_btn = gr.Button("Analyze")
        ai_output = gr.Textbox(label="Result")
        ai_btn.click(ai_analysis, inputs=text_input, outputs=ai_output)

if __name__ == "__main__":
    demo.launch()
"""
    app_file = tmp_path / "complex_ai_app.py"
    app_file.write_text(app_content)
    return app_file


class TestModalDeployer:
    """Test ModalDeployer class functionality."""

    def test_deployer_initialization(self):
        """Test deployer initializes correctly."""
        dummy_app_file = Path("dummy.py")
        deployer = ModalDeployer(dummy_app_file)
        assert deployer is not None

    @pytest.mark.asyncio
    async def test_check_modal_auth_with_env_vars(self):
        """Test Modal auth check with environment variables."""
        with patch.dict("os.environ", {"MODAL_TOKEN_ID": "test_id", "MODAL_TOKEN_SECRET": "test_secret"}):
            dummy_app_file = Path("dummy.py")
            deployer = ModalDeployer(dummy_app_file)
            result = await deployer.check_modal_auth_async()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_modal_auth_without_env_vars(self):
        """Test Modal auth check without environment variables."""
        with patch.dict("os.environ", {}, clear=True), patch("pathlib.Path.exists", return_value=False):
            dummy_app_file = Path("dummy.py")
            deployer = ModalDeployer(dummy_app_file)
            result = await deployer.check_modal_auth_async()
            assert result is False

    @pytest.mark.asyncio
    async def test_check_modal_auth_partial_env_vars(self):
        """Test Modal auth check with partial environment variables."""
        with patch.dict("os.environ", {"MODAL_TOKEN_ID": "test_id"}, clear=True), patch("pathlib.Path.exists", return_value=False):
            dummy_app_file = Path("dummy.py")
            deployer = ModalDeployer(dummy_app_file)
            result = await deployer.check_modal_auth_async()
            assert result is False

    @pytest.mark.asyncio
    async def test_create_deployment_minimum_config(self, sample_gradio_app):
        """Test creating deployment with minimum configuration."""
        from modal_for_noobs.modal_deploy import DeploymentConfig

        deployer = ModalDeployer(sample_gradio_app)
        config = DeploymentConfig(mode="minimum", app_name=sample_gradio_app.stem)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, config)

        assert deployment_file.exists()
        assert deployment_file.suffix == ".py"
        assert "modal_" in deployment_file.name

        content = deployment_file.read_text()

        # Check essential components
        assert "import modal" in content
        assert "modal.App(" in content
        assert "modal.Image.debian_slim" in content
        assert "gradio" in content
        assert "fastapi" in content
        assert "uvicorn" in content
        assert "@modal.asgi_app()" in content
        assert "deploy_gradio" in content

        # Check minimum dependencies only
        assert "torch" not in content
        assert "tensorflow" not in content
        assert "transformers" not in content

    @pytest.mark.asyncio
    async def test_create_deployment_optimized_config(self, sample_gradio_app):
        """Test creating deployment with optimized configuration."""
        from modal_for_noobs.modal_deploy import DeploymentConfig

        deployer = ModalDeployer(sample_gradio_app)
        config = DeploymentConfig(mode="optimized", app_name=sample_gradio_app.stem)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, config)

        assert deployment_file.exists()
        content = deployment_file.read_text()

        # Check optimized dependencies
        optimized_packages = ["torch", "tensorflow", "scikit-learn", "transformers", "opencv-python", "pillow"]
        assert any(package in content for package in optimized_packages)

        # Check GPU configuration
        assert "gpu=" in content or "container_idle_timeout" in content

    @pytest.mark.asyncio
    async def test_create_deployment_complex_app(self, sample_app_with_dependencies):
        """Test creating deployment for complex app with many dependencies."""
        from modal_for_noobs.modal_deploy import DeploymentConfig

        deployer = ModalDeployer(sample_app_with_dependencies)
        config = DeploymentConfig(mode="optimized", app_name=sample_app_with_dependencies.stem)
        deployment_file = await deployer.create_modal_deployment_async(sample_app_with_dependencies, config)

        assert deployment_file.exists()
        content = deployment_file.read_text()

        # Should include detected dependencies
        assert "pandas" in content
        assert "numpy" in content
        assert "matplotlib" in content

        # Should embed the app code
        assert "process_data" in content
        assert "generate_plot" in content
        assert "ai_analysis" in content
        assert "gr.Blocks" in content

    @pytest.mark.asyncio
    async def test_create_deployment_preserves_app_structure(self, sample_app_with_dependencies):
        """Test that deployment preserves complex app structure."""
        from modal_for_noobs.modal_deploy import DeploymentConfig

        deployer = ModalDeployer(sample_app_with_dependencies)
        config = DeploymentConfig(mode="minimum", app_name=sample_app_with_dependencies.stem)
        deployment_file = await deployer.create_modal_deployment_async(sample_app_with_dependencies, config)

        content = deployment_file.read_text()

        # Check that Gradio blocks structure is preserved
        assert "with gr.Blocks() as demo:" in content
        assert "with gr.Tab(" in content
        assert "gr.File(label=" in content
        assert "gr.Dataframe()" in content
        assert "gr.Plot()" in content
        assert ".click(" in content
        assert ".upload(" in content

    @pytest.mark.asyncio
    async def test_deployment_file_naming(self, sample_gradio_app):
        """Test deployment file naming convention."""
        from modal_for_noobs.modal_deploy import DeploymentConfig

        deployer = ModalDeployer(sample_gradio_app)
        config = DeploymentConfig(mode="minimum", app_name=sample_gradio_app.stem)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, config)

        expected_name = f"modal_{sample_gradio_app.stem}.py"
        assert deployment_file.name == expected_name
        assert deployment_file.parent == sample_gradio_app.parent

    @pytest.mark.asyncio
    async def test_deployment_app_naming(self, sample_gradio_app):
        """Test Modal app naming in deployment file."""
        from modal_for_noobs.modal_deploy import DeploymentConfig

        deployer = ModalDeployer(sample_gradio_app)
        config = DeploymentConfig(mode="minimum", app_name=sample_gradio_app.stem)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, config)

        content = deployment_file.read_text()
        expected_app_name = f"modal-for-noobs-{sample_gradio_app.stem}"
        assert expected_app_name in content

    @pytest.mark.asyncio
    async def test_deployment_error_handling_invalid_file(self):
        """Test deployment creation with invalid file."""
        from modal_for_noobs.modal_deploy import DeploymentConfig

        dummy_app_file = Path("dummy.py")
        deployer = ModalDeployer(dummy_app_file)
        config = DeploymentConfig(mode="minimum", app_name="nonexistent")

        with pytest.raises(FileNotFoundError):
            await deployer.create_modal_deployment_async(Path("nonexistent.py"), config)

    @pytest.mark.asyncio
    async def test_deployment_error_handling_invalid_config(self, sample_gradio_app):
        """Test deployment creation with invalid configuration."""
        from modal_for_noobs.modal_deploy import DeploymentConfig

        deployer = ModalDeployer(sample_gradio_app)
        config = DeploymentConfig(mode="invalid_config", app_name=sample_gradio_app.stem)

        # Should handle gracefully or raise appropriate error
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, config)
        # Should default to minimum or handle appropriately
        assert deployment_file.exists()


class TestDeploymentTemplates:
    """Test deployment template generation."""

    @pytest.mark.asyncio
    async def test_minimum_template_structure(self, sample_gradio_app):
        """Test minimum template has correct structure."""
        deployer = ModalDeployer(sample_gradio_app)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "minimum")

        content = deployment_file.read_text()

        # Check template structure
        assert "Modal Deployment Script" in content
        assert "Container Image Configuration" in content
        assert "Original Gradio Application Code" in content
        assert "@app.function(" in content
        assert "@modal.asgi_app()" in content
        assert "def deploy_gradio():" in content
        assert "mount_gradio_app" in content

    @pytest.mark.asyncio
    async def test_optimized_template_enhancements(self, sample_gradio_app):
        """Test optimized template includes performance enhancements."""
        deployer = ModalDeployer(sample_gradio_app)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "optimized")

        content = deployment_file.read_text()

        # Check for performance optimizations
        assert "timeout=" in content
        assert "container_idle_timeout=" in content or "scaledown_window=" in content
        assert "max_containers=" in content or "min_containers=" in content

    @pytest.mark.asyncio
    async def test_template_modal_branding(self, sample_gradio_app):
        """Test template includes Modal-for-noobs branding."""
        deployer = ModalDeployer(sample_gradio_app)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "minimum")

        content = deployment_file.read_text()

        # Check branding
        assert "modal-for-noobs" in content.lower()
        assert "# Generated by" in content or "Auto-generated" in content

    @pytest.mark.asyncio
    async def test_template_error_handling(self, sample_gradio_app):
        """Test template includes error handling."""
        deployer = ModalDeployer(sample_gradio_app)
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "minimum")

        content = deployment_file.read_text()

        # Check for error handling patterns
        assert "try:" in content or "except" in content or "if demo is None:" in content
        assert "queue" in content  # Should enable queuing for stability


class TestAsyncOperations:
    """Test async deployment operations."""

    @pytest.mark.asyncio
    async def test_concurrent_deployment_creation(self, tmp_path):
        """Test creating multiple deployments concurrently."""
        # Create multiple sample apps
        apps = []
        for i in range(3):
            app_file = tmp_path / f"app_{i}.py"
            app_file.write_text(f"""
import gradio as gr

def greet_{i}(name):
    return f"Hello {{name}} from app {i}!"

demo = gr.Interface(fn=greet_{i}, inputs="text", outputs="text")

if __name__ == "__main__":
    demo.launch()
""")
            apps.append(app_file)

        # Use the first app as the primary app for the deployer
        deployer = ModalDeployer(apps[0])

        # Create deployments concurrently
        tasks = [deployer.create_modal_deployment_async(app, "minimum") for app in apps]

        deployment_files = await asyncio.gather(*tasks)

        # Verify all deployments were created
        assert len(deployment_files) == 3
        for deployment_file in deployment_files:
            assert deployment_file.exists()

    @pytest.mark.asyncio
    async def test_deployment_with_async_timeout(self, sample_gradio_app):
        """Test deployment creation with timeout."""
        deployer = ModalDeployer(sample_gradio_app)

        # Should complete within reasonable time
        deployment_file = await asyncio.wait_for(deployer.create_modal_deployment_async(sample_gradio_app, "minimum"), timeout=10.0)

        assert deployment_file.exists()


class TestConfigurationHandling:
    """Test different configuration scenarios."""

    @pytest.mark.asyncio
    async def test_wizard_mode_config(self, sample_gradio_app):
        """Test wizard mode configuration handling."""
        deployer = ModalDeployer(sample_gradio_app)

        # Wizard mode should work similar to optimized
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "wizard")

        assert deployment_file.exists()
        content = deployment_file.read_text()
        assert "modal.App" in content

    @pytest.mark.asyncio
    async def test_custom_config_handling(self, sample_gradio_app):
        """Test custom configuration handling."""
        deployer = ModalDeployer(sample_gradio_app)

        # Should handle unknown configs gracefully
        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "custom")

        assert deployment_file.exists()
        # Should default to minimum configuration

    @pytest.mark.asyncio
    async def test_case_insensitive_config(self, sample_gradio_app):
        """Test case insensitive configuration handling."""
        deployer = ModalDeployer(sample_gradio_app)

        deployment_file = await deployer.create_modal_deployment_async(sample_gradio_app, "MINIMUM")

        assert deployment_file.exists()
        content = deployment_file.read_text()
        assert "gradio" in content


class TestFileHandling:
    """Test file handling edge cases."""

    @pytest.mark.asyncio
    async def test_empty_python_file(self, tmp_path):
        """Test deployment creation with empty Python file."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")

        deployer = ModalDeployer(empty_file)
        deployment_file = await deployer.create_modal_deployment_async(empty_file, "minimum")

        assert deployment_file.exists()
        # Should create valid deployment even with empty source

    @pytest.mark.asyncio
    async def test_large_python_file(self, tmp_path):
        """Test deployment creation with large Python file."""
        large_content = "# Large file\n" + "# Comment line\n" * 1000
        large_content += """
import gradio as gr

def greet(name):
    return f"Hello {name}!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")

if __name__ == "__main__":
    demo.launch()
"""

        large_file = tmp_path / "large_app.py"
        large_file.write_text(large_content)

        deployer = ModalDeployer(large_file)
        deployment_file = await deployer.create_modal_deployment_async(large_file, "minimum")

        assert deployment_file.exists()
        content = deployment_file.read_text()
        assert "# Large file" in content
        assert "def greet" in content

    @pytest.mark.asyncio
    async def test_unicode_content_handling(self, tmp_path):
        """Test deployment creation with Unicode content."""
        unicode_content = """
import gradio as gr

def greet(name):
    return f"Olá {name}! 🚀💚 Bem-vindo ao Modal-for-noobs! 💚🚀"

def analyze_text(text):
    return f"Análise: {text} - Processado com sucesso! 🇧🇷"

demo = gr.Interface(
    fn=greet,
    inputs="text",
    outputs="text",
    title="🇧🇷 App Brasileiro 🇧🇷",
    description="Aplicativo com caracteres especiais e emojis!"
)

if __name__ == "__main__":
    demo.launch()
"""

        unicode_file = tmp_path / "unicode_app.py"
        unicode_file.write_text(unicode_content, encoding="utf-8")

        deployer = ModalDeployer(unicode_file)
        deployment_file = await deployer.create_modal_deployment_async(unicode_file, "minimum")

        assert deployment_file.exists()
        content = deployment_file.read_text(encoding="utf-8")
        assert "🚀💚" in content
        assert "Olá" in content
        assert "🇧🇷" in content
