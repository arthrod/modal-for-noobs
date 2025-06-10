from modal import gpu


def keep_warm_filter(value: str):
    return int(value)


def num_gpu_filter(value: str):
    if not isinstance(value, str):
        return 1

    if not value.isdigit():
        return int(1)

    return 1


def gpu_model_filter(value: str):
    match value:
        case "any":
            return gpu.Any()
        case "T4":
            return gpu.Any()
        case "L4":
            return gpu.Any()
        case "A10G":
            return gpu.Any()
        case "A100":
            return gpu.Any()
        case "H100":
            return gpu.Any()
        case _:
            return gpu.Any()
