import socket
import selectors
import types

sel = selectors.DefaultSelector()
clientes = {}

def aceptar(sock, mask):
    conn, addr = sock.accept()  # Acepta la conexión
    print(f'[+] Conexión aceptada desde {addr}')
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, messages=[], outb=b"")
    clientes[conn] = data
    # Registrar la conexión del cliente en el selector
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data)
    print(f'[+] Conexión registrada para {addr}')

def actualizar(remitente, mensaje):
    # Enviar el mensaje a todos los clientes, menos al remitente
    for conn, data in clientes.items():
        if conn != remitente:
            data.messages.append(mensaje)

def manejar_cliente(conn, mask):
    if conn not in clientes:
        print("[!] Conexión no registrada, ignorando...")
        return  # Seguridad adicional para evitar KeyError

    data = clientes.get(conn)  # Usar .get() para evitar KeyError
    if not data:
        return  # Si el socket ya fue eliminado, salir

    if mask & selectors.EVENT_READ:
        try:
            recv_data = conn.recv(1024)
            if recv_data:
                mensaje = recv_data.decode()
                print(f'[Mensaje de {data.addr}]: {mensaje}')
                # Enviar el mensaje recibido a todos los demás clientes
                actualizar(conn, f"[{data.addr}]: {mensaje}".encode())
            else:
                cerrar_conexion(conn)
        except (ConnectionResetError, ConnectionAbortedError):
            print(f'[!] Conexión perdida con {data.addr}')
            cerrar_conexion(conn)
        except Exception as e:
            print(f'[!] Error inesperado con {data.addr}: {e}')
            cerrar_conexion(conn)

    if mask & selectors.EVENT_WRITE and data in clientes.values():
        if data.messages:
            mensaje = data.messages.pop(0)
            try:
                conn.sendall(mensaje)
            except Exception as e:
                print(f'[!] Error enviando a {data.addr}: {e}')
                cerrar_conexion(conn)

def cerrar_conexion(conn):
    try:
        if conn in clientes:
            addr = clientes[conn].addr
            print(f'[-] Cerrando conexión {addr}')
            sel.unregister(conn)
            del clientes[conn]  # Eliminar antes de cerrar
            conn.close()
    except Exception as e:
        print(f'[!] Error al cerrar conexión: {e}')

if __name__ == "__main__":
    HOST = "192.168.100.9"  # Ajusta si cambia la red
    PORT = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(100)
        sock.setblocking(False)
        # Registrar el socket de escucha para aceptar nuevas conexiones
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
