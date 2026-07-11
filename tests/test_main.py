"""Smoke test for main script."""

from unittest.mock import patch

import pytest

from main import main


@patch("main.copy_text_to_file")  # Prevent JOB_DESCRIPTION.md file creation
@patch("utils.posting.files_exist")  # Skip file existence checks
def test_main(mock_files_exist, mock_copy_text_to_file):
    """Test that main() runs without errors."""
    main()
