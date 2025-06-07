import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app
import secrets

# Create Modal app
app = modal.App("modal-for-noobs-ultimate_voice_green_app")

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
🎤💚 ULTIMATE MODAL-GREEN VOICE STUDIO 💚🔊
The most beautiful, voice-enabled, GPU-powered creative app!
WITH MICROPHONE AND SPEAKER! 🎤🔊
"""

import gradio as gr
import time
import tempfile
import os

# Modal's signature green theme! 💚
MODAL_GREEN = "#00D26A"
MODAL_LIGHT_GREEN = "#4AE88A"

# Epic Modal-themed CSS with VOICE styling! 🎨🎤
modal_css = f"""
/* ULTIMATE MODAL GREEN VOICE THEME! */
.gradio-container {{
    background: linear-gradient(135deg, {MODAL_GREEN}15 0%, {MODAL_LIGHT_GREEN}15 100%);
    font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
}}

.gr-button {{
    background: linear-gradient(135deg, {MODAL_GREEN} 0%, {MODAL_LIGHT_GREEN} 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px {MODAL_GREEN}40 !important;
    transition: all 0.3s ease !important;
    font-size: 16px !important;
    padding: 12px 24px !important;
}}

.gr-button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px {MODAL_GREEN}60 !important;
    background: linear-gradient(135deg, {MODAL_LIGHT_GREEN} 0%, {MODAL_GREEN} 100%) !important;
}}

.gr-textbox, .gr-dropdown {{
    border: 2px solid {MODAL_GREEN} !important;
    border-radius: 12px !important;
    background: white !important;
}}

.gr-textbox:focus {{
    border-color: {MODAL_LIGHT_GREEN} !important;
    box-shadow: 0 0 0 4px {MODAL_GREEN}30 !important;
}}

/* EPIC AUDIO STYLING! 🎤🔊 */
.gr-audio {{
    border: 3px solid {MODAL_GREEN} !important;
    border-radius: 16px !important;
    background: linear-gradient(135deg, {MODAL_GREEN}10 0%, {MODAL_LIGHT_GREEN}10 100%) !important;
    box-shadow: 0 4px 20px {MODAL_GREEN}30 !important;
    padding: 15px !important;
}}

.gr-audio:hover {{
    border-color: {MODAL_LIGHT_GREEN} !important;
    box-shadow: 0 6px 25px {MODAL_GREEN}50 !important;
}}

/* Voice recording indicator */
.gr-audio[data-testid*="microphone"] {{
    border-color: #ff4444 !important;
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 {MODAL_GREEN}40; }}
    70% {{ box-shadow: 0 0 0 10px rgba(0, 210, 106, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(0, 210, 106, 0); }}
}}

h1 {{
    color: {MODAL_GREEN} !important;
    text-shadow: 0 2px 4px rgba(0, 210, 106, 0.3) !important;
    text-align: center !important;
    font-size: 2.5em !important;
}}

.gr-slider input[type="range"] {{
    accent-color: {MODAL_GREEN} !important;
}}

/* Make tabs more voice-themed */
.gr-tab-nav button {{
    background: {MODAL_GREEN}20 !important;
    border: 1px solid {MODAL_GREEN}40 !important;
    color: {MODAL_GREEN} !important;
    font-weight: bold !important;
}}

