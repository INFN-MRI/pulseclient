"""Pulseclient library tools."""

import os
import socket
import time
import subprocess
import sys

# Import configparser or ConfigParser based on Python version
if sys.version_info[0] == 3:
    import configparser  # For Python 3
else:
    import ConfigParser as configparser  # For Python 2.7

# Default configuration values
DEFAULT_CONFIG = {
    "SERVER_IP": "127.0.0.1",
    "SERVER_PORT": 5000,
    "CHECK_INTERVAL": 2,
    "REMOTE_SERVER_USER": "sdc",
    "REMOTE_SERVER_HOST": "remote-machine-name",
    "SERVER_COMMAND": "python /srv/nfs/psd/usr/psd/pulseq/v7/bin/external_server.py",
    "SERVER_PROCESS_NAME": "external_server.py",
    "file_path_simulation": "params.dat",
    "file_path_production": "/srv/nfs/psd/usr/psd/pulseq/v7/temp/params.dat",
    "output_path_simulation": "sequence.bin",
    "output_path_production": "/srv/nfs/psd/usr/psd/pulseq/v7/temp/sequence.bin",
}

# Define the default config file location
DEFAULT_CONFIG_PATH = os.path.expanduser("~/.pulseclient.ini")  # User's home directory


def load_config():
    """
    Load configuration from the pulseclient.ini file.

    First, check the PULSECLIENT_CONFIG environment variable for the file location.
    If not set or file does not exist, fall back to the default config location.
    If no config file is found, use default values.
    Returns the configuration as a dictionary.
    """
    config = DEFAULT_CONFIG.copy()

    # Check the PULSECLIENT_CONFIG environment variable
    config_file = os.getenv("PULSECLIENT_CONFIG", DEFAULT_CONFIG_PATH)

    # If the file exists in the specified or default location, load the configuration
    if os.path.exists(config_file):
        print(
            "Loading configuration from: {}".format(config_file)
        )  # Use .format for compatibility
        parser = configparser.ConfigParser()
        parser.read(config_file)

        # Check if the "settings" section exists
        if parser.has_section("settings"):  # Use has_section instead of direct check
            config.update(
                {
                    "SERVER_IP": parser.get(
                        "settings", "SERVER_IP", fallback=config["SERVER_IP"]
                    ),
                    "SERVER_PORT": parser.getint(
                        "settings", "SERVER_PORT", fallback=config["SERVER_PORT"]
                    ),
                    "CHECK_INTERVAL": parser.getint(
                        "settings", "CHECK_INTERVAL", fallback=config["CHECK_INTERVAL"]
                    ),
                    "REMOTE_SERVER_USER": parser.get(
                        "settings",
                        "REMOTE_SERVER_USER",
                        fallback=config["REMOTE_SERVER_USER"],
                    ),
                    "REMOTE_SERVER_HOST": parser.get(
                        "settings",
                        "REMOTE_SERVER_HOST",
                        fallback=config["REMOTE_SERVER_HOST"],
                    ),
                    "SERVER_COMMAND": parser.get(
                        "settings",
                        "SERVER_COMMAND",
                        fallback=config["SERVER_COMMAND"],
                    ),
                    "SERVER_PROCESS_NAME": parser.get(
                        "settings",
                        "SERVER_PROCESS_NAME",
                        fallback=config["SERVER_PROCESS_NAME"],
                    ),
                    "file_path_simulation": parser.get(
                        "settings",
                        "file_path_simulation",
                        fallback=config["file_path_simulation"],
                    ),
                    "file_path_production": parser.get(
                        "settings",
                        "file_path_production",
                        fallback=config["file_path_production"],
                    ),
                    "output_path_simulation": parser.get(
                        "settings",
                        "output_path_simulation",
                        fallback=config["output_path_simulation"],
                    ),
                    "output_path_production": parser.get(
                        "settings",
                        "output_path_production",
                        fallback=config["output_path_production"],
                    ),
                }
            )
    else:
        print("No config file found at {}. Using default values.".format(config_file))

    return config


def is_localhost(config):
    """ Check if the IP is localhost. """
    return config["SERVER_IP"] == "127.0.0.1" or config["SERVER_IP"] == "localhost"


