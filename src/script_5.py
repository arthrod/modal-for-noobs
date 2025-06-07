# Let's create the core implementation files with proper syntax

# First, let's create the config.py file
config_py = '''
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

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
            
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value"""
        config = self.load_config()
        return config.get(key, default)
    
    def set_config_value(self, key: str, value: Any):
        """Set a specific configuration value"""
        config = self.load_config()
        config[key] = value
        self.save_config(config)
'''

# Auth module
auth_py = '''
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

class ModalAuthenticator:
    """Handle Modal authentication"""
    
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
    
    def setup_authentication(self, token_id: Optional[str] = None, token_secret: Optional[str] = None) -> bool:
        """Setup Modal authentication"""
        if token_id and token_secret:
            # Set environment variables
            os.environ["MODAL_TOKEN_ID"] = token_id
            os.environ["MODAL_TOKEN_SECRET"] = token_secret
            print("✓ Modal authentication configured via environment variables")
            return True
        else:
            # Run modal setup
            try:
                subprocess.run(["modal", "setup"], check=True)
                print("✓ Modal authentication setup complete")
                return True
            except subprocess.CalledProcessError:
                print("✗ Failed to setup Modal authentication")
                return False
                
    def parse_api_key(self, api_key: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse API key string into token ID and secret"""
        if ":" in api_key:
            return tuple(api_key.split(":", 1))
        return None, None
'''

# Wrapper module
wrapper_py = '''
import os
import sys
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, List

class GradioAppWrapper:
    """Wrap and prepare Gradio apps for Modal deployment"""
    
    def __init__(self, app_file: Path, mode: str = "minimum"):
        self.app_file = app_file
        self.mode = mode
        self.deployment_file = self.app_file.parent / f"modal_{self.app_file.stem}.py"
    
    def get_image_config(self) -> str:
        """Get Modal image configuration based on mode"""
        if self.mode == "minimum":
            return """
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio>=4.0.0",
    "fastapi[standard]>=0.100.0",
    "uvicorn>=0.20.0"
)"""
        else:  # optimized
            return """
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
)"""
    
    def find_gradio_interface(self) -> Optional[str]:
        """Find the Gradio interface variable name in the app file"""
        # Common variable names for Gradio interfaces
        common_names = ["demo", "app", "interface", "iface", "blocks"]
        
        # Try to load the module to inspect its contents
        module_name = self.app_file.stem
        spec = importlib.util.spec_from_file_location(module_name, self.app_file)
        if spec is None or spec.loader is None:
            return None
            
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            
            # Check for common variable names
            for name in common_names:
                if hasattr(module, name):
                    attr = getattr(module, name)
                    if hasattr(attr, 'launch') and hasattr(attr, 'queue'):
                        return name
            
            # If not found by name, check all attributes
            for attr_name in dir(module):
                if attr_name.startswith('__'):
                    continue
                    
                attr = getattr(module, attr_name)
                if hasattr(attr, 'launch') and hasattr(attr, 'queue'):
                    return attr_name
                    
            return None
        except Exception as e:
            print(f"Warning: Could not analyze Gradio app: {e}")
            return None
    
    def create_deployment_file(self) -> Path:
        """Create Modal deployment file"""
        # Configure GPU
        gpu_config = 'gpu="any",' if self.mode == "optimized" else ""
        module_name = self.app_file.stem
        
        # Try to find the Gradio interface variable
        interface_name = self.find_gradio_interface()
        if interface_name:
            demo_finder = f"""
    # Import the original Gradio app
    import {module_name}
    
    # Use the identified Gradio interface
    demo = {module_name}.{interface_name}
"""
        else:
            # Fallback to dynamic discovery
            demo_finder = f"""
    # Import the original Gradio app
    import {module_name}
    
    # Try to find the Gradio interface
    demo = None
    for attr_name in dir({module_name}):
        if attr_name.startswith('__'):
            continue
            
        attr = getattr({module_name}, attr_name)
        if hasattr(attr, 'queue') and hasattr(attr, 'launch'):
            demo = attr
            break
    
    if demo is None:
        raise ValueError("Could not find Gradio interface in {module_name}. "
                         "Please ensure your Gradio app defines a 'demo', 'app', or 'interface' variable.")
"""
        
        # Generate deployment code
        deployment_code = f'''
import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("easy-modal-gradio-{self.app_file.stem}")

# Configure image
{self.get_image_config()}

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
    
    import sys
    from pathlib import Path
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
{demo_finder}
    
    # Enable queuing for concurrent requests
    demo.queue(max_size=10)
    
    # Mount Gradio app to FastAPI
    fastapi_app = FastAPI(title="Easy Modal Gradio App")
    return mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    # For local testing
    app.run()
'''
        
        # Write deployment file
        with open(self.deployment_file, 'w') as f:
            f.write(deployment_code)
        
        print(f"✓ Created deployment file: {self.deployment_file}")
        return self.deployment_file
'''

# CLI module
cli_py = '''#!/usr/bin/env python3
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
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Import components
from easy_modal.config import EasyModalConfig
from easy_modal.auth import ModalAuthenticator
from easy_modal.wrapper import GradioAppWrapper

console = Console()

# Version info
__version__ = "1.0.0"

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
@click.option('--api-key', help='Modal API token (format: token_id:token_secret)')
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
            # Parse API key
            token_id, token_secret = authenticator.parse_api_key(api_key)
            if token_id and token_secret:
                authenticator.setup_authentication(token_id, token_secret)
            else:
                console.print("[red]✗[/red] Invalid API key format. Expected: token_id:token_secret")
                sys.exit(1)
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

# Create a simple example app
simple_app = '''
import gradio as gr

def greet(name, intensity):
    """Simple greeting function"""
    return "Hello, " + name + "!" * int(intensity)

# Create a Gradio interface
demo = gr.Interface(
    fn=greet,
    inputs=[
        gr.Textbox(label="Name", placeholder="Enter your name"),
        gr.Slider(minimum=1, maximum=10, step=1, label="Enthusiasm Level")
    ],
    outputs=gr.Textbox(label="Greeting"),
    title="Greeting App",
    description="A simple greeting application"
)

# Only launch if running directly
if __name__ == "__main__":
    demo.launch()
'''

# Print the files we've created
print("Config Module (config.py):")
print("-" * 40)
print(config_py)

print("\nAuth Module (auth.py):")
print("-" * 40)
print(auth_py)

print("\nWrapper Module (wrapper.py):")
print("-" * 40)
print(wrapper_py)

print("\nCLI Module (cli.py):")
print("-" * 40)
print(cli_py)

print("\nSample Gradio App (simple_app.py):")
print("-" * 40)
print(simple_app)