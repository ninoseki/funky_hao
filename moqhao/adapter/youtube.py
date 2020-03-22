from . import BaseAdapter


class YouTube(BaseAdapter):
    def _base_url(self):
        return "https://m.youtube.com/channel"

    def url(self):
        # "https://m.youtube.com/channel/{}/about"
        return "{}/{}/about".format(self._base_url(), self.id)

    async def _payload(self):
        html = await self._get()
        metas = html.find("meta")
        descs = [
            meta for meta in metas if meta.attrs.get("property") == "og:description"
        ]
        if len(descs) == 0:
            return

        descrption = descs[0]
        return descrption.attrs.get("content")
