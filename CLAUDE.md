# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install for development
pip install -e .[test]

# Run all tests
coverage run -m py.test -v

# Run a single test
pytest tests/test_subreddit.py::test_subreddit_refresh -v

# Run tests with a specific pattern
pytest -k "test_subreddit" -v

# Run linter (errors only)
pylint --rcfile .pylintrc -E rtv/

# Coverage report
coverage report

# Launch the app
python -m rtv
python -m rtv -s python          # open specific subreddit
python -m rtv <url>              # open specific submission
python -m rtv --copy-config      # copy default config to ~/.config/rtv/rtv.cfg

# Re-record VCR cassettes (requires real Reddit credentials + refresh token)
pytest --record-mode=once tests/test_subreddit.py
```

## Architecture

RTV is a curses-based TUI application. There are four major layers:

### 1. Pages (`page.py`, `*_page.py`)

`Page` is the base class for every screen. Each page owns:
- `self.content` — a `Content` subclass (the data model)
- `self.nav` — a `Navigator` (cursor position/scrolling)
- `self.controller` — a `Controller` that maps keypresses to methods

The `loop()` method in `Page` drives each screen: draw → wait for keypress → dispatch → handle any selected subpage. Pages return either themselves (continue looping) or a new page (navigate away). The entry point in `__init__.py:main()` launches `SubredditPage` and loops over whatever `page.loop()` returns.

Four concrete pages:
- `SubredditPage` — submission listing for a subreddit/search/user/domain
- `SubmissionPage` — a post and its comment tree
- `SubscriptionPage` — the user's subscribed subreddits
- `InboxPage` — the user's inbox messages

**Adding keybindings:** Use the `@Controller.register(*chars)` decorator on a page method. Methods that require an active OAuth session should also be decorated with `@logged_in` (defined in `page.py`), which shows a notification and short-circuits if the user is not authenticated.

### 2. Content (`content.py`)

`Content` subclasses wrap PRAW API objects and format them for display. They expose a `get(index, n_cols)` method the Navigator calls to fetch display-ready dicts. Key subclasses: `SubredditContent`, `SubmissionContent`, `SubscriptionContent`, `InboxContent`.

`RequestHeaderRateLimiter` is a PRAW handler subclass that injects Reddit API headers and respects rate-limit responses.

### 3. Terminal (`terminal.py`)

`Terminal` wraps `curses.stdscr` and provides all drawing primitives, input handling, subprocess launching (editor, pager, browser, mailcap), and the `LoadScreen` context manager for background HTTP requests. It is passed into every page and content class.

`clipboard.py` is a thin helper that delegates to `pbcopy` on macOS and `xsel`/`xclip` on Linux. Either `xsel` or `xclip` must be installed for clipboard support on Linux.

### 4. Config & Theme (`config.py`, `theme.py`)

`Config` is a dict-like object populated from CLI args and `~/.config/rtv/rtv.cfg`. It also manages persisted state: OAuth refresh token (`~/.local/share/rtv/refresh-token`) and browsing history (`~/.local/share/rtv/history.log`).

`Theme` loads color/attribute pairs from `.cfg` files in `rtv/themes/` or `~/.config/rtv/themes/` and registers them with curses. `ThemeList` wraps `Theme.list_themes()` to support F2/F3 cycling.

### Supporting modules

- `objects.py` — `Controller`/`Command` (keymap dispatch), `Navigator` (cursor math), `KeyMap`, `LoadScreen` (threaded spinner), `curses_session` context manager
- `oauth.py` — OAuth2 flow via a local HTTP server on port 6500
- `mime_parsers.py` — URL → MIME type resolution for mailcap media opening; each parser subclasses `BaseMIMEParser` and declares a `pattern` regex
- `docs.py` — all user-visible help strings (keybinding reference, usage text, user-agent string)
- `exceptions.py` — custom exception hierarchy

## Testing

Tests use **pytest** + **vcrpy** for HTTP fixture playback. Recorded cassettes live in `tests/cassettes/`. The `conftest.py` provides fixtures for `stdscr` (mocked curses), `reddit` (PRAW + VCR cassette), `terminal`, `config`, and pre-built page instances.

VCR cassettes are named after the pytest node name (e.g. `test_subreddit_refresh.yaml`). When a test is parametrized the cassette name includes the parameter (e.g. `test_content_subreddit_from_name[hot].yaml`).

By default tests run against pre-recorded cassettes (`--record-mode=none`). To re-record, pass `--record-mode=once` with a real refresh token at `~/.local/share/rtv/refresh-token`.

`MockStdscr` (in `conftest.py`) mimics `curses.stdscr`. Set `stdscr.nlines` and `stdscr.ncols` on the fixture to control the simulated terminal dimensions in a test.

## Python Version & Packaging

The codebase is Python 3.10+ only (tested through 3.14). Packaging lives in `pyproject.toml` (PEP 621, setuptools backend); `setup.py` is a shim that only carries the man-page `data_files` entry. The `mailcap` stdlib module was removed in Python 3.13 — the `standard-mailcap` backport is a conditional dependency for `python_version >= "3.13"`. Do not reintroduce `six`, `from __future__` imports, or `codecs.open`.

## Reddit API Notes

Reddit blocks unauthenticated API access (HTTP 403) from most networks since mid-2023. The OAuth2 installed-app flow (`oauth.reddit.com`, client id in `rtv/packages/praw/praw.ini`) is the supported path — users must log in (`u` key) for reliable usage. The token endpoints on both `api.reddit.com` and `www.reddit.com` remain functional.

## Test Cassette Compatibility

The VCR cassettes in `tests/cassettes/` were recorded with vcrpy 1.x and store raw gzip bodies. `DecompressSerializer` in `tests/conftest.py` inflates them at load time (urllib3 2.x no longer decompresses played-back responses). Keep using it when adding cassette-based tests.

## Bundled PRAW

RTV ships a pinned fork of PRAW 3 under `rtv/packages/praw/`. The `packages/__init__.py` stub falls back to a system PRAW 3 install if the bundled package is missing. Always use `from .packages import praw` rather than importing `praw` directly.
