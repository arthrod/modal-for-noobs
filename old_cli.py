"""Modal-for-noobs CLI - Beautiful, async-first Gradio deployment to Modal."""

import asyncio
import os
from pathlib import Path
from typing import Annotated, Optional

import typer
import uvloop
from loguru import logger
from rich import print as rprint
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from modal_for_noobs.config import Config, config
from modal_for_noobs.config_loader import config_loader
from modal_for_noobs.huggingface import HuggingFaceSpacesMigrator
from modal_for_noobs.modal_deploy import ModalDeployer
import secrets

# Modal's signature green theme
MODAL_GREEN = "#00D26A"
MODAL_DARK_GREEN = "#00A855"
MODAL_LIGHT_GREEN = "#4AE88A"

app = typer.Typer(
    name="modal-for-noobs",
    help="[bold green]🚀 Deploy Gradio apps to Modal with zero configuration[/bold green]",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)

console = Console()


def print_modal_banner(br_huehuehue: bool = False):
    """Print beautiful Modal-themed banner with ego boost."""
    # Load marketing content
    marketing = config_loader.load_modal_marketing()
    
    banner_text = Text()
    banner_text.append("🚀 ", style="bold white")
    banner_text.append("MODAL", style=f"bold {MODAL_GREEN}")
    banner_text.append("-FOR-", style="bold white")
    banner_text.append("NOOBS", style=f"bold {MODAL_LIGHT_GREEN}")
    banner_text.append(" 🚀", style="bold white")
    
    # Add ego boost content
    if br_huehuehue and "portuguese" in marketing:
        hero_content = marketing["portuguese"].get("hero", "")
        features = marketing["portuguese"].get("features", [])
    else:
        hero_content = marketing.get("banners", {}).get("hero", "")
        features = marketing.get("features", [])
    
    if hero_content:
        banner_text.append(f"\n\n{hero_content}", style=f"bold {MODAL_LIGHT_GREEN}")
    
    # Add a random feature highlight
    if features:
        feature = secrets.choice(features)
        banner_text.append(f"\n{feature}", style="bold white")
    
    rprint(Panel(
        Align.center(banner_text),
        style=f"{MODAL_GREEN}",
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))


def print_success(message: str):
    """Print success message with Modal green styling."""
    rprint(f"[{MODAL_GREEN}]✅ {message}[/{MODAL_GREEN}]")


def print_error(message: str):
    """Print error message."""
    rprint(f"[red]❌ {message}[/red]")


def print_warning(message: str):
    """Print warning message."""
    rprint(f"[yellow]⚠️  {message}[/yellow]")


def print_info(message: str):
    """Print info message with Modal styling."""
    rprint(f"[{MODAL_LIGHT_GREEN}]ℹ️  {message}[/{MODAL_LIGHT_GREEN}]")


