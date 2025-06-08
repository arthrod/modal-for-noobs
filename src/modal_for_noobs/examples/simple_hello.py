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