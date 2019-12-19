from androguard.core.bytecodes import dvm
from androguard.core.bytecodes.apk import APK
from typing import List
import base64
import click
import re
import sys
import json
import zlib


BYTES_TO_SKIP = 4


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


def find_hidden_dex(apk: APK):
    files = apk.get_files()
    hidden_dex_names = [x for x in files if re.match(
        r"assets/[a-z0-9]+/[a-z0-9]+", x)]
    if len(hidden_dex_names) == 1:
        hidden_dex_name = hidden_dex_names[0]
        data = apk.get_file(hidden_dex_name)
        return decrypt_dex(data)

    return None


def find_first_c2_accounts(strings: List[str]):
    accounts = [x for x in strings if re.match(r"^[a-z]+\|.+", x)]
    if len(accounts) != 1:
        return []

    urls = []
    for account in accounts[0].split("|")[1:]:
        name, provider = account.split("@")
        if provider == "youtube":
            urls.append("https://m.youtube.com/channel/{}/about".format(name))
        elif provider == "ins":
            urls.append("https://www.instagram.com/{}/".format(name))
        elif provider == "GoogleDoc" or provider == "GoogleDoc2":
            urls.append(
                "https://docs.google.com/document/d/{}/mobilebasic".format(name))
        elif provider == "vk":
            urls.append("https://m.vk.com/{}?act=info".format(name))
        elif provider == "blogger":
            urls.append("https://www.blogger.com/profile/{}".format(name))

    return urls


def find_phishing_step_stones(strings: List[str]):
    accounts = [x for x in strings if re.match(
        r"https:\/\/www\.pinterest\.com/[a-z0-9]+\/", x)]
    return accounts


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
    meta = {}

    if extract_dex:
        filename = "{}.dex".format(path)
        with open(filename, "wb") as fp:
            fp.write(dex.get_buff())
            meta["dex"] = "hidden dex is extracted as {}".format(filename)

    strings = dex.get_strings()
    output["1stC2destinations"] = find_first_c2_accounts(strings)
    output["phishingStepStones"] = find_phishing_step_stones(strings)
    output["meta"] = meta
    print(json.dumps(output, sort_keys=True, indent=4))


if __name__ == '__main__':
    main()
