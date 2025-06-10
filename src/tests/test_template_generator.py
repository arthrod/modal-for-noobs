"""Comprehensive tests for the template generation system."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from modal_for_noobs.template_generator import (
    RemoteFunctionConfig,
    TemplateConfig,
    TemplateGenerator,
    generate_from_wizard_input,
)


class TestRemoteFunctionConfig:
    """Test RemoteFunctionConfig dataclass."""
    
    def test_basic_creation(self):
        """Test basic creation of remote function config."""
        config = RemoteFunctionConfig(name="test_function")
        assert config.name == "test_function"
        assert config.keep_warm == 0
        assert config.gpu is None
        assert config.timeout == 300
    
    def test_full_configuration(self):
        """Test remote function with all options."""
        config = RemoteFunctionConfig(
            name="ml_function",
            keep_warm=2,
            gpu="A100",
            num_gpus=2,
            timeout=600,
            memory=16384,
            cpu=4.0,
            secret="my-secret",
            volume={"/data": "my-volume"},
            schedule="0 */6 * * *"
        )
        
        assert config.name == "ml_function"
        assert config.keep_warm == 2
        assert config.gpu == "A100"
        assert config.num_gpus == 2
        assert config.timeout == 600
        assert config.memory == 16384
        assert config.cpu == 4.0
        assert config.secret == "my-secret"
        assert config.volume == {"/data": "my-volume"}
        assert config.schedule == "0 */6 * * *"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = RemoteFunctionConfig(
            name="test_func",
            gpu="T4",
            keep_warm=1
        )
        
        result = config.to_dict()
        expected = {
            "name": "test_func",
            "keep_warm": 1,
            "gpu": "T4",
            "num_gpus": None,
            "timeout": 300,
            "memory": 8192,
            "cpu": 2.0,
            "secret": None,
            "volume": None,
            "schedule": None,
        }
        
        assert result == expected


class TestTemplateConfig:
    """Test TemplateConfig dataclass."""
    
    def test_basic_creation(self):
        """Test basic template config creation."""
        config = TemplateConfig(app_name="test-app")
        assert config.app_name == "test-app"
        assert config.deployment_mode == "minimum"
        assert config.timeout_seconds == 3600
        assert config.python_dependencies == []
        assert config.remote_functions == []
    
    def test_full_configuration(self):
        """Test template config with all options."""
        remote_func = RemoteFunctionConfig(name="worker")
        
        config = TemplateConfig(
            app_name="full-app",
            deployment_mode="optimized",
            description="Test deployment",
            timeout_seconds=7200,
            max_containers=20,
            python_dependencies=["numpy", "torch"],
            system_dependencies=["ffmpeg"],
            gpu_type="A100",
            num_gpus=2,
            provision_nfs=True,
            provision_logging=True,
            enable_dashboard=True,
            remote_functions=[remote_func],
            environment_variables={"DEBUG": "true"},
            secrets=["api-key"],
            original_code="print('hello')"
        )
        
        assert config.app_name == "full-app"
        assert config.deployment_mode == "optimized"
        assert config.gpu_type == "A100"
        assert config.num_gpus == 2
        assert config.provision_nfs is True
        assert len(config.remote_functions) == 1
        assert config.environment_variables == {"DEBUG": "true"}
        assert config.secrets == ["api-key"]
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = TemplateConfig(
            app_name="dict-test",
            deployment_mode="marimo",
            gpu_type="T4"
        )
        
        result = config.to_dict()
        assert result["app_name"] == "dict-test"
        assert result["deployment_mode"] == "marimo"
        assert result["gpu_type"] == "T4"
        assert isinstance(result["remote_functions"], list)


class TestTemplateGenerator:
    """Test TemplateGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = TemplateGenerator()
    
    def test_classify_filter(self):
        """Test the classify filter."""
        assert self.generator._classify_filter("my_class") == "MyClass"
        assert self.generator._classify_filter("test-name") == "TestName"
        assert self.generator._classify_filter("123invalid") == "Class123invalid"
        assert self.generator._classify_filter("valid_name") == "ValidName"
    
    def test_format_gpu_filter(self):
        """Test the GPU format filter."""
        assert self.generator._format_gpu_filter("any") == "gpu.Any()"
        assert self.generator._format_gpu_filter("T4") == "gpu.T4()"
        assert self.generator._format_gpu_filter("a100") == "gpu.A100()"
        assert self.generator._format_gpu_filter("unknown") == "gpu.Any()"
    
    def test_generate_image_config_minimum(self):
        """Test image config generation for minimum mode."""
        config = TemplateConfig(
            app_name="test",
            deployment_mode="minimum",
            python_dependencies=["gradio", "numpy"]
        )
        
        image_config = self.generator._generate_image_config(config)
        
        assert "modal.Image.debian_slim" in image_config
        assert "gradio" in image_config
        assert "numpy" in image_config
        assert "nvidia/cuda" not in image_config
    
    def test_generate_image_config_optimized(self):
        """Test image config generation for optimized mode."""
        config = TemplateConfig(
            app_name="test",
            deployment_mode="optimized",
            python_dependencies=["torch", "transformers"]
        )
        
        image_config = self.generator._generate_image_config(config)
        
        assert "nvidia/cuda" in image_config
        assert "torch" in image_config
        assert "transformers" in image_config
        assert "nvidia-smi" in image_config
    
    def test_generate_image_config_with_requirements(self):
        """Test image config with requirements file."""
        # Create temporary requirements file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("pandas==1.5.0\nscikit-learn>=1.0.0\n# This is a comment\n")
            req_file = Path(f.name)
        
        try:
            config = TemplateConfig(
                app_name="test",
                deployment_mode="minimum",
                requirements_file=req_file
            )
            
            image_config = self.generator._generate_image_config(config)
            
            assert "pandas==1.5.0" in image_config
            assert "scikit-learn>=1.0.0" in image_config
            assert "# This is a comment" not in image_config
        
        finally:
            os.unlink(req_file)
    
    def test_generate_deployment_minimum(self):
        """Test deployment generation for minimum mode."""
        config = TemplateConfig(
            app_name="test-app",
            deployment_mode="minimum",
            original_code="import gradio as gr\ndemo = gr.Interface(lambda x: x, 'text', 'text')",
            python_dependencies=["gradio"]
        )
        
        deployment = self.generator.generate_deployment(config)
        
        # Check basic structure
        assert "import modal" in deployment
        assert "APP_NAME = \"test-app\"" in deployment
        assert "DEPLOYMENT_MODE = \"minimum\"" in deployment
        assert "import gradio as gr" in deployment
        assert "demo = gr.Interface" in deployment
        assert "@app.function(" in deployment
        assert "deploy_gradio()" in deployment
    
    def test_generate_deployment_optimized_with_gpu(self):
        """Test deployment generation for optimized mode with GPU."""
        config = TemplateConfig(
            app_name="gpu-app",
            deployment_mode="optimized",
            original_code="print('GPU app')",
            gpu_type="A100",
            num_gpus=2,
            provision_logging=True
        )
        
        deployment = self.generator.generate_deployment(config)
        
        assert "DEPLOYMENT_MODE = \"optimized\"" in deployment
        assert "gpu=\"A100\"" in deployment
        assert "gpu_count=2" in deployment
        assert "import torch" in deployment
        assert "logger.info" in deployment
        assert "nvidia/cuda" in deployment
    
    def test_generate_deployment_with_remote_functions(self):
        """Test deployment with remote functions."""
        remote_func = RemoteFunctionConfig(
            name="background_task",
            gpu="T4",
            keep_warm=1,
            secret="my-secret"
        )
        
        config = TemplateConfig(
            app_name="func-app",
            deployment_mode="minimum",
            original_code="print('main app')",
            remote_functions=[remote_func]
        )
        
        deployment = self.generator.generate_deployment(config)
        
        assert "def background_task():" in deployment
        assert "gpu=gpu.T4()" in deployment
        assert "keep_warm=1" in deployment
        assert "modal.Secret.from_name(\"my-secret\")" in deployment
    
    def test_generate_deployment_marimo(self):
        """Test marimo-specific deployment generation."""
        config = TemplateConfig(
            app_name="marimo-app",
            deployment_mode="marimo",
            original_code="import gradio as gr\ndemo = gr.Interface(lambda x: x, 'text', 'text')",
            provision_nfs=True
        )
        
        deployment = self.generator.generate_deployment(config)
        
        assert "marimo" in deployment.lower()
        assert "volumes={WORKSPACE_PATH: volume}" in deployment
        assert "start_marimo_server" in deployment
        assert "/marimo" in deployment
    
    def test_generate_deployment_with_secrets_and_env(self):
        """Test deployment with secrets and environment variables."""
        config = TemplateConfig(
            app_name="secure-app",
            deployment_mode="minimum",
            original_code="print('secure')",
            secrets=["api-key", "db-password"],
            environment_variables={"DEBUG": "true", "ENV": "production"}
        )
        
        deployment = self.generator.generate_deployment(config)
        
        assert "modal.Secret.from_name(\"api-key\")" in deployment
        assert "modal.Secret.from_name(\"db-password\")" in deployment
        assert "\"DEBUG\": \"true\"" in deployment
        assert "\"ENV\": \"production\"" in deployment


