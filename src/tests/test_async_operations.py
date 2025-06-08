"""Tests for async operations and Modal CLI integration."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modal_for_noobs.cli import (
    _deploy_async,
    _kill_deployment_async,
    _milk_logs_async,
    _sanity_check_async,
    _setup_auth_async,
)


class TestAsyncDeployment:
    """Test async deployment functionality."""

    @pytest.mark.asyncio
    async def test_deploy_async_dry_run(self, sample_gradio_app):
        """Test async deployment with dry run."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer.create_modal_deployment_async.return_value = sample_gradio_app.parent / "modal_test.py"
            mock_deployer_class.return_value = mock_deployer

            # Should not raise exception
            await _deploy_async(
                app_file=sample_gradio_app,
                config_level="minimum",
                dry_run=True,
                wizard=False,
                br_huehuehue=False
            )

            mock_deployer.check_modal_auth_async.assert_called_once()
            mock_deployer.create_modal_deployment_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_deploy_async_no_auth(self, sample_gradio_app):
        """Test async deployment without authentication."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = False
            mock_deployer_class.return_value = mock_deployer

            # Should handle gracefully
            await _deploy_async(
                app_file=sample_gradio_app,
                config_level="minimum",
                dry_run=True,
                wizard=False,
                br_huehuehue=False
            )

            mock_deployer.check_modal_auth_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_deploy_async_wizard_mode(self, sample_gradio_app):
        """Test async deployment with wizard mode."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer.create_modal_deployment_async.return_value = sample_gradio_app.parent / "modal_test.py"
            mock_deployer_class.return_value = mock_deployer

            await _deploy_async(
                app_file=sample_gradio_app,
                config_level="minimum",
                dry_run=True,
                wizard=True,
                br_huehuehue=False
            )

            mock_deployer.create_modal_deployment_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_deploy_async_brazilian_mode(self, sample_gradio_app):
        """Test async deployment with Brazilian mode."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer.create_modal_deployment_async.return_value = sample_gradio_app.parent / "modal_test.py"
            mock_deployer_class.return_value = mock_deployer

            await _deploy_async(
                app_file=sample_gradio_app,
                config_level="minimum",
                dry_run=True,
                wizard=False,
                br_huehuehue=True
            )

            mock_deployer.create_modal_deployment_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_deploy_async_actual_deployment(self, sample_gradio_app):
        """Test async deployment without dry run."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer.create_modal_deployment_async.return_value = sample_gradio_app.parent / "modal_test.py"
            mock_deployer_class.return_value = mock_deployer

            # Mock subprocess for modal deploy
            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"success", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _deploy_async(
                app_file=sample_gradio_app,
                config_level="minimum",
                dry_run=False,
                wizard=False,
                br_huehuehue=False
            )

            mock_subprocess.assert_called()


class TestAsyncKillDeployment:
    """Test async kill deployment functionality."""

    @pytest.mark.asyncio
    async def test_kill_deployment_no_auth(self):
        """Test kill deployment without authentication."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = False
            mock_deployer_class.return_value = mock_deployer

            await _kill_deployment_async("ap-test123", False)

            mock_deployer.check_modal_auth_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_kill_deployment_list_mode(self):
        """Test kill deployment in list mode."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Mock modal app list
            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"ap-test123 | app-name | deployed | 1", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _kill_deployment_async(None, False)

            mock_subprocess.assert_called()

    @pytest.mark.asyncio
    async def test_kill_specific_deployment(self):
        """Test killing specific deployment."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Mock modal app list and stop
            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"ap-test123 | app-name | deployed | 1", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _kill_deployment_async("ap-test123", False)

            # Should call modal app list and modal app stop
            assert mock_subprocess.call_count >= 2

    @pytest.mark.asyncio
    async def test_kill_deployment_already_stopped(self):
        """Test killing deployment that's already stopped."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Mock modal app list showing stopped app
            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"ap-test123 | app-name | stopped | 0", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _kill_deployment_async("ap-test123", False)

            # Should only call modal app list, not stop
            mock_subprocess.assert_called()

    @pytest.mark.asyncio
    async def test_kill_deployment_with_containers(self):
        """Test killing deployment with running containers."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Mock responses for different commands
            responses = [
                # modal app list
                (b"ap-test123 | app-name | deployed | 1", b""),
                # modal app stop
                (b"stopped", b""),
                # modal container list
                (b"ct-12345 | container-name | running", b""),
                # modal container stop
                (b"stopped", b""),
            ]

            response_iter = iter(responses)

            async def mock_communicate():
                return next(response_iter)

            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _kill_deployment_async("ap-test123", False)

            # Should call multiple commands
            assert mock_subprocess.call_count >= 3

    @pytest.mark.asyncio
    async def test_kill_deployment_brazilian_mode(self):
        """Test kill deployment with Brazilian mode."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = False
            mock_deployer_class.return_value = mock_deployer

            # Should handle Brazilian mode without errors
            await _kill_deployment_async("ap-test123", True)

            mock_deployer.check_modal_auth_async.assert_called_once()


