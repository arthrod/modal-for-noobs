"""Unit tests for ConfigLoader."""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
import yaml

from modal_for_noobs.config_loader import ConfigLoader, config_loader


class TestConfigLoader:
    """Test suite for ConfigLoader."""
    
    def test_init(self):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader()
        assert loader.config_dir == Path(__file__).parent.parent / "modal_for_noobs" / "config"
    
    def test_load_base_packages_success(self):
        """Test successful loading of base packages configuration."""
        test_config = {
            "minimum": ["package1", "package2"],
            "optimized": ["package1", "package2", "package3"]
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(test_config))):
            loader = ConfigLoader()
            result = loader.load_base_packages()
            
        assert result == test_config
        assert "minimum" in result
        assert "optimized" in result
    
    def test_load_base_packages_file_not_found(self):
        """Test fallback when base packages config file is not found."""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            with patch("loguru.logger.warning") as mock_warning:
                loader = ConfigLoader()
                result = loader.load_base_packages()
                
        # Check fallback values
        assert "minimum" in result
        assert "optimized" in result
        assert "gra_jupy" in result
        assert result["minimum"] == ["gradio", "fastapi[standard]", "uvicorn"]
        assert "torch" in result["optimized"]
        assert "jupyter" in result["gra_jupy"]
        
        # Check warning was logged
        mock_warning.assert_called_once()
        assert "Could not load base packages config" in str(mock_warning.call_args)
    
    def test_load_base_packages_yaml_error(self):
        """Test fallback when YAML parsing fails."""
        with patch("builtins.open", mock_open(read_data="invalid: yaml: content:")):
            with patch("yaml.safe_load", side_effect=yaml.YAMLError("Invalid YAML")):
                with patch("loguru.logger.warning") as mock_warning:
                    loader = ConfigLoader()
                    result = loader.load_base_packages()
                    
        # Check fallback values
        assert "minimum" in result
        assert "optimized" in result
        
        # Check warning was logged
        mock_warning.assert_called_once()
    
    def test_load_modal_marketing_success(self):
        """Test successful loading of modal marketing configuration."""
        test_config = {
            "banners": {"hero": "Test Banner"},
            "features": ["Feature 1", "Feature 2"],
            "testimonials": ["Great product!"],
            "calls_to_action": ["Try now!"]
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(test_config))):
            loader = ConfigLoader()
            result = loader.load_modal_marketing()
            
        assert result == test_config
        assert result["banners"]["hero"] == "Test Banner"
        assert len(result["features"]) == 2
    
    def test_load_modal_marketing_fallback(self):
        """Test fallback when modal marketing config fails to load."""
        with patch("builtins.open", side_effect=Exception("Some error")):
            with patch("loguru.logger.warning") as mock_warning:
                loader = ConfigLoader()
                result = loader.load_modal_marketing()
                
        # Check fallback values
        assert "banners" in result
        assert "features" in result
        assert "testimonials" in result
        assert "calls_to_action" in result
        assert result["banners"]["hero"] == "🚀💚 POWERED BY MODAL 💚🚀"
        
        # Check warning was logged
        mock_warning.assert_called_once()
        assert "Could not load marketing config" in str(mock_warning.call_args)
    
    def test_load_deployment_examples_success(self):
        """Test successful loading of deployment examples configuration."""
        test_config = {
            "examples": {
                "test_app": {
                    "name": "Test Application",
                    "path": "path/to/test.py",
                    "mode": "minimum"
                }
            }
        }
        
        with patch("builtins.open", mock_open(read_data=yaml.dump(test_config))):
            loader = ConfigLoader()
            result = loader.load_deployment_examples()
            
        assert result == test_config
        assert "test_app" in result["examples"]
        assert result["examples"]["test_app"]["name"] == "Test Application"
    
    def test_load_deployment_examples_fallback(self):
        """Test fallback when deployment examples config fails to load."""
        with patch("builtins.open", side_effect=OSError("IO Error")):
            with patch("loguru.logger.warning") as mock_warning:
                loader = ConfigLoader()
                result = loader.load_deployment_examples()
                
        # Check fallback values
        assert "examples" in result
        assert "voice_app" in result["examples"]
        assert result["examples"]["voice_app"]["name"] == "🎤 Ultimate Voice Green App"
        assert result["examples"]["voice_app"]["mode"] == "optimized"
        
        # Check warning was logged
        mock_warning.assert_called_once()
        assert "Could not load examples config" in str(mock_warning.call_args)
    
    def test_config_loader_singleton(self):
        """Test that config_loader is a global singleton instance."""
        assert config_loader is not None
        assert isinstance(config_loader, ConfigLoader)
        assert config_loader.config_dir.name == "config"
    
    def test_all_methods_handle_exceptions_gracefully(self):
        """Test that all loader methods handle exceptions without crashing."""
        loader = ConfigLoader()
        
        # Mock all file operations to raise exceptions
        with patch("builtins.open", side_effect=Exception("Unexpected error")):
            with patch("loguru.logger.warning"):
                # All methods should return fallback values without raising
                packages = loader.load_base_packages()
                marketing = loader.load_modal_marketing()
                examples = loader.load_deployment_examples()
                
                assert isinstance(packages, dict)
                assert isinstance(marketing, dict)
                assert isinstance(examples, dict)