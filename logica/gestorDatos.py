# Módulo principal de lógica del sistema.
# Administra actividades, solicitudes, estudiantes, reportes y persistencia JSON.

import json
import os
import secrets
import string
import uuid
from datetime import datetime

# Importa las funciones de las estructuras de datos.
from logica.listaEnlazada import crear_lista, agregar, obtener_todos, eliminar_por_id
from logica.listaDoble import crear_lista_doble, agregar as agregar_historial
from logica.arbol import crear_arbol, insertar, buscar
from logica.grafo import crear_grafo, agregar_arista

# Rutas de los archivos JSON que almacenan la información del sistema.
RUTA_DATOS = "datos"
RUTA_ACTIVIDADES = os.path.join(RUTA_DATOS, "actividades.json")
RUTA_SOLICITUDES = os.path.join(RUTA_DATOS, "solicitudes.json")
RUTA_ESTUDIANTES = os.path.join(RUTA_DATOS, "estudiantes.json")

# Beneficios que puede ofrecer una actividad.
BENEFICIOS = [
    "Horas laborales",
    "Crédito deportivo",
    "Crédito social",
    "Crédito cultural"
]

FACULTADES_CARRERAS = {
    "FCAE": {
        "nombre": "Facultad de Ciencias Administrativas y Económicas (FCAE)",
        "carreras": (
            "Administración de Empresas",
            "Contabilidad y Finanzas",
            "Economía Empresarial",
            "Negocios Internacionales"
        )
    },
    "FCJHRI": {
        "nombre": "Facultad de Ciencias Jurídicas, Humanidades y Relaciones Internacionales (FCJHRI)",
        "carreras": (
            "Derecho",
            "Diplomacia y Relaciones Internacionales"
        )
    },
    "FCM": {
        "nombre": "Facultad de Ciencias Médicas (FCM)",
        "carreras": (
            "Medicina General",
            "Psicología",
            "Nutrición"
        )
    },
    "FODO": {
        "nombre": "Facultad de Odontología (FODO)",
        "carreras": ("Odontología",)
    },
    "FIA": {
        "nombre": "Facultad de Ingeniería y Arquitectura (FIA)",
        "carreras": (
            "Arquitectura",
            "Ingeniería Civil",
            "Ingeniería Industrial",
            "Ingeniería de Sistemas"
        )
    },
    "FMDC": {
        "nombre": "Facultad de Marketing, Diseño y Ciencias de la Comunicación",
        "carreras": (
            "Marketing y Publicidad",
            "Diseño y Comunicación Visual",
            "Comunicación y Relaciones Públicas"
        )
    },
    "UAM College": {
        "nombre": "UAM College",
        "carreras": (
            "Major in Global Management",
            "Major in Global Finance",
            "Major in Strategic Marketing",
            "Major in International Development"
        )
    }
}
TIPOS_BECA_ALEATORIOS = ("academica", "deportiva", "cultural")
ALFABETO_ALEATORIO = string.ascii_lowercase
DIGITOS_ALEATORIOS = string.digits


def _cadena_aleatoria(alfabeto, longitud, bytes_aleatorios):
    limite = 256 - (256 % len(alfabeto))
    caracteres = []

    for valor in bytes_aleatorios:
        if valor < limite:
            caracteres.append(alfabeto[valor % len(alfabeto)])
            if len(caracteres) == longitud:
                return "".join(caracteres)

    while len(caracteres) < longitud:
        valor = secrets.randbelow(limite)
        caracteres.append(alfabeto[valor % len(alfabeto)])

    return "".join(caracteres)


# Carga un archivo JSON. Si no existe, lo crea con la estructura inicial.
def cargar_json(ruta, valor_inicial):
    if not os.path.exists(ruta):
        guardar_json(ruta, valor_inicial)
        return valor_inicial

    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


# Guarda datos en un archivo JSON con formato legible.
def guardar_json(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)


# Guarda únicamente la información de las actividades.
def guardar_actividades(datos):
    guardar_json(RUTA_ACTIVIDADES, datos["actividades"])


# Guarda únicamente la información de las solicitudes.
def guardar_solicitudes(datos):
    guardar_json(RUTA_SOLICITUDES, datos["solicitudes"])


# Guarda únicamente la información de los estudiantes.
def guardar_estudiantes(datos):
    guardar_json(RUTA_ESTUDIANTES, datos["estudiantes"])


