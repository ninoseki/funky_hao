from androguard.core.bytecodes import dvm
from androguard.core.bytecodes.apk import APK
from typing import List
import base64
import click
import json
import re
import os
import sys
import zlib

BYTES_TO_SKIP = 4
KEY = b"Ab5d1Q32"


def parse_apk(path):
    try:
        apk = APK(path)
        return apk
    except:
        return None


def decrypt_dex(data):
    # credit: https://securelist.com/roaming-mantis-part-iv/90332/
    try:
        decompressed = zlib.decompress((data[BYTES_TO_SKIP:]))
        b64decoded = base64.b64decode(decompressed)
        return dvm.DalvikVMFormat(b64decoded)
    except:
        return None


def decrypt_dex_b(data):
    try:
        first_byte = data[BYTES_TO_SKIP]
        byte_array = []
        for idx in range(BYTES_TO_SKIP + 1, len(data)):
            byte_array.append(data[idx] ^ first_byte)
        decompressed = zlib.decompress(bytes(byte_array))
        b64decoded = base64.b64decode(decompressed)
        return dvm.DalvikVMFormat(b64decoded)
    except:
        return None


def find_hidden_dex(apk: APK):
    files = apk.get_files()
    hidden_dex_names = [x for x in files if re.match(
        r"assets/[a-z0-9]+/[a-z0-9]+", x)]
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


def find_c2(strings: List[str]):
    accounts = [x for x in strings if re.match(r"^[a-z0-9]+\|.+", x)]
    if len(accounts) != 1:
        return []

    c2 = {}
    for account in accounts[0].split("|")[1:]:
        id, provider = account.split("@")
        adapter = build_adapter(id, provider)
        if adapter is None:
            continue

        _c2 = adapter.find_c2()
        if _c2 is None:
            c2[adapter.url()] = {
                "payload": adapter.payload(),
                "error": "failed to analyze it",
            }
        else:
            c2[adapter.url()] = {
                "payload": adapter.payload(),
                "destination": _c2
            }

    return c2


def find_phishing(strings: List[str]):
    accounts = [x for x in strings if re.match(
        r"https:\/\/www\.pinterest\.com/[a-z0-9]+\/", x)]

    phishing = {}
    for account in accounts:
        id = account.split("/")[-2]
        adapter = build_adapter(id, "pinterest")
        if adapter is None:
            continue

        phishing[adapter.url()] = adapter.find_c2()

    return phishing


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--extract-dex/--no-extract-dex", default=True, help="Extract a hidden dex")
def main(path, extract_dex):
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

    strings = dex.get_strings()
    output["c2"] = find_c2(strings)
    output["phishing"] = find_phishing(strings)
    print(json.dumps(output, sort_keys=True, indent=4))


if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

    from moqhao.adapter.blogger import Blogger
    from moqhao.adapter.blogspot import Blogspot
    from moqhao.adapter.google import Google
    from moqhao.adapter.instagram import Instagram
    from moqhao.adapter.pinterest import Pinterest
    from moqhao.adapter.vk import VK
    from moqhao.adapter.youtube import YouTube

    main()
