import psycopg
import bcrypt
from src.database.db_pool import DatabasePool
# from src.api.auth import models

def get_db():
    try:
        pool = DatabasePool().get_pool()
        return pool
    except psycopg.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_user_dict(data):
    user = None
    if data is not None:
        keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture', 'oauth_id']
        user = dict(zip(keys, data))
    return user

async def fetch_db(query: str, params=None, fetchMany=False):
    pool = get_db()
    if pool is None:
        print("Database connection pool is not available.")
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    raw_data = None
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            raw_data = cur.fetchall() if fetchMany else cur.fetchone()
            conn.commit()
            return raw_data
    except psycopg.Error as e:
        print(f"fetch_db() failed: {e}")
        raise Exception(f"Database Failed to fetch data: {e}")
    finally:
        pool.putconn(conn)

async def update_db(query: str, params):
    pool = get_db()
    if pool is None:
        print("Database connection pool is not available.")
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows_updated = cur.rowcount
            conn.commit()
            return rows_updated
    except psycopg.Error as e:
        print(f"update_db() failed: {e}")
        if e.sqlstate == '23505':
            unique_key = ''
            if 'email' in str(e):
                unique_key = 'email'
            else:
                unique_key = 'username'
            raise Exception(f"An account with this {unique_key} already exists")
        raise Exception("Database Failed")

async def add_user_to_db(user, oauth_id: str = None):
    pool = get_db()
    if pool is None:
        print("Database connection pool is not available.")
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    user['oauth_id'] = oauth_id
    hashed_pw = ''
    if not user['oauth_id']:
        hashed_pw = bcrypt.hashpw(user['passwd'].encode('utf-8'), bcrypt.gensalt())
        user['passwd'] = hashed_pw.decode('utf-8')
    else:
        user['passwd'] = None
    query = """
        INSERT INTO users(email, username, first_name, last_name, passwd, picture, oauth_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s);
    """
    values = (user['email'], user['username'], user['first_name'], user['last_name'], user['passwd'], user['picture'], user['oauth_id'])
    registered_user = None
    try:
        with conn.cursor() as cur:
            cur.execute(query, values)
            cur.execute("SELECT * FROM users WHERE username = %s ;", (user['username'], ))
            registered_user = cur.fetchone()
            registered_user = get_user_dict(registered_user)
            conn.commit()
            del registered_user['passwd'], registered_user['oauth_id']
            return registered_user
    except psycopg.Error as e:
        print(f'add_user_to_db() failed: {e}')
        if e.sqlstate == '23505':
            unique_key = ''
            if 'email' in str(e):
                unique_key = 'email'
            else:
                unique_key = 'username'
            raise Exception(f"An account with this {unique_key} already exists")
        raise Exception("Database Failed to add user")
    finally:
        pool.putconn(conn)
async def get_user_by_username(username: str):
    user = None
    data = await fetch_db("SELECT * FROM users WHERE username = %s ;", (username, ))
    print('[get_user_by_username]', user)
    if data is not None:
        user = get_user_dict(data)
    return user

async def get_user_by_id(id: str):
    user = None
    data = await fetch_db("SELECT * FROM users WHERE id = %s ;", (id, ))
    if data is None:
        return data
    user = get_user_dict(data)
    if user:
        del user['passwd']
    return user

async def update_user_data(id: str, field: str, value: str):
    user = await get_user_by_id(id)
    if not user:
        return None
    query = f"UPDATE users SET {field} = %s WHERE id = %s;"
    await update_db(query, (value.lower(), id))
    return await get_user_by_id(id)

async def update_username(id: str, username: str):
    return await update_user_data(id, 'username', username)

async def update_email(id: str, email: str):
    return await update_user_data(id, 'email', email)

async def update_firstname(id: str, first_name: str):
    return await update_user_data(id, 'first_name', first_name)

async def update_lastname(id: str, last_name: str):
    return await update_user_data(id, 'last_name', last_name)

async def search_users(search_query: str):
    users = await fetch_db("SELECT * FROM users WHERE username LIKE %s;", (f'{search_query.lower()}%', ), True)
    for user in users:
        user = get_user_dict(user)
    return users