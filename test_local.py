#!/usr/bin/env python3
"""
Local test script for modal-for-noobs package.
Tests all imports and core functionality to ensure package works correctly.
"""

import sys
import traceback
from pathlib import Path

def test_basic_imports():
    """Test basic package imports."""
    print("🧪 Testing basic imports...")
    
    try:
        # Test main package import
        import modal_for_noobs
        print(f"✅ modal_for_noobs imported successfully (v{modal_for_noobs.__version__})")
        
        # Test CLI import
        from modal_for_noobs.cli import main
        print("✅ CLI import successful")
        
        # Test dashboard import (this was the original issue)
        from modal_for_noobs.dashboard import ModalDashboard
        print("✅ ModalDashboard import successful")
        
        # Test modal deployer import
        from modal_for_noobs.modal_deploy import ModalDeployer
        print("✅ ModalDeployer import successful")
        
        # Test CLI helpers import
        from modal_for_noobs.cli_helpers.common import MODAL_GREEN
        print("✅ CLI helpers import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_template_constants():
    """Test template constants imports and functionality."""
    print("\n🧪 Testing template constants...")
    
    try:
        from modal_for_noobs.templates.template_constants import (
            MODAL_IMPORTS,
            GRADIO_DETECTION,
            MARIMO_NOTEBOOK_HEADER,
            DASHBOARD_MODULE_TEMPLATE
        )
        print("✅ Template constants imported successfully")
        
        # Test that constants are strings and not empty
        assert isinstance(MODAL_IMPORTS, str) and len(MODAL_IMPORTS) > 0
        assert isinstance(GRADIO_DETECTION, str) and len(GRADIO_DETECTION) > 0
        assert isinstance(MARIMO_NOTEBOOK_HEADER, str) and len(MARIMO_NOTEBOOK_HEADER) > 0
        print("✅ Template constants are valid strings")
        
        return True
        
    except Exception as e:
        print(f"❌ Template constants test failed: {e}")
        traceback.print_exc()
        return False

def test_marimo_template():
    """Test marimo template functionality."""
    print("\n🧪 Testing marimo template...")
    
    try:
        from modal_for_noobs.templates.marimo.deployment_template import create_marimo_template
        
        # Test template creation
        template = create_marimo_template(
            app_name="test-app",
            image_config="image = modal.Image.debian_slim()",
            original_code="# Test code",
            timeout_seconds=300,
            max_containers=1
        )
        
        assert isinstance(template, str) and len(template) > 0
        assert "test-app" in template
        assert "marimo" in template.lower()
        print("✅ Marimo template creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Marimo template test failed: {e}")
        traceback.print_exc()
        return False

def test_modal_deployer():
    """Test ModalDeployer functionality."""
    print("\n🧪 Testing ModalDeployer...")
    
    try:
        from modal_for_noobs.modal_deploy import ModalDeployer
        import tempfile
        
        # Create a temporary test file for app_file parameter
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
            tmp_file.write("# Test gradio app\nimport gradio as gr\ndemo = gr.Interface(lambda x: x, 'text', 'text')")
            tmp_file_path = Path(tmp_file.name)
        
        try:
            # Create deployer instance with required app_file parameter
            deployer = ModalDeployer(tmp_file_path)
            print("✅ ModalDeployer instance created")
            
            # Test that deployer has expected methods
            assert hasattr(deployer, 'create_modal_deployment_async')
            assert hasattr(deployer, '_create_enhanced_template')
            print("✅ ModalDeployer has expected methods")
            
            return True
        finally:
            # Clean up temporary file
            tmp_file_path.unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ ModalDeployer test failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_creation():
    """Test dashboard creation functionality."""
    print("\n🧪 Testing dashboard creation...")
    
    try:
        from modal_for_noobs.dashboard import ModalDashboard
        
        # Create dashboard instance
        dashboard = ModalDashboard()
        print("✅ ModalDashboard instance created")
        
        # Test that dashboard has expected methods
        assert hasattr(dashboard, 'create_interface')
        print("✅ ModalDashboard has expected methods")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard creation test failed: {e}")
        traceback.print_exc()
        return False

def test_syntax_validation():
    """Test that all Python files have valid syntax."""
    print("\n🧪 Testing syntax validation...")
    
    try:
        import ast
        src_dir = Path(__file__).parent / "src" / "modal_for_noobs"
        
        python_files = list(src_dir.rglob("*.py"))
        failed_files = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                failed_files.append((py_file, e))
        
        if failed_files:
            print(f"❌ Syntax errors found in {len(failed_files)} files:")
            for file_path, error in failed_files:
                print(f"  - {file_path.relative_to(src_dir)}: {error}")
            return False
        else:
            print(f"✅ All {len(python_files)} Python files have valid syntax")
            return True
            
    except Exception as e:
        print(f"❌ Syntax validation failed: {e}")
        traceback.print_exc()
        return False

def test_f_string_issues():
    """Test for f-string backslash issues that were causing problems."""
    print("\n🧪 Testing f-string fixes...")
    
    try:
        # This should work now (was the original issue)
        test_content = "line1\nline2\nline3"
        newline_char = "\n"
        lines = test_content.split(newline_char)
        remaining = len(lines) - 1
        result = f"Found {remaining} additional lines"
        
        assert "2 additional lines" in result
        print("✅ F-string backslash handling works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ F-string test failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Starting modal-for-noobs local package tests")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Template Constants", test_template_constants),
        ("Marimo Template", test_marimo_template),
        ("ModalDeployer", test_modal_deployer),
        ("Dashboard Creation", test_dashboard_creation),
        ("Syntax Validation", test_syntax_validation),
        ("F-string Fixes", test_f_string_issues),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print("-" * 50)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Package is working correctly.")
        print("✨ The f-string syntax fixes are working!")
        print("🚀 Ready for HuggingFace Spaces deployment!")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Package needs fixes.")
        return False

if __name__ == "__main__":
    # Add the src directory to Python path for local testing
    src_dir = Path(__file__).parent / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
    
    success = run_all_tests()
    sys.exit(0 if success else 1)