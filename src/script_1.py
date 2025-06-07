# Create the main easy-modal CLI tool structure

# First, let's create the setup.py or pyproject.toml equivalent structure
setup_config = """
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "easy-modal"
version = "1.0.0"
description = "Idiot-proof Gradio deployment CLI for Modal"
authors = [{name = "Easy Modal Team", email = "team@easymodal.dev"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "click>=8.0.0",
    "modal>=0.57.0",
    "gradio>=4.0.0",
    "fastapi>=0.100.0",
    "pyyaml>=6.0",
    "rich>=10.0.0",
    "requests>=2.25.0"
]

[project.scripts]
easy-modal = "easy_modal.cli:main"

[project.optional-dependencies]
dev = ["pytest", "black", "flake8"]
"""

print("Setup Configuration (pyproject.toml):")
print(setup_config)

# Create the main CLI entry point
cli_main = '''#!/usr/bin/env python3
"""
Easy Modal CLI - Idiot-proof Gradio deployment for Modal
"""
import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

import click
import modal
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Version info
__version__ = "1.0.0"

class EasyModalConfig:
    """Configuration management for Easy Modal"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".easy-modal"
        self.config_file = self.config_dir / "config.yaml"
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

class ModalAuthenticator:
    """Handle Modal authentication"""
    
    def __init__(self):
        self.config = EasyModalConfig()
    
    def check_authentication(self) -> bool:
        """Check if Modal is authenticated"""
        try:
            # Check for MODAL_TOKEN_ID and MODAL_TOKEN_SECRET in environment
            if os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"):
                return True
            
            # Check for modal token file
            modal_config = Path.home() / ".modal.toml"
            if modal_config.exists():
                return True
                
            return False
        except Exception:
            return False
    
    def setup_authentication(self, token_id: Optional[str] = None, token_secret: Optional[str] = None):
        """Setup Modal authentication"""
        if token_id and token_secret:
            # Set environment variables
            os.environ["MODAL_TOKEN_ID"] = token_id
            os.environ["MODAL_TOKEN_SECRET"] = token_secret
            console.print("[green]✓[/green] Modal authentication configured via environment variables")
        else:
            # Run modal setup
            console.print("Setting up Modal authentication...")
            try:
                subprocess.run(["modal", "setup"], check=True)
                console.print("[green]✓[/green] Modal authentication setup complete")
            except subprocess.CalledProcessError:
                console.print("[red]✗[/red] Failed to setup Modal authentication")
                sys.exit(1)

class GradioAppWrapper:
    """Wrap and prepare Gradio apps for Modal deployment"""
    
    def __init__(self, app_file: Path, mode: str = "minimum"):
        self.app_file = app_file
        self.mode = mode
        self.deployment_file = self.app_file.parent / f"modal_{self.app_file.stem}.py"
    
    def generate_deployment_code(self) -> str:
        """Generate Modal deployment code for Gradio app"""
        
        # Read the original Gradio app
        with open(self.app_file, 'r') as f:
            original_code = f.read()
        
        # Generate appropriate image based on mode
        if self.mode == "minimum":
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
        gpu_config = 'gpu="any",' if self.mode == "optimized" else ""
        
        deployment_template = f'''
import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("easy-modal-gradio-{self.app_file.stem}")

# Configure image
{image_config}

# Original Gradio app code
{original_code}

@app.function(
    image=image,
    {gpu_config}
    min_containers=1,
    max_containers=1,  # Single container for sticky sessions
    timeout=3600,
    scaledown_window=60 * 20
)
@modal.concurrent(max_inputs=100)
@modal.asgi_app()
def deploy_gradio():
    """Deploy Gradio app with Modal"""
    
    # Get the demo object from the original code
    # This assumes the Gradio interface is assigned to 'demo' or similar
    import sys
    import types
    
    # Execute the original code to get the Gradio interface
    local_vars = {{}}
    exec(open("{self.app_file}").read(), {{}}, local_vars)
    
    # Find the Gradio interface object
    demo = None
    for var_name, var_value in local_vars.items():
        if hasattr(var_value, 'queue') and hasattr(var_value, 'launch'):
            demo = var_value
            break
    
    if demo is None:
        # Try common variable names
        for name in ['demo', 'app', 'interface', 'iface']:
            if name in local_vars:
                demo = local_vars[name]
                break
    
    if demo is None:
        raise ValueError("Could not find Gradio interface in the provided file")
    
    # Enable queuing for concurrent requests
    demo.queue(max_size=10)
    
    # Mount Gradio app to FastAPI
    fastapi_app = FastAPI(title="Easy Modal Gradio App")
    return mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    # For local testing
    app.run()
