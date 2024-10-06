
PulseClient
===========

PulseClient is a Python library designed to facilitate the communication between an Pulseq interpreter process running
on a MRI scanner and an external Pulseq sequence design server. 

It provides functionality to check if a remote Pulseq design server is running, start the server if it isn't, and monitor sequence parameter files for transfer readiness. 

Features
--------
- Checks if a remote Pulseq design server process is running.
- Starts the Pulseq design server on a remote machine via SSH if it is not running.
- Monitors the creation of a sequence parameters (e.g., FOV, matrix size, etc) by the Pulseq interpreter and sends it to a designated server.
- Configuration management through a `.ini` file for easy customization.
- Fallback to default values if no configuration file is found.

Installation
------------
PulseClient can be installed via pip::

  pip install pulseclient

As an alternative, you can incorporate this library in your Pulseq interpreter code as::

  git submodule add -b plugin https://github.com/INFN-MRI/pulseclient.git bin

Development
-----------
If you want to modifiy the PulseClient code base::

  git clone https://github.com/INFN-MRI/pulseclient.git
  pip install -e ./pulseclient

Configuration
-------------
PulseClient uses a configuration file named ``pulseclient.ini``. You can specify the location of this file using the ``PULSECLIENT_CONFIG`` environment variable. 
If not set, the library will search for the configuration file in the default location::

  /srv/psd/usr/psd/pulseq/config/pulseclient.ini

The configuration file should contain the following sections::

  [settings]
  SERVER_IP = 192.168.1.100
  SERVER_PORT = 8000
  CHECK_INTERVAL = 0.1
  REMOTE_SERVER_USER = user
  REMOTE_SERVER_HOST = remote-server-address.com
  REMOTE_SERVER_COMMAND = external_server.py &
  SERVER_PROCESS_NAME = external_server.py
  file_path_simulation = /path/to/simulation/params.dat
  file_path_hardware = /path/to/production/params.dat


where ``file_path_simulation`` and ``file_path_hardware`` are the path to the `params.dat` file created
by the Pulseq interpreter either in simulation or actual hardware execution, which can be toggled at runtime
by the Pulseq interpreter itself.

Usage
-----
You can run the PulseClient from the command line, providing a simulation flag (``0`` for hardware, ``1`` for simulation, default is ``1``)::

  start_client.py [simulate]

Replace ``[simulate]`` with ``1`` for simulation or `0` for hardware mode.

Testing
-------
To run the tests, execute the following command in the terminal::

   python -m unittest discover -s tests

License
-------
This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

Contributing
------------
Contributions are welcome! Please fork the repository and submit a pull request.
