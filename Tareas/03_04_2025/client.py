import socket
import threading

def recibir_mensajes(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print("\n[Nuevo mensaje]:", msg)
        except:
            print("Conexión cerrada.")
            break

def cliente():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.100.9", 5555))  

    thread = threading.Thread(target=recibir_mensajes, args=(sock,))
    thread.daemon = True
    thread.start()

    print("Escribe mensajes. Escribe 'salir' para cerrar.")
    while True:
        msg = input("> ")
        if msg.lower() == "salir":
            break
        sock.send(msg.encode())

    sock.close()

cliente()
