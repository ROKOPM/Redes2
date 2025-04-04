import socket
import selectors
import threading
import sys

sel = selectors.DefaultSelector()

def recibir(sock):
    while True:
        try:
            data = sock.recv(1024)
            if data:
                print(f"\n[Mensaje recibido]: {data.decode()}")
            else:
                print("Conexión cerrada por el servidor.")
                break
        except:
            break

def main():
    if len(sys.argv) != 3:
        print("Uso:", sys.argv[0], "<host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # Hilo para escuchar mensajes del servidor
    threading.Thread(target=recibir, args=(sock,), daemon=True).start()

    print("Puedes escribir mensajes. Presiona Ctrl+C para salir.")
    try:
        while True:
            msg = input("> ")
            if msg:
                sock.sendall(msg.encode())
    except KeyboardInterrupt:
        print("\nCerrando cliente...")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
