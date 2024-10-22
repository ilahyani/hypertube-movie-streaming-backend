import os
import sys
from dotenv import load_dotenv
import psycopg

load_dotenv()

#TODO: Handle Rollbacks even if it doesn't happen often
#TODO: before applying a mig, fetch the mig table and see if it's there already

def generate_migrations_file(migration_files, migration_dir):
    content = ""
    for mig in migration_files:
        try:
            with open(os.path.join(migration_dir, mig)) as file:
                content += file.read() + "\n"
        except FileNotFoundError:
            print(f'File {os.path.join(migration_dir, mig)} Not Found.')
            continue
        except Exception as e:
            print(f'Error: {e}')
            continue
    try:
        with open('./migrations.sql', 'w') as file:
            file.write(content)
    except Exception as e:
        exit(f'Failed to open file migrations.sql: {e}')
    return './migrations.sql'

def get_migrations():
    migration_data = sys.argv[1:]
    if len(migration_data) == 1:
        if os.path.isfile(migration_data[0]):
            return migration_data[0]
        elif os.path.isdir(migration_data[0]):
            migration_files = sorted(os.listdir(migration_data[0]))
            return generate_migrations_file(migration_files, migration_data[0])
        else:
            exit(f'Invalid Argument: {migration_data[0]}')
    else:
        return generate_migrations_file(migration_data, '.')

migration_file_path = get_migrations()
migration_content = ""
with open(migration_file_path) as file:
    migration_content = file.read()
    migration_file_path == './migrations.sql' and os.remove(migration_file_path)
print(migration_content)

DB_HOST = os.getenv('POSTGRES_HOST')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_PORT = os.getenv('POSTGRES_PORT')

try:
    with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}") as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(migration_content)
                conn.commit()
            except Exception as e:
                conn.rollback()
                exit(f'oops: {e}')
except Exception as e:
    print(f'Failed to connect to database: {e}')