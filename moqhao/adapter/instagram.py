import httpx

from . import BaseAdapter


class Instagram(BaseAdapter):
    def _base_url(self):
        return "https://www.instagram.com"

    def url(self):
        # https://www.instagram.com/{}/?__a=1
        return "{}/{}/?__a=1".format(self._base_url(), self.id)

    async def _get(self):
        client = httpx.AsyncClient()
        r = await client.get(self.url())
        return r.json()

    async def _payload(self):
        json = await self._get()
        return json.get("graphql", {}).get("user", {}).get("biography")
