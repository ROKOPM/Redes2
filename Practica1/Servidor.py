import socket
import random

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
        letters = 'ABC'
        return letters.index(pos[0].upper()) + (int(pos[1]) - 1) * 3

    def ganador(self, jugador):
        condiciones = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
            [0, 4, 8], [2, 4, 6]  # Diagonales
        ]
        return any(all(self.matriz[i] == jugador for i in cond) for cond in condiciones)

    def movimientos_disponibles(self):
        return [i for i, v in enumerate(self.matriz) if v == ' ']

    def movimiento_random(self):
        if self.movimientos_disponibles():
            return random.choice(self.movimientos_disponibles())
        return None

def main():
    servidor = Server()
    matrix = Matrix()
    matrix.mostrar()

    try:
        while True:
            print("Turno del jugador Cliente X.")
            charpos = servidor.recibir()
            matrix.agregar('X', charpos)
            if matrix.ganador('X'):
                print("Jugador X gana!")
                servidor.enviar("GANASTE")
                break

            print("Turno del servidor (O).")
            move = matrix.movimiento_random()
            if move is not None:
                letters = 'ABC'
                server_move = f"{letters[move % 3]}{(move // 3) + 1}"
                matrix.agregar('O', server_move)
                servidor.enviar(server_move)
                if matrix.ganador('O'):
                    print("Jugador O gana!")
                    break
    except KeyboardInterrupt:
        print("\nCerrando el servidor...")
    finally:
        servidor.cerrar_socket()

if __name__ == "__main__":
    main()
