import psycopg
import bcrypt
from src.database.db_pool import DatabasePool
from src.api.auth import models
# import src.grpc.user_pb2 as user_pb2

#TODO: BETTER ERROR HANDLING, DB ERRORS SHOULDN'T BE IN HTTP RESPONSES

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

async def add_user_to_db(user: models.UserRegistrationModel, oauth_id: str = None):
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
            # registered_user = dict(zip(['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture'], registered_user))
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
    # print('[ADD USER TO DB] username: ', user['username'])
    # registered_user = await get_user_by_username(user['username'])
    # print('[ADD USER TO DB] user ', registered_user)
    # return None

async def get_user_by_username(username: str):
    user = None
    data = await fetch_db("SELECT * FROM users WHERE username = %s ;", (username, ))
    print('[get_user_by_username]', user)
    if data is not None:
        # keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
        # user = dict(zip(keys, data))
        user = get_user_dict(data)
    return user

async def get_user_by_id(id: str):
    user = None
    data = await fetch_db("SELECT * FROM users WHERE id = %s ;", (id, ))
    if data is None:
        return data
    # keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
    # user = dict(zip(keys, data))
    user = get_user_dict(data)
    if user:
        del user['passwd']
    return user

async def update_username(id: str, username: str):
    user = await get_user_by_id(id)
    if not user:
        return None
    updated = await update_db("UPDATE users SET username = %s WHERE id = %s;", (username.lower(), id))
    user = await get_user_by_id(id)
    return user

async def update_email(id: str, email: str):
    user = await get_user_by_id(id)
    if not user:
        return None
    updated = await update_db("UPDATE users SET email = %s WHERE id = %s;", (email.lower(), id))
    user = await get_user_by_id(id)
    return user

async def update_firstname(id: str, first_name: str):
    user = await get_user_by_id(id)
    if not user:
        return None
    updated = await update_db("UPDATE users SET first_name = %s WHERE id = %s;", (first_name, id))
    user = await get_user_by_id(id)
    return user

async def update_lastname(id: str, last_name: str):
    user = await get_user_by_id(id)
    if not user:
        return None
    updated = await update_db("UPDATE users SET last_name = %s WHERE id = %s;", (last_name, id))
    user = await get_user_by_id(id)
    return user

async def search_users(search_query: str):
    # keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
    users = await fetch_db("SELECT * FROM users WHERE username LIKE %s;", (f'{search_query.lower()}%', ), True)
    for user in users:
        # print(user)
        # user = dict(zip(keys, user))
        user = get_user_dict(user)
    return users