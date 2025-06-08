import gradio as gr
import modal
from fastapi import FastAPI
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("modal-for-noobs-test_gradio_app")

# Configure image

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
)

# Original Gradio app code embedded
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

@app.function(
    image=image,    gpu="any",
    min_containers=1,
    max_containers=1,  # Single container for sticky sessions
    timeout=3600,
    scaledown_window=60 * 20
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
