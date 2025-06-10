"""🚀💚 Gradio Modal Deploy 💚🚀
Beautiful Gradio components for seamless Modal deployment and management.

Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨
"""

from .components import (
    ModalDeployButton,
    ModalExplorer,
    ModalStatusMonitor,
    ModalTheme,
)
from .decorators import (
    modal_auto_deploy,
    modal_gpu_when_needed,
    modal_memory_optimized,
)
from .utils import (
    deploy_to_modal,
    get_modal_status,
    setup_modal_auth,
)

__version__ = "0.1.0"
__author__ = "Arthur Souza Rodrigues (Neurotic Coder)"
__email__ = "arthrod@umich.edu"

__all__ = [
    # Components
    "ModalDeployButton",
    "ModalExplorer",
    "ModalStatusMonitor",
    "ModalTheme",
    "deploy_to_modal",
    "get_modal_status",
    # Decorators
    "modal_auto_deploy",
    "modal_gpu_when_needed",
    "modal_memory_optimized",
    # Utilities
    "setup_modal_auth",
]
