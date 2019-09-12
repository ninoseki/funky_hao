# funky_hao

## Install

```bash
git clone https://github.com/ninoseki/funky_hao
pip3 install -r requirements.txt
```

## MoqHao

- Features:
  - Extract payload(dex) from an APK file
  - Extract 1st C2 destinations from payload

```bash
$ python3 moqhao/main.py --help
Usage: main.py [OPTIONS] PATH

Options:
  --extract-payload / --no-extract-payload
                                  Extract and save pyaload as a dex
  --help                          Show this message and exit.
```

```bash
$ python3 moqhao/main.py samples/65f222e6fb45b64ee6d09195cbc0d050b37762444b00127fdf3a3c6946bae686
{
    "1stC2destinations": [
        "https://m.youtube.com/channel/REDACTED/about",
        "https://www.instagram.com/REDACTED",
        "https://docs.google.com/document/d/REDACTED/mobilebasic"
    ],
    "payload": "Payload is extracted as samples/65f222e6fb45b64ee6d09195cbc0d050b37762444b00127fdf3a3c6946bae686.dex"
}
```
