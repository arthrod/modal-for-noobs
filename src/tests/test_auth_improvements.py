"""Comprehensive tests for authentication improvements."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import pytest

from modal_for_noobs.auth_manager import ModalAuthManager, ModalAuthConfig
from modal_for_noobs.dashboard_auth import DashboardAuthenticator
from modal_for_noobs.easy_auth import EasyModalAuth


class TestModalAuthConfig:
    """Test ModalAuthConfig dataclass."""
    
    def test_basic_creation(self):
        """Test basic auth config creation."""
        config = ModalAuthConfig(
            token_id="ak-test123",
            token_secret="as-secret456"
        )
        assert config.token_id == "ak-test123"
        assert config.token_secret == "as-secret456"
        assert config.workspace is None
    
    def test_validation_success(self):
        """Test successful validation."""
        config = ModalAuthConfig(
            token_id="ak-valid123",
            token_secret="as-validsecret456",
            workspace="test-workspace"
        )
        is_valid, errors = config.validate()
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validation_failures(self):
        """Test various validation failures."""
        # Empty token ID
        config = ModalAuthConfig(token_id="", token_secret="as-secret")
        is_valid, errors = config.validate()
        assert is_valid is False
        assert "Token ID cannot be empty" in errors
        
        # Invalid token ID format
        config = ModalAuthConfig(token_id="invalid", token_secret="as-secret")
        is_valid, errors = config.validate()
        assert is_valid is False
        assert "Token ID must start with 'ak-'" in errors
        
        # Empty token secret
        config = ModalAuthConfig(token_id="ak-valid", token_secret="")
        is_valid, errors = config.validate()
        assert is_valid is False
        assert "Token secret cannot be empty" in errors
        
        # Invalid token secret format
        config = ModalAuthConfig(token_id="ak-valid", token_secret="invalid")
        is_valid, errors = config.validate()
        assert is_valid is False
        assert "Token secret must start with 'as-'" in errors
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = ModalAuthConfig(
            token_id="ak-test",
            token_secret="as-secret",
            workspace="workspace"
        )
        result = config.to_dict()
        expected = {
            "token_id": "ak-test",
            "token_secret": "as-secret",
            "workspace": "workspace"
        }
        assert result == expected
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "token_id": "ak-fromdict",
            "token_secret": "as-fromdict",
            "workspace": "test"
        }
        config = ModalAuthConfig.from_dict(data)
        assert config.token_id == "ak-fromdict"
        assert config.token_secret == "as-fromdict"
        assert config.workspace == "test"


class TestModalAuthManager:
    """Test ModalAuthManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.auth_manager = ModalAuthManager()
    
    def test_get_auth_from_env_success(self):
        """Test getting auth from environment variables."""
        with patch.dict(os.environ, {
            'MODAL_TOKEN_ID': 'ak-env123',
            'MODAL_TOKEN_SECRET': 'as-envsecret456'
        }):
            config = self.auth_manager.get_auth_from_env()
            assert config is not None
            assert config.token_id == 'ak-env123'
            assert config.token_secret == 'as-envsecret456'
    
    def test_get_auth_from_env_missing(self):
        """Test getting auth from environment when variables are missing."""
        with patch.dict(os.environ, {}, clear=True):
            config = self.auth_manager.get_auth_from_env()
            assert config is None
    
    def test_apply_auth_to_env(self):
        """Test applying auth config to environment."""
        config = ModalAuthConfig(
            token_id="ak-apply123",
            token_secret="as-applysecret456",
            workspace="apply-workspace"
        )
        
        with patch.dict(os.environ, {}, clear=True):
            self.auth_manager.apply_auth_to_env(config)
            assert os.environ.get('MODAL_TOKEN_ID') == 'ak-apply123'
            assert os.environ.get('MODAL_TOKEN_SECRET') == 'as-applysecret456'
            assert os.environ.get('MODAL_WORKSPACE') == 'apply-workspace'
    
    def test_validate_environment_success(self):
        """Test environment validation when properly configured."""
        with patch.dict(os.environ, {
            'MODAL_TOKEN_ID': 'ak-valid123',
            'MODAL_TOKEN_SECRET': 'as-validsecret456'
        }):
            is_valid, issues = self.auth_manager.validate_environment()
            assert is_valid is True
            assert len(issues) == 0
    
    def test_validate_environment_missing_vars(self):
        """Test environment validation with missing variables."""
        with patch.dict(os.environ, {}, clear=True):
            is_valid, issues = self.auth_manager.validate_environment()
            assert is_valid is False
            assert "MODAL_TOKEN_ID not found" in issues
            assert "MODAL_TOKEN_SECRET not found" in issues
    
    def test_validate_environment_invalid_format(self):
        """Test environment validation with invalid format."""
        with patch.dict(os.environ, {
            'MODAL_TOKEN_ID': 'invalid-format',
            'MODAL_TOKEN_SECRET': 'also-invalid'
        }):
            is_valid, issues = self.auth_manager.validate_environment()
            assert is_valid is False
            assert any("must start with 'ak-'" in issue for issue in issues)
            assert any("must start with 'as-'" in issue for issue in issues)
    
    @patch('modal_for_noobs.auth_manager.subprocess.run')
    def test_test_authentication_success(self, mock_run):
        """Test successful authentication test."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Authentication successful"
        
        config = ModalAuthConfig(
            token_id="ak-test123",
            token_secret="as-testsecret456"
        )
        
        result = self.auth_manager.test_authentication(config)
        assert result is True
        mock_run.assert_called_once()
    
    @patch('modal_for_noobs.auth_manager.subprocess.run')
    def test_test_authentication_failure(self, mock_run):
        """Test failed authentication test."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Authentication failed"
        
        config = ModalAuthConfig(
            token_id="ak-invalid",
            token_secret="as-invalid"
        )
        
        result = self.auth_manager.test_authentication(config)
        assert result is False
    
    def test_save_auth_config(self):
        """Test saving authentication config."""
        config = ModalAuthConfig(
            token_id="ak-save123",
            token_secret="as-savesecret456",
            workspace="save-workspace"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('modal_for_noobs.auth_manager.Path.home') as mock_home:
                mock_home.return_value = Path(temp_dir)
                
                result = self.auth_manager.save_auth(config)
                assert result is True
                
                # Check if config file was created
                config_file = Path(temp_dir) / '.modal-for-noobs' / 'auth.json'
                assert config_file.exists()
                
                # Verify content
                import json
                saved_data = json.loads(config_file.read_text())
                assert saved_data['token_id'] == 'ak-save123'
                assert saved_data['token_secret'] == 'as-savesecret456'
                assert saved_data['workspace'] == 'save-workspace'
    
    def test_load_auth_config(self):
        """Test loading authentication config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('modal_for_noobs.auth_manager.Path.home') as mock_home:
                mock_home.return_value = Path(temp_dir)
                
                # Create config file
                config_dir = Path(temp_dir) / '.modal-for-noobs'
                config_dir.mkdir()
                config_file = config_dir / 'auth.json'
                
                import json
                config_data = {
                    'token_id': 'ak-load123',
                    'token_secret': 'as-loadsecret456',
                    'workspace': 'load-workspace'
                }
                config_file.write_text(json.dumps(config_data))
                
                # Load config
                loaded_config = self.auth_manager.load_auth()
                assert loaded_config is not None
                assert loaded_config.token_id == 'ak-load123'
                assert loaded_config.token_secret == 'as-loadsecret456'
                assert loaded_config.workspace == 'load-workspace'


class TestDashboardAuthenticator:
    """Test DashboardAuthenticator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.auth = DashboardAuthenticator()
    
    def test_initialization(self):
        """Test authenticator initialization."""
        assert self.auth.auth_manager is not None
        assert self.auth.auth_state['is_authenticated'] is False
        assert self.auth.auth_state['auth_config'] is None
    
    def test_auth_status_not_authenticated(self):
        """Test auth status when not authenticated."""
        with patch.dict(os.environ, {}, clear=True):
            status = self.auth._get_auth_status_message()
            assert "❌ Not authenticated" in status
    
    def test_auth_status_authenticated_via_env(self):
        """Test auth status when authenticated via environment."""
        with patch.dict(os.environ, {
            'MODAL_TOKEN_ID': 'ak-env123',
            'MODAL_TOKEN_SECRET': 'as-envsecret456'
        }):
            with patch.object(self.auth.auth_manager, 'test_authentication', return_value=True):
                status = self.auth._get_auth_status_message()
                assert "✅ Authenticated via environment" in status
    
    def test_is_authenticated_check(self):
        """Test authentication check method."""
        # Initially not authenticated
        assert self.auth.is_authenticated() is False
        
        # Set as authenticated
        self.auth.auth_state['is_authenticated'] = True
        assert self.auth.is_authenticated() is True
    
    def test_create_auth_interface(self):
        """Test creating authentication interface."""
        interface = self.auth.create_auth_interface()
        assert interface is not None
        # Interface should be a Gradio Blocks object
        assert hasattr(interface, 'launch')
    
    def test_create_mini_auth_status(self):
        """Test creating mini auth status widget."""
        mini_auth, indicator, btn = self.auth.create_mini_auth_status()
        assert mini_auth is not None
        assert indicator is not None
        assert btn is not None


class TestEasyModalAuth:
    """Test EasyModalAuth class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.easy_auth = EasyModalAuth()
    
    def test_initialization(self):
        """Test easy auth initialization."""
        assert self.easy_auth.auth_sessions == {}
        assert self.easy_auth.authenticated_tokens == {}
        assert self.easy_auth.auth_flow_active is False
    
    @pytest.mark.asyncio
    async def test_start_auth_flow(self):
        """Test starting authentication flow."""
        auth_url, session_id = await self.easy_auth.start_auth_flow()
        
        assert session_id is not None
        assert len(session_id) > 0
        assert "modal.com" in auth_url
        assert session_id in self.easy_auth.auth_sessions
        assert self.easy_auth.auth_flow_active is True
    
    @pytest.mark.asyncio
    async def test_check_auth_status_invalid_session(self):
        """Test checking auth status with invalid session."""
        status = await self.easy_auth.check_auth_status("invalid-session")
        assert status['status'] == 'error'
        assert 'Invalid session ID' in status['message']
    
    @pytest.mark.asyncio
    async def test_check_auth_status_pending(self):
        """Test checking auth status for pending session."""
        auth_url, session_id = await self.easy_auth.start_auth_flow()
        
        status = await self.easy_auth.check_auth_status(session_id)
        assert status['status'] == 'pending'
        assert status['authenticated'] is False
    
    @pytest.mark.asyncio
    async def test_complete_auth_flow_success(self):
        """Test completing authentication flow successfully."""
        # Start flow
        auth_url, session_id = await self.easy_auth.start_auth_flow()
        
        # Simulate successful auth by modifying session
        import asyncio
        from datetime import datetime, timedelta
        
        # Wait a bit to simulate auth delay
        await asyncio.sleep(0.1)
        
        # Manually set session to success for test
        self.easy_auth.auth_sessions[session_id]['status'] = 'success'
        self.easy_auth.auth_sessions[session_id]['token_id'] = 'ak-demo123'
        self.easy_auth.auth_sessions[session_id]['token_secret'] = 'as-demosecret456'
        self.easy_auth.auth_sessions[session_id]['workspace'] = 'demo-workspace'
        
        # Complete flow
        tokens = await self.easy_auth.complete_auth_flow(session_id)
        
        assert tokens is not None
        assert tokens['token_id'] == 'ak-demo123'
        assert tokens['token_secret'] == 'as-demosecret456'
        assert tokens['workspace'] == 'demo-workspace'
        assert session_id not in self.easy_auth.auth_sessions  # Should be cleaned up
        assert session_id in self.easy_auth.authenticated_tokens
    
    @pytest.mark.asyncio
    async def test_complete_auth_flow_not_ready(self):
        """Test completing auth flow when not ready."""
        auth_url, session_id = await self.easy_auth.start_auth_flow()
        
        # Don't simulate success, try to complete immediately
        tokens = await self.easy_auth.complete_auth_flow(session_id)
        assert tokens is None
    
    def test_create_easy_auth_interface(self):
        """Test creating easy auth interface."""
        interface = self.easy_auth.create_easy_auth_interface()
        assert interface is not None
        assert hasattr(interface, 'launch')
    
    def test_status_html_generation(self):
        """Test status HTML generation."""
        # Test different statuses
        statuses = ['not_started', 'pending', 'success', 'error', 'expired', 'cancelled']
        
        for status in statuses:
            html = self.easy_auth._get_status_html(status)
            assert isinstance(html, str)
            assert len(html) > 0
            assert 'div' in html
    
    def test_progress_bar_html(self):
        """Test progress bar HTML generation."""
        html = self.easy_auth._get_progress_bar_html(50.0)
        assert isinstance(html, str)
        assert '50%' in html
        assert 'width: 50%' in html


class TestAuthenticationIntegration:
    """Integration tests for authentication components."""
    
    def test_auth_manager_dashboard_integration(self):
        """Test integration between auth manager and dashboard."""
        dashboard_auth = DashboardAuthenticator()
        
        # Test that dashboard uses auth manager correctly
        assert dashboard_auth.auth_manager is not None
        assert isinstance(dashboard_auth.auth_manager, ModalAuthManager)
    
    def test_environment_consistency(self):
        """Test consistency between environment and config handling."""
        auth_manager = ModalAuthManager()
        
        config = ModalAuthConfig(
            token_id="ak-test123",
            token_secret="as-testsecret456",
            workspace="test-workspace"
        )
        
        with patch.dict(os.environ, {}, clear=True):
            # Apply config to environment
            auth_manager.apply_auth_to_env(config)
            
            # Read back from environment
            read_config = auth_manager.get_auth_from_env()
            
            assert read_config is not None
            assert read_config.token_id == config.token_id
            assert read_config.token_secret == config.token_secret
            assert read_config.workspace == config.workspace
    
    @patch('modal_for_noobs.auth_manager.subprocess.run')
    def test_full_auth_workflow(self, mock_run):
        """Test complete authentication workflow."""
        mock_run.return_value.returncode = 0
        
        auth_manager = ModalAuthManager()
        
        # Create config
        config = ModalAuthConfig(
            token_id="ak-workflow123",
            token_secret="as-workflowsecret456"
        )
        
        # Validate
        is_valid, errors = config.validate()
        assert is_valid is True
        
        # Test authentication
        auth_success = auth_manager.test_authentication(config)
        assert auth_success is True
        
        # Apply to environment
        with patch.dict(os.environ, {}, clear=True):
            auth_manager.apply_auth_to_env(config)
            
            # Verify environment
            is_env_valid, env_issues = auth_manager.validate_environment()
            assert is_env_valid is True
            assert len(env_issues) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=modal_for_noobs.auth_manager", "--cov=modal_for_noobs.dashboard_auth", "--cov=modal_for_noobs.easy_auth"])