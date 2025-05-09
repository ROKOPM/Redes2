import socket
import threading
import time
import string
from collections import deque

HOST = "192.168.1.16"
PORT = 65431

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        self.partidas = {}  # Diccionario para rastreo de partidas por dificultad
        self.hilos_activos = {}  # Diccionario para rastrear hilos
        self.lock = threading.Lock() #Aqui esta lock
        print("Servidor listo. Esperando conexiones...")

        # Hilo para monitorear partidas y hilos
        threading.Thread(target=self._monitorear_estados, daemon=True).start()

    def _monitorear_estados(self):
        """Monitorea partidas y estados de hilos cada 10 segundos"""
        while True:
            print("\n=== ESTADO ACTUAL DEL SERVIDOR ===")
            print(f"Hilos activos: {threading.active_count()}")

            # Mostrar información de cada hilo
            for hilo in threading.enumerate():
                print(f"  - Hilo {hilo.name} (ID: {hilo.ident}) - Estado: {'Activo' if hilo.is_alive() else 'Inactivo'}")

            # Mostrar estado de las partidas
            print("\nPartidas activas:")
            for dificultad, lista_partidas in self.partidas.items():
                for idx, partida in enumerate(lista_partidas):
                    estado = partida['estado']
                    jugadores = len(partida['clientes'])
                    print(f"  - {dificultad} (Sala {idx + 1}): {estado} ({jugadores}/{partida['max_jugadores']} jugadores)")
            
            #Cancelar partida tras tiempo de espera
                    if estado == 'espera_reconexion' and time.time() - partida['tiempo_espera'] > 60:
                        print(f"[!] La partida {dificultad} (Sala {idx + 1}) ha excedido el tiempo de espera. Cancelando...")
                        self.broadcast("PARTIDA_CANCELADA", partida)

                    # Cerrar todas las conexiones de los jugadores
                        for cliente in partida['clientes']:
                            try:
                                cliente.send("La partida ha sido cancelada por tiempo de espera.\n".encode())
                                cliente.close()
                            except:
                                pass
                    
                    # Eliminar la partida de la lista
                        self.partidas[dificultad].remove(partida)
                        print(f"Partida {dificultad} (Sala {idx + 1}) eliminada.")
                    
            print("=" * 40 + "\n")
            time.sleep(10)

    def broadcast(self, mensaje, partida):
        for cliente in partida['clientes']:
            try:
                cliente.send(f"{mensaje}\n".encode())
            except:
                self.manejar_desconexion(cliente, partida)

    def manejar_desconexion(self, cliente, partida):
        with self.lock:
            if cliente in partida['clientes']:
                partida['clientes'].remove(cliente)
                print(f"[!] Cliente desconectado. Jugadores restantes: {len(partida['clientes'])}")
                cliente.close()

            # Remover de la cola de turnos
                partida['turno_cola'] = deque([c for c in partida['turno_cola'] if c != cliente])

                if partida['estado'] == 'activa' and len(partida['clientes']) < partida['max_jugadores']:
                    partida['estado'] = 'espera_reconexion'
                    partida['tiempo_espera'] = time.time()
                    self.broadcast("JUGADOR_DESCONECTADO", partida)
                    print(f"[!] Partida en espera de reconexión (60s).")

    
    def obtener_partida_disponible(self, dificultad):
        with self.lock:
            max_jugadores = 4
            max_salas = 2

            if dificultad not in self.partidas:
                self.partidas[dificultad] = []

            for partida in self.partidas[dificultad]:
                if partida['estado'] != 'activa' and len(partida['clientes']) < max_jugadores:
                    return partida  # Hay una sala disponible

            if len(self.partidas[dificultad]) < max_salas:
                nueva_partida = {
                    'clientes': [],
                    'matrix': Matrix(8 if dificultad == 'F' else 12),
                    'max_jugadores': max_jugadores,
                    'inicio': time.time(),
                    'estado': 'creada',
                    'tiempo_espera': None,
                    'turno_cola': deque(),
                    'turno': 0
                }
                self.partidas[dificultad].append(nueva_partida)
                print(f"Partida nueva creada para dificultad {dificultad}. Total: {len(self.partidas[dificultad])} salas.")
                return nueva_partida

            return None  # No hay salas disponibles

    def handle_client(self, cliente):
        addr = cliente.getpeername()
        print(f"[+] Conexión aceptada desde {addr} (Hilo: {threading.current_thread().name})")

        try:
            cliente.send("Ingrese la dificultad (F/A): ".encode())
            dificultad = cliente.recv(1024).decode().strip().upper()
            partida = self.obtener_partida_disponible(dificultad)
            if not partida:
                cliente.send("ERROR: No hay partidas disponibles".encode())
                cliente.close()
                return

            partida['clientes'].append(cliente)
            partida['turno_cola'].append(cliente)
            print(f"[+] Jugador unido a {dificultad}. Total: {len(partida['clientes'])}")

            if len(partida['clientes']) == partida['max_jugadores']:
                partida['estado'] = 'activa'
                print(f"[*] Partida {dificultad} iniciada.")
                threading.Thread(target=self.iniciar_juego, args=(partida, dificultad), daemon=True).start()
            else:
                partida['estado'] = 'waiting'
                cliente.send("Esperando más jugadores...\n".encode())
                self.broadcast(f"Partida {dificultad} está en estado 'waiting'.", partida)

        except Exception as e:
            print(f"[ERROR] En handle_client: {e}")

    def iniciar_juego(self, partida, dificultad):
        matrix = partida['matrix']
        jugadores = partida['clientes']

        # Asignar símbolos a cada jugador y almacenarlos
        simbolos_list = ['X', 'O', '!', '$']
        partida['simbolos'] = {}
        for i, jugador in enumerate(jugadores):
            partida['simbolos'][jugador] = simbolos_list[i]
            try:
                jugador.send(f"Partida iniciada! Tu símbolo es: {simbolos_list[i]}\n".encode())
            except:
                self.manejar_desconexion(jugador, partida)

        self.broadcast("INICIO", partida)
        self.broadcast(f"ACTUALIZACION:{','.join(matrix.matriz)}", partida)

        while partida['estado'] == 'activa':
            # Si la cola está vacía
            if not partida['turno_cola']:  
                break

            jugador_actual = partida['turno_cola'][0]
            try:
                jugador_actual.send("TURNO\n".encode())
                movimiento = jugador_actual.recv(1024).decode().strip()

                if not matrix.es_movimiento_valido(movimiento):
                    jugador_actual.send("ERROR:Movimiento inválido\n".encode())
                    continue

                simbolo = partida['simbolos'][jugador_actual]
                matrix.agregar(simbolo, movimiento)
                self.broadcast(f"ACTUALIZACION:{','.join(matrix.matriz)}", partida)

                if matrix.ganador(simbolo):
                    self.broadcast(f"GANADOR:{simbolo}", partida)
                    break
                elif matrix.empate():
                    self.broadcast("EMPATE", partida)
                    break

                # Rotar al siguiente jugador
                partida['turno_cola'].rotate(-1)

            except:
                self.manejar_desconexion(jugador_actual, partida)
                if partida['estado'] != 'activa':
                    break

        if partida['estado'] == 'activa':
            # Cerrar conexiones y limpiar
            for c in jugadores:
                try:
                    c.close()
                except:
                    pass
            self.partidas[dificultad].remove(partida)
            print(f"Partida {dificultad} finalizada.")

    def start(self):
        while True:
            try:
                cliente, addr = self.server.accept()
                hilo = threading.Thread(target=self.handle_client, args=(cliente,))
                hilo.start()
                self.hilos_activos[hilo.ident] = hilo  # Registrar hilo
            except KeyboardInterrupt:
                print("\n[!] Cierre del servidor solicitado por el usuario.")
                self.cerrar_servidor()
                break

    def cerrar_servidor(self):
        self.server.close()
        print("Servidor cerrado.")

