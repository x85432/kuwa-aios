import os
import sys
import logging
import subprocess
import tempfile
from pathlib import Path
from enum import Enum
from transformers import AutoTokenizer
from functools import lru_cache

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(Path(__file__).parent)))

from pipe.main import PipeExecutor
from kuwa.executor import LLMExecutor, Modelfile

logger = logging.getLogger(__name__)


class DecodeBuffer:
    """
    Decodes a byte stream, handling partial decoding.
    """

    def __init__(self, coding="utf-8"):
        self.coding = coding
        self.buffer = bytearray()

    def push(self, chunk: bytes):
        """
        Adds a chunk to buffer and decode partially.

        Args:
            chunk: The byte chunk to add.

        Returns:
            The decoded UTF-8 string (as much as possible)
        """
        self.buffer += chunk
        decoded_string = ""
        i = len(self.buffer)
        while i > 0:
            try:
                decoded_string = self.buffer[:i].decode(self.coding)
                break
            except UnicodeDecodeError:
                i -= 1
        self.buffer = self.buffer[i:]
        return decoded_string

    def finalize(self, chunk: bytes = b""):
        self.buffer += chunk
        if len(self.buffer) != 0:
            logger.debug(f"[DecodeBuffer] undecoded buffer content: {self.buffer}")
        return self.buffer.decode(self.coding, "replace")


class OutputState(Enum):
    PROMPT_PROCESSING = 0
    TOKEN_GENERATION = 1
    POST_GENERATION = 2


class QnnGenieExecutor(LLMExecutor):
    def __init__(self):
        super().__init__()

    def extend_arguments(self, parser):
        parser.add_argument(
            "--tokenizer",
            type=str,
            default="meta-llama/Llama-3.2-3B-Instruct",
            help="HF repository ID of the tokenizer.",
        )
        parser.add_argument(
            "--model", type=str, default="llama-v3_2-3b-chat", help="Model ID"
        )
        pass

    def setup(self):
        self.model_id = self.args.model
        self.hf_hub_model_id = self.args.tokenizer
        self.stop = False
        self.tokenizer = self.get_tokenizer(self.hf_hub_model_id)
        self.pipe = None

    @lru_cache
    def get_tokenizer(self, hf_hub_model_id):
        tokenizer = AutoTokenizer.from_pretrained(hf_hub_model_id)
        return tokenizer

    async def run_genie_t2t(
        self, prompt: str, model_id: str, print_debug: bool = False
    ):
        # prompt = prompt.replace('\n', '\\n')
        # qai_hub_model_id = model_id.replace("-", "_") + "_quantized"
        working_dir = str((Path.cwd() / model_id).resolve())
        prompt_fd, prompt_file_path = tempfile.mkstemp()
        with os.fdopen(prompt_fd, "w+", encoding="utf-8") as f:
            f.write(prompt)
            f.seek(0)
            logger.debug(f"[prompt] {f.read()}")

        qnn_binary_path = (Path.cwd() / "QNN_binaries-2.31").resolve()
        genie_t2t_run_paths = list(qnn_binary_path.glob("genie-t2t-run*"))
        genie_config_path = "genie_config.json"
        if len(genie_t2t_run_paths) == 0:
            raise RuntimeError(
                f'Could not find "genie_t2t_run" executable in directory "{qnn_binary_path}"'
            )
        cmd = [
            genie_t2t_run_paths[0],
            "-c",
            genie_config_path,
            "--prompt_file",
            prompt_file_path,
        ]
        cmd = [str(arg) for arg in cmd]

        try:
            self.pipe = PipeExecutor()

            generator = self.pipe.run_cmd(cmd, cwd=working_dir, shell=False)
            # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=working_dir, shell=False)
            # decode_buffer = DecodeBuffer()
            begin_keyword = "[BEGIN]:"  # [TODO] Remove llama header
            end_keyword = "[END]"
            output_buffer = ""
            output_state = OutputState.PROMPT_PROCESSING
            async for stream_name, chunk in generator:
                # for chunk in iter(lambda: p.stdout.read(1), b''):
                #     decoded_string = decode_buffer.push(chunk)

                if self.in_debug():
                    print(chunk, end="", flush=True)

                if print_debug:
                    yield chunk
                    continue

                output_buffer += chunk

                if (
                    output_state == OutputState.PROMPT_PROCESSING
                    and begin_keyword in output_buffer
                ):
                    output_state = OutputState.TOKEN_GENERATION
                    output_buffer = output_buffer[
                        output_buffer.index(begin_keyword) + len(begin_keyword) :
                    ].lstrip()

                if output_state == OutputState.TOKEN_GENERATION:
                    if len(output_buffer) < len(end_keyword):
                        continue
                    if output_buffer.endswith(end_keyword):
                        output_state = OutputState.POST_GENERATION
                        output_buffer = output_buffer.replace(end_keyword, "")
                        yield output_buffer
                    else:
                        output_length = len(output_buffer) - len(end_keyword)
                        output_chunk = output_buffer[:output_length]
                        output_buffer = output_buffer[output_length:]
                        yield output_chunk

        except subprocess.CalledProcessError as e:
            logger.exception(e.output.decode())
        finally:
            os.remove(prompt_file_path)

    async def llm_compute(self, history: list[dict], modelfile: Modelfile):
        model_id = modelfile.parameters["llm_"].get("model", self.model_id)
        tokenizer_id = modelfile.parameters["llm_"].get(
            "tokenizer", self.hf_hub_model_id
        )
        print_debug = modelfile.parameters["llm_"].get("debug", False)

        self.tokenizer = self.get_tokenizer(tokenizer_id)
        prompt = self.tokenizer.apply_chat_template(
            history, tokenize=False, add_generation_prompt=True
        )

        response_generator = self.run_genie_t2t(
            prompt=prompt, model_id=model_id, print_debug=print_debug
        )

        self.stop = False
        async for reply in response_generator:
            if self.stop:
                await response_generator.aclose()
            yield reply
        logger.info("Done")

    async def abort(self):
        self.stop = True
        if self.pipe:
            await self.pipe.abort()
        logger.debug("aborted")
        return "Aborted"


if __name__ == "__main__":
    executor = QnnGenieExecutor()
    executor.run()
