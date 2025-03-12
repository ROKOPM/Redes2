import socket

def create_server_socket():
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set socket options to reuse address
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind socket to host and port
    host = 'localhost'
    port = 12345
    server_socket.bind((host, port))
    # Listen for connections
    server_socket.listen(5)
    return server_socket