import socket
import threading

HOST = "192.168.1.13"
PORT = 65432

class Cliente:
    def __init__(self, host, puerto):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, puerto))
        self.running = True

    def recibir_mensajes(self):
        while self.running:
            try:
                mensaje = self.client.recv(4096).decode()
                if mensaje:
                    print(mensaje)  # Mostrar mensajes del servidor
                else:
                    print("Conexión cerrada por el servidor.")
                    self.running = False
                    break
            except Exception as e:
                print(f"Error al recibir mensaje: {e}")
                self.running = False
                break

    def enviar_mensaje(self, mensaje):
        try:
            self.client.send(mensaje.encode())
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")
            self.running = False

    def cerrar(self):
        self.client.close()

def main():
    cliente = Cliente(HOST, PORT)
    
    # Hilo para recibir mensajes del servidor
    hilo_recibir = threading.Thread(target=cliente.recibir_mensajes)
    hilo_recibir.daemon = True  # Para que el hilo se cierre al finalizar el programa
    hilo_recibir.start()

    try:
        while cliente.running:
            # Leer entrada del usuario y enviar al servidor
            mensaje = input(">>> ").strip().upper()
            cliente.enviar_mensaje(mensaje)

    except KeyboardInterrupt:
        print("Desconectando cliente...")

    finally:
        cliente.cerrar()

if __name__ == "__main__":
    main()