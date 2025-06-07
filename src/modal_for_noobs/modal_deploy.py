"""Async Modal deployment functionality."""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Optional

import httpx
from loguru import logger
from rich import print as rprint

from .config_loader import config_loader

# Modal's signature colors
MODAL_GREEN = "#00D26A"


class ModalDeployer:
    """Async-first Modal deployment handler."""

    async def check_modal_auth_async(self) -> bool:
        """Check if Modal is authenticated (async)."""
        # Check environment variables
        if os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"):
            return True
        
        # Check for modal config file
        modal_config = Path.home() / ".modal.toml"
        return modal_config.exists()

    async def setup_modal_auth_async(self) -> bool:
        """Setup Modal authentication (async)."""
        try:
            process = await asyncio.create_subprocess_exec(
                "modal", "setup",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                rprint(f"[{MODAL_GREEN}]✅ Modal authentication setup complete![/{MODAL_GREEN}]")
                return True
            else:
                rprint(f"[red]❌ Failed to setup Modal authentication: {stderr.decode()}[/red]")
                return False
        except FileNotFoundError:
            rprint("[red]❌ Modal CLI not found. Please install: pip install modal[/red]")
            return False

    async def create_modal_deployment_async(self, app_file: Path, mode: str = "minimum", requirements_path: Optional[Path] = None, timeout_minutes: int = 60, test_deploy: bool = False) -> Path:
        """Create Modal deployment file for Gradio app (async)."""
        deployment_file = app_file.parent / f"modal_{app_file.stem}.py"
        
        # Parse requirements.txt if provided
        custom_packages = []
        if requirements_path and requirements_path.exists():
            try:
                requirements_content = requirements_path.read_text().strip()
                for line in requirements_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Remove version numbers and git URLs as requested
                        package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0].split('>')[0].split('<')[0].split('@')[0].strip()
                        if package_name:
                            custom_packages.append(f'"{package_name}"')
            except Exception as e:
                logger.warning(f"Could not parse requirements.txt: {e}")

        # Load base packages from config
        package_config = config_loader.load_base_packages()
        base_packages_list = package_config.get(mode, package_config.get("minimum", []))
        
        # Format packages for Modal
        base_packages = [f'"{pkg}"' for pkg in base_packages_list]
        
        # Combine base packages with custom ones (avoiding duplicates)
        all_packages = base_packages.copy()
        for pkg in custom_packages:
            pkg_clean = pkg.strip('"').lower()
            if not any(pkg_clean in base_pkg.strip('"').lower() for base_pkg in base_packages):
                all_packages.append(pkg)
        
        packages_str = ',\n    '.join(all_packages)
        
        image_config = f'''
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    {packages_str}
)'''

        # GPU configuration
        gpu_line = '    gpu="any",' if mode in ["optimized", "gra_jupy"] else ""
        
        # Timeout configuration
        if test_deploy:
            timeout_seconds = 30  # 30 seconds for testing
            scaledown_window = 5  # Scale down quickly
        else:
            timeout_seconds = timeout_minutes * 60
            scaledown_window = 60 * 20  # 20 minutes
        
        # Read the original app code
        original_code = app_file.read_text()
        
        # Generate deployment code with embedded source
        deployment_template = f'''
import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("modal-for-noobs-{app_file.stem}")

# Configure image
{image_config}

# Original Gradio app code embedded
{original_code}

@app.function(
    image=image,{gpu_line}
    min_containers=1,
    max_containers=1,  # Single container for sticky sessions
    timeout={timeout_seconds},
    scaledown_window={scaledown_window}
)
@modal.concurrent(max_inputs=100)
@modal.asgi_app()
def deploy_gradio():
    """Deploy Gradio app with Modal"""
    
    # The demo variable should be available from the embedded code above
    # Try to find it in the global scope
    demo = None
    
    # Check if demo is in globals
    if 'demo' in globals():
        demo = globals()['demo']
    elif 'app' in globals() and hasattr(globals()['app'], 'queue'):
        demo = globals()['app']
    elif 'interface' in globals():
        demo = globals()['interface']
    elif 'iface' in globals():
        demo = globals()['iface']
    
    if demo is None:
        # Last resort: scan all globals for Gradio interfaces
        for var_name, var_value in globals().items():
            if hasattr(var_value, 'queue') and hasattr(var_value, 'launch'):
                demo = var_value
                break
    
    if demo is None:
        raise ValueError("Could not find Gradio interface in the app")
    
    # Enable queuing for concurrent requests
    demo.queue(max_size=10)
    
    # Mount Gradio app to FastAPI
    fastapi_app = FastAPI(title="Modal-for-noobs Gradio App")
    return mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    app.run()
'''
        
        # Write deployment file (async file writing)
        def write_file():
            with open(deployment_file, 'w') as f:
                f.write(deployment_template.strip())
        
        await asyncio.to_thread(write_file)
        
        rprint(f"[{MODAL_GREEN}]✅ Created deployment file: {deployment_file}[/{MODAL_GREEN}]")
        return deployment_file

    async def deploy_to_modal_async(self, deployment_file: Path) -> Optional[str]:
        """Deploy to Modal and return the URL (async)."""
        try:
            process = await asyncio.create_subprocess_exec(
                "modal", "deploy", str(deployment_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                rprint(f"[red]❌ Deployment failed: {stderr.decode()}[/red]")
                return None
            
            # Extract URL from output
            output_lines = stdout.decode().split('\n')
            url = None
            for line in output_lines:
                if 'https://' in line and 'modal.run' in line:
                    url = line.strip()
                    break
            
            return url
            
        except Exception as e:
            logger.error(f"Deployment error: {e}")
            return None