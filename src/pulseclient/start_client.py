#!/usr/bin/env python3

import argparse
from .lib import start_server, watch_file, load_config


def main():
    """
    Main entry point for the CLI. Parses an integer argument to determine the mode of operation:
    - 1 for simulation (uses configured simulation file path),
    - 0 for production (uses configured production file path).
    If no argument is provided, the default is 1 (simulate mode).
    """
    # Create an argument parser for CLI
    parser = argparse.ArgumentParser(
        description="Watch a file and send it to a remote server."
    )

    # Positional argument for simulation mode (expects 1 for simulate, 0 for production)
    parser.add_argument(
        "mode",
        type=int,
        nargs="?",  # Makes it optional
        default=1,  # Default to simulate mode (1)
        choices=[0, 1],
        help=(
            "Mode of operation: "
            "1 for simulate (use local params.dat), "
            "0 for production (use remote file path). Default is 1."
        ),
    )

    # Parse the arguments
    args = parser.parse_args()

    # Load the configuration from the ini file or defaults
    config = load_config()

    # Determine the file path based on the mode
    if args.mode == 1:
        file_path = config["file_path_simulation"]
        print(f"Running in simulate mode (using {file_path})")
    else:
        file_path = config["file_path_production"]
        print(f"Running in production mode (using {file_path})")

    # Start the server (on a remote machine)
    start_server(config)

    # Watch for the file and send it once ready
    watch_file(file_path, config)


if __name__ == "__main__":
    main()
