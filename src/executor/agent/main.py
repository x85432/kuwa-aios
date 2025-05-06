import os
import sys
import logging
import asyncio
import i18n
import pydantic
from typing import List, Dict
from httpx import HTTPStatusError
from enum import Enum

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kuwa.executor import LLMExecutor, Modelfile
from kuwa.client import KuwaClient

logger = logging.getLogger(__name__)


def parse_flow(
    modelfile: Modelfile,
    show_step_log: bool,
    append_history: bool,
    default_bot=".bot/copycat",
):
    if modelfile.input_bot is None:
        logger.info('No "INPUT-BOT" instruction found in the Botfile.')
    if modelfile.process_bot is None:
        logger.info('No "PROCESS-BOT" or "FROM" instruction found in the Botfile.')
    if modelfile.output_bot is None:
        logger.info('No "OUTPUT-BOT" instruction found in the Botfile.')

    bot_list = [modelfile.input_bot, modelfile.process_bot, modelfile.output_bot]
    prefix_list = [
        modelfile.input_prefix,
        modelfile.before_prompt,
        modelfile.output_prefix,
    ]
    suffix_list = [
        modelfile.input_suffix,
        modelfile.after_prompt,
        modelfile.output_suffix,
    ]

    reversed_flow = []
    last_bot = True
    for bot, prefix, suffix in list(zip(bot_list, prefix_list, suffix_list))[::-1]:
        if bot is None:
            continue
        reversed_flow.append(
            BotNode(
                bot_name=str(bot),
                prompt_prefix=str(prefix or ""),
                prompt_suffix=str(suffix or ""),
                show_response=bool(show_step_log or last_bot),
                append_history=append_history,
            )
        )
        last_bot = False

    flow = list(reversed(reversed_flow))
    if len(flow) == 0:
        flow.append(
            BotNode(
                bot_name=str(default_bot),
                prompt_prefix="",
                prompt_suffix="",
                show_response=True,
            )
        )
    return flow


class AgentState(Enum):
    IDLE = 0
    RUNNING = 1
    ABORTING = 2


class BotNode(pydantic.BaseModel):
    bot_name: str
    prompt_prefix: str
    prompt_suffix: str
    show_response: bool
    append_history: bool


class AgentRunner:
    api_base_url: str = ""
    kernel_url: str = ""
    api_key: str = ""
    state: AgentState = AgentState.IDLE

    def __init__(self, api_base_url, kernel_url, api_key):
        self.api_base_url = api_base_url
        self.kernel_url = kernel_url
        self.api_key = api_key
        self.state = AgentState.IDLE

    async def _invoke_bot(self, bot_name, history):
        client = KuwaClient(
            base_url=self.api_base_url,
            kernel_base_url=self.kernel_url,
            model=bot_name,
            auth_token=self.api_key,
        )

        try:
            generator = client.chat_complete(messages=history)
            async for chunk in generator:
                if self.state == AgentState.ABORTING:
                    await client.abort()
                    self.state = AgentState.IDLE
                    return
                yield chunk
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                yield i18n.t("agent.bot_not_found") + bot_name
                return
            else:
                raise

    async def run_flow(self, history: List[Dict], flow: List[BotNode]):
        self.state = AgentState.RUNNING

        memory = history.copy()

        for node in flow:
            prompt = node.prompt_prefix + memory[-1]["content"] + node.prompt_suffix
            memory[-1]["content"] = prompt
            generator = self._invoke_bot(
                bot_name=node.bot_name,
                history=memory,
            )
            response = ""
            async for chunk in generator:
                response += chunk
                if node.show_response:
                    yield chunk

            if self.state != AgentState.RUNNING:
                return

            if node.show_response:
                yield "\n"

            response_record = {"role": "user", "content": response}
            if node.append_history:
                # Invert user and assistant
                memory = [
                    dict(
                        i,
                        role=dict(user="assistant", assistant="user").get(
                            i["role"], i["role"]
                        ),
                    )
                    for i in memory
                ]
                memory.append(response_record)
            else:
                memory = [response_record]

    async def abort(self):
        self.state = AgentState.ABORTING

        while self.state == AgentState.IDLE:
            asyncio.sleep(0.5)


class AgentExecutor(LLMExecutor):
    runner: AgentRunner | None = None

    def __init__(self):
        super().__init__()

    def extend_arguments(self, parser):
        """
        Override this method to add custom command-line arguments.
        """
        parser.add_argument(
            "--api_base_url",
            default="http://127.0.0.1/",
            help="The API base URL of Kuwa multi-chat WebUI",
        )
        parser.add_argument(
            "--api_key",
            default=None,
            help="The API authentication token of Kuwa multi-chat WebUI",
        )

    def setup(self):
        i18n.load_path.append("lang/")
        self.state = AgentState.IDLE

    def setup_i18n(self, lang):
        i18n.config.set("error_on_missing_translation", True)
        i18n.config.set("fallback", "en")
        i18n.config.set("locale", lang)

    async def llm_compute(self, history: list[dict], modelfile: Modelfile):
        self.setup_i18n(modelfile.parameters["_lang"])
        api_key = modelfile.parameters.get("_user_token", self.args.api_key)
        if api_key is None:
            yield i18n.t("agent.no_kuwa_api_key")
        api_base_url = modelfile.parameters.get(
            "_kuwa_api_base_urls", [self.args.api_base_url]
        )[0]
        show_step_log = modelfile.parameters["agent_"].get("show_step_log", False)
        append_history = modelfile.parameters["agent_"].get("append_history", False)

        flow = parse_flow(
            modelfile=modelfile,
            show_step_log=show_step_log,
            append_history=append_history,
        )
        if len(flow) == 0:
            yield i18n.t("agent.no_input_bot")
            return

        self.runner = AgentRunner(
            api_base_url=api_base_url, kernel_url=self.kernel_url, api_key=api_key
        )
        try:
            generator = self.runner.run_flow(history=history, flow=flow)

            async for chunk in generator:
                yield chunk
        finally:
            self.runner = None

    async def abort(self):
        if self.runner is not None:
            await self.runner.abort()
            self.runner = None
        logger.debug("aborted")
        return "Aborted"


if __name__ == "__main__":
    executor = AgentExecutor()
    executor.run()
