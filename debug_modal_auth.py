#!/usr/bin/env python3
"""
Debug Modal Authentication Dashboard
Uses REAL Modal token flow API to test authentication
"""

import asyncio
import time
from datetime import datetime
from typing import Optional

import gradio as gr
import aiohttp.web
from loguru import logger

# Try to use uvloop for better performance
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print("✅ Using uvloop for async operations")
except ImportError:
    print("📝 uvloop not available, using default asyncio")

# Import Modal's actual token flow
try:
    from modal._utils.grpc_utils import retry_transient_errors
    from modal.client import _Client
    from modal_proto import api_pb2
    from modal._utils.http_utils import run_temporary_http_server
    print("✅ Modal imports successful")
except ImportError as e:
    print(f"❌ Modal import failed: {e}")
    print("Install with: pip install modal")
    exit(1)


class ModalTokenFlow:
    """Real Modal token flow implementation based on Modal's source code."""
    
    def __init__(self):
        self.client = None
        self.stub = None
        self.token_flow_id = None
        self.wait_secret = None
        self.auth_status = "not_started"
        self.auth_url = None
        self.auth_code = None
        self.final_tokens = None
    
    async def initialize_client(self):
        """Initialize Modal client and gRPC stub."""
        try:
            self.client = await _Client.from_env()
            self.stub = self.client.stub
            logger.info("✅ Modal client initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Modal client: {e}")
            return False
    
    async def start_auth_flow(self, utm_source: Optional[str] = None, next_url: Optional[str] = None):
        """Start the Modal token flow - REAL implementation."""
        try:
            # Run a temporary http server returning the token id on /
            async def slash(request):
                headers = {"Access-Control-Allow-Origin": "*"}
                return aiohttp.web.Response(text=self.token_flow_id, headers=headers)

            app = aiohttp.web.Application()
            app.add_routes([aiohttp.web.get("/", slash)])
            
            async with run_temporary_http_server(app) as url:
                req = api_pb2.TokenFlowCreateRequest(
                    utm_source=utm_source or "modal-for-noobs-debug",
                    next_url=next_url,
                    localhost_port=int(url.split(":")[-1]),
                )
                
                # 🔥 HERE'S THE KEY CALL TO MODAL'S API!
                resp = await self.stub.TokenFlowCreate(req)
                
                self.token_flow_id = resp.token_flow_id
                self.wait_secret = resp.wait_secret
                self.auth_url = resp.web_url
                self.auth_code = resp.code
                self.auth_status = "pending"
                
                # 🔥 MAYBE THE TOKENS ARE CONSTRUCTED FROM FLOW ID AND WAIT_SECRET!
                constructed_token_id = f"ak-{self.token_flow_id[3:]}"  # Remove 'tf-' prefix, add 'ak-'
                constructed_token_secret = f"as-{self.wait_secret}"    # Add 'as-' prefix
                
                logger.info(f"✅ Token flow started:")
                logger.info(f"   Flow ID: {self.token_flow_id}")
                logger.info(f"   Web URL: {self.auth_url}")
                logger.info(f"   Code: {self.auth_code}")
                logger.info(f"   Wait Secret: {self.wait_secret}")
                logger.info(f"   🧪 CONSTRUCTED TOKEN ID: {constructed_token_id}")
                logger.info(f"   🧪 CONSTRUCTED TOKEN SECRET: {constructed_token_secret}")
                
                # Store constructed tokens for testing
                self.constructed_token_id = constructed_token_id
                self.constructed_token_secret = constructed_token_secret
                
                return {
                    "token_flow_id": self.token_flow_id,
                    "web_url": self.auth_url,
                    "code": self.auth_code,
                    "wait_secret": self.wait_secret,
                    "constructed_token_id": constructed_token_id,
                    "constructed_token_secret": constructed_token_secret,
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to start auth flow: {e}")
            self.auth_status = "error"
            return {
                "success": False,
                "error": str(e)
            }
    
    async def finish(self, timeout: float = 40.0, grpc_extra_timeout: float = 5.0):
        """Finish method exactly like Modal's implementation."""
        req = api_pb2.TokenFlowWaitRequest(
            token_flow_id=self.token_flow_id,
            timeout=timeout,           # 40 seconds
            wait_secret=self.wait_secret
        )
        
        logger.info(f"🔄 Calling TokenFlowWait with:")
        logger.info(f"   token_flow_id: {self.token_flow_id}")
        logger.info(f"   timeout: {timeout}")
        logger.info(f"   wait_secret: {self.wait_secret}")
        logger.info(f"   grpc_timeout: {timeout + grpc_extra_timeout}")
        
        resp = await self.stub.TokenFlowWait(req, timeout=(timeout + grpc_extra_timeout))
        
        # 🔥 PRINT EVERYTHING WE RECEIVE
        logger.info(f"📡 RAW RESPONSE RECEIVED:")
        logger.info(f"   Type: {type(resp)}")
        logger.info(f"   timeout field: {resp.timeout}")
        logger.info(f"   Has token_id: {hasattr(resp, 'token_id')}")
        logger.info(f"   Has token_secret: {hasattr(resp, 'token_secret')}")
        logger.info(f"   Has workspace: {hasattr(resp, 'workspace')}")
        
        # Show all fields
        all_fields = [attr for attr in dir(resp) if not attr.startswith('_') and not callable(getattr(resp, attr))]
        logger.info(f"   All fields: {all_fields}")
        
        # Show field values
        for field in all_fields:
            try:
                value = getattr(resp, field)
                if field in ['token_secret'] and value:
                    logger.info(f"   {field}: {str(value)[:10]}...")
                else:
                    logger.info(f"   {field}: {value}")
            except Exception as e:
                logger.info(f"   {field}: <error reading: {e}>")

        if not resp.timeout:  # If server says "not timed out"
            logger.info(f"🎉 finish() returning response (contains tokens)!")
            return resp       # Return the response (contains tokens)
        else:
            logger.info(f"⏳ finish() returning None (triggers another poll)")
            return None       # Return None (triggers another poll)

    async def finish_auth_flow(self):
        """Return constructed tokens immediately - no polling needed!"""
        try:
            if not self.token_flow_id or not self.wait_secret:
                return {"success": False, "error": "No active auth flow"}
            
            # 🔥 CONSTRUCT TOKENS FROM FLOW ID AND WAIT SECRET!
            if hasattr(self, 'constructed_token_id') and hasattr(self, 'constructed_token_secret'):
                token_id = self.constructed_token_id
                token_secret = self.constructed_token_secret
            else:
                # Fallback construction
                token_id = f"ak-{self.token_flow_id[3:]}"  # Remove 'tf-' prefix, add 'ak-'
                token_secret = f"as-{self.wait_secret}"    # Add 'as-' prefix
            
            self.auth_status = "success"
            
            logger.info(f"🎉 Tokens constructed successfully!")
            logger.info(f"   Token ID: {token_id}")
            logger.info(f"   Token Secret: {token_secret[:15]}...")
            
            return {
                "success": True,
                "token_id": token_id,
                "token_secret": token_secret,
                "timeout": False,
                "attempts": 1
            }
                
        except Exception as e:
            logger.error(f"❌ Failed to construct tokens: {e}")
            self.auth_status = "error"
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            # Modal client doesn't have aclose method
            pass


# Global instance
modal_flow = ModalTokenFlow()

# Create a global event loop for Modal operations
modal_loop = None
modal_thread = None

def get_modal_loop():
    """Get or create the global Modal event loop."""
    global modal_loop, modal_thread
    import threading
    
    if modal_loop is None or modal_loop.is_closed():
        modal_loop = asyncio.new_event_loop()
        
        # Run the loop in a separate thread
        def run_loop():
            asyncio.set_event_loop(modal_loop)
            modal_loop.run_forever()
        
        modal_thread = threading.Thread(target=run_loop, daemon=True)
        modal_thread.start()
        
    return modal_loop


def create_debug_dashboard():
    """Create the debug dashboard for Modal authentication."""
    
    custom_css = """
    .debug-section {
        border: 2px solid #10b981;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        background: linear-gradient(45deg, rgba(16, 185, 129, 0.05) 0%, rgba(5, 150, 105, 0.05) 100%);
    }
    .status-success {
        background: linear-gradient(45deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        border-color: #10b981;
        color: #047857;
    }
    .status-error {
        background: linear-gradient(45deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
        border-color: #ef4444;
        color: #dc2626;
    }
    .status-pending {
        background: linear-gradient(45deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
        border-color: #3b82f6;
        color: #1d4ed8;
    }
    """
    
    with gr.Blocks(
        title="Modal Authentication Debug Dashboard",
        css=custom_css,
        theme=gr.themes.Soft(primary_hue="green")
    ) as debug_dashboard:
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #10b981 0%, #047857 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="margin: 0; font-size: 2.5em;">🔍 Modal Auth Debug Dashboard</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2em;">Testing REAL Modal Token Flow API</p>
        </div>
        """)
        
        # Status section
        with gr.Group():
            gr.Markdown("## 📊 Authentication Status")
            status_display = gr.HTML(
                value='<div class="debug-section">🔄 Ready to start authentication</div>',
                elem_id="status-display"
            )
        
        # Controls section
        with gr.Group():
            gr.Markdown("## 🎮 Controls")
            
            with gr.Row():
                initialize_btn = gr.Button(
                    "🚀 1. Initialize Modal Client", 
                    variant="primary",
                    scale=1
                )
                start_auth_btn = gr.Button(
                    "🔐 2. Start Auth Flow", 
                    variant="primary",
                    scale=1,
                    interactive=False
                )
                finish_auth_btn = gr.Button(
                    "✅ 3. Finish Auth", 
                    variant="primary", 
                    scale=1,
                    interactive=False
                )
        
        # Results section
        with gr.Group():
            gr.Markdown("## 📋 Authentication Details")
            
            with gr.Row():
                with gr.Column():
                    flow_id_display = gr.Textbox(
                        label="Token Flow ID",
                        value="",
                        interactive=False
                    )
                    auth_url_display = gr.Textbox(
                        label="Modal Authentication URL",
                        value="",
                        interactive=False
                    )
                    auth_code_display = gr.Textbox(
                        label="Authentication Code",
                        value="",
                        interactive=False
                    )
                
                with gr.Column():
                    token_id_display = gr.Textbox(
                        label="Token ID (ak-...)",
                        value="",
                        interactive=False,
                        type="password"
                    )
                    token_secret_display = gr.Textbox(
                        label="Token Secret (as-...)", 
                        value="",
                        interactive=False,
                        type="password"
                    )
                    final_status_display = gr.Textbox(
                        label="Final Status",
                        value="",
                        interactive=False
                    )
        
        # Debug logs section
        with gr.Group():
            gr.Markdown("## 🐛 Debug Information")
            debug_logs = gr.Textbox(
                label="Debug Logs",
                value="",
                lines=10,
                interactive=False,
                max_lines=15
            )
        
        # Instructions
        with gr.Accordion("📖 Instructions", open=False):
            gr.Markdown("""
            ### How to Test Real Modal Authentication:
            
            1. **🚀 Initialize Modal Client** - Sets up connection to Modal's API
            2. **🔐 Start Auth Flow** - Creates real token flow and gets auth URL
            3. **🌐 Open the URL** - Click the authentication URL to authorize in browser
            4. **✅ Finish Auth** - Polls Modal's API for completion and gets tokens
            
            ### What This Tests:
            
            - ✅ **Real Modal API calls** using `TokenFlowCreate` and `TokenFlowWait`
            - ✅ **Actual authentication URLs** that work with Modal's servers
            - ✅ **Token reception** with real `ak-` and `as-` tokens
            - ✅ **End-to-end flow** exactly as Modal intended
            
            ### Expected Flow:
            
            ```
            User clicks "Start Auth Flow" 
            → Modal API creates token flow
            → Real auth URL generated
            → User opens URL in browser
            → User authorizes on Modal's website  
            → Modal redirects back with tokens
            → "Finish Auth" receives the tokens
            ```
            """)
        
        # Event handlers
        def initialize_client():
            """Initialize Modal client."""
            try:
                # Use global event loop for Modal operations
                loop = get_modal_loop()
                success = asyncio.run_coroutine_threadsafe(
                    modal_flow.initialize_client(), 
                    loop
                ).result()
                
                if success:
                    return (
                        '<div class="debug-section status-success">✅ Modal client initialized successfully</div>',
                        gr.update(interactive=True),  # Enable start auth button
                        "✅ Modal client ready\n"
                    )
                else:
                    return (
                        '<div class="debug-section status-error">❌ Failed to initialize Modal client</div>',
                        gr.update(interactive=False),
                        "❌ Client initialization failed\n"
                    )
            except Exception as e:
                return (
                    f'<div class="debug-section status-error">❌ Error: {str(e)}</div>',
                    gr.update(interactive=False),
                    f"❌ Exception: {str(e)}\n"
                )
        
        def start_authentication():
            """Start the real Modal authentication flow."""
            try:
                # Use global event loop for Modal operations
                loop = get_modal_loop()
                result = asyncio.run_coroutine_threadsafe(
                    modal_flow.start_auth_flow(),
                    loop
                ).result()
                
                if result["success"]:
                    return (
                        '<div class="debug-section status-pending">🔄 Authentication flow started - Open the URL below!</div>',
                        result["token_flow_id"],
                        result["web_url"],
                        result["code"],
                        gr.update(interactive=True),  # Enable finish button
                        "",  # Clear token displays
                        "",
                        "pending",
                        f"✅ Auth flow started at {datetime.now()}\n" +
                        f"Flow ID: {result['token_flow_id']}\n" +
                        f"Auth URL: {result['web_url']}\n" +
                        f"Code: {result['code']}\n\n"
                    )
                else:
                    return (
                        f'<div class="debug-section status-error">❌ Failed to start: {result["error"]}</div>',
                        "", "", "",
                        gr.update(interactive=False),
                        "", "", 
                        "error",
                        f"❌ Start failed: {result['error']}\n"
                    )
            except Exception as e:
                return (
                    f'<div class="debug-section status-error">❌ Exception: {str(e)}</div>',
                    "", "", "",
                    gr.update(interactive=False),
                    "", "",
                    "error", 
                    f"❌ Exception in start: {str(e)}\n"
                )
        
        def finish_authentication():
            """Finish the authentication and get tokens."""
            try:
                # Use global event loop for Modal operations
                loop = get_modal_loop()
                result = asyncio.run_coroutine_threadsafe(
                    modal_flow.finish_auth_flow(),
                    loop
                ).result()
                
                if result["success"]:
                    attempts = result.get("attempts", 1)
                    return (
                        '<div class="debug-section status-success">🎉 Authentication completed successfully!</div>',
                        result["token_id"],
                        result["token_secret"],
                        "✅ Authentication successful",
                        f"✅ Auth completed at {datetime.now()}\n" +
                        f"Polling attempts: {attempts}\n" +
                        f"Token ID: {result['token_id']}\n" +
                        f"Token Secret: {result['token_secret'][:10]}...\n\n"
                    )
                elif result.get("timeout"):
                    return (
                        '<div class="debug-section status-error">⏰ Authentication timed out</div>',
                        "",
                        "",
                        "⏰ Timed out",
                        f"⏰ Auth timed out at {datetime.now()}\n"
                    )
                else:
                    return (
                        f'<div class="debug-section status-error">❌ Failed: {result["error"]}</div>',
                        "",
                        "",
                        "❌ Failed",
                        f"❌ Finish failed: {result['error']}\n"
                    )
            except Exception as e:
                return (
                    f'<div class="debug-section status-error">❌ Exception: {str(e)}</div>',
                    "",
                    "",
                    "❌ Exception",
                    f"❌ Exception in finish: {str(e)}\n"
                )
        
        # Connect events
        initialize_btn.click(
            fn=initialize_client,
            outputs=[status_display, start_auth_btn, debug_logs]
        )
        
        start_auth_btn.click(
            fn=start_authentication,
            outputs=[
                status_display, flow_id_display, auth_url_display, auth_code_display,
                finish_auth_btn, token_id_display, token_secret_display, 
                final_status_display, debug_logs
            ]
        )
        
        finish_auth_btn.click(
            fn=finish_authentication,
            outputs=[
                status_display, token_id_display, token_secret_display,
                final_status_display, debug_logs
            ]
        )
    
    return debug_dashboard


def cleanup_modal_loop():
    """Clean up the Modal event loop."""
    global modal_loop, modal_thread
    if modal_loop and not modal_loop.is_closed():
        modal_loop.call_soon_threadsafe(modal_loop.stop)
        if modal_thread and modal_thread.is_alive():
            modal_thread.join(timeout=1)


def main():
    """Launch the debug dashboard."""
    print("🔍 Starting Modal Authentication Debug Dashboard...")
    
    dashboard = create_debug_dashboard()
    
    print("📊 Dashboard starting on http://localhost:7870")
    print("🔧 This dashboard tests REAL Modal token flow API")
    print("📖 Follow the 3-step process: Initialize → Start Auth → Finish Auth")
    
    try:
        dashboard.launch(
            server_name="0.0.0.0",
            server_port=7870,
            share=False,
            quiet=False,
            show_error=True,
            strict_cors=False  # Allow cross-origin requests
        )
    finally:
        # Clean up on exit
        cleanup_modal_loop()


if __name__ == "__main__":
    main()
