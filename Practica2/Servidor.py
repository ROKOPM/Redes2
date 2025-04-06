import socket
import random

HOST = "192.168.1.13"
PORT = 65431

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(1)
        self.client, _ = self.server.accept()

    def recibir(self):
        return self.client.recv(1024).decode()

    def enviar(self, mensaje):
        self.client.send(mensaje.encode())

    def cerrar_socket(self):
        self.client.close()
        self.server.close()

class Matrix:
    def __init__(self, size):
        self.size = size
        self.matriz = [' ' for _ in range(size * size)]

    def mostrar(self):
        print("\n" * 2)
        # Encabezado de columnas
        letras = 'ABCDE'[:self.size]
        encabezado = "\t\t  " + "   ".join(letras)
        print(encabezado)
    
        # Filas del tablero
        for i in range(0, len(self.matriz), self.size):
            fila_num = (i // self.size) + 1
            row = self.matriz[i:i+self.size]
            print(f"\t\t{fila_num} " + " | ".join(row))
            if i + self.size < len(self.matriz):
                separador = "\t\t  " + "-" * (self.size * 3 - 1)
                print(separador)

    def agregar(self, elemento, pos):
        pos_index = self.cast(pos)
        if self.matriz[pos_index] == ' ':
            self.matriz[pos_index] = elemento
        self.mostrar()

    def cast(self, pos):
        letters = 'ABCDE'[:self.size]
        col = letters.index(pos[0].upper())
        row = int(pos[1]) - 1
        return row * self.size + col

    def ganador(self, jugador):
        # Verificar filas y columnas
        for i in range(self.size):
            if all(self.matriz[i*self.size + j] == jugador for j in range(self.size)) or \
               all(self.matriz[j*self.size + i] == jugador for j in range(self.size)):
                return True
        
        # Verificar diagonales
        diag1 = all(self.matriz[i*self.size + i] == jugador for i in range(self.size))
        diag2 = all(self.matriz[i*self.size + (self.size-1-i)] == jugador for i in range(self.size))
        return diag1 or diag2

    def empate(self):
        return ' ' not in self.matriz

    def movimiento_random(self):
        disponibles = [i for i, cell in enumerate(self.matriz) if cell == ' ']
        return random.choice(disponibles) if disponibles else None

def main():
    servidor = Server()
    
    # Recibir dificultad
    difficulty = servidor.recibir()
    size = 3 if difficulty == 'F' else 5
    matrix = Matrix(size)
    matrix.mostrar()

    try:
        while True:
            # Turno cliente
            jugada = servidor.recibir()
            matrix.agregar('X', jugada)
            
            if matrix.ganador('X'):
                servidor.enviar("GANASTE")
                break
            if matrix.empate():
                servidor.enviar("EMPATE")
                break
            
            # Turno servidor
            move = matrix.movimiento_random()
            letters = 'ABCDE'[:size]
            fila = move // size
            columna = move % size
            server_move = f"{letters[columna]}{fila + 1}"
            
            matrix.agregar('O', server_move)
            servidor.enviar(server_move)
            
            if matrix.ganador('O'):
                break
            if matrix.empate():
                servidor.enviar("EMPATE")
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        servidor.cerrar_socket()

if __name__ == "__main__":
    main()