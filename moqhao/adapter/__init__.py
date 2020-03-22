from abc import ABC, abstractmethod
from Crypto.Cipher import DES
from functools import lru_cache
from httpx import HTTPError
from requests_html import HTML
import base64
import httpx


class BaseAdapter(ABC):
    def __init__(self, id: str):
        self.id = id
        self.bytes_to_skip = 4
        self.key = b"Ab5d1Q32"

    @abstractmethod
    def _base_url(self):
        pass

    def url(self):
        return "{}/{}".format(self._base_url(), self.id)

    async def _get(self) -> HTML:
        client = httpx.AsyncClient()
        r = await client.get(self.url())
        return HTML(html=r.text)

    @abstractmethod
    def _payload(self):
        pass

    async def payload(self):
        try:
            return await self._payload()
        except HTTPError:
            pass

        return None

    def _bytes_to_skip(self):
        return 4

    async def decrypt(self):
        payload = await self.payload()
        if payload is None:
            return None

        b = base64.urlsafe_b64decode(payload)
        des = DES.new(self.key, 2, self.key)
        decrypted = des.decrypt(b)
        return decrypted[: -self.bytes_to_skip]

    async def find_c2(self):
        try:
            decrypted = await self.decrypt()
            if decrypted is None:
                return

            return decrypted.decode("utf-8")
        except ValueError:
            pass

        return None
