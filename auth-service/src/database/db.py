import psycopg
import bcrypt
from src.database.db_pool import DatabasePool
from src.api.auth import models
from fastapi import HTTPException

def get_db():
    try:
        pool = DatabasePool().get_pool()
        return pool
    except psycopg.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

async def fetch_db(query: str, params=None, fetchMany=False):
    pool = get_db()
    if pool is None:
        print("Database connection pool is not available.")
        raise HTTPException(status_code=500, detail=f"Database Failed: Connection Pool Error")
    conn = pool.getconn()
    raw_data = None
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            raw_data = cur.fetchmany() if fetchMany else cur.fetchone()
            conn.commit()
            return raw_data
    except psycopg.Error as e:
        print(f"fetch_db() failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database Failed")
    finally:
        pool.putconn(conn)

async def add_user_to_db(user: models.UserRegistrationModel, authenticatedWithStrategy: bool):
    pool = get_db()
    if pool is None:
        print("Database connection pool is not available.")
        raise HTTPException(status_code=500, detail=f"Database Failed: Connection Pool Error")
    conn = pool.getconn()
    user['username'] = user['username'].replace(" ", "_")
    hashed_pw = ''
    if not authenticatedWithStrategy:
        hashed_pw = bcrypt.hashpw(user['passwd'].encode('utf-8'), bcrypt.gensalt())
        user['passwd'] = hashed_pw.decode('utf-8')
    else:
        user['passwd'] = None
    query = """
        INSERT INTO users(email, username, first_name, last_name, passwd, picture)
        VALUES(%s, %s, %s, %s, %s, %s);
    """
    values = (user['email'], user['username'], user['first_name'], user['last_name'], user['passwd'], user['picture'])
    try:
        with conn.cursor() as cur:
            cur.execute(query, values)
            conn.commit()
            del user['passwd']
    except psycopg.Error as e:
        print(f'add_user_to_db() failed: {e}')
        if e.sqlstate == '23505':
            unique_key = ''
            if 'email' in str(e):
                unique_key = 'email'
            else:
                unique_key = 'username'
            raise HTTPException(status_code=400, detail=f"An account with this {unique_key} already exists")
    finally:
        pool.putconn(conn)
    registered_user = await get_user_from_db(user['username'])
    return registered_user

async def get_user_from_db(username: str):
    user = None
    data = await fetch_db("SELECT * FROM users WHERE username = %s ;", (username, ))
    if data is not None:
        keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
        user = dict(zip(keys, data))
    return user

async def get_user_by_id(id: str):
    user = None
    data = await fetch_db("SELECT * FROM users WHERE id = %s ;", (id, ))
    if data is not None:
        keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
        user = dict(zip(keys, data))
    del user['passwd']
    return user