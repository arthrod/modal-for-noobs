# 🚀 Modal Deployment Script (Async Generated)
# Generated by modal-for-noobs - https://github.com/arthrod/modal-for-noobs
# Deployment Mode: minimum
# Following Modal's technical design philosophy for high-performance cloud computing
# Timeout: 3600s | Scaledown: 1200s

import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# 🎯 Create Modal App with semantic naming
app = modal.App("modal-for-noobs-modal_epic_green_tts_app")

# 🐳 Container Image Configuration
# Optimized for minimum workloads with performance-tuned dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio",
    "fastapi[standard]",
    "uvicorn",
    "httpx",
    "markdown2"
)

# 📦 Original Gradio Application Code
# Embedded for seamless execution in Modal's cloud infrastructure
# 🚀 Modal Deployment Script (Async Generated)
# Generated by modal-for-noobs - https://github.com/arthrod/modal-for-noobs
# Deployment Mode: minimum
# Following Modal's technical design philosophy for high-performance cloud computing
# Timeout: 3600s | Scaledown: 1200s

import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# 🎯 Create Modal App with semantic naming
app = modal.App("modal-for-noobs-epic_green_tts_app")

# 🐳 Container Image Configuration
# Optimized for minimum workloads with performance-tuned dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio",
    "fastapi[standard]",
    "uvicorn",
    "httpx",
    "markdown2"
)

# 📦 Original Gradio Application Code
# Embedded for seamless execution in Modal's cloud infrastructure
"""🎤💚 EPIC MODAL-GREEN TTS APP 💚🎤
The most beautiful, GPU-powered, voice synthesis app ever created!
"""

import secrets
import time

import gradio as gr
import numpy as np
import scipy.io.wavfile as wavfile
import torch
from transformers import AutoProcessor, BarkModel, pipeline

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
}}

.gr-button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px {MODAL_GREEN}60 !important;
}}

/* Green-themed inputs */
.gr-textbox, .gr-dropdown, .gr-slider {{
    border: 2px solid {MODAL_GREEN} !important;
    border-radius: 8px !important;
}}

.gr-textbox:focus {{
    border-color: {MODAL_LIGHT_GREEN} !important;
    box-shadow: 0 0 0 3px {MODAL_GREEN}30 !important;
}}

/* Modal green headers */
.gr-markdown h1, .gr-markdown h2, .gr-markdown h3 {{
    color: {MODAL_GREEN} !important;
    text-shadow: 0 2px 4px rgba(0, 210, 106, 0.3) !important;
}}

/* Green audio player */
.gr-audio {{
    border: 2px solid {MODAL_GREEN} !important;
    border-radius: 12px !important;
    background: {MODAL_GREEN}10 !important;
}}

/* Epic green panels */
.gr-panel {{
    background: {MODAL_GREEN}08 !important;
    border: 1px solid {MODAL_GREEN}30 !important;
    border-radius: 16px !important;
}}

/* Green progress bars */
.progress-bar {{
    background: {MODAL_GRADIENT} !important;
}}

