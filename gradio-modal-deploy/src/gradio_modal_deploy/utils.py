"""Utility functions for Modal deployment and management."""

import asyncio
from pathlib import Path

import uvloop
from loguru import logger

from .core import modal_api


def setup_modal_auth() -> bool:
    """
    Setup Modal authentication synchronously.
    
    Returns:
        bool: True if authentication was successful
    """
    try:
        return uvloop.run(modal_api.setup_auth())
    except Exception as e:
        logger.error(f"Failed to setup Modal auth: {e}")
        return False


def get_modal_status() -> dict[str, any]:
    """
    Get current Modal deployment status synchronously.
    
    Returns:
        dict: Status information including deployments list
    """
    try:
        deployments = uvloop.run(modal_api.list_deployments())
        
        return {
            "authenticated": uvloop.run(modal_api.check_auth()),
            "deployments": deployments,
            "total_deployments": len(deployments),
            "active_deployments": len([d for d in deployments if d.get("status") == "running"])
        }
    except Exception as e:
        logger.error(f"Failed to get Modal status: {e}")
        return {
            "authenticated": False,
            "deployments": [],
            "total_deployments": 0,
            "active_deployments": 0,
            "error": str(e)
        }


def deploy_to_modal(
    app_file: str | Path,
    mode: str = "optimized",
    timeout_minutes: int = 60,
    auto_auth: bool = True
) -> dict[str, any]:
    """
    Deploy a Gradio app to Modal synchronously.
    
    Args:
        app_file: Path to the Gradio app file
        mode: Deployment mode (minimum, optimized, gra_jupy)
        timeout_minutes: Auto-kill timeout in minutes
        auto_auth: Automatically handle authentication
    
    Returns:
        dict: Deployment result with success status and URL
    """
    app_path = Path(app_file)
    
    if not app_path.exists():
        return {
            "success": False,
            "error": f"App file not found: {app_path}"
        }
    
    try:
        # Run async deployment
        result = uvloop.run(_deploy_async(app_path, mode, timeout_minutes, auto_auth))
        return result
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def kill_deployment(app_name: str) -> bool:
    """
    Kill a specific Modal deployment synchronously.
    
    Args:
        app_name: Name of the app to kill
    
    Returns:
        bool: True if kill was successful
    """
    try:
        return uvloop.run(modal_api.kill_deployment(app_name))
    except Exception as e:
        logger.error(f"Failed to kill deployment {app_name}: {e}")
        return False


def list_deployments() -> list[dict[str, any]]:
    """
    List all active Modal deployments synchronously.
    
    Returns:
        list: List of deployment information
    """
    try:
        return uvloop.run(modal_api.list_deployments())
    except Exception as e:
        logger.error(f"Failed to list deployments: {e}")
        return []


def validate_app_file(app_file: str | Path) -> dict[str, any]:
    """
    Validate a Gradio app file for Modal deployment.
    
    Args:
        app_file: Path to the app file to validate
    
    Returns:
        dict: Validation result with recommendations
    """
    app_path = Path(app_file)
    
    if not app_path.exists():
        return {
            "valid": False,
            "error": f"File not found: {app_path}",
            "recommendations": ["Create the file first"]
        }
    
    if not app_path.suffix == ".py":
        return {
            "valid": False,
            "error": "File must be a Python file (.py)",
            "recommendations": ["Rename file with .py extension"]
        }
    
    try:
        content = app_path.read_text()
        
        # Check for Gradio imports
        has_gradio = "import gradio" in content or "from gradio" in content
        has_blocks = "gr.Blocks" in content or "gradio.Blocks" in content
        has_interface = "gr.Interface" in content or "gradio.Interface" in content
        has_launch = ".launch(" in content
        
        recommendations = []
        warnings = []
        
        if not has_gradio:
            recommendations.append("Add 'import gradio as gr' to your file")
        
        if not (has_blocks or has_interface):
            recommendations.append("Create a Gradio interface using gr.Blocks() or gr.Interface()")
        
        if not has_launch:
            warnings.append("Consider adding .launch() for local testing")
        
        # Check for common ML libraries
        ml_libraries = ["torch", "tensorflow", "transformers", "sklearn", "numpy", "pandas"]
        detected_ml = [lib for lib in ml_libraries if lib in content]
        
        if detected_ml:
            recommendations.append(f"Consider using 'optimized' mode for ML libraries: {', '.join(detected_ml)}")
        
        # Check for Jupyter-related imports
        jupyter_imports = ["jupyter", "notebook", "ipywidgets", "matplotlib", "plotly"]
        detected_jupyter = [lib for lib in jupyter_imports if lib in content]
        
        if detected_jupyter:
            recommendations.append("Consider using 'gra_jupy' mode for Jupyter features")
        
        return {
            "valid": has_gradio and (has_blocks or has_interface),
            "has_gradio": has_gradio,
            "has_interface": has_blocks or has_interface,
            "has_launch": has_launch,
            "detected_ml_libraries": detected_ml,
            "detected_jupyter": detected_jupyter,
            "recommendations": recommendations,
            "warnings": warnings,
            "suggested_mode": _suggest_deployment_mode(detected_ml, detected_jupyter)
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Failed to read file: {str(e)}",
            "recommendations": ["Check file permissions and content"]
        }


def _suggest_deployment_mode(ml_libraries: list[str], jupyter_libraries: list[str]) -> str:
    """Suggest the best deployment mode based on detected libraries."""
    if jupyter_libraries:
        return "gra_jupy"
    elif ml_libraries:
        return "optimized"
    else:
        return "minimum"


async def _deploy_async(
    app_path: Path,
    mode: str,
    timeout_minutes: int,
    auto_auth: bool
) -> dict[str, any]:
    """Internal async deployment function."""
    try:
        # Check authentication
        if auto_auth and not await modal_api.check_auth():
            logger.info("🔐 Setting up Modal authentication...")
            auth_success = await modal_api.setup_auth()
            if not auth_success:
                return {"success": False, "error": "Authentication failed"}
        
        # Deploy the app
        logger.info(f"🚀 Deploying {app_path.name} to Modal ({mode} mode)...")
        result = await modal_api.deploy_app(app_path, mode, timeout_minutes)
        
        if result.get("success"):
            logger.success(f"✅ Deployment successful: {result.get('url')}")
        else:
            logger.error(f"❌ Deployment failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Deployment error: {e}")
        return {"success": False, "error": str(e)}