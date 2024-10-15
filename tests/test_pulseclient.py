"""Test suite for pulseclient library."""

import os
import socket
import subprocess
import sys
import time
import unittest

from io import BytesIO  # Used to mock binary file handling

# Conditional imports based on Python version
if sys.version_info[0] == 2:
    from mock import call, patch, mock_open, MagicMock  # For Python 2.7
else:
    from unittest.mock import call, patch, mock_open, MagicMock  # For Python 3.x

from pulseclient.lib import (
    load_config,
    is_server_running,
    start_server,
    is_file_complete,
    send_file_to_server,
    send_buffer_to_server,
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


class TestSendBufferToServer(unittest.TestCase):

    @patch("builtins.open", create=True)
    @patch("socket.socket")
    def test_send_buffer_to_server(self, mock_socket, mock_open):
        """
        Test that send_buffer_to_server correctly sends data to the server
        and writes the server's response to a file.
        """

        # Setup
        data_buffer = b"Test byte buffer data to be sent"
        config = {"SERVER_IP": "127.0.0.1", "SERVER_PORT": 5000}
        response_file_path = "test_response.bin"
        expected_server_response = [
            b"Server response data part 1",
            b"Server response data part 2",
        ]

        # Mock the socket connection and behavior
        mock_sock_instance = mock_socket.return_value

        # Simulate server sending data in parts, followed by an empty string (end of stream)
        mock_sock_instance.recv.side_effect = expected_server_response + [
            b""
        ]  # Simulate end of transmission

        # Mock file open to return a file-like mock object
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run the function
        send_buffer_to_server(data_buffer, config, response_file_path)

        # Assertions:
        # 1. Assert socket connection was made to the correct IP and port
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_sock_instance.connect.assert_called_once_with(("127.0.0.1", 5000))

        # 2. Assert data was sent through the socket
        mock_sock_instance.sendall.assert_called()  # Ensure some data was sent

        # 3. Assert file writes occurred correctly
        # Check that the file was opened in 'wb' mode
        mock_open.assert_called_once_with(response_file_path, "wb")

        # Check the data that was written to the file
        # Now using assert_has_calls to allow for multiple calls
        mock_file.write.assert_has_calls(
            [
                call(b"Server response data part 1"),
                call(b"Server response data part 2"),
            ],
            any_order=True,
        )

        # # 4. Assert socket was closed
        mock_sock_instance.close.assert_called_once()
