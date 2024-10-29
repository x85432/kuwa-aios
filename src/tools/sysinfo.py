#!/usr/local/bin/python

import os
import platform
import requests
from urllib.parse import urljoin
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

def get_env_var():
    result = ["**Environment Variables**"]
    env = dict(os.environ)
    env["KUWA_API_KEY"] = "******"
    env = dict(sorted(env.items()))
    result.extend([f'{k}={v}' for k,v in env.items()])

    return result

def get_kernel_info():
    result = ["**Registered Executors**"]
    kernel_debug_url = urljoin(os.environ.get("KUWA_KERNEL_BASE_URL"), "./worker/debug")

    try:
        resp = requests.get(kernel_debug_url, headers={"Accept":"application/json"})
        resp.raise_for_status()
        registered_executors = resp.json()
        result.extend([
            "| Access Code (ID) | Endpoint | Status | Job History ID | Job User ID |",
            "|---|---|---|---|---|",
        ])
        for access_code, group in registered_executors.items():
            result.extend([
                "|{access_code}|{endpoint}|{status}|{job_history_id}|{job_user_id}|".format(
                    access_code=access_code,
                    **executor,
                )
                for executor in group
            ])
    except Exception as e:
        result.append(f"Failed to get registered executors form kernel: {repr(e)}")
    finally:
        return result


if __name__ == "__main__":
    sysinfo = [get_kuwa_info(), get_torch_info(), get_env_var(), get_kernel_info()]
    print('\n\n'.join(['\n'.join(section) for section in sysinfo]))