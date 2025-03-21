import socket
import threading
import time

# Configuración del servidor
HOST = '10.3.56.44'  # Dirección local
PORT = 12345        # Puerto de escucha
MAX_CLIENTS = 5

def handle_client(conn, addr):
    print(f"[NUEVA CONEXIÓN] Cliente conectado desde {addr}")
    conn.setblocking(False)  # Hacer que el socket del cliente también sea no bloqueante
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"[RECIBIDO] {addr}: {data}")
            conn.sendall(f"Echo: {data}".encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"[DESCONECTADO] Cliente {addr} se ha desconectado")

# Crear socket del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)  # Hacer que el socket del servidor sea no bloqueante
server.bind((HOST, PORT))
server.listen(MAX_CLIENTS)
print(f"[INICIO] Servidor escuchando en {HOST}:{PORT}")

while True:
    try:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVO] Conexiones activas: {threading.active_count() - 1}")
    except Exception as e:
        print(f"[ERROR] Aceptando conexión: {e}")
