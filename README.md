# funky_hao

## Requirements

- Python 3.7+
- poetry

## Install

```bash
git clone https://github.com/ninoseki/funky_hao
poetry install
```

## MoqHao

- Features:
  - Extract a hidden dex
  - Extract C2 destinations
  - Extract phishing websites

```bash
$ python moqhao/main.py --help
Usage: main.py [OPTIONS] PATH

Options:
  --extract-dex / --no-extract-dex
                                  Extract a hidden dex
  --help                          Show this message and exit.
```

```bash
python moqhao/main.py samples/foo.apk
```
