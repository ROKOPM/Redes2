import socket
import os

class Client:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect(("192.168.1.82", 5555))
        print("Connected to server!")

    def enviar(self, mensaje):
        self.server.send(mensaje.encode())
        print("Mensaje enviado!")

    def recibir(self):
        data = self.server.recv(1024).decode()
        print(f"El Servidor dice: {data}")
        return data

    def cerrar(self):
        self.server.close()
        print("Socket cerrado.\n")

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
    cliente = Client()
    matrix = Matrix()
    matrix.mostrar()

    while True:
        print("\tEs tu turno.")
        charpos = input("Inserta la posición: ")
        pos = int(charpos)
        matrix.agregar('X', pos)
        cliente.enviar(charpos)

        print("Turno del jugador Servidor.")
        charpos = cliente.recibir()[0]
        pos = int(charpos)
        matrix.agregar('O', pos)

if __name__ == "__main__":
    main()
