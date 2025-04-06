import socket

HOST = "192.168.1.13"  # Dirección del servidor
PORT = 65431  # Puerto del servidor

class Client:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((HOST, PORT))
        print("Connected to server!")

    def enviar(self, mensaje):
        self.server.send(mensaje.encode())

    def recibir(self):
        return self.server.recv(1024).decode()

    def cerrar(self):
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

    def es_movimiento_valido(self, pos):
        try:
            pos_index = self.cast(pos)
            return self.matriz[pos_index] == ' '
        except:
            return False

def main():
    cliente = Client()
    
    # Selección de dificultad
    difficulty = input("Selecciona dificultad (Fácil/Avanzado) [F/A]: ").upper()
    while difficulty not in ('F', 'A'):
        print("Opción inválida. Usa F para Fácil o A para Avanzado.")
        difficulty = input("Selecciona dificultad [F/A]: ").upper()
    cliente.enviar(difficulty)
    
    size = 3 if difficulty == 'F' else 5
    matrix = Matrix(size)
    matrix.mostrar()

    while True:
        print("\tEs tu turno.")
        valid_letters = 'ABCDE'[:size]
        valid_numbers = [str(i+1) for i in range(size)]
        
        while True:
            charpos = input(f"Ingresa posición (Ej: {valid_letters[0]}{valid_numbers[0]}): ").upper()
            if len(charpos) == 2 and charpos[0] in valid_letters and charpos[1] in valid_numbers:
                if matrix.es_movimiento_valido(charpos):
                    break
                else:
                    print("Posición ocupada. Intenta otra.")
            else:
                print(f"Formato incorrecto. Usa {valid_letters} y {valid_numbers}.")
        
        matrix.agregar('X', charpos)
        cliente.enviar(charpos)

        respuesta = cliente.recibir()
        if respuesta == "GANASTE":
            print("¡Ganaste!")
            break
        elif respuesta == "EMPATE":
            print("¡Empate!")
            break
            
        matrix.agregar('O', respuesta)
        
        # Verificar si el servidor ganó
        if all(cell != ' ' for cell in matrix.matriz):
            print("¡Empate!")
            break

    cliente.cerrar()

if __name__ == "__main__":
    main()