# Inicializa el sistema cargando los JSON y preparando las estructuras.
def inicializar_sistema():
    datos = {
        "actividades": cargar_json(RUTA_ACTIVIDADES, {"actividades": []}),
        "solicitudes": cargar_json(RUTA_SOLICITUDES, {"solicitudes": []}),
        "estudiantes": cargar_json(RUTA_ESTUDIANTES, {"estudiantes": []}),
        "cola_pendientes": crear_lista(),
        "historial": crear_lista_doble(),
        "arbol": crear_arbol(),
        "grafo": crear_grafo()
    }

    cargar_estructuras(datos)
    return datos


# Reconstruye las estructuras de datos a partir de los archivos JSON.
def cargar_estructuras(datos):
    # Se reinician para evitar datos duplicados al actualizar el sistema.
    datos["cola_pendientes"] = crear_lista()
    datos["historial"] = crear_lista_doble()
    datos["arbol"] = crear_arbol()
    datos["grafo"] = crear_grafo()

    # Inserta cada actividad en el árbol de búsqueda.
    for actividad in datos["actividades"]["actividades"]:
        insertar(datos["arbol"], actividad)

    # Carga solicitudes pendientes e historial.
    for solicitud in datos["solicitudes"]["solicitudes"]:
        if solicitud["estado"] == "Pendiente":
            agregar(datos["cola_pendientes"], solicitud)

        agregar_historial(datos["historial"], solicitud)

        # Crea los nodos del grafo y sus relaciones.
        nodo_estudiante = f"Estudiante: {solicitud['cif']}"
        nodo_actividad = f"Actividad: {solicitud['nombre_actividad']}"
        nodo_beneficio = f"Beneficio: {solicitud['beneficio_solicitado']}"

        agregar_arista(datos["grafo"], nodo_estudiante, nodo_actividad, "solicitó")
        agregar_arista(datos["grafo"], nodo_actividad, nodo_beneficio, "otorga")


# ------------------------- ACTIVIDADES -------------------------

# Devuelve todas las actividades registradas.
def obtener_actividades(datos):
    return datos["actividades"]["actividades"]


# Devuelve solo las actividades cuya fecha aún no ha pasado.
def obtener_actividades_disponibles(datos):
    disponibles = []
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    for actividad in datos["actividades"]["actividades"]:
        if actividad["fecha"] >= fecha_actual:
            disponibles.append(actividad)

    return disponibles


# Busca una actividad mediante su ID único.
def buscar_actividad_por_id(datos, id_actividad):
    for actividad in datos["actividades"]["actividades"]:
        if actividad["id"] == id_actividad:
            return actividad

    return None


# Busca una actividad en el árbol por su nombre.
def buscar_actividad_por_nombre(datos, nombre):
    return buscar(datos["arbol"], nombre)


# Crea una nueva actividad después de validar los datos.
def crear_actividad(datos, formulario):
    nombre = formulario.get("nombre", "").strip()
    descripcion = formulario.get("descripcion", "").strip()
    fecha = formulario.get("fecha", "")
    hora_inicio = formulario.get("hora_inicio", "")
    hora_fin = formulario.get("hora_fin", "")
    lugar = formulario.get("lugar", "").strip()
    beneficio = formulario.get("beneficio", "")
    horas_texto = formulario.get("horas_convalidables", "0")

    # Validación de campos obligatorios.
    if not nombre or not fecha or not hora_inicio or not hora_fin or not beneficio:
        return {
            "exito": False,
            "mensaje": "Todos los campos obligatorios deben estar completos."
        }

    # Validación del tipo de beneficio.
    if beneficio not in BENEFICIOS:
        return {
            "exito": False,
            "mensaje": "El beneficio seleccionado no es válido."
        }

    # No se permiten actividades con fecha anterior al día actual.
    if fecha < datetime.now().strftime("%Y-%m-%d"):
        return {
            "exito": False,
            "mensaje": "La fecha de la actividad no puede ser anterior a hoy."
        }

    # La hora de inicio debe ser anterior a la hora de finalización.
    if hora_inicio >= hora_fin:
        return {
            "exito": False,
            "mensaje": "La hora de inicio debe ser anterior a la hora de fin."
        }

    horas = 0

    # Solo las actividades de horas laborales requieren cantidad de horas.
    if beneficio == "Horas laborales":
        try:
            horas = int(horas_texto)
        except ValueError:
            return {
                "exito": False,
                "mensaje": "Las horas convalidables deben ser un número entero."
            }

        if horas <= 0:
            return {
                "exito": False,
                "mensaje": "Las horas convalidables deben ser mayores que cero."
            }

    nueva_actividad = {
        "id": f"ACT-{str(uuid.uuid4())[:8].upper()}",
        "nombre": nombre,
        "descripcion": descripcion,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "lugar": lugar,
        "beneficio": beneficio,
        "horas_convalidables": horas,
        "estado": "Disponible"
    }

    # Agrega la actividad y actualiza el archivo JSON y las estructuras.
    datos["actividades"]["actividades"].append(nueva_actividad)
    guardar_actividades(datos)
    cargar_estructuras(datos)

    return {
        "exito": True,
        "mensaje": "Actividad registrada correctamente."
    }


