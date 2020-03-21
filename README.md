# funky_hao

## Install

```bash
git clone https://github.com/ninoseki/funky_hao
pipenv install
```

## MoqHao

- Features:
  - Extract a hidden dex
  - Extract C2 destinations
  - Extract phishing websites

```bash
$ python3 moqhao/main.py --help
Usage: main.py [OPTIONS] PATH

Options:
  --extract-dex / --no-extract-dex
                                  Extract a hidden dex
  --help                          Show this message and exit.
```

```bash
python3 moqhao/main.py samples/foo.apk
```
