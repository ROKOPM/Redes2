import socket
import selectors
import threading
import sys

sel = selectors.DefaultSelector()

def recibir(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[!] Conexión cerrada por el servidor.")
                break
            print(f"\n[Mensaje recibido]: {data.decode()}")
        except ConnectionResetError:
            print("\n[!] Conexión cerrada inesperadamente.")
            break
        except Exception as e:
            print(f"\n[!] Error recibiendo datos: {e}")
            break

def main():
    if len(sys.argv) != 3:
        print("Uso:", sys.argv[0], "<host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"[!] No se pudo conectar al servidor: {e}")
        sys.exit(1)

    # Hilo para escuchar mensajes del servidor
    threading.Thread(target=recibir, args=(sock,), daemon=True).start()

    print("Puedes escribir mensajes. Presiona Ctrl+C para salir.")
    try:
        while True:
            msg = input("> ")
            if msg:
                try:
                    sock.sendall(msg.encode())
                except BrokenPipeError:
                    print("[!] No se pudo enviar el mensaje, conexión cerrada.")
                    break
    except KeyboardInterrupt:
        print("\nCerrando cliente...")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
