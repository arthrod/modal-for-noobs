"""Modal-for-noobs: Easy Modal deployment for Gradio apps."""

__version__ = "0.2.0"
__author__ = "Arthur Souza Rodrigues"
__email__ = "arthrod@umich.edu"

from .cli import app, main
from .config import config
from .modal_deploy import ModalDeployer

__all__ = ["__author__", "__email__", "__version__", "app", "main", "config", "ModalDeployer"]
