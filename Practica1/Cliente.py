import socket
from datetime import datetime

class Cliente:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tablero = []
        self.simbolo_servidor = 'O'
    
    def conectar(self, host, port, dificultad):
        self.sock.connect((host, port))
        self.sock.sendall(dificultad.encode())
        
        respuesta = self.sock.recv(1024).decode()
        print(respuesta)
        self.inicializar_tablero(dificultad)
        self.mostrar_tablero()
        
        while True:
            try:
                x = int(input("Fila: "))
                y = int(input("Columna: "))
                self.sock.sendall(f"{x},{y}".encode())
                
                data = self.sock.recv(1024).decode()
                if '-' in data:  # Mensaje final
                    estado, tiempo = data.split('-')
                    print(f"\nResultado: {estado} | {tiempo}")
                    break
                
                if data == "Casilla ocupada":
                    print("¡Casilla ocupada! Intenta otra")
                    continue
                
                x_s, y_s, estado = data.split(',')
                self.tablero[int(x_s)][int(y_s)] = self.simbolo_servidor
                self.mostrar_tablero()
                print(f"Estado: {estado}")
                
            except ValueError:
                print("Entrada inválida. Usa números enteros")

    def inicializar_tablero(self, dificultad):
        size = 5 if dificultad == "avanzado" else 3
        self.tablero = [[' ' for _ in range(size)] for _ in range(size)]

    def mostrar_tablero(self):
        print("\nTablero:")
        for row in self.tablero:
            print('|'.join(row))
            print('-' * (len(row)*2 - 1))

if __name__ == "__main__":
    host = input("IP del servidor: ")
    port = int(input("Puerto: "))
    dificultad = input("Dificultad (principiante/avanzado): ").lower()
    
    cliente = Cliente()
    cliente.conectar(host, port, dificultad)