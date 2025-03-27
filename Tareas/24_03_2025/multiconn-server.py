import socket
import selectors
import types

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()  
    print(f'Conexión aceptada desde {addr}')
    conn.setblocking(False)
    data = types.SimpleNamespace(handler=read_write, messages=[], outb=b"")
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data)

def read_write(conn, mask):
    data = sel.get_map()[conn].data

    if mask & selectors.EVENT_READ:
        recv_data = conn.recv(1024)
        if recv_data:
            print(f'Recibido: {recv_data} desde {conn}')
            data.messages.append(recv_data)
        else:
            print(f'Cerrando conexión {conn}')
            sel.unregister(conn)
            conn.close()
            return

    if mask & selectors.EVENT_WRITE and data.messages:
        data.outb = data.messages.pop(0)
        print(f'Enviando: {data.outb} a {conn}')
        conn.sendall(data.outb)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(('192.168.135.167', 12345))
    sock.listen(100)
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, accept)

    try:
        while True:
            events = sel.select()
            for key, mask in events:
                callback = key.data.handler if hasattr(key.data, "handler") else key.data
                callback(key.fileobj, mask)
    except KeyboardInterrupt:
        print("Servidor detenido")
    finally:
        sel.close()
