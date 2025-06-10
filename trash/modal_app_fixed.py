import modal
from fastapi import FastAPI
import gradio as gr
from gradio.routes import mount_gradio_app

# Create Modal app
app = modal.App("modal-for-noobs-app")

# Configure image

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "gradio",
    "fastapi[standard]",
    "uvicorn",
    "httpx",
    "markdown2",
    "torch",
    "transformers",
    "accelerate",
    "diffusers",
    "pillow",
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "plotly",
    "requests",
    "beautifulsoup4",
    "scikit-learn",
    "streamlit",
    "openai",
    "langchain"
)

# Original Gradio app code embedded
"""
🚀💚 MODAL EXAMPLES EXPLORER 💚🚀
Dynamic Modal Examples Browser - Powered by Modal-for-noobs!
Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨
"""

import asyncio
import base64
import gradio as gr
import httpx

# Try different markdown packages
try:
    import markdown
except ImportError:
    try:
        import markdown2 as markdown
    except ImportError:
        # Fallback - no markdown processing
        markdown = None

# Modal's signature green theme! 💚
MODAL_GREEN = "#00D26A"
MODAL_LIGHT_GREEN = "#4AE88A"

class GitHubAPI:
    """Async GitHub API client for Modal examples."""

    BASE_URL = "https://api.github.com"
    REPO_OWNER = "modal-labs"
    REPO_NAME = "modal-examples"

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_repo_contents(self, path: str = "") -> list[dict]:
        """Get repository contents for a specific path."""
        url = f"{self.BASE_URL}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/{path}"

        try:
            response = await self.client.get(url)

            # Handle 404 specifically - path doesn't exist
            if response.status_code == 404:
                print(f"📁 Path not found: {path}")
                return []

            response.raise_for_status()
            data = response.json()

            # Ensure we return a list
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Single file response, wrap in list
                return [data]
            else:
                print(f"⚠️ Unexpected response format for path '{path}': {type(data)}")
                return []

        except httpx.TimeoutException:
            print(f"⏰ Timeout fetching contents for path '{path}'")
            return []
        except httpx.HTTPError as e:
            if "404" in str(e):
                print(f"📁 Path not found: {path}")
            else:
                print(f"⚠️ HTTP error fetching repo contents for path '{path}': {e}")
            return []
        except Exception as e:
            print(f"⚠️ Unexpected error fetching repo contents for path '{path}': {e}")
            return []

    async def get_file_content(self, path: str) -> str:
        """Get the content of a specific file."""
        url = f"{self.BASE_URL}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/contents/{path}"

        try:
            response = await self.client.get(url)

            # Handle 404 specifically - file doesn't exist
            if response.status_code == 404:
                return f"❌ File not found: {path}"

            response.raise_for_status()

            data = response.json()
            if data.get("encoding") == "base64":
                try:
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    return content
                except (UnicodeDecodeError, base64.binascii.Error):
                    return f"⚠️ Binary file or encoding issue: {path}"
            else:
                return data.get("content", "")

        except httpx.TimeoutException:
            print(f"⏰ Timeout fetching '{path}'")
            return f"❌ Timeout loading file: {path}"
        except httpx.HTTPError as e:
            if "404" in str(e):
                return f"❌ File not found: {path}"
            print(f"⚠️ HTTP error fetching '{path}': {e}")
            return f"❌ HTTP error loading file: {path}"
        except Exception as e:
            print(f"⚠️ Unexpected error fetching '{path}': {e}")
            return f"❌ Error loading file: {path}"

    async def get_all_folders(self) -> list[dict]:
        """Get all folders in the repository root."""
        contents = await self.get_repo_contents()

        folders = []

        # Add fake "root" directory for organization - ALWAYS first
        folders.append({
            "name": "root",
            "path": ""
        })

        for item in contents:
            if item.get("type") == "dir":
                folders.append({
                    "name": item["name"],
                    "path": item["path"]
                })

        # Sort all except root (keep root first)
        root_folder = folders[0]
        other_folders = sorted(folders[1:], key=lambda x: x["name"])
        return [root_folder] + other_folders

    async def get_python_files_in_folder(self, folder_path: str) -> list[dict]:
        """Get all Python files in a specific folder."""
        contents = await self.get_repo_contents(folder_path)

        print(f"🔍 Raw contents for '{folder_path}': {len(contents)} items")

        # Debug: show all items found
        for item in contents:
            print(f"📁 Item: {item.get('name', 'NO_NAME')} | Type: {item.get('type', 'NO_TYPE')} | Path: {item.get('path', 'NO_PATH')}")

        python_files = []
        for item in contents:
            item_name = item.get("name", "")
            item_type = item.get("type", "")

            if item_type == "file" and item_name.endswith(".py"):
                python_files.append({
                    "name": item_name,
                    "path": item.get("path", "")
                })
                print(f"✅ Added Python file: {item_name}")
            elif item_name.endswith(".py"):
                print(f"⚠️ Skipped Python file (wrong type '{item_type}'): {item_name}")

        print(f"🐍 Found {len(python_files)} Python files total")
        if python_files:
            print(f"📄 Final files: {[f['name'] for f in python_files]}")

        return sorted(python_files, key=lambda x: x["name"])

    async def get_readme_content(self, folder_path: str = "") -> str:
        """Get README.md content for a folder, with fallback to root README."""
        # Try folder-specific README first
        if folder_path:
            readme_path = f"{folder_path}/README.md"
            content = await self.get_file_content(readme_path)
            # Only return if we got actual content (not an error message)
            if content and not content.startswith("❌"):
                return content

        # Fallback to root README
        root_readme_content = await self.get_file_content("README.md")
        # If root README also fails, return a helpful message
        if root_readme_content and not root_readme_content.startswith("❌"):
            return root_readme_content

        # If both fail, return a user-friendly message
        folder_display = folder_path if folder_path else "root"
        return f"""# 📄 No README Available

No README.md file found for the **{folder_display}** folder.

This folder might contain example code without documentation, or the README might be located elsewhere.

💡 **Tip:** Check the Python files in this folder to see what examples are available!"""