def _is_server_running_locally(config):
    """
    Check if the server process is running locally.
    This function checks the system's process list to see if the server is running.
    """
    try:
        # For Python 2.6+ and Python 3 compatibility, we use subprocess with Popen
        if os.name == 'nt':
            # For Windows, check with tasklist
            process = subprocess.Popen(["tasklist"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            # For Unix-based systems (Linux/Mac), use ps
            process = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, _ = process.communicate()
        # Convert to string in case it's bytes (for Python 3+)
        stdout = stdout.decode("utf-8") if isinstance(stdout, bytes) else stdout

        # Check if the server name is in the process list
        if config["SERVER_PROCESS_NAME"] in stdout:
            print("Server is already running.")
            return True
        else:
            print("Server is not running.")
            return False

    except Exception as e:
        print("Failed to check if server is running: %s" % str(e))
        return False
    
    
def _is_server_running_remotely(config):
    """Check if the server is running on a remote machine via SSH."""
    try:
        # Build SSH command to check if the process is running
        ssh_command = [
            "ssh",
            "%s@%s" % (config["REMOTE_SERVER_USER"], config["REMOTE_SERVER_HOST"]),
            "ps aux | grep %s | grep -v grep" % config["SERVER_PROCESS_NAME"],
        ]

        # Execute the SSH command
        process = subprocess.Popen(
            ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = process.communicate()

        # If output contains the process name, it's already running
        if config["SERVER_PROCESS_NAME"] in output.decode("utf-8"):
            print("Server is already running on remote machine.")
            return True
        else:
            print("Server is not running on remote machine.")
            return False

    except Exception as e:
        print("Error while checking server status: %s" % str(e))
        return False


def is_server_running(config):
    """Check if the server is running on a remote machine."""
    if is_localhost(config):
        return _is_server_running_locally(config)
    return _is_server_running_remotely(config)


def _start_server_locally(config):
    """Start the server on the local machine."""
    print("Starting server locally on localhost...")
    process = subprocess.Popen(
        config["SERVER_COMMAND"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
    )
    output, error = process.communicate()

    if process.returncode == 0:
        print("Server started successfully on local machine.")
    else:
        print("Failed to start server. Error: %s" % error.decode("utf-8"))     


def _start_server_remotely(config):
    """Start the server on a remote machine using SSH."""
    print("Starting server on remote machine...")
    ssh_command = [
        "ssh",
        "%s@%s" % (config["REMOTE_SERVER_USER"], config["REMOTE_SERVER_HOST"]),
        config["SERVER_COMMAND"],
    ]

    # Start the external server via SSH
    process = subprocess.Popen(
        ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
    )
    output, error = process.communicate()

    if process.returncode == 0:
        print("Server started successfully on remote machine.")
    else:
        print("Failed to start server. Error: %s" % error.decode("utf-8"))     


def start_server(config):
    """Start the server."""
    if is_server_running(config):
        return

    # try:
    if is_localhost(config):
        _start_server_locally(config)
    else:
        _start_server_remotely(config)
            
    # except Exception as e:
    #     print("Error while starting server: %s" % str(e))


def is_file_complete(file_path, config):
    """Check if the file is complete and ready for processing by comparing file size over time."""
    try:
        file_size = os.stat(file_path).st_size
        time.sleep(config["CHECK_INTERVAL"])  # Wait a bit to see if the size changes
        new_size = os.stat(file_path).st_size
        return (
            file_size == new_size and file_size > 0
        )  # If size hasn't changed, the file is complete
    except OSError:
        return False


def send_file_to_server(file_path, config):
    """Send the file over a socket connection to the external server."""
    try:
        # Open a socket connection to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((config["SERVER_IP"], config["SERVER_PORT"]))
        print(
            "Connected to server %s:%d" % (config["SERVER_IP"], config["SERVER_PORT"])
        )

        # Open the file and send its content over the socket
        with open(file_path, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                sock.sendall(data)
        print("File sent to the server successfully.")

        # Close the socket
        sock.close()

    except Exception as e:
        print("Failed to send file to server: %s" % str(e))


def send_buffer_to_server(data_buffer, config, response_file_path):
    """
    Send the byte buffer over a socket connection to the external server.

    After sending the buffer, waits for the server's response to write it down to a file.
    """
    try:
        # Open a socket connection to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((config["SERVER_IP"], config["SERVER_PORT"]))
        print(
            "Connected to server %s:%d" % (config["SERVER_IP"], config["SERVER_PORT"])
        )

        # Send the entire data buffer over the socket using sendall
        sock.sendall(data_buffer)
        print("Data buffer sent to the server successfully.")

        # Now, receive the response from the server
        with open(response_file_path, "wb") as response_file:
            while True:
                received_data = sock.recv(1024)
                if not received_data:
                    break
                response_file.write(received_data)
            print(
                "Response received from server and written to %s." % response_file_path
            )

    except Exception as e:
        print("Failed to communicate with server: %s" % str(e))

    finally:
        sock.close()  # Ensure the socket is closed


def watch_file(file_path, config, output_path):
    """Watch the file for changes and send it to the server once it's complete."""
    while True:
        if os.path.exists(file_path) and is_file_complete(file_path, config):
            print("File detected and is ready: %s" % file_path)
            send_buffer_to_server(file_path, config, output_path)
            break

        # Wait before checking again
        time.sleep(config["CHECK_INTERVAL"])
