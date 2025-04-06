import socket
import threading

HOST = "192.168.100.9"
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
            # Esperar que el servidor pida la selección de dificultad
            mensaje = input(">>> ").strip().upper()

            if "elige dificultad" in mensaje:
                # Mostrar el mensaje para elegir dificultad
                print("Elige la dificultad:")
                print("1. Fácil (3x3)")
                print("2. Medio (4x4)")
                print("3. Difícil (4x6)")

                # Solicitar la elección de dificultad
                while True:
                    seleccion = input(">>> ").strip()
                    if seleccion == "1" or seleccion == "2" or seleccion == "3":
                        cliente.enviar_mensaje(seleccion)
                        print(f"Dificultad {seleccion} seleccionada correctamente.")
                        break
                    else:
                        print("Selección inválida, por favor elige 1, 2 o 3.")
            else:
                # Enviar el mensaje al servidor (para movimientos)
                cliente.enviar_mensaje(mensaje)

    except KeyboardInterrupt:
        print("Desconectando cliente...")

    finally:
        cliente.cerrar()

if __name__ == "__main__":
    main()
