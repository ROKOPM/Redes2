import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b"Mensaje 1 del cliente.", b"Mensaje 2 del cliente."]

def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print("Iniciando conexión", connid, "con", server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            messages=list(messages),
            outb=b"",
            received_data=b"",
        )
        sel.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("Enviando", repr(data.outb), "a conexión", data.connid)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
            if not data.messages:
                sel.modify(sock, selectors.EVENT_READ, data)

    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)
            if recv_data:
                print("Recibido", repr(recv_data), "de conexión", data.connid)
                data.received_data += recv_data
            else:
                print("Cerrando conexión", data.connid)
                sel.unregister(sock)
                sock.close()
        except ConnectionResetError:
            print(f"Conexión {data.connid} cerrada por el servidor")
            sel.unregister(sock)
            sock.close()

if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <num_connections>")
    sys.exit(1)

host, port, num_conns = sys.argv[1:4]
start_connections(host, int(port), int(num_conns))

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
