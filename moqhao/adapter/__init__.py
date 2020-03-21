from abc import ABC, abstractmethod
from Crypto.Cipher import DES
from requests_html import HTMLSession
import base64
import requests
from functools import lru_cache


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

    def _get(self):
        session = HTMLSession()
        r = session.get(self.url())
        return r.html

    @abstractmethod
    def _payload(self):
        pass

    @lru_cache(maxsize=None)
    def payload(self):
        try:
            return self._payload()
        except requests.exceptions.RequestException as e:
            return
        except requests.exceptions.ConnectionError as e:
            return

    def _bytes_to_skip(self):
        return 4

    def decrypt(self):
        payload = self.payload()
        if payload is None:
            return

        b = base64.urlsafe_b64decode(payload)
        des = DES.new(self.key, 2, self.key)
        decrypted = des.decrypt(b)
        return decrypted[: -self.bytes_to_skip]

    def find_c2(self):
        try:
            decrypted = self.decrypt()
            if decrypted is None:
                return

            return decrypted.decode("utf-8")
        except ValueError as e:
            return