# Global GitHub API instance
github_api = GitHubAPI()

# Epic Modal-themed CSS! 🎨
modal_css = f"""
/* MODAL EXAMPLES EXPLORER THEME! */
.gradio-container {{
    background: linear-gradient(135deg, {MODAL_GREEN}15 0%, {MODAL_LIGHT_GREEN}15 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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

.gr-dropdown, .gr-textbox {{
    border: 2px solid {MODAL_GREEN} !important;
    border-radius: 12px !important;
    background: white !important;
}}

.gr-dropdown:focus, .gr-textbox:focus {{
    border-color: {MODAL_LIGHT_GREEN} !important;
    box-shadow: 0 0 0 4px {MODAL_GREEN}30 !important;
}}

/* Code blocks styling */
.gr-code {{
    border: 2px solid {MODAL_GREEN} !important;
    border-radius: 12px !important;
    background: #f8f9fa !important;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace !important;
}}

/* Markdown styling */
.gr-markdown {{
    background: white !important;
    border-radius: 12px !important;
    padding: 20px !important;
    border: 1px solid {MODAL_GREEN}40 !important;
}}

.gr-markdown h1, .gr-markdown h2, .gr-markdown h3 {{
    color: {MODAL_GREEN} !important;
}}

.gr-markdown code {{
    background: {MODAL_GREEN}20 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}}

.gr-markdown pre {{
    background: #f8f9fa !important;
    border: 1px solid {MODAL_GREEN}40 !important;
    border-radius: 8px !important;
    padding: 15px !important;
}}

h1 {{
    color: {MODAL_GREEN} !important;
    text-shadow: 0 2px 4px rgba(0, 210, 106, 0.3) !important;
    text-align: center !important;
    font-size: 2.5em !important;
}}
"""

async def load_folders():
    """Load all folders from Modal examples repository."""
    try:
        folders = await github_api.get_all_folders()

        if not folders:
            # If no folders found, return error dropdown
            return gr.update(
                choices=["❌ No folders found or connection failed"],
                value="❌ No folders found or connection failed"
            )

        folder_choices = [f"📁 {folder['name']}" for folder in folders]

        # Always start with root folder selected
        root_choice = "📁 root"
        if root_choice in folder_choices:
            default_value = root_choice
        else:
            default_value = folder_choices[0] if folder_choices else None

        return gr.update(
            choices=folder_choices,
            value=default_value,
            interactive=True
        )
    except Exception as e:
        print(f"🚨 Error loading folders: {e}")
        return gr.update(
            choices=["❌ Error loading folders - check connection"],
            value="❌ Error loading folders - check connection"
        )

