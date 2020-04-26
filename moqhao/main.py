import base64
import functools
import json
import os
import re
import sys
import zlib
from typing import List

import aiometer
import asyncclick as click
from androguard.core.bytecodes import dvm
from androguard.core.bytecodes.apk import APK
from loguru import logger

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))  # noqa # isort:skip

from moqhao.adapter.blogger import Blogger  # noqa # isort:skip
from moqhao.adapter.blogspot import Blogspot  # noqa # isort:skip
from moqhao.adapter.google import Google  # noqa # isort:skip
from moqhao.adapter.instagram import Instagram  # noqa # isort:skip
from moqhao.adapter.pinterest import Pinterest  # noqa # isort:skip
from moqhao.adapter.vk import VK  # noqa # isort:skip
from moqhao.adapter.youtube import YouTube  # noqa # isort:skip


BYTES_TO_SKIP = 4
KEY = b"Ab5d1Q32"


def parse_apk(path):
    try:
        apk = APK(path)
        return apk
    except Exception:
        return None


def decrypt_dex(data):
    # credit: https://securelist.com/roaming-mantis-part-iv/90332/
    try:
        decompressed = zlib.decompress((data[BYTES_TO_SKIP:]))
        b64decoded = base64.b64decode(decompressed)
        vm = dvm.DalvikVMFormat(b64decoded)
        logger.debug("Decrypted as type A")
        return vm
    except Exception:
        logger.debug("Failed to decrypt as type A")
        return None


def decrypt_dex_b(data):
    try:
        first_byte = data[BYTES_TO_SKIP]
        byte_array = []
        for idx in range(BYTES_TO_SKIP + 1, len(data)):
            byte_array.append(data[idx] ^ first_byte)
        decompressed = zlib.decompress(bytes(byte_array))
        b64decoded = base64.b64decode(decompressed)
        vm = dvm.DalvikVMFormat(b64decoded)
        logger.debug("Decrypted as type B")
        return vm
    except Exception:
        logger.debug("Failed to decrypt as type B")
        return None


def find_hidden_dex(apk: APK):
    files = apk.get_files()
    hidden_dex_names = [x for x in files if re.match(r"assets/[a-z0-9]+/[a-z0-9]+", x)]
    if len(hidden_dex_names) == 1:
        hidden_dex_name = hidden_dex_names[0]
        data = apk.get_file(hidden_dex_name)
        dex = decrypt_dex(data)
        if dex is not None:
            return dex
        return decrypt_dex_b(data)

    return None


def build_adapter(id: str, provider: str):
    if provider == "youtube":
        return YouTube(id)
    elif provider == "ins":
        return Instagram(id)
    elif provider == "GoogleDoc":
        return Google(id)
    elif provider == "GoogleDoc2":
        return Google(id)
    elif provider == "blogger":
        return Blogger(id)
    elif provider == "vk":
        return VK(id)
    elif provider == "blogspot":
        return Blogspot(id)
    elif provider == "pinterest":
        return Pinterest(id)
    else:
        return


def list_to_dict(items):
    memo = {}
    for item in items:
        for key in item.keys():
            memo[key] = item[key]
    return memo


async def find_c2(strings: List[str]):
    accounts = [x for x in strings if re.match(r"^[a-z0-9]+\|.+", x)]
    if len(accounts) != 1:
        return []

    adapters = []
    for account in accounts[0].split("|")[1:]:
        logger.debug(f"1st C2 = {account}")

        id, provider = account.split("@")
        adapter = build_adapter(id, provider)
        if adapter is None:
            continue
        adapters.append(adapter)

    async def run_adapter(adapter):
        _c2 = await adapter.find_c2()
        if _c2 is None:
            return {
                adapter.url(): {
                    "payload": await adapter.payload(),
                    "error": "failed to analyze it",
                }
            }
        else:
            return {
                adapter.url(): {"payload": await adapter.payload(), "destination": _c2}
            }

    jobs = [functools.partial(run_adapter, adapter) for adapter in adapters]
    results = await aiometer.run_all(jobs, max_at_once=10)
    return list_to_dict(results)


async def find_phishing(strings: List[str]):
    accounts = [
        x for x in strings if re.match(r"https:\/\/www\.pinterest\.com/[a-z0-9]+\/", x)
    ]

    adapters = []
    for account in accounts:
        id = account.split("/")[-2]
        adapter = build_adapter(id, "pinterest")
        if adapter is None:
            continue
        adapters.append(adapter)

    async def run_adapter(adapter):
        return {adapter.url(): await adapter.find_c2()}

    jobs = [functools.partial(run_adapter, adapter) for adapter in adapters]
    results = await aiometer.run_all(jobs, max_at_once=10)
    return list_to_dict(results)


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--extract-dex/--no-extract-dex", default=True, help="Extract a hidden dex"
)
async def main(path, extract_dex):
    apk = parse_apk(path)
    if apk is None:
        print("Invalid apk is given")
        sys.exit(1)

    dex = find_hidden_dex(apk)
    if dex is None:
        print("Failed to parse dex")
        sys.exit(1)

    output = {}

    if extract_dex:
        filename = "{}.dex".format(path)
        with open(filename, "wb") as fp:
            fp.write(dex.get_buff())
            output["dex"] = "hidden dex is extracted as {}".format(filename)

    strings = [string.decode() for string in dex.get_strings()]
    output["c2"] = await find_c2(strings)
    output["phishing"] = await find_phishing(strings)
    print(json.dumps(output, sort_keys=True, indent=4))


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
