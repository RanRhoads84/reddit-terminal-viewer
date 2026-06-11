# Installing RTV

## Requirements

- **Python 3.10 or newer** (tested through 3.14)
- **pip** (bundled with Python 3.4+)
- Linux or macOS — Windows is not supported

### System packages (Linux)

Clipboard support requires a clipboard tool. Install the one that matches your
display server — RTV probes for them in this order: `wl-copy`, `xsel`, `xclip`.

```bash
# Wayland (modern default on most distros)
sudo apt install wl-clipboard          # Debian / Ubuntu
sudo pacman -S wl-clipboard            # Arch
sudo dnf install wl-clipboard          # Fedora

# X11 / XWayland fallback
sudo apt install xsel                  # Debian / Ubuntu
sudo pacman -S xsel                    # Arch
sudo dnf install xsel                  # Fedora
```

macOS clipboard works out of the box via `pbcopy`.

---

## Install from source

```bash
git clone https://github.com/michael-lazar/rtv.git
cd rtv
pip install .
```

This installs the `rtv` command into your active Python environment. Use a virtual environment to keep it isolated:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
rtv --version
```

### Install to user site-packages (no root, no venv)

```bash
pip install --user .
```

Make sure `~/.local/bin` is on your `$PATH`.

---

## Development install

Install in editable mode with test dependencies:

```bash
git clone https://github.com/michael-lazar/rtv.git
cd rtv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

Run the app directly from the repo without installing:

```bash
python -m rtv
python -m rtv -s python       # open r/python on launch
python -m rtv <url>           # open a specific submission
```

---

## Running tests

```bash
# All tests against pre-recorded HTTP cassettes (no network required)
coverage run -m pytest -v

# Single test file
pytest tests/test_terminal.py -v

# Match tests by name pattern
pytest -k "test_subreddit" -v

# Coverage report
coverage report
```

Tests use [vcrpy](https://github.com/kevin1024/vcrpy) to replay recorded HTTP
responses from `tests/cassettes/`. No network access or Reddit credentials are
required for a normal test run.

### Re-recording cassettes

To record new cassettes against the live Reddit API you need a valid refresh
token from a logged-in session:

```bash
pytest --record-mode=once tests/test_subreddit.py
```

RTV saves your refresh token at `~/.local/share/rtv/refresh-token` after you
log in with the `u` key. The token is stripped from cassettes automatically on
save.

---

## First run and Reddit authentication

Reddit blocks unauthenticated API access from most networks (policy since
mid-2023). Browsing without logging in will show a "Forbidden" error on many
subreddits. To get full access:

1. Launch RTV: `rtv`
2. Press `u` to open the OAuth login flow — this opens a browser tab
3. Authorize the app; the browser redirects to `localhost:6500`
4. RTV stores the refresh token at `~/.local/share/rtv/refresh-token` and
   logs in automatically on subsequent launches

The OAuth flow uses Reddit's installed-app grant over `oauth.reddit.com`.
No client secret is required.

---

## Optional: copy default configs

```bash
# Config file → ~/.config/rtv/rtv.cfg
rtv --copy-config

# Mailcap template → ~/.mailcap  (for opening media with external programs)
rtv --copy-mailcap
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'kitchen'`** — you are running Python
from outside the virtual environment where RTV is installed. Activate the venv
or reinstall with `pip install .`.

**`ModuleNotFoundError: No module named 'mailcap'`** — Python 3.13+ removed
the `mailcap` stdlib module. Install the backport:

```bash
pip install standard-mailcap
```

This is listed as an automatic dependency for Python >= 3.13, so a clean
`pip install .` should handle it. If you installed manually from an older
`setup.py`-based tree, install the backport explicitly.

**Garbled unicode / `M-b~@M-"` characters** — run with `rtv --ascii`, or
ensure your terminal is configured for UTF-8 (`locale` should show
`LANG=en_US.UTF-8` or similar).

**`rtv: command not found` after `pip install --user .`** — add
`~/.local/bin` to your `PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
