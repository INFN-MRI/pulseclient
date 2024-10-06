"""Test suite for pulseclient library."""

import os
import socket
import subprocess
import sys
import time
import unittest

# Conditional imports based on Python version
if sys.version_info[0] == 2:
    from mock import patch, mock_open, MagicMock  # For Python 2.7
else:
    from unittest.mock import patch, mock_open, MagicMock  # For Python 3.x

from pulseclient.lib import (
    load_config,
    is_server_running,
    start_server,
    is_file_complete,
    send_file_to_server,
    watch_file,
)


class TestPulseClient(unittest.TestCase):

    @patch("os.path.exists")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="[DEFAULT]\nSERVER_IP = 192.168.1.100\n",
    )
    def test_load_config_from_default_location(self, mock_file, mock_exists):
        mock_exists.return_value = True  # Simulate that the config file exists
        config = load_config()
        self.assertEqual(config["SERVER_IP"], "192.168.1.100")

    @patch("os.path.exists")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="[DEFAULT]\nSERVER_PORT = 12345\n",
    )
    @patch.dict(os.environ, {"PULSECLIENT_CONFIG": "/custom/path/to/pulseclient.ini"})
    def test_load_config_from_env_variable(self, mock_file, mock_exists):
        mock_exists.return_value = True
        config = load_config()
        self.assertEqual(config["SERVER_PORT"], 12345)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]\n")
    def test_load_config_partial_custom_values(self, mock_file, mock_exists):
        mock_exists.return_value = True
        config = load_config()
        self.assertEqual(
            config["SERVER_IP"], "192.168.1.100"
        )  # Default value should be used

    @patch("subprocess.Popen")
    def test_is_server_running(self, mock_popen):
        # Mock the output of the command
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"external_server.py", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        config = load_config()  # Load config to pass to the function
        result = is_server_running(config)
        self.assertTrue(result)  # The server is running

    @patch("subprocess.Popen")
    def test_start_server_when_running(self, mock_popen):
        config = load_config()  # Load config to pass to the function
        with patch("pulseclient.lib.is_server_running", return_value=True):
            start_server(config)  # Should not raise an error
            mock_popen.assert_not_called()  # Ensure no command is executed

    @patch("subprocess.Popen")
    def test_start_server_when_not_running(self, mock_popen):
        config = load_config()  # Load config to pass to the function
        with patch("pulseclient.lib.is_server_running", return_value=False):
            mock_process = MagicMock()
            mock_process.returnc
