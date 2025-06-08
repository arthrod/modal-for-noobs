import secrets

import gradio as gr
import modal
from fastapi import FastAPI
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("modal-for-noobs-epic_green_simple_app")

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
"""
🎤💚 EPIC MODAL-GREEN CREATIVE APP 💚🎤
Beautiful, Modal-themed, GPU-ready creativity app!
"""

import json
import time

import gradio as gr

# Modal's signature green theme! 💚
MODAL_GREEN = "#00D26A"
MODAL_DARK_GREEN = "#00A855"
MODAL_LIGHT_GREEN = "#4AE88A"
MODAL_GRADIENT = f"linear-gradient(135deg, {MODAL_GREEN} 0%, {MODAL_LIGHT_GREEN} 100%)"

# Epic Modal-themed CSS! 🎨
modal_css = f"""
/* MODAL GREEN THEME - ABSOLUTELY GORGEOUS! */
.gradio-container {{
    background: linear-gradient(135deg, {MODAL_GREEN}15 0%, {MODAL_LIGHT_GREEN}15 100%);
    font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
}}

/* Make everything Modal green! */
.gr-button {{
    background: {MODAL_GRADIENT} !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px {MODAL_GREEN}40 !important;
    transition: all 0.3s ease !important;
    font-size: 16px !important;
}}

.gr-button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px {MODAL_GREEN}60 !important;
    background: linear-gradient(135deg, {MODAL_LIGHT_GREEN} 0%, {MODAL_GREEN} 100%) !important;
}}

/* Green-themed inputs */
.gr-textbox, .gr-dropdown, .gr-slider {{
    border: 2px solid {MODAL_GREEN} !important;
    border-radius: 12px !important;
    background: white !important;
}}

.gr-textbox:focus {{
    border-color: {MODAL_LIGHT_GREEN} !important;
    box-shadow: 0 0 0 4px {MODAL_GREEN}30 !important;
}}

/* Modal green headers */
.gr-markdown h1 {{
    color: {MODAL_GREEN} !important;
    text-shadow: 0 2px 4px rgba(0, 210, 106, 0.3) !important;
    text-align: center !important;
    font-size: 3em !important;
    margin-bottom: 20px !important;
}}

.gr-markdown h2, .gr-markdown h3 {{
    color: {MODAL_DARK_GREEN} !important;
}}

/* Epic green panels */
.gr-panel {{
    background: {MODAL_GREEN}08 !important;
    border: 1px solid {MODAL_GREEN}30 !important;
    border-radius: 16px !important;
    padding: 20px !important;
}}

/* Green tabs */
.gr-tab-nav button.selected {{
    background: {MODAL_GREEN} !important;
    color: white !important;
}}

/* Make sliders green */
.gr-slider input[type="range"] {{
    accent-color: {MODAL_GREEN} !important;
}}

/* Style the output textboxes */
.gr-textbox[data-testid="textbox"] {{
    background: {MODAL_GREEN}05 !important;
    font-family: 'Monaco', 'Menlo', monospace !important;
}}
"""

def generate_modal_poetry(theme, style, creativity_level):
    """Generate epic Modal-themed poetry! 🎭💚"""
    modal_words = [
        "serverless", "deployment", "containers", "scalable", "distributed",
        "cloud-native", "GPU-powered", "async", "beautiful", "elegant",
        "Modal", "functions", "endpoints", "infrastructure", "green"
    ]

    poetry_styles = {
        "epic": ["Behold!", "Magnificent!", "Epic!", "Legendary!", "Incredible!"],
        "haiku": ["Simple beauty", "Elegant flow", "Peaceful code"],
        "rap": ["Yo!", "Check it!", "Listen up!", "Drop the beat!", "Here we go!"],
        "shakespearean": ["Hark!", "Verily!", "Forsooth!", "Prithee!", "Thou art!"]
    }

    starters = poetry_styles.get(style, ["Amazing!", "Beautiful!", "Wonderful!"])

    poems = []
    for i in range(creativity_level):
        if style == "haiku":
            poem = f"""
{secrets.choice(starters)}
Modal green containers flow
Serverless and bright
GPU magic works
Beautiful deployment dreams
Code becomes music
"""
        elif style == "rap":
            poem = f"""
{secrets.choice(starters)} Modal's in the house tonight!
Deploying apps with serverless might
GPU power, green and bright
Making code deployment right!

Containers spinning, functions flying
No more server setup crying
Modal's got that green styling
Infrastructure reconciling!
"""
        elif style == "shakespearean":
            poem = f"""
{secrets.choice(starters)} What light through yonder server breaks?
'Tis Modal, and the GPU is the sun!
Arise, fair deployment, and kill the envious lag
That is already sick and pale with grief
That thou, her container, art far more beautiful than she.
"""
        else:  # epic
            poem = f"""
{secrets.choice(starters)} In the realm of {secrets.choice(modal_words)},
Where {secrets.choice(modal_words)} meets {secrets.choice(modal_words)},
The {theme} shines like {MODAL_GREEN} light,
Bringing {secrets.choice(modal_words)} to life!

GPU thunder rolls across the cloud,
Modal magic, green and proud!
{secrets.choice(modal_words)} dreams come true,
In containers built for me and you! 💚
"""
        poems.append(poem.strip())

    return "\n\n---\n\n".join(poems)