class Matrix:
    def __init__(self, size):
        self.size = size
        self.matriz = [' ' for _ in range(size * size)]

    def cast(self, pos):
        if len(pos) < 2 or len(pos) > 3:
            raise ValueError("Formato inválido")
        letra = pos[0].upper()
        num = pos[1:]
        
        #Validar columnas
        letras_validas = string.ascii_uppercase [:self.size]
        if letra not in letras_validas:
            raise ValueError("Posición inválida: columna fuera de rango")
        
        #Validar filas
        if not num.isdigit() or not (1 <= int(num) <= self.size):
            raise ValueError("Posición inválida: fila fuera de rango")
        
        fila = int(num) - 1
        columna = letras_validas.index(letra)
        return fila * self.size + columna

    def agregar(self, simbolo, pos):
        idx = self.cast(pos)
        if self.matriz[idx] == ' ':
            self.matriz[idx] = simbolo

    def es_movimiento_valido(self, pos):
        try:
            idx = self.cast(pos)
            return self.matriz[idx] == ' '
        except ValueError:
            return False

    def ganador(self, simbolo):
        objetivo = 4 if self.size == 8 else 6

        #horizontal
        for fila in range(self.size):
            contador = 0
            for col in range(self.size):
                idx = fila * self.size + col
                if self.matriz[idx] == simbolo:
                    contador += 1
                    if contador >= objetivo:
                        return True
                else:
                    contador = 0

        #vertical
        for col in range(self.size):
            contador = 0
            for fila in range(self.size):
                idx = fila * self.size + col
                if self.matriz[idx] == simbolo:
                    contador += 1
                    if contador >= objetivo:
                        return True
                else:
                    contador = 0

        #diagonal (de izquierda arriba a derecha abajo)
        for fila in range(self.size - objetivo + 1):
            for col in range(self.size - objetivo + 1):
                contador = 0
                for k in range(objetivo):
                    idx = (fila + k) * self.size + (col + k)
                    if self.matriz[idx] == simbolo:
                        contador += 1
                        if contador >= objetivo:
                            return True
                    else:
                        break

        # diagonal (de derecha arriba a izquierda abajo)
        for fila in range(self.size - objetivo + 1):
            for col in range(objetivo - 1, self.size):
                contador = 0
                for k in range(objetivo):
                    idx = (fila + k) * self.size + (col - k)
                    if self.matriz[idx] == simbolo:
                        contador += 1
                        if contador >= objetivo:
                            return True
                    else:
                        break

        return False

    def empate(self):
        return ' ' not in self.matriz

if __name__ == "__main__":
    servidor = Server()
    servidor.start()
