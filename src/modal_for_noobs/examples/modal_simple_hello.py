import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("modal-for-noobs-simple_hello")

# Configure image

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio",
    "fastapi[standard]",
    "uvicorn",
    "httpx",
    "markdown2"
)

# Original Gradio app code embedded
"""
👋 Simple Hello World - Your first Modal app that says hello with Modal green styling!
"""

import gradio as gr

# Modal's signature green theme! 💚
MODAL_GREEN = "#00D26A"
MODAL_LIGHT_GREEN = "#4AE88A"

# Custom CSS with Modal theme
modal_css = f"""
.gradio-container {{
    background: linear-gradient(135deg, {MODAL_GREEN}15 0%, {MODAL_LIGHT_GREEN}15 100%);
}}

.gr-button {{
    background: linear-gradient(135deg, {MODAL_GREEN} 0%, {MODAL_LIGHT_GREEN} 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px {MODAL_GREEN}40 !important;
}}

.gr-button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px {MODAL_GREEN}60 !important;
}}

h1 {{
    color: {MODAL_GREEN} !important;
    text-align: center !important;
}}
"""

def greet(name):
    """Greet function with Modal styling."""
    if not name.strip():
        return "👋 Hello! Please enter your name!"
    
    return f"🚀💚 Hello {name}! Welcome to Modal-for-noobs! 💚🚀"

# Create interface
demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="What's your name?", placeholder="Enter your name here..."),
    outputs=gr.Textbox(label="Modal Greeting"),
    title="🚀💚 Modal Hello World 💚🚀",
    description="Your first Modal app - beautifully styled with Modal green theme!",
    css=modal_css,
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    demo.launch()

@app.function(
    image=image,
    min_containers=1,
    max_containers=1,  # Single container for sticky sessions
    timeout=3600,
    scaledown_window=1200
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