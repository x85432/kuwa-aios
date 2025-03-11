import os
import sys
import logging
from chatgpt import ChatGptExecutor

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)


class NimExecutor(ChatGptExecutor):
    model_name: str = "nvidia/nemotron-4-340b-instruct"
    openai_base_url: str = "https://integrate.api.nvidia.com/v1/"
    api_token_name: str = "nim_token"
    token_display_name: str = "Nvidia NIM API"
    context_window: int = 131072

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    executor = NimExecutor()
    executor.run()
