from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MDBFile
import pyodbc
import sqlite3
import pandas as pd
from django.conf import settings
import os
from datetime import datetime
import json
import uuid
import shutil


# Create your views here.

def index(request):

    # Page from the theme 
    return render(request, 'pages/index.html')

def db_manager(request):
    context = {
        'parent': '',
        'segment': 'db_manager'
    }
    return render(request, 'pages/db-manager.html', context)



@csrf_exempt
def upload_mdb(request):
    if request.method == 'POST':
        try:
            # Obtener el archivo subido
            uploaded_file = request.FILES.get('file')
            data = json.loads(request.POST.get('data'))
            name = data.get('inputNameValue')
            version = data.get('inputVersionValue')
            
            print(name);
            if not uploaded_file:
                return JsonResponse({'success': False, 'message': 'No se proporcionó ningún archivo.'}, status=400)
   
            # Guardar el archivo en la base de datos
            mdb_file = MDBFile(
                file=uploaded_file,  # Archivo subido
                name=name,  # Usar el nombre del archivo como nombre
                version=version,  # Valor por defecto para la versión
                status="Pendiente"  # Valor por defecto para el estado
            )
            mdb_file.save()
            
            ''' Conversión de .mdb a .sqlite '''
            try:
                # Obtener la ruta relativa y completa del archivo MDB
                relative_path = mdb_file.file.name  # "mdb_files/nombre_archivo.mdb"
                full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                print(f"Ruta completa del archivo MDB: {full_path}")

                # Verificar si el archivo MDB existe
                if not os.path.exists(full_path):
                    raise FileNotFoundError(f"El archivo MDB no existe en la ruta: {full_path}")

                # Extraer el nombre del archivo sin la ruta "mdb_files/"
                mdb_file_name = os.path.basename(relative_path)  # "nombre_archivo.mdb"
                sqlite_db_name = os.path.splitext(mdb_file_name)[0] + ".sqlite3"  # Cambiar extensión a .sqlite

                # Ruta completa para guardar la base de datos SQLite
                sqlite_db_path = os.path.join(settings.MEDIA_ROOT, "sqlite_files", sqlite_db_name)

                # Crear la carpeta "sqlite_files" si no existe
                os.makedirs(os.path.dirname(sqlite_db_path), exist_ok=True)

                # Conexión a Access
                conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={full_path}"
                print(f"Cadena de conexión a Access: {conn_str}")

                try:
                    access_conn = pyodbc.connect(conn_str)
                    cursor = access_conn.cursor()
                except pyodbc.Error as e:
                    raise Exception(f"Error al conectar a la base de datos Access: {e}")

                # Conexión a SQLite (usando la ruta completa)
                try:
                    sqlite_conn = sqlite3.connect(sqlite_db_path)
                except sqlite3.Error as e:
                    raise Exception(f"Error al conectar a la base de datos SQLite: {e}")

                # Obtener nombres de las tablas en Access
                tables = [row.table_name for row in cursor.tables(tableType="TABLE")]
                print(f"Tablas encontradas en Access: {tables}")

                # Migrar cada tabla de Access a SQLite
                for table in tables:
                    print(f"Exportando {table}...")

                    try:
                        # Leer datos de Access en un DataFrame de pandas
                        df = pd.read_sql(f"SELECT * FROM {table}", access_conn)

                        # Guardar los datos en SQLite
                        df.to_sql(table, sqlite_conn, if_exists="replace", index=False)
                    except Exception as e:
                        print(f"Error al exportar la tabla {table}: {e}")

                print(f"✅ Migración completada. Base de datos SQLite guardada en: {sqlite_db_path}")
                
                ''' Backup db2.sqlite '''
                
                DB2_PATH = os.path.join(settings.BASE_DIR, "db2.sqlite3")
                NUEVA_DB_PATH = sqlite_db_path
                
                """Crea una copia de seguridad con la fecha y un ID único"""
                fecha = datetime.now().strftime("%d-%m-%y")  # Formato YYYY-MM-DD
                unique_id = uuid.uuid4().hex[:6]  # ID único de 6 caracteres
                backup_name = f"db2_backup_{fecha}_{unique_id}.sqlite3"
                backup_path = os.path.join(settings.MEDIA_ROOT, "backups", backup_name)

                shutil.copy2(DB2_PATH, backup_path)
                print(f"✅ Copia de seguridad creada en: {backup_path}")
                
                ''' Insertar datos nuevos '''
                
                def get_last_signal_number(db_path, table_name):
                    """Obtiene el último '# de Señal' de una tabla"""
                    with sqlite3.connect(db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT MAX(\"# de Señal\") FROM {table_name}")
                        result = cursor.fetchone()
                        return result[0] if result and result[0] else 0
                
                """Sincroniza db2.sqlite3 con nueva.sqlite3 sin modificar datos existentes"""
                
                with sqlite3.connect(DB2_PATH) as conn_db2, sqlite3.connect(NUEVA_DB_PATH) as conn_nueva:
                    cursor_db2 = conn_db2.cursor()
                    cursor_nueva = conn_nueva.cursor()

                    # Obtener las tablas disponibles en la base de datos nueva
                    cursor_nueva.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor_nueva.fetchall()]

                    for table in tables:
                        last_signal_db2 = get_last_signal_number(DB2_PATH, table)
                        last_signal_nueva = get_last_signal_number(NUEVA_DB_PATH, table)

                        if last_signal_nueva > last_signal_db2:
                            print(f"🔹 Actualizando '{table}': Nuevos registros encontrados")

                            # Obtener solo los registros nuevos
                            cursor_nueva.execute(f"SELECT * FROM {table} WHERE \"# de Señal\" > ?", (last_signal_db2,))
                            new_records = cursor_nueva.fetchall()

                            if new_records:
                                # Obtener nombres de columnas
                                cursor_nueva.execute(f"PRAGMA table_info({table})")
                                columns = [col[1] for col in cursor_nueva.fetchall()]
                                columns_str = ', '.join(f'"{col}"' for col in columns)
                                placeholders = ', '.join(['?' for _ in columns])

                                # Insertar registros en db2
                                insert_query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                                cursor_db2.executemany(insert_query, new_records)
                                conn_db2.commit()

                                print(f"✅ {len(new_records)} registros añadidos en '{table}'")
                        else:
                            print(f"✔ '{table}' ya está actualizada")

                print(f"🎉 Base de datos actualizada correctamente. Copia de seguridad en: {backup_path}")

                conn_db2.commit()
                conn_db2.close()
                conn_nueva.close()
                

                
            except FileNotFoundError as e:
                print(f"Error: {e}")
            except pyodbc.Error as e:
                print(f"Error de ODBC: {e}")
            except sqlite3.Error as e:
                print(f"Error de SQLite: {e}")
            except Exception as e:
                print(f"Error inesperado: {e}")
            finally:
                # Cerrar conexiones en el bloque finally para asegurarse de que siempre se cierren
                if 'access_conn' in locals():
                    access_conn.close()
                if 'sqlite_conn' in locals():
                    sqlite_conn.close()
                print("Conexiones cerradas.")
                

            return JsonResponse({
                'success': True,
                'message': 'Base de datos actualizada correctamente.',
                'file_id': mdb_file.id,
                'file_name': mdb_file.name
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)



def getDatabases(request):
    archivos = MDBFile.objects.all().values("upload_date", "name", "file", "version", "status")
    
    data = [
        {
            "upload_date": archivo["upload_date"].strftime("%d/%m/%y %H:%M"),
            "name": archivo["name"],
            "file": archivo["file"],
            "version": archivo["version"],
            "status": archivo["status"],
        }
        for archivo in archivos
    ]
    
    return JsonResponse({"data": data})