async def load_python_files(folder_choice):
    """Load Python files for selected folder."""
    if not folder_choice or folder_choice.startswith("❌"):
        return gr.update(choices=["📝 Select a folder first"], value="📝 Select a folder first")

    try:
        # Extract folder name from choice
        folder_name = folder_choice.replace("📁 ", "")

        # Handle root folder specially
        if folder_name == "root":
            folder_name = ""  # Empty string for repository root

        print(f"🔍 Loading Python files for folder: '{folder_name}'")

        # Get Python files in the folder
        python_files = await github_api.get_python_files_in_folder(folder_name)

        if python_files:
            file_choices = [f"🐍 {file['name']}" for file in python_files]
            print(f"✅ Found {len(python_files)} Python files in '{folder_name}'")
            print(f"📝 Creating dropdown with choices: {file_choices}")

            # Return update instead of new dropdown
            return gr.update(
                choices=file_choices,
                value=file_choices[0] if file_choices else None,
                interactive=True
            )
        else:
            folder_display = "root" if folder_name == "" else folder_name
            print(f"📝 No Python files found in '{folder_display}'")

            # Return update instead of new dropdown
            return gr.update(
                choices=[f"📝 No Python files found in {folder_display}"],
                value=f"📝 No Python files found in {folder_display}",
                interactive=True
            )

    except Exception as e:
        print(f"🚨 Error loading Python files for '{folder_choice}': {e}")
        return gr.update(
            choices=["❌ Error loading files - try again"],
            value="❌ Error loading files - try again"
        )

async def load_readme_content(folder_choice):
    """Load README content for selected folder."""
    if not folder_choice or folder_choice.startswith("❌"):
        return "📝 Select a folder to see its README content!"

    try:
        # Extract folder name from choice
        folder_name = folder_choice.replace("📁 ", "")

        # Handle root folder specially
        if folder_name == "root":
            folder_name = ""  # Empty string for repository root

        folder_display = "root" if folder_name == "" else folder_name
        print(f"📚 Loading README for folder: '{folder_display}'")

        # Get README content
        readme_content = await github_api.get_readme_content(folder_name)

        if readme_content:
            print(f"✅ README loaded for '{folder_display}'")
            return readme_content
        else:
            print(f"📄 No README found for '{folder_display}'")
            return f"""# 📄 No README Available

No README.md file found for the **{folder_display}** folder.

This folder might contain example code without documentation, or the README might be located elsewhere.

💡 **Tip:** Check the Python files in this folder to see what examples are available!"""

    except Exception as e:
        print(f"🚨 Error loading README for '{folder_choice}': {e}")
        return f"""# ❌ Error Loading README

Could not load README for this folder.

**Error:** {str(e)}

💡 **Try:** Refreshing the folders or selecting a different folder."""

async def load_python_file_content(folder_choice, file_choice):
    """Load content of selected Python file."""
    if not folder_choice or not file_choice or folder_choice.startswith("❌") or file_choice.startswith(("📝", "❌")):
        return "🐍 Select a folder and Python file to view its content!"

    try:
        # Extract names from choices
        folder_name = folder_choice.replace("📁 ", "")
        file_name = file_choice.replace("🐍 ", "")

        # Handle root folder specially
        if folder_name == "root":
            file_path = file_name  # File is in repository root
        else:
            file_path = f"{folder_name}/{file_name}"

        # Get file content
        file_content = await github_api.get_file_content(file_path)

        if file_content:
            return file_content
        else:
            return f"📄 Could not load content for '{file_path}'"

    except Exception as e:
        print(f"Error loading file content: {e}")
        return f"❌ Error loading file: {str(e)}"

def sync_load_folders():
    """Sync wrapper for loading folders."""
    try:
        # Check if there's already an event loop running
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an async context, use a different approach
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_async_load_folders)
                return future.result()
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(load_folders())
            finally:
                loop.close()
    except Exception as e:
        print(f"🚨 Error in sync_load_folders: {e}")
        return gr.update(choices=["❌ Error loading folders"], value="❌ Error loading folders")

def _run_async_load_folders():
    """Helper function to run async load_folders in a new thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(load_folders())
    finally:
        loop.close()

def sync_load_python_files(folder_choice):
    """Sync wrapper for loading Python files."""
    try:
        # Check if there's already an event loop running
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an async context, use a different approach
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_async_load_python_files, folder_choice)
                return future.result()
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(load_python_files(folder_choice))
            finally:
                loop.close()
    except Exception as e:
        print(f"🚨 Error in sync_load_python_files: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return gr.update(choices=["❌ Error loading files"], value="❌ Error loading files")

def _run_async_load_python_files(folder_choice):
    """Helper function to run async load_python_files in a new thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(load_python_files(folder_choice))
    finally:
        loop.close()

