from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.urls import reverse
from home.utils import get_mapping_or_error, find_compatible_connectors
from .models import *
from .models_harness import Conexiones
from django_eventstream import send_event
from datetime import datetime
from .hardware.commander import Commander
from .hardware.ut61eplus import UT61EPLUS

import pyodbc
import sqlite3
import pandas as pd
import os
import json
import uuid
import shutil
import random
import re



def index(request):
    return render(request, 'pages/index.html')


def update_db(request):
    context = {
        'parent': '',
        'segment': 'edit_db'
    }
    return render(request, 'pages/update-db.html', context)


def edit_db(request):
    context = {
        'parent': '',
        'segment': 'edit_db'
    }
    return render(request, 'pages/edit-db.html', context)


def getDatabases(request):
    registros = MDBFile.objects.using("default").all()
    
    data = [
        {
            "upload_date": r.upload_date.strftime("%d/%m/%y %H:%M"),
            "file": r.file.name if r.file else None,  # Devuelve solo el nombre del archivo
            "version": r.version,
            "created_records": r.created_records,
        }
        for r in registros
    ]
    return JsonResponse({"data": data})


def editConexionesHarness(request):
    # en vez de values se puede utilizar .only para generar la estructura como getDatabases.
    data = list(Conexiones.objects.using("harness").values(
        'field_de_señal', 
        'nombre', 
        'tipo_señal', 
        'PEM_Polaridad', 
        'PEM_Telemetria'
    ))
    return JsonResponse({"data": data})


def saveConexionesHarness(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            field_de_senal = data.get("field_de_señal")
            column = data.get("column")
            new_value = data.get("value").strip() if data.get("value") else None

            print(f"Recibido: {data}")  # Debugging

            allowed_fields = ["tipo_señal", "PEM_Polaridad", "PEM_Telemetria"]
            if column not in allowed_fields:
                return JsonResponse({"message": f"Campo '{column}' no es editable", "type": "warning"}, status=400)

            obj = Conexiones.objects.using("harness").get(field_de_señal=field_de_senal)

            if obj:
                current_value = getattr(obj, column)

                # Normalizar valores: None en BD equivale a "" en el frontend
                if current_value is None:
                    current_value = ""

                # Evitar guardar si el nuevo valor es igual al actual
                if (new_value is None and current_value == "") or str(current_value).strip() == new_value:
                    return JsonResponse({"message": "No se realizaron cambios", "type": "info"}, status=200)

                # Guardar como NULL si está vacío
                setattr(obj, column, new_value)
                obj.save(using="harness")

                return JsonResponse({"message": "Actualización exitosa", "type": "success"}, status=200)

            return JsonResponse({"message": "Registro no encontrado", "type": "danger"}, status=404)

        except Exception as e:
            return JsonResponse({"message": str(e), "type": "danger"}, status=500)

    return JsonResponse({"message": "Método no permitido", "type": "danger"}, status=405)


def getLastDbUpdate(request):
    # Obtener la fecha más reciente
    latest_file = MDBFile.objects.using("default").order_by('-upload_date').first()
    
    if latest_file:
        # Formatear la fecha en un formato legible (opcional)
        latest_date = latest_file.upload_date.strftime("%d/%m/%Y %H:%M")
    else:
        latest_date = None  # Si no hay archivos, devolver None
    
    # Devolver la fecha como JSON
    return JsonResponse({"latest_upload_date": latest_date})


def backup_harness():
    """Crea una copia de seguridad de harness.sqlite3 con fecha e ID único."""
    try:
        fecha = datetime.now().strftime("%Y-%m-%d")
        unique_id = uuid.uuid4().hex[:6]
        backup_name = f"harness_backup_{fecha}_{unique_id}.sqlite3"
        backup_path = os.path.join(settings.MEDIA_ROOT, "backups", backup_name)
        harness_path = os.path.join(settings.BASE_DIR, "harness.sqlite3")

        # Verificar si harness.sqlite3 existe
        if not os.path.exists(harness_path):
            send_event("dbupdate", "message", {"status": "error", "text": f"Error: No se encontró la base de datos en {harness_path}"})
            return None

        # Crear la carpeta si no existe
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        # Realizar la copia de seguridad
        shutil.copy2(harness_path, backup_path)
        send_event("dbupdate", "message", {"status": "success", "text": f"Copia de seguridad creada en: /media/backups/{backup_name}"})

        return backup_path
    except Exception as e:
        send_event("dbupdate", "message", {"status": "error", "text": f"Error creando backup: {e}"})
        return None
    
    
@csrf_exempt
def backup_harness_ajax(request):
    if request.method == "POST":
        backup_path = backup_harness()
        if backup_path:
            file_name = os.path.basename(backup_path);
            return JsonResponse({"status": "success", "message": "Copia de seguridad creada correctamente.", "backup_name": file_name})
        return JsonResponse({"status": "error", "message": "Error al crear la copia de seguridad."}, status=500)
    return JsonResponse({"status": "error", "message": "Método no permitido."}, status=405)


def convert_mdb_to_sqlite(mdb_path, sqlite_path, sqlite_name):
    """
    Convierte un archivo de base de datos Microsoft Access (.mdb o .accdb) a formato SQLite (.sqlite3),
    copiando todas las tablas y sus datos.

    Parámetros:
    ----------
    mdb_path : str
        Ruta al archivo .mdb (Microsoft Access) de origen.
    
    sqlite_path : str
        Ruta de destino donde se guardará el archivo .sqlite3 generado.
    
    sqlite_name : str
        Nombre del archivo SQLite (utilizado únicamente para mostrar en el mensaje final).

    Retorna:
    -------
    str
        Ruta completa donde fue guardado el archivo SQLite (`sqlite_path`).

    Comportamiento:
    --------------
    - Establece conexión con el archivo `.mdb` usando ODBC.
    - Recupera la lista de todas las tablas de tipo "TABLE".
    - Por cada tabla:
        - Lee su contenido completo con `pandas.read_sql`.
        - La exporta a SQLite usando `df.to_sql`, reemplazando si ya existía.
        - Emite eventos informativos con `send_event`.
    - Informa si hubo errores de conexión o durante la exportación de cada tabla.

    Dependencias:
    ------------
    - `pyodbc`: para conectar con la base de datos Access.
    - `pandas`: para convertir datos a DataFrame y exportar a SQLite.
    - `sqlite3`: módulo estándar para conexión con SQLite.
    - `send_event(event_type, event_subtype, payload)`: función externa usada para informar estado del proceso.

    Notas:
    -----
    - El parámetro `sqlite_name` se usa solo para fines informativos (en logs o mensajes).
    - Si alguna tabla falla durante la exportación, las demás continúan siendo procesadas.
    - El archivo SQLite generado reemplazará cualquier archivo existente en `sqlite_path`.

    Excepciones:
    -----------
    - Lanza una excepción si falla la conexión al archivo Access.
    """
    
    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_path}"
    try:
        access_conn = pyodbc.connect(conn_str)
        cursor = access_conn.cursor()
    except pyodbc.Error as e:
        send_event("dbupdate", "message", {"status": "error", "text": f"Error al conectar a Access"})
        raise Exception(f"Error al conectar a Access: {e}")
    
    sqlite_conn = sqlite3.connect(sqlite_path)
    tables = [row.table_name for row in cursor.tables(tableType="TABLE")]
    send_event("dbupdate", "message", {"status": "info", "text": f"Tablas encontradas: {tables}"})
    
    for table in tables:
        try:
            df = pd.read_sql(f"SELECT * FROM {table}", access_conn)
            df.to_sql(table, sqlite_conn, if_exists="replace", index=False)
            send_event("dbupdate", "message", {"status": "info", "text": f"Exportado: {table}"})
        except Exception as e:
            send_event("dbupdate", "message", {"status": "error", "text": f"Error exportando {table}: {e}"})
    
    send_event("dbupdate", "message", {"status": "success", "text": f"SQLite creado en: media/sqlite_files/{sqlite_name}"})
    access_conn.close()
    sqlite_conn.close()
    return sqlite_path