'''
        
        return deployment_template
    
    def create_deployment_file(self):
        """Create Modal deployment file"""
        deployment_code = self.generate_deployment_code()
        
        with open(self.deployment_file, 'w') as f:
            f.write(deployment_code)
        
        console.print(f"[green]✓[/green] Created deployment file: {self.deployment_file}")
        return self.deployment_file

@click.group()
@click.version_option(version=__version__)
def main():
    """Easy Modal CLI - Deploy Gradio apps to Modal with zero configuration"""
    pass

@main.command()
@click.argument('app_file', type=click.Path(exists=True, path_type=Path))
@click.option('--minimum', 'mode', flag_value='minimum', default=True,
              help='Deploy with minimal dependencies (CPU only)')
@click.option('--optimized', 'mode', flag_value='optimized',
              help='Deploy with ML libraries and GPU support')
@click.option('--step-by-step', is_flag=True,
              help='Interactive deployment wizard')
@click.option('--config', type=click.Path(path_type=Path),
              help='Use configuration file')
@click.option('--api-key', help='Modal API token')
@click.option('--dry-run', is_flag=True, help='Generate files without deploying')
def deploy(app_file: Path, mode: str, step_by_step: bool, config: Optional[Path], 
          api_key: Optional[str], dry_run: bool):
    """Deploy Gradio app to Modal"""
    
    console.print(Panel.fit(
        f"[bold blue]Easy Modal Gradio Deployment[/bold blue]\\n"
        f"App: {app_file}\\n"
        f"Mode: {mode}",
        border_style="blue"
    ))
    
    # Initialize components
    authenticator = ModalAuthenticator()
    
    # Handle step-by-step mode
    if step_by_step:
        console.print("\\n[yellow]Step-by-step deployment wizard[/yellow]")
        
        # Ask for deployment mode if not specified
        if mode == 'minimum':
            mode_choice = click.prompt(
                "Deployment mode",
                type=click.Choice(['minimum', 'optimized']),
                default='minimum'
            )
            mode = mode_choice
        
        # Ask for GPU if optimized
        if mode == 'optimized':
            gpu_confirm = click.confirm("Enable GPU support?", default=True)
            if not gpu_confirm:
                mode = 'minimum'
    
    # Check authentication
    if not authenticator.check_authentication():
        console.print("[yellow]⚠[/yellow] Modal authentication required")
        
        if api_key:
            # Extract token parts if full token provided
            if api_key.startswith('ak-'):
                console.print("[red]✗[/red] Please provide both MODAL_TOKEN_ID and MODAL_TOKEN_SECRET")
                sys.exit(1)
            else:
                authenticator.setup_authentication()
        else:
            authenticator.setup_authentication()
    else:
        console.print("[green]✓[/green] Modal authentication verified")
    
    # Create deployment wrapper
    wrapper = GradioAppWrapper(app_file, mode)
    deployment_file = wrapper.create_deployment_file()
    
    if dry_run:
        console.print(f"[yellow]Dry run complete. Generated: {deployment_file}[/yellow]")
        return
    
    # Deploy to Modal
    console.print("\\n[blue]Deploying to Modal...[/blue]")
    try:
        result = subprocess.run(
            ["modal", "deploy", str(deployment_file)],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract URL from output
        output_lines = result.stdout.split('\\n')
        url = None
        for line in output_lines:
            if 'https://' in line and 'modal.run' in line:
                url = line.strip()
                break
        
        console.print("[green]✓[/green] Deployment successful!")
        if url:
            console.print(f"[blue]🌐 Your app is live at:[/blue] {url}")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Deployment failed: {e}")
        console.print(f"Error output: {e.stderr}")
        sys.exit(1)

@main.command()
@click.option('--token-id', help='Modal token ID')
@click.option('--token-secret', help='Modal token secret')
def auth(token_id: Optional[str], token_secret: Optional[str]):
    """Setup Modal authentication"""
    authenticator = ModalAuthenticator()
    
    if token_id and token_secret:
        authenticator.setup_authentication(token_id, token_secret)
    else:
        authenticator.setup_authentication()

@main.command()
@click.option('--generate', is_flag=True, help='Generate sample configuration')
def config(generate: bool):
    """Manage configuration"""
    config_manager = EasyModalConfig()
    
    if generate:
        sample_config = {
            'default_mode': 'minimum',
            'default_gpu': False,
            'volumes': [],
            'secrets': [],
            'custom_image_packages': []
        }
        
        config_file = Path('easy-modal-config.yaml')
        with open(config_file, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False)
        
        console.print(f"[green]✓[/green] Generated sample config: {config_file}")
    else:
        current_config = config_manager.load_config()
        console.print("Current configuration:")
        console.print(yaml.dump(current_config, default_flow_style=False))

if __name__ == "__main__":
    main()
'''

print("\nMain CLI Module (easy_modal/cli.py):")
print("=" * 60)
print(cli_main)