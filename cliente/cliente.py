import socket
import json
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"
PUERTO = 5001


def recibir_respuesta(cliente):
    """Recibe la respuesta completa hasta encontrar el salto de línea."""

    datos = bytearray()

    while True:
        fragmento = cliente.recv(1024)

        if not fragmento:
            raise ConnectionError("El servidor cerró la conexión.")

        datos.extend(fragmento)

        if b"\n" in datos:
            mensaje, resto = datos.split(b"\n", 1)

            if resto:
                raise ValueError("Se recibieron datos adicionales.")

            return mensaje.decode("utf-8")



def enviar_tarea(identificador, descripcion):
    """Envía una tarea JSON y recibe el resultado."""

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Conectarse al servidor
        cliente.connect((HOST, PUERTO))

        # Crear la tarea como diccionario
        tarea = {
            "id": identificador,
            "descripcion": descripcion
        }

        # Convertir el diccionario a JSON
        datos = json.dumps(tarea, ensure_ascii=False)

        # Enviar la tarea
        cliente.sendall((datos + "\n").encode("utf-8"))

        # Recibir la respuesta
        respuesta = recibir_respuesta(cliente)

        # Convertir JSON recibido a diccionario
        resultado = json.loads(respuesta)

        print(f"\nTarea enviada: {tarea}")

        if "error" in resultado:
            print(f"Error: {resultado['error']}")
        else:
            print(f"Resultado: {resultado}")

    except (ConnectionError, OSError):
        print(f"Error de conexión al enviar la tarea {identificador}")

    except json.JSONDecodeError:
        print("Error: el servidor devolvió una respuesta JSON inválida.")

    finally:
        cliente.close()


def detener_servidor():
    """Solicita el apagado ordenado del servidor."""

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, PUERTO))

        solicitud = {
            "accion": "detener"
        }

        datos = json.dumps(solicitud)

        cliente.sendall((datos + "\n").encode("utf-8"))

        respuesta = recibir_respuesta(cliente)

        print("\nRespuesta del servidor:")
        print(json.loads(respuesta))

    except (ConnectionError, OSError):
        print("No se pudo conectar con el servidor.")

    finally:
        cliente.close()



def menu():
    while True:
        print("\n===== SISTEMA DE GESTIÓN DE TAREAS =====")
        print("1. Enviar una tarea")
        print("2. Enviar cinco tareas simultáneamente")
        print("3. Salir")
        print("4. Detener servidor")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            descripcion = input("Ingrese la descripción de la tarea: ")
            enviar_tarea(1, descripcion)

        elif opcion == "2":

            tareas = [
                (1, "Revisar inventario"),
                (2, "Controlar stock"),
                (3, "Generar informe"),
                (4, "Actualizar registros"),
                (5, "Verificar pedidos")
            ]

            with ThreadPoolExecutor(max_workers=5) as ejecutor:
                futuros = [
                    ejecutor.submit(enviar_tarea, identificador, descripcion)
                    for identificador, descripcion in tareas
                ]

                for futuro in futuros:
                    futuro.result()

            print("\nTodas las tareas finalizaron.")

        elif opcion == "3":
            print("Cliente finalizado.")
            break

        elif opcion == "4":
            confirmar = input("¿Desea detener el servidor? (s/n): ")

            if confirmar.lower() == "s":
                detener_servidor()
                break

        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu()
