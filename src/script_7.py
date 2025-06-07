# Let me create the files using proper string escaping and formatting

# Create the main CLI implementation
cli_code = '''#!/usr/bin/env python3
"""
Easy Modal CLI - Complete working example
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
        image_config = """
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio>=4.0.0",
    "fastapi[standard]>=0.100.0",
    "uvicorn>=0.20.0"
)"""
    else:  # optimized
        image_config = """
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

    # GPU configuration
    gpu_line = '    gpu="any",' if mode == "optimized" else ""
    
    # Generate deployment code
    deployment_template = f"""
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
    '''Deploy Gradio app with Modal'''
    
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
"""
    
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
    print("\\nDeploying to Modal...")
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
'''

# Create a test Gradio app
test_gradio_app = '''
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
    title="Easy Modal Test App",
    description="A simple greeting application for testing easy-modal CLI"
)

if __name__ == "__main__":
    demo.launch()
'''

# Create pyproject.toml
pyproject_content = '''
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
'''

# Create setup instructions
setup_instructions = '''
# Easy Modal CLI - Setup and Usage Instructions

## Installation

### Method 1: From Source (Development)
```bash
git clone https://github.com/your-org/easy-modal
cd easy-modal
pip install -e .
```

### Method 2: From PyPI (Future)
```bash
pip install easy-modal
```

## Quick Start

### 1. Create a Gradio App
Create a file called `my_app.py`:

```python
import gradio as gr

def process_text(text):
    return f"Processed: {text.upper()}"

demo = gr.Interface(
    fn=process_text,
    inputs=gr.Textbox(label="Input"),
    outputs=gr.Textbox(label="Output"),
    title="My Gradio App"
)

if __name__ == "__main__":
    demo.launch()
```

### 2. Deploy to Modal
```bash
# Basic deployment (CPU only)
easy-modal deploy my_app.py

# Optimized deployment (GPU + ML libraries)
easy-modal deploy --optimized my_app.py

# Dry run (generate files without deploying)
easy-modal deploy --dry-run my_app.py
```

## Authentication

### Setup Modal Authentication
```bash
easy-modal auth
```

This will run `modal setup` to configure your Modal credentials.

### Alternative: Environment Variables
```bash
export MODAL_TOKEN_ID=your_token_id
export MODAL_TOKEN_SECRET=your_token_secret
easy-modal deploy my_app.py
```

## How It Works

1. **Authentication Check**: Verifies Modal credentials
2. **App Analysis**: Finds your Gradio interface (demo, app, interface, etc.)
3. **Image Configuration**: Sets up Docker image with dependencies
4. **Code Generation**: Creates `modal_yourapp.py` deployment file
5. **Modal Deploy**: Runs `modal deploy` and returns live URL

## Key Features

- **Zero Configuration**: Works out of the box
- **Smart Detection**: Automatically finds Gradio interfaces
- **Proper Integration**: Uses `mount_gradio_app` for FastAPI
- **Session Support**: Single container for sticky sessions
- **Queue Management**: Handles concurrent users
- **GPU Support**: Optional GPU deployment mode

## Generated Deployment File

When you run `easy-modal deploy my_app.py`, it creates `modal_my_app.py`:

```python
import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

app = modal.App("easy-modal-gradio-my_app")

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio>=4.0.0",
    "fastapi[standard]>=0.100.0",
    "uvicorn>=0.20.0"
)

@app.function(
    image=image,
    min_containers=1,
    max_containers=1,  # Single container for sticky sessions
    timeout=3600,
    scaledown_window=60 * 20
)
@modal.concurrent(max_inputs=100)
@modal.asgi_app()
def deploy_gradio():
    import sys
    from pathlib import Path
    
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    import my_app
    demo = my_app.demo
    demo.queue(max_size=10)
    
    fastapi_app = FastAPI(title="Easy Modal Gradio App")
    return mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    app.run()
```

## Best Practices

1. **Name your Gradio interface**: Use `demo`, `app`, or `interface` as variable names
2. **Keep dependencies minimal**: Use `--minimum` for faster deployments
3. **Use GPU mode for ML**: Use `--optimized` for ML workloads
4. **Test locally first**: Run your Gradio app locally before deploying

## Troubleshooting

### Common Issues

1. **"Could not find Gradio interface"**
   - Ensure your app defines a variable like `demo`, `app`, or `interface`
   - Check that the variable has `launch()` and `queue()` methods

2. **"Modal authentication failed"**
   - Run `easy-modal auth` to set up credentials
   - Check that Modal CLI is installed: `pip install modal`

3. **"Deployment failed"**
   - Verify your Gradio app runs locally
   - Check Modal service status
   - Try `--dry-run` to debug generated code

### Getting Help

- Check the logs in the Modal dashboard
- Run with `--dry-run` to inspect generated files
- Ensure all dependencies are compatible
'''

# Print everything
print("Easy Modal CLI - Complete Implementation")
print("=" * 60)
print("\nMain CLI Code (easy_modal_cli.py):")
print("-" * 40)
print(cli_code)

print("\nTest Gradio App (test_app.py):")
print("-" * 40)
print(test_gradio_app)

print("\nPyproject.toml:")
print("-" * 40)
print(pyproject_content)

print("\nSetup Instructions:")
print("-" * 40)
print(setup_instructions)