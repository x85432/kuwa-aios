import os
import random

import pytest
from pathlib import Path

from mcp_openai import MCPClient
from mcp_openai.config import (
    MCPClientConfig,
    MCPServerConfig,
    LLMRequestConfig,
    LLMClientConfig,
)

import os
import sys
import asyncio
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kuwa.executor import LLMExecutor, Modelfile

logger = logging.getLogger(__name__)


class McpExecutor(LLMExecutor):
    def __init__(self):
        super().__init__()

    def extend_arguments(self, parser):
        """
        Override this method to add custom command-line arguments.
        """
        parser.add_argument(
            "--delay", type=float, default=0.02, help="Inter-token delay"
        )

    def setup(self):
        self.stop = False

    async def llm_compute(self, history: list[dict], modelfile: Modelfile):
        try:
            self.stop = False
            if history[-1]["content"] == "/crash":
                raise RuntimeError("oiiaioiiiiai")
            for i in "".join([i["content"] for i in history]).strip():
                yield i
                if self.stop:
                    self.stop = False
                    break
                await asyncio.sleep(
                    modelfile.parameters.get("llm_delay", self.args.delay)
                )
        except Exception:
            logger.exception("Error occurs during generation.")
            raise
        finally:
            logger.debug("finished")

    async def abort(self):
        self.stop = True
        logger.debug("aborted")
        return "Aborted"


if __name__ == "__main__":
    executor = McpExecutor()
    executor.run()

async def client():
    server_path = Path(__file__).parent / "server" / "example.py"
    server_name = "calculator"
    client = MCPClient(
        MCPClientConfig(
            mcpServers={
                server_name: MCPServerConfig(
                    command="python",
                    args=[str(server_path)],
                )
            }
        ),
        LLMClientConfig(
            api_key=os.getenv("API_KEY"),
            base_url=os.environ.get("BASE_URL"),
        ),
        LLMRequestConfig(
            model=os.environ.get("MODEL_NAME"),
            # seed=42,
        ),
    )

    await client.connect_to_server(server_name)
    yield client


@pytest.mark.asyncio()
class TestServer:
    """Test suite for calculator operations"""

    async def test_addition(self, client):
        a, b = random.randint(1, 400), random.randint(1, 400)
        messages = [{"role": "user", "content": f"What is {a} + {b}?"}]
        messages = await client.process_messages(messages)
        response = messages[-1]["content"]
        assert str(a + b) in response
        assert len(messages) == 4

    async def test_subtraction(self, client):
        a, b = random.randint(1, 400), random.randint(1, 400)
        messages = [{"role": "user", "content": f"What is {a} - {b}?"}]
        messages = await client.process_messages(messages)
        response = messages[-1]["content"]
        assert str(a - b) in response
        assert len(messages) == 4

    async def test_multiplication(self, client):
        a, b = random.randint(1, 9), random.randint(1, 9)
        messages = [{"role": "user", "content": f"What is {a} × {b}?"}]
        messages = await client.process_messages(messages)
        response = messages[-1]["content"]
        assert str(a * b) in response
        assert len(messages) == 4

    async def test_division(self, client):
        a, b = random.randint(2, 400), random.randint(1, 400)
        messages = [{"role": "user", "content": f"What is {a * b} ÷ {b}?"}]
        messages = await client.process_messages(messages)
        response = messages[-1]["content"]
        assert str(a) in response
        assert len(messages) == 4

    async def test_all_operations(self, client):
        a, b = random.randint(1, 400), random.randint(1, 400)
        content = (
            f"What is {a} + {b}?",
            f"What is {a} - {b}?",
            f"What is {a} × {b}?",
            f"What is {a * b} ÷ {b}?",
        )
        messages = [{"role": "user", "content": "\n".join(content)}]
        messages = await client.process_messages(messages)
        response = messages[-1]["content"]
        assert str(a + b) in response
        assert str(a - b) in response
        assert str(a * b) in response
        assert str(a) in response
        assert len(messages) == 7

    # @pytest.mark.skip(reason="Not implemented")
    async def test_nested_operations(self, client):
        a, b, c = random.randint(40, 60), random.randint(40, 60), random.randint(2, 5)
        messages = [
            {
                "role": "system",
                "content": (
                    "Solve the expression step by step, following the order of "
                    "operations (PEMDAS). Solve one step at a time. Use **only** "
                    "one function at a time between `add`, `sub`, `mul` and `div`."
                ),
            },
            {"role": "user", "content": f"What is ({a} + {b}) × {c}?"},
        ]
        messages = await client.process_messages(messages)
        print("LEN MESSAGES", len(messages))

        from pprint import pprint

        pprint(messages)

        response = messages[-1]["content"]
        assert str((a + b) * c) in response
        assert len(messages) == 8