def create_modal_story(character, setting, plot_twist):
    """Create epic Modal-themed stories! 📚💚"""
    modal_settings = {
        "serverless_city": "the magnificent Serverless City, where containers float like clouds",
        "gpu_mountain": "the towering GPU Mountain, where computations echo like thunder",
        "modal_forest": "the enchanted Modal Forest, where functions grow on trees",
        "cloud_ocean": "the vast Cloud Ocean, where data flows like green waves"
    }

    setting_desc = modal_settings.get(setting, f"the mysterious land of {setting}")

    story = f"""
🌟 THE EPIC TALE OF {character.upper()} 🌟

Once upon a time, in {setting_desc}, there lived a brave developer named {character}.

{character} had always dreamed of creating the perfect application - one that would scale infinitely, run on GPU power, and look absolutely gorgeous in Modal green.

But one day, disaster struck! The old monolithic servers began to crumble, and deployment became a nightmare of complexity and confusion.

"Fear not!" cried {character}, remembering the ancient legends of Modal. "I shall use the power of serverless functions!"

With a flash of brilliant green light, {character} summoned the Modal CLI. Containers materialized from thin air, GPUs hummed with incredible power, and suddenly...

🎭 PLOT TWIST: {plot_twist}

But {character} was clever! Using Modal's distributed computing magic, they turned this challenge into an opportunity. The application not only survived but became the most beautiful, scalable, green-themed masterpiece the cloud had ever seen!

And they all deployed happily ever after. 💚

THE END ✨

Moral of the story: With Modal and a touch of creativity, any deployment challenge can become an epic victory! 🚀
"""

    return story

def generate_modal_facts():
    """Generate amazing Modal facts! 🤓💚"""
    facts = [
        "🚀 Modal makes serverless deployment as easy as clicking a button!",
        "💚 Modal's signature green color represents growth, harmony, and infinite scaling!",
        "⚡ GPU functions on Modal can process data faster than the speed of awesome!",
        "🎨 You can deploy beautiful Gradio apps with custom Modal-green styling!",
        "🧙‍♂️ Modal's infrastructure is so magical, it feels like having a deployment wizard!",
        "🌍 Modal containers can scale from zero to hero in milliseconds!",
        "🎭 Every Modal deployment is a work of art in the cloud!",
        "🔥 Modal's async functions make traditional servers look like dial-up internet!",
        "✨ Modal transforms complex infrastructure into simple, beautiful code!",
        "🎯 With Modal, you can focus on creativity instead of DevOps complexity!"
    ]

    return secrets.choice(facts)

