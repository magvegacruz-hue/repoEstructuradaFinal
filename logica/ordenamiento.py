# Implementación del método de ordenamiento por inserción.
# Ordena solicitudes o actividades según el campo seleccionado.


# La función "clave" permite indicar qué campo se utilizará para ordenar.
# Ejemplo: clave=lambda solicitud: solicitud["fecha_solicitud"]
def ordenar_por_insercion(lista, clave=lambda elemento: elemento):
    elementos_ordenados = [(elemento, clave(elemento)) for elemento in lista]

    for indice in range(1, len(elementos_ordenados)):
        elemento_actual = elementos_ordenados[indice]
        posicion = indice - 1

        while (
            posicion >= 0
            and elementos_ordenados[posicion][1] > elemento_actual[1]
        ):
            elementos_ordenados[posicion + 1] = elementos_ordenados[posicion]
            posicion -= 1

        elementos_ordenados[posicion + 1] = elemento_actual

    return [elemento for elemento, _ in elementos_ordenados]