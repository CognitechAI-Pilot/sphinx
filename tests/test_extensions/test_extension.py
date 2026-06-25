"""Test sphinx.extension module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from sphinx.errors import VersionRequirementError
from sphinx.extension import Extension, verify_needs_extensions

if TYPE_CHECKING:
    from sphinx.testing.util import SphinxTestApp


@pytest.mark.sphinx('html', testroot='root')
def test_needs_extensions(app: SphinxTestApp) -> None:
    # empty needs_extensions
    assert app.config.needs_extensions == {}
    verify_needs_extensions(app, app.config)

    # needs_extensions fulfilled
    app.config.needs_extensions = {'test.extension': '3.9'}
    app.extensions['test.extension'] = Extension(
        'test.extension', 'test.extension', version='3.10'
    )
    verify_needs_extensions(app, app.config)

    # needs_extensions not fulfilled
    app.config.needs_extensions = {'test.extension': '3.11'}
    app.extensions['test.extension'] = Extension(
        'test.extension', 'test.extension', version='3.10'
    )
    with pytest.raises(VersionRequirementError):
        verify_needs_extensions(app, app.config)


def test_extension_default_attributes() -> None:
    """Test Extension stores name, module, and sets defaults for optional attrs."""
    ext = Extension('myext', object)
    assert ext.name == 'myext'
    assert ext.module is object
    assert ext.version == 'unknown version'
    assert ext.parallel_read_safe is None
    assert ext.parallel_write_safe is True


def test_extension_custom_attributes() -> None:
    """Test Extension stores custom version and parallel safety flags."""
    ext = Extension(
        'myext',
        object,
        version='1.2.3',
        parallel_read_safe=True,
        parallel_write_safe=False,
    )
    assert ext.version == '1.2.3'
    assert ext.parallel_read_safe is True
    assert ext.parallel_write_safe is False


def test_needs_extensions_none_config() -> None:
    """Test verify_needs_extensions returns early when needs_extensions is None."""
    app = MagicMock()
    config = MagicMock()
    config.needs_extensions = None
    # Should not raise or access app.extensions
    verify_needs_extensions(app, config)
    app.extensions.get.assert_not_called()


@pytest.mark.sphinx('html', testroot='root')
def test_needs_extensions_missing_extension(app: SphinxTestApp) -> None:
    """Test verify_needs_extensions warns when a required extension is not loaded."""
    app.config.needs_extensions = {'missing.extension': '1.0'}
    # Remove the extension if it happens to be present
    app.extensions.pop('missing.extension', None)
    # Should log a warning but not raise
    verify_needs_extensions(app, app.config)
    assert 'missing.extension' in app._warning.getvalue()


@pytest.mark.sphinx('html', testroot='root')
def test_needs_extensions_unknown_version(app: SphinxTestApp) -> None:
    """Test verify_needs_extensions raises when extension version is 'unknown version'."""
    app.config.needs_extensions = {'test.extension': '1.0'}
    app.extensions['test.extension'] = Extension('test.extension', 'test.extension')
    with pytest.raises(VersionRequirementError):
        verify_needs_extensions(app, app.config)


@pytest.mark.sphinx('html', testroot='root')
def test_needs_extensions_invalid_version_string(app: SphinxTestApp) -> None:
    """Test verify_needs_extensions falls back to string comparison on InvalidVersion."""
    app.config.needs_extensions = {'test.extension': 'beta'}
    app.extensions['test.extension'] = Extension(
        'test.extension', 'test.extension', version='alpha'
    )
    # 'beta' > 'alpha' lexicographically, so requirement is not fulfilled
    with pytest.raises(VersionRequirementError):
        verify_needs_extensions(app, app.config)


@pytest.mark.sphinx('html', testroot='root')
def test_needs_extensions_invalid_version_string_fulfilled(app: SphinxTestApp) -> None:
    """Test verify_needs_extensions with invalid version strings that are satisfied."""
    app.config.needs_extensions = {'test.extension': 'alpha'}
    app.extensions['test.extension'] = Extension(
        'test.extension', 'test.extension', version='beta'
    )
    # 'alpha' < 'beta' lexicographically, so requirement is fulfilled
    verify_needs_extensions(app, app.config)