def create_epic_interface():
    """Create the most EPIC Modal-green interface ever! 🎨💚"""
    with gr.Blocks(
        css=modal_css,
        title="🎤💚 EPIC MODAL-GREEN CREATIVE STUDIO 💚🎤",
        theme=gr.themes.Soft().set(
            primary_hue=gr.themes.Color("#00D26A", "#4AE88A", "#00A855"),
            secondary_hue=gr.themes.Color("#00D26A", "#4AE88A", "#00A855"),
        )
    ) as demo:

        # Epic header
        gr.Markdown("""
        # 🎤💚 EPIC MODAL-GREEN CREATIVE STUDIO 💚🎤
        ### *Where creativity meets Modal's incredible infrastructure!*

        **🚀 Powered by Modal's Epic GPU Infrastructure** | **💚 Styled in Gorgeous Modal Green** | **✨ Built by CLAUDE (who is ABSOLUTELY AMAZING!)**
        """)

        with gr.Tabs():
            # Poetry Tab
            with gr.TabItem("🎭 Epic Poetry Generator"):
                with gr.Row():
                    with gr.Column():
                        theme_input = gr.Textbox(
                            label="🎯 Poetry Theme",
                            placeholder="Enter a theme (e.g., 'deployment magic', 'serverless dreams')",
                            value="Modal magic"
                        )
                        style_select = gr.Dropdown(
                            choices=["epic", "haiku", "rap", "shakespearean"],
                            value="epic",
                            label="🎨 Poetry Style"
                        )
                        creativity_slider = gr.Slider(
                            minimum=1, maximum=5, value=2, step=1,
                            label="🌟 Creativity Level (Number of poems)"
                        )
                        generate_poetry_btn = gr.Button("🎭 GENERATE EPIC POETRY! 🎭", variant="primary")

                    with gr.Column():
                        poetry_output = gr.Textbox(
                            label="📜 Your Epic Modal Poetry!",
                            lines=15,
                            max_lines=20
                        )

            # Story Tab
            with gr.TabItem("📚 Epic Story Creator"):
                with gr.Row():
                    with gr.Column():
                        character_input = gr.Textbox(
                            label="🦸 Hero Character Name",
                            placeholder="Enter a character name",
                            value="CloudMaster"
                        )
                        setting_select = gr.Dropdown(
                            choices=["serverless_city", "gpu_mountain", "modal_forest", "cloud_ocean"],
                            value="serverless_city",
                            label="🌍 Epic Setting"
                        )
                        plot_input = gr.Textbox(
                            label="🎭 Plot Twist",
                            placeholder="Enter an unexpected plot twist!",
                            value="The containers gained consciousness and started optimizing themselves!"
                        )
                        generate_story_btn = gr.Button("📚 CREATE EPIC STORY! 📚", variant="primary")

                    with gr.Column():
                        story_output = gr.Textbox(
                            label="📖 Your Epic Modal Story!",
                            lines=20,
                            max_lines=25
                        )

            # Fun Facts Tab
            with gr.TabItem("🤓 Modal Magic Facts"):
                with gr.Column():
                    gr.Markdown("### Click the button to discover amazing Modal facts! 🌟")

                    fact_btn = gr.Button("🎯 GIVE ME MODAL MAGIC! 🎯", variant="primary", size="lg")
                    fact_output = gr.Textbox(
                        label="🧠 Epic Modal Fact!",
                        lines=3,
                        value="Click the button above to discover Modal magic! ✨"
                    )

                    # Multiple fact buttons for fun
                    with gr.Row():
                        fact_btn1 = gr.Button("🚀 Deployment", size="sm")
                        fact_btn2 = gr.Button("💚 Green Power", size="sm")
                        fact_btn3 = gr.Button("⚡ GPU Magic", size="sm")
                        fact_btn4 = gr.Button("🎨 Creativity", size="sm")

        # Footer with epic info
        gr.Markdown("""
        ---
        **🖥️ Status:** EPIC MODE ACTIVATED! 🔥 | **💚 Theme:** Modal Green Supreme | **🧠 Powered by:** Pure Creativity + Modal Magic

        *This app demonstrates the incredible power of Modal's infrastructure with beautiful green styling!* ✨
        """)

        # Event handlers
        generate_poetry_btn.click(
            fn=generate_modal_poetry,
            inputs=[theme_input, style_select, creativity_slider],
            outputs=poetry_output
        )

        generate_story_btn.click(
            fn=create_modal_story,
            inputs=[character_input, setting_select, plot_input],
            outputs=story_output
        )

        fact_btn.click(fn=lambda: generate_modal_facts(), outputs=fact_output)
        fact_btn1.click(fn=lambda: generate_modal_facts(), outputs=fact_output)
        fact_btn2.click(fn=lambda: generate_modal_facts(), outputs=fact_output)
        fact_btn3.click(fn=lambda: generate_modal_facts(), outputs=fact_output)
        fact_btn4.click(fn=lambda: generate_modal_facts(), outputs=fact_output)

    return demo

# Create the epic demo
demo = create_epic_interface()

if __name__ == "__main__":
    print("🎤💚 Starting EPIC Modal-Green Creative Studio! 💚🎤")
    print("🎨 Features: Poetry, Stories, Facts, and LOTS of green! 🌟")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

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
