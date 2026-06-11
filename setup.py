"""
Shim for metadata that PEP 621 pyproject.toml does not support.

All project metadata lives in pyproject.toml; only the man page
data_files entry remains here.
"""
import setuptools

setuptools.setup(
    data_files=[("share/man/man1", ["rtv.1"])],
)