# Edita una actividad existente.
def editar_actividad(datos, id_actividad, formulario):
    actividad = buscar_actividad_por_id(datos, id_actividad)

    if actividad is None:
        return {
            "exito": False,
            "mensaje": "La actividad no existe."
        }

    hora_inicio = formulario.get("hora_inicio", "")
    hora_fin = formulario.get("hora_fin", "")

    if hora_inicio >= hora_fin:
        return {
            "exito": False,
            "mensaje": "La hora de inicio debe ser anterior a la hora de fin."
        }

    # Actualiza los campos permitidos de la actividad.
    actividad["nombre"] = formulario.get("nombre", "").strip()
    actividad["descripcion"] = formulario.get("descripcion", "").strip()
    actividad["fecha"] = formulario.get("fecha", "")
    actividad["hora_inicio"] = hora_inicio
    actividad["hora_fin"] = hora_fin
    actividad["lugar"] = formulario.get("lugar", "").strip()
    actividad["beneficio"] = formulario.get("beneficio", "")

    try:
        actividad["horas_convalidables"] = int(
            formulario.get("horas_convalidables", "0")
        )
    except ValueError:
        actividad["horas_convalidables"] = 0

    guardar_actividades(datos)
    cargar_estructuras(datos)

    return {
        "exito": True,
        "mensaje": "Actividad actualizada correctamente."
    }


# Elimina una actividad y marca sus solicitudes como "Evento eliminado".
def eliminar_actividad(datos, id_actividad):
    actividad = buscar_actividad_por_id(datos, id_actividad)

    if actividad is None:
        return {
            "exito": False,
            "mensaje": "La actividad no existe."
        }

    datos["actividades"]["actividades"].remove(actividad)

    # Actualiza el estado de las solicitudes relacionadas.
    for solicitud in datos["solicitudes"]["solicitudes"]:
        if solicitud["id_actividad"] == id_actividad:
            solicitud["estado"] = "Evento eliminado"
            solicitud["observacion"] = "La actividad fue eliminada por Vida Estudiantil."

    guardar_actividades(datos)
    guardar_solicitudes(datos)
    cargar_estructuras(datos)

    return {
        "exito": True,
        "mensaje": "Actividad eliminada y solicitudes actualizadas."
    }


# ------------------------- SOLICITUDES -------------------------

# Busca una solicitud por su ID único.
def buscar_solicitud_por_id(datos, id_solicitud):
    for solicitud in datos["solicitudes"]["solicitudes"]:
        if solicitud["id_solicitud"] == id_solicitud:
            return solicitud

    return None


# Cuenta cuántas solicitudes tiene un estudiante en una misma actividad.
def contar_solicitudes_estudiante_actividad(datos, cif, id_actividad):
    contador = 0

    for solicitud in datos["solicitudes"]["solicitudes"]:
        if solicitud["cif"] == cif and solicitud["id_actividad"] == id_actividad:
            contador += 1

    return contador


# Registra al estudiante si aún no existe en el archivo JSON.
def registrar_estudiante(datos, formulario):
    cif = formulario.get("cif", "").strip()

    for estudiante in datos["estudiantes"]["estudiantes"]:
        if estudiante["cif"] == cif:
            return

    nuevo_estudiante = {
        "cif": cif,
        "nombre": formulario.get("nombre", "").strip(),
        "facultad": formulario.get("facultad", "").strip(),
        "carrera": formulario.get("carrera", "").strip(),
        "tipo_beca": formulario.get("tipo_beca", "").strip(),
        "correo": formulario.get("correo", "").strip()
    }

    datos["estudiantes"]["estudiantes"].append(nuevo_estudiante)
    guardar_estudiantes(datos)


