import socket
import random
import threading
import time  # Nuevo: Import para manejar el tiempo

HOST = "192.168.1.13"
PORT = 65431

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        self.partidas = {}  
        print("Servidor listo. Esperando conexiones...")

        # Nuevo: Hilo que verifica partidas sin jugadores por 1 minuto
        threading.Thread(target=self._verificar_partidas_incompletas, daemon=True).start()

    # ========== Método nuevo para validación de tiempo ==========
    def _verificar_partidas_incompletas(self):
        """Elimina partidas que llevan más de 1 minuto sin completarse"""
        while True:
            tiempo_actual = time.time()
            partidas_a_eliminar = []
            
            for dificultad, partida in self.partidas.items():
                tiempo_transcurrido = tiempo_actual - partida['start_time']
                jugadores_conectados = len(partida['clientes'])
                
                # Validar si pasó 1 minuto y faltan jugadores
                if tiempo_transcurrido > 60 and jugadores_conectados < partida['max_jugadores']:
                    partidas_a_eliminar.append(dificultad)
                    for cliente in partida['clientes']:
                        try:
                            cliente.send("No se encontraron mas jugadores\n".encode())
                            cliente.close()
                        except:
                            pass
            
            # Eliminar partidas fuera del loop para evitar errores
            for dificultad in partidas_a_eliminar:
                del self.partidas[dificultad]
            
            time.sleep(5)  # Revisar cada 5 segundos
    # ============================================================

    # Envía un mensaje a todos los clientes de una partida
    def broadcast(self, mensaje, dificultad):
        if dificultad in self.partidas:
            for cliente in self.partidas[dificultad]['clientes']:
                try:
                    cliente.send(f"{mensaje}\n".encode())
                except:
                    self.manejar_desconexion(cliente, dificultad)

    # Elimina un cliente desconectado y notifica
    def manejar_desconexion(self, cliente, dificultad):
        if dificultad in self.partidas:
            self.partidas[dificultad]['clientes'].remove(cliente)
            self.broadcast(f"JUGADOR_DESCONECTADO", dificultad)
            cliente.close()

    # Valida si hay cupo en la partida según la dificultad
    def validar_partida(self, dificultad):
        max_jugadores = 2  # Cambiado a 2 para ambas dificultades
        if dificultad not in self.partidas:
            self.partidas[dificultad] = {
                'clientes': [],
                'matrix': Matrix(3 if dificultad == 'F' else 5),
                'max_jugadores': max_jugadores,
                'start_time': time.time()  # Nuevo: Registra inicio de la partida
            }
        return len(self.partidas[dificultad]['clientes']) < max_jugadores

    # Metodo para manejar cada cliente
    def handle_client(self, cliente):
        addr = cliente.getpeername() #Se va a ver los clientes en el servidor
        print(f"Nueva conexión aceptada desde: {addr}")
        
        try:
            dificultad = cliente.recv(1024).decode().strip().upper()
            if not self.validar_partida(dificultad):
                cliente.send("ERROR:Partida llena".encode())
                cliente.close()
                return

            # Agregar cliente a la partida
            partida = self.partidas[dificultad]
            partida['clientes'].append(cliente)
            self.broadcast(f"JUGADOR_CONECTADO:{len(partida['clientes'])}", dificultad)

            # Iniciar partida cuando esté completa
            if len(partida['clientes']) == partida['max_jugadores']:
                self.broadcast("INICIO", dificultad)
                self.iniciar_juego(dificultad)

        except Exception as e:
            print(f"Error: {e}")

    # Lógica principal del juego
    def iniciar_juego(self, dificultad):
        partida = self.partidas[dificultad]
        matrix = partida['matrix']
        jugadores = partida['clientes']
        turno = 0

        # Enviar el tablero vacío inicial a todos los clientes
        self.broadcast(f"ACTUALIZACION:{','.join(matrix.matriz)}", dificultad)

        while True:
            jugador_actual = jugadores[turno % len(jugadores)]
            try:
                jugador_actual.send("TURNO\n".encode())
                movimiento = jugador_actual.recv(1024).decode().strip()

                # Validar movimiento
                if not matrix.es_movimiento_valido(movimiento):
                    jugador_actual.send("ERROR:Movimiento inválido\n".encode())
                    continue

                # Actualizar tablero y notificar
                simbolo = 'X' if turno % 2 == 0 else 'O'
                matrix.agregar(simbolo, movimiento)
                self.broadcast(f"ACTUALIZACION:{','.join(matrix.matriz)}", dificultad)

                # Verificar victoria/empate
                if matrix.ganador(simbolo):
                    self.broadcast(f"GANADOR:{simbolo}", dificultad)
                    break
                elif matrix.empate():
                    self.broadcast("EMPATE", dificultad)
                    break

                turno += 1

            except:
                self.broadcast("DESCONEXION", dificultad)
                break

        # Cerrar partida
        del self.partidas[dificultad]
        for c in jugadores:
            c.close()
#Este metodo de aca inicializa los hilos para los clientes
    def start(self):
        while True:
            cliente, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(cliente,)).start()

class Matrix:
    def __init__(self, size):
        self.size = size
        self.matriz = [' ' for _ in range(size * size)]

    # Convierte posición (ej: A1) a índice
    def cast(self, pos):
        if len(pos) != 2:
            raise ValueError("Formato inválido")
        letra = pos[0].upper()
        num = pos[1]
        letras_validas = 'ABCDE'[:self.size]
        if letra not in letras_validas or not num.isdigit():
            raise ValueError("Posición inválida")
        fila = int(num) - 1
        columna = letras_validas.index(letra)
        return fila * self.size + columna

    # Añade un símbolo al tablero
    def agregar(self, simbolo, pos):
        idx = self.cast(pos)
        if self.matriz[idx] == ' ':
            self.matriz[idx] = simbolo

    # Verifica si el movimiento es válido
    def es_movimiento_valido(self, pos):
        try:
            idx = self.cast(pos)
            return self.matriz[idx] == ' '
        except:
            return False

    # Comprueba si hay un ganador
    def ganador(self, simbolo):
        # Filas y columnas
        for i in range(self.size):
            if all(self.matriz[i*self.size + j] == simbolo for j in range(self.size)):
                return True
            if all(self.matriz[j*self.size + i] == simbolo for j in range(self.size)):
                return True
        # Diagonales
        diag1 = all(self.matriz[i*self.size + i] == simbolo for i in range(self.size))
        diag2 = all(self.matriz[i*self.size + (self.size-1-i)] == simbolo for i in range(self.size))
        return diag1 or diag2

    # Verifica empate
    def empate(self):
        return ' ' not in self.matriz

if __name__ == "__main__":
    servidor = Server()
    servidor.start()