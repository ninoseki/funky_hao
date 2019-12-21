from . import BaseAdapter

import requests


class Instagram(BaseAdapter):
    def _base_url(self):
        return "https://www.instagram.com"

    def url(self):
        # https://www.instagram.com/{}/?__a=1
        return "{}/{}/?__a=1".format(self._base_url(), self.id)

    def _get(self):
        return requests.get(self.url()).json()

    def _payload(self):
        json = self._get()
        return json.get("graphql", {}).get("user", {}).get("biography")
