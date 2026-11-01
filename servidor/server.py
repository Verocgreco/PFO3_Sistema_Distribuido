import socket
import threading
import queue
import json

from worker import worker

# Configuración del servidor
HOST = "127.0.0.1"
PUERTO = 5001
CANTIDAD_WORKERS = 3

# Cola compartida de tareas
cola_tareas = queue.Queue()

# Evento para controlar el apagado
apagando = threading.Event()

# Listas para controlar los hilos
hilos_workers = []
hilos_clientes = []


def recibir_mensaje(conexion):
    """Recibe un mensaje completo delimitado por salto de línea."""

    datos = bytearray()

    while True:
        fragmento = conexion.recv(1024)

        if not fragmento:
            raise ConnectionError("El cliente cerró la conexión.")

        datos.extend(fragmento)

        if b"\n" in datos:
            mensaje, resto = datos.split(b"\n", 1)

            if resto:
                raise ValueError("Se recibieron datos adicionales.")

            return mensaje.decode("utf-8")

        if len(datos) > 4096:
            raise ValueError("El mensaje supera el tamaño permitido.")


def atender_cliente(conexion, direccion):
    """Atiende solicitudes de clientes."""

    print(f"Cliente conectado: {direccion}")

    try:
        datos = recibir_mensaje(conexion)
        solicitud = json.loads(datos)

        if not isinstance(solicitud, dict):
            raise ValueError("La solicitud debe ser un objeto JSON.")

        # Comprobar si el cliente solicita detener el servidor
        if solicitud.get("accion") == "detener":

            respuesta = {
                "mensaje": "Solicitud de apagado recibida."
            }

            conexion.sendall(
                (json.dumps(respuesta) + "\n").encode("utf-8")
            )

            print("Se recibió una solicitud de apagado.")
            apagando.set()
            return

        # Validar la tarea
        identificador = solicitud.get("id")
        descripcion = solicitud.get("descripcion")

        if (
            not isinstance(identificador, int)
            or isinstance(identificador, bool)
            or not isinstance(descripcion, str)
            or not descripcion.strip()
        ):
            raise ValueError(
                "La tarea debe tener un ID entero y una descripción válida."
            )

        if apagando.is_set():
            raise ValueError("El servidor está en proceso de apagado.")

        # Crear evento de sincronización
        evento = threading.Event()

        tarea = {
            "id": identificador,
            "descripcion": descripcion,
            "resultado": None,
            "evento": evento
        }

        # Enviar tarea a la cola
        cola_tareas.put(tarea)

        # Esperar a que termine el procesamiento
        evento.wait()

        # Enviar resultado
        respuesta = json.dumps(
            tarea["resultado"],
            ensure_ascii=False
        )

        conexion.sendall((respuesta + "\n").encode("utf-8"))

        print(f"Tarea {identificador} respondida a {direccion}")

    except (json.JSONDecodeError, ValueError, ConnectionError) as error:
        try:
            respuesta = json.dumps({"error": str(error)})
            conexion.sendall((respuesta + "\n").encode("utf-8"))
        except OSError:
            pass

    except OSError as error:
        print(f"Error de conexión con {direccion}: {error}")

    finally:
        conexion.close()


# Crear e iniciar los workers
for numero in range(1, CANTIDAD_WORKERS + 1):

    hilo = threading.Thread(
        target=worker,
        args=(numero, cola_tareas)
    )

    hilo.start()
    hilos_workers.append(hilo)


# Crear el servidor TCP
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

servidor.bind((HOST, PUERTO))
servidor.listen()

# Permitir revisar periódicamente si se solicitó el apagado
servidor.settimeout(1)

print(f"Servidor escuchando en {HOST}:{PUERTO}")
print(f"Workers activos: {CANTIDAD_WORKERS}")


try:
    while not apagando.is_set():

        try:
            conexion, direccion = servidor.accept()

        except socket.timeout:
            continue

        hilo_cliente = threading.Thread(
            target=atender_cliente,
            args=(conexion, direccion)
        )

        hilo_cliente.start()
        hilos_clientes.append(hilo_cliente)

finally:
    print("\nDeteniendo servidor...")

    # Cerrar el socket de escucha
    servidor.close()

    # Esperar a que terminen las conexiones activas
    for hilo in hilos_clientes:
        hilo.join()

    # Esperar a que se procesen las tareas pendientes
    cola_tareas.join()

    # Enviar una señal de finalización a cada worker
    for _ in range(CANTIDAD_WORKERS):
        cola_tareas.put(None)

    # Esperar a que finalicen todos los workers
    for hilo in hilos_workers:
        hilo.join()

    print("Todos los workers finalizaron.")
    print("Servidor detenido correctamente.")
