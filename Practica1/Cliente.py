#Aqui va codigo para la primera practica import socket
import socket

def create_client_socket():
    # Create client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to server
    host = 'localhost'
    port = 12345
    client_socket.connect((host, port))
    return client_socket