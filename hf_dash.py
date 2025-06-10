"""Modal Dashboard - Beautiful monitoring interface for Modal deployments."""

import asyncio
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
import httpx
from loguru import logger
from rich import print as rprint

# Import Modal color palette from common module
from modal_for_noobs.cli_helpers.common import MODAL_BLACK, MODAL_DARK_GREEN, MODAL_GREEN, MODAL_LIGHT_GREEN

# Import ModalDeployer for deployment functionality
from modal_for_noobs.modal_deploy import ModalDeployer
from modal_for_noobs.ui.components import ModalStatusMonitor

# Import new UI components and themes
from modal_for_noobs.ui.themes import MODAL_CSS, MODAL_THEME

# GPU cost estimates (per hour in USD)
GPU_COSTS = {
    "T4": 0.60,
    "L4": 1.10,
    "A10G": 1.20,
    "A100": 4.00,
    "H100": 8.00,
    "CPU": 0.30,  # CPU-only instances
}


@dataclass
class ModalDeployment:
    """Represents a Modal deployment with its metadata."""

    app_id: str
    app_name: str
    created_at: str
    state: str
    url: str | None = None
    gpu_type: str | None = None
    runtime_minutes: float = 0.0
    estimated_cost: float = 0.0
    uptime: str = "Unknown"
    containers: int = 0
    functions: list[str] = None

    def __post_init__(self):
        if self.functions is None:
            self.functions = []

    def estimate_hourly_cost(self) -> float:
        """Estimate hourly cost based on GPU type."""
        if self.gpu_type and self.gpu_type in GPU_COSTS:
            return GPU_COSTS[self.gpu_type] * self.containers
        return GPU_COSTS["CPU"] * self.containers

    def calculate_running_cost(self) -> float:
        """Calculate cost for current runtime."""
        hourly_cost = self.estimate_hourly_cost()
        return (self.runtime_minutes / 60.0) * hourly_cost