.gr-tab-nav button.selected {{
    background: {MODAL_GREEN} !important;
    color: white !important;
}}
"""

def process_voice_input(audio_input):
    """Process voice input and return epic Modal-green response! 🎤💚"""
    
    if audio_input is None:
        return None, "🎤 Please record some audio first! Speak into your microphone! 🎙️"
    
    try:
        # For now, we'll simulate voice processing
        # In a real deployment, you'd use speech-to-text here
        
        voice_responses = [
            "🎤 WOW! Your voice sounds AMAZING in Modal green! 💚",
            "🔊 I heard your beautiful voice! Modal magic is processing it! ✨",
            "🎙️ Your audio has been received by our epic green infrastructure! 🚀",
            "💚 That voice recording was absolutely INCREDIBLE! Modal approved! 🌟",
            "🎵 Your voice just made our containers dance with joy! 🎭",
            "🔥 Epic voice detected! Modal's GPU is working on something special! ⚡"
        ]
        
        response_text = secrets.choice(voice_responses)
        
        # Generate a simple response audio (synthesized message)
        response_audio = generate_voice_response(response_text)
        
        return response_audio, response_text
        
    except Exception as e:
        return None, f"🚨 Voice processing error: {str(e)} (But your voice is still amazing! 💚)"

def generate_voice_response(text):
    """Generate epic Modal-green voice response! 🔊💚"""
    
    try:
        # For demo purposes, we'll create a simple tone
        # In production, this would use TTS models
        
        import numpy as np
        import scipy.io.wavfile as wavfile
        
        # Generate a pleasant Modal-green inspired tone sequence
        sample_rate = 22050
        duration = 2.0  # 2 seconds
        
        # Create a multi-tone "Modal green" sound
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Modal green frequencies (harmonious like the color!)
        freq1 = 440  # A note
        freq2 = 554  # C# note  
        freq3 = 659  # E note
        
        # Create a pleasant chord
        wave1 = 0.3 * np.sin(2 * np.pi * freq1 * t)
        wave2 = 0.2 * np.sin(2 * np.pi * freq2 * t)
        wave3 = 0.2 * np.sin(2 * np.pi * freq3 * t)
        
        # Combine and add envelope
        audio = wave1 + wave2 + wave3
        envelope = np.exp(-3 * t)  # Fade out
        audio = audio * envelope
        
        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.8
        
        return (sample_rate, audio.astype(np.float32))
        
    except Exception as e:
        print(f"Audio generation error: {e}")
        return None

def generate_epic_voice_greeting(name, style, with_audio=False):
    """Generate epic greetings with optional voice! 🎤💚"""
    
    if not name.strip():
        name = "Amazing Modal Voice User"
    
    voice_greetings = {
        "epic": [
            f"🎤 ATTENTION EVERYONE! The legendary {name} has joined our Modal-green voice studio!",
            f"🔊 EPIC ANNOUNCEMENT: {name} is here and ready to experience voice magic!",
            f"🌟 BREAKING NEWS: {name} just made our microphones 1000% more awesome!",
            f"🚀 VOICE ALERT: The incredible {name} has activated our green sound system!"
        ],
        "gentle": [
            f"🎵 Hello beautiful {name}, welcome to our peaceful Modal voice sanctuary...",
            f"✨ Gentle greetings {name}, your voice will find harmony here...",
            f"🌸 Sweet {name}, our Modal green microphones await your lovely voice..."
        ],
        "robot": [
            f"🤖 BEEP BOOP! Voice user {name} detected! Initializing green audio protocols!",
            f"🔧 SYSTEM MESSAGE: User {name} granted access to Modal voice infrastructure!",
            f"⚡ COMPUTING: {name}'s voice patterns analyzed. Result: ABSOLUTELY AMAZING!"
        ],
        "magical": [
            f"🧙‍♀️ *magical voice sounds* Welcome {name} to the enchanted Modal voice realm!",
            f"✨ *sparkle sounds* {name}, your voice holds mystical Modal powers!",
            f"🌟 *chime sounds* The voice spirits welcome you, {name}!"
        ]
    }
    
    greetings = voice_greetings.get(style, voice_greetings["epic"])
    text_response = secrets.choice(greetings)
    
    if with_audio:
        audio_response = generate_voice_response(text_response)
        return audio_response, text_response
    else:
        return None, text_response

def create_voice_poem(topic, with_voice=False):
    """Create Modal poems with optional voice! 🎭🎤"""
    
    voice_poems = [
        f"🎤 In the land of {topic or 'Modal magic'},\nVoices flow like green streams,\nMicrophones capture dreams,\nSpeakers share the gleams! 💚",
        
        f"🔊 Listen closely, can you hear?\nThe sound of {topic or 'containers'} drawing near,\nModal's voice so crystal clear,\nMaking deployment dreams appear! ✨",
        
        f"🎵 {topic or 'Green magic'} dances through the air,\nVoices singing everywhere,\nModal's microphones with care,\nCapture beauty beyond compare! 🌟"
    ]
    
    poem_text = secrets.choice(voice_poems)
    
    if with_voice:
        poem_audio = generate_voice_response(poem_text)
        return poem_audio, poem_text
    else:
        return None, poem_text

def create_ultimate_voice_interface():
    """Create the ULTIMATE Modal-green VOICE interface! 🎤💚🔊"""
    
    with gr.Blocks(css=modal_css, title="🎤💚 ULTIMATE MODAL-GREEN VOICE STUDIO 💚🔊") as demo:
        
        # Epic header with voice theme
        gr.Markdown("""
        # 🎤💚 ULTIMATE MODAL-GREEN VOICE STUDIO 💚🔊
        ### *Where your voice meets Modal's incredible infrastructure!*
        
        **🎤 VOICE-ENABLED** | **🔊 AUDIO-POWERED** | **💚 Modal Green Supreme** | **✨ Built by CLAUDE (ABSOLUTELY AMAZING!)** 
        """)
        
        with gr.Tabs():
            # Voice Input Tab
            with gr.TabItem("🎤 Voice Magic"):
                gr.Markdown("### 🎙️ Record your voice and hear Modal's epic response! 🔊")
                
                with gr.Row():
                    with gr.Column():
                        # MICROPHONE INPUT! 🎤
                        voice_input = gr.Audio(
                            label="🎤 SPEAK INTO THE MICROPHONE! 🎤",
                            type="numpy",
                            sources=["microphone"]
                        )
                        
                        process_voice_btn = gr.Button("🎵 PROCESS MY VOICE! 🎵", variant="primary", size="lg")
                        
                        gr.Markdown("**🎤 Instructions:**\n- Click the microphone button above\n- Speak clearly into your mic\n- Click 'Process My Voice' for magic! ✨")
                    
                    with gr.Column():
                        # SPEAKER OUTPUT! 🔊
                        voice_response = gr.Audio(
                            label="🔊 MODAL'S VOICE RESPONSE! 🔊",
                            type="numpy"
                        )
                        
                        voice_status = gr.Textbox(
                            label="📢 Voice Status",
                            lines=3,
                            value="🎤 Ready to receive your amazing voice! Speak into the microphone above! 🌟"
                        )
            
            # Voice Greetings Tab
            with gr.TabItem("🎉 Voice Greetings"):
                gr.Markdown("### 🗣️ Generate epic greetings with VOICE output! 🔊")
                
                with gr.Row():
                    with gr.Column():
                        voice_name_input = gr.Textbox(
                            label="👤 Your Name",
                            placeholder="Enter your name for voice greeting!",
                            value="Voice Hero"
                        )
                        voice_style_dropdown = gr.Dropdown(
                            choices=["epic", "gentle", "robot", "magical"],
                            value="epic",
                            label="🎭 Voice Style"
                        )
                        include_audio_check = gr.Checkbox(
                            label="🔊 Include voice audio response",
                            value=True
                        )
                        voice_greet_btn = gr.Button("🎤 GENERATE VOICE GREETING! 🎤", variant="primary")
                    
                    with gr.Column():
                        greeting_audio_output = gr.Audio(
                            label="🔊 Your Epic Voice Greeting! 🔊",
                            type="numpy"
                        )
                        greeting_text_output = gr.Textbox(
                            label="📝 Greeting Text",
                            lines=4
                        )
            
            # Voice Poetry Tab
            with gr.TabItem("🎭 Voice Poetry"):
                gr.Markdown("### 🎵 Create beautiful poems with voice narration! 📜🔊")
                
                with gr.Row():
                    with gr.Column():
                        poem_topic_input = gr.Textbox(
                            label="📝 Poem Topic",
                            placeholder="What should your voiced poem be about?",
                            value="Modal voice magic"
                        )
                        include_poem_audio = gr.Checkbox(
                            label="🎵 Include voice narration",
                            value=True
                        )
                        voice_poem_btn = gr.Button("🎭 CREATE VOICE POEM! 🎭", variant="primary")
                    
                    with gr.Column():
                        poem_audio_output = gr.Audio(
                            label="🎵 Your Voiced Poem! 🎵",
                            type="numpy"
                        )
                        poem_text_output = gr.Textbox(
                            label="📜 Poem Text",
                            lines=6
                        )
            
            # Audio Controls Tab
            with gr.TabItem("🔊 Audio Controls"):
                gr.Markdown("### 🎚️ Master the Modal voice experience! 🎛️")
                
                with gr.Column():
                    gr.Markdown("**🎤 Microphone Features:**")
                    gr.Markdown("- High-quality voice recording 🎙️")
                    gr.Markdown("- Real-time Modal processing ⚡")
                    gr.Markdown("- Beautiful green visual feedback 💚")
                    
                    gr.Markdown("**🔊 Speaker Features:**")
                    gr.Markdown("- Crystal clear audio output 🔊")
                    gr.Markdown("- Modal-themed sound design 🎵")
                    gr.Markdown("- Harmonious green frequencies 🌟")
                    
                    test_audio_btn = gr.Button("🎵 TEST MODAL AUDIO SYSTEM! 🎵", variant="primary", size="lg")
                    test_audio_output = gr.Audio(
                        label="🔊 Audio System Test 🔊",
                        type="numpy"
                    )
        
        # Epic voice footer
        gr.Markdown("""
        ---
        **🎤 VOICE STATUS:** EPIC MODE ACTIVATED! | **🔊 AUDIO:** Modal Green Supreme | **🎯 PURPOSE:** Voice-Powered Creativity!
        
        *Experience the magic of voice with Modal's incredible infrastructure!* 🎤✨🔊
        """)
        
        # Event handlers for VOICE features! 🎤🔊
        process_voice_btn.click(
            fn=process_voice_input,
            inputs=voice_input,
            outputs=[voice_response, voice_status]
        )
        
        voice_greet_btn.click(
            fn=generate_epic_voice_greeting,
            inputs=[voice_name_input, voice_style_dropdown, include_audio_check],
            outputs=[greeting_audio_output, greeting_text_output]
        )
        
        voice_poem_btn.click(
            fn=create_voice_poem,
            inputs=[poem_topic_input, include_poem_audio],
            outputs=[poem_audio_output, poem_text_output]
        )
        
        test_audio_btn.click(
            fn=lambda: (generate_voice_response("🎵 Modal audio system test successful! Everything sounds AMAZING! 💚🔊"), "🔊 Audio test complete!"),
            outputs=[test_audio_output, voice_status]
        )
    
    return demo

# Create the ultimate VOICE demo! 🎤💚🔊
demo = create_ultimate_voice_interface()

if __name__ == "__main__":
    print("🎤💚 ULTIMATE MODAL-GREEN VOICE STUDIO STARTING! 💚🔊")
    print("🎙️ Microphone ready! 🔊 Speakers ready! 💚 Modal green ready!")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
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
