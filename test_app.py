"""Simple test Gradio app for testing modal-for-noobs deployment."""

import gradio as gr


def greet(name):
    """Greet function for testing."""
    return f"Hello {name}! 🚀 Deployed with modal-for-noobs!"


# Create the Gradio interface
demo = gr.Interface(
    fn=greet,
    inputs=gr.Textbox(label="Your Name", placeholder="Enter your name here..."),
    outputs=gr.Textbox(label="Greeting"),
    title="🚀 Modal for Noobs Test App",
    description="A simple test app to verify modal-for-noobs deployment works perfectly!",
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    demo.launch(strict_cors=False)  # Allow localhost, HuggingFace, and Modal cross-origin requests