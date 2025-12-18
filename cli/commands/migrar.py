"""
CLI Commands Migrar
"""

import os
import uuid

import psycopg2
from dotenv import load_dotenv
from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.main import app

load_dotenv()  # Take environment variables from .env

# Cargar variables de entorno para la base de datos ANTERIOR
OLD_DB_NAME = os.environ.get("OLD_DB_NAME")
OLD_DB_USER = os.environ.get("OLD_DB_USER")
OLD_DB_PASS = os.environ.get("OLD_DB_PASS")
OLD_DB_HOST = os.environ.get("OLD_DB_HOST")
OLD_DB_PORT = os.environ.get("OLD_DB_PORT")

# Cargar variables de entorno para la base de datos NUEVA
NEW_DB_NAME = os.environ.get("NEW_DB_NAME")
NEW_DB_USER = os.environ.get("NEW_DB_USER")
NEW_DB_PASS = os.environ.get("NEW_DB_PASS")
NEW_DB_HOST = os.environ.get("NEW_DB_HOST")
NEW_DB_PORT = os.environ.get("NEW_DB_PORT")

app.app_context().push()


def copiar_cit_dias_inhabiles(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla cit_dias_inhabiles de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute("SELECT fecha, descripcion, estatus FROM cit_dias_inhabiles ORDER BY fecha ASC")
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar registros en la base de datos NUEVA
    contador = 0
    insert_query = "INSERT INTO cit_dias_inhabiles (id, fecha, descripcion, estatus) VALUES (%s, %s, %s, %s)"
    try:
        for row in rows:
            fecha = row[0]  # La fecha es la primer columna
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM cit_dias_inhabiles WHERE fecha = %s", (fecha,))
            if cursor_new.fetchone():
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
    except Exception as error:
        raise Exception(f"Error al insertar {fecha}: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    return f"  {contador} cit_dias_inhabiles copiados."


def copiar_distritos(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla distritos de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
                SELECT
                    clave, nombre, nombre_corto, es_distrito_judicial, es_distrito, es_jurisdiccional,
                    estatus, creado, modificado
                FROM
                    distritos
                ORDER BY
                    id ASC
            """,
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar registros en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO distritos (id,
            clave, nombre, nombre_corto, es_distrito_judicial, es_distrito, es_jurisdiccional,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            clave = row[0]  # La clave es la primer columna
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM distritos WHERE clave = %s", (clave,))
            if cursor_new.fetchone():
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
    except Exception as error:
        raise Exception(f"Error al insertar {clave}: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    return f"  {contador} distritos copiados."


def copiar_autoridades(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla autoridades de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
                SELECT
                    distritos.clave AS distrito_clave,
                    materias.clave AS materia_clave,
                    autoridades.clave,
                    autoridades.descripcion,
                    autoridades.descripcion_corta,
                    autoridades.es_jurisdiccional,
                    autoridades.estatus,
                    autoridades.creado,
                    autoridades.modificado
                FROM
                    autoridades
                    JOIN distritos ON autoridades.distrito_id = distritos.id
                    JOIN materias ON autoridades.materia_id = materias.id
                ORDER BY
                    autoridades.id ASC
            """,
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar registros en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO autoridades (id,
            distrito_id,
            materia_id,
            clave, descripcion, descripcion_corta, es_jurisdiccional,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            (SELECT id FROM distritos WHERE clave = %s),
            (SELECT id FROM materias WHERE clave = %s),
            %s, %s, %s, %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM autoridades WHERE clave = %s", (row[2],))
            if cursor_new.fetchone():
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
    except Exception as error:
        raise Exception(f"Error al insertar registros en la BD NUEVA: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    return f"  {contador} autoridades copiados."


def copiar_domicilios(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla domicilios de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
                SELECT
                    clave, edificio, estado, municipio, calle, num_ext, num_int, colonia, cp, completo,
                    estatus, creado, modificado
                FROM
                    domicilios
                ORDER BY
                    clave ASC
            """,
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar registros en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO domicilios (id,
            clave, edificio, estado, municipio, calle, num_ext, num_int, colonia, cp, completo,
            estatus, creado, modificado,
            es_activo)
        VALUES (%s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s,
            true)
    """
    try:
        for row in rows:
            clave = row[0]  # La clave es la primer columna
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM domicilios WHERE clave = %s", (clave,))
            if cursor_new.fetchone():
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
    except Exception as error:
        raise Exception(f"Error al insertar {clave}: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    return f"  {contador} domicilios copiados."


def copiar_oficinas(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla oficinas de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
                SELECT
                    distritos.clave AS distrito_clave,
                    domicilios.clave AS domicilio_clave,
                    oficinas.clave, oficinas.descripcion, oficinas.descripcion_corta,
                    oficinas.es_jurisdiccional, oficinas.puede_agendar_citas,
                    oficinas.apertura, oficinas.cierre, oficinas.limite_personas, oficinas.puede_enviar_qr,
                    oficinas.estatus, oficinas.creado, oficinas.modificado
                FROM
                    oficinas
                    JOIN distritos ON oficinas.distrito_id = distritos.id
                    JOIN domicilios ON oficinas.domicilio_id = domicilios.id
                ORDER BY oficinas.clave ASC
            """,
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar registros en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO oficinas (id,
            distrito_id,
            domicilio_id,
            clave, descripcion, descripcion_corta,
            es_jurisdiccional, puede_agendar_citas,
            apertura, cierre, limite_personas, puede_enviar_qr,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            (SELECT id FROM distritos WHERE clave = %s),
            (SELECT id FROM domicilios WHERE clave = %s),
            %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            clave = row[2]  # La clave de la oficina es la tercer columna
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM oficinas WHERE clave = %s", (clave,))
            if cursor_new.fetchone():
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
    except Exception as error:
        raise Exception(f"Error al insertar {clave}: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    return f"  {contador} oficinas copiadas."


def copiar_cit_categorias(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla cit_categorias de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
            SELECT
                clave, nombre,
                estatus, creado, modificado
            FROM
                cit_categorias
            ORDER BY
                clave ASC
        """
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar datos en la tabla cit_categorias en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO cit_categorias (id,
            clave, nombre,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            %s, %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            clave = row[0]  # La clave es la primer columna
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM cit_categorias WHERE clave = %s", (clave,))
            if cursor_new.fetchone():
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
    except Exception as error:
        raise Exception(f"Error al insertar {clave}: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    return f"  {contador} cit_categorias copiados."


def copiar_cit_servicios(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla cit_servicios de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
                SELECT
                    cit_categorias.clave AS cit_categoria_clave,
                    cit_servicios.clave,
                    cit_servicios.descripcion,
                    cit_servicios.duracion,
                    cit_servicios.documentos_limite,
                    cit_servicios.desde,
                    cit_servicios.hasta,
                    cit_servicios.dias_habilitados,
                    cit_servicios.estatus,
                    cit_servicios.creado,
                    cit_servicios.modificado
                FROM
                    cit_servicios
                    JOIN cit_categorias ON cit_servicios.cit_categoria_id = cit_categorias.id
            """,
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar registros en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO cit_servicios (id,
            cit_categoria_id,
            clave, descripcion, duracion, documentos_limite,
            desde, hasta, dias_habilitados,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            (SELECT id FROM cit_categorias WHERE clave = %s),
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            cit_servicio_clave = row[1]  # La clave del servicio es la segunda columna
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM cit_servicios WHERE clave = %s", (cit_servicio_clave,))
            if cursor_new.fetchone():
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
    except Exception as error:
        raise Exception(f"Error al insertar {cit_servicio_clave}: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    return f"  {contador} cit_servicios copiados."


def copiar_cit_oficinas_servicios(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla cit_oficinas_servicios de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute(
            """
                SELECT
                    cit_servicios.clave AS cit_servicio_clave,
                    oficinas.clave AS oficina_clave,
                    cit_oficinas_servicios.descripcion,
                    cit_oficinas_servicios.estatus,
                    cit_oficinas_servicios.creado,
                    cit_oficinas_servicios.modificado
                FROM
                    cit_oficinas_servicios
                    JOIN cit_servicios ON cit_oficinas_servicios.cit_servicio_id = cit_servicios.id
                    JOIN oficinas ON cit_oficinas_servicios.oficina_id = oficinas.id
                ORDER BY cit_oficinas_servicios.id ASC
            """,
        )
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar registros en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO cit_oficinas_servicios (id,
            cit_servicio_id,
            oficina_id,
            descripcion,
            estatus, creado, modificado, es_activo)
        VALUES (%s,
            (SELECT id FROM cit_servicios WHERE clave = %s),
            (SELECT id FROM oficinas WHERE clave = %s),
            %s,
            %s, %s, %s, true)
    """
    try:
        for row in rows:
            cit_servicio_clave = row[0]  # La clave del servicio es la primer columna
            oficina_clave = row[1]  # La clave de la oficina es la segunda columna
            # Si ya existe un registro con cit_servicio_id y oficina_id, omitir
            cursor_new.execute(
                """
                SELECT id FROM cit_oficinas_servicios
                WHERE cit_servicio_id = (SELECT id FROM cit_servicios WHERE clave = %s)
                AND oficina_id = (SELECT id FROM oficinas WHERE clave = %s)
                """,
                (cit_servicio_clave, oficina_clave),
            )
            if cursor_new.fetchone():
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
    except Exception as error:
        raise Exception(f"Error al insertar {cit_servicio_clave} en {oficina_clave}: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    return f"  {contador} cit_oficinas_servicios copiados."


def copiar_cit_clientes(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla cit_clientes de la base de datos ANTERIOR a la NUEVA"""
    # Inicializar limit y offset para paginar la consulta de la base de datos ANTERIOR
    limit = 1000
    offset = 0
    contador = 0
    # Bucle para leer e insertar registros en lotes
    while True:
        # Leer registros en la base de datos ANTERIOR
        try:
            cursor_old.execute(
                """
                    SELECT
                        nombres, apellido_primero, apellido_segundo, curp, telefono, email,
                        contrasena_md5, contrasena_sha256, renovacion, limite_citas_pendientes,
                        estatus, creado, modificado
                    FROM
                        cit_clientes
                    LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cursor_old.fetchall()
        except Exception as error:
            raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
        # Si no hay más registros, salir del ciclo
        if not rows:
            break
        # Insertar registros en la base de datos NUEVA
        insert_query = """
            INSERT INTO cit_clientes
                (id, nombres, apellido_primero, apellido_segundo, curp, telefono, email,
                contrasena_md5, contrasena_sha256, renovacion, limite_citas_pendientes,
                estatus, creado, modificado,
                autoriza_mensajes, enviar_boletin,
                es_adulto_mayor, es_mujer, es_identidad, es_discapacidad, es_personal_interno)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                false, false,
                false, false, false, false, false)
        """
        try:
            for row in rows:
                email = row[5]  # El email es la sexta columna
                # Consultar si el registro ya existe
                cursor_new.execute("SELECT id FROM cit_clientes WHERE email = %s", (email,))
                if cursor_new.fetchone():
                    continue  # Ya existe, se omite
                # Insertar
                new_id = str(uuid.uuid4())
                cursor_new.execute(insert_query, (new_id, *row))
                contador += 1
        except Exception as error:
            raise Exception(f"Error al insertar {email}: {error}")
        # Confirmar los cambios
        conn_new.commit()
        # Incrementar offset para la siguiente página
        offset += limit
    # Mensaje final
    return f"  {contador} cit_clientes copiados."


def copiar_cit_clientes_recuperaciones(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla cit_clientes_recuperaciones de la base de datos ANTERIOR a la NUEVA"""
    # Inicializar limit y offset para paginar la consulta de la base de datos ANTERIOR
    limit = 1000
    offset = 0
    contador = 0
    # Bucle para leer e insertar registros en lotes
    while True:
        # Leer registros en la base de datos ANTERIOR
        try:
            cursor_old.execute(
                """
                    SELECT
                        cit_clientes_recuperaciones.id as id_original,
                        cit_clientes.email,
                        cit_clientes_recuperaciones.expiracion,
                        cit_clientes_recuperaciones.cadena_validar,
                        cit_clientes_recuperaciones.mensajes_cantidad,
                        cit_clientes_recuperaciones.ya_recuperado,
                        cit_clientes_recuperaciones.estatus,
                        cit_clientes_recuperaciones.creado,
                        cit_clientes_recuperaciones.modificado
                    FROM
                        cit_clientes_recuperaciones
                        JOIN cit_clientes ON cit_clientes_recuperaciones.cit_cliente_id = cit_clientes.id
                    ORDER BY cit_clientes_recuperaciones.id ASC
                    LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cursor_old.fetchall()
        except Exception as error:
            raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
        # Si no hay más registros, salir del ciclo
        if not rows:
            break
        # Insertar registros en la base de datos NUEVA
        insert_query = """
            INSERT INTO cit_clientes_recuperaciones (id, id_original,
                cit_cliente_id,
                expiracion, cadena_validar, mensajes_cantidad, ya_recuperado,
                estatus, creado, modificado)
            VALUES (%s, %s,
                (SELECT id FROM cit_clientes WHERE email = %s),
                %s, %s, %s, %s,
                %s, %s, %s)
        """
        try:
            for row in rows:
                id_original = row[0]  # El id_original es la primer columna
                # Consultar si el registro ya existe
                cursor_new.execute("SELECT id FROM cit_clientes_recuperaciones WHERE id_original = %s", (id_original,))
                if cursor_new.fetchone():
                    continue  # Ya existe, se omite
                # Insertar
                new_id = str(uuid.uuid4())
                cursor_new.execute(insert_query, (new_id, *row))
                contador += 1
        except Exception as error:
            raise Exception(f"Error al insertar {id_original}: {error}")
        # Confirmar los cambios
        conn_new.commit()
        # Incrementar offset para la siguiente página
        offset += limit
    # Mensaje final
    return f"  {contador} cit_clientes_recuperaciones copiados."


def copiar_cit_clientes_registros(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla cit_clientes_registros de la base de datos ANTERIOR a la NUEVA"""
    # Inicializar limit y offset para paginar la consulta de la base de datos ANTERIOR
    limit = 1000
    offset = 0
    contador = 0
    # Bucle para leer e insertar registros en lotes
    while True:
        # Leer registros en la base de datos ANTERIOR
        try:
            cursor_old.execute(
                """
                    SELECT
                        id AS id_original,
                        nombres,
                        apellido_primero,
                        apellido_segundo,
                        curp,
                        telefono,
                        email,
                        expiracion,
                        cadena_validar,
                        mensajes_cantidad,
                        ya_registrado,
                        estatus,
                        creado,
                        modificado
                    FROM
                        cit_clientes_registros
                    ORDER BY cit_clientes_registros.id ASC
                    LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cursor_old.fetchall()
        except Exception as error:
            raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
        # Si no hay más registros, salir del ciclo
        if not rows:
            break
        # Insertar registros en la base de datos NUEVA
        insert_query = """
            INSERT INTO cit_clientes_registros (id, id_original,
                nombres, apellido_primero, apellido_segundo, curp, telefono, email,
                expiracion, cadena_validar, mensajes_cantidad, ya_registrado,
                estatus, creado, modificado)
            VALUES (%s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s)
        """
        try:
            for row in rows:
                id_original = row[0]  # El id_original es la primer columna
                # Consultar si el registro ya existe
                cursor_new.execute("SELECT id FROM cit_clientes_registros WHERE id_original = %s", (id_original,))
                if cursor_new.fetchone():
                    continue  # Ya existe, se omite
                # Insertar
                new_id = str(uuid.uuid4())
                cursor_new.execute(insert_query, (new_id, *row))
                contador += 1
        except Exception as error:
            raise Exception(f"Error al insertar {id_original}: {error}")
        # Confirmar los cambios
        conn_new.commit()
        # Incrementar offset para la siguiente página
        offset += limit
    # Mensaje final
    return f"  {contador} cit_clientes_registros copiados."


def copiar_cit_citas(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla cit_citas de la base de datos ANTERIOR a la NUEVA"""
    # Inicializar limit y offset para paginar la consulta de la base de datos ANTERIOR
    limit = 1000
    offset = 0
    contador = 0
    # Bucle para leer e insertar registros en lotes
    while True:
        # Leer registros en la base de datos ANTERIOR
        try:
            cursor_old.execute(
                """
                    SELECT
                        cit_citas.id as id_original,
                        cit_clientes.email,
                        cit_servicios.clave AS cit_servicio_clave,
                        oficinas.clave AS oficina_clave,
                        cit_citas.inicio,
                        cit_citas.termino,
                        cit_citas.notas,
                        cit_citas.estado,
                        cit_citas.cancelar_antes,
                        cit_citas.asistencia,
                        cit_citas.codigo_asistencia,
                        cit_citas.estatus,
                        cit_citas.creado,
                        cit_citas.modificado
                    FROM
                        cit_citas
                        JOIN cit_clientes ON cit_citas.cit_cliente_id = cit_clientes.id
                        JOIN cit_servicios ON cit_citas.cit_servicio_id = cit_servicios.id
                        JOIN oficinas ON cit_citas.oficina_id = oficinas.id
                    ORDER BY cit_citas.id ASC
                    LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cursor_old.fetchall()
        except Exception as error:
            raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
        # Si no hay más registros, salir del ciclo
        if not rows:
            break
        # Insertar registros en la base de datos NUEVA
        insert_query = """
            INSERT INTO cit_citas (id, id_original,
                cit_cliente_id, cit_servicio_id, oficina_id,
                inicio, termino, notas, estado, cancelar_antes,
                asistencia, codigo_asistencia, codigo_acceso_id, codigo_acceso_imagen,
                estatus, creado, modificado)
            VALUES (%s, %s,
                (SELECT id FROM cit_clientes WHERE email = %s),
                (SELECT id FROM cit_servicios WHERE clave = %s),
                (SELECT id FROM oficinas WHERE clave = %s),
                %s, %s, %s, %s, %s,
                %s, %s, NULL, NULL,
                %s, %s, %s)
        """
        try:
            for row in rows:
                id_original = row[0]  # El id_original es la primer columna
                # Consultar si el registro ya existe
                cursor_new.execute("SELECT id FROM cit_citas WHERE id_original = %s", (id_original,))
                if cursor_new.fetchone():
                    continue  # Ya existe, se omite
                # Insertar
                new_id = str(uuid.uuid4())
                cursor_new.execute(insert_query, (new_id, *row))
                contador += 1
        except Exception as error:
            raise Exception(f"Error al insertar {id_original}: {error}")
        # Confirmar los cambios
        conn_new.commit()
        # Incrementar offset para la siguiente página
        offset += limit
    # Mensaje final
    return f"  {contador} cit_citas copiados."


def copiar_pag_tramites_servicios(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla pag_tramites_servicios de la base de datos ANTERIOR a la NUEVA"""
    # Leer registros en la base de datos ANTERIOR
    try:
        cursor_old.execute("SELECT clave, descripcion, costo, url, estatus, creado, modificado FROM pag_tramites_servicios")
        rows = cursor_old.fetchall()
    except Exception as error:
        raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
    # Continuar solo si se leyeron registros
    if not rows:
        raise Exception("No hay registros en la base de datos ANTERIOR.")
    # Insertar registros en la base de datos NUEVA
    contador = 0
    insert_query = """
        INSERT INTO pag_tramites_servicios (id, clave, descripcion, costo, url, estatus, creado, modificado, es_activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true)
    """
    try:
        for row in rows:
            clave = row[0]  # La clave es la primer columna
            # Consultar si el registro ya existe
            cursor_new.execute("SELECT id FROM pag_tramites_servicios WHERE clave = %s", (clave,))
            if cursor_new.fetchone():
                continue  # Ya existe, se omite
            # Insertar
            new_id = str(uuid.uuid4())
            cursor_new.execute(insert_query, (new_id, *row))
            contador += 1
    except Exception as error:
        raise Exception(f"Error al insertar {clave}: {error}")
    # Confirmar los cambios
    conn_new.commit()
    # Mensaje final
    return f"  {contador} pag_tramites_servicios copiados."


def copiar_pag_pagos(conn_old, cursor_old, conn_new, cursor_new) -> str:
    """Copiar tabla pag_pagos de la base de datos ANTERIOR a la NUEVA"""
    # Inicializar limit y offset para paginar la consulta de la base de datos ANTERIOR
    limit = 1000
    offset = 0
    contador = 0
    # Bucle para leer e insertar registros en lotes
    while True:
        # Leer registros en la base de datos ANTERIOR
        try:
            cursor_old.execute(
                """
                    SELECT
                        pag_pagos.id as id_original,
                        autoridades.clave AS autoridad_clave,
                        distritos.clave AS distrito_clave,
                        cit_clientes.email,
                        pag_tramites_servicios.clave AS pag_tramite_servicio_clave,
                        pag_pagos.caducidad,
                        pag_pagos.cantidad,
                        pag_pagos.descripcion,
                        pag_pagos.estado,
                        pag_pagos.email,
                        pag_pagos.folio,
                        pag_pagos.resultado_tiempo,
                        pag_pagos.resultado_xml,
                        pag_pagos.total,
                        pag_pagos.ya_se_envio_comprobante,
                        pag_pagos.estatus,
                        pag_pagos.creado,
                        pag_pagos.modificado
                    FROM
                        pag_pagos
                        JOIN autoridades ON pag_pagos.autoridad_id = autoridades.id
                        JOIN distritos ON pag_pagos.distrito_id = distritos.id
                        JOIN cit_clientes ON pag_pagos.cit_cliente_id = cit_clientes.id
                        JOIN pag_tramites_servicios ON pag_pagos.pag_tramite_servicio_id = pag_tramites_servicios.id
                    ORDER BY pag_pagos.id ASC
                    LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cursor_old.fetchall()
        except Exception as error:
            raise Exception(f"Error al leer registros de la BD ANTERIOR: {error}")
        # Si no hay más registros, salir del ciclo
        if not rows:
            break
        # Insertar registros en la base de datos NUEVA
        insert_query = """
            INSERT INTO pag_pagos (id, id_original,
                autoridad_id,
                distrito_id,
                cit_cliente_id,
                pag_tramite_servicio_id,
                caducidad, cantidad, descripcion, estado, email,
                folio, resultado_tiempo, resultado_xml, total, ya_se_envio_comprobante,
                estatus, creado, modificado)
            VALUES (%s, %s,
                (SELECT id FROM autoridades WHERE clave = %s),
                (SELECT id FROM distritos WHERE clave = %s),
                (SELECT id FROM cit_clientes WHERE email = %s),
                (SELECT id FROM pag_tramites_servicios WHERE clave = %s),
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s)
        """
        try:
            for row in rows:
                id_original = row[0]  # El id_original es la primer columna
                # Consultar si el registro ya existe
                cursor_new.execute("SELECT id FROM pag_pagos WHERE id_original = %s", (id_original,))
                if cursor_new.fetchone():
                    continue  # Ya existe, se omite
                # Insertar
                new_id = str(uuid.uuid4())
                cursor_new.execute(insert_query, (new_id, *row))
                contador += 1
        except Exception as error:
            raise Exception(f"Error al insertar {id_original}: {error}")
        # Confirmar los cambios
        conn_new.commit()
        # Incrementar offset para la siguiente página
        offset += limit
    # Mensaje final
    return f"  {contador} pag_pagos copiados."


migrar = Typer()


@migrar.command()
def copiar():
    """Copiar registros de la base de datos ANTERIOR a la NUEVA"""
    console = Console()
    try:
        # Conectar a la base de datos ANTERIOR
        conn_old = psycopg2.connect(
            dbname=OLD_DB_NAME,
            user=OLD_DB_USER,
            password=OLD_DB_PASS,
            host=OLD_DB_HOST,
            port=OLD_DB_PORT,
        )
        cursor_old = conn_old.cursor()
    except Exception as error:
        console.print(f"[red]Error al conectar a la BD ANTERIOR:[/red] {error}")
        return
    try:
        # Conectar a la base de datos NUEVA
        conn_new = psycopg2.connect(
            dbname=NEW_DB_NAME,
            user=NEW_DB_USER,
            password=NEW_DB_PASS,
            host=NEW_DB_HOST,
            port=NEW_DB_PORT,
        )
        cursor_new = conn_new.cursor()
    except Exception as error:
        console.print(f"[red]Error al conectar a la BD NUEVA:[/red] {error}")
        return
    # Ejecutar las copias en el orden correcto
    try:
        console.print("[cyan]Copiando tabla cit_dias_inhabiles...[/cyan]")
        mensaje = copiar_cit_dias_inhabiles(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla distritos...[/cyan]")
        mensaje = copiar_distritos(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla autoridades...[/cyan]")
        mensaje = copiar_autoridades(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla domicilios...[/cyan]")
        mensaje = copiar_domicilios(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla oficinas...[/cyan]")
        mensaje = copiar_oficinas(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla cit_categorias...[/cyan]")
        mensaje = copiar_cit_categorias(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla cit_servicios...[/cyan]")
        mensaje = copiar_cit_servicios(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla cit_oficias_servicios...[/cyan]")
        mensaje = copiar_cit_oficinas_servicios(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla cit_clientes...[/cyan]")
        mensaje = copiar_cit_clientes(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla cit_clientes_recuperaciones...[/cyan]")
        mensaje = copiar_cit_clientes_recuperaciones(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla cit_clientes_registros...[/cyan]")
        mensaje = copiar_cit_clientes_registros(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla cit_citas...[/cyan]")
        mensaje = copiar_cit_citas(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla pag_tramites_servicios...[/cyan]")
        mensaje = copiar_pag_tramites_servicios(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
        console.print("[cyan]Copiando tabla pag_pagos[/cyan]")
        mensaje = copiar_pag_pagos(conn_old, cursor_old, conn_new, cursor_new)
        console.print(f"[green]{mensaje}[/green]")
    except Exception as error:
        console.print(f"[yellow]{error}[/yellow]")
        return
    # Cerrar las conexiones (si no se cerraron ya en las funciones)
    try:
        cursor_old.close()
        conn_old.close()
        cursor_new.close()
        conn_new.close()
    except Exception:
        pass
