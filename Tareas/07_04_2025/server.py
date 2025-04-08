import socket
import threading
import time
import random

lock = threading.Lock()

def handle_client(conn, addr):
    intentos = 0
    exito = False
    for _ in range(10):
        if lock.acquire(blocking=False):
            try:
                print(f"[{addr}] Entró en la sección crítica")
                conn.sendall(b"Acceso concedido a la seccion critica\n")
                time.sleep(random.randint(1, 3))  # Simulamos trabajo
                exito = True
                break
            finally:
                lock.release()
        else:
            intentos += 1
            conn.sendall(f"No se pudo acceder. Intento {intentos}\n".encode())
            time.sleep(2)

    if not exito:
        conn.sendall(b"No se pudo acceder a la seccion critica tras 10 intentos\n")

    conn.close()

# Crear socket TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('192.168.100.9', 9999))
server.listen()

print("Servidor listo en el puerto 9999...")

while True:
    conn, addr = server.accept()
    hilo = threading.Thread(target=handle_client, args=(conn, addr))
    hilo.start()
