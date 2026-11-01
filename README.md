# PFO3 – Sistema Distribuido Cliente-Servidor

**Materia:** Programación sobre Redes  
**Trabajo práctico:** PFO 3 – Rediseño como Sistema Distribuido  
**Lenguaje:** Python  
**Comunicación:** Sockets TCP  
**Formato de intercambio:** JSON

## Descripción del proyecto

Este proyecto implementa un sistema cliente-servidor que permite enviar y procesar tareas mediante comunicación por sockets TCP.

El servidor recibe solicitudes de los clientes, administra una cola de tareas y distribuye su procesamiento entre un conjunto de workers que funcionan mediante hilos (threads).

La implementación permite trabajar con múltiples solicitudes concurrentes y devolver al cliente el resultado del procesamiento.

## Tecnologías utilizadas

- Python.
- Sockets TCP (`socket`).
- Programación concurrente (`threading`).
- Cola de tareas (`queue`).
- Intercambio de datos en formato JSON (`json`).

## Estructura del proyecto

```text
PFO3_Sistema_distribuido/
│
├── servidor/
│   ├── server.py
│   └── worker.py
│
├── cliente/
│   └── client.py
│
└── .gitignore
```

## Funcionamiento

El sistema está compuesto por los siguientes elementos:

- **Cliente:** permite enviar tareas al servidor y recibir los resultados.
- **Servidor:** recibe las conexiones TCP, valida las solicitudes y administra la cola de tareas.
- **Cola de tareas:** organiza las solicitudes pendientes de procesamiento.
- **Workers:** tres hilos independientes procesan las tareas de manera concurrente.
- **Comunicación JSON:** permite intercambiar solicitudes y respuestas entre cliente y servidor.

## Ejecución del proyecto

Se requiere tener Python instalado.

**1. Iniciar el servidor**

Abrir una terminal en la carpeta principal del proyecto y ejecutar:

```bash
cd servidor
python server.py
```

El servidor quedará a la espera de conexiones de clientes.

**2. Iniciar el cliente**

Abrir una segunda terminal, también desde la carpeta principal del proyecto, y ejecutar:

```bash
cd cliente
python client.py
```

**3. Opciones disponibles en el cliente**

El menú permite:

1. Enviar una tarea individual.
2. Enviar cinco tareas simultáneamente para demostrar el procesamiento concurrente.
3. Salir del cliente.
4. Solicitar la detención ordenada del servidor.

## Pruebas realizadas

Se realizaron pruebas de comunicación entre cliente y servidor, envío y recepción de mensajes JSON, procesamiento de tareas individuales y procesamiento concurrente de cinco tareas.

Se verificó el funcionamiento de los tres workers y la finalización ordenada del servidor.

## Objetivo

Demostrar los conceptos fundamentales de comunicación cliente-servidor mediante sockets TCP, concurrencia, utilización de hilos y distribución de tareas.