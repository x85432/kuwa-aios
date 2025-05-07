import os
import logging
import argparse
import asyncio
from kuwa.client import KuwaClient
from kuwa.client.base import StopAsyncGenerator

logger = logging.getLogger(__name__)

class TestKuwaApi:

    def __init__(self, base_url, api_key, model):
        logger.info(f"Base URL: {base_url}")
        logger.info(f"API Key: {api_key[:5]}...")
        self.client = KuwaClient(
            base_url=base_url,
            model=model,
            auth_token=api_key,
        )

    async def test_chat_complete(self, stream):
        logger.info(f"*** test_chat_complete, stream={stream}")
        generator = self.client.chat_complete(
            messages=[
                {'role': 'user', 'content': 'Hello!'}
            ],
            streaming=stream
        )
        async for chunk in generator:
            logger.info(chunk)
        logger.info("****************")

    async def test_chat_complete_with_exit_code(self, stream):
        logger.info(f"*** test_chat_complete_with_exit_code, stream={stream}")
        generator = self.client.chat_complete_with_exit_code(
            messages=[
                {'role': 'user', 'content': 'Hello!'}
            ],
            streaming=stream
        )
        try:
            async for chunk in generator:
                logger.info(chunk)
        except StopAsyncGenerator as e:
            logger.info(f"Return code: {e.value}")
        
        logger.info("****************")
    
async def main():
    parser = argparse.ArgumentParser(
        description="Test the Kuwa API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--base-url", default=os.environ.get('KUWA_API_BASE_URL', 'http://localhost/v1.0/'), help="The custom base URL for the Kuwa API.")
    parser.add_argument("--api-key", default=os.environ.get('KUWA_API_KEY'), help="The API token for authentication with Kuwa.")
    parser.add_argument("--model", default=".tool/kuwa/copycat", help="The custom base URL for the Kuwa API.")
    parser.add_argument("--log", type=str, default="INFO", help="the log level. (INFO, DEBUG, ...)")
    args = parser.parse_args()

    # Setup logger
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {args.log}')
    logging.basicConfig(level=numeric_level)
    
    api_client = TestKuwaApi(
        base_url = args.base_url,
        api_key = args.api_key,
        model = args.model
    )
    await api_client.test_chat_complete(stream=False)
    await api_client.test_chat_complete(stream=True)
    await api_client.test_chat_complete_with_exit_code(stream=False)
    await api_client.test_chat_complete_with_exit_code(stream=True)

if __name__ == '__main__':
    asyncio.run(main())