def get_last_signal_number(db_path, table_name):
    """Obtiene el último '# de Señal' registrado en una tabla."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT MAX(\"# de Señal\") FROM {table_name}")
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0


def sync_databases(harness_path, new_db_path, sqlite_name):
    """
    Sincroniza datos de una base SQLite nueva (`new_db_path`) hacia la base principal (`harness_path`),
    sin sobrescribir ni modificar registros existentes.

    La sincronización se basa en el campo `# de Señal`, asumiendo que es un identificador numérico incremental.
    Solo se copian los registros que estén en la base nueva y tengan un `# de Señal` mayor que el último en la base original.

    Parámetros:
    ----------
    harness_path : str
        Ruta al archivo `harness.sqlite3`, base de datos principal donde se insertarán los nuevos registros.
    
    new_db_path : str
        Ruta al archivo SQLite desde donde se copiarán los datos nuevos.
    
    sqlite_name : str
        Nombre del archivo SQLite nuevo (actualmente no se utiliza dentro de la función, pero podría usarse para logs o validaciones externas).

    Retorna:
    -------
    int
        Cantidad total de registros nuevos insertados en la base `harness_path`.

    Comportamiento:
    --------------
    - Recorre todas las tablas existentes en `new_db_path`.
    - Compara el último valor de `# de Señal` en cada tabla de ambas bases.
    - Si `new_db_path` tiene registros más nuevos, los copia a `harness_path`.
    - Emite eventos de estado mediante `send_event` para indicar progreso o resultados.
    - No borra ni actualiza registros existentes.
    
    Dependencias:
    ------------
    - `get_last_signal_number(db_path, table)`: función externa que retorna el valor máximo de `# de Señal` en una tabla dada.
    - `send_event(event_type, event_subtype, payload)`: función externa para emitir mensajes de estado al sistema o a la interfaz.

    Notas:
    -----
    - Se asume que todas las tablas en ambas bases tienen una columna `# de Señal`.
    - No se realiza validación del esquema entre bases. Ambas deben tener estructuras compatibles.
    - La variable `sqlite_name` no se utiliza dentro de la función y puede eliminarse si no se necesita externamente.
    """
    #modifications_made = False
    total_new_records = 0
    with sqlite3.connect(harness_path) as conn_harness, sqlite3.connect(new_db_path) as conn_new:
        cursor_harness = conn_harness.cursor()
        cursor_new = conn_new.cursor()
        
        cursor_new.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor_new.fetchall()]
        
        for table in tables:
            last_signal_harness = get_last_signal_number(harness_path, table)
            last_signal_new = get_last_signal_number(new_db_path, table)
            
            if last_signal_new > last_signal_harness:
                #modifications_made = modifications_made or True #Si es false le asigna true
                send_event("dbupdate", "message", {"status": "info", "text": f"Actualizando {table}..."})
                
                cursor_new.execute(f"SELECT * FROM {table} WHERE \"# de Señal\" > ?", (last_signal_harness,))
                new_records = cursor_new.fetchall()
                
                if new_records:
                    cursor_new.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor_new.fetchall()]
                    columns_str = ', '.join(f'"{col}"' for col in columns)
                    placeholders = ', '.join(['?' for _ in columns])
                    insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                    
                    cursor_harness.executemany(insert_query, new_records)
                    conn_harness.commit()
                    
                    new_rec_qty = len(new_records)
                    total_new_records += new_rec_qty
                    send_event("dbupdate", "message", {"status": "success", "style": "success", "text": f"{new_rec_qty} registros añadidos en {table}"})
                             
        if not total_new_records:
             send_event("dbupdate", "message", {"status": "info", "style": "info", "text": f"No se agregaron registros en ninguna tabla"}) 
             
    return total_new_records
    
    
@csrf_exempt
def upload_mdb(request):
    if request.method != 'POST':
        return
        #return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    
    try:
        uploaded_file = request.FILES.get('file')
        data = json.loads(request.POST.get('data', '{}'))
        name = data.get('inputNameValue')
        version = data.get('inputVersionValue')
        
        if not uploaded_file:
            send_event("dbupdate", "message", {"status": "error", "text": f"Ocurrio un error al subir el archivo .mdb"})
            return JsonResponse({'success': False, 'message': 'Ocurrio un error al subir el archivo .mdb'}, status=400)
        
        mdb_file = MDBFile(file=uploaded_file, name=name, version=version, created_records=0)
        mdb_file.save(using="default")
        
        mdb_path = os.path.join(settings.MEDIA_ROOT, mdb_file.file.name)
        sqlite_name = os.path.splitext(os.path.basename(mdb_file.file.name))[0] + ".sqlite3"
        sqlite_path = os.path.join(settings.MEDIA_ROOT, "sqlite_files", sqlite_name)
        
        send_event("dbupdate", "message", {"status": "success", "text": f"MDB guardado en: media/{mdb_file.file.name}"})
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        
        # Enviar mensaje inicial
        send_event("dbupdate", "message", {"status": "info", "text": f"Iniciando conversión de MDB a SQLite"})
        convert_mdb_to_sqlite(mdb_path, sqlite_path, sqlite_name)
        
        
        send_event("dbupdate", "message", {"status": "info", "text": f"Creando backup de harness.sqlite3"})
        backup_path = backup_harness()

        if not backup_path:
            send_event("dbupdate", "message", {"status": "error", "text": f"Error creando copia de seguridad"})
            return JsonResponse({'success': False, 'message': 'Error creando copia de seguridad.'}, status=500)
        
        send_event("dbupdate", "message", {"status": "info", "text": f"Sincronizando bases de datos"})

        total_new_records = sync_databases(os.path.join(settings.BASE_DIR, "harness.sqlite3"), sqlite_path, sqlite_name)

        mdb_file.created_records = total_new_records
        mdb_file.save(update_fields=['created_records'], using="default")

        send_event("dbupdate", "message", {"status": "success", "text": f"Proceso completado"})
        return JsonResponse({'success': True, 'message': 'Proceso completado'}, status=200)
    except Exception as e:
        send_event("dbupdate", "message", {"status": "error", "text": f"Error: {e}"})
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    
def get_unique_connectors():
    connectors = Conexiones.objects.using("harness").exclude(activo_si_no_field="no").values_list("conector_orig", flat=True)
    connectors_dest = Conexiones.objects.using("harness").exclude(activo_si_no_field="no").values_list("conector_dest", flat=True)

    # Unificar, eliminar None y duplicados
    unique_connectors = sorted(set(filter(None, connectors)).union(set(filter(None, connectors_dest))))

    return unique_connectors


def api_connector_types(request):
    unique_types = get_unique_connector_types()
    return JsonResponse([{"value": t, "text": t} for t in unique_types], safe=False)


def get_unique_connector_types():
    EXCLUDED_VALUES = {"TBD", "NA(ladocaja)", None}

    connectors_orig_type = Conexiones.objects.using("harness") \
        .exclude(activo_si_no_field="no") \
        .values_list("tipo_de_con_orig", flat=True)

    connectors_dest_type = Conexiones.objects.using("harness") \
        .exclude(activo_si_no_field="no") \
        .values_list("tipo_de_con_dest", flat=True)

    # Unificar, eliminar duplicados y los valores excluidos
    all_connectors = set(connectors_orig_type).union(set(connectors_dest_type))
    unique_connector_types = sorted([c for c in all_connectors if c not in EXCLUDED_VALUES])

    return unique_connector_types


def get_letter_to_number_mapping():
    letter_to_number = {}

    # A-Z → 1-26
    for i in range(26):
        letter_to_number[chr(65 + i)] = i + 1  # A=1, B=2, ..., Z=26

    # a-z → 27-52
    for i in range(26):
        letter_to_number[chr(97 + i)] = i + 27  # a=27, b=28, ..., z=52

    # AA-ZZ → 53-78
    for i in range(26):
        letter_to_number[chr(65 + i) * 2] = i + 53  # AA=53, BB=54, ..., ZZ=78

    return letter_to_number

LETTER_TO_NUMBER = get_letter_to_number_mapping()

def expand_values(value):
    expanded = []
    for item in value.split(","):
        item = item.strip()
        if item in LETTER_TO_NUMBER:
            expanded.append(str(LETTER_TO_NUMBER[item]))
        else:
            expanded.append(item)
    return expanded


def new_test(request):
    context = {
        'parent': '',
        'segment': 'new_test',
        'connectors': get_unique_connectors()
    }
    
    if request.method == "POST":
        connector = request.POST.get("connector").strip() if request.POST.get("connector") else None
        test_type = request.POST.get("test_type")
        
        if not connector or not test_type:
            return render(request, 'pages/new-test.html', {
                "error": "Todos los campos son obligatorios",
                "connectors": get_unique_connectors()
            })

        valid_test_types = ["Pin a chasis", "Pin a otros", "Entre par de pines", "Pin a pin"]
        
        if test_type not in valid_test_types:
            return render(request, 'pages/new-test.html', {
                "error": "Tipo de prueba no válido",
                "connectors": get_unique_connectors()
            })

        with transaction.atomic():
            # Obtener tipo de conector desde la base "harness"
            first_con = Conexiones.objects.using("harness").filter(
                conector_orig=connector
            ).exclude(activo_si_no_field="no").first() or Conexiones.objects.using("harness").filter(
                conector_dest=connector
            ).exclude(activo_si_no_field="no").first()

            connector_type = first_con.tipo_de_con_orig if first_con and first_con.conector_orig == connector else first_con.tipo_de_con_dest if first_con else ""

            # Crear una nueva sesión de prueba
            session = TestSession.objects.create(
                connector=connector,
                test_type=test_type,
                connector_type=connector_type or ""
            )
            
            # Filtrar señales que involucran el conector seleccionado (origen o destino)
            connections = Conexiones.objects.using("harness").filter(
                conector_orig=connector
            ).exclude(activo_si_no_field="no") | Conexiones.objects.using("harness").filter(
                conector_dest=connector
            ).exclude(activo_si_no_field="no")

            # Agrupar conexiones por conector destino
            etapas = {}
            for conn in connections:
                destino = conn.conector_dest if conn.conector_orig == connector else conn.conector_orig
                if destino not in etapas:
                    etapas[destino] = []
                etapas[destino].append(conn)
                
            # Definir valores esperados según el tipo de prueba
            expected_values = {
                "Pin a chasis": (100000000, "OL"),
                "Pin a otros": (100000000, "OL"),
                "Pin a pin": (0, 1)
            }

            min_expected, max_expected = expected_values.get(test_type, (None, None))

            for i, (dest, signals) in enumerate(etapas.items(), start=1):
                # Obtener tipo de conector destino (si se conoce)
                tipo_destino = signals[0].tipo_de_con_dest if signals[0].conector_dest == dest else signals[0].tipo_de_con_orig

                # Crear etapas "reference" y "test"
                reference_stage = TestStage.objects.create(
                    session=session,
                    stage_number=i,
                    stage_type='reference',
                    connector_dest=dest,
                    connector_type=tipo_destino or "",
                    instructions=f"Conectar {connector} y {dest} para ejecutar la prueba.",
                )
                
                test_stage = TestStage.objects.create(
                    session=session,
                    stage_number=i,
                    stage_type='test',
                    connector_dest=dest,
                    connector_type=tipo_destino or "",
                    instructions=f"Conectar {connector} y {dest} para ejecutar la prueba.",
                )
                
                result_created = False
                
                for signal in signals:
                    # Crear TestResult de referencia sin normalización
                    TestResult.objects.create(
                        stage=reference_stage,
                        signal_id=signal.field_de_señal,
                        signal_name=signal.nombre,
                        signal_type=signal.tipo_señal,
                        conector_orig=signal.conector_orig,
                        conector_orig_type=signal.tipo_de_con_orig or "",
                        pin_a=signal.pin_orig or "N/A",
                        conector_dest=signal.conector_dest,
                        conector_dest_type=signal.tipo_de_con_dest or "",
                        pin_b=signal.pin_dest or "N/A",
                        min_exp_value=min_expected or "0",
                        max_exp_value=max_expected or "0",
                    )
                    
                    # Validación de pines
                    pin_a_raw = signal.pin_orig or "N/A"
                    pin_b_raw = signal.pin_dest or "N/A"

                    invalid_values = {"TBD", "TBD*", "TBC", "TBC*", "---", "---*", "-", "+"}
                    if pin_a_raw in invalid_values or pin_b_raw in invalid_values:
                        continue

                    # Normalización de pines
                    clean_pin_a = pin_a_raw.replace("*", "").replace("(", "").replace(")", "")
                    clean_pin_b = pin_b_raw.replace("*", "").replace("(", "").replace(")", "")

                    # Separar pines por coma si vienen agrupados
                    pin_a_parts = [p.strip() for p in clean_pin_a.split(",")]
                    pin_b_parts = [p.strip() for p in clean_pin_b.split(",")]

                    for original_a in pin_a_parts:
                        mapped_a = str(LETTER_TO_NUMBER.get(original_a, original_a))
                        for original_b in pin_b_parts:
                            mapped_b = str(LETTER_TO_NUMBER.get(original_b, original_b))

                            # Crear resultado de prueba con valores mapeados y tooltips
                            TestResult.objects.create(
                                stage=test_stage,
                                signal_id=signal.field_de_señal,
                                signal_name=signal.nombre,
                                signal_type=signal.tipo_señal,
                                conector_orig=signal.conector_orig,
                                conector_orig_type=signal.tipo_de_con_orig or "",
                                pin_a=mapped_a,
                                tooltip_a=original_a,
                                conector_dest=signal.conector_dest,
                                conector_dest_type=signal.tipo_de_con_dest or "",
                                pin_b=mapped_b,
                                tooltip_b=original_b,
                                min_exp_value=min_expected or "0",
                                max_exp_value=max_expected or "0",
                                result="pending",
                            )
                            
                            result_created = True
                    
                # Marcar etapa como no medible si no se creó ningún resultado
                if not result_created:
                    test_stage.status = 'unmeasurable'
                    test_stage.save()
                    reference_stage.status = 'unmeasurable'
                    reference_stage.save()
                            
            # Verificar si toda la sesión quedó sin resultados medibles
            test_stages = session.stages.filter(stage_type='test')
            has_results = any(stage.results.exists() for stage in test_stages)

            if not has_results:
                session.status = 'unmeasurable'
                session.save()
                            
        return redirect("test_preview", session_id=session.id)
    
    return render(request, 'pages/new-test.html', context)

    
def test_log(request):
    context = {
        "parent": "",
        "segment": "test_log",
        'connectors': get_unique_connectors()
    }

    # Obtener todas las sesiones de prueba agrupadas por conector
    test_sessions = TestSession.objects.using("default").all().order_by("-created_at")
    
    grouped_sessions = {}
    for session in test_sessions:
        if session.connector not in grouped_sessions:
            grouped_sessions[session.connector] = []

        # Contar cuántos TestStage tiene cada sesión
        session.teststage_count = session.stages.filter(stage_type='test').count()
        
        grouped_sessions[session.connector].append(session)

    context["grouped_sessions"] = grouped_sessions

    return render(request, "pages/test-log.html", context)


@csrf_exempt
def delete_test_session(request, session_id):
    if request.method == "POST":
        session = get_object_or_404(TestSession, id=session_id)
        session.delete()
        return JsonResponse({"success": True, "message": "Sesión eliminada correctamente."})
    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)


def test_preview_view(request, session_id):
    session = get_object_or_404(TestSession, id=session_id)

    # Obtener todas las etapas test y reference, agrupadas por stage_number
    all_stages = session.stages.all().select_related().order_by("stage_number", "stage_type")

    # Separar por tipo
    reference_stages = {s.stage_number: s for s in all_stages if s.stage_type == "reference"}
    test_stages = {s.stage_number: s for s in all_stages if s.stage_type == "test"}

    # Generar pares (reference_stage, test_stage)
    stage_numbers = sorted(set(reference_stages) | set(test_stages))
    stage_pairs = [(reference_stages.get(n), test_stages.get(n)) for n in stage_numbers]

    # Para el breadcrumb
    all_test_stages = list(test_stages.values())
    stage_links = []
    for stage in all_test_stages:
        stage_links.append({
            "id": stage.id,
            "stage_number": stage.stage_number,
            "result_count": stage.results.count()
        })

    context = {
        "session": session,
        "stage_pairs": stage_pairs,
        "stages_count": len(all_test_stages),
        "all_test_stages": all_test_stages,
        "stage_links": stage_links,
    }

    return render(request, "pages/test-preview.html", context)

    
def test_stage_view(request, session_id, stage_id):
    session = get_object_or_404(TestSession, id=session_id)

    # Etapa de prueba actual (stage_type = 'test') desde URL
    stage_test = get_object_or_404(TestStage, id=stage_id, session=session, stage_type='test')

    # Etapa de referencia asociada (mismo stage_number)
    stage_reference = get_object_or_404(
        TestStage,
        session=session,
        stage_number=stage_test.stage_number,
        stage_type='reference'
    )

    # Todas las etapas de tipo test (para breadcrumbs/paginador)
    all_test_stages = list(session.stages.filter(stage_type='test').order_by('stage_number'))

    # Diccionario de navegación para breadcrumb: stage_number -> stage_id (test)
    test_stage_map = {stage.stage_number: stage.id for stage in all_test_stages}

    # Obtener etapas anterior y siguiente
    prev_stage = session.stages.filter(stage_type='test', stage_number=stage_test.stage_number - 1).first()
    next_stage = session.stages.filter(stage_type='test', stage_number=stage_test.stage_number + 1).first()

    prev_stage_id = prev_stage.id if prev_stage else None
    prev_stage_number = prev_stage.stage_number if prev_stage else None
    next_stage_id = next_stage.id if next_stage else None
    next_stage_number = next_stage.stage_number if next_stage else None

    # Traer todos los resultados en una sola consulta
    results = TestResult.objects.filter(stage__in=[stage_reference, stage_test]).select_related("stage")

    # Separar por tipo
    reference_results = [r for r in results if r.stage_id == stage_reference.id]
    test_results = [r for r in results if r.stage_id == stage_test.id]

    # Formateo para mostrar
    formatted_test_results = [
        {
            "id": r.id,  
            "signal_id": r.signal_id,
            "signal_name": r.signal_name,
            "signal_type": r.signal_type,
            "conector_orig": r.conector_orig,
            "conector_orig_type": r.conector_orig_type,
            "pin_a": r.pin_a,
            "tooltip_a": r.tooltip_a or "",
            "conector_dest": r.conector_dest,
            "conector_dest_type": r.conector_dest_type,
            "pin_b": r.pin_b,
            "tooltip_b": r.tooltip_b or "",
            "min_exp_value": r.min_exp_value,
            "max_exp_value": r.max_exp_value,
            "measured_value": r.measured_value,
            "result": r.result,
            "result_display": r.get_result_display(),
            "timestamp": r.timestamp,
        }
        for r in test_results
    ]

    formatted_reference_results = [
        {
            "signal_id": r.signal_id,
            "signal_name": r.signal_name,
            "signal_type": r.signal_type,
            "conector_orig": r.conector_orig,
            "conector_orig_type": r.conector_orig_type,
            "pin_a": r.pin_a,
            "conector_dest": r.conector_dest,
            "conector_dest_type": r.conector_dest_type,
            "pin_b": r.pin_b,
            "min_exp_value": r.min_exp_value,
            "max_exp_value": r.max_exp_value,
            "measured_value": r.measured_value,
            "result": r.result,
            "result_display": r.get_result_display(),
            "timestamp": r.timestamp,
        } for r in reference_results
    ]

    context = {
        "session": session,
        "stage_test": stage_test,
        "stage_reference": stage_reference,
        "test_results": formatted_test_results,
        "reference_results": formatted_reference_results,
        "prev_stage_id": prev_stage_id,
        "prev_stage_number": prev_stage_number,
        "next_stage_id": next_stage_id,
        "next_stage_number": next_stage_number,
        "all_test_stages": all_test_stages,
        "test_stage_map": test_stage_map,
    }
    return render(request, "pages/test-stage.html", context)


def test_result_view(request, session_id):
    session = get_object_or_404(TestSession, id=session_id)

    # Obtener todas las etapas test y reference, agrupadas por stage_number
    all_stages = session.stages.all().select_related().order_by("stage_number", "stage_type")

    # Separar por tipo
    reference_stages = {s.stage_number: s for s in all_stages if s.stage_type == "reference"}
    test_stages = {s.stage_number: s for s in all_stages if s.stage_type == "test"}

    # Generar pares (reference_stage, test_stage)
    stage_numbers = sorted(set(reference_stages) | set(test_stages))
    stage_pairs = [(reference_stages.get(n), test_stages.get(n)) for n in stage_numbers]

    # Para el breadcrumb
    all_test_stages = list(test_stages.values())
    test_stage_map = {stage.stage_number: stage.id for stage in all_test_stages}
    
    stage_links = []
    for stage in all_test_stages:
        stage_links.append({
            "id": stage.id,
            "stage_number": stage.stage_number,
            "result_count": stage.results.count()
        })

    context = {
        "session": session,
        "stage_pairs": stage_pairs,
        "stages_count": len(all_test_stages),
        "all_test_stages": all_test_stages,
        "stage_links": stage_links,
    }
    return render(request, "pages/test-result.html", context)



def test_hardware(request):
    cmder = Commander("tcp://10.245.1.103:9194", 5000)  # IP de PC PXI
    card = 1
    bus = 25
    dev = 8

    log = []  # Para registrar los resultados de cada comando

    try:
        res_open = cmder.pik_open(card, bus, dev)
        log.append({"comando": "pik_open", "resultado": res_open})

        # Si el resultado es False y NO contiene "Already Open", detener con error
        if isinstance(res_open, (list, tuple)):
            success, mensaje = res_open
            if not success and "Already Open" not in str(mensaje):
                return JsonResponse({
                    "status": "error",
                    "message": "Error al intentar iniciar la conexión con la placa",
                    "detalle": mensaje,
                    "log": log
                }, status=500)
        else:
            # En caso de que `pik_open` no devuelva una tupla (por seguridad)
            return JsonResponse({
                "status": "error",
                "message": "Formato de respuesta inesperado al intentar iniciar la conexión con la placa",
                "log": log
            }, status=500)

        res_clear = cmder.pik_clear_card('1')
        log.append({"comando": "pik_clear_card", "resultado": res_clear})

        success1, result1 = cmder.pik_op_bit("1", "3", "1", "1")
        log.append({
            "comando": 'pik_op_bit("1", "3", "1", "1")',
            "success": success1,
            "resultado": result1
        })

        success2, result2 = cmder.pik_op_bit("1", "7", "1", "1")
        log.append({
            "comando": 'pik_op_bit("1", "7", "1", "1")',
            "success": success2,
            "resultado": result2
        })

        if success2:
            return JsonResponse({
                "status": "ok",
                "message": "Conexión exitosa con la placa.",
                "log": log
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Falló la comunicación con la placa.",
                "log": log
            }, status=500)

    except Exception as e:
        log.append({"comando": "error", "resultado": str(e)})
        return JsonResponse({
            "status": "error",
            "message": f"Error inesperado: {str(e)}",
            "log": log
        }, status=500)



def hardware(request):
    ip_config = GlobalConfig.objects.filter(key="ip_port").first()
    context = {
        'parent': '',
        'segment': 'hardware',
        'connection_config': ip_config  # esto sigue funcionando en el template
    }
    return render(request, 'pages/hardware-admin.html', context)


@csrf_exempt
def api_save_hardware_edit(request):

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            model_name = data.get("model")
            pk = data.get("id")
            field = data.get("field")
            value = data.get("value")

            model = apps.get_model("home", model_name)
            obj = model.objects.get(pk=pk)
            
            if not field or not isinstance(field, str) or field is None:
                return JsonResponse({"message": "Campo 'field' inválido o faltante", "type": "danger"}, status=400)

            setattr(obj, field, value)
            obj.save()

            return JsonResponse({"message": "Actualizado con éxito", "type": "success"})
        except Exception as e:
            return JsonResponse({"message": str(e), "type": "danger"}, status=500)

   
@csrf_exempt
def api_create_hardware_record(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            model_name = data.get("model")
            fields = data.get("fields", {})
            model = apps.get_model("home", model_name)

            obj = model.objects.create(**fields)

            return JsonResponse({
                "message": "Registro creado",
                "type": "success",
                "id": obj.pk
            })

        except IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                return JsonResponse({
                    "message": f"Ya existe un registro con ese nombre.",
                    "type": "danger"
                }, status=400)
            return JsonResponse({
                "message": "Error de integridad en la base de datos.",
                "type": "danger"
            }, status=400)

        except Exception as e:
            return JsonResponse({
                "message": str(e),
                "type": "danger"
            }, status=500)

    return JsonResponse({"message": "Método no permitido"}, status=405)


@csrf_exempt
def api_delete_hardware_record(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            model_name = data.get("model")
            pk = data.get("id")

            model = apps.get_model("home", model_name)
            obj = model.objects.get(pk=pk)
            obj.delete()

            return JsonResponse({"message": "Eliminado correctamente", "type": "success"})
        except Exception as e:
            return JsonResponse({"message": str(e), "type": "danger"}, status=500)
    return JsonResponse({"message": "Método no permitido"}, status=405)
       
       
def api_get_adapters(request):
    data = []

    for adapter in Adapter.objects.all():
        connectors = adapter.connectors.all()

        pxi_connectors = connectors.filter(connector_side='pxi-side').order_by('id')
        test_connectors = connectors.filter(connector_side='test-side').order_by('-id')

        def format_connectors(queryset):
            return "<br>".join(
                f"{pc.label} ({pc.connector_type})"
                for pc in queryset
            )

        data.append({
            "id": adapter.id,
            "name": adapter.name,
            "pxi_connectors": format_connectors(pxi_connectors),
            "test_connectors": format_connectors(test_connectors),
        })

    return JsonResponse({"data": data})


def api_get_relaycards(request):
    data = list(RelayCard.objects.all().values())
    return JsonResponse({"data": data})

def api_get_signaltypes(request):
    data = list(SignalTypesMaxMin.objects.all().values())
    return JsonResponse({"data": data})


def get_global_config():
    configs = GlobalConfig.objects.all()
    return {
        cfg.key: {
            "id": cfg.id,
            "value": cfg.value
        }
        for cfg in configs
    }


def api_get_global_config(request):
    data = get_global_config()
    return JsonResponse(data)


def api_list_adapterconnectors(request):
    adapter_id = request.GET.get("adapter")
    connectors = AdapterConnector.objects.filter(adapter_id=adapter_id).order_by('-id')

    data = []
    for c in connectors:
        data.append({
            "id": c.id,
            "label": c.label,
            "connector_type": c.connector_type,
            "pin_qty": c.pin_qty,
            "connector_side": c.connector_side,
            "connector_side_display": c.get_connector_side_display(),
        })

    return JsonResponse({"data": data})
    
    
@csrf_exempt
def api_create_adapter(request):
    name = request.POST.get("name", "").strip()

    if not name:
        return JsonResponse({"status": "error", "message": "El nombre es obligatorio."})

    if Adapter.objects.filter(name__iexact=name).exists():
        return JsonResponse({"status": "error", "message": "Ya existe un adaptador con ese nombre."})

    adapter = Adapter.objects.create(name=name)

    # Crear conectores PXI
    in_connectors = []
    out_connectors = []

    for i in range(1, 4):
        in_con = AdapterConnector.objects.create(
            adapter=adapter,
            connector_type="DB50F",
            label=f"DB-50-H-IN-{i}",
            pin_qty=50,
            connector_side="pxi-side"
        )
        in_connectors.append(in_con)

        out_con = AdapterConnector.objects.create(
            adapter=adapter,
            connector_type="DB50M",
            label=f"DB-50-M-OUT-{i}",
            pin_qty=50,
            connector_side="pxi-side"
        )
        out_connectors.append(out_con)

    relay_cards = RelayCard.objects.filter(name__in=["PXI-1", "PXI-2"])

    # Entradas (U)
    relay_maps_u = RelayPinMap.objects.filter(
        relay_card__in=relay_cards,
        pxi_channel_type='U'
    ).order_by('relay_card__name', 'pxi_channel')

    in_idx = 0
    in_pin = 1

    for rmap in relay_maps_u:
        if in_idx >= len(in_connectors):
            break
        AdapterPinMap.objects.create(
            adapter=adapter,
            relay_pin_map=rmap,
            pxi_connector=in_connectors[in_idx],
            to_pxi_pin=in_pin
        )
        in_pin += 1
        if in_pin > 50:
            in_idx += 1
            in_pin = 1

    # Salidas (M)
    relay_maps_m = RelayPinMap.objects.filter(
        relay_card__in=relay_cards,
        pxi_channel_type='M'
    ).order_by('relay_card__name', 'pxi_channel')

    out_idx = 0
    out_pin = 1

    for rmap in relay_maps_m:
        if out_idx >= len(out_connectors):
            break
        AdapterPinMap.objects.create(
            adapter=adapter,
            relay_pin_map=rmap,
            pxi_connector=out_connectors[out_idx],
            to_pxi_pin=out_pin
        )
        out_pin += 1
        if out_pin > 50:
            out_idx += 1
            out_pin = 1

    return JsonResponse({"status": "ok", "adapter_id": adapter.id})


def adapter_connectors_view(request, id):
    try:
        adapter = Adapter.objects.get(pk=id)
    except Adapter.DoesNotExist:
        return redirect("new_adapter_view")

    return render(request, "pages/adapter-connectors.html", {"adapter": adapter})


def adapter_connections_view(request, id):
    try:
        adapter = apps.get_model("home", "Adapter").objects.get(pk=id)
    except apps.get_model("home", "Adapter").DoesNotExist:
        return redirect("new_adapter_view")
    return render(request, "pages/adapter-connections.html", {"adapter": adapter})


def api_list_adapterpinmap(request):
    adapter_id = request.GET.get("adapter")
    qs = apps.get_model("home", "AdapterPinMap").objects.filter(adapter_id=adapter_id)
    data = []
    for m in qs:
        data.append({
            "id": m.id,
            "pxi_connector": f"{m.pxi_connector.label} ({m.pxi_connector.connector_type})",
            "to_pxi_pin": m.to_pxi_pin,
            "test_connector": m.test_connector.id if m.test_connector else None,
            "test_connector_display": (
                f"{m.test_connector.label} ({m.test_connector.connector_type})"
                if m.test_connector else ""
            ),
            "to_test_pin": m.to_test_pin,
            "pxi_channel_type": m.relay_pin_map.get_pxi_channel_type_display(), 
            "pxi_channel": m.relay_pin_map.pxi_channel,
            "relay_card_name": m.relay_pin_map.relay_card.name, 
        })
    return JsonResponse({"data": data})


@csrf_exempt
def api_save_adapterpinmap(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    data = json.loads(request.body)
    field, val, obj_id = data.get('field'), data.get('value'), data.get('id')

    if field not in ('test_connector', 'to_test_pin'):
        return JsonResponse({"error": "Campo no permitido"}, status=400)

    Model = apps.get_model("home", "AdapterPinMap")
    AdapterConnector = apps.get_model("home", "AdapterConnector")
    instance = get_object_or_404(Model, pk=obj_id)

    # Procesamiento de FK
    if field == 'test_connector':
        if val in (None, '', 'null'):
            val = None
        else:
            try:
                val = AdapterConnector.objects.get(pk=val)
            except (ValueError, AdapterConnector.DoesNotExist):
                return JsonResponse({"error": "Conector inválido"}, status=400)

    setattr(instance, field, val)

    try:
        instance.full_clean()
        print("DEBUG:", instance.test_connector, type(instance.test_connector))
        instance.save()
        return JsonResponse({"success": True})
    except ValidationError as e:
        msg = e.message_dict.get(field, e.messages)[0]
        return JsonResponse({"error": msg}, status=400)
    except IntegrityError:
        return JsonResponse({"error": "Combinación duplicada"}, status=400)


def api_create_adapterconnector(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            adapter_id = data.get("adapter_id")
            label = data.get("label", "").strip()
            connector_type = data.get("connector_type", "").strip()
            pin_qty = data.get("pin_qty")
            connector_side = "test-side"
            
            if not adapter_id or not connector_type or not label or not pin_qty:
                return JsonResponse({"type": "warning", "message": "Todos los campos son obligatorios."}, status=400)
                            
            try:
                pin_qty = int(pin_qty)
                if pin_qty <= 0:
                    raise ValueError()
            except ValueError:
                return JsonResponse({
                    "type": "warning",
                    "message": "La cantidad de pines debe ser un número entero positivo."
                })
                
            try:
                adapter = Adapter.objects.get(pk=adapter_id)
            except Adapter.DoesNotExist:
                return JsonResponse({
                    "type": "warning",
                    "message": "Adaptador no encontrado."
                })


            if AdapterConnector.objects.filter(adapter=adapter, label__iexact=label).exists():
                return JsonResponse({"message": "Este adaptador ya tiene un conector con esa etiqueta.", "type": "warning"}, status=400)

            connector = AdapterConnector.objects.create(
                adapter=adapter,
                connector_type=connector_type,
                label=label,
                pin_qty=pin_qty,
                connector_side=connector_side
            )
            
                
            return JsonResponse({
                "type": "success",
                "message": "Conector creado correctamente.",
                "id": connector.id
            })

        except Exception as e:
            return JsonResponse({"message": str(e), "type": "danger"}, status=500)

@csrf_exempt
def api_toggle_adapter_availability(request):
    try:
        data = json.loads(request.body)
        adapter_id = data.get("adapter_id")
        adapter = Adapter.objects.get(id=adapter_id)

        adapter.availability = not adapter.availability
        adapter.save()

        return JsonResponse({"success": True, "new_value": adapter.availability})
    except Adapter.DoesNotExist:
        return JsonResponse({"success": False, "message": "Adaptador no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

@csrf_exempt
def api_get_adapter_availability(request):
    adapter_id = request.GET.get("id")
    try:
        adapter = Adapter.objects.get(id=adapter_id)
        return JsonResponse({"success": True, "value": adapter.availability})
    except Adapter.DoesNotExist:
        return JsonResponse({"success": False, "message": "Adaptador no encontrado"}, status=404)


def api_get_fixedconnectors_availability(request):
    config = GlobalConfig.objects.filter(key="fixedconnectors_availability").first()
    is_enabled = config.value == "1" if config else False
    return JsonResponse({"enabled": is_enabled})


def api_toggle_fixedconnectors_availability(request):
    from django.views.decorators.csrf import csrf_exempt
    import json

    data = json.loads(request.body)
    enabled = data.get("enabled", False)

    config, _ = GlobalConfig.objects.get_or_create(key="fixedconnectors_availability")
    config.value = "1" if enabled else "0"
    config.save()

    return JsonResponse({"success": True, "enabled": enabled})


def api_adapterpinmap_bulk_update(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        fields = data.get('fields', {})

        if not ids or not isinstance(ids, list):
            return JsonResponse({'error': 'IDs inválidos'}, status=400)

        test_connector_val = fields.get('test_connector')
        test_connector = None
        assign_pins = False

        if test_connector_val not in ("", "null", None):
            try:
                test_connector = AdapterConnector.objects.get(id=int(test_connector_val))
                if len(ids) == test_connector.pin_qty:
                    assign_pins = True
            except (AdapterConnector.DoesNotExist, ValueError):
                return JsonResponse({'error': 'El conector seleccionado no existe'}, status=400)

        # Recuperar los objetos en el orden dado
        pin_maps = list(AdapterPinMap.objects.filter(id__in=ids))
        pin_map_dict = {str(obj.id): obj for obj in pin_maps}

        updated_objs = []
        for index, str_id in enumerate(ids, start=1):
            obj = pin_map_dict.get(str(str_id))
            if not obj:
                continue

            if 'test_connector' in fields:
                obj.test_connector = test_connector
                obj.to_test_pin = index if assign_pins else None

            updated_objs.append(obj)

        AdapterPinMap.objects.bulk_update(updated_objs, ['test_connector', 'to_test_pin'])

        return JsonResponse({'status': 'ok', 'updated': len(updated_objs)})

    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    
    
def check_required_hw():
    """
    Verifica la conectividad con las placas de relés y el multímetro.

    Retorna una lista de errores (vacía si todo está OK).
    """
    errors = []

    config = get_global_config()
    ip_port = config.get("ip_port", {}).get("value", "")

    # Verificación de PXI
    if not ip_port:
        errors.append("No se encontró configuración de IP y puerto para las placas de relés.")
    else:
        cmder = Commander(ip_port, 5000)
        if not cmder.connected:
            errors.append(f"No se pudo conectar con el PXI en {ip_port}.")

    # Verificación del multímetro
    if not UT61EPLUS.is_available():
        errors.append("No se detectó el multímetro UT61E+ o no respondió correctamente.")

    return errors


def api_check_required_hw(request):
    """
    View que verifica el estado del hardware (placas de relés y multímetro).
    Se utiliza de forma asíncrona en el frontend para habilitar o no el botón de comenzar.
    """
    errores = check_required_hw()

    if errores:
        return JsonResponse({
            "success": False,
            "errores": errores,
            "disable_start": True
        }, status=200)
    else:
        return JsonResponse({
            "success": True,
            "errores": [],
            "disable_start": False
        }, status=200)

    
def api_generate_instructions(request, stage_id):
    try:
        stage = TestStage.objects.select_related('session').prefetch_related('results').get(id=stage_id)
    except TestStage.DoesNotExist:
        return JsonResponse({"error": ["Error: La etapa especificada no existe."]})

    if stage.stage_type != 'test':
        return JsonResponse({"error": ["Error: Solo se pueden generar instrucciones para etapas de tipo 'test'."]})

    session = stage.session
    test_type = session.test_type
    connector_label = session.connector
    connector_type_str = session.connector_type
    connector_dest = stage.connector_dest
    connector_dest_type = stage.connector_type

    if test_type == 'Pin a chasis':
        # Obtener conectores compatibles
        usable, disabled_adapters, disabled_fixed = find_compatible_connectors(connector_type_str, 'input')

        # Conectores deshabilitados (preparamos por si los necesitamos)
        deshabilitados_info = []
        for cat, obj, tipo_base, flags, adapter_name in disabled_adapters + disabled_fixed:
            if cat == 'fixed':
                deshabilitados_info.append(
                    f"Fijo: {obj.label} ({obj.connector_type})"
                )
            else:
                deshabilitados_info.append(
                    f"Adaptador: {adapter_name} → {obj.label} ({obj.connector_type})"
                )

        if not usable:
            if deshabilitados_info:
                return JsonResponse({
                    "error": [f"Error: No se encontró ningún conector habilitado para \"{connector_label} <strong>({connector_type_str})</strong>\"."],
                    "disabled_connectors": deshabilitados_info
                })
            else:
                return JsonResponse({
                    "error": [f"Error: No se encontró ningún conector compatible para \"{connector_label} <strong>({connector_type_str})</strong>\"."],
                    "disabled_connectors": deshabilitados_info
                })
            

        # Tomar el primer candidato usable
        categoria, conector_obj, tipo_compatible_base, flags, adapter_name = usable[0]

        # Verificar mapping de pines
        pines_invalidos = []
        for result in stage.results.all():
            if result.conector_orig == connector_label:
                pin = result.pin_a
            elif result.conector_dest == connector_label:
                pin = result.pin_b
            else:
                continue

            mapeo = get_mapping_or_error(conector_obj, pin)
            if not mapeo:
                pines_invalidos.append(pin)

        if pines_invalidos:
            if categoria == 'adapter':
                adapter = conector_obj.adapter
                url = request.build_absolute_uri(reverse("adapter_connections_view", args=[adapter.id]))
                return JsonResponse({
                    "error": [
                        f"Error: El conector a utilizar [{conector_obj.label}] ({conector_obj.connector_type}) del adaptador \"{adapter.name}\" no tiene la configuración de mapeo necesaria.",
                        f'Revisa la configuración en: <a href="{url}" target="_blank">{url}</a>'
                    ]
                })
            else:
                return JsonResponse({
                    "error": [
                        f"Error: El conector a utilizar {conector_obj.label} ({conector_obj.connector_type}) no tiene la configuración de mapeo necesaria."
                    ]
                })
                
        connector_payload = {
            "category": categoria,                            # "fixed" o "adapter"
            "id": conector_obj.id,                            # la PK
            "label": conector_obj.label,
            "connector_type": conector_obj.connector_type
        }

        # Construcción del mensaje de instrucción
        if categoria == 'fixed':
            msg1 = (
                f"Conecte <span class=\"text-azure\">[{connector_label} ({connector_type_str})]</span> en "
                f"<span class=\"text-azure\">[{conector_obj.label} ({conector_obj.connector_type})]</span>"
            )
        else:
            msg1 = (
                f"Utilice el adaptador \"{adapter_name}\". Conecte <span class=\"text-azure\">[{connector_label} ({connector_type_str})]</span> en "
                f"<span class=\"text-azure\">[{conector_obj.label} ({conector_obj.connector_type})]</span>"
            )

        if flags.get('extender') and flags.get('cambiador_sexo'):
            msg1 += " utilizando un cambiador de sexo y un extender DB a DD"
        elif flags.get('extender'):
            msg1 += " utilizando un extender DB a DD"
        elif flags.get('cambiador_sexo'):
            msg1 += " utilizando un cambiador de sexo"

        msg2 = (
            f"Conecte una punta del tester en <span class=\"text-azure\">Monitor 1</span> y la otra punta en la carcasa (GND) "
            f"del conector <span class=\"text-azure\">[{connector_dest} ({connector_dest_type})]</span>"
        )

        return JsonResponse({
            "instructions": [msg1, msg2],
            "disabled_connectors": deshabilitados_info,
            "suggested_connector": connector_payload
        })

    elif test_type == 'Pin a otros':
        return JsonResponse({"error": ["Error: Generación de instrucciones para 'Pin a otros' no implementada aún."]})

    elif test_type == 'Entre par de pines':
        return JsonResponse({"error": ["Error: Generación de instrucciones para 'Entre par de pines' no implementada aún."]})

    elif test_type == 'Pin a pin':
        return JsonResponse({"error": ["Error: Generación de instrucciones para 'Pin a pin' no implementada aún."]})

    return JsonResponse({"error": [f"Error: Tipo de prueba desconocido '{test_type}'."]})


@csrf_exempt
def run_test_stage(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)
    
    # Revisar devolucion json.
    errores_hw = check_required_hw()
    if errores_hw:
        return JsonResponse({
            "error": errores_hw,
            "disable_start": True
        }, status=400)

    try:
        data = json.loads(request.body)
        
        config = get_global_config()
        ip_port = config.get("ip_port", {}).get("value", "")
        
        if not ip_port:
            return JsonResponse({
                "success": False,
                "message": "No se encontró configuración de IP y puerto."
            }, status=400)
            
        cmder = Commander(ip_port, 5000) #IP de PC pxi. Placa local en 10.245.1.100 misma mascara y puerta de enlace
        
        if not cmder.connected:
            print('Error de conexion con PXI')
            return JsonResponse({
                "success": False,
                "message": f"No se pudo conectar con el hardware en {ip_port}."
            }, status=500)

        result_test = get_object_or_404(TestResult, id=data.get("result_id"))
        stage = result_test.stage        
        session = stage.session
        test_type = session.test_type
        pin_a = result_test.pin_a
        pin_b = result_test.pin_b
        connector_label = session.connector
        connector_type_str = session.connector_type
        connector_dest = stage.connector_dest
        connector_dest_type = stage.connector_type
        
        suggested_connector_id = data.get("connector_id")
        suggested_connector_category = data.get("connector_category")
        if suggested_connector_category == "fixed":
            suggested_conector_obj = get_object_or_404(FixedConnector, id=suggested_connector_id)
        else:
            suggested_conector_obj = get_object_or_404(AdapterConnector, id=suggested_connector_id)
        

        if not result_test:
            return JsonResponse({"success": False, "message": "Resultado de prueba no encontrado."}, status=404)
        
        if not suggested_conector_obj:
            return JsonResponse({"success": False, "message": "Ocurrio un error al obtener el conector lado PXI a utilizar."}, status=404)
                
        
        relay1 = RelayCard.objects.get(id=1)
        relay2 = RelayCard.objects.get(id=2)

        id_1, bus_1, dev_1 = relay1.id, relay1.bus, relay1.device
        id_2, bus_2, dev_2 = relay2.id, relay2.bus, relay2.device
        
        
        
        print("[RUN-TEST DEBUG CMDER-STATUS]:", cmder)
        
        print("[RUN-TEST DEBUG]:", cmder.pik_open(id_1,bus_1,dev_1))
        print("[RUN-TEST DEBUG]:", cmder.pik_open(id_2,bus_2,dev_2))
        
        print("[RUN-TEST DEBUG]:", cmder.pik_clear_card(id_1))
        print("[RUN-TEST DEBUG]:", cmder.pik_clear_card(id_2))

        if test_type == "Pin a chasis":
            min_val = float(result_test.min_exp_value or 0)
            max_val = float("inf") if result_test.max_exp_value == "OL" else float(result_test.max_exp_value or 0)
            # Determinar qué pin se debe activar según el conector
            if result_test.conector_orig == session.connector:
                pin_to_test = pin_a
            elif result_test.conector_dest == session.connector:
                pin_to_test = pin_b
            else:
                return JsonResponse({
                    "success": False,
                    "message": f"Error: El conector \"{session.connector}\" no coincide con los conectores de la de prueba."
                }, status=400)

            mapping_result = get_mapping_or_error(suggested_conector_obj, pin_to_test)
                
            relay_card_id, pxi_channel = mapping_result
            
            print("[RUN-TEST DEBUG]:", cmder.pik_op_bit(relay_card_id,"7","1","1"))
            print("[RUN-TEST DEBUG]:", cmder.pik_op_bit(relay_card_id,"3",pxi_channel,"1"))
            
            
            # Simulación de lectura (reemplazar por: measured_value = multimeter.measure())
            #measured_value = random.choice([random.randint(0, 500000000), "OL"])            

            ut = UT61EPLUS()
            measured_value = ut.takeMeasurement()
            print("[RUN-TEST DEBUG-TESTER]:", measured_value)  
            
            
            
            """ if measured_value == "OL":
                result_status = "pass"
            else:
                result_status = "pass" if min_val <= measured_value <= max_val else "fail" """
                                

        elif test_type == "Pin a otros":
            # Activar pin_a
            #relay.activate(pin_a)

            # Simulación de lectura (reemplazar por: measured_value = multimeter.measure())
            measured_value = random.choice([random.randint(0, 500000000), "OL"])

            #relay.deactivate(pin_a)

            result_status = "pass" if min_val <= measured_value <= max_val else "fail"

        elif test_type == "Entre par de pines":
            # Activar ambos pines
            #relay.activate(pin_a)
            #relay.activate(pin_b)

            # Simulación de lectura (reemplazar por: measured_value = multimeter.measure())
            measured_value = random.choice([random.randint(0, 500000000), "OL"])

            #relay.deactivate(pin_a)
            #relay.deactivate(pin_b)

            result_status = "pass" if min_val <= measured_value <= max_val else "fail"

        elif test_type == "Pin a pin":
            # Activar pin_a
            #relay.activate(pin_a)

            # Simulación de lectura (reemplazar por: measured_value = multimeter.measure())
            measured_value = random.choice([random.randint(0, 500000000), "OL"])

            #relay.deactivate(pin_a)

            result_status = "pass" if min_val <= measured_value <= max_val else "fail"

        else:
            raise ValueError(f"Tipo de prueba no soportado: {test_type}")


        """  # Simular medición
        measured_value = random.choice([random.randint(0, 500000000), "OL"])
        min_val = float(result_test.min_exp_value or 0)
        max_val = float("inf") if result_test.max_exp_value == "OL" else float(result_test.max_exp_value or 0)
        # Fin simulacion prueba

        # Esto solo aplica para el tipo de prueba "Pin to chasis" aca iria un if por cada tipo de prueba 
        if measured_value == "OL":
            result_status = "pass"
        else:
            result_status = "pass" if min_val <= measured_value <= max_val else "fail" """
            
            
        """ Fin zona de deteccion y logica por cada de tipo de prueba  """
        
        print("[RUN-TEST DEBUG]:", cmder.pik_close(id_1))
        print("[RUN-TEST DEBUG]:", cmder.pik_close(id_2))

        timestamp = timezone.now()

        # Guardar SOLO en result_test
        """ result_test.measured_value = str(measured_value)
        result_test.result = result_status
        result_test.timestamp = timestamp
        result_test.save() """

        # Marcar etapa como completada si ya no hay pendientes
        if not TestResult.objects.filter(stage=stage, result="pending").exists():
            stage.status = "completed"
            stage.save()

        # Si al menos un stage se completó, la sesión pasa a "in_progress"
        if session.status == "pending":
            session.status = "in_progress"
            session.save()

        # Si todas las etapas están completadas, cerrar la sesión
        if not TestStage.objects.filter(session=session, stage_type="test", status="pending").exists():
            session.status = "completed"
            session.save()

        return JsonResponse({
            "success": True,
            "measured": measured_value,
            "result": result_status,
            "result_display": result_test.get_result_display(),
            "timestamp": timestamp.strftime("%H:%M:%S")
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)








































