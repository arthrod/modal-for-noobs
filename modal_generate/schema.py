from dataclasses import dataclass

from modal.gpu import GPU_T


@dataclass
class RemoteFunctionDefinition:
    name: str
    keep_warm: int = 0
    gpu: GPU_T = None
    num_gpus: int = None
    local_files: dict[str, str] = None
    secret: str = None
    volume: dict[str, str] = None
    timeout: int = 60