@app.command()
def deploy(
    app_file: Annotated[Path, typer.Argument(help="Path to your Gradio app file")],
    minimum: Annotated[bool, typer.Option("--minimum", help="Deploy with minimal dependencies (CPU only)")] = False,
    optimized: Annotated[bool, typer.Option("--optimized", help="Deploy with ML libraries and GPU support")] = False,
    gra_jupy: Annotated[bool, typer.Option("--gra-jupy", help="Deploy with Gradio + Jupyter combo for beautiful notebooks")] = False,
    wizard: Annotated[bool, typer.Option("--wizard", help="Interactive step-by-step deployment wizard")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Generate files without deploying")] = False,
    test_deploy: Annotated[bool, typer.Option("--test-deploy", help="Deploy with immediate kill for testing")] = False,
    deploy_without_expiration: Annotated[bool, typer.Option("--deploy-without-expiration", help="Deploy without auto-kill (dangerous!)")] = False,
    br_huehuehue: Annotated[bool, typer.Option("--br-huehuehue", help="Modo brasileiro com muito huehuehue! 🇧🇷")] = False,
    env_file: Annotated[str, typer.Option("--env-file", help="Path to environment file")] = ".env",
) -> None:
    """🚀 Deploy your Gradio app to Modal like a boss!"""
    
    print_modal_banner(br_huehuehue)
    
    # Handle wizard mode
    if wizard:
        wizard_text = Text()
        wizard_text.append("🧙‍♂️ DEPLOYMENT WIZARD 🧙‍♂️", style=f"bold {MODAL_GREEN}")
        wizard_text.append("\n✨ Let's walk through your deployment step by step!", style="bold white")
        
        rprint(Panel(
            Align.center(wizard_text),
            border_style=f"{MODAL_GREEN}",
            padding=(1, 2)
        ))
        
        # Step 1: Confirm app file
        rprint(f"\n[{MODAL_GREEN}]📱 Step 1: App File[/{MODAL_GREEN}]")
        confirmed_file = typer.confirm(f"Deploy this Gradio app: {app_file}?", default=True)
        if not confirmed_file:
            print_error("Deployment cancelled!")
            raise typer.Exit(0)
        
        # Step 2: Choose deployment mode
        rprint(f"\n[{MODAL_GREEN}]⚡ Step 2: Deployment Mode[/{MODAL_GREEN}]")
        rprint("Choose your deployment mode:")
        rprint(f"  [bold]minimum[/bold] - CPU only, basic packages (faster, cheaper)")
        rprint(f"  [bold]optimized[/bold] - GPU + ML libraries (more powerful)")
        
        mode_choice = typer.prompt(
            "Which mode do you want? [minimum/optimized]",
            default='minimum'
        )
        
        # Validate choice
        if mode_choice not in ['minimum', 'optimized']:
            print_warning(f"Invalid choice '{mode_choice}', defaulting to 'minimum'")
            mode_choice = 'minimum'
        
        # Step 3: GPU confirmation if optimized
        if mode_choice == 'optimized':
            rprint(f"\n[{MODAL_GREEN}]🚀 Step 3: GPU Configuration[/{MODAL_GREEN}]")
            gpu_confirm = typer.confirm("Enable GPU support? (recommended for ML workloads)", default=True)
            if not gpu_confirm:
                mode_choice = 'minimum'
                print_warning("Switching to minimum mode (CPU only)")
        
        # Step 4: Check for requirements.txt in drop folder
        rprint(f"\n[{MODAL_GREEN}]📦 Step 4: Dependencies[/{MODAL_GREEN}]")
        drop_folder = Path("drop-ur-precious-stuff-here")
        requirements_file = drop_folder / "requirements.txt"
        
        if requirements_file.exists():
            print_success(f"Found requirements.txt in {drop_folder}!")
            rprint(f"  📄 File: {requirements_file}")
            
            # Show contents preview
            try:
                requirements_content = requirements_file.read_text().strip()
                if requirements_content:
                    lines = requirements_content.split('\n')[:5]  # Show first 5 lines
                    rprint("  📋 Contents preview:")
                    for line in lines:
                        if line.strip():
                            rprint(f"    - {line.strip()}")
                    if len(requirements_content.split('\n')) > 5:
                        rprint(f"    ... and {len(requirements_content.split('\n')) - 5} more packages")
                else:
                    rprint("  📝 File is empty")
            except Exception:
                rprint("  ❌ Could not read file contents")
            
            use_requirements = typer.confirm("Include these dependencies in your deployment?", default=True)
        else:
            rprint(f"  📂 No requirements.txt found in {drop_folder}")
            rprint("  💡 Pro tip: Drop your requirements.txt there for automatic detection!")
            use_requirements = False
        
        # Step 5: Dry run option
        rprint(f"\n[{MODAL_GREEN}]🏃 Step 5: Deployment Type[/{MODAL_GREEN}]")
        wizard_dry_run = typer.confirm("Do a dry run first? (generate files without deploying)", default=False)
        
        # Summary
        rprint(f"\n[{MODAL_GREEN}]📋 Deployment Summary[/{MODAL_GREEN}]")
        rprint(f"  📱 App: {app_file}")
        rprint(f"  ⚡ Mode: {mode_choice.upper()}")
        rprint(f"  📦 Requirements: {'INCLUDED' if use_requirements else 'DEFAULT ONLY'}")
        rprint(f"  🏃 Dry Run: {'YES' if wizard_dry_run else 'NO'}")
        
        final_confirm = typer.confirm("\nLooks good? Let's deploy! 🚀", default=True)
        if not final_confirm:
            print_error("Deployment cancelled!")
            raise typer.Exit(0)
        
        mode = mode_choice
        dry_run = wizard_dry_run
        # Pass requirements file path to deployer if user wants it
        requirements_path = requirements_file if use_requirements else None
    else:
        # Determine mode from flags
        if gra_jupy:
            mode = "gra_jupy"
        elif optimized:
            mode = "optimized"
        else:
            mode = "minimum"
        # Check for requirements in non-wizard mode too
        drop_folder = Path("drop-ur-precious-stuff-here")
        requirements_file = drop_folder / "requirements.txt"
        requirements_path = requirements_file if requirements_file.exists() else None
    
    # Beautiful deployment info panel
    info_text = Text()
    info_text.append("📁 App: ", style="bold")
    info_text.append(str(app_file), style=f"{MODAL_GREEN}")
    info_text.append("\n⚡ Mode: ", style="bold")
    info_text.append(mode.upper(), style=f"bold {MODAL_LIGHT_GREEN}")
    
    if dry_run:
        info_text.append("\n🏃 Dry Run: ", style="bold")
        info_text.append("ON", style="yellow")
    
    rprint(Panel(
        info_text,
        title="[bold]🎯 Deployment Configuration[/bold]",
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))
    
    # Determine timeout
    if deploy_without_expiration:
        timeout_minutes = 24 * 60  # 24 hours max
    else:
        timeout_minutes = 60  # Default 1 hour
    
    # Run async deployment
    uvloop.run(_deploy_async(app_file, mode, dry_run, env_file, requirements_path, timeout_minutes, test_deploy, br_huehuehue))


@app.command()
def mn(  # pragma: no cover - legacy alias not exercised in tests
    app_file: Annotated[Path, typer.Argument(help="Path to your Gradio app file")],
    optimized: Annotated[bool, typer.Option("--optimized", "-o", help="Deploy with GPU + ML libraries")] = False,
    gra_jupy: Annotated[bool, typer.Option("--gra-jupy", help="Deploy with Gradio + Jupyter combo")] = False,
    test_deploy: Annotated[bool, typer.Option("--test-deploy", help="Deploy with immediate kill for testing")] = False,
    deploy_without_expiration: Annotated[bool, typer.Option("--deploy-without-expiration", help="Deploy without auto-kill")] = False,
    br_huehuehue: Annotated[bool, typer.Option("--br-huehuehue", help="Modo brasileiro! 🇧🇷")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Generate files without deploying")] = False,
) -> None:
    """⚡ Quick deploy (alias for deploy) - because noobs love shortcuts!"""
    
    print_modal_banner(br_huehuehue)
    
    # Determine mode from flags
    if gra_jupy:
        mode = "gra_jupy"
    elif optimized:
        mode = "optimized"
    else:
        mode = "minimum"
    
    # Quick deploy message
    quick_text = Text()
    quick_text.append("⚡ QUICK DEPLOY ⚡", style=f"bold {MODAL_GREEN}")
    quick_text.append(f"\n📱 {app_file}", style="bold white")
    quick_text.append(f" → {mode.upper()}", style=f"bold {MODAL_LIGHT_GREEN}")
    
    rprint(Panel(
        Align.center(quick_text),
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))
    
    # Check for requirements in quick mode too
    drop_folder = Path("drop-ur-precious-stuff-here")
    requirements_file = drop_folder / "requirements.txt"
    requirements_path = requirements_file if requirements_file.exists() else None
    
    # Determine timeout
    if deploy_without_expiration:
        timeout_minutes = 24 * 60  # 24 hours max
    else:
        timeout_minutes = 60  # Default 1 hour
    
    # Run deployment
    uvloop.run(_deploy_async(app_file, mode, dry_run, ".env", requirements_path, timeout_minutes, test_deploy, br_huehuehue))


@app.command()
def time_to_get_serious(  # pragma: no cover - not covered in tests
    spaces_url: Annotated[str, typer.Argument(help="HuggingFace Spaces URL")] = "https://huggingface.co/spaces/arthrod/tucano-voraz-old",
    optimized: Annotated[bool, typer.Option("--optimized", help="Deploy with GPU and ML libraries")] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Generate files without deploying")] = False,
) -> None:
    """💪 Time to get SERIOUS! Migrate HuggingFace Spaces to Modal like a PRO!"""
    
    print_modal_banner()
    
    # Epic migration banner
    serious_text = Text()
    serious_text.append("💪 TIME TO GET SERIOUS! 💪", style=f"bold {MODAL_GREEN}")
    serious_text.append("\n🔥 HuggingFace → Modal Migration 🔥", style=f"bold {MODAL_LIGHT_GREEN}")
    serious_text.append(f"\n🎯 Target: ", style="bold")
    serious_text.append(spaces_url, style=f"{MODAL_GREEN}")
    
    rprint(Panel(
        Align.center(serious_text),
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))
    
    # Run async migration
    uvloop.run(_migrate_hf_spaces_async(spaces_url, optimized, dry_run))


@app.command()
<<<<<<< HEAD:old_cli.py
<<<<<<< HEAD
def auth(  # pragma: no cover - requires user credentials
    token_id: Annotated[Optional[str], typer.Option("--token-id", help="Modal token ID")] = None,
    token_secret: Annotated[Optional[str], typer.Option("--token-secret", help="Modal token secret")] = None,
=======
def auth(
    token_id: Annotated[str | None, typer.Option("--token-id", help="Modal token ID")] = None,
    token_secret: Annotated[str | None, typer.Option("--token-secret", help="Modal token secret")] = None,
>>>>>>> 78decec (feat: add changes)
=======
def auth(
    token_id: Annotated[str | None, typer.Option("--token-id", help="Modal token ID")] = None,
    token_secret: Annotated[str | None, typer.Option("--token-secret", help="Modal token secret")] = None,
>>>>>>> 78decec (feat: add changes):src/modal_for_noobs/cli.py
) -> None:
    """🔐 Setup Modal authentication - get your keys ready!"""
    
    print_modal_banner()
    
    auth_text = Text()
    auth_text.append("🔐 MODAL AUTHENTICATION SETUP 🔐", style=f"bold {MODAL_GREEN}")
    auth_text.append("\n🗝️  Setting up your Modal credentials...", style="bold white")
    
    rprint(Panel(
        Align.center(auth_text),
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))
    
    uvloop.run(_setup_auth_async(token_id, token_secret))


@app.command()
<<<<<<< HEAD:old_cli.py
<<<<<<< HEAD
def kill_a_deployment(  # pragma: no cover - interactive helper
    deployment_id: Annotated[str | None, typer.Argument(help="Deployment ID to kill")] = None,
=======
def kill_a_deployment(
    deployment_id: Annotated[str | None, typer.Argument(help="Deployment ID to terminate")] = None,
>>>>>>> 78decec (feat: add changes)
=======
def kill_a_deployment(
    deployment_id: Annotated[str | None, typer.Argument(help="Deployment ID to terminate")] = None,
>>>>>>> 78decec (feat: add changes):src/modal_for_noobs/cli.py
    br_huehuehue: Annotated[bool, typer.Option("--br-huehuehue", help="Modo brasileiro com muito huehuehue! 🇧🇷")] = False,
) -> None:
    """💀 Completely terminate deployments and remove containers from servers!"""
    
    print_modal_banner(br_huehuehue)
    
    if br_huehuehue:
        kill_text = Text()
        kill_text.append("💀 MATADOR DE DEPLOYMENTS 💀", style=f"bold {MODAL_GREEN}")
        kill_text.append("\n🇧🇷 Hora de matar alguns deployments! Huehuehue! 🇧🇷", style="bold white")
    else:
        kill_text = Text()
        kill_text.append("💀 DEPLOYMENT KILLER 💀", style=f"bold {MODAL_GREEN}")
        kill_text.append("\n⚰️ Time to put some deployments to rest...", style="bold white")
    
    rprint(Panel(
        Align.center(kill_text),
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))
    
    uvloop.run(_kill_deployment_async(deployment_id, br_huehuehue))


@app.command()
<<<<<<< HEAD:old_cli.py
<<<<<<< HEAD
def sanity_check(  # pragma: no cover - optional helper
=======
=======
>>>>>>> 78decec (feat: add changes):src/modal_for_noobs/cli.py
def milk_logs(
    app_name: Annotated[str | None, typer.Argument(help="App name to get logs from")] = None,
    follow: Annotated[bool, typer.Option("--follow", "-f", help="Follow logs in real-time")] = False,
    lines: Annotated[int, typer.Option("--lines", "-n", help="Number of log lines to show")] = 100,
    br_huehuehue: Annotated[bool, typer.Option("--br-huehuehue", help="Modo brasileiro! 🇧🇷")] = False,
) -> None:
    """🥛 Milk the logs from your Modal deployments - fresh and creamy!"""
    
    print_modal_banner(br_huehuehue)
    
    if br_huehuehue:
        milk_text = Text()
        milk_text.append("🥛 ORDENHADOR DE LOGS 🥛", style=f"bold {MODAL_GREEN}")
        milk_text.append("\n🇧🇷 Hora de ordenhar alguns logs fresquinhos! Huehuehue! 🇧🇷", style="bold white")
    else:
        milk_text = Text()
        milk_text.append("🥛 LOG MILKER 🥛", style=f"bold {MODAL_GREEN}")
        milk_text.append("\n🧑‍🌾 Time to milk some fresh, creamy logs from Modal!", style="bold white")
    
    rprint(Panel(
        Align.center(milk_text),
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))
    
    uvloop.run(_milk_logs_async(app_name, follow, lines, br_huehuehue))


@app.command()
def sanity_check(
>>>>>>> 78decec (feat: add changes)
    br_huehuehue: Annotated[bool, typer.Option("--br-huehuehue", help="Modo brasileiro com muito huehuehue! 🇧🇷")] = False,
) -> None:
    """🔍 Check what's deployed in your Modal account - sanity check time!"""
    
    print_modal_banner(br_huehuehue)
    
    if br_huehuehue:
        sanity_text = Text()
        sanity_text.append("🔍 VERIFICAÇÃO DE SANIDADE MODAL 🔍", style=f"bold {MODAL_GREEN}")
        sanity_text.append("\n🇧🇷 Verificando seus deployments... huehuehue! 🇧🇷", style="bold white")
    else:
        sanity_text = Text()
        sanity_text.append("🔍 MODAL SANITY CHECK 🔍", style=f"bold {MODAL_GREEN}")
        sanity_text.append("\n🧠 Checking what's deployed in your account...", style="bold white")
    
    rprint(Panel(
        Align.center(sanity_text),
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))
    
    uvloop.run(_sanity_check_async(br_huehuehue))


@app.command("config")
def config_info(
    env_file: Annotated[str, typer.Option("--env-file", help="Path to environment file")] = ".env",
) -> None:
    """📋 Show your current configuration - knowledge is power!"""
    
    print_modal_banner()
    
    # Load config
    if env_file != ".env":
        global config
        config = Config(env_file)
    
    config_text = Text()
    # The tests look for the phrase "Current Configuration" so include it in the
    # header to remain backwards compatible.
    config_text.append("📋 Current Configuration 📋", style=f"bold {MODAL_GREEN}")
    config_text.append(f"\n🌍 Environment: ", style="bold")
    config_text.append(config.environment, style=f"{MODAL_LIGHT_GREEN}")
    config_text.append(f"\n🐛 Debug Mode: ", style="bold")
    config_text.append(str(config.debug), style=f"{MODAL_LIGHT_GREEN}")
    config_text.append(f"\n📝 Log Level: ", style="bold")
    config_text.append(config.log_level, style=f"{MODAL_LIGHT_GREEN}")

    unkey_config = config.get_unkey_config()
    config_text.append(f"\n🔐 Unkey: ", style="bold")
    if unkey_config["root_key"]:
        config_text.append("✅ CONFIGURED", style=f"bold {MODAL_GREEN}")
    else:
        config_text.append("❌ NOT CONFIGURED", style="bold red")
    
    rprint(Panel(
        config_text,
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))


<<<<<<< HEAD:old_cli.py
<<<<<<< HEAD
# ---------------------------------------------------------------------------
# Compatibility alias for the old `config-info` command used in the tests.
# ---------------------------------------------------------------------------

@app.command("config-info", hidden=True)
def config_info_alias(env_file: Annotated[str, typer.Option("--env-file", help="Path to environment file")] = ".env") -> None:
    """Backward compatible wrapper calling :func:`config_info`."""
    config_info(env_file=env_file)


@app.command()
def mcp(  # pragma: no cover - not tested
    port: Annotated[int, typer.Option("--port", help="Port for the MCP server")] = 8000,
) -> None:
    """Launch a minimal MCP server for Claude, Cursor, Roo and VSCode."""

    print_modal_banner()

    from mcp.server.fastmcp.server import FastMCP

    typer.echo(f"Starting MCP server on port {port} ...")
    server = FastMCP(port=port)
    server.run("sse")
=======
=======
>>>>>>> 78decec (feat: add changes):src/modal_for_noobs/cli.py
@app.command("run-examples")
def run_examples(
    example_name: Annotated[str | None, typer.Argument(help="Example to run (leave empty to list all)")] = None,
    optimized: Annotated[bool, typer.Option("--optimized", help="Deploy with GPU + ML libraries")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Generate files without deploying")] = False,
    br_huehuehue: Annotated[bool, typer.Option("--br-huehuehue", help="Modo brasileiro! 🇧🇷")] = False,
) -> None:
    """🎯 Run built-in examples - perfect for testing and learning!"""
    
    print_modal_banner(br_huehuehue)
    
    # Get examples directory
    examples_dir = Path(__file__).parent / "examples"
    
    if not examples_dir.exists():
        print_error("Examples directory not found!")
        return
    
    # Get all Python files in examples directory
    example_files = list(examples_dir.glob("*.py"))
    available_examples = [f.stem for f in example_files if not f.name.startswith("__")]
    
    if not example_name:
        # List all available examples
        if br_huehuehue:
            examples_text = Text()
            examples_text.append("🎯 EXEMPLOS DISPONÍVEIS 🎯", style=f"bold {MODAL_GREEN}")
            examples_text.append("\n🇧🇷 Escolha um exemplo para deployar! Huehuehue! 🇧🇷", style="bold white")
        else:
            examples_text = Text()
            examples_text.append("🎯 AVAILABLE EXAMPLES 🎯", style=f"bold {MODAL_GREEN}")
            examples_text.append("\n🚀 Choose an example to deploy and learn!", style="bold white")
        
        if available_examples:
            examples_text.append("\n\n📚 Examples:", style="bold")
            for example in sorted(available_examples):
                # Try to get description from the file
                example_file = examples_dir / f"{example}.py"
                description = _get_example_description(example_file)
                examples_text.append(f"\n  🎯 {example}", style=f"bold {MODAL_LIGHT_GREEN}")
                if description:
                    examples_text.append(f" - {description}", style="white")
            
            if br_huehuehue:
                examples_text.append("\n\n💡 Para rodar um exemplo:", style="bold")
                examples_text.append(f"\n  modal-for-noobs run-examples <nome-do-exemplo> --br-huehuehue", style=f"{MODAL_GREEN}")
            else:
                examples_text.append("\n\n💡 To run an example:", style="bold")
                examples_text.append(f"\n  modal-for-noobs run-examples <example-name> --optimized", style=f"{MODAL_GREEN}")
        else:
            if br_huehuehue:
                examples_text.append("\n\n❌ Nenhum exemplo encontrado! Huehuehue!", style="red")
            else:
                examples_text.append("\n\n❌ No examples found!", style="red")
        
        rprint(Panel(
            examples_text,
            border_style=f"{MODAL_GREEN}",
            padding=(1, 2)
        ))
        return
    
    # Check if example exists
    if example_name not in available_examples:
        if br_huehuehue:
            print_error(f"Exemplo '{example_name}' não encontrado! Huehuehue!")
            print_info("Use 'modal-for-noobs run-examples' para ver exemplos disponíveis")
        else:
            print_error(f"Example '{example_name}' not found!")
            print_info("Use 'modal-for-noobs run-examples' to see available examples")
        return
    
    # Deploy the example
    example_file = examples_dir / f"{example_name}.py"
    
    if br_huehuehue:
        deploy_text = Text()
        deploy_text.append("🚀 DEPLOYANDO EXEMPLO 🚀", style=f"bold {MODAL_GREEN}")
        deploy_text.append(f"\n🎯 Exemplo: {example_name}", style="bold white")
        deploy_text.append(f"\n📁 Arquivo: {example_file.name}", style=f"{MODAL_LIGHT_GREEN}")
        deploy_text.append("\n🇧🇷 Vamos nessa! Huehuehue! 🇧🇷", style="bold white")
    else:
        deploy_text = Text()
        deploy_text.append("🚀 DEPLOYING EXAMPLE 🚀", style=f"bold {MODAL_GREEN}")
        deploy_text.append(f"\n🎯 Example: {example_name}", style="bold white")
        deploy_text.append(f"\n📁 File: {example_file.name}", style=f"{MODAL_LIGHT_GREEN}")
        deploy_text.append("\n⚡ Let's go!", style="bold white")
    
    rprint(Panel(
        Align.center(deploy_text),
        border_style=f"{MODAL_GREEN}",
        padding=(1, 2)
    ))
    
    # Determine mode
    mode = "optimized" if optimized else "minimum"
    
    # Run deployment
    uvloop.run(_deploy_async(example_file, mode, dry_run, ".env", None, 60, False, br_huehuehue))


def _get_example_description(example_file: Path) -> str:
    """Extract description from example file docstring."""
    try:
        content = example_file.read_text()
        # Look for module docstring
        lines = content.split('\n')
        in_docstring = False
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('"""') or line.startswith("'''"):
                if in_docstring:
                    break  # End of docstring
                else:
                    in_docstring = True
                    # Check if it's a single line docstring
                    if line.count('"""') == 2 or line.count("'''") == 2:
                        desc = line.replace('"""', '').replace("'''", '').strip()
                        if desc:
                            return desc
                    continue
            elif in_docstring:
                if line and not line.startswith('#'):
                    description_lines.append(line)
                if len(description_lines) >= 1:  # Just get first line
                    break
        
        if description_lines:
            return description_lines[0]
    except Exception:
        pass
    
    return ""
<<<<<<< HEAD:old_cli.py
>>>>>>> 78decec (feat: add changes)
=======
>>>>>>> 78decec (feat: add changes):src/modal_for_noobs/cli.py


async def _deploy_async(
    app_file: Path, 
    mode: str, 
    dry_run: bool, 
    env_file: str, 
    requirements_path: Path | None = None, 
    timeout_minutes: int = 60, 
    test_deploy: bool = False, 
    br_huehuehue: bool = False
) -> None:
    """Async deployment logic with beautiful progress."""
    
    # Load configuration
    if env_file != ".env":
        global config
        config = Config(env_file)
    
    logger.info(f"Starting modal-for-noobs deployment in {config.environment} mode")
    
    deployer = ModalDeployer()

    # When running a dry run we simply generate the deployment file without
    # performing any Modal authentication steps. This keeps the tests fast and
    # avoids hitting the real Modal CLI.
    if dry_run:
        with Progress(
            SpinnerColumn(spinner_name="dots", style=f"{MODAL_GREEN}"),
            TextColumn("[progress.description]{task.description}", style="bold white"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("📝 Creating deployment file...", total=None)
            deployment_file = await deployer.create_modal_deployment_async(app_file, mode, requirements_path, timeout_minutes, test_deploy)
            progress.update(task, description="✅ Deployment file created!")

        print_success(f"Deployment file created: {deployment_file.name}")
        print_info("Dry run complete - files ready for deployment!")
        return

    # Normal deployment workflow requires authentication
    with Progress(
        SpinnerColumn(spinner_name="dots", style=f"{MODAL_GREEN}"),
        TextColumn("[progress.description]{task.description}", style="bold white"),
        console=console,
        transient=True,
    ) as progress:

        auth_task = progress.add_task("🔍 Checking Modal authentication...", total=None)

        if not await deployer.check_modal_auth_async():
            progress.update(auth_task, description="🔐 Setting up Modal authentication...")
            print_warning("No Modal credentials found - starting authentication setup!")

            if not await deployer.setup_modal_auth_async():
                print_error("Authentication failed!")
                raise typer.Exit(1)

        progress.update(auth_task, description="✅ Modal authentication verified!")

        # Create deployment file
        deploy_task = progress.add_task("📝 Creating deployment file...", total=None)
        deployment_file = await deployer.create_modal_deployment_async(app_file, mode, requirements_path, timeout_minutes, test_deploy)
        progress.update(deploy_task, description="✅ Deployment file created!")

    print_success("Authentication verified!")
    print_success(f"Deployment file created: {deployment_file.name}")
    
    # Deploy to Modal with progress
    with Progress(
        SpinnerColumn(spinner_name="earth", style=f"{MODAL_GREEN}"),
        TextColumn("[progress.description]{task.description}", style="bold white"),
        console=console,
    ) as progress:
        
        deploy_task = progress.add_task("🚀 Deploying to Modal...", total=None)
        url = await deployer.deploy_to_modal_async(deployment_file)
        progress.update(deploy_task, description="✅ Deployment complete!")
    
    # Success celebration!
    if url:
        if br_huehuehue:
            success_text = Text()
            success_text.append("🎉 DEPLOYMENT BEM-SUCEDIDO! HUEHUEHUE! 🎉", style=f"bold {MODAL_GREEN}")
            success_text.append("\n🌐 Seu app está ONLINE em:", style="bold white")
            success_text.append(f"\n{url}", style=f"bold {MODAL_LIGHT_GREEN}")
            success_text.append("\n\n🔥 Você oficialmente NÃO é mais um noob! HUEHUEHUE! 🔥", style=f"bold {MODAL_GREEN}")
        else:
            success_text = Text()
            success_text.append("🎉 DEPLOYMENT SUCCESSFUL! 🎉", style=f"bold {MODAL_GREEN}")
            success_text.append("\n🌐 Your app is LIVE at:", style="bold white")
            success_text.append(f"\n{url}", style=f"bold {MODAL_LIGHT_GREEN}")
            success_text.append("\n\n🔥 You're officially NOT a noob anymore! 🔥", style=f"bold {MODAL_GREEN}")
        
        rprint(Panel(
            Align.center(success_text),
            border_style=f"{MODAL_GREEN}",
            padding=(1, 2)
        ))
    else:
        if br_huehuehue:
            print_success("Deployment concluído com sucesso! Huehuehue!")
        else:
            print_success("Deployment completed successfully!")


async def _migrate_hf_spaces_async(spaces_url: str, optimized: bool, dry_run: bool) -> None:  # pragma: no cover - heavy network usage
    """Async HuggingFace Spaces migration with epic visuals."""
    
    migrator = HuggingFaceSpacesMigrator()
    
    with Progress(
        SpinnerColumn(spinner_name="aesthetic", style=f"{MODAL_GREEN}"),
        TextColumn("[progress.description]{task.description}", style="bold white"),
        console=console,
    ) as progress:
        
        # Extract space info
        extract_task = progress.add_task("🔍 Analyzing HuggingFace Space...", total=None)
        space_info = await migrator.extract_space_info_async(spaces_url)
        progress.update(extract_task, description=f"✅ Found space: {space_info['repo_id']}")
        
        # Download files
        download_task = progress.add_task("📥 Downloading space files...", total=None)
        local_dir = await migrator.download_space_files_async(space_info)
        progress.update(download_task, description=f"✅ Downloaded to: {local_dir.name}")
        
        # Convert to Modal
        convert_task = progress.add_task("🔄 Converting to Modal deployment...", total=None)
        app_file = await migrator.convert_to_modal_async(local_dir, optimized)
        progress.update(convert_task, description="✅ Modal deployment ready!")
    
    print_success(f"Space analysis complete: {space_info['repo_id']}")
    print_success(f"Files downloaded to: {local_dir}")
    print_success(f"Modal deployment created: {app_file.name}")
    
    if dry_run:
        print_info("Dry run complete - ready to deploy when you are!")
        return
    
    # Deploy with celebration
    deployer = ModalDeployer()
    
    with Progress(
        SpinnerColumn(spinner_name="earth", style=f"{MODAL_GREEN}"),
        TextColumn("[progress.description]{task.description}", style="bold white"),
        console=console,
    ) as progress:
        
        deploy_task = progress.add_task("🚀 Launching migrated app...", total=None)
        url = await deployer.deploy_to_modal_async(app_file)
        progress.update(deploy_task, description="✅ Migration complete!")
    
    # Epic success message
    if url:
        migration_text = Text()
        migration_text.append("🎊 MIGRATION SUCCESSFUL! 🎊", style=f"bold {MODAL_GREEN}")
        migration_text.append("\n🚀 HuggingFace → Modal = DONE!", style=f"bold {MODAL_LIGHT_GREEN}")
        migration_text.append("\n🌐 Your migrated app:", style="bold white")
        migration_text.append(f"\n{url}", style=f"bold {MODAL_GREEN}")
        migration_text.append("\n\n💪 You just got SERIOUS! 💪", style=f"bold {MODAL_GREEN}")
        
        rprint(Panel(
            Align.center(migration_text),
            border_style=f"{MODAL_GREEN}",
            padding=(1, 2)
        ))
    else:
        print_success("HuggingFace Space migrated successfully!")


async def _setup_auth_async(token_id: str | None, token_secret: str | None) -> None:  # pragma: no cover - external CLI interaction
    """Async authentication setup with progress."""
    
    deployer = ModalDeployer()
    
    if token_id and token_secret:
        os.environ["MODAL_TOKEN_ID"] = token_id
        os.environ["MODAL_TOKEN_SECRET"] = token_secret
        print_success("Modal authentication configured via environment variables!")
    else:
        with Progress(
            SpinnerColumn(spinner_name="dots", style=f"{MODAL_GREEN}"),
            TextColumn("[progress.description]{task.description}", style="bold white"),
            console=console,
        ) as progress:
            
            auth_task = progress.add_task("🔐 Setting up Modal authentication...", total=None)
            success = await deployer.setup_modal_auth_async()
            
            if success:
                progress.update(auth_task, description="✅ Authentication setup complete!")
                print_success("You're all set! Ready to deploy! 🚀")
            else:
                progress.update(auth_task, description="❌ Authentication failed!")
                print_error("Authentication setup failed!")


async def _sanity_check_async(br_huehuehue: bool = False) -> None:  # pragma: no cover - requires network
    """Async sanity check for Modal deployments."""
    
    deployer = ModalDeployer()
    
    with Progress(
        SpinnerColumn(spinner_name="dots", style=f"{MODAL_GREEN}"),
        TextColumn("[progress.description]{task.description}", style="bold white"),
        console=console,
    ) as progress:
        
        check_task = progress.add_task("🔍 Checking Modal deployments...", total=None)
        
        try:
            # Check Modal authentication first
            if not await deployer.check_modal_auth_async():
                progress.update(check_task, description="❌ No Modal authentication found!")
                if br_huehuehue:
                    print_error("Nenhuma autenticação Modal encontrada! Huehuehue, configure primeiro!")
                else:
                    print_error("No Modal authentication found! Please run 'modal-for-noobs auth' first!")
                return
            
            # Run modal app list command
            process = await asyncio.create_subprocess_exec(
                "modal", "app", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            progress.update(check_task, description="✅ Sanity check complete!")
            
            if process.returncode == 0:
                output = stdout.decode().strip()
                if output:
                    if br_huehuehue:
                        rprint(f"\n[{MODAL_GREEN}]🎉 Apps encontrados em sua conta Modal (huehuehue!):[/{MODAL_GREEN}]")
                    else:
                        rprint(f"\n[{MODAL_GREEN}]🎉 Apps found in your Modal account:[/{MODAL_GREEN}]")
                    rprint(f"```\n{output}\n```")
                else:
                    if br_huehuehue:
                        rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ Nenhum app deployado ainda! Hora de começar! Huehuehue![/{MODAL_LIGHT_GREEN}]")
                    else:
                        rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ No apps deployed yet! Time to get started![/{MODAL_LIGHT_GREEN}]")
            else:
                error_msg = stderr.decode().strip()
                if br_huehuehue:
                    print_error(f"Erro ao verificar deployments: {error_msg}")
                else:
                    print_error(f"Error checking deployments: {error_msg}")
                
        except Exception as e:
            progress.update(check_task, description="❌ Error during sanity check!")
            if br_huehuehue:
                print_error(f"Erro na verificação de sanidade: {str(e)}")
            else:
                print_error(f"Sanity check error: {str(e)}")


<<<<<<< HEAD:old_cli.py
<<<<<<< HEAD
async def _kill_deployment_async(deployment_id: str | None = None, br_huehuehue: bool = False) -> None:  # pragma: no cover - not covered
    """Async kill deployment functionality."""
=======
async def _kill_deployment_async(deployment_id: str | None = None, br_huehuehue: bool = False) -> None:
    """Async kill deployment functionality - completely stops and removes containers."""
>>>>>>> 78decec (feat: add changes)
=======
async def _kill_deployment_async(deployment_id: str | None = None, br_huehuehue: bool = False) -> None:
    """Async kill deployment functionality - completely stops and removes containers."""
>>>>>>> 78decec (feat: add changes):src/modal_for_noobs/cli.py
    
    deployer = ModalDeployer()
    
    with Progress(
        SpinnerColumn(spinner_name="dots", style=f"{MODAL_GREEN}"),
        TextColumn("[progress.description]{task.description}", style="bold white"),
        console=console,
    ) as progress:
        
        # Check authentication first
        auth_task = progress.add_task("🔍 Checking Modal authentication...", total=None)
        
        if not await deployer.check_modal_auth_async():
            progress.update(auth_task, description="❌ No Modal authentication found!")
            if br_huehuehue:
                print_error("Nenhuma autenticação Modal encontrada! Huehuehue, configure primeiro!")
            else:
                print_error("No Modal authentication found! Please run 'modal-for-noobs auth' first!")
            return
        
        progress.update(auth_task, description="✅ Authentication verified!")
        
        if deployment_id:
            # Kill specific deployment with enhanced feedback
            kill_task = progress.add_task(f"💀 Terminating deployment {deployment_id}...", total=None)
            
            try:
                # First, check if the app is currently running
                list_process = await asyncio.create_subprocess_exec(
                    "modal", "app", "list",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                list_stdout, list_stderr = await list_process.communicate()
                
                app_status = "unknown"
                if list_process.returncode == 0:
                    list_output = list_stdout.decode().strip()
                    for line in list_output.split('\n'):
                        if deployment_id in line:
                            if "deployed" in line:
                                app_status = "deployed"
                            elif "stopped" in line:
                                app_status = "stopped"
                            break
                
                if app_status == "stopped":
                    progress.update(kill_task, description=f"ℹ️ Deployment {deployment_id} was already stopped!")
                    if br_huehuehue:
                        print_success(f"Deployment {deployment_id} já estava parado! Huehuehue!")
                        rprint(f"[{MODAL_LIGHT_GREEN}]💡 O app foi completamente removido dos containers ativos![/{MODAL_LIGHT_GREEN}]")
                    else:
                        print_success(f"Deployment {deployment_id} was already stopped!")
                        rprint(f"[{MODAL_LIGHT_GREEN}]💡 App completely removed from active containers![/{MODAL_LIGHT_GREEN}]")
                    return
                
                # Stop the deployment
                progress.update(kill_task, description=f"🛑 Stopping deployment {deployment_id}...")
                stop_process = await asyncio.create_subprocess_exec(
                    "modal", "app", "stop", deployment_id,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stop_stdout, stop_stderr = await stop_process.communicate()
                
                if stop_process.returncode == 0:
                    # Also stop any running containers for this app
                    progress.update(kill_task, description=f"🔄 Checking for running containers...")
                    
                    container_process = await asyncio.create_subprocess_exec(
                        "modal", "container", "list",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    container_stdout, container_stderr = await container_process.communicate()
                    
                    containers_killed = 0
                    if container_process.returncode == 0:
                        container_output = container_stdout.decode().strip()
                        # Look for containers matching our app name
                        for line in container_output.split('\n'):
                            if deployment_id in line or "modal-for-noobs" in line:
                                # Extract container ID and stop it
                                parts = line.split()
                                if len(parts) > 0:
                                    container_id = parts[0]
                                    if container_id.startswith('ct-'):
                                        progress.update(kill_task, description=f"💀 Stopping container {container_id}...")
                                        container_stop_process = await asyncio.create_subprocess_exec(
                                            "modal", "container", "stop", container_id,
                                            stdout=asyncio.subprocess.PIPE,
                                            stderr=asyncio.subprocess.PIPE
                                        )
                                        await container_stop_process.communicate()
                                        if container_stop_process.returncode == 0:
                                            containers_killed += 1
                    
                    progress.update(kill_task, description=f"✅ Deployment {deployment_id} completely terminated!")
                    
                    if br_huehuehue:
                        print_success(f"💀 Deployment {deployment_id} foi completamente exterminado! Huehuehue!")
                        if containers_killed > 0:
                            rprint(f"[{MODAL_GREEN}]🔥 {containers_killed} containers também foram mortos![/{MODAL_GREEN}]")
                        rprint(f"[{MODAL_LIGHT_GREEN}]✨ App removido de todos os servidores! Não consome mais recursos![/{MODAL_LIGHT_GREEN}]")
                    else:
                        print_success(f"💀 Deployment {deployment_id} completely terminated!")
                        if containers_killed > 0:
                            rprint(f"[{MODAL_GREEN}]🔥 {containers_killed} containers also stopped![/{MODAL_GREEN}]")
                        rprint(f"[{MODAL_LIGHT_GREEN}]✨ App removed from all servers! No longer consuming resources![/{MODAL_LIGHT_GREEN}]")
                else:
                    error_msg = stop_stderr.decode().strip()
                    progress.update(kill_task, description="❌ Failed to terminate deployment!")
                    if br_huehuehue:
                        print_error(f"Erro ao exterminar deployment: {error_msg}")
                    else:
                        print_error(f"Failed to terminate deployment: {error_msg}")
                        
            except Exception as e:
                progress.update(kill_task, description="❌ Error during termination operation!")
                if br_huehuehue:
                    print_error(f"Erro ao exterminar deployment: {str(e)}")
                else:
                    print_error(f"Error terminating deployment: {str(e)}")
        
        else:
            # List deployments for user to choose
            list_task = progress.add_task("📋 Listing deployments to terminate...", total=None)
            
            try:
                process = await asyncio.create_subprocess_exec(
                    "modal", "app", "list",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                progress.update(list_task, description="✅ Deployments listed!")
                
                if process.returncode == 0:
                    output = stdout.decode().strip()
                    if output:
                        if br_huehuehue:
                            rprint(f"\n[{MODAL_GREEN}]💀 EXTERMINADOR DE DEPLOYMENTS 💀[/{MODAL_GREEN}]")
                            rprint(f"[{MODAL_LIGHT_GREEN}]Deployments disponíveis para exterminar (huehuehue!):[/{MODAL_LIGHT_GREEN}]")
                        else:
                            rprint(f"\n[{MODAL_GREEN}]💀 DEPLOYMENT EXTERMINATOR 💀[/{MODAL_GREEN}]")
                            rprint(f"[{MODAL_LIGHT_GREEN}]Deployments available to terminate:[/{MODAL_LIGHT_GREEN}]")
                        
                        rprint(f"```\n{output}\n```")
                        
                        # Count deployed vs stopped
                        lines = output.split('\n')
                        deployed_count = sum(1 for line in lines if 'deployed' in line)
                        stopped_count = sum(1 for line in lines if 'stopped' in line)
                        
                        if deployed_count > 0:
                            if br_huehuehue:
                                rprint(f"\n[{MODAL_GREEN}]🔥 {deployed_count} deployments ativos consumindo recursos![/{MODAL_GREEN}]")
                                rprint(f"[{MODAL_LIGHT_GREEN}]💡 Para exterminar um deployment específico:[/{MODAL_LIGHT_GREEN}]")
                                rprint("./mn.sh --kill-deployment <app-id> --br-huehuehue")
                            else:
                                rprint(f"\n[{MODAL_GREEN}]🔥 {deployed_count} active deployments consuming resources![/{MODAL_GREEN}]")
                                rprint(f"[{MODAL_LIGHT_GREEN}]💡 To terminate a specific deployment:[/{MODAL_LIGHT_GREEN}]")
                                rprint("./mn.sh --kill-deployment <app-id>")
                        else:
                            if br_huehuehue:
                                rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ Nenhum deployment ativo! Todos exterminados! Huehuehue![/{MODAL_LIGHT_GREEN}]")
                            else:
                                rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ No active deployments! Everything terminated![/{MODAL_LIGHT_GREEN}]")
                        
                        if stopped_count > 0:
                            if br_huehuehue:
                                rprint(f"[{MODAL_LIGHT_GREEN}]ℹ️ {stopped_count} deployments já exterminados (não consomem recursos)[/{MODAL_LIGHT_GREEN}]")
                            else:
                                rprint(f"[{MODAL_LIGHT_GREEN}]ℹ️ {stopped_count} deployments already terminated (no resource consumption)[/{MODAL_LIGHT_GREEN}]")
                    else:
                        if br_huehuehue:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ Nenhum deployment encontrado! Tudo limpo! Huehuehue![/{MODAL_LIGHT_GREEN}]")
                        else:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ No deployments found! Everything clean![/{MODAL_LIGHT_GREEN}]")
                else:
                    error_msg = stderr.decode().strip()
                    if br_huehuehue:
                        print_error(f"Erro ao listar deployments: {error_msg}")
                    else:
                        print_error(f"Error listing deployments: {error_msg}")
                        
            except Exception as e:
                progress.update(list_task, description="❌ Error listing deployments!")
                if br_huehuehue:
                    print_error(f"Erro ao listar deployments: {str(e)}")
                else:
                    print_error(f"Error listing deployments: {str(e)}")


async def _milk_logs_async(
    app_name: str | None = None, 
    follow: bool = False, 
    lines: int = 100, 
    br_huehuehue: bool = False
) -> None:
    """Async log milking functionality - get those creamy logs! 🥛"""
    
    deployer = ModalDeployer()
    
    with Progress(
        SpinnerColumn(spinner_name="dots", style=f"{MODAL_GREEN}"),
        TextColumn("[progress.description]{task.description}", style="bold white"),
        console=console,
    ) as progress:
        
        # Check authentication first
        auth_task = progress.add_task("🔍 Checking Modal authentication...", total=None)
        
        if not await deployer.check_modal_auth_async():
            progress.update(auth_task, description="❌ No Modal authentication found!")
            if br_huehuehue:
                print_error("Nenhuma autenticação Modal encontrada! Huehuehue, configure primeiro!")
            else:
                print_error("No Modal authentication found! Please run 'modal-for-noobs auth' first!")
            return
        
        progress.update(auth_task, description="✅ Authentication verified!")
        
        if not app_name:
            # List apps for user to choose
            list_task = progress.add_task("📋 Finding apps to milk logs from...", total=None)
            
            try:
                process = await asyncio.create_subprocess_exec(
                    "modal", "app", "list",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                progress.update(list_task, description="✅ Apps found!")
                
                if process.returncode == 0:
                    output = stdout.decode().strip()
                    if output:
                        if br_huehuehue:
                            rprint(f"\n[{MODAL_GREEN}]🥛 Apps disponíveis para ordenhar logs (huehuehue!):[/{MODAL_GREEN}]")
                        else:
                            rprint(f"\n[{MODAL_GREEN}]🥛 Apps available for log milking:[/{MODAL_GREEN}]")
                        rprint(f"```\n{output}\n```")
                        
                        if br_huehuehue:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]💡 Para ordenhar logs de um app específico:[/{MODAL_LIGHT_GREEN}]")
                            rprint("modal-for-noobs milk-logs <app-name> --br-huehuehue")
                        else:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]💡 To milk logs from a specific app:[/{MODAL_LIGHT_GREEN}]")
                            rprint("modal-for-noobs milk-logs <app-name> --follow")
                    else:
                        if br_huehuehue:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ Nenhum app para ordenhar! Deploye algo primeiro! Huehuehue![/{MODAL_LIGHT_GREEN}]")
                        else:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ No apps to milk logs from! Deploy something first![/{MODAL_LIGHT_GREEN}]")
                else:
                    error_msg = stderr.decode().strip()
                    if br_huehuehue:
                        print_error(f"Erro ao listar apps: {error_msg}")
                    else:
                        print_error(f"Error listing apps: {error_msg}")
                        
            except Exception as e:
                progress.update(list_task, description="❌ Error listing apps!")
                if br_huehuehue:
                    print_error(f"Erro ao listar apps: {str(e)}")
                else:
                    print_error(f"Error listing apps: {str(e)}")
        
        else:
            # Milk logs from specific app
            milk_task = progress.add_task(f"🥛 Milking logs from {app_name}...", total=None)
            
            try:
                # Build modal logs command - Modal CLI uses different syntax
                cmd = ["modal", "app", "logs", app_name]
                if follow:
                    cmd.append("--follow")
                # Note: Modal CLI doesn't support --lines flag, so we'll get all logs and limit client-side
                
                if follow:
                    # For follow mode, we need to stream the output
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    progress.update(milk_task, description=f"🥛 Streaming fresh logs from {app_name}...")
                    
                    if br_huehuehue:
                        rprint(f"\n[{MODAL_GREEN}]🥛 Logs fresquinhos de {app_name} (huehuehue!):[/{MODAL_GREEN}]")
                    else:
                        rprint(f"\n[{MODAL_GREEN}]🥛 Fresh creamy logs from {app_name}:[/{MODAL_GREEN}]")
                    rprint("=" * 80)
                    
                    # Stream output line by line
                    while True:
                        line = await process.stdout.readline()
                        if not line:
                            break
                        
                        log_line = line.decode().strip()
                        if log_line:
                            # Add milk emoji to each log line for fun
                            rprint(f"🥛 {log_line}")
                    
                    await process.wait()
                    
                else:
                    # For non-follow mode, get all logs at once
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0:
                        progress.update(milk_task, description=f"✅ Logs milked from {app_name}!")
                        
                        logs = stdout.decode().strip()
                        if logs:
                            if br_huehuehue:
                                rprint(f"\n[{MODAL_GREEN}]🥛 Logs fresquinhos de {app_name} (huehuehue!):[/{MODAL_GREEN}]")
                            else:
                                rprint(f"\n[{MODAL_GREEN}]🥛 Fresh creamy logs from {app_name}:[/{MODAL_GREEN}]")
                            rprint("=" * 80)
                            
                            # Pretty print logs with milk emojis (limit to requested lines)
                            log_lines = logs.split('\n')
                            displayed_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
                            
                            for line in displayed_lines:
                                if line.strip():
                                    rprint(f"🥛 {line}")
                            
                            rprint("=" * 80)
                            if br_huehuehue:
                                print_success(f"Logs ordenhados com sucesso de {app_name}! ({len(displayed_lines)} linhas) Huehuehue!")
                            else:
                                print_success(f"Successfully milked {len(displayed_lines)} lines of creamy logs from {app_name}!")
                        else:
                            if br_huehuehue:
                                rprint(f"\n[{MODAL_LIGHT_GREEN}]📝 Nenhum log encontrado para {app_name}![/{MODAL_LIGHT_GREEN}]")
                            else:
                                rprint(f"\n[{MODAL_LIGHT_GREEN}]📝 No logs found for {app_name}![/{MODAL_LIGHT_GREEN}]")
                    else:
                        error_msg = stderr.decode().strip()
                        progress.update(milk_task, description="❌ Failed to milk logs!")
                        if br_huehuehue:
                            print_error(f"Erro ao ordenhar logs: {error_msg}")
                        else:
                            print_error(f"Failed to milk logs: {error_msg}")
                        
            except Exception as e:
                progress.update(milk_task, description="❌ Error during log milking!")
                if br_huehuehue:
                    print_error(f"Erro ao ordenhar logs: {str(e)}")
                else:
                    print_error(f"Error milking logs: {str(e)}")


def main() -> None:
    """Main CLI entry point with beautiful styling."""
    app()


if __name__ == "__main__":
    main()
