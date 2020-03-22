from . import BaseAdapter
import requests


class Pinterest(BaseAdapter):
    def _base_url(self):
        return "https://www.pinterest.com"

    async def _payload(self):
        html = await self._get()
        metas = html.find("meta")
        abouts = [
            meta for meta in metas if meta.attrs.get("property") == "pinterestapp:about"
        ]
        if len(abouts) == 0:
            return

        about = abouts[0]
        return about.attrs.get("content")

    async def find_c2(self):
        return await self.payload()
