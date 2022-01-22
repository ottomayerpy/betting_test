import os

DEBUG = True

PG_USER = os.getenv('PGUSER')
PG_PASSWORD = os.getenv('PGPASSWORD')
PG_DB = os.getenv('PGDATABASE')
PG_HOST = 'db'
PG_PORT = 5432
