import time


def worker(numero, cola_tareas):
    """Obtiene tareas de la cola y las procesa."""

    print(f"Worker {numero} iniciado.")

    while True:

        # Obtener una tarea pendiente
        tarea = cola_tareas.get()
        if tarea is None:
            print(f"Worker {numero} finalizado.")
            cola_tareas.task_done()
            break

        identificador = tarea["id"]
        descripcion = tarea["descripcion"]

        print(
            f"Worker {numero} procesando tarea {identificador}: "
            f"{descripcion}"
        )

        # Simular el procesamiento
        time.sleep(3)

        # Generar el resultado
        tarea["resultado"] = {
            "id": identificador,
            "estado": "completada",
            "worker": numero,
            "mensaje": f"Tarea '{descripcion}' procesada correctamente"
        }

        # Avisar que terminó el procesamiento
        tarea["evento"].set()

        print(f"Worker {numero} finalizó la tarea {identificador}.")

        cola_tareas.task_done()