# Registra una nueva solicitud de convalidación.
def registrar_solicitud(datos, id_actividad, formulario):
    actividad = buscar_actividad_por_id(datos, id_actividad)

    if actividad is None:
        return {
            "exito": False,
            "mensaje": "La actividad no existe."
        }

    cif = formulario.get("cif", "").strip()
    beneficio = formulario.get("beneficio_solicitado", "")

    # Validación de datos obligatorios del estudiante.
    if not cif or not formulario.get("nombre", "").strip():
        return {
            "exito": False,
            "mensaje": "El CIF y el nombre son obligatorios."
        }

    facultad = formulario.get("facultad", "").strip()
    carrera = formulario.get("carrera", "").strip()

    if not facultad or not carrera:
        return {
            "exito": False,
            "mensaje": "La facultad y la carrera son obligatorias."
        }

    if (
        facultad not in FACULTADES_CARRERAS
        or carrera not in FACULTADES_CARRERAS[facultad]["carreras"]
    ):
        return {
            "exito": False,
            "mensaje": "La carrera seleccionada no pertenece a la facultad."
        }

    if beneficio not in BENEFICIOS:
        return {
            "exito": False,
            "mensaje": "El beneficio solicitado no es válido."
        }

    # La inscripción cierra cuando inicia la actividad.
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    if fecha_actual >= actividad["fecha"]:
        return {
            "exito": False,
            "mensaje": "El periodo de inscripción ya está cerrado."
        }

    # Límite de tres solicitudes independientes por actividad.
    if contar_solicitudes_estudiante_actividad(datos, cif, id_actividad) >= 3:
        return {
            "exito": False,
            "mensaje": "Ya alcanzaste el límite de 3 solicitudes para esta actividad."
        }

    nueva_solicitud = {
        "id_solicitud": f"SOL-{str(uuid.uuid4())[:8].upper()}",
        "cif": cif,
        "nombre_estudiante": formulario.get("nombre", "").strip(),
        "facultad": facultad,
        "carrera": carrera,
        "tipo_beca": formulario.get("tipo_beca", "").strip(),
        "correo": formulario.get("correo", "").strip(),
        "id_actividad": id_actividad,
        "nombre_actividad": actividad["nombre"],
        "beneficio_solicitado": beneficio,
        "horas_solicitadas": actividad["horas_convalidables"],
        "fecha_solicitud": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": "Pendiente",
        "observacion": ""
    }

    # Guarda la solicitud y actualiza las estructuras.
    datos["solicitudes"]["solicitudes"].append(nueva_solicitud)
    guardar_solicitudes(datos)
    cargar_estructuras(datos)

    registrar_estudiante(datos, formulario)

    return {
        "exito": True,
        "mensaje": "Solicitud enviada correctamente. Estado: Pendiente."
    }


# Genera solicitudes de prueba con datos aleatorios que cumplen los formatos pedidos.
def generar_solicitudes_aleatorias(datos, id_actividad, cantidad):
    if (
        not isinstance(cantidad, int)
        or isinstance(cantidad, bool)
        or cantidad < 1
        or cantidad > 1_000_000
    ):
        return {
            "exito": False,
            "mensaje": "La cantidad debe estar entre 1 y 1,000,000."
        }

    actividad = buscar_actividad_por_id(datos, id_actividad)

    if actividad is None:
        return {
            "exito": False,
            "mensaje": "La actividad no existe."
        }

    solicitudes_existentes = datos["solicitudes"]["solicitudes"]
    cifs_existentes = {
        estudiante["cif"] for estudiante in datos["estudiantes"]["estudiantes"]
    }
    cifs_existentes.update(
        solicitud["cif"] for solicitud in solicitudes_existentes
    )
    cifs_generados = set()
    ids_generados = set()
    ids_existentes = {
        solicitud["id_solicitud"] for solicitud in solicitudes_existentes
    }
    solicitudes_nuevas = []
    estudiantes_nuevos = []
    fecha_solicitud = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    while len(solicitudes_nuevas) < cantidad:
        muestra_aleatoria = secrets.token_bytes(48)
        cif = _cadena_aleatoria(
            DIGITOS_ALEATORIOS,
            8,
            muestra_aleatoria[:10]
        )

        if cif in cifs_existentes or cif in cifs_generados:
            continue

        cifs_generados.add(cif)
        nombre = _cadena_aleatoria(
            ALFABETO_ALEATORIO,
            8,
            muestra_aleatoria[10:26]
        )
        facultad = secrets.choice(tuple(FACULTADES_CARRERAS))
        carrera = secrets.choice(FACULTADES_CARRERAS[facultad]["carreras"])
        tipo_beca = secrets.choice(TIPOS_BECA_ALEATORIOS)
        correo = _cadena_aleatoria(
            ALFABETO_ALEATORIO,
            10,
            muestra_aleatoria[26:]
        ) + "@uamv.edu.ni"

        estudiante = {
            "cif": cif,
            "nombre": nombre,
            "facultad": facultad,
            "carrera": carrera,
            "tipo_beca": tipo_beca,
            "correo": correo
        }
        estudiantes_nuevos.append(estudiante)
        id_solicitud = f"SOL-{uuid.uuid4().hex.upper()}"

        while id_solicitud in ids_existentes or id_solicitud in ids_generados:
            id_solicitud = f"SOL-{uuid.uuid4().hex.upper()}"

        ids_generados.add(id_solicitud)
        solicitudes_nuevas.append({
            "id_solicitud": id_solicitud,
            "cif": cif,
            "nombre_estudiante": nombre,
            "facultad": facultad,
            "carrera": carrera,
            "tipo_beca": tipo_beca,
            "correo": correo,
            "id_actividad": id_actividad,
            "nombre_actividad": actividad["nombre"],
            "beneficio_solicitado": secrets.choice(BENEFICIOS),
            "horas_solicitadas": actividad["horas_convalidables"],
            "fecha_solicitud": fecha_solicitud,
            "estado": "Pendiente",
            "observacion": ""
        })

    solicitudes_existentes.extend(solicitudes_nuevas)
    datos["estudiantes"]["estudiantes"].extend(estudiantes_nuevos)
    guardar_solicitudes(datos)
    guardar_estudiantes(datos)
    cargar_estructuras(datos)

    return {
        "exito": True,
        "mensaje": f"Se generaron {cantidad:,} solicitudes aleatorias correctamente."
    }