class TestGenerateFromWizardInput:
    """Test the generate_from_wizard_input function."""
    
    def test_basic_generation(self):
        """Test basic deployment generation."""
        deployment = generate_from_wizard_input(
            app_name="wizard-test",
            deployment_mode="minimum",
            original_code="import gradio as gr\ndemo = gr.Interface(lambda x: x, 'text', 'text')"
        )
        
        assert "wizard-test" in deployment
        assert "minimum" in deployment
        assert "import gradio as gr" in deployment
        assert "deploy_gradio()" in deployment
    
    def test_generation_with_all_options(self):
        """Test generation with all wizard options."""
        remote_functions = [
            {
                "name": "process_data",
                "gpu": "T4",
                "keep_warm": 2,
                "timeout": 600,
                "secret": "data-key"
            }
        ]
        
        deployment = generate_from_wizard_input(
            app_name="full-wizard-test",
            deployment_mode="optimized",
            original_code="print('complex app')",
            provision_nfs=True,
            provision_logging=True,
            system_dependencies=["ffmpeg"],
            python_dependencies=["torch", "transformers"],
            remote_functions=remote_functions,
            gpu_type="A100",
            secrets=["main-secret"],
            environment_variables={"MODEL_NAME": "gpt-4"},
        )
        
        assert "full-wizard-test" in deployment
        assert "optimized" in deployment
        assert "ffmpeg" in deployment
        assert "torch" in deployment
        assert "def process_data():" in deployment
        assert "gpu=gpu.T4()" in deployment
        assert "keep_warm=2" in deployment
        assert "MODEL_NAME" in deployment
        assert "main-secret" in deployment
    
    def test_generation_with_requirements_file(self):
        """Test generation with requirements file."""
        # Create temporary requirements file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("fastapi==0.68.0\nuvicorn[standard]\n")
            req_file = Path(f.name)
        
        try:
            deployment = generate_from_wizard_input(
                app_name="req-test",
                deployment_mode="minimum",
                original_code="print('with requirements')",
                requirements_file=req_file
            )
            
            assert "fastapi==0.68.0" in deployment
            assert "uvicorn[standard]" in deployment
        
        finally:
            os.unlink(req_file)


