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
            name = data.get('name')
            version = data.get('version')
            update = data.get('update')
            
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
            
            
            if int(update) == 1:
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
                    sqlite_db_name = os.path.splitext(mdb_file_name)[0] + ".sqlite"  # Cambiar extensión a .sqlite

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

                    print(f"Migración completada. Base de datos SQLite guardada en: {sqlite_db_path}")

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
                'message': 'Archivo subido correctamente.',
                'file_id': mdb_file.id,
                'file_name': mdb_file.name
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)