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
def auth(  # pragma: no cover - requires user credentials
    token_id: Annotated[Optional[str], typer.Option("--token-id", help="Modal token ID")] = None,
    token_secret: Annotated[Optional[str], typer.Option("--token-secret", help="Modal token secret")] = None,
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
def kill_a_deployment(  # pragma: no cover - interactive helper
    deployment_id: Annotated[str | None, typer.Argument(help="Deployment ID to kill")] = None,
    br_huehuehue: Annotated[bool, typer.Option("--br-huehuehue", help="Modo brasileiro com muito huehuehue! 🇧🇷")] = False,
) -> None:
    """💀 Kill a specific deployment or list active ones to choose from!"""
    
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
def sanity_check(  # pragma: no cover - optional helper
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


async def _kill_deployment_async(deployment_id: str | None = None, br_huehuehue: bool = False) -> None:  # pragma: no cover - not covered
    """Async kill deployment functionality."""
    
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
            # Kill specific deployment
            kill_task = progress.add_task(f"💀 Killing deployment {deployment_id}...", total=None)
            
            try:
                process = await asyncio.create_subprocess_exec(
                    "modal", "app", "stop", deployment_id,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    progress.update(kill_task, description=f"✅ Deployment {deployment_id} killed!")
                    if br_huehuehue:
                        print_success(f"Deployment {deployment_id} foi morto com sucesso! Huehuehue!")
                    else:
                        print_success(f"Deployment {deployment_id} killed successfully!")
                else:
                    error_msg = stderr.decode().strip()
                    progress.update(kill_task, description="❌ Failed to kill deployment!")
                    if br_huehuehue:
                        print_error(f"Erro ao matar deployment: {error_msg}")
                    else:
                        print_error(f"Failed to kill deployment: {error_msg}")
                        
            except Exception as e:
                progress.update(kill_task, description="❌ Error during kill operation!")
                if br_huehuehue:
                    print_error(f"Erro ao matar deployment: {str(e)}")
                else:
                    print_error(f"Error killing deployment: {str(e)}")
        
        else:
            # List deployments for user to choose
            list_task = progress.add_task("📋 Listing active deployments...", total=None)
            
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
                            rprint(f"\n[{MODAL_GREEN}]🎯 Deployments ativos para matar (huehuehue!):[/{MODAL_GREEN}]")
                        else:
                            rprint(f"\n[{MODAL_GREEN}]🎯 Active deployments available to kill:[/{MODAL_GREEN}]")
                        rprint(f"```\n{output}\n```")
                        
                        if br_huehuehue:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]💡 Para matar um deployment específico:[/{MODAL_LIGHT_GREEN}]")
                            rprint("modal-for-noobs kill-a-deployment <deployment-id> --br-huehuehue")
                        else:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]💡 To kill a specific deployment:[/{MODAL_LIGHT_GREEN}]")
                            rprint("modal-for-noobs kill-a-deployment <deployment-id>")
                    else:
                        if br_huehuehue:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ Nenhum deployment ativo para matar! Todos já estão mortos! Huehuehue![/{MODAL_LIGHT_GREEN}]")
                        else:
                            rprint(f"\n[{MODAL_LIGHT_GREEN}]✨ No active deployments to kill! Everything is already dead![/{MODAL_LIGHT_GREEN}]")
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


def main() -> None:
    """Main CLI entry point with beautiful styling."""
    app()


if __name__ == "__main__":
    main()
