from . import BaseAdapter

import requests


class Google(BaseAdapter):
    def __init__(self, id: str):
        super().__init__(id)
        self.bytes_to_skip = 5

    def _base_url(self):
        return "https://docs.google.com/document/d"

    def url(self):
        # https://docs.google.com/document/d/{}/mobilebasic
        return "{}/{}/mobilebasic".format(self._base_url(), self.id)

    def _payload(self):
        html = self._get()
        title = html.find("title", first=True).text
        return title.split("/")[0]

    def find_c2(self):
        id = self._payload()
        self.id = id
        return super().find_c2()
