import asyncio
import json
import logging
import random
import typing

from contextlib import asynccontextmanager
from functools import lru_cache

from aiohttp import WSMsgType, ClientSession

from gosu_parlai_client.utils import load_file


logger = logging.getLogger(__name__)


class ParlAiException(Exception):
    pass


class ParlAiInvalidMessage(ParlAiException):
    pass


class ParlAiConnectionClosed(ParlAiException):
    pass


class ParlAiClient:
    MAX_RETRIES = 3
    RECEIVE_TIMEOUT = 30

    def __init__(self, parlai_host: str, session: ClientSession):
        self.parlai_host = parlai_host
        self.session = session
        self.history = []
        self.ws = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self.ws:
            await self.ws.close()
            self.ws = None

    async def connect(self):
        self.ws = await self.session._ws_connect(self.parlai_host, receive_timeout=self.RECEIVE_TIMEOUT)

    async def set_random_persona(self) -> str:
        return await self.set_personas(random.choice(load_bst_persona_lists()))

    async def set_personas(self, persona_list: typing.List[str]) -> str:
        texts = [f'your persona: {persona}' for persona in persona_list]
        return await self.ask('\n'.join(texts))

    async def _ask(self, text: str) -> str:
        await self.ws.send_str(json.dumps(dict(text=text), ensure_ascii=False))
        msg = await self.ws.receive()
        if msg.type is WSMsgType.TEXT:
            return json.loads(msg.data)['text']
        elif msg.type is WSMsgType.CLOSED:
            raise ParlAiConnectionClosed
        else:
            raise ParlAiInvalidMessage(f"Unexpected websocket message received from ParlAI webserver: {msg}")

    async def ask(self, text: str) -> str:
        """
        text can be multiline string to simulate multiple observes
        """
        self.history.append(text)
        for retry in range(self.MAX_RETRIES):
            try:
                if not self.ws:
                    await self.connect()
                    response = await self._ask('\n'.join(self.history))
                else:
                    response = await self._ask(text)

                self.history.append(response)
                return response
            except Exception as e:
                if retry >= self.MAX_RETRIES - 1:
                    raise
                else:
                    logger.debug(f'Error while asking ParlAI server response: {e}, retrying')
                    await self.close()


@asynccontextmanager
async def create_parlai_client(host: str) -> ParlAiClient:
    async with ClientSession() as session:
        async with ParlAiClient(parlai_host=host, session=session) as client:
            yield client


@lru_cache
def load_bst_persona_lists() -> typing.List[typing.List[str]]:
    """
    http://parl.ai/downloads/blended_skill_talk/personas_list.txt
    """
    return [
        [persona.replace('your persona: ', '') for persona in personas.split('\n') if persona]
        for personas in load_file('personas_list.txt').split('||')
    ]
