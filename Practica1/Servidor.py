import socket
import os

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("", 5555))
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
        print("Socket cerrado, cliente desconectado.")

class Matrix:
    def __init__(self):
        self.matriz = [str(i+1) for i in range(9)]

    def mostrar(self):
        print("\n" * 2)
        for i in range(0, 9, 3):
            print("\t\t" + "  ".join(self.matriz[i:i+3]))
            print("\n" * 3)

    def agregar(self, elemento, pos):
        self.matriz[pos-1] = elemento
        os.system("cls" if os.name == "nt" else "clear")
        self.mostrar()

    def cast(self, pos):
        return int(pos) - 48

def main():
    servidor = Server()
    matrix = Matrix()
    matrix.mostrar()

    while True:
        print("Turno del jugador Cliente X.")
        charpos = servidor.recibir()[0]
        pos = int(charpos)
        matrix.agregar('X', pos)

        print("\tEs tu turno jugador O.")
        charpos = input("Inserta la posición: ")
        pos = int(charpos)
        matrix.agregar('O', pos)
        servidor.enviar(charpos)

if __name__ == "__main__":
    main()
