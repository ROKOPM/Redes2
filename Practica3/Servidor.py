import socket
import threading
import time

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

            print("=" * 40 + "\n")
            time.sleep(10)

    def broadcast(self, mensaje, partida):
        for cliente in partida['clientes']:
            try:
                cliente.send(f"{mensaje}\n".encode())
            except:
                self.manejar_desconexion(cliente, partida)

    def manejar_desconexion(self, cliente, partida):
        if cliente in partida['clientes']:
            partida['clientes'].remove(cliente)
            print(f"[!] Cliente desconectado. Jugadores restantes: {len(partida['clientes'])}")
            cliente.close()

            if partida['estado'] == 'activa' and len(partida['clientes']) < partida['max_jugadores']:
                partida['estado'] = 'espera_reconexion'
                partida['tiempo_espera'] = time.time()
                self.broadcast("JUGADOR_DESCONECTADO", partida)
                print(f"[!] Partida en espera de reconexión (60s).")

    def obtener_partida_disponible(self, dificultad):
        max_jugadores = 2
        max_salas = 5

        if dificultad not in self.partidas:
            self.partidas[dificultad] = []

        for partida in self.partidas[dificultad]:
            if partida['estado'] != 'activa' and len(partida['clientes']) < max_jugadores:
                return partida  # Hay una sala disponible

        if len(self.partidas[dificultad]) < max_salas:
            nueva_partida = {
                'clientes': [],
                'matrix': Matrix(3 if dificultad == 'F' else 5),
                'max_jugadores': max_jugadores,
                'inicio': time.time(),
                'estado': 'creada',
                'tiempo_espera': None,
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
            cliente.send("Ingrese la dificultad (F/M/D): ".encode())
            dificultad = cliente.recv(1024).decode().strip().upper()
            partida = self.obtener_partida_disponible(dificultad)
            if not partida:
                cliente.send("ERROR: No hay partidas disponibles".encode())
                cliente.close()
                return

            partida['clientes'].append(cliente)
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
        turno = partida['turno']

        self.broadcast("INICIO", partida)
        self.broadcast(f"ACTUALIZACION:{','.join(matrix.matriz)}", partida)

        while partida['estado'] == 'activa':
            jugador_actual = jugadores[turno % 2]
            try:
                jugador_actual.send("TURNO\n".encode())
                movimiento = jugador_actual.recv(1024).decode().strip()

                if not matrix.es_movimiento_valido(movimiento):
                    jugador_actual.send("ERROR:Movimiento inválido\n".encode())
                    continue

                simbolo = 'X' if turno % 2 == 0 else 'O'
                matrix.agregar(simbolo, movimiento)
                self.broadcast(f"ACTUALIZACION:{','.join(matrix.matriz)}", partida)

                if matrix.ganador(simbolo):
                    self.broadcast(f"GANADOR:{simbolo}", partida)
                    break
                elif matrix.empate():
                    self.broadcast("EMPATE", partida)
                    break

                turno += 1
                partida['turno'] = turno

            except:
                self.manejar_desconexion(jugador_actual, partida)
                if partida['estado'] != 'activa':
                    break

        if partida['estado'] == 'activa':
            # Solo se elimina si terminó normalmente
            for c in jugadores:
                try:
                    c.close()
                except:
                    pass
            self.partidas[dificultad].remove(partida)
            print(f"Partida {dificultad} finalizada.")
        else:
            print(f"Partida {dificultad} en espera de reconexión. No se eliminará.")

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

    def agregar(self, simbolo, pos):
        idx = self.cast(pos)
        if self.matriz[idx] == ' ':
            self.matriz[idx] = simbolo

    def es_movimiento_valido(self, pos):
        try:
            idx = self.cast(pos)
            return self.matriz[idx] == ' '
        except:
            return False

    def ganador(self, simbolo):
        for i in range(self.size):
            if all(self.matriz[i * self.size + j] == simbolo for j in range(self.size)):
                return True
            if all(self.matriz[j * self.size + i] == simbolo for j in range(self.size)):
                return True
        diag1 = all(self.matriz[i * self.size + i] == simbolo for i in range(self.size))
        diag2 = all(self.matriz[i * self.size + (self.size - 1 - i)] == simbolo for i in range(self.size))
        return diag1 or diag2

    def empate(self):
        return ' ' not in self.matriz

if __name__ == "__main__":
    servidor = Server()
    servidor.start()
