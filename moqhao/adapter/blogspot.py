from . import BaseAdapter

import requests


class Blogspot(BaseAdapter):
    def _base_url(self):
        return ""

    def url(self):
        # https://{}.blogspot.com/?m=1
        return "https://{}.blogspot.com/?m=1".format(self.id)

    def _payload(self):
        html = self._get()
        selector = "#Profile1 > div > div > div > dl > dt > a"
        profile = html.find(selector, first=True)
        if profile is None:
            return
        else:
            return profile.text