# Devuelve las solicitudes pendientes almacenadas en la lista enlazada.
def obtener_solicitudes_pendientes(datos):
    return obtener_todos(datos["cola_pendientes"])


# Cambia el estado de una solicitud pendiente a convalidado o rechazado.
def cambiar_estado_solicitud(datos, id_solicitud, nuevo_estado, observacion=""):
    solicitud = buscar_solicitud_por_id(datos, id_solicitud)

    if solicitud is None:
        return {
            "exito": False,
            "mensaje": "La solicitud no existe."
        }

    # Solo se procesan solicitudes que siguen pendientes.
    if solicitud["estado"] != "Pendiente":
        return {
            "exito": False,
            "mensaje": "Solo se pueden procesar solicitudes pendientes."
        }

    solicitud["estado"] = nuevo_estado
    solicitud["observacion"] = observacion

    guardar_solicitudes(datos)
    cargar_estructuras(datos)

    return {
        "exito": True,
        "mensaje": f"Solicitud marcada como {nuevo_estado}."
    }


# Obtiene todas las solicitudes asociadas al CIF de un estudiante.
def obtener_historial_estudiante(datos, cif):
    historial = []

    for solicitud in datos["solicitudes"]["solicitudes"]:
        if solicitud["cif"] == cif:
            historial.append(solicitud)

    return historial


# Suma únicamente las horas laborales con estado "Convalidado".
def calcular_horas_convalidadas(datos, cif):
    total = 0

    for solicitud in datos["solicitudes"]["solicitudes"]:
        if (
            solicitud["cif"] == cif
            and solicitud["estado"] == "Convalidado"
            and solicitud["beneficio_solicitado"] == "Horas laborales"
        ):
            total += solicitud["horas_solicitadas"]

    return total


# Cuenta los créditos convalidados por tipo.
def calcular_creditos_convalidados(datos, cif):
    creditos = {
        "Crédito deportivo": 0,
        "Crédito social": 0,
        "Crédito cultural": 0
    }

    for solicitud in datos["solicitudes"]["solicitudes"]:
        if solicitud["cif"] == cif and solicitud["estado"] == "Convalidado":
            beneficio = solicitud["beneficio_solicitado"]

            if beneficio in creditos:
                creditos[beneficio] += 1

    return creditos


# ------------------------- REPORTES -------------------------

# Genera indicadores generales para el panel de Vida Estudiantil.
def generar_reportes(datos):
    solicitudes = datos["solicitudes"]["solicitudes"]

    pendientes = 0
    convalidadas = 0
    rechazadas = 0
    horas_totales = 0

    for solicitud in solicitudes:
        if solicitud["estado"] == "Pendiente":
            pendientes += 1

        if solicitud["estado"] == "Convalidado":
            convalidadas += 1

            if solicitud["beneficio_solicitado"] == "Horas laborales":
                horas_totales += solicitud["horas_solicitadas"]

        if solicitud["estado"] == "Rechazado":
            rechazadas += 1

    return {
        "pendientes": pendientes,
        "convalidadas": convalidadas,
        "rechazadas": rechazadas,
        "horas_totales": horas_totales,
        "total_actividades": len(datos["actividades"]["actividades"])
    }


# Devuelve el grafo completo para representarlo en HTML.
def generar_grafo(datos):
    return datos["grafo"]["adyacencias"]