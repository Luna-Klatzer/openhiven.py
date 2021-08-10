![openhiven.py](https://socialify.git.ci/Luna-Klatzer/openhiven.py/image?description=1&font=Source%20Code%20Pro&forks=1&issues=1&language=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2FLuna-Klatzer%2Fdocs_openhiven.py%2Fmain%2Fdocs%2Fassets%2Fimages%2Fopenhivenpy.png&owner=1&pattern=Floating%20Cogs&pulls=1&stargazers=1&theme=Light)

# [Content](#content)

- [The Hiven API-Wrapper](#the-hiven-api-wrapper-openhivenpy)
    - [Dependencies](#dependencies)
    - [Installation](#installation)
        - [Install (PyPi Release)](#install-pypi-release)
        - [Install (PyPi Specific Version)](#install-pypi-specific-version)
        - [Install (Github Build)](#install-github-build)
    - [Documentation](#documentation)
        - [Usage Example (v0.1.3.2)](#usage-example-v0132)
    - [Contributors](#contributors)
    - [Copyright and License](#copyright-and-license)

# The Hiven API-Wrapper `openhiven.py`

<p align="center">

[![Package Version](https://img.shields.io/badge/package%20version-v0.1.3.2-purple?logo=python)](https://github.com/Luna-Klatzer/openhiven.py)
[![Python Version](https://img.shields.io/badge/python->=3.7-blue?logo=python)](https://python.org)
![Build](https://img.shields.io/github/workflow/status/Luna-Klatzer/openhiven.py/CodeQL?logo=github)
![Lines of Code](https://img.shields.io/tokei/lines/github/Luna-Klatzer/openhiven.py)
[![License](https://img.shields.io/github/license/Luna-Klatzer/openhiven.py)](https://github.com/Luna-Klatzer/openhiven.py/blob/main/LICENSE)
![Coverage](./pytest/coverage.svg)
[![codecov](https://codecov.io/gh/Luna-Klatzer/openhiven.py/branch/main/graph/badge.svg?token=36ADSJZ6F3)](https://codecov.io/gh/Luna-Klatzer/openhiven.py)

</p>

## Dependencies

[![aiohttp](https://img.shields.io/github/pipenv/locked/dependency-version/Luna-Klatzer/openhiven.py/aiohttp/main)](https://docs.aiohttp.org/en/stable/)
[![asyncio](https://img.shields.io/github/pipenv/locked/dependency-version/Luna-Klatzer/openhiven.py/asyncio/main)](https://docs.python.org/3/library/asyncio.html)
[![typing](https://img.shields.io/github/pipenv/locked/dependency-version/Luna-Klatzer/openhiven.py/typing/main)](https://docs.python.org/3/library/typing.html)

## Installation
### Install (PyPi Release)

```bash
python3 -m pip install -U openhivenpy
```

### Install (PyPi Specific Version)

```bash
python3 -m pip install -U openhivenpy==version
```

### Install (Github Build)
```bash
python3 -m pip install -U https://github.com/Luna-Klatzer/openhiven.py/archive/main.zip
```

## Documentation

For full documentation visit the documentation our github pages build
[here](https://Luna-Klatzer.github.io/docs_openhiven.py/)


### Usage Example (v0.1.3.2)

**A simple UserClient Bot for quick usage:**

```python

import openhivenpy as hiven

client = hiven.UserClient()

@client.event()
async def on_ready():
    print("Bot is ready")

client.run("Insert token")

```

**A simple CommandListener for reacting to commands:**

```python 

import openhivenpy as hiven

client = hiven.UserClient()

@client.event()
async def on_ready():
    print("Bot is ready")

@client.event()
async def on_message_create(msg):
    if msg.content.startswith("-"):
        if msg.content == "-ping":
            return await msg.room.send("pong")

client.run("Insert token")
 
```

**Inherited HivenClient Example:**

```python 

import openhivenpy as hiven

class Bot(hiven.UserClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print("Bot is ready!")

if __name__ == '__main__':
    client = Bot()
    client.run("Insert token")

```

## Contributors

<a href="https://github.com/Nicolas-Klatzer/openhiven.py/graphs/contributors"><image src="https://contributors-img.web.app/image?repo=Nicolas-Klatzer/openhiven.py"></a>

## Copyright and License

![License](https://img.shields.io/github/license/Luna-Klatzer/openhiven.py?color=cyan)

Copyright (c) 2021, Nicolas
Klatzer[*](#legal-name-which-does-not-match-the-preferred-and-commonly-used-name-luna-klatzer)
. All rights reserved.

See the [LICENSE](./LICENSE) for information on terms & conditions for usage

###### *Legal name, which does not match the preferred and commonly used name Luna Klatzer
