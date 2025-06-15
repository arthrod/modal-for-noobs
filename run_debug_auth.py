#!/usr/bin/env python3
"""
Simple runner for the Modal authentication debug dashboard.
"""

import sys
import subprocess
from pathlib import Path
from security import safe_command

def main():
    """Run the debug authentication dashboard."""
    print("🔍 Modal Authentication Debug Dashboard")
    print("=" * 50)
    
    # Check if Modal is installed
    try:
        import modal
        print("✅ Modal package found")
    except ImportError:
        print("❌ Modal package not found")
        print("📦 Installing Modal...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "modal"])
        print("✅ Modal installed")
    
    # Check if we're in the right directory
    debug_file = Path(__file__).parent / "debug_modal_auth.py"
    if not debug_file.exists():
        print(f"❌ Debug file not found: {debug_file}")
        return 1
    
    print("\n🚀 Starting debug dashboard...")
    print("📊 Dashboard will be available at: http://localhost:7870")
    print("🔧 This tests REAL Modal token flow API")
    print("\n📖 Instructions:")
    print("1. Click '🚀 1. Initialize Modal Client'")
    print("2. Click '🔐 2. Start Auth Flow'") 
    print("3. Open the generated URL in your browser")
    print("4. Authorize on Modal's website")
    print("5. Click '✅ 3. Finish Auth' to get tokens")
    print("\n" + "=" * 50)
    
    # Run the debug dashboard
    try:
        safe_command.run(subprocess.run, [sys.executable, str(debug_file)], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Dashboard failed with exit code {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    sys.exit(main())
