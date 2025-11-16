"""Smoke test for main script."""

from unittest.mock import patch

import pytest

from main import main


@patch("utils.posting.files_exist")
def test_main(mock_files_exist):
    """Test that main() runs without errors."""
    # Mock files_exist to skip file existence checks
    main()
