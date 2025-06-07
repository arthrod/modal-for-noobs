#!/usr/bin/env python3
"""
Easy Modal CLI - Complete Working Implementation
"""
import os
import sys
import subprocess
from pathlib import Path

import click


def check_modal_auth():
    """Check if Modal is authenticated"""
    # Check environment variables
    if os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"):
        return True
    
    # Check for modal config file
    modal_config = Path.home() / ".modal.toml"
    return modal_config.exists()


def setup_modal_auth():
    """Setup Modal authentication"""
    try:
        subprocess.run(["modal", "setup"], check=True)
        print("✓ Modal authentication setup complete")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to setup Modal authentication")
        return False


def create_modal_deployment(app_file, mode="minimum"):
    """Create Modal deployment file for Gradio app"""
    app_path = Path(app_file)
    deployment_file = app_path.parent / f"modal_{app_path.stem}.py"
    
    # Configure image based on mode
    if mode == "minimum":
        image_config = '''
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio>=4.0.0",
    "fastapi[standard]>=0.100.0",
    "uvicorn>=0.20.0"
)'''
    else:  # optimized
        image_config = '''
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio>=4.0.0",
    "fastapi[standard]>=0.100.0",
    "uvicorn>=0.20.0",
    "torch>=2.0.0",
    "transformers>=4.20.0",
    "accelerate>=0.20.0",
    "diffusers>=0.20.0",
    "pillow>=9.0.0",
    "numpy>=1.21.0",
    "pandas>=1.3.0"
)'''

    # GPU configuration
    gpu_line = '    gpu="any",' if mode == "optimized" else ""
    
    # Generate deployment code
    deployment_template = f'''
import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("easy-modal-gradio-{app_path.stem}")

# Configure image
{image_config}

@app.function(
    image=image,{gpu_line}
    min_containers=1,
    max_containers=1,  # Single container for sticky sessions
    timeout=3600,
    scaledown_window=60 * 20
)
@modal.concurrent(max_inputs=100)
@modal.asgi_app()
def deploy_gradio():
    """Deploy Gradio app with Modal"""
    
    import sys
    from pathlib import Path
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Import the original Gradio app
    import {app_path.stem}
    
    # Try to find the Gradio interface
    demo = None
    for attr_name in ["demo", "app", "interface", "iface"]:
        if hasattr({app_path.stem}, attr_name):
            attr = getattr({app_path.stem}, attr_name)
            if hasattr(attr, 'queue') and hasattr(attr, 'launch'):
                demo = attr
                break
    
    if demo is None:
        # Fallback: scan all attributes
        for attr_name in dir({app_path.stem}):
            if attr_name.startswith('__'):
                continue
            attr = getattr({app_path.stem}, attr_name)
            if hasattr(attr, 'queue') and hasattr(attr, 'launch'):
                demo = attr
                break
    
    if demo is None:
        raise ValueError("Could not find Gradio interface")
    
    # Enable queuing for concurrent requests
    demo.queue(max_size=10)
    
    # Mount Gradio app to FastAPI
    fastapi_app = FastAPI(title="Easy Modal Gradio App")
    return mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    app.run()
'''
    
    # Write deployment file
    with open(deployment_file, 'w') as f:
        f.write(deployment_template.strip())
    
    print(f"✓ Created deployment file: {deployment_file}")
    return deployment_file


@click.group()
def cli():
    """Easy Modal CLI - Deploy Gradio apps to Modal with zero configuration"""
    pass


@cli.command()
@click.argument('app_file', type=click.Path(exists=True))
@click.option('--minimum', 'mode', flag_value='minimum', default=True,
              help='Deploy with minimal dependencies (CPU only)')
@click.option('--optimized', 'mode', flag_value='optimized',
              help='Deploy with ML libraries and GPU support')
@click.option('--dry-run', is_flag=True, help='Generate files without deploying')
def deploy(app_file, mode, dry_run):
    """Deploy Gradio app to Modal"""
    
    print(f"🚀 Easy Modal Gradio Deployment")
    print(f"App: {app_file}")
    print(f"Mode: {mode}")
    print()
    
    # Check authentication
    if not check_modal_auth():
        print("⚠ Modal authentication required")
        if not setup_modal_auth():
            sys.exit(1)
    else:
        print("✓ Modal authentication verified")
    
    # Create deployment file
    deployment_file = create_modal_deployment(app_file, mode)
    
    if dry_run:
        print(f"Dry run complete. Generated: {deployment_file}")
        return
    
    # Deploy to Modal
    print("\nDeploying to Modal...")
    try:
        result = subprocess.run(
            ["modal", "deploy", str(deployment_file)],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract URL from output
        output_lines = result.stdout.split('\n')
        url = None
        for line in output_lines:
            if 'https://' in line and 'modal.run' in line:
                url = line.strip()
                break
        
        print("✓ Deployment successful!")
        if url:
            print(f"🌐 Your app is live at: {url}")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Deployment failed: {e}")
        sys.exit(1)


@cli.command()
def auth():
    """Setup Modal authentication"""
    if check_modal_auth():
        print("✓ Modal is already authenticated")
    else:
        setup_modal_auth()


if __name__ == "__main__":
    cli()