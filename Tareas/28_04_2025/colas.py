import logging
import threading
import time
import queue

# Configuración del logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )

# Crear una cola con capacidad limitada
TAMANO_BUFFER = 10
buffer = queue.Queue(maxsize=TAMANO_BUFFER)

# Bandera para indicar si la producción ha terminado
produccion_terminada = threading.Event()

def consumidor():
    """Consume elementos del buffer (cola)"""
    logging.debug('Iniciando hilo consumidor')
    nombre = threading.current_thread().name

    while True:
        try:
            # Intentar obtener un elemento con timeout
            elemento = buffer.get(timeout=1)
            logging.debug(f'{nombre}: Consumiendo elemento {elemento}. Elementos en buffer: {buffer.qsize()}')
            buffer.task_done()
            time.sleep(0.5)  # Simular tiempo de consumo
        except queue.Empty:
            if produccion_terminada.is_set() and buffer.empty():
                logging.debug(f'{nombre}: Producción terminada y buffer vacío. Saliendo.')
                break

def productor():
    """Produce elementos y los coloca en el buffer (cola)"""
    logging.debug('Iniciando hilo productor')

    for i in range(1, 16):
        buffer.put(i)  # Bloquea si la cola está llena
        logging.debug(f'Productor: Produciendo elemento {i}. Elementos en buffer: {buffer.qsize()}')
        time.sleep(0.3)  # Simular tiempo de producción
    
    produccion_terminada.set()
    logging.debug('Productor: Producción terminada.')

# Crear hilos
c1 = threading.Thread(name='Consumidor 1', target=consumidor)
c2 = threading.Thread(name='Consumidor 2', target=consumidor)
p = threading.Thread(name='Productor', target=productor)

# Iniciar hilos
c1.start()
time.sleep(1)  # Esperar un poco antes de iniciar el segundo consumidor
c2.start()
time.sleep(1)  # Esperar un poco antes de iniciar el productor
p.start()

# Esperar a que todos los hilos terminen
p.join()
c1.join()
c2.join()

logging.debug('Todos los hilos han terminado')
