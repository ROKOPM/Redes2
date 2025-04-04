import socket
import selectors
import types

sel = selectors.DefaultSelector()
clientes = {}

def aceptar(sock, mask):
    conn, addr = sock.accept()
    print(f'[+] Conexión aceptada desde {addr}')
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, messages=[], outb=b"")
    clientes[conn] = data
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data)

def actualizar(remitente, mensaje):
    for conn, data in clientes.items():
        if conn != remitente:
            data.messages.append(mensaje)

def manejar_cliente(conn, mask):
    if conn not in clientes:
        print("[!] Conexión no registrada, ignorando...")
        return  # Seguridad adicional para evitar KeyError

    data = clientes[conn]

    if mask & selectors.EVENT_READ:
        try:
            recv_data = conn.recv(1024)
            if recv_data:
                mensaje = recv_data.decode()
                print(f'[Mensaje de {data.addr}]: {mensaje}')
                actualizar(conn, f"[{data.addr}]: {mensaje}".encode())
            else:
                cerrar_conexion(conn)
        except (ConnectionResetError, ConnectionAbortedError):
            print(f'[!] Conexión perdida con {data.addr}')
            cerrar_conexion(conn)

    if mask & selectors.EVENT_WRITE:
        if data.messages:
            mensaje = data.messages.pop(0)
            try:
                conn.sendall(mensaje)
            except Exception as e:
                print(f'[!] Error enviando a {data.addr}: {e}')
                cerrar_conexion(conn)

def cerrar_conexion(conn):
    try:
        addr = clientes[conn].addr
        print(f'[-] Cerrando conexión {addr}')
        sel.unregister(conn)
        conn.close()
        del clientes[conn]
    except Exception as e:
        print(f'[!] Error al cerrar conexión: {e}')

if __name__ == "__main__":
    HOST = "192.168.100.9"  # Ajusta si cambia la red
    PORT = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(100)
        sock.setblocking(False)
        sel.register(sock, selectors.EVENT_READ, aceptar)

        print(f"✅ Servidor escuchando en {HOST}:{PORT}...")

        try:
            while True:
                events = sel.select()
                for key, mask in events:
                    if key.data is None:
                        aceptar(key.fileobj, mask)
                    else:
                        manejar_cliente(key.fileobj, mask)
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido")
        finally:
            sel.close()
