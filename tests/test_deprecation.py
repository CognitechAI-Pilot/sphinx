"""Tests for sphinx.deprecation module."""

from __future__ import annotations

import pytest

from sphinx.deprecation import (
    RemovedInSphinx10Warning,
    RemovedInSphinx11Warning,
    _deprecation_warning,
)


def test_deprecation_warning_removed_in_sphinx10() -> None:
    """Test _deprecation_warning emits RemovedInSphinx10Warning for remove=(10, 0)."""
    with pytest.warns(
        RemovedInSphinx10Warning, match=r"'mymodule\.old_name' is deprecated"
    ):
        _deprecation_warning('mymodule', 'old_name', remove=(10, 0))


def test_deprecation_warning_removed_in_sphinx11() -> None:
    """Test _deprecation_warning emits RemovedInSphinx11Warning for remove=(11, 0)."""
    with pytest.warns(
        RemovedInSphinx11Warning, match=r"'mymodule\.old_name' is deprecated"
    ):
        _deprecation_warning('mymodule', 'old_name', remove=(11, 0))


def test_deprecation_warning_with_canonical_name() -> None:
    """Test _deprecation_warning includes replacement name in the message."""
    with pytest.warns(
        RemovedInSphinx10Warning,
        match=r"The alias 'mymodule\.old_name' is deprecated, use 'mymodule\.new_name' instead",
    ):
        _deprecation_warning(
            'mymodule', 'old_name', 'mymodule.new_name', remove=(10, 0)
        )


def test_deprecation_warning_raises_attribute_error() -> None:
    """Test _deprecation_warning raises AttributeError when raises=True."""
    with pytest.raises(AttributeError, match=r"'mymodule\.old_name' is deprecated"):
        _deprecation_warning('mymodule', 'old_name', remove=(10, 0), raises=True)


def test_deprecation_warning_raises_with_canonical_name() -> None:
    """Test _deprecation_warning with raises=True includes the canonical name."""
    with pytest.raises(
        AttributeError,
        match=r"The alias 'mymodule\.old_name' is deprecated, use 'mymodule\.new_name' instead",
    ):
        _deprecation_warning(
            'mymodule', 'old_name', 'mymodule.new_name', remove=(10, 0), raises=True
        )


def test_deprecation_warning_invalid_remove_version() -> None:
    """Test _deprecation_warning raises RuntimeError for an unsupported removal version."""
    with pytest.raises(RuntimeError, match=r'removal version .* is invalid'):
        _deprecation_warning('mymodule', 'old_name', remove=(9, 0))
