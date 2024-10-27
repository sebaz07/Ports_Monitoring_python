import psutil
from prometheus_client import start_http_server, Gauge, Info
import time
import os

# Definir puertos a monitorear
puertos_a_monitorear = list(
    map(int, os.getenv('PUERTOS_A_MONITOREAR', '3000,8080').split(',')))

# Crear métricas para Prometheus
conexiones_por_estado = {port: {} for port in puertos_a_monitorear}
for port in puertos_a_monitorear:
    conexiones_por_estado[port] = {
        'time_wait': Gauge(f'conexiones_time_wait_{port}', f'Conexiones TIME_WAIT en el puerto {port}'),
        'established': Gauge(f'conexiones_established_{port}', f'Conexiones ESTABLISHED en el puerto {port}'),
        'close_wait': Gauge(f'conexiones_close_wait_{port}', f'Conexiones CLOSE_WAIT en el puerto {port}'),
        'total': Gauge(f'conexiones_total_{port}', f'Total de conexiones en el puerto {port}'),
        'estado_actual': Info(f'estado_actual_{port}', f'Estado actual del puerto {port}')
    }

# Inicializa el servidor de Prometheus en un puerto (por ejemplo, 8000)
prometheus_port = int(os.getenv('PROMETHEUS_PORT', '8000'))
start_http_server(prometheus_port)

# Función para monitorear los puertos


def monitorear_puertos():
    try:
        for port in puertos_a_monitorear:
            estados = {'TIME_WAIT': 0, 'ESTABLISHED': 0, 'CLOSE_WAIT': 0}

            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port and conn.status in estados:
                    estados[conn.status] += 1

            total_conexiones = sum(estados.values())
            conexiones_por_estado[port]['time_wait'].set(estados['TIME_WAIT'])
            conexiones_por_estado[port]['established'].set(
                estados['ESTABLISHED'])
            conexiones_por_estado[port]['close_wait'].set(
                estados['CLOSE_WAIT'])
            conexiones_por_estado[port]['total'].set(total_conexiones)

            # Actualizar el estado actual del puerto
            estado_actual = {
                'TIME_WAIT': str(estados['TIME_WAIT']),
                'ESTABLISHED': str(estados['ESTABLISHED']),
                'CLOSE_WAIT': str(estados['CLOSE_WAIT']),
                'TOTAL': str(total_conexiones)
            }
            conexiones_por_estado[port]['estado_actual'].info(estado_actual)

    except Exception as e:
        print(f"Error al monitorear puertos: {e}")


# Loop para actualizar las métricas cada 5 segundos
while True:
    monitorear_puertos()
    time.sleep(5)
