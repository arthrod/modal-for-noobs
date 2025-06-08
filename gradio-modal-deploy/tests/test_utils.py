"""Tests for utility functions."""

import pytest
from unittest.mock import patch, AsyncMock
from gradio_modal_deploy.utils import validate_app_file, get_modal_status


def test_validate_app_file_ml_detection(tmp_path):
    """Test ML library detection in app validation."""
    app_file = tmp_path / "ml_app.py"
    app_file.write_text("""
import gradio as gr
import torch
import transformers

def process(text):
    return f"Processed: {text}"

with gr.Blocks() as demo:
    gr.Markdown("# ML App")

demo.launch()
""")

    result = validate_app_file(app_file)
    assert result["valid"]
    assert "torch" in result["detected_ml_libraries"]
    assert "transformers" in result["detected_ml_libraries"]
    assert result["suggested_mode"] == "optimized"


def test_validate_app_file_jupyter_detection(tmp_path):
    """Test Jupyter library detection in app validation."""
    app_file = tmp_path / "jupyter_app.py"
    app_file.write_text("""
import gradio as gr
import matplotlib.pyplot as plt
import plotly

def create_plot():
    return plt.figure()

with gr.Blocks() as demo:
    gr.Markdown("# Jupyter App")

demo.launch()
""")

    result = validate_app_file(app_file)
    assert result["valid"]
    assert "matplotlib" in result["detected_jupyter"]
    assert "plotly" in result["detected_jupyter"]
    assert result["suggested_mode"] == "gra_jupy"


@patch('gradio_modal_deploy.core.modal_api')
def test_get_modal_status_success(mock_modal_api):
    """Test successful Modal status retrieval."""
    mock_modal_api.check_auth = AsyncMock(return_value=True)
    mock_modal_api.list_deployments = AsyncMock(return_value=[
        {"name": "test-app", "status": "running"},
        {"name": "other-app", "status": "stopped"}
    ])

    status = get_modal_status()

    assert status["authenticated"]
    assert status["total_deployments"] == 2
    assert status["active_deployments"] == 1


@patch('gradio_modal_deploy.core.modal_api')
def test_get_modal_status_error(mock_modal_api):
    """Test Modal status retrieval with error."""
    mock_modal_api.check_auth = AsyncMock(side_effect=Exception("Test error"))

    status = get_modal_status()

    assert not status["authenticated"]
    assert status["total_deployments"] == 0
    assert "error" in status
