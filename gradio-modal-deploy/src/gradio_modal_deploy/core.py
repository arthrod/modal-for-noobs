"""Core functionality for Modal deployment and GitHub integration."""

import asyncio
import base64
from pathlib import Path

import httpx
from loguru import logger


class ModalAPI:
    """Async Modal API client for deployment management."""

    def __init__(self):
        """Initialize Modal API client."""
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def check_auth(self) -> bool:
        """Check if Modal is authenticated."""
        try:
            process = await asyncio.create_subprocess_exec(
                "modal", "auth", "current",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return process.returncode == 0
        except FileNotFoundError:
            logger.error("Modal CLI not found. Please install: pip install modal")
            return False

    async def setup_auth(self) -> bool:
        """Setup Modal authentication."""
        try:
            process = await asyncio.create_subprocess_exec(
                "modal", "setup",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return process.returncode == 0
        except Exception as e:
            logger.error(f"Failed to setup Modal auth: {e}")
            return False

    async def deploy_app(
        self,
        app_file: Path,
        mode: str = "optimized",
        timeout_minutes: int = 60
    ) -> dict[str, any]:
        """Deploy a Gradio app to Modal."""
        try:
            # Create deployment file
            deployment_file = await self._create_deployment_file(app_file, mode, timeout_minutes)

            # Deploy to Modal
            process = await asyncio.create_subprocess_exec(
                "modal", "deploy", str(deployment_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                # Extract URL from output
                output = stdout.decode()
                url = self._extract_url_from_output(output)

                return {
                    "success": True,
                    "url": url,
                    "output": output,
                    "deployment_file": deployment_file
                }
            return {
                "success": False,
                "error": stderr.decode(),
                "deployment_file": deployment_file
            }

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_deployment_file(
        self,
        app_file: Path,
        mode: str,
        timeout_minutes: int
    ) -> Path:
        """Create Modal deployment file."""
        # This would use the same logic as the main modal-for-noobs package
        # For now, it's a simplified version
        deployment_file = app_file.parent / f"modal_{app_file.stem}.py"

        # Read original app code
        original_code = app_file.read_text()

        # Create deployment template
        deployment_template = f"""
import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("gradio-modal-deploy-{app_file.stem}")

# Configure image based on mode
{self._get_image_config(mode)}

# Original Gradio app code
{original_code}

@app.function(
    image=image,
    timeout={timeout_minutes * 60},
    min_containers=1,
    max_containers=1
)
@modal.asgi_app()
def deploy_gradio():
    # Find the Gradio demo
    demo = None
    for var_name, var_value in globals().items():
        if hasattr(var_value, 'queue') and hasattr(var_value, 'launch'):
            demo = var_value
            break

    if demo is None:
        raise ValueError("Could not find Gradio interface")

    demo.queue(max_size=10)

    fastapi_app = FastAPI(title="Gradio Modal Deploy App")
    return mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    app.run()
"""

        # Write deployment file
        deployment_file.write_text(deployment_template.strip())
        return deployment_file

    def _get_image_config(self, mode: str) -> str:
        """Get image configuration based on deployment mode."""
        if mode == "minimum":
            return '''
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio", "fastapi", "uvicorn"
)'''
        if mode == "gra_jupy":
            return '''
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio", "fastapi", "uvicorn", "jupyter", "jupyterlab",
    "notebook", "ipywidgets", "matplotlib", "plotly", "seaborn"
)'''
        # optimized
        return '''
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio", "fastapi", "uvicorn", "torch", "transformers",
    "accelerate", "diffusers", "pillow", "numpy", "pandas"
)'''

    def _extract_url_from_output(self, output: str) -> str | None:
        """Extract deployment URL from Modal output."""
        lines = output.split('\n')
        for line in lines:
            if 'https://' in line and 'modal.run' in line:
                return line.strip()
        return None

    async def list_deployments(self) -> list[dict[str, any]]:
        """List active Modal deployments."""
        try:
            process = await asyncio.create_subprocess_exec(
                "modal", "app", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                # Parse output into structured data
                deployments = []
                lines = stdout.decode().split('\n')

                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            deployments.append({
                                "name": parts[0],
                                "status": parts[1] if len(parts) > 1 else "unknown",
                                "url": self._extract_url_from_line(line)
                            })

                return deployments
            logger.error(f"Failed to list deployments: {stderr.decode()}")
            return []

        except Exception as e:
            logger.error(f"Error listing deployments: {e}")
            return []

    def _extract_url_from_line(self, line: str) -> str | None:
        """Extract URL from a deployment line."""
        if 'https://' in line:
            parts = line.split()
            for part in parts:
                if part.startswith('https://'):
                    return part
        return None

    async def kill_deployment(self, app_name: str) -> bool:
        """Kill a specific deployment."""
        try:
            process = await asyncio.create_subprocess_exec(
                "modal", "app", "stop", app_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return process.returncode == 0
        except Exception as e:
            logger.error(f"Failed to kill deployment {app_name}: {e}")
            return False


class GitHubAPI:
    """Async GitHub API client for Modal examples."""

    def __init__(self, repo: str = "modal-labs/modal-examples"):
        """Initialize GitHub API client."""
        self.repo = repo
        self.owner, self.repo_name = repo.split('/')
        self.base_url = "https://api.github.com"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_repo_contents(self, path: str = "") -> list[dict[str, any]]:
        """Get repository contents for a specific path."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/contents/{path}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch repo contents for path '{path}': {e}")
            return []

    async def get_file_content(self, path: str) -> str:
        """Get the content of a specific file."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/contents/{path}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            if data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
            return data.get("content", "")

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch file content for '{path}': {e}")
            return ""

    async def get_all_folders(self) -> list[dict[str, str]]:
        """Get all folders in the repository root."""
        contents = await self.get_repo_contents()

        folders = []
        for item in contents:
            if item.get("type") == "dir":
                folders.append({
                    "name": item["name"],
                    "path": item["path"]
                })

        return sorted(folders, key=lambda x: x["name"])

    async def get_python_files_in_folder(self, folder_path: str) -> list[dict[str, str]]:
        """Get all Python files in a specific folder."""
        contents = await self.get_repo_contents(folder_path)

        python_files = []
        for item in contents:
            if item.get("type") == "file" and item["name"].endswith(".py"):
                python_files.append({
                    "name": item["name"],
                    "path": item["path"]
                })

        return sorted(python_files, key=lambda x: x["name"])

    async def get_readme_content(self, folder_path: str = "") -> str:
        """Get README.md content for a folder, with fallback to root README."""
        # Try folder-specific README first
        if folder_path:
            readme_path = f"{folder_path}/README.md"
            content = await self.get_file_content(readme_path)
            if content:
                return content

        # Fallback to root README
        root_readme_content = await self.get_file_content("README.md")
        return root_readme_content


# Global instances
modal_api = ModalAPI()
github_api = GitHubAPI()
