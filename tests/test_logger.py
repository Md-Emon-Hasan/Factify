from unittest.mock import patch, MagicMock
from app.core.logger import setup_logging
import os

@patch("app.core.logger.os.makedirs")
@patch("app.core.logger.os.path.exists")
def test_setup_logging_creates_dir(mock_exists, mock_makedirs):
    mock_exists.return_value = False
    setup_logging()
    mock_makedirs.assert_called()
