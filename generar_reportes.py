import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arriendos.settings")
django.setup()

from django.db import connection
from propiedades.models import Inmueble


def reporte_por_comuna():
    """Requisito 2: listado de inmuebles para arriendo separado por comunas,
    solo con los campos "nombre" y "descripción". Se resuelve con el ORM de
    Django y se valida con una consulta SQL directa sobre el motor de BD."""

    # Consulta filtrada con el ORM (Django genera y ejecuta el SQL por debajo)
    inmuebles_orm = (
        Inmueble.objects
        .filter(disponibilidad=True)
        .select_related('comuna')
        .order_by('comuna__nombre', 'nombre')
    )

    # Misma consulta escrita directamente en SQL, para dejar explícito el uso
    # de sentencias SQL con filtros sobre el motor de base de datos
    sql = """
        SELECT c.nombre AS comuna, i.nombre AS nombre, i.descripcion AS descripcion
        FROM propiedades_inmueble i
        INNER JOIN propiedades_comuna c ON c.id = i.comuna_id
        WHERE i.disponibilidad = TRUE
        ORDER BY c.nombre, i.nombre
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        filas_sql = cursor.fetchall()

    assert len(inmuebles_orm) == len(filas_sql), "ORM y SQL no coinciden en cantidad de filas"

    with open('reporte_por_comuna.txt', 'w', encoding='utf-8') as archivo:
        comuna_actual = None
        for inmueble in inmuebles_orm:
            nombre_comuna = inmueble.comuna.nombre if inmueble.comuna else 'Sin comuna'
            if nombre_comuna != comuna_actual:
                comuna_actual = nombre_comuna
                archivo.write(f"\n=== Comuna: {comuna_actual} ===\n")
            archivo.write(f"- {inmueble.nombre}: {inmueble.descripcion}\n")

    print(f"Generado reporte_por_comuna.txt ({len(inmuebles_orm)} inmuebles, ORM y SQL coinciden)")


def reporte_por_region():
    """Requisito 3: listado de inmuebles para arriendo separado por regiones,
    solo con los campos "nombre" y "descripción". Misma lógica que el reporte
    por comuna: ORM + SQL directo, cruzando ambos resultados."""

    inmuebles_orm = (
        Inmueble.objects
        .filter(disponibilidad=True)
        .select_related('comuna__region')
        .order_by('comuna__region__nombre', 'nombre')
    )

    sql = """
        SELECT r.nombre AS region, i.nombre AS nombre, i.descripcion AS descripcion
        FROM propiedades_inmueble i
        INNER JOIN propiedades_comuna c ON c.id = i.comuna_id
        INNER JOIN propiedades_region r ON r.id = c.region_id
        WHERE i.disponibilidad = TRUE
        ORDER BY r.nombre, i.nombre
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        filas_sql = cursor.fetchall()

    assert len(inmuebles_orm) == len(filas_sql), "ORM y SQL no coinciden en cantidad de filas"

    with open('reporte_por_region.txt', 'w', encoding='utf-8') as archivo:
        region_actual = None
        for inmueble in inmuebles_orm:
            nombre_region = inmueble.comuna.region.nombre if inmueble.comuna else 'Sin región'
            if nombre_region != region_actual:
                region_actual = nombre_region
                archivo.write(f"\n=== Región: {region_actual} ===\n")
            archivo.write(f"- {inmueble.nombre}: {inmueble.descripcion}\n")

    print(f"Generado reporte_por_region.txt ({len(inmuebles_orm)} inmuebles, ORM y SQL coinciden)")


if __name__ == '__main__':
    reporte_por_comuna()
    reporte_por_region()
