import socket

HOST = "192.168.100.9"  # Dirección del servidor
PORT = 65432  # Puerto del servidor

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(1)
        print("Escuchando para conexiones entrantes.")
        self.client, _ = self.server.accept()
        print("Cliente conectado!")

    def recibir(self):
        data = self.client.recv(1024).decode()
        print(f"El cliente dice: {data}")
        return data

    def enviar(self, mensaje):
        self.client.send(mensaje.encode())
        print("Mensaje enviado!")

    def cerrar_socket(self):
        self.client.close()
        self.server.close()
        print("Socket cerrado, cliente desconectado.")

    def __del__(self):
        self.cerrar_socket()

class Matrix:
    def __init__(self):
        self.matriz = [' ' for _ in range(9)]  # Inicializamos con espacio vacío

    def mostrar(self):
        print("\n" * 2)
        for i in range(0, 9, 3):
            print("\t\t" + " | ".join(self.matriz[i:i+3]))
            if i + 3 < 9:
                print("\t\t---------")

    def agregar(self, elemento, pos):
        pos = self.cast(pos)
        if self.matriz[pos] == ' ':
            self.matriz[pos] = elemento
        self.mostrar()

    def cast(self, pos):
        # Convertir las letras a índices de lista
        letters = 'ABC'
        return letters.index(pos[0].upper()) + (int(pos[1]) - 1) * 3

def main():
    servidor = Server()
    matrix = Matrix()
    matrix.mostrar()

    try:
        while True:
            print("Turno del jugador Cliente X.")
            charpos = servidor.recibir()
            matrix.agregar('X', charpos)

            print("\tEs tu turno jugador O.")
            charpos = input("Inserta la posición (Ej: A1, B2, C3): ")
            matrix.agregar('O', charpos)
            servidor.enviar(charpos)
    except KeyboardInterrupt:
        print("\nCerrando el servidor...")
        servidor.cerrar_socket()

if __name__ == "__main__":
    main()