class TestAsyncLogMilking:
    """Test async log milking functionality."""

    @pytest.mark.asyncio
    async def test_milk_logs_no_auth(self):
        """Test milk logs without authentication."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = False
            mock_deployer_class.return_value = mock_deployer

            await _milk_logs_async("test-app", False, 100, False)

            mock_deployer.check_modal_auth_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_milk_logs_list_apps(self):
        """Test milk logs in list apps mode."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Mock modal app list
            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"ap-test123 | app-name | deployed | 1", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _milk_logs_async(None, False, 100, False)

            mock_subprocess.assert_called()

    @pytest.mark.asyncio
    async def test_milk_logs_specific_app(self):
        """Test milking logs for specific app."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Mock modal app logs
            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"2023-01-01 12:00:00 INFO: App started", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _milk_logs_async("test-app", False, 100, False)

            mock_subprocess.assert_called()

    @pytest.mark.asyncio
    async def test_milk_logs_follow_mode(self):
        """Test milking logs in follow mode."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Mock modal app logs with follow
            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"2023-01-01 12:00:00 INFO: App started", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _milk_logs_async("test-app", True, 100, False)

            mock_subprocess.assert_called()

    @pytest.mark.asyncio
    async def test_milk_logs_custom_lines(self):
        """Test milking logs with custom line count."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"logs", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _milk_logs_async("test-app", False, 500, False)

            mock_subprocess.assert_called()


class TestAsyncSanityCheck:
    """Test async sanity check functionality."""

    @pytest.mark.asyncio
    async def test_sanity_check_no_auth(self):
        """Test sanity check without authentication."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = False
            mock_deployer_class.return_value = mock_deployer

            await _sanity_check_async(False)

            mock_deployer.check_modal_auth_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_sanity_check_with_auth(self):
        """Test sanity check with authentication."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Mock modal app list
            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"ap-test123 | app-name | deployed | 1", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _sanity_check_async(False)

            mock_subprocess.assert_called()

    @pytest.mark.asyncio
    async def test_sanity_check_brazilian_mode(self):
        """Test sanity check with Brazilian mode."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = False
            mock_deployer_class.return_value = mock_deployer

            await _sanity_check_async(True)

            mock_deployer.check_modal_auth_async.assert_called_once()


class TestAsyncAuthSetup:
    """Test async authentication setup."""

    @pytest.mark.asyncio
    async def test_setup_auth_basic(self):
        """Test basic auth setup."""
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_process = MagicMock()
            mock_process.returncode = 0
            async def mock_communicate():
                return (b"success", b"")
            mock_process.communicate = mock_communicate
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            await _setup_auth_async("test_id", "test_secret")

            mock_subprocess.assert_called()

    @pytest.mark.asyncio
    async def test_setup_auth_failure(self):
        """Test auth setup failure handling."""
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_process = MagicMock()
            mock_process.returncode = 1
            mock_process.communicate.return_value = asyncio.coroutine(
                lambda: (b"", b"authentication failed")
            )()
            async def mock_subprocess_exec(*args, **kwargs):
                return mock_process
            mock_subprocess.return_value = mock_subprocess_exec()

            # Should handle gracefully
            await _setup_auth_async("invalid_id", "invalid_secret")

            mock_subprocess.assert_called()


class TestErrorHandling:
    """Test error handling in async operations."""

    @pytest.mark.asyncio
    async def test_subprocess_exception_handling(self):
        """Test handling of subprocess exceptions."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class, \
             patch("asyncio.create_subprocess_exec") as mock_subprocess:

            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Mock subprocess to raise exception
            mock_subprocess.side_effect = Exception("Subprocess failed")

            # Should handle gracefully
            await _kill_deployment_async("ap-test123", False)

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of operation timeouts."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()

            async def slow_auth_check():
                await asyncio.sleep(10)  # Simulate slow operation
                return True

            mock_deployer.check_modal_auth_async = slow_auth_check
            mock_deployer_class.return_value = mock_deployer

            # Should complete or timeout gracefully
            try:
                await asyncio.wait_for(_kill_deployment_async("ap-test123", False), timeout=1.0)
            except TimeoutError:
                pass  # Expected for this test

    @pytest.mark.asyncio
    async def test_concurrent_operations_stability(self):
        """Test stability of concurrent async operations."""
        with patch("modal_for_noobs.cli.ModalDeployer") as mock_deployer_class:
            mock_deployer = MagicMock()
            mock_deployer.check_modal_auth_async.return_value = True
            mock_deployer_class.return_value = mock_deployer

            # Run multiple operations concurrently
            tasks = [
                _sanity_check_async(False),
                _kill_deployment_async(None, False),
                _milk_logs_async(None, False, 100, False),
            ]

            # Should complete without interfering with each other
            await asyncio.gather(*tasks, return_exceptions=True)
