# Let me fix the syntax error and create the CLI module properly

# First, let's create the deployment template separately
deployment_template = '''
import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("easy-modal-gradio-{app_name}")

# Configure image
{image_config}

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
    
    # Import the original Gradio app
    import sys
    from pathlib import Path
    
    # Add the directory containing the original app to Python path
    app_dir = Path(__file__).parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    
    # Import and execute the original app code
    {original_code_import}
    
    # Enable queuing for concurrent requests
    demo.queue(max_size=10)
    
    # Mount Gradio app to FastAPI
    fastapi_app = FastAPI(title="Easy Modal Gradio App")
    return mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    # For local testing
    app.run()
'''

print("Deployment Template:")
print(deployment_template)

# Now create the main CLI components
cli_components = {
    "config_manager": '''
class EasyModalConfig:
    """Configuration management for Easy Modal"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".easy-modal"
        self.config_file = self.config_dir / "config.yaml"
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save_config(self, config: Dict[str, Any]):
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
''',
    
    "authenticator": '''
class ModalAuthenticator:
    """Handle Modal authentication"""
    
    def __init__(self):
        self.config = EasyModalConfig()
    
    def check_authentication(self) -> bool:
        try:
            if os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"):
                return True
            
            modal_config = Path.home() / ".modal.toml"
            if modal_config.exists():
                return True
                
            return False
        except Exception:
            return False
    
    def setup_authentication(self, token_id: Optional[str] = None, token_secret: Optional[str] = None):
        if token_id and token_secret:
            os.environ["MODAL_TOKEN_ID"] = token_id
            os.environ["MODAL_TOKEN_SECRET"] = token_secret
            print("✓ Modal authentication configured via environment variables")
        else:
            try:
                subprocess.run(["modal", "setup"], check=True)
                print("✓ Modal authentication setup complete")
            except subprocess.CalledProcessError:
                print("✗ Failed to setup Modal authentication")
                sys.exit(1)
''',
    
    "app_wrapper": '''
class GradioAppWrapper:
    """Wrap and prepare Gradio apps for Modal deployment"""
    
    def __init__(self, app_file: Path, mode: str = "minimum"):
        self.app_file = app_file
        self.mode = mode
        self.deployment_file = self.app_file.parent / f"modal_{self.app_file.stem}.py"
    
    def get_image_config(self) -> str:
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
    
    def create_deployment_file(self):
        # Read original app code
        with open(self.app_file, 'r') as f:
            original_code = f.read()
        
        # Prepare import statement
        module_name = self.app_file.stem
        original_code_import = f"""
    # Import the original gradio app
    import {module_name}
    
    # Try to find the demo object
    demo = None
    for attr_name in dir({module_name}):
        attr = getattr({module_name}, attr_name)
        if hasattr(attr, 'queue') and hasattr(attr, 'launch'):
            demo = attr
            break
    
    if demo is None:
        raise ValueError("Could not find Gradio interface in {module_name}")
"""
        
        # Configure GPU
        gpu_config = 'gpu="any",' if self.mode == "optimized" else ""
        
        # Generate deployment code
        deployment_code = f"""
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
    \"\"\"Deploy Gradio app with Modal\"\"\"
    
    import sys
    from pathlib import Path
    
    # Add current directory to path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
{original_code_import}
    
    # Enable queuing for concurrent requests
    demo.queue(max_size=10)
    
    # Mount Gradio app to FastAPI
    fastapi_app = FastAPI(title="Easy Modal Gradio App")
    return mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    app.run()
"""
        
        # Write deployment file
        with open(self.deployment_file, 'w') as f:
            f.write(deployment_code)
        
        print(f"✓ Created deployment file: {self.deployment_file}")
        return self.deployment_file
'''
}

print("\nCLI Components:")
for name, component in cli_components.items():
    print(f"\n{name.upper()}:")
    print("=" * 40)
    print(component)