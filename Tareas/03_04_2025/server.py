import socket
import threading

clients = []

def handle_client(conn, addr):
    print(f"[NUEVA CONEXIÓN] {addr} conectado.")
    conn.send("Conectado al servidor.".encode())

    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break

            print(f"[{addr}] {msg}")
            
            # Reenviar mensaje a los otros clientes
            for client in clients:
                if client != conn:
                    try:
                        client.send(f"Mensaje de {addr}: {msg}".encode())
                    except:
                        clients.remove(client)
        except:
            break

    print(f"[DESCONECTADO] {addr}")
    clients.remove(conn)
    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("192.168.100.9", 5555))  
    server.listen()

    print("[ESCUCHANDO] Servidor en espera de conexiones...")

    while True:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start_server()

