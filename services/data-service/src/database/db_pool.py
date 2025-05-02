import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()

class DatabasePool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
            cls._instance.pool = ConnectionPool(
                conninfo=f"dbname={os.getenv('POSTGRES_DB')} "
                    f"user={os.getenv('POSTGRES_USER')} "
                    f"password={os.getenv('POSTGRES_PASSWORD')} "
                    f"host={os.getenv('POSTGRES_HOST')} "
                    f"port={os.getenv('POSTGRES_PORT')}",
                min_size=10,
                max_size=100,
                timeout=10
            )
        return cls._instance

    def get_pool(self):
        return self.pool
