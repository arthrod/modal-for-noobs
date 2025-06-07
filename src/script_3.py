# Now let's create the main CLI entry point

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
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Version info
__version__ = "1.0.0"

# Import components
from easy_modal.config import EasyModalConfig
from easy_modal.auth import ModalAuthenticator
from easy_modal.wrapper import GradioAppWrapper

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
            if ":" in api_key:
                token_id, token_secret = api_key.split(":", 1)
                authenticator.setup_authentication(token_id, token_secret)
            else:
                console.print("[red]✗[/red] Please provide both MODAL_TOKEN_ID and MODAL_TOKEN_SECRET")
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

print("Main CLI Entry Point (easy_modal/cli.py):")
print("=" * 60)
print(cli_main)

# Now let's create a sample Gradio app that we can use to test our CLI
sample_gradio_app = '''
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

print("\nSample Gradio App (sample_app.py):")
print("=" * 60)
print(sample_gradio_app)

# Let's also create a more complex Gradio app example
complex_gradio_app = '''
import gradio as gr
import numpy as np
from PIL import Image

# Simulated ML model
def process_image(image, enhancement_level, apply_filter):
    """Process an image with simulated ML effects"""
    # Convert to numpy array if it's a PIL Image
    if isinstance(image, Image.Image):
        img_array = np.array(image)
    else:
        img_array = image
        
    # Apply enhancement (brightness adjustment)
    enhanced = img_array * (enhancement_level / 5.0)
    enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
    
    # Apply filter if requested
    if apply_filter:
        # Simple edge detection filter
        from scipy.ndimage import sobel
        if len(enhanced.shape) == 3:  # Color image
            gray = np.mean(enhanced, axis=2).astype(np.uint8)
            edges = sobel(gray)
            # Normalize to 0-255
            edges = (edges / edges.max() * 255).astype(np.uint8)
            # Convert back to RGB
            enhanced = np.stack([edges, edges, edges], axis=2)
    
    return enhanced

# Create Blocks interface
with gr.Blocks(title="Image Processor") as demo:
    gr.Markdown("# Advanced Image Processing Demo")
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(label="Input Image", type="numpy")
            enhancement = gr.Slider(minimum=1, maximum=10, value=5, step=0.1, label="Enhancement Level")
            filter_checkbox = gr.Checkbox(label="Apply Edge Detection")
            process_btn = gr.Button("Process Image")
        
        with gr.Column():
            output_image = gr.Image(label="Processed Image")
            info_text = gr.Textbox(label="Processing Info", interactive=False)
    
    # Define processing function with info
    def process_with_info(image, level, apply_filter):
        if image is None:
            return None, "Please upload an image first"
        
        try:
            result = process_image(image, level, apply_filter)
            info = f"Processed with enhancement level {level}"
            if apply_filter:
                info += " and edge detection"
            return result, info
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    # Set up event handler
    process_btn.click(
        fn=process_with_info,
        inputs=[input_image, enhancement, filter_checkbox],
        outputs=[output_image, info_text]
    )
    
    # Add examples
    gr.Examples(
        examples=[
            ["https://images.unsplash.com/photo-1507608616759-54f48f0af0ee", 5.0, False],
            ["https://images.unsplash.com/photo-1682687982501-1e58ab814714", 7.0, True],
        ],
        inputs=[input_image, enhancement, filter_checkbox]
    )

# Only launch if running directly
if __name__ == "__main__":
    demo.launch()
'''

print("\nComplex Gradio App Example (complex_app.py):")
print("=" * 60)
print(complex_gradio_app)

# Let's create a README for our tool
readme = '''# Easy Modal CLI

A fully working, idiot-proof, out-of-the-box Gradio component CLI for Modal deployment.

## Installation

```bash
pip install easy-modal
```

## Usage

### Quick Start

Deploy a Gradio app to Modal with minimal configuration:

```bash
easy-modal deploy your_gradio_app.py
```

### Deployment Options

- **Minimum Mode** (default): Basic CPU-only deployment with essential dependencies
  ```bash
  easy-modal --minimum your_gradio_app.py
  ```

- **Optimized Mode**: GPU-enabled deployment with ML libraries
  ```bash
  easy-modal --optimized your_gradio_app.py
  ```

- **Step-by-Step Wizard**: Interactive guided configuration
  ```bash
  easy-modal --step-by-step your_gradio_app.py
  ```

### Authentication

Set up Modal authentication:

```bash
easy-modal auth
```

Or provide your API token directly:

```bash
easy-modal deploy your_gradio_app.py --api-key YOUR_TOKEN_ID:YOUR_TOKEN_SECRET
```

### Configuration

Generate a sample configuration file:

```bash
easy-modal config --generate
```

## Features

- Automatic Modal authentication setup
- Volume and Secret management
- Image configuration with appropriate dependencies
- ASGI app mounting for Gradio
- Queue and concurrency setup
- Single container deployment for sticky sessions

## Requirements

- Python 3.9+
- Gradio 4.0+
- Modal 0.57+
'''

print("\nREADME.md:")
print("=" * 60)
print(readme)