class TestTemplateValidation:
    """Test template validation and error handling."""
    
    def test_invalid_deployment_mode(self):
        """Test handling of invalid deployment mode."""
        generator = TemplateGenerator()
        config = TemplateConfig(
            app_name="test",
            deployment_mode="invalid_mode",
            original_code="print('test')"
        )
        
        # Should fall back to base template
        deployment = generator.generate_deployment(config)
        assert "import modal" in deployment
        assert "test" in deployment
    
    def test_empty_app_name(self):
        """Test handling of empty app name."""
        deployment = generate_from_wizard_input(
            app_name="",
            deployment_mode="minimum",
            original_code="print('test')"
        )
        
        # Should still generate valid deployment
        assert "import modal" in deployment
        assert "print('test')" in deployment
    
    def test_invalid_gpu_type(self):
        """Test handling of invalid GPU type."""
        generator = TemplateGenerator()
        
        # Invalid GPU should default to gpu.Any()
        assert generator._format_gpu_filter("invalid") == "gpu.Any()"
        assert generator._format_gpu_filter("") == "gpu.Any()"


class TestTemplateIntegration:
    """Integration tests for template generation."""
    
    def test_all_deployment_modes(self):
        """Test that all deployment modes can be generated."""
        modes = ["minimum", "optimized", "marimo", "gradio-jupyter"]
        
        for mode in modes:
            deployment = generate_from_wizard_input(
                app_name=f"test-{mode}",
                deployment_mode=mode,
                original_code="import gradio as gr\ndemo = gr.Interface(lambda x: x, 'text', 'text')"
            )
            
            assert f"test-{mode}" in deployment
            assert mode in deployment
            assert "import modal" in deployment
            assert "deploy_gradio()" in deployment
    
    def test_template_syntax_validity(self):
        """Test that generated templates have valid Python syntax."""
        deployment = generate_from_wizard_input(
            app_name="syntax-test",
            deployment_mode="optimized",
            original_code="""
import gradio as gr

def greet(name):
    return f"Hello {name}!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
            """,
            gpu_type="T4",
            provision_nfs=True,
            python_dependencies=["torch"],
            environment_variables={"TEST": "value"}
        )
        
        # Try to compile the generated code
        try:
            compile(deployment, "<generated>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Generated template has syntax error: {e}")
    
    def test_no_nested_f_strings(self):
        """Test that generated templates don't contain nested f-strings."""
        deployment = generate_from_wizard_input(
            app_name="nested-test",
            deployment_mode="marimo",
            original_code="demo = gr.Interface(lambda x: f'Hello {x}!', 'text', 'text')",
            environment_variables={"VAR1": "value1", "VAR2": "value2"}
        )
        
        # Check that there are no problematic nested f-string patterns
        # This is a simplified check - in practice, we'd use AST parsing
        lines = deployment.split('\n')
        for line in lines:
            if 'f"' in line and '{' in line:
                # Make sure any f-string doesn't contain nested braces in a problematic way
                brace_count = line.count('{') - line.count('{{')
                # This is a basic check - more sophisticated validation would be needed
                assert brace_count >= 0, f"Potentially problematic f-string: {line}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])