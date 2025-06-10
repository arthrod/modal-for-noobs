"""Tests for Gradio components."""

from pathlib import Path

import pytest

from gradio_modal_deploy import ModalDeployButton, ModalTheme
from gradio_modal_deploy.utils import validate_app_file


def test_modal_deploy_button_creation() -> None:
    """Test ModalDeployButton component creation."""
    button = ModalDeployButton(
        app_file="test_app.py",
        mode="minimum",
        timeout_minutes=30,
    )

    assert button.app_file == Path("test_app.py")
    assert button.mode == "minimum"
    assert button.timeout_minutes == 30


def test_modal_theme_creation() -> None:
    """Test ModalTheme creation."""
    theme = ModalTheme()
    assert theme is not None


def test_validate_app_file_nonexistent() -> None:
    """Test validation of non-existent file."""
    result = validate_app_file("nonexistent.py")
    assert not result["valid"]
    assert "not found" in result["error"].lower()


def test_validate_app_file_wrong_extension() -> None:
    """Test validation of file with wrong extension."""
    result = validate_app_file("test.txt")
    assert not result["valid"]
    assert "python file" in result["error"].lower()


@pytest.fixture
def sample_gradio_app(tmp_path):
    """Create a sample Gradio app file for testing."""
    app_file = tmp_path / "test_app.py"
    app_file.write_text("""
import gradio as gr

def greet(name):
    return f"Hello {name}!"

with gr.Blocks() as demo:
    gr.Markdown("# Test App")
    name_input = gr.Textbox(label="Name")
    output = gr.Textbox(label="Greeting")
    btn = gr.Button("Greet")
    btn.click(greet, inputs=name_input, outputs=output)

if __name__ == "__main__":
    demo.launch()
""")
    return app_file


def test_validate_gradio_app(sample_gradio_app) -> None:
    """Test validation of a proper Gradio app."""
    result = validate_app_file(sample_gradio_app)
    assert result["valid"]
    assert result["has_gradio"]
    assert result["has_interface"]
    assert result["suggested_mode"] == "minimum"
