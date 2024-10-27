import subprocess
import re
from prometheus_client import start_http_server, Gauge
import time

# Puertos a monitorear
puertos_a_monitorear = [3000, 8080]  # Cambia estos puertos según sea necesario

# Crear métricas para Prometheus
conexiones_por_estado = {port: {} for port in puertos_a_monitorear}
for port in puertos_a_monitorear:
    conexiones_por_estado[port] = {
        'time_wait': Gauge(f'conexiones_time_wait_{port}', f'Conexiones TIME_WAIT en el puerto {port}'),
        'established': Gauge(f'conexiones_established_{port}', f'Conexiones ESTABLISHED en el puerto {port}'),
        'close_wait': Gauge(f'conexiones_close_wait_{port}', f'Conexiones CLOSE_WAIT en el puerto {port}'),
    }

# Inicia el servidor de Prometheus
start_http_server(8000)


def obtener_conexiones_netstat():
    # Ejecuta el comando netstat y captura la salida
    result = subprocess.run(
        ['netstat', '-n'], stdout=subprocess.PIPE, text=True)
    return result.stdout


def monitorear_puertos():
    # Llama a netstat y analiza la salida
    salida_netstat = obtener_conexiones_netstat()

    for port in puertos_a_monitorear:
        estados = {'TIME_WAIT': 0, 'ESTABLISHED': 0, 'CLOSE_WAIT': 0}

        # Busca líneas que contengan el puerto monitoreado
        for linea in salida_netstat.splitlines():
            if f':{port}' in linea:
                # Usamos una expresión regular para identificar el estado de la conexión
                match = re.search(r'\s+([A-Z]+)\s+', linea)
                if match:
                    estado = match.group(1)
                    if estado in estados:
                        estados[estado] += 1

        # Actualiza las métricas para cada puerto
        conexiones_por_estado[port]['time_wait'].set(estados['TIME_WAIT'])
        conexiones_por_estado[port]['established'].set(estados['ESTABLISHED'])
        conexiones_por_estado[port]['close_wait'].set(estados['CLOSE_WAIT'])


# Loop para actualizar las métricas cada 5 segundos
while True:
    monitorear_puertos()
    time.sleep(5)
