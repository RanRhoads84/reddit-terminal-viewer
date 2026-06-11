----------------------
Contributor Guidelines
----------------------

Before you start
================

- Post an issue on the `tracker <https://github.com/michael-lazar/rtv/issues>`_ describing the bug or feature you would like to add
- If an issue already exists, leave a comment to let others know that you intend to work on it

Considerations
==============

- One of the project's goals is to maintain compatibility with as many terminal emulators as possible.
  Please be mindful of this when designing a new feature

  - Is it compatible with both Linux and macOS?
  - Requires Python 3.10 or newer
  - Will it work over SSH (without X11)?
  - What about terminals that don't support color? Or those with limited (8/256) colors?
  - Will it work in tmux/screen?
  - Will it fail gracefully if unicode is not supported?

- If you're adding a new feature, try to include a few test cases.
  See the section below on setting up your test environment
- If you tried, but you can't get the tests running in your environment, it's ok
- If you are unsure about anything, ask!

Submitting a pull request
=========================

- Reference the issue # that the pull request is related to
- Make sure you have merged in the latest changes from the ``master`` branch
- After you submit, make sure that the Travis-CI build passes
- Be prepared to have your code reviewed.
  For non-trivial additions, it's normal for this process to take a few iterations

Style guide
===========

- All code should follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_
- Try to keep lines under 80 characters, but don't sacrifice readability to do it!

  **Ugly**

  .. code-block:: python

              text = ''.join(
                  line for line in fp2 if not line.startswith('#'))

  **Better**

  .. code-block:: python

            text = ''.join(line for line in fp2 if not line.startswith('#'))

- Use the existing codebase as a reference when writing docstrings (adopted from the `Google Style Guide <https://google.github.io/styleguide/pyguide.html#Comments>`_)
- Do **not** add encoding headers (``# -*- coding: utf-8 -*-``) — Python 3 defaults to UTF-8
- **Please don't submit pull requests for style-only code changes**

Running the tests
=================

This project uses `pytest <http://pytest.org/>`_ and `VCR.py <https://vcrpy.readthedocs.org/>`_.

VCR records HTTP requests during the test run and stores them in *tests/cassettes* for subsequent runs.
This keeps tests fast and reproducible — no network access required.

1. Install the test dependencies (editable install recommended for development)

   .. code-block:: bash

      $ pip install -e ".[test]"

2. Run the tests using the pre-recorded cassettes

   .. code-block:: bash

      $ coverage run -m pytest -v
      # or for a specific file:
      $ pytest tests/test_terminal.py -v

3. By default the cassettes are read-only. To record new cassettes against the
   live Reddit API, you need a valid refresh token. Log in to RTV first (``u`` key),
   then the token is saved at ``~/.local/share/rtv/refresh-token``.

   .. code-block:: bash

      $ pytest --record-mode=once tests/test_subreddit.py

   Sensitive information is automatically stripped from cassettes when they are saved.

4. Commit any new cassette files alongside the new test case.
