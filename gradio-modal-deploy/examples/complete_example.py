"""
🚀💚 Complete Gradio Modal Deploy Example 💚🚀
Shows all features of the gradio-modal-deploy package.

Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨
"""

import gradio as gr
from gradio_modal_deploy import (
    ModalDeployButton,
    ModalExplorer,
    ModalStatusMonitor,
    ModalTheme,
    modal_auto_deploy,
    modal_gpu_when_needed,
    get_modal_status,
    validate_app_file
)


# Example ML function that auto-detects GPU need
@modal_gpu_when_needed
def process_with_ai(text: str) -> str:
    """Example AI processing function."""
    # Simulated ML processing
    import time
    time.sleep(1)  # Simulate processing

    return f"🤖 AI processed: '{text}' with Modal magic! ✨"


def create_complete_demo():
    """Create a complete demo showcasing all features."""

    # Use the beautiful Modal theme
    theme = ModalTheme()

    with gr.Blocks(
        theme=theme,
        title="🚀💚 Complete Modal Deploy Demo 💚🚀",
        css="""
        .demo-section {
            background: rgba(0, 210, 106, 0.05);
            padding: 20px;
            border-radius: 12px;
            margin: 10px 0;
            border: 1px solid rgba(0, 210, 106, 0.2);
        }
        """
    ) as demo:

        # Header
        gr.Markdown("""
        # 🚀💚 Complete Gradio Modal Deploy Demo 💚🚀
        ### *Showcasing all features of gradio-modal-deploy package*

        **📦 Package Features** | **🎨 Beautiful Themes** | **🚀 One-Click Deploy** | **📊 Live Monitoring**
        """)

        with gr.Tabs():
            # Tab 1: Basic App with Deploy Button
            with gr.TabItem("🚀 Deploy Demo"):
                with gr.Column(elem_classes=["demo-section"]):
                    gr.Markdown("### 🎯 AI Text Processing with Auto-Deploy")

                    with gr.Row():
                        with gr.Column():
                            text_input = gr.Textbox(
                                label="📝 Enter text to process",
                                placeholder="Type something amazing...",
                                value="Hello Modal!"
                            )
                            process_btn = gr.Button("🤖 Process with AI", variant="primary")

                        with gr.Column():
                            output_text = gr.Textbox(
                                label="🎉 AI Result",
                                interactive=False
                            )

                    # Connect the processing
                    process_btn.click(
                        fn=process_with_ai,
                        inputs=text_input,
                        outputs=output_text
                    )

                    gr.Markdown("### 🚀 One-Click Modal Deployment")

                    # Modal deployment button
                    deploy_button = ModalDeployButton(
                        app_file=__file__,
                        mode="optimized",  # GPU + ML libraries
                        timeout_minutes=60,
                        auto_auth=True
                    )

            # Tab 2: Modal Explorer
            with gr.TabItem("📁 Examples Explorer"):
                gr.Markdown("### 📚 Explore Modal's Official Examples")

                # Modal examples explorer
                explorer = ModalExplorer(
                    github_repo="modal-labs/modal-examples",
                    auto_refresh=True,
                    show_deploy_button=True
                )

            # Tab 3: Status Monitor
            with gr.TabItem("📊 Status Monitor"):
                gr.Markdown("### 📈 Modal Deployment Monitoring")

                # Status monitor
                monitor = ModalStatusMonitor(
                    refresh_interval=5,
                    show_logs=True,
                    show_costs=True
                )

            # Tab 4: Package Info
            with gr.TabItem("ℹ️ About Package"):
                gr.Markdown("""
                ## 🎯 About gradio-modal-deploy

                This package provides beautiful Gradio components for seamless Modal deployment:

                ### 🚀 Components
                - **ModalDeployButton** - One-click deployment to Modal
                - **ModalExplorer** - Interactive Modal examples browser
                - **ModalStatusMonitor** - Real-time deployment monitoring
                - **ModalTheme** - Beautiful Modal-themed styling

                ### 🎨 Decorators
                - **@modal_auto_deploy** - Automatic deployment on app creation
                - **@modal_gpu_when_needed** - Smart GPU allocation
                - **@modal_memory_optimized** - Memory-optimized functions

                ### 🛠️ Utilities
                - **setup_modal_auth()** - Handle Modal authentication
                - **get_modal_status()** - Get deployment status
                - **deploy_to_modal()** - Programmatic deployment
                - **validate_app_file()** - Validate Gradio apps

                ### 📦 Installation
                ```bash
                # With uv (recommended)
                uv add gradio-modal-deploy

                # With pip
                pip install gradio-modal-deploy
                ```

                ### 🎯 Quick Start
                ```python
                import gradio as gr
                from gradio_modal_deploy import ModalDeployButton, ModalTheme

                theme = ModalTheme()

                with gr.Blocks(theme=theme) as demo:
                    gr.Markdown("# My App")

                    # Add one-click deploy
                    deploy_btn = ModalDeployButton(
                        app_file="app.py",
                        mode="optimized"
                    )

                demo.launch()
                ```

                ### 🌟 Features
                - 🚀 **One-click deployment** to Modal's serverless infrastructure
                - 📁 **Live GitHub integration** with Modal examples
                - 📊 **Real-time monitoring** of deployments and costs
                - 🎨 **Beautiful Modal theming** with signature green colors
                - 🤖 **Smart resource detection** for GPU/memory optimization
                - ⚡ **Modern async/await** patterns with uvloop
                - 🔐 **Automatic authentication** handling

                ---

                💚 **Made with <3 by [Neurotic Coder](https://github.com/arthrod) and assisted by Beloved Claude** ✨

                📚 **Documentation:** [gradio-modal-deploy.readthedocs.io](https://gradio-modal-deploy.readthedocs.io)
                🐛 **Issues:** [GitHub Issues](https://github.com/arthrod/gradio-modal-deploy/issues)
                """)

                # Show current status
                def show_status():
                    status = get_modal_status()
                    return f"""
                    ### 📊 Current Modal Status
                    - **Authenticated:** {'✅ Yes' if status.get('authenticated') else '❌ No'}
                    - **Total Deployments:** {status.get('total_deployments', 0)}
                    - **Active Deployments:** {status.get('active_deployments', 0)}
                    """

                status_display = gr.Markdown()
                status_btn = gr.Button("🔄 Check Status", variant="secondary")
                status_btn.click(fn=show_status, outputs=status_display)

        # Footer
        gr.Markdown("""
        ---
        ### 🚀 Ready to Deploy?

        1. **🎨 Customize** your app with Modal theming
        2. **🔧 Add** ModalDeployButton for one-click deployment
        3. **📊 Monitor** with ModalStatusMonitor
        4. **🚀 Deploy** to Modal's incredible infrastructure!

        **💚 Experience the Modal difference today!**
        """)

    return demo


# Auto-deploy decorator example (commented out to avoid automatic deployment)
# @modal_auto_deploy(mode="optimized", timeout=60)
def create_auto_deploy_demo():
    """Example of auto-deployment decorator."""
    return create_complete_demo()


if __name__ == "__main__":
    print("🚀💚 COMPLETE GRADIO MODAL DEPLOY DEMO STARTING! 💚🚀")
    print("📦 Showcasing all package features...")
    print("💚 Made with <3 by Neurotic Coder and assisted by Beloved Claude!")

    demo = create_complete_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
