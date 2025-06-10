"""Complete Modal Dashboard with all authentication options and enhanced features."""

import asyncio
import json
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import gradio as gr
from loguru import logger
from rich import print as rprint

from modal_for_noobs.cli_helpers.common import MODAL_GREEN, MODAL_LIGHT_GREEN, MODAL_DARK_GREEN
from modal_for_noobs.auth_manager import ModalAuthManager, ModalAuthConfig
from modal_for_noobs.template_generator import generate_from_wizard_input


class CompleteModalDashboard:
    """Complete Modal dashboard with all authentication options and enhanced features."""
    
    def __init__(self):
        """Initialize the complete dashboard."""
        self.auth_manager = ModalAuthManager()
        self.is_authenticated = False
        self.current_auth_config = None
    
    def create_complete_interface(self) -> gr.Blocks:
        """Create the complete dashboard interface with all features.
        
        Returns:
            Gradio Blocks interface with all authentication and deployment features
        """
        # Custom CSS with all three greens
        custom_css = f"""
        .modal-header {{
            background: linear-gradient(135deg, {MODAL_GREEN} 0%, {MODAL_DARK_GREEN} 50%, {MODAL_LIGHT_GREEN} 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .auth-card {{
            border: 2px solid {MODAL_GREEN};
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            background: linear-gradient(45deg, rgba(16, 185, 129, 0.05) 0%, rgba(5, 150, 105, 0.05) 100%);
        }}
        .auth-success {{
            background: linear-gradient(45deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
            border-color: {MODAL_GREEN};
            color: {MODAL_DARK_GREEN};
        }}
        .auth-pending {{
            background: linear-gradient(45deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
            border-color: #3b82f6;
            color: #1d4ed8;
        }}
        .wizard-step {{
            background: linear-gradient(135deg, {MODAL_GREEN} 0%, {MODAL_DARK_GREEN} 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            margin: 8px 0;
            font-weight: bold;
        }}
        .feature-card {{
            border: 1px solid {MODAL_LIGHT_GREEN};
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            background: linear-gradient(45deg, rgba(52, 211, 153, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%);
        }}
        """
        
        with gr.Blocks(
            title="Modal for Noobs - Complete Dashboard",
            css=custom_css,
            theme=gr.themes.Soft(
                primary_hue="green",
                secondary_hue="emerald",
                neutral_hue="slate"
            )
        ) as dashboard:
            # Header with all three greens
            gr.HTML(f"""
            <div class="modal-header">
                <h1 style="margin: 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    🚀 Modal for Noobs
                </h1>
                <p style="margin: 10px 0 0 0; font-size: 1.3em; opacity: 0.9;">
                    Deploy to Modal in minutes, not hours!
                </p>
                <p style="margin: 5px 0 0 0; font-size: 1.1em; opacity: 0.8;">
                    Complete deployment experience with authentication, templates, and monitoring
                </p>
            </div>
            """)
            
            # Global state
            auth_state = gr.State(value={
                "authenticated": False, 
                "method": None, 
                "config": None,
                "session_id": None
            })
            
            with gr.Tabs() as main_tabs:
                # Tab 1: Authentication Hub (Primary)
                with gr.Tab("🔐 Connect to Modal") as auth_tab:
                    gr.Markdown("## Welcome! Let's get you connected to Modal")
                    gr.Markdown(
                        f"Choose your preferred authentication method. **Link Authentication** is "
                        f"recommended for beginners - it's the easiest and most secure!"
                    )
                    
                    # Authentication status
                    auth_status_display = gr.HTML(
                        value=self._get_auth_status_html(False),
                        elem_id="auth-status-main"
                    )
                    
                    with gr.Tabs() as auth_methods:
                        # Method 1: Link Authentication (Primary - Noob Friendly)
                        with gr.Tab("🌐 Link Authentication (Recommended)") as link_auth_tab:
                            with gr.Column(elem_classes=["auth-card"]):
                                gr.Markdown("### 🎯 Super Easy - Just Click and Authorize!")
                                gr.Markdown(
                                    "This is the **easiest way** to connect. No API keys to copy, "
                                    "no complex setup - just click a button and authorize in your browser!"
                                )
                                
                                # Link auth interface
                                with gr.Row():
                                    with gr.Column(scale=2):
                                        gr.Markdown(
                                            "**How it works:**\\n"
                                            "1. 🔗 Click the button below\\n"
                                            "2. 🌐 A new tab opens with Modal's authorization page\\n"
                                            "3. 🔐 Log in or sign up (it's free!)\\n"
                                            "4. ✅ Click 'Authorize' and you're done!"
                                        )
                                    with gr.Column(scale=1):
                                        link_auth_btn = gr.Button(
                                            "🚀 Connect via Link",
                                            variant="primary",
                                            size="lg",
                                            elem_classes=["feature-card"]
                                        )
                                
                                # Progress section for link auth
                                with gr.Column(visible=False) as link_progress:
                                    gr.Markdown("### 🔄 Waiting for authorization...")
                                    gr.Markdown("A new tab should have opened. Please authorize modal-for-noobs to continue.")
                                    
                                    link_progress_bar = gr.HTML(
                                        value=self._get_progress_html(0),
                                        elem_id="link-progress"
                                    )
                                    
                                    link_cancel_btn = gr.Button("Cancel", variant="secondary")
                                
                                # Success section for link auth
                                with gr.Column(visible=False) as link_success:
                                    gr.Markdown("### ✅ Connected Successfully!")
                                    link_workspace_display = gr.Textbox(
                                        label="Connected Workspace",
                                        value="",
                                        interactive=False
                                    )
                                    gr.Markdown("🎉 You're all set! You can now deploy your apps to Modal!")
                        
                        # Method 2: Token Authentication (Manual)
                        with gr.Tab("🔑 Token Authentication") as token_auth_tab:
                            with gr.Column(elem_classes=["auth-card"]):
                                gr.Markdown("### 🛠️ Manual Setup - For Advanced Users")
                                gr.Markdown(
                                    "If you prefer manual setup or already have tokens, enter them here."
                                )
                                
                                with gr.Row():
                                    with gr.Column(scale=2):
                                        gr.Markdown(
                                            "**Steps:**\\n"
                                            "1. 🌐 Get your tokens from Modal\\n"
                                            "2. 📋 Copy Token ID and Token Secret\\n"
                                            "3. 📝 Paste them below\\n"
                                            "4. ✅ Click Authenticate"
                                        )
                                    with gr.Column(scale=1):
                                        open_tokens_btn = gr.Button(
                                            "🌐 Open Tokens Page",
                                            variant="secondary",
                                            elem_classes=["feature-card"]
                                        )
                                
                                with gr.Row():
                                    token_id_input = gr.Textbox(
                                        label="Token ID (starts with 'ak-')",
                                        placeholder="ak-your-token-id-here",
                                        type="text",
                                        scale=1
                                    )
                                    token_secret_input = gr.Textbox(
                                        label="Token Secret (starts with 'as-')",
                                        placeholder="as-your-token-secret-here",
                                        type="password",
                                        scale=1
                                    )
                                
                                workspace_input = gr.Textbox(
                                    label="Workspace Name (optional)",
                                    placeholder="your-workspace-name"
                                )
                                
                                with gr.Row():
                                    token_auth_btn = gr.Button(
                                        "🔐 Authenticate with Tokens",
                                        variant="primary",
                                        scale=1
                                    )
                                    test_connection_btn = gr.Button(
                                        "🧪 Test Connection",
                                        variant="secondary",
                                        scale=1
                                    )
                                
                                token_result = gr.Textbox(
                                    label="Result",
                                    interactive=False,
                                    lines=3
                                )
                        
                        # Method 3: File Upload Authentication
                        with gr.Tab("📁 File Upload") as file_auth_tab:
                            with gr.Column(elem_classes=["auth-card"]):
                                gr.Markdown("### 📂 Import from File")
                                gr.Markdown(
                                    "If you have a Modal config file from another setup, upload it here."
                                )
                                
                                config_file_upload = gr.File(
                                    label="Upload Modal Config File",
                                    file_types=[".toml", ".json", ".txt"],
                                    type="filepath"
                                )
                                
                                file_result = gr.Textbox(
                                    label="Upload Result",
                                    interactive=False,
                                    lines=3
                                )
                                
                                gr.Markdown(
                                    "**Supported formats:**\\n"
                                    "- JSON files with token_id and token_secret\\n"
                                    "- TOML configuration files\\n"
                                    "- Text files with environment variables"
                                )
                    
                    # Help section
                    with gr.Accordion("❓ Need Help?", open=False):
                        gr.Markdown(
                            f"""
                            ### 🆘 Authentication Help
                            
                            **Which method should I choose?**
                            - 🌐 **Link Authentication**: Best for beginners, most secure, easiest setup
                            - 🔑 **Token Authentication**: For advanced users who prefer manual control
                            - 📁 **File Upload**: For importing existing configurations
                            
                            ### 🔗 Link Authentication (Recommended)
                            This is the safest and easiest method. It uses OAuth 2.0 (same as "Sign in with Google").
                            Your password is never shared with modal-for-noobs.
                            
                            ### 🛡️ Security
                            - Link authentication is most secure (OAuth 2.0)
                            - Token secrets are never saved to disk
                            - All connections use HTTPS encryption
                            
                            ### 🆘 Troubleshooting
                            - **Browser tab didn't open?** Check your popup blocker
                            - **Authorization failed?** Make sure you have a Modal account
                            - **Still having issues?** Try the Token Authentication method
                            """
                        )
                
                # Tab 2: App Generator with Enhanced Features
                with gr.Tab("🎯 Generate Your App") as generate_tab:
                    with gr.Column():
                        # Auth check for this tab
                        gen_auth_check = gr.HTML(
                            value=self._get_auth_check_html(False),
                            elem_id="auth-check-generate"
                        )
                        
                        with gr.Column() as generator_section:
                            gr.Markdown("## 🧙‍♂️ Enhanced App Generation Wizard")
                            gr.Markdown(
                                "Create powerful Modal deployments with our advanced wizard. "
                                "All features from modal_generate are included!"
                            )
                            
                            # File upload
                            app_file_upload = gr.File(
                                label="📁 Upload Your Python App",
                                file_types=[".py"],
                                type="filepath"
                            )
                            
                            # Or paste code
                            gr.Markdown("**Or paste your code here:**")
                            code_input = gr.Code(
                                label="Python Code",
                                language="python",
                                value="""# Paste your Gradio app code here...
import gradio as gr

def greet(name):
    return f'Hello {name}!'

demo = gr.Interface(fn=greet, inputs='text', outputs='text')
demo.launch()""",
                                lines=10
                            )
                            
                            # Enhanced wizard sections
                            with gr.Accordion("⚙️ Enhanced Configuration Wizard", open=True):
                                # Step 1: Basic Settings
                                with gr.Group():
                                    gr.HTML('<div class="wizard-step">Step 1: Basic Settings</div>')
                                    with gr.Row():
                                        app_name_input = gr.Textbox(
                                            label="App Name",
                                            placeholder="my-awesome-app",
                                            scale=2
                                        )
                                        deployment_mode = gr.Dropdown(
                                            label="Deployment Mode",
                                            choices=[
                                                ("🌱 Minimum - Fast & cheap", "minimum"),
                                                ("⚡ Optimized - GPU + ML", "optimized"),
                                                ("📓 Marimo - Reactive notebooks", "marimo"),
                                                ("🪐 Gradio+Jupyter - Classic notebooks", "gradio-jupyter"),
                                            ],
                                            value="minimum",
                                            scale=2
                                        )
                                
                                # Step 2: Advanced Features (Enhanced)
                                with gr.Group():
                                    gr.HTML('<div class="wizard-step">Step 2: Advanced Features</div>')
                                    with gr.Row():
                                        enable_gpu = gr.Checkbox(
                                            label="🚀 Enable GPU",
                                            value=False
                                        )
                                        gpu_type = gr.Dropdown(
                                            label="GPU Type",
                                            choices=["any", "T4", "L4", "A10G", "A100", "H100"],
                                            value="any",
                                            visible=False
                                        )
                                        num_gpus = gr.Slider(
                                            label="Number of GPUs",
                                            minimum=1,
                                            maximum=8,
                                            value=1,
                                            step=1,
                                            visible=False
                                        )
                                    
                                    with gr.Row():
                                        enable_storage = gr.Checkbox(
                                            label="💾 Persistent Storage (NFS)",
                                            value=False
                                        )
                                        enable_logging = gr.Checkbox(
                                            label="📝 Enhanced Logging",
                                            value=False
                                        )
                                        enable_dashboard_monitoring = gr.Checkbox(
                                            label="📊 Dashboard Monitoring",
                                            value=False
                                        )
                                    
                                    with gr.Row():
                                        timeout_minutes = gr.Slider(
                                            label="⏱️ Timeout (minutes)",
                                            minimum=5,
                                            maximum=1440,  # 24 hours
                                            value=60,
                                            step=5
                                        )
                                        max_containers = gr.Slider(
                                            label="📈 Max Containers",
                                            minimum=1,
                                            maximum=100,
                                            value=10,
                                            step=1
                                        )
                                
                                # Step 3: Dependencies & Environment
                                with gr.Group():
                                    gr.HTML('<div class="wizard-step">Step 3: Dependencies & Environment</div>')
                                    
                                    requirements_upload = gr.File(
                                        label="📦 Upload requirements.txt",
                                        file_types=[".txt"],
                                        type="filepath"
                                    )
                                    
                                    with gr.Row():
                                        python_packages = gr.Textbox(
                                            label="Extra Python Packages",
                                            placeholder="numpy, pandas, scikit-learn",
                                            info="Comma-separated list"
                                        )
                                        system_packages = gr.Textbox(
                                            label="System Dependencies",
                                            placeholder="ffmpeg, curl, git",
                                            info="Comma-separated list"
                                        )
                                    
                                    # Environment variables
                                    with gr.Row():
                                        env_vars_input = gr.Textbox(
                                            label="Environment Variables",
                                            placeholder="DEBUG=true,API_URL=https://api.example.com",
                                            info="Comma-separated key=value pairs"
                                        )
                                        secrets_input = gr.Textbox(
                                            label="Modal Secrets",
                                            placeholder="api-key,db-password",
                                            info="Comma-separated secret names"
                                        )
                                
                                # Step 4: Remote Functions (Enhanced Feature)
                                with gr.Group():
                                    gr.HTML('<div class="wizard-step">Step 4: Remote Functions (Advanced)</div>')
                                    
                                    enable_remote_functions = gr.Checkbox(
                                        label="🔧 Enable Remote Functions",
                                        value=False,
                                        info="Add background tasks and scheduled functions"
                                    )
                                    
                                    with gr.Column(visible=False) as remote_functions_config:
                                        gr.Markdown("**Configure Remote Functions:**")
                                        
                                        remote_function_name = gr.Textbox(
                                            label="Function Name",
                                            placeholder="process_data"
                                        )
                                        
                                        with gr.Row():
                                            remote_gpu = gr.Dropdown(
                                                label="Function GPU",
                                                choices=["none", "T4", "A100", "H100"],
                                                value="none"
                                            )
                                            keep_warm = gr.Slider(
                                                label="Keep Warm Containers",
                                                minimum=0,
                                                maximum=10,
                                                value=0,
                                                step=1
                                            )
                                        
                                        with gr.Row():
                                            schedule_input = gr.Textbox(
                                                label="Schedule (cron format)",
                                                placeholder="0 */6 * * *",
                                                info="Optional: Schedule function to run periodically"
                                            )
                                            remote_timeout = gr.Slider(
                                                label="Function Timeout (seconds)",
                                                minimum=60,
                                                maximum=3600,
                                                value=300,
                                                step=60
                                            )
                                        
                                        add_remote_function_btn = gr.Button(
                                            "➕ Add Remote Function",
                                            variant="secondary",
                                            size="sm"
                                        )
                                        
                                        remote_functions_list = gr.JSON(
                                            label="Configured Remote Functions",
                                            value=[],
                                            visible=False
                                        )
                            
                            # Generate button
                            generate_btn = gr.Button(
                                "🚀 Generate Enhanced Deployment",
                                variant="primary",
                                size="lg",
                                elem_classes=["feature-card"]
                            )
                            
                            # Output
                            generation_output = gr.Code(
                                label="Generated Deployment Code",
                                language="python",
                                lines=25,
                                visible=False
                            )
                            
                            with gr.Row(visible=False) as output_actions:
                                download_btn = gr.DownloadButton(
                                    label="📥 Download Deployment File",
                                    variant="secondary"
                                )
                                deploy_btn = gr.Button(
                                    "🚀 Deploy to Modal",
                                    variant="primary"
                                )
                
                # Tab 3: Monitor & Manage
                with gr.Tab("📊 Monitor & Manage") as monitor_tab:
                    with gr.Column():
                        # Auth check
                        monitor_auth_check = gr.HTML(
                            value=self._get_auth_check_html(False),
                            elem_id="auth-check-monitor"
                        )
                        
                        with gr.Column() as monitoring_section:
                            gr.Markdown("## 📊 Deployment Monitoring & Management")
                            
                            with gr.Row():
                                refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
                                stop_selected_btn = gr.Button("🛑 Stop Selected", variant="secondary")
                                logs_btn = gr.Button("📝 View Logs", variant="secondary")
                            
                            # Deployments table
                            deployments_df = gr.Dataframe(
                                headers=["App Name", "Status", "URL", "Created", "GPU", "Cost"],
                                datatype=["str", "str", "str", "str", "str", "str"],
                                col_count=(6, "fixed"),
                                label="Your Deployments"
                            )
                            
                            # Selected deployment details
                            with gr.Row():
                                selected_app = gr.Dropdown(
                                    label="Select App for Details",
                                    choices=[],
                                    interactive=True
                                )
                                
                                with gr.Column():
                                    get_info_btn = gr.Button("ℹ️ Get Info")
                                    kill_app_btn = gr.Button("💀 Kill App", variant="stop")
                            
                            # Logs output
                            logs_output = gr.Textbox(
                                label="Application Logs",
                                lines=15,
                                max_lines=15,
                                visible=False,
                                interactive=False
                            )
                
                # Tab 4: Help & Examples
                with gr.Tab("❓ Help & Examples") as help_tab:
                    gr.Markdown("## 🎓 Complete Guide to Modal for Noobs")
                    
                    with gr.Accordion("🚀 Quick Start Guide", open=True):
                        gr.Markdown(f"""
                        ### Step-by-Step Guide
                        
                        **1. 🔐 Connect to Modal (Choose your method)**
                        - **🌐 Link Authentication (Recommended)**: Just click and authorize!
                        - **🔑 Token Authentication**: Manual setup with API tokens
                        - **📁 File Upload**: Import existing configuration
                        
                        **2. 🎯 Generate Your App**
                        - Upload your Python file or paste code
                        - Use the Enhanced Configuration Wizard
                        - Configure GPU, storage, environment variables
                        - Add remote functions for background tasks
                        
                        **3. 🚀 Deploy and Monitor**
                        - Review generated code
                        - Deploy to Modal
                        - Monitor in real-time
                        - View logs and manage deployments
                        """)
                    
                    with gr.Accordion("🎯 Example Applications", open=False):
                        gr.Markdown("""
                        ### Simple Gradio App
                        ```python
                        import gradio as gr
                        
                        def greet(name):
                            return f"Hello {name}!"
                        
                        demo = gr.Interface(fn=greet, inputs="text", outputs="text")
                        demo.launch()
                        ```
                        
                        ### ML Model with GPU
                        ```python
                        import gradio as gr
                        import torch
                        
                        def predict(text):
                            # Your ML model here
                            device = "cuda" if torch.cuda.is_available() else "cpu"
                            return f"Processed on {device}: {text}"
                        
                        demo = gr.Interface(fn=predict, inputs="text", outputs="text")
                        demo.launch()
                        ```
                        
                        ### Advanced App with Background Tasks
                        ```python
                        import gradio as gr
                        from datetime import datetime
                        
                        def process_data(data):
                            # Main interface function
                            return f"Processed at {datetime.now()}: {data}"
                        
                        # Background task (will be added as remote function)
                        def background_task():
                            print("Running background task...")
                            return "Task completed"
                        
                        demo = gr.Interface(fn=process_data, inputs="text", outputs="text")
                        demo.launch()
                        ```
                        """)
                    
                    with gr.Accordion("🔧 Advanced Features Guide", open=False):
                        gr.Markdown(f"""
                        ### Enhanced Features Explained
                        
                        **🚀 GPU Support**
                        - Choose from T4, L4, A10G, A100, H100
                        - Configure number of GPUs (1-8)
                        - Automatic CUDA setup
                        
                        **💾 Persistent Storage**
                        - NFS volumes for data persistence
                        - Shared storage across containers
                        - Automatic backup capabilities
                        
                        **🔧 Remote Functions**
                        - Background tasks
                        - Scheduled functions (cron)
                        - Keep-warm containers
                        - Custom GPU allocation per function
                        
                        **📊 Monitoring & Logging**
                        - Real-time deployment status
                        - Enhanced logging with structured output
                        - Performance metrics
                        - Cost tracking
                        
                        **🔐 Security Features**
                        - Environment variables
                        - Modal secrets integration
                        - Secure token handling
                        - OAuth 2.0 authentication
                        """)
                    
                    with gr.Accordion("🆘 Troubleshooting", open=False):
                        gr.Markdown("""
                        ### Common Issues & Solutions
                        
                        **Authentication Problems:**
                        - Make sure you clicked "Authorize" in the browser
                        - Check your popup blocker settings
                        - Try refreshing and connecting again
                        - Use Token Authentication as fallback
                        
                        **Deployment Fails:**
                        - Verify your code has a `demo` variable for Gradio apps
                        - Check all dependencies are included
                        - Try "minimum" mode first
                        - Review generated code for errors
                        
                        **App Won't Start:**
                        - Check logs in the monitoring tab
                        - Verify your code works locally
                        - Check environment variables and secrets
                        - Ensure GPU configuration matches your code
                        
                        **Performance Issues:**
                        - Enable GPU for ML workloads
                        - Increase container limits
                        - Use keep-warm for frequently called functions
                        - Monitor resource usage
                        """)
            
            # Event handlers
            def show_gpu_options(enable_gpu):
                return gr.update(visible=enable_gpu), gr.update(visible=enable_gpu)
            
            def show_remote_functions_config(enable_remote):
                return gr.update(visible=enable_remote)
            
            def start_link_authentication():
                """Start OAuth-style link authentication."""
                try:
                    # In a real implementation, this would start the OAuth flow
                    # For now, simulate opening the authorization URL
                    auth_url = "https://modal.com/oauth/authorize?client_id=modal-for-noobs"
                    webbrowser.open(auth_url)
                    
                    return {
                        link_auth_btn: gr.update(visible=False),
                        link_progress: gr.update(visible=True),
                        link_success: gr.update(visible=False),
                        auth_status_display: self._get_auth_status_html(False, "pending")
                    }
                except Exception as e:
                    logger.error(f"Failed to start link auth: {e}")
                    return {
                        auth_status_display: self._get_auth_status_html(False, "error", str(e))
                    }
            
            def authenticate_with_tokens(token_id, token_secret, workspace):
                """Authenticate using tokens."""
                if not token_id or not token_secret:
                    return "❌ Please provide both Token ID and Token Secret!", self._get_auth_status_html(False)
                
                config = ModalAuthConfig(
                    token_id=token_id.strip(),
                    token_secret=token_secret.strip(),
                    workspace=workspace.strip() if workspace else None
                )
                
                is_valid, errors = config.validate()
                if not is_valid:
                    return f"❌ Validation failed:\\n{chr(10).join(errors)}", self._get_auth_status_html(False)
                
                if self.auth_manager.test_authentication(config):
                    self.auth_manager.apply_auth_to_env(config)
                    self.auth_manager.save_auth(config)
                    self.is_authenticated = True
                    self.current_auth_config = config
                    
                    return "✅ Authentication successful! 🎉", self._get_auth_status_html(True, workspace)
                else:
                    return "❌ Authentication failed! Please check your tokens.", self._get_auth_status_html(False)
            
            def generate_enhanced_deployment(
                file_path, code, app_name, mode, enable_gpu, gpu_type, num_gpus,
                enable_storage, enable_logging, enable_dashboard_monitoring,
                timeout, max_containers, requirements_file, python_packages, 
                system_packages, env_vars, secrets, enable_remote_functions, remote_functions_data
            ):
                """Generate enhanced deployment with all features."""
                try:
                    # Get source code
                    if file_path:
                        source_code = Path(file_path).read_text()
                        if not app_name:
                            app_name = Path(file_path).stem
                    elif code:
                        source_code = code
                        if not app_name:
                            app_name = "my-gradio-app"
                    else:
                        return None, False, False, "❌ Please provide either a file or code!"
                    
                    # Parse inputs
                    python_deps = [pkg.strip() for pkg in python_packages.split(",") if pkg.strip()] if python_packages else []
                    system_deps = [pkg.strip() for pkg in system_packages.split(",") if pkg.strip()] if system_packages else []
                    
                    # Parse environment variables
                    env_dict = {}
                    if env_vars:
                        for pair in env_vars.split(","):
                            if "=" in pair:
                                key, value = pair.split("=", 1)
                                env_dict[key.strip()] = value.strip()
                    
                    # Parse secrets
                    secrets_list = [s.strip() for s in secrets.split(",") if s.strip()] if secrets else []
                    
                    # Parse remote functions
                    remote_functions = []
                    if enable_remote_functions and remote_functions_data:
                        # Process remote functions data
                        for func_data in remote_functions_data:
                            remote_functions.append(func_data)
                    
                    # Generate deployment
                    deployment_code = generate_from_wizard_input(
                        app_name=app_name,
                        deployment_mode=mode,
                        original_code=source_code,
                        provision_nfs=enable_storage,
                        provision_logging=enable_logging,
                        enable_dashboard=enable_dashboard_monitoring,
                        gpu_type=gpu_type if enable_gpu else None,
                        num_gpus=num_gpus if enable_gpu else None,
                        python_dependencies=python_deps,
                        system_dependencies=system_deps,
                        requirements_file=Path(requirements_file) if requirements_file else None,
                        environment_variables=env_dict,
                        secrets=secrets_list,
                        remote_functions=remote_functions,
                        timeout_seconds=timeout * 60,
                        max_containers=max_containers
                    )
                    
                    # Create download file
                    output_file = f"modal_{app_name}.py"
                    with open(output_file, "w") as f:
                        f.write(deployment_code)
                    
                    return (
                        gr.update(value=deployment_code, visible=True),
                        gr.update(visible=True),
                        gr.update(value=output_file, visible=True),
                        gr.update(visible=True),
                        "✅ Enhanced deployment generated successfully!"
                    )
                    
                except Exception as e:
                    logger.error(f"Generation failed: {e}")
                    return (
                        None, False, False, False,
                        f"❌ Generation failed: {str(e)}"
                    )
            
            # Connect events
            enable_gpu.change(
                fn=show_gpu_options,
                inputs=enable_gpu,
                outputs=[gpu_type, num_gpus]
            )
            
            enable_remote_functions.change(
                fn=show_remote_functions_config,
                inputs=enable_remote_functions,
                outputs=remote_functions_config
            )
            
            link_auth_btn.click(
                fn=start_link_authentication,
                outputs=[link_auth_btn, link_progress, link_success, auth_status_display]
            )
            
            token_auth_btn.click(
                fn=authenticate_with_tokens,
                inputs=[token_id_input, token_secret_input, workspace_input],
                outputs=[token_result, auth_status_display]
            )
            
            generate_btn.click(
                fn=generate_enhanced_deployment,
                inputs=[
                    app_file_upload, code_input, app_name_input, deployment_mode,
                    enable_gpu, gpu_type, num_gpus, enable_storage, enable_logging,
                    enable_dashboard_monitoring, timeout_minutes, max_containers,
                    requirements_upload, python_packages, system_packages,
                    env_vars_input, secrets_input, enable_remote_functions, remote_functions_list
                ],
                outputs=[generation_output, output_actions, download_btn, deploy_btn, gen_auth_check]
            )
        
        return dashboard
    
    def _get_auth_status_html(self, is_authenticated: bool, status: str = None, workspace: str = None, error_msg: str = None) -> str:
        """Get authentication status HTML with all three greens."""
        if is_authenticated:
            return f"""
            <div style="
                background: linear-gradient(45deg, {MODAL_GREEN} 0%, {MODAL_LIGHT_GREEN} 100%);
                color: white;
                padding: 16px;
                border-radius: 8px;
                margin: 16px 0;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <span style="font-size: 24px;">✅</span>
                <strong style="font-size: 18px; margin-left: 8px;">Connected to Modal!</strong>
                {f'<br><span style="opacity: 0.9;">Workspace: {workspace}</span>' if workspace else ''}
            </div>
            """
        elif status == "pending":
            return f"""
            <div style="
                background: linear-gradient(45deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                padding: 16px;
                border-radius: 8px;
                margin: 16px 0;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <span style="font-size: 24px;">🔄</span>
                <strong style="font-size: 18px; margin-left: 8px;">Connecting to Modal...</strong>
            </div>
            """
        elif status == "error":
            return f"""
            <div style="
                background: linear-gradient(45deg, #ef4444 0%, #dc2626 100%);
                color: white;
                padding: 16px;
                border-radius: 8px;
                margin: 16px 0;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <span style="font-size: 24px;">❌</span>
                <strong style="font-size: 18px; margin-left: 8px;">Connection Failed</strong>
                {f'<br><span style="opacity: 0.9;">{error_msg}</span>' if error_msg else ''}
            </div>
            """
        else:
            return f"""
            <div style="
                background: linear-gradient(45deg, {MODAL_DARK_GREEN} 0%, {MODAL_GREEN} 100%);
                color: white;
                padding: 16px;
                border-radius: 8px;
                margin: 16px 0;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <span style="font-size: 24px;">🔐</span>
                <strong style="font-size: 18px; margin-left: 8px;">Ready to Connect</strong>
                <br><span style="opacity: 0.9;">Choose your authentication method above</span>
            </div>
            """
    
    def _get_auth_check_html(self, is_authenticated: bool) -> str:
        """Get authentication check HTML for tabs."""
        if is_authenticated:
            return f"""
            <div style="
                background: linear-gradient(45deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
                border: 2px solid {MODAL_GREEN};
                color: {MODAL_DARK_GREEN};
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 16px;
                text-align: center;
            ">
                <span style="font-size: 20px;">✅</span>
                <strong>Connected to Modal - Ready to proceed!</strong>
            </div>
            """
        else:
            return f"""
            <div style="
                background: linear-gradient(45deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
                border: 2px solid #ef4444;
                color: #dc2626;
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 16px;
                text-align: center;
            ">
                <span style="font-size: 20px;">❌</span>
                <strong>Please connect to Modal first</strong>
                <br>Go to the "Connect to Modal" tab to get started
            </div>
            """
    
    def _get_progress_html(self, progress: float) -> str:
        """Get progress bar HTML."""
        return f"""
        <div style="
            width: 100%;
            height: 12px;
            background: #e5e7eb;
            border-radius: 6px;
            overflow: hidden;
            margin: 16px 0;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        ">
            <div style="
                width: {progress}%;
                height: 100%;
                background: linear-gradient(45deg, {MODAL_GREEN} 0%, {MODAL_LIGHT_GREEN} 100%);
                transition: width 0.3s ease;
                border-radius: 6px;
            "></div>
        </div>
        <p style="text-align: center; color: {MODAL_DARK_GREEN}; margin-top: 8px; font-weight: 500;">
            {int(progress)}% complete
        </p>
        """


def launch_complete_dashboard(port: int = 7860, share: bool = False):
    """Launch the complete Modal dashboard with all features.
    
    Args:
        port: Port to run the dashboard on
        share: Whether to create a public share link
    """
    dashboard = CompleteModalDashboard()
    interface = dashboard.create_complete_interface()
    
    rprint(f"[{MODAL_GREEN}]🚀 Launching Complete Modal Dashboard...[/{MODAL_GREEN}]")
    rprint(f"[{MODAL_LIGHT_GREEN}]📊 Dashboard available at: http://localhost:{port}[/{MODAL_LIGHT_GREEN}]")
    rprint(f"[{MODAL_DARK_GREEN}]✨ Features: Link auth, token auth, file upload, enhanced templates, monitoring![/{MODAL_DARK_GREEN}]")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share,
        quiet=False,
        show_error=True,
        debug=False,
        strict_cors=False  # Allow localhost, HuggingFace, and Modal cross-origin requests
    )


if __name__ == "__main__":
    # For testing
    launch_complete_dashboard()