import socket
import random
from datetime import datetime

class Servidor:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.juego_iniciado = False
        self.tablero = []
        self.m = 3  # Valores por defecto
        self.n = 3
        self.k = 3
        self.simbolo_cliente = 'X'
        self.simbolo_servidor = 'O'
        self.inicio_partida = None

    def configurar_dificultad(self, dificultad):
        if dificultad == "avanzado":
            self.m, self.n, self.k = 5, 5, 5
        else:  # principiante
            self.m, self.n, self.k = 3, 3, 3
        self.tablero = [[' ' for _ in range(self.n)] for _ in range(self.m)]

    def iniciar(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f"Servidor escuchando en {self.host}:{self.port}...")
        
        conn, addr = self.sock.accept()
        print(f"Conexión establecida con {addr}")
        self.inicio_partida = datetime.now()
        
        # Recibir dificultad
        dificultad = conn.recv(1024).decode()
        self.configurar_dificultad(dificultad)
        conn.sendall(f"Partida iniciada - Dificultad: {dificultad}".encode())
        
        while True:
            # Turno cliente
            data = conn.recv(1024).decode()
            if not data:
                break
            
            x, y = map(int, data.split(','))
            if self.tablero[x][y] == ' ':
                self.tablero[x][y] = self.simbolo_cliente
                estado = self.verificar_estado()
                if estado != "continuar":
                    self.finalizar_partida(conn, estado)
                    break
                
                # Turno servidor
                x_s, y_s = self.generar_jugada_servidor()
                self.tablero[x_s][y_s] = self.simbolo_servidor
                estado = self.verificar_estado()
                conn.sendall(f"{x_s},{y_s},{estado}".encode())
                
                if estado != "continuar":
                    self.finalizar_partida(conn, estado)
                    break
            else:
                conn.sendall("Casilla ocupada".encode())
        
        conn.close()
        self.sock.close()

    def generar_jugada_servidor(self):
        casillas_vacias = [(i, j) for i in range(self.m) for j in range(self.n) if self.tablero[i][j] == ' ']
        return random.choice(casillas_vacias)

    def verificar_estado(self):
        # Horizontal y vertical
        for i in range(self.m):
            for j in range(self.n - self.k + 1):
                if self.tablero[i][j] != ' ' and all(self.tablero[i][j + l] == self.tablero[i][j] for l in range(self.k)):
                    return "ganaste" if self.tablero[i][j] == self.simbolo_cliente else "perdiste"
                
        for j in range(self.n):
            for i in range(self.m - self.k + 1):
                if self.tablero[i][j] != ' ' and all(self.tablero[i + l][j] == self.tablero[i][j] for l in range(self.k)):
                    return "ganaste" if self.tablero[i][j] == self.simbolo_cliente else "perdiste"

        # Empate
        if all(cell != ' ' for row in self.tablero for cell in row):
            return "empate"
        
        return "continuar"

    def finalizar_partida(self, conn, estado):
        fin_partida = datetime.now()
        duracion = fin_partida - self.inicio_partida
        mensaje = f"{estado}-Tiempo: {duracion.total_seconds()} segundos"
        conn.sendall(mensaje.encode())
        print("Partida finalizada:", mensaje)

if __name__ == "__main__":
    host = input("Ingrese IP del servidor: ")
    port = int(input("Ingrese puerto: "))
    dificultad = input("Dificultad (principiante/avanzado): ").lower()
    
    servidor = Servidor(host, port)
    servidor.configurar_dificultad(dificultad)
    servidor.iniciar()