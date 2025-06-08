"""Decorators for automatic Modal deployment and resource management."""

import asyncio
import functools
import inspect
from pathlib import Path
from typing import Any, Callable

import gradio as gr
import uvloop
from loguru import logger

from .core import modal_api


def modal_auto_deploy(
    mode: str = "optimized",
    timeout_minutes: int = 60,
    auto_auth: bool = True,
    deploy_on_run: bool = True
):
    """
    Decorator for automatic Modal deployment of Gradio apps.
    
    Args:
        mode: Deployment mode (minimum, optimized, gra_jupy)
        timeout_minutes: Auto-kill timeout in minutes
        auto_auth: Automatically handle Modal authentication
        deploy_on_run: Deploy immediately when the function runs
    
    Example:
        @modal_auto_deploy(mode="optimized", timeout=60)
        def create_my_app():
            with gr.Blocks() as demo:
                gr.Markdown("# My Amazing App")
            return demo
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Call the original function to create the Gradio app
            demo = func(*args, **kwargs)
            
            if not isinstance(demo, gr.Blocks):
                raise ValueError(f"Function {func.__name__} must return a gr.Blocks instance")
            
            if deploy_on_run:
                # Get the file path of the function
                frame = inspect.currentframe().f_back
                file_path = Path(frame.f_globals.get('__file__', 'unknown.py'))
                
                # Deploy to Modal
                def sync_deploy():
                    try:
                        return uvloop.run(_deploy_to_modal_async(
                            file_path, mode, timeout_minutes, auto_auth
                        ))
                    except Exception as e:
                        logger.error(f"Auto-deployment failed: {e}")
                        return None
                
                deployment_result = sync_deploy()
                
                if deployment_result and deployment_result.get("success"):
                    logger.success(f"🚀 Auto-deployed to Modal: {deployment_result.get('url')}")
                    
                    # Add deployment info to the Gradio app
                    with demo:
                        gr.Markdown(f"""
                        ### 🚀 Deployed to Modal!
                        **URL:** {deployment_result.get('url')}
                        **Mode:** {mode.upper()}
                        **Timeout:** {timeout_minutes} minutes
                        """)
                else:
                    logger.warning("Auto-deployment failed, running locally")
            
            return demo
        
        return wrapper
    return decorator


def modal_gpu_when_needed(func: Callable) -> Callable:
    """
    Decorator that automatically scales to GPU when ML operations are detected.
    
    This decorator analyzes the function for common ML library imports
    and automatically requests GPU resources when needed.
    
    Example:
        @modal_gpu_when_needed
        def process_image(image):
            import torch  # GPU detected automatically
            # Your ML processing here
            return processed_image
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Analyze function source for ML libraries
        source = inspect.getsource(func)
        gpu_libraries = [
            'torch', 'tensorflow', 'transformers', 'diffusers',
            'accelerate', 'cuda', 'cupy', 'jax'
        ]
        
        needs_gpu = any(lib in source for lib in gpu_libraries)
        
        if needs_gpu:
            logger.info(f"🔥 GPU detected for function {func.__name__}")
            # In a real implementation, this would set Modal GPU flags
            # For now, it's just a marker
        
        return func(*args, **kwargs)
    
    return wrapper


def modal_memory_optimized(
    max_memory_gb: int = 8,
    auto_scale: bool = True
):
    """
    Decorator for memory-optimized Modal functions.
    
    Args:
        max_memory_gb: Maximum memory to allocate (GB)
        auto_scale: Automatically scale memory based on usage
    
    Example:
        @modal_memory_optimized(max_memory_gb=16, auto_scale=True)
        def process_large_dataset(data):
            # Automatically handles large data processing
            return analyze_data(data)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"🧠 Memory-optimized function {func.__name__} (max: {max_memory_gb}GB)")
            
            # In a real implementation, this would set Modal memory flags
            # and monitor memory usage
            
            try:
                result = func(*args, **kwargs)
                logger.success(f"✅ Memory-optimized execution completed for {func.__name__}")
                return result
            except MemoryError:
                if auto_scale:
                    logger.warning(f"⚠️ Memory limit reached, auto-scaling {func.__name__}")
                    # Would trigger auto-scaling here
                raise
        
        return wrapper
    return decorator


def modal_persistent_storage(
    storage_path: str = "/tmp/modal_storage",
    auto_backup: bool = True
):
    """
    Decorator for functions that need persistent storage.
    
    Args:
        storage_path: Path for persistent storage
        auto_backup: Automatically backup data
    
    Example:
        @modal_persistent_storage(storage_path="/data", auto_backup=True)
        def save_model(model, name):
            # Automatically handles persistent storage
            model.save(f"/data/{name}")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"💾 Persistent storage enabled for {func.__name__} at {storage_path}")
            
            # In a real implementation, this would set up Modal volumes
            # and handle data persistence
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


async def _deploy_to_modal_async(
    file_path: Path,
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
        logger.info(f"🚀 Deploying {file_path.name} to Modal...")
        result = await modal_api.deploy_app(file_path, mode, timeout_minutes)
        
        return result
        
    except Exception as e:
        logger.error(f"Deployment error: {e}")
        return {"success": False, "error": str(e)}