import selectors
import socket
import types
import random

HOST = "192.168.1.13"
PORT = 65432
sel = selectors.DefaultSelector()

LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class Matrix:
#Definimos la config de la matriz
    def __init__(self, filas, columnas, objetivo):
        self.filas = filas
        self.columnas = columnas
        self.objetivo = objetivo
        self.matriz = [[" " for _ in range(columnas)] for _ in range(filas)]

#Esto muestra la matriz
    def mostrar(self):
        header = "   " + "   ".join(LETRAS[:self.columnas])
        lines = [header]
        for idx, fila in enumerate(self.matriz):
            line = f"{idx+1}  " + " | ".join(fila)
            lines.append(line)
            if idx < self.filas - 1:
                separator = "   " + "---+" * (self.columnas - 1) + "---"
                lines.append(separator)
        return "\n".join(lines)
#Este es el metodo que Agrega los simobolos de la matriz ya dibujada
    def agregar(self, simbolo, pos):
        try:
            col = LETRAS.index(pos[0].upper())
            fila = int(pos[1:]) - 1
        except (ValueError, IndexError):
            return False
        if fila < 0 or fila >= self.filas or col < 0 or col >= self.columnas:
            return False
        if self.matriz[fila][col] == " ":
            self.matriz[fila][col] = simbolo
            return True
        return False

    def ganador(self, simbolo):
        for f in range(self.filas):
            for c in range(self.columnas):
                if self.check_direccion(f, c, 1, 0, simbolo): return True
                if self.check_direccion(f, c, 0, 1, simbolo): return True
                if self.check_direccion(f, c, 1, 1, simbolo): return True
                if self.check_direccion(f, c, 1, -1, simbolo): return True
        return False

    def check_direccion(self, f, c, df, dc, simbolo):
        try:
            for i in range(self.objetivo):
                if self.matriz[f + i * df][c + i * dc] != simbolo:
                    return False
            return True
        except IndexError:
            return False

    def posiciones_disponibles(self):
        posiciones = []
        for f in range(self.filas):
            for c in range(self.columnas):
                if self.matriz[f][c] == " ":
                    posiciones.append(f"{LETRAS[c]}{f+1}")
        return posiciones
#Deinir clientes 
clients = []
current_turn = 0
matrix = None
symbols = ["X", "O"]

def aceptar_conexion(sock):
    conn, addr = sock.accept()
    print(f"Cliente conectado desde {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    sel.register(conn, selectors.EVENT_READ, data=data)
    clients.append(conn)
 #Aqui tenemos que el primer jugador en conectarse es el que elige dificultad
    if len(clients) == 1:
        conn.send("Eres el Jugador 1. Elige dificultad:\n1. Fácil (3x3)\n2. Medio (4x4)\n3. Difícil (4x6)\n".encode())
#Para 2 jugadores
    elif len(clients) == 2:
        clients[1].send("Eres el Jugador 2. Esperando jugadas...\n".encode())
        clients[0].send("Comienza el juego. Es tu turno.\n".encode())
        mostrar_tablero_a_todos()

#Procesamos los turnos con un indice
def procesar_jugada(conn, mensaje):
    global current_turn, matrix
    jugador_idx = clients.index(conn)
    
    if jugador_idx != current_turn:
        conn.send("No es tu turno.\n".encode())
        return

    mensaje = mensaje.strip().upper()
    if not matrix.agregar(symbols[jugador_idx], mensaje):
        conn.send("Movimiento inválido o repetido.\n".encode())
        return

    if matrix.ganador(symbols[jugador_idx]):
        enviar_a_todos(f"Jugador {jugador_idx+1} ha ganado!\n")
        mostrar_tablero_a_todos()
        cerrar_servidor()
        return

    mostrar_tablero_a_todos()

    current_turn = (current_turn + 1) % 2
    clients[current_turn].send("Es tu turno.\n".encode())

def mostrar_tablero_a_todos():
    if matrix is not None:
        tablero_str = matrix.mostrar()
        enviar_a_todos(tablero_str + "\n")

def enviar_a_todos(mensaje):
    for c in clients[:]:
        try:
            c.send(mensaje.encode())
        except Exception as e:
            print(f"Error al enviar a un cliente: {e}")
            if c in clients:
                clients.remove(c)
            c.close()

def cerrar_servidor():
    for c in clients:
        c.close()
    sel.close()
    exit()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print(f"Servidor en escucha {HOST}:{PORT}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            aceptar_conexion(key.fileobj)
        else:
            sock = key.fileobj
            data = key.data
            try:
                recv_data = sock.recv(1024)
                if recv_data:
                    mensaje = recv_data.decode().strip()
                    if clients[0] == sock and matrix is None:
                        if mensaje == "1":
                            matrix = Matrix(3, 3, 3)
                        elif mensaje == "2":
                            matrix = Matrix(4, 4, 4)
                        elif mensaje == "3":
                            matrix = Matrix(4, 6, 4)
                        else:
                            sock.send("Opción inválida. Intenta de nuevo.\n".encode())
                            continue
                        sock.send("Dificultad seleccionada. Esperando al Jugador 2...\n".encode())
                    elif matrix:
                        procesar_jugada(sock, mensaje)
                else:
                    print("Cliente desconectado")
                    if sock in clients:
                        clients.remove(sock)
                    sel.unregister(sock)
                    sock.close()
            except Exception as e:
                print(f"Error: {e}")
                if sock in clients:
                    clients.remove(sock)
                sel.unregister(sock)
                sock.close()