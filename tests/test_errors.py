from __future__ import annotations

from sphinx.errors import ExtensionError, PycodeError, SphinxParallelError


def test_extension_error_repr() -> None:
    exc = ExtensionError('foo')
    assert repr(exc) == "ExtensionError('foo')"


def test_extension_error_with_orig_exc_repr() -> None:
    exc = ExtensionError('foo', Exception('bar'))
    assert repr(exc) == "ExtensionError('foo', Exception('bar'))"


def test_extension_error_category_without_modname() -> None:
    """Test ExtensionError.category when modname is not set."""
    exc = ExtensionError('foo')
    assert exc.category == 'Extension error'


def test_extension_error_category_with_modname() -> None:
    """Test ExtensionError.category when modname is provided."""
    exc = ExtensionError('foo', modname='myext')
    assert exc.category == 'Extension error (myext)'


def test_extension_error_str_without_orig_exc() -> None:
    """Test ExtensionError.__str__ when orig_exc is not set."""
    exc = ExtensionError('foo')
    assert str(exc) == 'foo'


def test_extension_error_str_with_orig_exc() -> None:
    """Test ExtensionError.__str__ when orig_exc is set."""
    exc = ExtensionError('foo', Exception('bar'))
    assert str(exc) == 'foo (exception: bar)'


def test_sphinx_parallel_error_str() -> None:
    """Test SphinxParallelError stores message and traceback, and str returns message."""
    exc = SphinxParallelError('parallel failure', 'traceback text')
    assert exc.message == 'parallel failure'
    assert exc.traceback == 'traceback text'
    assert str(exc) == 'parallel failure'


def test_pycode_error_str_single_arg() -> None:
    """Test PycodeError.__str__ with a single argument."""
    exc = PycodeError('source error')
    assert str(exc) == 'source error'


def test_pycode_error_str_multiple_args() -> None:
    """Test PycodeError.__str__ with an additional exception argument."""
    inner = ValueError('inner problem')
    exc = PycodeError('source error', inner)
    assert str(exc) == "source error (exception was: ValueError('inner problem'))"