class ModalDashboard:
    """Dashboard for monitoring and managing Modal deployments."""

    def __init__(self):
        self.deployments: list[ModalDeployment] = []
        self.refresh_interval = 30  # seconds

    async def fetch_deployments(self) -> list[ModalDeployment]:
        """Fetch current deployments from Modal library."""
        try:
            import modal
            
            # Test authentication by trying to list apps
            try:
                apps = modal.App.list()
                deployments = []
                
                for app in apps:
                    deployment = ModalDeployment(
                        app_id=app.name,
                        state="running" if app.state == "active" else "stopped",
                        created_at=datetime.now().isoformat(),
                        url=getattr(app, 'web_url', None),
                        gpu_type="unknown",
                        runtime_minutes=0,
                        estimated_cost=0.0
                    )
                    deployments.append(deployment)
                
                return deployments
                
            except Exception as e:
                logger.info(f"Not authenticated with Modal or error listing apps: {e}")
                return []

        except Exception as e:
            logger.error(f"Error fetching deployments: {e}")
            return []

    async def _parse_text_output(self, output: str) -> list[ModalDeployment]:
        """Parse text output from modal app list command with enhanced parsing."""
        deployments = []
        lines = output.strip().split("\n")

        # Look for actual deployment lines (skip headers and separators)
        for line in lines:
            line = line.strip()
            if not line or "─" in line or line.startswith("app_id") or line.startswith("App"):
                continue

            # Parse app lines - format varies but typically: app_id state created_at
            parts = line.split()
            if len(parts) >= 2:
                app_id = parts[0]
                state = parts[1] if len(parts) > 1 else "unknown"
                created_at = " ".join(parts[2:]) if len(parts) > 2 else "Unknown"

                # Try to extract more details for each app
                app_details = await self._get_app_details(app_id)

                deployment = ModalDeployment(
                    app_id=app_id,
                    app_name=app_details.get("name", app_id),
                    created_at=created_at,
                    state=state,
                    url=app_details.get("url"),
                    gpu_type=app_details.get("gpu_type", "CPU"),
                    runtime_minutes=app_details.get("runtime_minutes", 0.0),
                    estimated_cost=0.0,  # Calculate based on runtime
                    uptime=app_details.get("uptime", "Unknown"),
                    containers=app_details.get("containers", 1),
                    functions=app_details.get("functions", []),
                )

                # Calculate estimated cost
                deployment.estimated_cost = deployment.calculate_running_cost()
                deployments.append(deployment)

        return deployments

    async def _get_app_details(self, app_id: str) -> dict[str, Any]:
        """Get detailed information about a specific app."""
        details = {
            "name": app_id,
            "url": None,
            "gpu_type": "CPU",
            "runtime_minutes": 0.0,
            "uptime": "Unknown",
            "containers": 1,
            "functions": [],
        }

        try:
            # Try to get app logs to extract more information
            process = await asyncio.create_subprocess_exec(
                "modal", "app", "logs", app_id, "--lines", "5", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logs = stdout.decode()

                # Extract URL from logs
                url_match = re.search(r"https://[^\s]+\.modal\.run[^\s]*", logs)
                if url_match:
                    details["url"] = url_match.group()

                # Look for GPU mentions in logs
                if "T4" in logs:
                    details["gpu_type"] = "T4"
                elif "L4" in logs:
                    details["gpu_type"] = "L4"
                elif "A10G" in logs:
                    details["gpu_type"] = "A10G"
                elif "A100" in logs:
                    details["gpu_type"] = "A100"
                elif "H100" in logs:
                    details["gpu_type"] = "H100"

                # Estimate runtime from timestamps in logs
                timestamps = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", logs)
                if len(timestamps) >= 2:
                    try:
                        start_time = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
                        end_time = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
                        runtime = (end_time - start_time).total_seconds() / 60.0
                        details["runtime_minutes"] = runtime
                    except Exception:
                        pass

        except Exception as e:
            logger.debug(f"Could not get details for app {app_id}: {e}")

        return details

    async def stop_deployment(self, app_id: str) -> dict[str, Any]:
        """Stop a specific deployment."""
        try:
            process = await asyncio.create_subprocess_exec(
                "modal", "app", "stop", app_id, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {"success": True, "message": f"Successfully stopped {app_id}"}
            else:
                return {"success": False, "message": stderr.decode()}

        except Exception as e:
            return {"success": False, "message": str(e)}

    async def fetch_logs(self, app_id: str, lines: int = 100) -> str:
        """Fetch logs for a specific deployment."""
        try:
            process = await asyncio.create_subprocess_exec(
                "modal", "app", "logs", app_id, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logs = stdout.decode()
                # Return last N lines
                log_lines = logs.split("\n")
                return "\n".join(log_lines[-lines:])
            else:
                return f"Error fetching logs: {stderr.decode()}"

        except Exception as e:
            return f"Error fetching logs: {str(e)}"

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface for the dashboard."""
        with gr.Blocks(title="Modal-for-Noobs Dashboard", theme=MODAL_THEME, css=MODAL_CSS) as demo:
            # Header
            gr.Markdown(
                f"""
                # 🚀 Modal-for-Noobs Dashboard

                <div style="color: {MODAL_LIGHT_GREEN};">
                Deploy from HuggingFace Spaces to Modal with one click!
                </div>
                """
            )

            # Hackathon Features Section
            with gr.Tab("🏆 Deploy to Modal"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## 🌟 HuggingFace to Modal Deployment")

                        # Feature 1: HuggingFace Spaces URL input
                        with gr.Row():
                            hf_url = gr.Textbox(
                                label="HuggingFace Spaces URL",
                                placeholder="https://huggingface.co/spaces/username/space-name",
                                info="Enter the URL of the HuggingFace Space you want to deploy",
                                scale=4
                            )
                            hf_url_ok = gr.Button("OK", variant="secondary", scale=1)

                        # Feature 2: Modal Authentication
                        gr.Markdown("""
                        ### 🔐 Modal Authentication
                        You need Modal tokens to deploy. Choose one of these options:
                        
                        **Option 1:** Use the button below for web authentication
                        **Option 2:** Set environment variables manually:
                        - `MODAL_TOKEN_ID=your_token_id`
                        - `MODAL_TOKEN_SECRET=your_token_secret`
                        """)
                        
                        with gr.Row():
                            modal_token_id = gr.Textbox(
                                label="Modal Token ID (Optional)",
                                placeholder="ak-... or st-...",
                                info="Leave empty to use environment variables or web auth"
                            )
                        
                        with gr.Row():
                            modal_token_secret = gr.Textbox(
                                label="Modal Token Secret (Optional)",
                                placeholder="Your token secret",
                                type="password",
                                info="Leave empty to use environment variables or web auth"
                            )
                        
                        with gr.Row():
                            set_tokens_btn = gr.Button("💾 Set Tokens", variant="secondary")
                            login_btn = gr.Button("🔐 Web Authenticate", variant="primary")
                            
                        with gr.Row():
                            login_status = gr.Textbox(label="Authentication Status", interactive=False, lines=3)

                        # Feature 5: Template selection dropdown
                        template_choice = gr.Dropdown(
                            choices=["FastAPI + Gradio", "Pure Gradio", "Streamlit", "Custom Python"],
                            label="Deployment Template",
                            value="FastAPI + Gradio",
                            info="Choose how to deploy your app",
                        )

                        # Feature 4: File/folder upload
                        with gr.Row():
                            with gr.Column():
                                file_upload = gr.File(label="Upload Python File", file_types=[".py"], file_count="single")
                            with gr.Column():
                                folder_upload = gr.File(label="Upload Folder (as ZIP)", file_types=[".zip"], file_count="single")

                        deploy_btn = gr.Button("🚀 Deploy to Modal", variant="primary", size="lg")

                        with gr.Column():
                            gr.Markdown("## 📊 Deployment Results")
                            deployment_output = gr.Textbox(
                                label="Deployment Status", lines=10, interactive=False, placeholder="Deployment results will appear here..."
                            )

                            # Deployment links
                            deployment_links = gr.Markdown("### 🔗 Deployment Links\nLinks will appear after successful deployment")

                # Original monitoring tab
            # Monitoring Section
            with gr.Tab("📊 Monitor Deployments"):
                # Main monitoring interface
                with gr.Row():
                    # Left column - Deployments list
                    with gr.Column(scale=2):
                        gr.Markdown("## 📊 Active Deployments")

                        deployments_df = gr.Dataframe(
                            headers=["App ID", "State", "GPU", "Runtime", "Cost", "URL"],
                            datatype=["str", "str", "str", "str", "str", "str"],
                            interactive=False,
                            label="",
                        )

                        # Control buttons
                        with gr.Row():
                            selected_app = gr.Textbox(label="Selected App ID", placeholder="Enter app ID to manage")
                            stop_btn = gr.Button("⏹️ Stop", variant="primary")
                            logs_btn = gr.Button("📜 View Logs", variant="secondary")

                    # Right column - Details and metrics
                    with gr.Column(scale=1):
                        gr.Markdown("## 📊 Quick Actions")
                        refresh_btn = gr.Button("🔄 Refresh Deployments", variant="primary")

            # Logs section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## 📜 Deployment Logs")
                    logs_output = gr.Textbox(
                        label="",
                        lines=20,
                        max_lines=30,
                        interactive=False,
                        placeholder="Select a deployment and click 'View Logs' to see logs here...",
                    )

            # Status output
            status_output = gr.Textbox(label="Status", interactive=False, visible=True)

            # Event handlers
            async def refresh_deployments():
                """Refresh the deployments list."""
                try:
                    deployments = await self.fetch_deployments()

                    # Format for dataframe with enhanced info
                    data = []
                    for d in deployments:
                        cost_str = f"${d.estimated_cost:.4f}" if d.estimated_cost > 0 else "N/A"
                        runtime_str = f"{d.runtime_minutes:.1f}m" if d.runtime_minutes > 0 else "N/A"
                        data.append([d.app_id, d.state, d.gpu_type, runtime_str, cost_str, d.url or "N/A"])

                    return {
                        deployments_df: data,
                        status_output: f"✅ Refreshed at {datetime.now().strftime('%H:%M:%S')}",
                    }
                except Exception as e:
                    return {status_output: f"❌ Error refreshing: {str(e)}"}

                async def stop_selected_deployment(app_id: str):
                    """Stop the selected deployment."""
                    if not app_id:
                        return {status_output: "❌ Please enter an app ID"}

                    result = await self.stop_deployment(app_id)
                    if result["success"]:
                        # Refresh deployments after stopping
                        refresh_result = await refresh_deployments()
                        refresh_result[status_output] = f"✅ {result['message']}"
                        return refresh_result
                    else:
                        return {status_output: f"❌ {result['message']}"}

                async def view_logs(app_id: str):
                    """View logs for the selected deployment."""
                    if not app_id:
                        return {logs_output: "", status_output: "❌ Please enter an app ID"}

                    logs = await self.fetch_logs(app_id)
                    return {logs_output: logs, status_output: f"✅ Fetched logs for {app_id}"}

                # Hackathon feature functions
                async def set_modal_tokens(token_id: str, token_secret: str):
                    """Set Modal tokens directly."""
                    try:
                        import os
                    
                        if not token_id or not token_secret:
                            return "❌ Both Token ID and Token Secret are required!"
                    
                        # Set tokens in environment
                        os.environ["MODAL_TOKEN_ID"] = token_id.strip()
                        os.environ["MODAL_TOKEN_SECRET"] = token_secret.strip()
                    
                        # Test authentication
                        import modal
                        try:
                            modal.App.list()
                            return "✅ Tokens set successfully! You are now authenticated with Modal!"
                        except Exception as e:
                            return f"❌ Invalid tokens: {str(e)}"
                        
                    except Exception as e:
                        return f"❌ Error setting tokens: {str(e)}"

                async def login_to_modal():
                    """Handle Modal web authentication."""
                    try:
                        import modal
                    
                        # Test Modal authentication by trying to list apps
                        try:
                            apps = modal.App.list()
                            return "✅ You are already authenticated with Modal!\n\n🎉 You can deploy your apps!"
                        
                        except Exception as e:
                            error_str = str(e)
                            if "Token missing" in error_str or "authenticate" in error_str:
                                # Not authenticated - provide auth instructions
                                try:
                                    from modal._utils.auth_utils import _new_token_flow
                                    auth_url = _new_token_flow()
                                
                                    instructions = f"""🔐 Modal Authentication Required

    **Option 1: Web Authentication**
    👋 Click this link: {auth_url}
    1. Sign in to your Modal account
    2. Complete the authentication flow
    3. Click this button again to verify

    **Option 2: Manual Token Setup**
    1. Visit: https://modal.com/tokens
    2. Create a new token (you'll get Token ID + Secret)
    3. Fill in the token fields above and click "Set Tokens"

    **Option 3: Environment Variables**
    Set these in your environment:
    - `MODAL_TOKEN_ID=your_token_id`
    - `MODAL_TOKEN_SECRET=your_token_secret`

    🔄 **After any option, click this button again to verify!**"""
                                
                                    return instructions
                                
                                except Exception:
                                    # Fallback to general instructions
                                    return """🔐 Modal Authentication Required

    **Get your tokens:**
    1. Visit: https://modal.com/tokens
    2. Create a new token
    3. You'll get both Token ID and Token Secret

    **Then choose one:**
    - Fill token fields above and click "Set Tokens"
    - Run: `modal token set --token-id YOUR_ID --token-secret YOUR_SECRET`
    - Set environment variables: `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`"""
                            else:
                                return f"❌ Error testing authentication: {error_str}\n\nPlease visit https://modal.com/tokens to authenticate manually."
                        
                    except ImportError:
                        return "❌ Modal library not found. Please install modal: pip install modal"
                    except Exception as e:
                        return f"❌ Error: {str(e)}\n\n💡 Please visit https://modal.com/tokens to authenticate manually."

                async def deploy_to_modal(hf_url: str, template: str, py_file, zip_file):
                    """Deploy to Modal using hackathon features."""
                    try:
                        import modal
                        output_lines = []

                        # 1. Check authentication first by testing Modal library
                        try:
                            modal.App.list()
                            output_lines.append("🔑 Modal authentication verified")
                        except Exception as e:
                            error_str = str(e)
                            if "Token missing" in error_str or "authenticate" in error_str:
                                return "❌ Deployment failed: Please authenticate with Modal first!", "### 🔗 Deployment Links\nDeployment failed - Not authenticated"
                            else:
                                return f"❌ Deployment failed: Authentication error - {error_str}", "### 🔗 Deployment Links\nDeployment failed - Auth error"

                        # 2. Handle HuggingFace URL
                        if hf_url:
                            output_lines.append(f"🌟 Processing HuggingFace Space: {hf_url}")
                            # Extract space info
                            space_parts = hf_url.split("/")[-2:]
                            if len(space_parts) == 2:
                                username, space_name = space_parts
                                output_lines.append(f"📦 Space: {username}/{space_name}")

                        # 3. Handle file uploads
                        source_path = None
                        if py_file:
                            output_lines.append(f"📄 Processing Python file: {py_file.name}")
                            source_path = py_file.name
                        elif zip_file:
                            output_lines.append(f"📁 Processing ZIP file: {zip_file.name}")
                            source_path = zip_file.name

                        # 4. Select template and deploy
                        output_lines.append(f"🎯 Using template: {template}")

                        # 5. ACTUAL DEPLOYMENT using existing modal-for-noobs functionality
                        if hf_url:
                            # Use HuggingFace migration
                            from modal_for_noobs.huggingface import HuggingFaceSpacesMigrator

                            migrator = HuggingFaceSpacesMigrator()

                            output_lines.append("🔄 Migrating from HuggingFace...")
                            space_info = await migrator.extract_space_info_async(hf_url)
                            local_dir = await migrator.download_space_files_async(space_info)
                            app_file = await migrator.convert_to_modal_async(local_dir, template == "FastAPI + Gradio")

                            # Deploy with ModalDeployer
                            mode = "optimized" if template in ["FastAPI + Gradio", "Streamlit"] else "minimum"
                            deployer = ModalDeployer(app_file=app_file, mode=mode)
                            deployment_url = await deployer.deploy_to_modal_async(app_file)

                        elif source_path:
                            # Deploy uploaded file
                            from pathlib import Path

                            app_file = Path(source_path)
                            mode = "optimized" if template in ["FastAPI + Gradio", "Streamlit"] else "minimum"

                            deployer = ModalDeployer(app_file=app_file, mode=mode)
                            deployment_url = await deployer.deploy_to_modal_async(app_file)

                        else:
                            # Create example app with template
                            from pathlib import Path

                            from modal_for_noobs.utils.easy_cli_utils import create_modal_deployment

                            # Create a simple app based on template
                            temp_app = Path(f"temp_hackathon_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

                            if template == "FastAPI + Gradio":
                                app_content = """import gradio as gr
    import modal
    app = modal.App("hackathon-gradio-app")
    @app.function()
    @modal.web_endpoint(method="GET")
    def hello():
        return "Hello from Modal!"
    if __name__ == "__main__":
        with app.run():
            print("App running!")"""
                            else:
                                app_content = """import gradio as gr
    def greet(name):
        return f"Hello, {name}!"
    demo = gr.Interface(fn=greet, inputs="text", outputs="text")
    if __name__ == "__main__":
        demo.launch()"""

                            temp_app.write_text(app_content)

                            mode = "optimized" if template in ["FastAPI + Gradio", "Streamlit"] else "minimum"
                            deployer = ModalDeployer(app_file=temp_app, mode=mode)
                            deployment_url = await deployer.deploy_to_modal_async(temp_app)

                        output_lines.append("🚀 Deploying to Modal...")

                        if deployment_url:
                            output_lines.extend(["✅ Deployment successful!", f"🌐 URL: {deployment_url}", f"💰 Estimated cost: $0.30/hour"])

                            # Generate deployment links markdown
                            links_md = f"""
                            ### 🔗 Deployment Links
                        
                            **Live App:** [{deployment_url}]({deployment_url})
                        
                            **Modal Dashboard:** [View in Modal](https://modal.com/apps)
                        
                            **Template Used:** {template}
                        
                            **Deployment Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            """
                        else:
                            output_lines.append("❌ Deployment failed - no URL returned")
                            links_md = "### 🔗 Deployment Links\nDeployment failed"

                        return "\n".join(output_lines), links_md

                    except Exception as e:
                        return f"❌ Deployment failed: {str(e)}", "### 🔗 Deployment Links\nDeployment failed"

                # Connect hackathon events
                set_tokens_btn.click(fn=set_modal_tokens, inputs=[modal_token_id, modal_token_secret], outputs=[login_status])
                login_btn.click(fn=login_to_modal, outputs=[login_status])
            
                hf_url.submit(
                    fn=deploy_to_modal,
                    inputs=[hf_url, template_choice, file_upload, folder_upload],
                    outputs=[deployment_output, deployment_links],
                )
                hf_url_ok.click(
                    fn=deploy_to_modal,
                    inputs=[hf_url, template_choice, file_upload, folder_upload],
                    outputs=[deployment_output, deployment_links],
                )

                deploy_btn.click(
                    fn=deploy_to_modal,
                    inputs=[hf_url, template_choice, file_upload, folder_upload],
                    outputs=[deployment_output, deployment_links],
                )

                # Connect monitoring events
                refresh_btn.click(fn=refresh_deployments, outputs=[deployments_df, status_output])

                stop_btn.click(
                    fn=stop_selected_deployment,
                    inputs=[selected_app],
                    outputs=[deployments_df, status_output],
                )

                logs_btn.click(fn=view_logs, inputs=[selected_app], outputs=[logs_output, status_output])

                # Initial load for monitoring tab - removed to prevent auth errors on startup
                # Users can click refresh button after authenticating

            return demo


def launch_dashboard(port: int = 7860, share: bool = False):
    """Launch the Modal monitoring dashboard."""
    dashboard = ModalDashboard()
    interface = dashboard.create_interface()

    rprint(f"[{MODAL_GREEN}]🚀 Launching Modal Monitoring Dashboard...[/{MODAL_GREEN}]")
    rprint(f"[{MODAL_LIGHT_GREEN}]📊 Dashboard will be available at: http://localhost:{port}[/{MODAL_LIGHT_GREEN}]")

    interface.launch(
        server_name="0.0.0.0", 
        server_port=port, 
        share=share, 
        quiet=True,
        strict_cors=False  # Allow localhost, HuggingFace, and Modal cross-origin requests
    )


if __name__ == "__main__":
    # For testing
    launch_dashboard()