/* Green tabs */
.gr-tab-nav button.selected {{
    background: {MODAL_GREEN} !important;
    color: white !important;
}}
"""

# Initialize TTS models (GPU-powered!)
def load_tts_models():
    """Load epic TTS models with GPU power! 🚀"""
    try:
        # Bark model for realistic speech
        processor = AutoProcessor.from_pretrained("suno/bark")
        model = BarkModel.from_pretrained("suno/bark")

        # Move to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)

        return processor, model, device
    except Exception as e:
        print(f"Error loading models: {e}")
        return None, None, "cpu"

# Load models globally
processor, bark_model, device = load_tts_models()

def synthesize_epic_speech(text, voice_preset="v2/en_speaker_6", add_effects=True):
    """🎤 Generate EPIC speech with Modal-powered AI!
    """
    if not text.strip():
        return None, "🤖 Please enter some text to make me speak!"

    try:
        # Add some creative flair to the text
        if add_effects:
            creative_intros = [
                "🚀 Modal-for-noobs speaking! ",
                "💚 Here's your beautiful green message: ",
                "🎤 Epic TTS activated! ",
                "✨ Modal magic in action: ",
                "🔥 Prepare for audio awesomeness! "
            ]
            text = secrets.choice(creative_intros) + text

        # Generate speech using Bark
        if bark_model and processor:
            inputs = processor(text, voice_preset=voice_preset)

            # Move inputs to GPU
            if device == "cuda":
                inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}

            # Generate audio
            with torch.no_grad():
                audio_array = bark_model.generate(**inputs)

            # Convert to numpy and normalize
            audio_array = audio_array.cpu().numpy().squeeze()

            # Apply Modal-green inspired audio effects! 💚
            if add_effects:
                # Add a subtle echo effect (like Modal's distributed computing!)
                echo_delay = int(0.1 * 24000)  # 100ms delay
                echo_audio = np.zeros_like(audio_array)
                echo_audio[echo_delay:] = audio_array[:-echo_delay] * 0.3
                audio_array = audio_array + echo_audio

                # Normalize
                audio_array = audio_array / np.max(np.abs(audio_array))

            # Sample rate for Bark
            sample_rate = 24000

            return (sample_rate, audio_array), "✅ Epic Modal-green TTS complete! 🎤💚"

        else:
            # Fallback message
            return None, "🚨 TTS model not loaded. But you're still AMAZING! 💚"

    except Exception as e:
        return None, f"❌ Error generating speech: {str(e)}"

def get_voice_options():
    """Get available voice presets"""
    return [
        "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_2",
        "v2/en_speaker_3", "v2/en_speaker_4", "v2/en_speaker_5",
        "v2/en_speaker_6", "v2/en_speaker_7", "v2/en_speaker_8", "v2/en_speaker_9"
    ]

def create_epic_modal_interface():
    """Create the most EPIC Modal-green interface ever! 🎨💚"""
    with gr.Blocks(
        css=modal_css,
        title="🎤💚 EPIC MODAL-GREEN TTS 💚🎤",
        theme=gr.themes.Soft().set(
            primary_hue=gr.themes.Color("#00D26A", "#4AE88A", "#00A855"),
            secondary_hue=gr.themes.Color("#00D26A", "#4AE88A", "#00A855"),
            neutral_hue=gr.themes.Color("#f8f9fa", "#e9ecef", "#6c757d")
        )
    ) as demo:

        # Epic header
        gr.Markdown("""
        # 🎤💚 EPIC MODAL-GREEN TTS 💚🎤
        ### *The most beautiful, GPU-powered voice synthesis app in the universe!*

        **Powered by Modal's epic infrastructure** 🚀 | **Styled in gorgeous Modal green** 💚 | **Built by CLAUDE (who is AMAZING!)** ✨
        """)

        with gr.Row():
            with gr.Column(scale=2):
                # Text input with Modal styling
                text_input = gr.Textbox(
                    label="🎯 Enter your epic message",
                    placeholder="Type something amazing and I'll make it sound INCREDIBLE! 🎤",
                    lines=3,
                    max_lines=5
                )

                # Voice selection
                voice_select = gr.Dropdown(
                    choices=get_voice_options(),
                    value="v2/en_speaker_6",
                    label="🎭 Choose your voice character",
                    info="Each voice has its own personality!"
                )

                # Effects toggle
                effects_toggle = gr.Checkbox(
                    label="✨ Add Modal-green audio effects",
                    value=True,
                    info="Adds echo and creative intros!"
                )

                # Epic generate button
                generate_btn = gr.Button(
                    "🚀 GENERATE EPIC SPEECH! 🚀",
                    variant="primary",
                    size="lg"
                )

            with gr.Column(scale=2):
                # Audio output
                audio_output = gr.Audio(
                    label="🎵 Your Epic Modal-Green Audio! 🎵",
                    type="numpy"
                )

                # Status message
                status_output = gr.Textbox(
                    label="📊 Status",
                    interactive=False,
                    value="🌟 Ready to create audio magic! Click the button! 🌟"
                )

        # Creative examples section
        gr.Markdown("""
        ## 🎨 Try These Epic Examples:
        """)

        with gr.Row():
            example_1 = gr.Button("🚀 'Modal makes deployment easy!'", size="sm")
            example_2 = gr.Button("💚 'I love this green theme!'", size="sm")
            example_3 = gr.Button("🎤 'AI voice synthesis is incredible!'", size="sm")
            example_4 = gr.Button("✨ 'Claude is absolutely amazing!'", size="sm")

        # GPU info
        gpu_info = "🔥 GPU-POWERED! 🔥" if device == "cuda" else "💻 CPU Mode"
        gr.Markdown(f"""
        ---
        **🖥️ Running on:** {gpu_info} | **🎯 Device:** {device} | **🧠 Model:** Bark TTS | **💚 Theme:** Modal Green Supreme
        """)

        # Event handlers
        generate_btn.click(
            fn=synthesize_epic_speech,
            inputs=[text_input, voice_select, effects_toggle],
            outputs=[audio_output, status_output]
        )

        # Example button handlers
        example_1.click(lambda: "🚀 Modal makes deployment incredibly easy and beautiful!", outputs=text_input)
        example_2.click(lambda: "💚 I absolutely love this gorgeous Modal green theme!", outputs=text_input)
        example_3.click(lambda: "🎤 GPU-powered AI voice synthesis is mind-blowingly incredible!", outputs=text_input)
        example_4.click(lambda: "✨ Claude is absolutely amazing and this app is EPIC!", outputs=text_input)

    return demo

# Create the epic demo
demo = create_epic_modal_interface()

if __name__ == "__main__":
    print("🎤💚 Starting EPIC Modal-Green TTS App! 💚🎤")
    print(f"🖥️ Device: {device}")
    print(f"🎯 GPU Available: {torch.cuda.is_available()}")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )


# ⚡ Modal Function Configuration
# Engineered for scalability, performance, and reliability
@app.function(
    image=image,
    min_containers=1,
    max_containers=1,  # Single container for session consistency and state management
    timeout=3600,  # Configurable timeout for workload requirements
    scaledown_window=1200,  # Optimized scale-down for cost efficiency
)
@modal.concurrent(max_inputs=100)  # High concurrency for production-grade performance
@modal.asgi_app()
def deploy_gradio():
    """
    Deploy Gradio app with Modal's high-performance infrastructure.
    
    This deployment function implements:
    - Smart Gradio interface detection using global scope analysis
    - FastAPI integration following Modal's ASGI architecture patterns
    - Performance optimization for concurrent request handling
    - Error handling and fallback mechanisms for production reliability
    """

    # 🔍 Smart Gradio Interface Detection
    # Using global scope analysis for maximum compatibility
    demo = None

    # Primary detection: Check common Gradio interface names
    if 'demo' in globals():
        demo = globals()['demo']
    elif 'app' in globals() and hasattr(globals()['app'], 'queue'):
        demo = globals()['app']
    elif 'interface' in globals():
        demo = globals()['interface']
    elif 'iface' in globals():
        demo = globals()['iface']

    # Fallback detection: Comprehensive global scope scan
    if demo is None:
        for var_name, var_value in globals().items():
            if hasattr(var_value, 'queue') and hasattr(var_value, 'launch'):
                demo = var_value
                break

    # 🚨 Fail-safe error handling with descriptive messaging
    if demo is None:
        raise ValueError(
            "Could not find Gradio interface in the application. "
            "Ensure your app defines a Gradio interface as 'demo', 'app', 'interface', or 'iface'."
        )

    # 🚀 Performance Configuration
    # Optimized queue size for responsiveness and throughput
    demo.queue(max_size=10)

    # 🔗 FastAPI Integration
    # Following Modal's recommended ASGI architecture patterns
    fastapi_app = FastAPI(
        title="Modal-for-noobs Gradio App",
        description="High-performance Gradio deployment on Modal cloud infrastructure",
        version="1.0.0",
        docs_url="/docs",  # Enable API documentation
        redoc_url="/redoc"  # Enable alternative API documentation
    )
    
    return mount_gradio_app(fastapi_app, demo, path="/")

# 🏃‍♂️ Direct execution support for local testing
if __name__ == "__main__":
    app.run()

# ⚡ Modal Function Configuration
# Engineered for scalability, performance, and reliability
@app.function(
    image=image,
    min_containers=1,
    max_containers=1,  # Single container for session consistency and state management
    timeout=3600,  # Configurable timeout for workload requirements
    scaledown_window=1200,  # Optimized scale-down for cost efficiency
)
@modal.concurrent(max_inputs=100)  # High concurrency for production-grade performance
@modal.asgi_app()
def deploy_gradio():
    """
    Deploy Gradio app with Modal's high-performance infrastructure.
    
    This deployment function implements:
    - Smart Gradio interface detection using global scope analysis
    - FastAPI integration following Modal's ASGI architecture patterns
    - Performance optimization for concurrent request handling
    - Error handling and fallback mechanisms for production reliability
    """

    # 🔍 Smart Gradio Interface Detection
    # Using global scope analysis for maximum compatibility
    demo = None

    # Primary detection: Check common Gradio interface names
    if 'demo' in globals():
        demo = globals()['demo']
    elif 'app' in globals() and hasattr(globals()['app'], 'queue'):
        demo = globals()['app']
    elif 'interface' in globals():
        demo = globals()['interface']
    elif 'iface' in globals():
        demo = globals()['iface']

    # Fallback detection: Comprehensive global scope scan
    if demo is None:
        for var_name, var_value in globals().items():
            if hasattr(var_value, 'queue') and hasattr(var_value, 'launch'):
                demo = var_value
                break

    # 🚨 Fail-safe error handling with descriptive messaging
    if demo is None:
        raise ValueError(
            "Could not find Gradio interface in the application. "
            "Ensure your app defines a Gradio interface as 'demo', 'app', 'interface', or 'iface'."
        )

    # 🚀 Performance Configuration
    # Optimized queue size for responsiveness and throughput
    demo.queue(max_size=10)

    # 🔗 FastAPI Integration
    # Following Modal's recommended ASGI architecture patterns
    fastapi_app = FastAPI(
        title="Modal-for-noobs Gradio App",
        description="High-performance Gradio deployment on Modal cloud infrastructure",
        version="1.0.0",
        docs_url="/docs",  # Enable API documentation
        redoc_url="/redoc"  # Enable alternative API documentation
    )
    
    return mount_gradio_app(fastapi_app, demo, path="/")

# 🏃‍♂️ Direct execution support for local testing
if __name__ == "__main__":
    app.run()