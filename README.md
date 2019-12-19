# funky_hao

## Install

```bash
git clone https://github.com/ninoseki/funky_hao
pip3 install -r requirements.txt
```

## MoqHao

- Features:
  - Extract a hidden from MoqHao
  - Extract 1st C2 destinations
  - Extract step stones to phishing websites

```bash
$ python3 moqhao/main.py --help
Usage: main.py [OPTIONS] PATH

Options:
  --extract-dex / --no-extract-dex
                                  Extract a hidden dex
  --help                          Show this message and exit.
```

```bash
$ python3 moqhao/main.py samples/foo.apk
{
    "1stC2destinations": [
        "https://www.blogger.com/profile/foo",
        "https://www.blogger.com/profile/bar",
    ],
    "meta": {
        "dex": "hidden dex is extracted as samples/foo.dex"
    },
    "phishingStepStones": [
        "https://www.pinterest.com/foo/",
        "https://www.pinterest.com/bar/",
    ]
}
```
