"""Pytest configuration and fixtures."""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Add parent directory to path so we can import from the project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock streamlit for testing
# Create minimal mocks for streamlit components used in the code
# This must be done before any imports that use streamlit


def create_streamlit_mock():
    """Create a mock streamlit module."""
    mock_st = MagicMock()

    # Create mock objects that support method chaining
    mock_empty_obj = MagicMock()
    mock_empty_obj.code = MagicMock(return_value=mock_empty_obj)
    mock_empty_obj.text = MagicMock(return_value=mock_empty_obj)
    mock_empty_obj.markdown = MagicMock(return_value=mock_empty_obj)
    mock_empty_obj.write = MagicMock()

    mock_expander_obj = MagicMock()
    mock_expander_obj.__enter__ = MagicMock(return_value=mock_expander_obj)
    mock_expander_obj.__exit__ = MagicMock(return_value=False)
    mock_expander_obj.code = MagicMock()
    mock_expander_obj.text = MagicMock()

    mock_progress_obj = MagicMock()
    mock_progress_obj.progress = MagicMock()

    # Set up streamlit functions
    mock_st.code = MagicMock(return_value=mock_empty_obj)
    mock_st.empty = MagicMock(return_value=mock_empty_obj)
    mock_st.text = MagicMock(return_value=mock_empty_obj)
    mock_st.markdown = MagicMock(return_value=mock_empty_obj)
    mock_st.info = MagicMock()
    mock_st.success = MagicMock()
    mock_st.error = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.progress = MagicMock(return_value=mock_progress_obj)
    mock_st.expander = MagicMock(return_value=mock_expander_obj)

    # columns should return a list with the requested number of columns
    # Can be called with an integer or a list of weights
    def columns_mock(n):
        if isinstance(n, list):
            return [MagicMock() for _ in range(len(n))]
        return [MagicMock() for _ in range(n)]

    mock_st.columns = columns_mock
    mock_st.subheader = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.rerun = MagicMock()

    # cache_resource decorator that adds a clear() method
    def cache_resource_decorator(func):
        func.clear = MagicMock()
        return func

    mock_st.cache_resource = cache_resource_decorator
    mock_st.set_page_config = MagicMock()
    mock_st.link_button = MagicMock()
    mock_st.status = MagicMock(return_value=mock_expander_obj)

    return mock_st


# Patch streamlit before any imports
sys.modules["streamlit"] = create_streamlit_mock()
