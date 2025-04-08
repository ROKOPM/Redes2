import threading
import logging
import time
import random

caracter = ""
lock = threading.Lock()
resultados = {}  # Guardar si cada hilo entró o no, y cuántos intentos hizo

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )


def worker():
    global caracter
    intentos = 0
    exito = False
    nombre = threading.current_thread().name

    for _ in range(10):
        if lock.acquire(blocking=False):
            try:
                logging.debug("Entré en la sección crítica")
                caracter = nombre
                time.sleep(random.randint(1, 3))  # Simula trabajo
                exito = True
                break
            finally:
                lock.release()
                logging.debug("Salí de la sección crítica - valor de caracter: %s", caracter)
        else:
            intentos += 1
            logging.debug("No pude entrar. Intento fallido #%d", intentos)
            time.sleep(2)

    if not exito:
        logging.debug("No logré acceder a la sección crítica tras %d intentos", intentos)

    # Guardamos el resultado de este hilo
    resultados[nombre] = {"exito": exito, "intentos": intentos}


# Crear varios hilos
hilos = []
for i in range(5):  # Puedes cambiar la cantidad de hilos aquí
    t = threading.Thread(target=worker, name=f"Hilo-{i+1}")
    hilos.append(t)
    t.start()

# Esperar a que terminen
for t in hilos:
    t.join()

# Mostrar resumen final
print("\n=== RESUMEN FINAL ===")
for nombre, datos in resultados.items():
    estado = "Accedió" if datos["exito"] else "No accedió"
    print(f"{nombre}: {estado}, intentos realizados: {datos['intentos']}")
print(f"Último valor de 'caracter': {caracter}")
