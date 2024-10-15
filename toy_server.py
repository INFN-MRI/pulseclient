#!/usr/bin/python

import socket

def start_server():
    # Create a socket object
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to an address and port
    server_sock.bind(('127.0.0.1', 5000))
    server_sock.listen(1)
    print("Server listening on 127.0.0.1:5000")

    # Wait for a client connection
    conn, addr = server_sock.accept()
    print("Connected by", addr)

    # Receive data from the client
    received_data = b""
    while True:
        data = conn.recv(1024)
        if not data:
            break
        received_data += data

    print("Data received from client:", received_data)

    # Send a response back to the client
    response = b"Server response data: " + received_data
    conn.sendall(response)
    
    # Signal that no more data will be sent
    conn.shutdown(socket.SHUT_WR)

    # Close the connection
    conn.close()

if __name__ == "__main__":
    start_server()
