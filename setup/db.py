import os
from contextlib import contextmanager
import pyodbc

import project_settings

timeout = '30'

drivers = [item for item in pyodbc.drivers()]
try:
    driver = drivers[-1]
except Exception as e:
    print('No ODBC drivers found!')
    driver = '{ODBC Driver 17 for SQL Server}'

print(f'Found drivers: {drivers} Trying to use driver: {driver}')
server = f"tcp:{os.environ.get('AZURE_SQL_DB_HOST', 'ENV UNAVAILABLE')}"
port = '1433'
database = os.environ.get('AZURE_SQL_DB_NAME', 'ENV UNAVAILABLE')
username = os.environ.get('AZURE_SQL_DB_USER', 'ENV UNAVAILABLE')
password = os.environ.get('AZURE_SQL_DB_PASSWORD', 'ENV UNAVAILABLE')
object_id = os.environ.get('AZURE_SQL_OBJECT_ID', 'ENV UNAVAILABLE')


if project_settings.IS_LOCAL_ENV == 0:
    connection_string = 'DRIVER=' + driver + ';SERVER=' + server + ';PORT=' + port + ';DATABASE=' + database + ';UID=' + object_id + ';Connection Timeout=' + timeout + ';Authentication=ActiveDirectoryMsi'
    # connection_string = 'DRIVER=' + driver + ';SERVER=' + server + ';PORT=' + port + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password + ';Connection Timeout=' + timeout
else:
    connection_string = 'DRIVER=' + driver + ';SERVER=' + server + ';PORT=' + port + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password + ';Connection Timeout=' + timeout

print("DB >>>>> ", connection_string)


@contextmanager
def get_db_cursor(commit=True):
    conn = None
    try:
        conn = pyodbc.connect(connection_string)
        with conn:
            with conn.cursor() as cur:
                yield cur
                if commit:
                    conn.commit()
    finally:
        if conn:
            conn.close()

