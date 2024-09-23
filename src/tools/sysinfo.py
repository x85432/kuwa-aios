#!/usr/local/bin/python

import platform
from importlib.metadata import version

def get_kuwa_info():
    result  = [
        "**System information**",
        f"- Platform: {platform.platform()}",
        f"- Kuwa-executor version: {version('kuwa-executor')}"
    ]
    return result
    
def get_torch_info():
    try:
        import torch
    except ImportError:
        return ["- Torch is not installed."]
    result = [
        "**Torch information**",
        f"- Pytorch version: {torch.__version__}",
        f"- Is CUDA available?: {torch.cuda.is_available()}",
        ]
    if torch.cuda.is_available():
        device = torch.device('cuda')
        result += [
            f"- Linked CUDA version: {torch.version.cuda}",
            f"- Number of CUDA devices: {torch.cuda.device_count()}",
            f"- A torch tensor: {torch.rand(5).to(device)}",
        ]
    return result

if __name__ == "__main__":
    sysinfo = get_kuwa_info() + [''] + get_torch_info()
    print('\n'.join(sysinfo))