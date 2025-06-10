"""Modal Dashboard - Beautiful monitoring interface for Modal deployments."""

import asyncio
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import gradio as gr
import httpx
from loguru import logger
from rich import print as rprint

# Import Modal color palette from common module
from modal_for_noobs.cli_helpers.common import MODAL_GREEN, MODAL_LIGHT_GREEN, MODAL_DARK_GREEN, MODAL_BLACK

# Import new UI components and themes
from modal_for_noobs.ui.themes import MODAL_THEME, MODAL_CSS
from modal_for_noobs.ui.components import ModalStatusMonitor

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
    url: Optional[str] = None
    gpu_type: Optional[str] = None
    runtime_minutes: float = 0.0
    estimated_cost: float = 0.0
    uptime: str = "Unknown"
    containers: int = 0
    functions: List[str] = None
    
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
        self.deployments: List[ModalDeployment] = []
        self.refresh_interval = 30  # seconds
        
    async def fetch_deployments(self) -> List[ModalDeployment]:
        """Fetch current deployments from Modal CLI."""
        try:
            # Run modal app list command
            process = await asyncio.create_subprocess_exec(
                "modal", "app", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Failed to fetch deployments: {stderr.decode()}")
                return []
            
            # Parse text output - Modal CLI doesn't support JSON yet
            return await self._parse_text_output(stdout.decode())
            
        except Exception as e:
            logger.error(f"Error fetching deployments: {e}")
            return []
    
    async def _parse_text_output(self, output: str) -> List[ModalDeployment]:
        """Parse text output from modal app list command with enhanced parsing."""
        deployments = []
        lines = output.strip().split('\n')
        
        # Look for actual deployment lines (skip headers and separators)
        for line in lines:
            line = line.strip()
            if not line or '─' in line or line.startswith('app_id') or line.startswith('App'):
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
                    functions=app_details.get("functions", [])
                )
                
                # Calculate estimated cost
                deployment.estimated_cost = deployment.calculate_running_cost()
                deployments.append(deployment)
        
        return deployments
    
    async def _get_app_details(self, app_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific app."""
        details = {
            "name": app_id,
            "url": None,
            "gpu_type": "CPU",
            "runtime_minutes": 0.0,
            "uptime": "Unknown",
            "containers": 1,
            "functions": []
        }
        
        try:
            # Try to get app logs to extract more information
            process = await asyncio.create_subprocess_exec(
                "modal", "app", "logs", app_id, "--lines", "5",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logs = stdout.decode()
                
                # Extract URL from logs
                url_match = re.search(r'https://[^\s]+\.modal\.run[^\s]*', logs)
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
                timestamps = re.findall(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', logs)
                if len(timestamps) >= 2:
                    try:
                        start_time = datetime.fromisoformat(timestamps[0].replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(timestamps[-1].replace('Z', '+00:00'))
                        runtime = (end_time - start_time).total_seconds() / 60.0
                        details["runtime_minutes"] = runtime
                    except Exception:
                        pass
        
        except Exception as e:
            logger.debug(f"Could not get details for app {app_id}: {e}")
        
        return details
    
    
    async def stop_deployment(self, app_id: str) -> Dict[str, Any]:
        """Stop a specific deployment."""
        try:
            process = await asyncio.create_subprocess_exec(
                "modal", "app", "stop", app_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
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
                "modal", "app", "logs", app_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logs = stdout.decode()
                # Return last N lines
                log_lines = logs.split('\n')
                return '\n'.join(log_lines[-lines:])
            else:
                return f"Error fetching logs: {stderr.decode()}"
                
        except Exception as e:
            return f"Error fetching logs: {str(e)}"
    
    async def get_credit_balance(self) -> Dict[str, Any]:
        """Get Modal credit balance and usage info."""
        # Note: Modal doesn't expose credit balance via CLI yet
        # This is a placeholder for future implementation
        return {
            "balance": "N/A",
            "usage_this_month": "N/A",
            "estimated_remaining": "N/A"
        }
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface for the dashboard."""
        with gr.Blocks(
            title="Modal Monitoring Dashboard",
            theme=MODAL_THEME,
            css=MODAL_CSS
        ) as demo:
            # Header
            gr.Markdown(
                f"""
                # 🚀 Modal Monitoring Dashboard
                
                <div style="color: {MODAL_LIGHT_GREEN};">
                Real-time monitoring and management for your Modal deployments
                </div>
                """
            )
            
            with gr.Row():
                # Left column - Deployments list
                with gr.Column(scale=2):
                    gr.Markdown("## 📊 Active Deployments")
                    
                    refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
                    deployments_df = gr.Dataframe(
                        headers=["App ID", "State", "GPU", "Runtime", "Cost", "URL"],
                        datatype=["str", "str", "str", "str", "str", "str"],
                        interactive=False,
                        label="",
                    )
                    
                    # Control buttons
                    with gr.Row():
                        selected_app = gr.Textbox(
                            label="Selected App ID",
                            placeholder="Enter app ID to manage"
                        )
                        stop_btn = gr.Button("⏹️ Stop", variant="primary")
                        logs_btn = gr.Button("📜 View Logs", variant="secondary")
                
                # Right column - Details and metrics
                with gr.Column(scale=1):
                    gr.Markdown("## 💰 Account Info")
                    
                    with gr.Row():
                        credit_balance = gr.Textbox(
                            label="Credit Balance",
                            value="Loading...",
                            interactive=False
                        )
                    
                    with gr.Row():
                        usage_this_month = gr.Textbox(
                            label="Usage This Month",
                            value="Loading...",
                            interactive=False
                        )
            
            # Logs section
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## 📜 Deployment Logs")
                    logs_output = gr.Textbox(
                        label="",
                        lines=20,
                        max_lines=30,
                        interactive=False,
                        placeholder="Select a deployment and click 'View Logs' to see logs here..."
                    )
            
            # Status output
            status_output = gr.Textbox(
                label="Status",
                interactive=False,
                visible=True
            )
            
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
                        data.append([
                            d.app_id,
                            d.state,
                            d.gpu_type,
                            runtime_str,
                            cost_str,
                            d.url or "N/A"
                        ])
                    
                    # Also update credit info
                    credit_info = await self.get_credit_balance()
                    
                    return {
                        deployments_df: data,
                        credit_balance: credit_info["balance"],
                        usage_this_month: credit_info["usage_this_month"],
                        status_output: f"✅ Refreshed at {datetime.now().strftime('%H:%M:%S')}"
                    }
                except Exception as e:
                    return {
                        status_output: f"❌ Error refreshing: {str(e)}"
                    }
            
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
                    return {
                        logs_output: "Please enter an app ID",
                        status_output: "❌ Please enter an app ID"
                    }
                
                logs = await self.fetch_logs(app_id)
                return {
                    logs_output: logs,
                    status_output: f"✅ Fetched logs for {app_id}"
                }
            
            # Connect events
            refresh_btn.click(
                fn=refresh_deployments,
                outputs=[deployments_df, credit_balance, usage_this_month, status_output]
            )
            
            stop_btn.click(
                fn=stop_selected_deployment,
                inputs=[selected_app],
                outputs=[deployments_df, credit_balance, usage_this_month, status_output]
            )
            
            logs_btn.click(
                fn=view_logs,
                inputs=[selected_app],
                outputs=[logs_output, status_output]
            )
            
            # Initial load
            demo.load(
                fn=refresh_deployments,
                outputs=[deployments_df, credit_balance, usage_this_month, status_output]
            )
        
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
        quiet=True
    )


if __name__ == "__main__":
    # For testing
    launch_dashboard()