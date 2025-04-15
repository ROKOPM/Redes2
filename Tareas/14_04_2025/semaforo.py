import logging
import threading
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )


class ActivePool:
    def __init__(self):
        self.active = []
        self.lock = threading.Lock()

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            logging.debug('Ejecutando append: %s', self.active)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            logging.debug('Ejecutando remove: %s', self.active)


def worker(s, pool, numero_tabla):
    logging.debug('Esperando para acceder al grupo')
    with s:
        logging.debug("Adquirí el semáforo")
        name = threading.currentThread().getName()
        pool.makeActive(name)

       
        logging.info(f"Tabla del {numero_tabla}")
        for i in range(1, 11):
            resultado = numero_tabla * i
            print(f"{numero_tabla} x {i} = {resultado}")
            time.sleep(0.05)  

        pool.makeInactive(name)
        logging.debug("Haciendo el release del semáforo")



pool = ActivePool()
s = threading.Semaphore(2)  # dos tablas por ciclo
threads = []


for n in range(1, 12):
    t = threading.Thread(target=worker, name=f"Hilo-{n}", args=(s, pool, n))
    threads.append(t)
    t.start()

# Esperamos que todos los hilos terminen
for t in threads:
    t.join()

print("¡Todas las tablas han sido mostradas!")
