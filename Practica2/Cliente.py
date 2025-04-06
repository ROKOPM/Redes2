import socket

HOST = "192.168.1.13"
PORT = 65431
#La config de cliente
class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        print("Conectado al servidor. Esperando jugadores...")

    def enviar(self, mensaje):
        self.sock.send(mensaje.encode())

    def recibir(self):
        return self.sock.recv(1024).decode()

    def cerrar(self):
        self.sock.close()
        
#Dibuja la matriz necesaria segun la dificultad en base al size enviado
class Matrix:
    def __init__(self, size):
        self.size = size
        self.matriz = [' ' for _ in range(size * size)]

    def mostrar(self):
        print("\n" + "="*30)
        letras = 'ABCDE'[:self.size]
        print("\t\t  " + "   ".join(letras))
        for i in range(0, len(self.matriz), self.size):
            fila = self.matriz[i:i+self.size]
            print(f"\t\t{(i//self.size)+1} " + " | ".join(fila))
            if i + self.size < len(self.matriz):
                print("\t\t  " + "-"*(self.size*3-1))

#Dibuja las posicones
    def agregar(self, elemento, pos):
        try:
            pos_index = self.cast(pos)
            if self.matriz[pos_index] == ' ':
                self.matriz[pos_index] = elemento
            self.mostrar()
        except ValueError as e:
            print(f"Error: {e}")

#Manejo de errores en caso de que introduzcas un valor no valido
    def cast(self, pos):
        if len(pos) != 2:
            raise ValueError("Formato debe ser LetraNúmero (Ej: A1)")
        letra = pos[0].upper()
        num = pos[1]
        letras_validas = 'ABCDE'[:self.size]
        if letra not in letras_validas or not num.isdigit():
            raise ValueError("Posición inválida")
        fila = int(num) - 1
        col = letras_validas.index(letra)
        if fila < 0 or fila >= self.size:
            raise ValueError("Fila inválida")
        return fila * self.size + col

    def es_movimiento_valido(self, pos):
        try:
            pos_index = self.cast(pos)
            return self.matriz[pos_index] == ' '
        except ValueError:
            return False

def main():
    cliente = Client()
    
    # Selección y validación de dificultad
    difficulty = ''
    while difficulty not in ('F', 'A'):
        difficulty = input("Selecciona dificultad [Fácil/Avanzado] (F/A): ").upper()
        if difficulty not in ('F', 'A'):
            print("Opción inválida. Intenta nuevamente.")
    
    cliente.enviar(difficulty)
    size = 3 if difficulty == 'F' else 5
    
    try:
        inicio = cliente.recibir()
        if inicio != "INICIO":
            raise ConnectionError("Error de sincronización con el servidor")
        
        matrix = Matrix(size)
        matrix.mostrar()

        while True:
            print("\n<<< TU TURNO >>>")
            valid_letras = 'ABCDE'[:size]
            valid_nums = [str(i+1) for i in range(size)]
            
            # Validación de entrada
            while True:
                movimiento = input(f"Ingresa posición ({valid_letras[0]}1-{valid_letras[-1]}{size}): ").upper()
                if matrix.es_movimiento_valido(movimiento):
                    break
                print("Movimiento inválido o posición ocupada!")
            
            matrix.agregar('X', movimiento)
            cliente.enviar(movimiento)

            respuesta = cliente.recibir()
            if respuesta in ("GANASTE", "EMPATE", "PERDISTE"):
                print(f"\n*** {respuesta} ***")
                break
                
            matrix.agregar('O', respuesta)
            print("\n<<< MOVIMIENTO DEL SERVIDOR >>>")

    except (ConnectionError, ConnectionAbortedError) as e:
        print(f"\nError de conexión: {e}")
    finally:
        cliente.cerrar()

if __name__ == "__main__":
    main()