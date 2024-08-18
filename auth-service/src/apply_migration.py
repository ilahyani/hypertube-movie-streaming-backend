import os, subprocess, sys
from dotenv import load_dotenv

load_dotenv()

migrations = sys.argv[1:]

if len(migrations) == 1:
    if os.path.isfile(migrations[0]):
        migration_path = f"database/migrations/{migrations[0]}"
    elif os.path.isdir(migrations[0]):
        migration_content = ""
        migration_files = sorted(os.listdir(migrations[0]))
        for migration in migration_files:
            try:
                with open(f'{migrations[0]}/{migration}', 'r') as file:
                    migration_content += file.read() + "\n"
            except FileNotFoundError:
                print(f'File {migrations[0]}/{migration} not found.')
            except Exception as e:
                print(f'An error occurred: {e}')
        try:
            with open(f'database/migrations/tmp.sql', 'w') as file:
                file.write(migration_content)
        except FileNotFoundError:
            print(f'Failed to open file database/migrations/tmp.sql')
        except Exception as e:
            print(f'An error occurred: {e}')
        migration_path = "database/migrations/tmp.sql"
    else:
        exit(f'Invalid Argument: {migrations[0]} Resource Not Found')
else:
    migration_content = ""
    for migration in migrations:
        try:
            with open(f'database/migrations/{migration}', 'r') as file:
                migration_content += file.read() + "\n"
        except FileNotFoundError:
            exit(f'File database/migrations/{migration} not found.')
        except Exception as e:
            exit(f'An error occurred: {e}')
    try:
        with open(f'database/migrations/tmp.sql', 'w') as file:
            file.write(migration_content)
    except FileNotFoundError:
        exit(f'Failed to open file database/migrations/tmp.sql')
    except Exception as e:
        exit(f'An error occurred: {e}')
    migration_path = "database/migrations/tmp.sql"

command = f"cat {migration_path} | docker exec -i hyperdb psql -U {os.getenv("POSTGRES_USER")} -d {os.getenv("POSTGRES_DB")}"
result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if result.stderr.decode('utf-8') == "":
    print("MIGRATION APPLIED SUCCESSFULLY!!")
else:
    exit(f"MIGRATION FAILED!!\n{result.stderr.decode('utf-8')}")

os.remove("database/migrations/tmp.sql")