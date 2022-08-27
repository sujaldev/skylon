<h1 align=center>
  <img alt="Skylon Logo" src="https://github.com/sujaldev/skylon/raw/main/docs/images/logo.svg?raw=true" width=300><br>
  SKYLON<br>
  <img alt="Badge" src="https://github.com/sujaldev/skylon/raw/main/docs/images/badge.svg?raw=true">
</h1>

This is my attempt at making a browser, which started with different motives but
now this is just a toy browser.

### Supported Engines:

| Engine Name | Remarks                          |
|-------------|----------------------------------|
| Chromium    | To support, well, the entire web |
| Skylon      | The toy engine I built           |

To embed chromium [cefpython](https://github.com/cztomczak/cefpython) was used.

Since this is a school project and implementing data storage either via mysql or
pickle was a requirement, I have implemented a small user data section so that
it can store your engine preference.

### DEMO

https://user-images.githubusercontent.com/75830554/187023050-c800f03d-5202-478e-8db5-9a0eabfa48e1.mp4

### CONTRIBUTE

To contribute to the skylon engine itself, create a pull request for the
[core](https://github.com/sujaldev/skylon/tree/core) branch.

### HOW TO RUN?

```shell
git clone https://github.com/sujaldev/skylon
cd skylon
# my aws free tier ended, the main branch relies on a database and so will not work
# I have pushed a temporary fix for this on the server-down branch
# switch to it by running git checkout server-down
pip install -r requirements.txt
cd src
export PYTHONPATH='../:./skylon'  # or you can use the full path like '/path/to/cloned/directory:/path/to/cloned/directory/src/skylon'
python main.py
```

NOTE: As of now the latest python version supported by cefpython3
is [3.7](https://github.com/cztomczak/cefpython#latest-release), so you will need to install python 3.7 and if you are
using virtualenv you can specify it as below:

```shell
virtualenv --python=python3.7 dest
```

### SUPPORTED PLATFORMS

_NOTE: This project has cross-platform support but requires a bit of tweaking to
support platforms other than linux_

- [x] Linux
- [x] Windows (refer to [#3](https://github.com/sujaldev/skylon/issues/3))
- [ ] Mac (requires minor changes)

### Other linked repositories

- [skylon-core](https://github.com/sujaldev/skylon-core) <br>
  This repository contained the skylon engine, but now it <br>
  has shifted to the core branch of this repository itself<br> <br>
- [skylon-legacy](https://github.com/sujaldev/skylon-legacy) <br>
  This was my first attempt at creating a browser, <br>
  only to realise I am currently one stupid developer.
