from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from .models import MDBFile, TestSession, TestStage, TestResult
from .models_harness import Conexiones
from django_eventstream import send_event
from datetime import datetime
from collections import defaultdict

import pyodbc
import sqlite3
import pandas as pd
import os
import json
import uuid
import shutil


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

#@csrf_exempt

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
    """Convierte un archivo .mdb a .sqlite3"""
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
    """Sincroniza harness.sqlite3 con la nueva base sin modificar datos existentes."""
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
            session = TestSession.objects.create(connector=connector, test_type=test_type)
            
            connections = Conexiones.objects.using("harness").filter(
                conector_orig=connector
            ).exclude(activo_si_no_field="no") | Conexiones.objects.using("harness").filter(
                conector_dest=connector
            ).exclude(activo_si_no_field="no")

            etapas = {}
            for conn in connections:
                destino = conn.conector_dest if conn.conector_orig == connector else conn.conector_orig
                if destino not in etapas:
                    etapas[destino] = []
                etapas[destino].append(conn)
                
            expected_values = {
                "Pin a chasis": (100000000, "OL"),
                "Pin a otros": (100000000, "OL"),
                "Pin a pin": (0, 10),
            }

            min_expected, max_expected = expected_values.get(test_type, (None, None))

            for i, (dest, signals) in enumerate(etapas.items(), start=1):
                reference_stage = TestStage.objects.create(
                    session=session,
                    stage_number=i,
                    stage_type='reference',
                    connector_dest=dest,
                    instructions=f"Conectar {connector} y {dest} para ejecutar la prueba.",
                )
                
                test_stage = TestStage.objects.create(
                    session=session,
                    stage_number=i,
                    stage_type='test',
                    connector_dest=dest,
                    instructions=f"Conectar {connector} y {dest} para ejecutar la prueba.",
                )
                
                for signal in signals:
                    # Crear TestResult para referencia SIN modificaciones
                    TestResult.objects.create(
                        stage=reference_stage,
                        signal_id=signal.field_de_señal,
                        signal_name=signal.nombre,
                        conector_orig=signal.conector_orig,
                        pin_a=signal.pin_orig or "N/A",
                        conector_dest=signal.conector_dest,
                        pin_b=signal.pin_dest or "N/A",
                        min_exp_value=min_expected or "0",
                        max_exp_value=max_expected or "0",
                        result="Pendiente",
                    )
                    
                    # Procesamiento de datos para test_stage
                    pin_a, pin_b = signal.pin_orig or "N/A", signal.pin_dest or "N/A"
                    
                    invalid_values = {"TBD", "TBD*", "TBC", "TBC*", "---", "---*", "-", "+"}
                    if pin_a in invalid_values or pin_b in invalid_values:
                        continue
                    
                    pin_a = pin_a.replace("*", "").replace("(", "").replace(")", "")
                    pin_b = pin_b.replace("*", "").replace("(", "").replace(")", "")

                    expanded_pin_a = expand_values(pin_a)
                    expanded_pin_b = expand_values(pin_b)
                    
                    for a in expanded_pin_a:
                        for b in expanded_pin_b:
                            TestResult.objects.create(
                                stage=test_stage,
                                signal_id=signal.field_de_señal,
                                signal_name=signal.nombre,
                                conector_orig=signal.conector_orig,
                                pin_a=a,
                                conector_dest=signal.conector_dest,
                                pin_b=b,
                                min_exp_value=min_expected or "0",
                                max_exp_value=max_expected or "0",
                                result="Pendiente",
                            )
        return redirect("test_summary", session_id=session.id)
    
    return render(request, 'pages/new-test.html', context)


def test_summary(request, session_id):
    session = get_object_or_404(TestSession, id=session_id)
    stages = session.stages.filter(stage_type='reference')
    stages_count = session.stages.filter(stage_type='test').count()

    return render(request, "pages/test-summary.html", {
        "session": session,
        "stages": stages,
        "stages_count": stages_count,
    })
    
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

def test_stage_view(request, session_id, stage_id):
    session = get_object_or_404(TestSession, id=session_id)

    # Obtener la etapa de referencia y su correspondiente test
    stage_reference = get_object_or_404(TestStage, id=stage_id, session=session, stage_type='reference')
    stage_test = get_object_or_404(TestStage, session=session, stage_number=stage_reference.stage_number, stage_type='test')

    # Obtener todas las etapas de prueba en una sola consulta
    test_stages = list(session.stages.filter(stage_type='test').order_by("stage_number"))

    # Crear el mapeo stage_number -> id de reference en una sola consulta
    reference_stage_map = dict(session.stages.filter(stage_type='reference').values_list("stage_number", "id"))

    # Obtener prev y next en una sola consulta
    prev_next_dict = dict(
        session.stages.filter(
            stage_number__in=[stage_reference.stage_number - 1, stage_reference.stage_number + 1],
            stage_type="reference"
        ).values_list("stage_number", "id")
    )

    prev_stage_id = prev_next_dict.get(stage_reference.stage_number - 1)
    next_stage_id = prev_next_dict.get(stage_reference.stage_number + 1)

    # Obtener todos los resultados en una sola consulta
    test_results = TestResult.objects.filter(stage__in=[stage_reference, stage_test]).select_related("stage")

    # Separar en referencia y test
    reference_results = []
    test_results_list = []
    for result in test_results:
        if result.stage_id == stage_reference.id:
            reference_results.append(result)
        else:
            test_results_list.append(result)

    # Crear diccionario de referencia con defaultdict
    reference_dict = defaultdict(lambda: {"pin_a": "No ref", "pin_b": "No ref"})
    reference_dict.update({r.signal_id: {"pin_a": r.pin_a, "pin_b": r.pin_b} for r in reference_results})

    # Formatear los datos para la tabla
    test_results_data = [
        {
            "signal_name": test.signal_name,
            "conector_orig": test.conector_orig,
            "pin_a": test.pin_a,
            "tooltip_a": reference_dict[test.signal_id]["pin_a"],
            "conector_dest": test.conector_dest,
            "pin_b": test.pin_b,
            "tooltip_b": reference_dict[test.signal_id]["pin_b"],
            "min_exp_value": test.min_exp_value,
            "max_exp_value": test.max_exp_value,
            "measured_value": test.measured_value,
            "result": test.result,
            "timestamp": test.timestamp,
        }
        for test in test_results_list
    ]

    # Renderizar el template con el contexto
    context = {
        "session": session,
        "stage_reference": stage_reference,
        "stage_test": stage_test,
        "test_results": test_results_data,
        "test_results_raw": test_results_list,
        "reference_results": reference_results,
        "total_stages": len(test_stages),
        "prev_stage_id": prev_stage_id,
        "prev_stage_number": stage_reference.stage_number - 1 if prev_stage_id else None,
        "next_stage_id": next_stage_id,
        "next_stage_number": stage_reference.stage_number + 1 if next_stage_id else None,
        "test_stages": test_stages,
        "reference_stage_map": reference_stage_map,
    }
    return render(request, "pages/test-stage.html", context)



