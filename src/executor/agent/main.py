import os
import sys
import asyncio
import logging
import json
import i18n
from httpx import HTTPStatusError
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kuwa.executor import LLMExecutor, Modelfile
from kuwa.client import KuwaClient

logger = logging.getLogger(__name__)

class AgentExecutor(LLMExecutor):
    def __init__(self):
        super().__init__()

    def extend_arguments(self, parser):
        """
        Override this method to add custom command-line arguments.
        """
        parser.add_argument('--api_base_url', default="http://127.0.0.1/", help='The API base URL of Kuwa multi-chat WebUI')
        parser.add_argument('--api_key', default=None, help='The API authentication token of Kuwa multi-chat WebUI')

    def setup(self):
        i18n.load_path.append('lang/')

    def setup_i18n(self, lang):
        i18n.config.set("error_on_missing_translation", True)
        i18n.config.set("fallback", "en")
        i18n.config.set("locale", lang)

    async def call_bot(self, api_base_url, api_key, bot_name, history):
        client = KuwaClient(
            base_url=api_base_url,
            kernel_base_url=self.kernel_url,
            model=bot_name,
            auth_token=api_key
        )

        try:
            generator = client.chat_complete(
                messages=history
            )
            async for chunk in generator:
                yield chunk
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                yield i18n.t("agent.bot_not_found") + bot_name
                return
            else:
                raise

    async def llm_compute(self, history: list[dict], modelfile:Modelfile):
        api_base_url = modelfile.parameters.get("_kuwa_api_base_urls", [self.args.api_base_url])[0]
        api_key = modelfile.parameters.get("_user_token", self.args.api_key)
        show_step_log = modelfile.parameters['agent_'].get("show_step_log", False)
        next_full_history = modelfile.parameters['agent_'].get("next_full_history", False)
        
        self.setup_i18n(modelfile.parameters["_lang"])

        if api_key is None:
            yield i18n.t("agent.no_kuwa_api_key" )        

        if modelfile.input_bot is None:
            yield i18n.t("agent.no_input_bot")
            return

        # =======================

        history[-1]['content'] = modelfile.before_prompt + history[-1]['content'] + modelfile.after_prompt
        generator = self.call_bot(
            api_base_url=api_base_url,
            api_key=api_key,
            bot_name=modelfile.input_bot,
            history=history
        )
        intermediate_result = ""
        async for chunk in generator:
            intermediate_result += chunk
            if show_step_log or modelfile.output_bot is None:
                yield chunk
        
        if modelfile.output_bot is None:
            logger.info("No \"OUTPUT-BOT\" instruction found in the Botfile.")
            return

        if show_step_log:
            yield "\n"

        # =======================
        
        if next_full_history:
            history[-1]['content'] = intermediate_result
        else:
            history = [
                {
                    'role': 'user',
                    'content': intermediate_result
                }
            ]
        history[-1]['content'] = modelfile.before_response + history[-1]['content'] + modelfile.after_response

        generator = self.call_bot(
            api_base_url=api_base_url,
            api_key=api_key,
            bot_name=modelfile.output_bot,
            history=history
        )
        intermediate_result = ""
        async for chunk in generator:
            yield chunk

    async def abort(self):
        logger.debug("aborted")
        return "Aborted"

if __name__ == "__main__":
    executor = AgentExecutor()
    executor.run()