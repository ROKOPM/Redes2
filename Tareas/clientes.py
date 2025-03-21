import socket
import time

HOST = '127.0.0.1'
PORT = 12345

def client_workload():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    for i in range(5):
        message = f"Mensaje {i+1} desde el cliente"
        client.sendall(message.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        print(f"[SERVIDOR RESPUESTA] {response}")
        time.sleep(1)  # Simula carga de trabajo
    
    client.close()

if __name__ == "__main__":
    client_workload()