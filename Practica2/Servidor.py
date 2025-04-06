import socket
import random
import threading

HOST = "192.168.1.13"
PORT = 65431

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        self.clients = []
        self.barrier = threading.Barrier(5)
        print("Esperando 5 conexiones...")

#Esperar conexiones
    def handle_client(self, client):
        try:
            self.clients.append(client)
            print(f"Conexión ({len(self.clients)}/5)")
            self.barrier.wait()
#Recibir dificultad y guardar para modificar matriz con size
            difficulty = client.recv(1024).decode().strip().upper()
            size = 3 if difficulty == 'F' else 5
            matrix = Matrix(size)
            client.send("INICIO".encode())
            
            print(f"Juego {len(self.clients)} iniciado ({size}x{size})")
            
#Envio de actualizacion al cliente de movimientos del servidor y su copia correspondiente
#Cada entidad mantiene su copia solo se envian los movimientos echos por cada uno 
            while True:
                jugada = client.recv(1024).decode()
                if not jugada or jugada == "SALIR":
                    break
                
                try:
                    matrix.agregar('X', jugada)
                except ValueError:
                    client.send("INVALIDO".encode())
                    continue
                
                if matrix.ganador('X'):
                    client.send("GANASTE".encode())
                    break
                    
                if matrix.empate():
                    client.send("EMPATE".encode())
                    break
                
                # Turno del servidor
                disponibles = matrix.movimientos_disponibles()
                if not disponibles:
                    client.send("EMPATE".encode())
                    break
#El random
                move = random.choice(disponibles)
                letras = 'ABCDE'[:size]
                server_move = f"{letras[move % size]}{(move // size) + 1}"
                matrix.agregar('O', server_move)
                client.send(server_move.encode())
                
                if matrix.ganador('O'):
                    client.send("PERDISTE".encode())
                    break

        except (ConnectionResetError, BrokenPipeError):
            print("Cliente desconectado")
        finally:
            client.close()
            
#Inicializar hilos para cada cliente

    def start(self):
        for _ in range(5):
            client, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def cerrar_socket(self):
        for client in self.clients:
            client.close()
        self.server.close()
        print("Todos los sockets cerrados.")

class Matrix:
    def __init__(self, size):
        self.size = size
        self.matriz = [' ' for _ in range(size * size)]
#Ahora si ya se muestran las coordenadas y e base a size se construye la matriz
    def mostrar(self):
        print("\n" + "="*30)
        letras = 'ABCDE'[:self.size]
        print("\t\t  " + "   ".join(letras))
        for i in range(0, len(self.matriz), self.size):
            fila = self.matriz[i:i+self.size]
            print(f"\t\t{(i//self.size)+1} " + " | ".join(fila))
            if i + self.size < len(self.matriz):
                print("\t\t  " + "-"*(self.size*3-1))

    def agregar(self, elemento, pos):
        pos_index = self.cast(pos)
        if self.matriz[pos_index] == ' ':
            self.matriz[pos_index] = elemento
            
#Validaciones para errores
    def cast(self, pos):
        if len(pos) != 2:
            raise ValueError("Formato inválido")
        letra = pos[0].upper()
        num = pos[1]
        letras_validas = 'ABCDE'[:self.size]
        if letra not in letras_validas or not num.isdigit():
            raise ValueError("Posición inválida")
        fila = int(num) - 1
        if fila < 0 or fila >= self.size:
            raise ValueError("Fila inválida")
        return fila * self.size + letras_validas.index(letra)
    
#Codiciones de victoria(en base a la matriz y el tamaño 

    def ganador(self, jugador):
        # Horizontal y vertical
        for i in range(self.size):
            if all(self.matriz[i*self.size + j] == jugador for j in range(self.size)):
                return True
            if all(self.matriz[j*self.size + i] == jugador for j in range(self.size)):
                return True
        
        # Diagonales
        diag1 = all(self.matriz[i*self.size + i] == jugador for i in range(self.size))
        diag2 = all(self.matriz[i*self.size + (self.size-1-i)] == jugador for i in range(self.size))
        return diag1 or diag2

    def empate(self):
        return ' ' not in self.matriz

    def movimientos_disponibles(self):
        return [i for i, v in enumerate(self.matriz) if v == ' ']

#llamadas
if __name__ == "__main__":
    try:
        servidor = Server()
        servidor.start()
        input("Presiona Enter para detener el servidor...\n")
    except KeyboardInterrupt:
        print("\nServidor detenido manualmente")
    finally:
        servidor.cerrar_socket()