def sync_load_readme_content(folder_choice):
    """Sync wrapper for loading README content."""
    try:
        # Check if there's already an event loop running
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an async context, use a different approach
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_async_load_readme_content, folder_choice)
                return future.result()
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(load_readme_content(folder_choice))
            finally:
                loop.close()
    except Exception as e:
        print(f"🚨 Error in sync_load_readme_content: {e}")
        return f"❌ Error loading README: {str(e)}"

def _run_async_load_readme_content(folder_choice):
    """Helper function to run async load_readme_content in a new thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(load_readme_content(folder_choice))
    finally:
        loop.close()

def sync_load_python_file_content(folder_choice, file_choice):
    """Sync wrapper for loading Python file content."""
    try:
        # Check if there's already an event loop running
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an async context, use a different approach
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_async_load_python_file_content, folder_choice, file_choice)
                return future.result()
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(load_python_file_content(folder_choice, file_choice))
            finally:
                loop.close()
    except Exception as e:
        print(f"🚨 Error in sync_load_python_file_content: {e}")
        return f"❌ Error loading file content: {str(e)}"

def _run_async_load_python_file_content(folder_choice, file_choice):
    """Helper function to run async load_python_file_content in a new thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(load_python_file_content(folder_choice, file_choice))
    finally:
        loop.close()

