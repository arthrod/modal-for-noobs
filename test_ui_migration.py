#!/usr/bin/env python3
"""Test script to verify UI component migration."""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    # Test imports
    from modal_for_noobs.cli_helpers.common import MODAL_GREEN, MODAL_LIGHT_GREEN, MODAL_DARK_GREEN, MODAL_BLACK
    print("✅ Common constants imported successfully")
    
    from modal_for_noobs.ui.themes import MODAL_THEME, MODAL_CSS, create_modal_theme, get_modal_css
    print("✅ UI themes imported successfully")
    
    from modal_for_noobs.ui.components import ModalDeployButton, ModalExplorer, ModalStatusMonitor
    print("✅ UI components imported successfully")
    
    # Test theme creation
    theme = create_modal_theme()
    css = get_modal_css()
    print(f"✅ Theme created successfully: {type(theme)}")
    print(f"✅ CSS generated successfully: {len(css)} characters")
    
    # Test color consistency
    print(f"✅ Modal Green: {MODAL_GREEN}")
    print(f"✅ Modal Light Green: {MODAL_LIGHT_GREEN}")
    print(f"✅ Modal Dark Green: {MODAL_DARK_GREEN}")
    print(f"✅ Modal Black: {MODAL_BLACK}")
    
    print("\n🎉 All UI component migration tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)