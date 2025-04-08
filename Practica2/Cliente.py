import socket

HOST = "192.168.1.13"
PORT = 65431

class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.buffer = ""
        
        # Selección de dificultad
        while True:
            dificultad = input("Dificultad [Fácil(F)/Avanzado(A)]: ").upper()
            if dificultad in ('F', 'A'):
                break
        self.sock.send(dificultad.encode())
        
        # Verificar respuesta del servidor
        respuesta = self.sock.recv(1024).decode()
        if respuesta.startswith("ERROR"):
            print(respuesta.split(":")[1])
            exit()

    # Envía un mensaje al servidor
    def enviar(self, mensaje):
        self.sock.send(mensaje.encode())

    # Recibe un mensaje del servidor
    def recibir(self):
        while True:
            if "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                return line
            data = self.sock.recv(1024).decode()
            if not data:
                return None
            self.buffer += data

    # Cierra la conexión
    def cerrar(self):
        self.sock.close()

class Matrix:
    def __init__(self, size):
        self.size = size
        self.matriz = [' ' for _ in range(size * size)]

    # Muestra el tablero
    def mostrar(self):
        letras = 'ABCDE'[:self.size]
        print("\nTablero:")
        print("\t   " + "   ".join(letras))
        for i in range(0, len(self.matriz), self.size):
            fila = self.matriz[i:i+self.size]
            print(f"\t{i//self.size + 1}  " + " | ".join(fila))
            if i + self.size < len(self.matriz):
                print("\t  " + "-"*(self.size*4 - 1))

#Envios del cliente para el servidor
def main():
    cliente = Client()
    matrix = None

    try:
        while True:
            mensaje = cliente.recibir()
            if not mensaje:
                break
            if mensaje == "INICIO":
                print("¡Partida iniciada!")
            elif mensaje.startswith("ACTUALIZACION:"):
                matriz_str = mensaje.split(":")[1].split(",")
                if not matrix:
                    size = int(len(matriz_str)**0.5)
                    matrix = Matrix(size)
                matrix.matriz = matriz_str
                matrix.mostrar()
            elif mensaje == "TURNO":
                movimiento = input("Tu turno (ej: A1): ").upper()
                cliente.enviar(movimiento)
            elif mensaje.startswith("GANADOR:"):
                print(f"¡GANADOR: {mensaje.split(':')[1]}!")
                break
            elif mensaje == "EMPATE":
                print("¡Empate!")
                break
            elif mensaje == "JUGADOR_DESCONECTADO":
                print("¡Un jugador se desconectó! Esperando a que alguien se una para reiniciar la partida...")
                matrix = None  # Limpiar el tablero
            # timeout del servidor
            elif mensaje == "No se encontraron mas jugadores":
                print("No se encontraron mas jugadores")
                break
    finally:
        cliente.cerrar()

if __name__ == "__main__":
    main()