def create_modal_examples_explorer():
    """Create the Modal Examples Explorer interface."""

    with gr.Blocks(css=modal_css, title="🚀💚 Modal Examples Explorer 💚🚀") as demo:

        # Epic header
        gr.Markdown("""
        # 🚀💚 MODAL EXAMPLES EXPLORER 💚🚀
        ### *Dynamic browser for Modal's incredible GitHub examples!*

        **🎯 LIVE GITHUB INTEGRATION** | **📁 AUTO-DISCOVERY** | **🐍 PYTHON FILE VIEWER** | **📚 README RENDERER**

        *Explore [modal-labs/modal-examples](https://github.com/modal-labs/modal-examples) in real-time!*
        """)

        with gr.Row():
            with gr.Column(scale=1):
                # Folder selection
                gr.Markdown("### 📁 Choose a Folder")
                folder_dropdown = gr.Dropdown(
                    label="📂 Modal Examples Folders",
                    choices=["🔄 Loading folders..."],
                    value="🔄 Loading folders...",
                    interactive=True
                )

                refresh_folders_btn = gr.Button("🔄 Refresh Folders", variant="secondary")

                # Python file selection
                gr.Markdown("### 🐍 Choose a Python File")
                python_file_dropdown = gr.Dropdown(
                    label="🐍 Python Files",
                    choices=["📝 Select a folder first"],
                    value="📝 Select a folder first",
                    interactive=True
                )

                # Action buttons
                gr.Markdown("### 🚀 Actions")
                deploy_btn = gr.Button("🚀 Deploy This Example!", variant="primary", size="lg")
                view_on_github_btn = gr.Button("👀 View on GitHub", variant="secondary")

                # Output areas for button actions
                deploy_instructions = gr.Markdown(
                    value="📝 Select a folder and Python file, then click 'Deploy This Example!' to get deployment instructions.",
                    label="🚀 Deployment Instructions"
                )

                github_instructions = gr.Markdown(
                    value="👀 Select a file to get GitHub link",
                    label="👀 GitHub Link"
                )

            with gr.Column(scale=2):
                # Content display area
                with gr.Tabs():
                    with gr.TabItem("📚 README"):
                        readme_content = gr.Markdown(
                            value="📝 Select a folder to see its README content!",
                            label="📚 README Content"
                        )

                    with gr.TabItem("🐍 Python Code"):
                        python_content = gr.Code(
                            value="🐍 Select a folder and Python file to view its content!",
                            language="python",
                            label="🐍 Python File Content"
                        )

                    with gr.TabItem("ℹ️ About"):
                        gr.Markdown("""
                        ## 🎯 About Modal Examples Explorer

                        This app dynamically fetches and displays examples from the official
                        [Modal Examples Repository](https://github.com/modal-labs/modal-examples).

                        ### 🚀 Features:
                        - **📁 Live Folder Discovery**: Automatically detects all example categories
                        - **🐍 Python File Browser**: View any Python example file
                        - **📚 README Rendering**: Read documentation for each example category
                        - **🔄 Real-time Updates**: Always shows the latest examples from GitHub
                        - **💚 Beautiful Modal Styling**: Designed with Modal's signature green theme

                        ### 🛠️ How to Use:
                        1. **📁 Select a folder** from the dropdown (e.g., "10_integrations")
                        2. **🐍 Choose a Python file** to explore
                        3. **📚 Read the README** to understand the examples
                        4. **🚀 Deploy with Modal-for-noobs** when ready!

                        ### 💚 Powered by Modal-for-noobs
                        This explorer is built with the same technology that powers our
                        deployment platform - Modal's incredible serverless infrastructure!

                        ---

                        💚 **Made with <3 by [Neurotic Coder](https://github.com/arthrod) and assisted by Beloved Claude** ✨
                        """)

        # Event handlers

        # Load folders on startup
        demo.load(
            fn=sync_load_folders,
            outputs=folder_dropdown
        )

        # Refresh folders button
        refresh_folders_btn.click(
            fn=sync_load_folders,
            outputs=folder_dropdown
        )

        # Update Python files when folder changes
        folder_dropdown.change(
            fn=sync_load_python_files,
            inputs=folder_dropdown,
            outputs=python_file_dropdown
        )

        # Update README when folder changes
        folder_dropdown.change(
            fn=sync_load_readme_content,
            inputs=folder_dropdown,
            outputs=readme_content
        )

        # Update Python content when file changes
        python_file_dropdown.change(
            fn=sync_load_python_file_content,
            inputs=[folder_dropdown, python_file_dropdown],
            outputs=python_content
        )

        # Deploy button functionality
        def handle_deploy_click(folder_choice, file_choice):
            """Handle deploy button click."""
            if not folder_choice or not file_choice or folder_choice.startswith(("❌", "🔄")) or file_choice.startswith(("📝", "❌")):
                return "⚠️ Please select both a folder and a Python file first!"

            folder_name = folder_choice.replace("📁 ", "")
            file_name = file_choice.replace("🐍 ", "")

            if folder_name == "root":
                file_path = file_name
                deploy_cmd = f"./mn.sh {file_name} --optimized"
                github_url = f"https://github.com/modal-labs/modal-examples/blob/main/{file_name}"
            else:
                file_path = f"{folder_name}/{file_name}"
                deploy_cmd = f"./mn.sh {file_path} --optimized"
                github_url = f"https://github.com/modal-labs/modal-examples/blob/main/{file_path}"

            instructions = f"""🚀 **Ready to Deploy: {file_path}**

**Option 1: Quick Deploy (Recommended)**
```bash
{deploy_cmd}
```

**Option 2: Wizard Mode (Guided)**
```bash
./mn.sh {file_path} --wizard
```

**Option 3: Brazilian Mode (Huehuehue!)**
```bash
./mn.sh {file_path} --optimized --br-huehuehue
```

📋 **Steps:**
1. Copy the command above
2. Run it in your modal-for-noobs directory
3. Watch the magic happen! ✨

🔗 **View on GitHub:** [See original file]({github_url})

💡 **Pro tip:** Use `mn --milk-logs` to view deployment logs after deploying!
"""
            return instructions

        deploy_btn.click(
            fn=handle_deploy_click,
            inputs=[folder_dropdown, python_file_dropdown],
            outputs=deploy_instructions
        )

        # View on GitHub button functionality
        def handle_github_click(folder_choice, file_choice):
            """Handle view on GitHub button click."""
            if not folder_choice or not file_choice or folder_choice.startswith(("❌", "🔄")) or file_choice.startswith(("📝", "❌")):
                return "⚠️ Please select both a folder and a Python file first!"

            folder_name = folder_choice.replace("📁 ", "")
            file_name = file_choice.replace("🐍 ", "")

            if folder_name == "root":
                github_url = f"https://github.com/modal-labs/modal-examples/blob/main/{file_name}"
            else:
                github_url = f"https://github.com/modal-labs/modal-examples/blob/main/{folder_name}/{file_name}"

            return f"🔗 **View on GitHub:** [Open {file_name}]({github_url})"

        view_on_github_btn.click(
            fn=handle_github_click,
            inputs=[folder_dropdown, python_file_dropdown],
            outputs=github_instructions
        )

    return demo

# Create the demo
demo = create_modal_examples_explorer()

if __name__ == "__main__":
    print("🚀💚 MODAL EXAMPLES EXPLORER STARTING! 💚🚀")
    print("📁 Loading Modal examples from GitHub...")
    print("💚 Made with <3 by Neurotic Coder and assisted by Beloved Claude!")

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
    scaledown_window=1200
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
