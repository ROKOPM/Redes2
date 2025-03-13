import socket

HOST = "192.168.100.9"  # Dirección del servidor
PORT = 65432  # Puerto del servidor

class Client:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((HOST, PORT))  # Usando el HOST y PORT especificados
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
    cliente = Client()
    matrix = Matrix()
    matrix.mostrar()

    while True:
        print("\tEs tu turno.")
        charpos = input("Inserta la posición (Ej: A1, B2, C3): ")
        matrix.agregar('X', charpos)
        cliente.enviar(charpos)

        print("Turno del jugador Servidor.")
        charpos = cliente.recibir()
        matrix.agregar('O', charpos)

if __name__ == "__main__":
    main()
