import pytest

from rtv.clipboard import copy_linux, copy_osx
from rtv.exceptions import ProgramError

from unittest import mock


def test_copy_no_clipboard_tool():
    with mock.patch('subprocess.Popen'), \
            mock.patch('subprocess.call', return_value=1):
        with pytest.raises(ProgramError):
            copy_linux('test')


def test_copy_wayland():
    """wl-copy is selected when it is the first tool found."""
    p = mock.Mock()
    p.communicate = mock.Mock()

    def which_side_effect(args, **_):
        return 0 if args[1] == 'wl-copy' else 1

    with mock.patch('subprocess.Popen', return_value=p) as Popen, \
            mock.patch('subprocess.call', side_effect=which_side_effect):
        copy_linux('test')
        assert Popen.call_args[0][0] == ['wl-copy']
        p.communicate.assert_called_with(input='test'.encode('utf-8'))
        copy_linux('test ❤')
        p.communicate.assert_called_with(input='test ❤'.encode('utf-8'))


def test_copy_xsel():
    """xsel is selected when wl-copy is absent."""
    p = mock.Mock()
    p.communicate = mock.Mock()

    def which_side_effect(args, **_):
        return 0 if args[1] == 'xsel' else 1

    with mock.patch('subprocess.Popen', return_value=p) as Popen, \
            mock.patch('subprocess.call', side_effect=which_side_effect):
        copy_linux('test')
        assert Popen.call_args[0][0] == ['xsel', '-b', '-i']
        p.communicate.assert_called_with(input='test'.encode('utf-8'))


def test_copy_osx():
    p = mock.Mock()
    p.communicate = mock.Mock()

    with mock.patch('subprocess.Popen', return_value=p) as Popen:
        copy_osx('test')
        assert Popen.call_args[0][0] == ['pbcopy', 'w']
        p.communicate.assert_called_with(input='test'.encode('utf-8'))
        copy_osx('test ❤')
        p.communicate.assert_called_with(input='test ❤'.encode('utf-8'))
