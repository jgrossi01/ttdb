from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MDBFile
from .models_db2 import Conectores
from django_eventstream import send_event
from datetime import datetime
from django.http import StreamingHttpResponse

import pyodbc
import sqlite3
import pandas as pd
from django.conf import settings
import os
import json
import uuid
import shutil
import time
import queue

def index(request):
    return render(request, 'pages/index.html')

def db_manager(request):
    context = {
        'parent': '',
        'segment': 'db_manager'
    }
    
    c = Conectores(conector="USB-C")
    c.save(using="db2", force_insert=True) # o force_update
    
    # send_event(<channel>, <event_type>, <event_data>)
    #send_event("dbupdate", "message", {"text": "hello world"})
    return render(request, 'pages/db-manager.html', context)

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

def backup_db2():
    """Crea una copia de seguridad de db2.sqlite3 con fecha e ID único."""
    try:
        fecha = datetime.now().strftime("%Y-%m-%d")
        unique_id = uuid.uuid4().hex[:6]
        backup_name = f"db2_backup_{fecha}_{unique_id}.sqlite3"
        backup_path = os.path.join(settings.MEDIA_ROOT, "backups", backup_name)
        db2_path = os.path.join(settings.BASE_DIR, "db2.sqlite3")

        # Verificar si db2.sqlite3 existe
        if not os.path.exists(db2_path):
            send_event("dbupdate", "message", {"status": "error", "text": f"Error: No se encontró la base de datos en {db2_path}"})
            #log_message(messages, f"Error: No se encontró la base de datos en {db2_path}")
            return None

        # Crear la carpeta si no existe
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        # Realizar la copia de seguridad
        shutil.copy2(db2_path, backup_path)
        send_event("dbupdate", "message", {"status": "success", "text": f"Copia de seguridad creada en: /media/backups/{backup_name}"})
        #log_message(messages, f"Copia de seguridad creada: {backup_path}")

        return backup_path
    except Exception as e:
        send_event("dbupdate", "message", {"status": "error", "text": f"Error creando backup: {e}"})
        #log_message(messages, f"Error creando backup: {e}")
        return None


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

def sync_databases(db2_path, new_db_path, sqlite_name):
    """Sincroniza db2.sqlite3 con la nueva base sin modificar datos existentes."""
    #modifications_made = False
    total_new_records = 0
    with sqlite3.connect(db2_path) as conn_db2, sqlite3.connect(new_db_path) as conn_new:
        cursor_db2 = conn_db2.cursor()
        cursor_new = conn_new.cursor()
        
        cursor_new.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor_new.fetchall()]
        
        for table in tables:
            last_signal_db2 = get_last_signal_number(db2_path, table)
            last_signal_new = get_last_signal_number(new_db_path, table)
            
            if last_signal_new > last_signal_db2:
                #modifications_made = modifications_made or True #Si es false le asigna true
                send_event("dbupdate", "message", {"status": "info", "text": f"Actualizando {table}..."})
                
                cursor_new.execute(f"SELECT * FROM {table} WHERE \"# de Señal\" > ?", (last_signal_db2,))
                new_records = cursor_new.fetchall()
                
                if new_records:
                    cursor_new.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor_new.fetchall()]
                    columns_str = ', '.join(f'"{col}"' for col in columns)
                    placeholders = ', '.join(['?' for _ in columns])
                    insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                    
                    cursor_db2.executemany(insert_query, new_records)
                    conn_db2.commit()
                    
                    new_rec_qty = len(new_records)
                    total_new_records += new_rec_qty
                    send_event("dbupdate", "message", {"status": "success", "text": f"{new_rec_qty} registros añadidos en {table}"})
                             
        if not total_new_records:
             send_event("dbupdate", "message", {"status": "info", "text": f"No se agregaron registros en ninguna tabla"}) 
             
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
        
        
        send_event("dbupdate", "message", {"status": "info", "text": f"Creando backup de db2.sqlite3"})
        backup_path = backup_db2()

        if not backup_path:
            send_event("dbupdate", "message", {"status": "error", "text": f"Error creando copia de seguridad"})
            return JsonResponse({'success': False, 'message': 'Error creando copia de seguridad.'}, status=500)
        
        send_event("dbupdate", "message", {"status": "info", "text": f"Sincronizando bases de datos"})

        total_new_records = sync_databases(os.path.join(settings.BASE_DIR, "db2.sqlite3"), sqlite_path, sqlite_name)

        mdb_file.created_records = total_new_records
        mdb_file.save(update_fields=['created_records'], using="default")

        send_event("dbupdate", "message", {"status": "success", "text": f"Proceso completado"})
        return JsonResponse({'success': True, 'message': 'Proceso completado'}, status=200)
    except Exception as e:
        send_event("dbupdate", "message", {"status": "error", "text": f"Error: {e}"})
        return JsonResponse({'success': False, 'message': str(e)}, status=400)