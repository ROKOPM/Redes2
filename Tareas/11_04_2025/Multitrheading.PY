import logging
import threading
import time

# Configuración del logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s (%(threadName)-2s) %(message)s',
                    )

# Tamaño del buffer
TAMANO_BUFFER = 10
# Contador para elementos en el buffer
elementos_en_buffer = 0
# Bandera para indicar si la producción ha terminado
produccion_terminada = False
# Crear condición y lock
cond = threading.Condition()

def consumidor():
    """Espera la condición y consume elementos del buffer"""
    global elementos_en_buffer, produccion_terminada
    
    logging.debug('Iniciando hilo consumidor')
    nombre = threading.currentThread().name
    
    with cond:
        while True:
            # Esperar mientras el buffer esté vacío y la producción no haya terminado
            while elementos_en_buffer == 0 and not produccion_terminada:
                logging.debug(f'{nombre}: Buffer vacío, esperando...')
                cond.wait()
            
            # Si el buffer está vacío y la producción terminó, salir
            if elementos_en_buffer == 0 and produccion_terminada:
                logging.debug(f'{nombre}: Producción terminada y buffer vacío. Saliendo.')
                break
                
            # Consumir un elemento
            elementos_en_buffer -= 1
            logging.debug(f'{nombre}: Consumiendo elemento. Elementos en buffer: {elementos_en_buffer}')
            
            # Notificar al productor que hay espacio disponible
            cond.notify_all()
            
            # Simular tiempo de consumo
            time.sleep(0.5)

def productor():
    """Produce elementos y los coloca en el buffer"""
    global elementos_en_buffer, produccion_terminada
    
    logging.debug('Iniciando hilo productor')
    
    # Simular producción de 15 elementos (más que el tamaño del buffer)
    for i in range(1, 16):
        with cond:
            # Esperar si el buffer está lleno
            while elementos_en_buffer >= TAMANO_BUFFER:
                logging.debug(f'Productor: Buffer lleno ({elementos_en_buffer}), esperando...')
                cond.wait()
            
            # Producir un elemento
            elementos_en_buffer += 1
            logging.debug(f'Productor: Produciendo elemento {i}. Elementos en buffer: {elementos_en_buffer}')
            
            # Notificar a los consumidores que hay elementos disponibles
            cond.notify_all()
            
            # Simular tiempo de producción
            time.sleep(0.3)
    
    # Marcar que la producción ha terminado
    with cond:
        produccion_terminada = True
        logging.debug('Productor: Producción terminada. Notificando a los consumidores.')
        cond.notify_all()

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
