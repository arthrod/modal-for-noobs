"""Utility helpers from the legacy easy_modal_cli module."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path


def check_modal_auth() -> bool:
    """Return True if Modal authentication is configured."""
    if os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"):
        return True
    return (Path.home() / ".modal.toml").exists()


def setup_modal_auth() -> bool:
    """Run ``modal setup`` if Modal authentication is missing."""
    try:
        subprocess.run(["modal", "setup"], check=True)
    except subprocess.CalledProcessError:
        return False
    return True


def create_modal_deployment(app_file: str | Path, mode: str = "minimum") -> Path:
    """Create a simple Modal deployment file for a Gradio app."""
    app_path = Path(app_file)
    deployment_file = app_path.parent / f"modal_{app_path.stem}.py"

    if mode == "minimum":
        image_config = (
            "image = modal.Image.debian_slim(python_version='3.11').pip_install(\n"
            "    'gradio>=4.0.0',\n    'fastapi[standard]>=0.100.0',\n    'uvicorn>=0.20.0'\n)"
        )
    else:
        image_config = (
            "image = modal.Image.debian_slim(python_version='3.11').pip_install(\n"
            "    'gradio>=4.0.0',\n    'fastapi[standard]>=0.100.0',\n    'uvicorn>=0.20.0',\n"
            "    'torch>=2.0.0',\n    'transformers>=4.20.0',\n    'accelerate>=0.20.0',\n"
            "    'diffusers>=0.20.0',\n    'pillow>=9.0.0',\n    'numpy>=1.21.0',\n    'pandas>=1.3.0'\n)"
        )

    gpu_line = "    gpu='any'," if mode == "optimized" else ""

    deployment_template = f"""
import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

app = modal.App('easy-modal-gradio-{app_path.stem}')

{image_config}

@app.function(
    image=image,{gpu_line}
    min_containers=1,
    max_containers=1,
    timeout=3600,
    scaledown_window=60 * 20,
)
@modal.concurrent(max_inputs=100)
@modal.asgi_app()
def deploy_gradio():
    import sys
    from pathlib import Path

    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    import {app_path.stem} as target
    demo = None
    for attr in ['demo', 'app', 'interface', 'iface']:
        if hasattr(target, attr):
            obj = getattr(target, attr)
            if hasattr(obj, 'queue') and hasattr(obj, 'launch'):
                demo = obj
                break
    if demo is None:
        for attr in dir(target):
            if attr.startswith('_'):
                continue
            obj = getattr(target, attr)
            if hasattr(obj, 'queue') and hasattr(obj, 'launch'):
                demo = obj
                break
    if demo is None:
        raise ValueError('Could not find Gradio interface')
    demo.queue(max_size=10)
    fastapi_app = FastAPI(title='Easy Modal Gradio App')
    return mount_gradio_app(fastapi_app, demo, path='/')

if __name__ == '__main__':
    app.run()
"""

    deployment_file.write_text(deployment_template.strip())
    return deployment_file
