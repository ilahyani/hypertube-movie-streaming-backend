import os
import sys
from dotenv import load_dotenv
import psycopg

load_dotenv()

def generate_migrations_file(migration_files, migration_dir):
    """
    Generate a single migrations file from a list of migration files
    Args:
        migration_files (list): List of migration file names
        migration_dir (str): Directory containing the migration files
    Returns:
        str: Path to the generated migrations file
    """
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
    """
    Get the migrations file path or generate it from a directory.
    Returns:
        str: Path to the migrations file.
    """
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

with psycopg.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}") as conn:
    with conn.cursor() as cur:
        try:
            cur.execute(migration_content)
            conn.commit()
        except Exception as e:
            conn.rollback()
            exit(f'oops: {e}')