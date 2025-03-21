import threading
import time
import random
#holis
class CuentaBancaria:
    def __init__(self):
        self.saldo = 0
        self.lock = threading.Lock()

    def ingresar(self, cantidad):
        with self.lock:
            self.saldo += cantidad
            print(f"[{threading.current_thread().name}] Deposito de {cantidad} realizado. Saldo actual: {self.saldo}")

    def retirar(self, cantidad):
        with self.lock:
            if self.saldo >= cantidad:
                self.saldo -= cantidad
                print(f"[{threading.current_thread().name}] Retiro de {cantidad} realizado. Saldo actual: {self.saldo}")
            else:
                print(f"[{threading.current_thread().name}] Fondos insuficientes para retirar {cantidad}. Saldo actual: {self.saldo}")

    def consultar_saldo(self):
        with self.lock:
            print(f"[{threading.current_thread().name}] Consulta de saldo: {self.saldo}")

# Instancia de la cuenta bancaria
cuenta = CuentaBancaria()

# Funciones para los hilos
def depositar():
    for _ in range(5):
        cantidad = random.randint(3, 100)
        cuenta.ingresar(cantidad)
        time.sleep(random.uniform(0.1, 0.5))

def retirar():
    for _ in range(5):
        cantidad = random.randint(3, 100)
        cuenta.retirar(cantidad)
        time.sleep(random.uniform(0.1, 0.8))


def consultar():
    for _ in range(5):
        cuenta.consultar_saldo()
        time.sleep(random.uniform(0.1, 0.5))

# Creación de los hilos
hilo_deposito = threading.Thread(target=depositar, name= "Hilo_Depositos")
hilo_retiro = threading.Thread(target=retirar, name= "Hilo_Retiros")
hilo_consulta = threading.Thread(target=consultar, name= "Hilo_Consultas")

# Iniciar los hilos
hilo_deposito.start()
hilo_retiro.start()
hilo_consulta.start()

# Esperar a que los hilos terminen
hilo_deposito.join()
hilo_retiro.join()
hilo_consulta.join()

print("Operaciones finalizadas.")
