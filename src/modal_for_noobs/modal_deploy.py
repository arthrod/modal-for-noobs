"""Async Modal deployment functionality with improved error handling and refactored logic."""

import asyncio
import os
import subprocess
from pathlib import Path

import httpx
from loguru import logger
from rich import print as rprint

from .config_loader import config_loader

# Modal's official color palette
MODAL_GREEN = "#7FEE64"  # Primary brand green (RGB: 127, 238, 100)


class ModalDeployer:
    """Async-first Modal deployment handler."""
    
    def __init__(self, app_file: Path, mode: str = "minimum", br_huehuehue: bool = False):
        """Initialize the deployer with app file and deployment mode."""
        self.app_file = app_file
        self.mode = mode
        self.br_huehuehue = br_huehuehue
        self.config_loader = config_loader

    async def check_modal_auth_async(self) -> bool:
        """Check if Modal is authenticated (async).
        
        Returns:
            bool: True if authenticated, False otherwise.
        """
        try:
            # Check environment variables
            if os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"):
                logger.debug("Modal authentication found via environment variables")
                return True

            # Check for modal config file
            modal_config = Path.home() / ".modal.toml"
            if modal_config.exists():
                logger.debug(f"Modal authentication found at {modal_config}")
                return True
            
            logger.debug("No Modal authentication found")
            return False
        except Exception as e:
            logger.error(f"Error checking Modal authentication: {e}")
            return False

    async def setup_modal_auth_async(self) -> bool:
        """Setup Modal authentication (async).
        
        Returns:
            bool: True if setup succeeded, False otherwise.
        """
        try:
            logger.info("Running modal setup asynchronously...")
            process = await asyncio.create_subprocess_exec(
                "modal", "setup",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.debug(f"Modal setup output: {stdout.decode()}")
                rprint(f"[{MODAL_GREEN}]✅ Modal authentication setup complete![/{MODAL_GREEN}]")
                return True
            else:
                error_msg = stderr.decode()
                logger.error(f"Modal setup failed with exit code {process.returncode}: {error_msg}")
                rprint(f"[red]❌ Failed to setup Modal authentication: {error_msg}[/red]")
                return False
        except FileNotFoundError:
            logger.error("Modal CLI not found")
            rprint("[red]❌ Modal CLI not found. Please install: pip install modal[/red]")
            return False
        except asyncio.SubprocessError as e:
            logger.error(f"Subprocess error during modal setup: {e}")
            rprint(f"[red]❌ Subprocess error: {e}[/red]")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during modal setup: {e}")
            rprint(f"[red]❌ Unexpected error: {e}[/red]")
            return False

    def _get_image_config(self, deployment_mode: str, packages: list[str]) -> str:
        """Get Modal image configuration based on deployment mode.

        Args:
            deployment_mode: The deployment mode ("minimum", "optimized", or "gra_jupy").
            packages: List of packages to install.

        Returns:
            str: Modal image configuration string.
        """
        packages_str = ',\n    '.join([f'"{pkg}"' for pkg in packages])
        return f'''image = modal.Image.debian_slim(python_version="3.11").pip_install(
    {packages_str}
)'''

    async def create_modal_deployment_async(
        self,
        app_file: Path,
        deployment_mode: str = "minimum",
        requirements_path: Path | None = None,
        timeout_minutes: int = 60,
        test_deploy: bool = False
    ) -> Path:
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
        base_packages_list = package_config.get(deployment_mode, package_config.get("minimum", []))

        # Combine base packages with custom ones (avoiding duplicates)
        all_packages = base_packages_list.copy()
        for pkg in custom_packages:
            pkg_clean = pkg.strip('"').lower()
            if not any(pkg_clean in base_pkg.lower() for base_pkg in base_packages_list):
                all_packages.append(pkg.strip('"'))

        image_config = self._get_image_config(deployment_mode, all_packages)

        # GPU configuration
        gpu_line = '    gpu="any",' if deployment_mode in ["optimized", "gra_jupy"] else ""

        # Timeout configuration
        if test_deploy:
            timeout_seconds = 30  # 30 seconds for testing
            scaledown_window = 5  # Scale down quickly
        else:
            timeout_seconds = timeout_minutes * 60
            scaledown_window = 60 * 20  # 20 minutes

        # Read the original app code
        original_code = app_file.read_text()

        # Generate deployment code with embedded source following Modal's design philosophy
        deployment_template = f'''# 🚀 Modal Deployment Script (Async Generated)
# Generated by modal-for-noobs - https://github.com/arthrod/modal-for-noobs
# Deployment Mode: {deployment_mode}
# Following Modal's technical design philosophy for high-performance cloud computing
# Timeout: {timeout_seconds}s | Scaledown: {scaledown_window}s

import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# 🎯 Create Modal App with semantic naming
app = modal.App("modal-for-noobs-{app_file.stem}")

# 🐳 Container Image Configuration
# Optimized for {deployment_mode} workloads with performance-tuned dependencies
{image_config}

# 📦 Original Gradio Application Code
# Embedded for seamless execution in Modal's cloud infrastructure
{original_code}

# ⚡ Modal Function Configuration
# Engineered for scalability, performance, and reliability
@app.function(
    image=image,{gpu_line}
    min_containers=1,
    max_containers=1,  # Single container for session consistency and state management
    timeout={timeout_seconds},  # Configurable timeout for workload requirements
    scaledown_window={scaledown_window},  # Optimized scale-down for cost efficiency
)
@modal.concurrent(max_inputs=100)  # High concurrency for production-grade performance
@modal.asgi_app()
def deploy_gradio():
    \"\"\"
    Deploy Gradio app with Modal's high-performance infrastructure.
    
    This deployment function implements:
    - Smart Gradio interface detection using global scope analysis
    - FastAPI integration following Modal's ASGI architecture patterns
    - Performance optimization for concurrent request handling
    - Error handling and fallback mechanisms for production reliability
    \"\"\"

    # 🔍 Smart Gradio Interface Detection
    # Using global scope analysis for maximum compatibility
    demo = None

    # Primary detection: Check common Gradio interface names
    if 'demo' in globals():
        demo = globals()['demo']
    elif 'app' in globals() and hasattr(globals()['app'], 'queue'):
        demo = globals()['app']
    elif 'interface' in globals():
        demo = globals()['interface']
    elif 'iface' in globals():
        demo = globals()['iface']

    # Fallback detection: Comprehensive global scope scan
    if demo is None:
        for var_name, var_value in globals().items():
            if hasattr(var_value, 'queue') and hasattr(var_value, 'launch'):
                demo = var_value
                break

    # 🚨 Fail-safe error handling with descriptive messaging
    if demo is None:
        raise ValueError(
            "Could not find Gradio interface in the application. "
            "Ensure your app defines a Gradio interface as 'demo', 'app', 'interface', or 'iface'."
        )

    # 🚀 Performance Configuration
    # Optimized queue size for responsiveness and throughput
    demo.queue(max_size=10)

    # 🔗 FastAPI Integration
    # Following Modal's recommended ASGI architecture patterns
    fastapi_app = FastAPI(
        title="Modal-for-noobs Gradio App",
        description="High-performance Gradio deployment on Modal cloud infrastructure",
        version="1.0.0",
        docs_url="/docs",  # Enable API documentation
        redoc_url="/redoc"  # Enable alternative API documentation
    )
    
    return mount_gradio_app(fastapi_app, demo, path="/")

# 🏃‍♂️ Direct execution support for local testing
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

    async def deploy_to_modal_async(self, deployment_file: Path) -> str | None:
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
    
    async def deploy(self) -> str | None:
        """Main deployment method that orchestrates the entire deployment process.
        
        Returns:
            str | None: The deployment URL if successful, None otherwise.
        """
        try:
            # Check authentication
            if not await self.check_modal_auth_async():
                logger.info("Modal authentication not found, setting up...")
                if not await self.setup_modal_auth_async():
                    raise Exception("Failed to setup Modal authentication")
            
            # Create deployment file
            deployment_file = await self.create_modal_deployment_async(
                self.app_file,
                deployment_mode=self.mode
            )
            
            # Deploy to Modal
            url = await self.deploy_to_modal_async(deployment_file)
            
            if url:
                rprint(f"[{MODAL_GREEN}]🎉 Deployment successful![/{MODAL_GREEN}]")
                rprint(f"[{MODAL_GREEN}]🌐 Your app is live at: {url}[/{MODAL_GREEN}]")
            else:
                raise Exception("Failed to get deployment URL")
                
            return url
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise
