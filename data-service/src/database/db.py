import psycopg
import bcrypt
from src.database.db_pool import DatabasePool

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

def get_movie_dict(data):
    movie = None
    if data is not None:
        keys = ['id', 'last_watched', 'watched', 'downloaded', 'download_path']
        movie = dict(zip(keys, data))
    return movie

def get_comment_dict(data):
    comment = None
    if data is not None:
        keys = ['id', 'author_id', 'movie_id', 'date', 'comment']
        comment = dict(zip(keys, data))
    return comment

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
        INSERT INTO Users(email, username, first_name, last_name, passwd, picture, oauth_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s);
    """
    values = (user['email'], user['username'], user['first_name'], user['last_name'], user['passwd'], user['picture'], user['oauth_id'])
    registered_user = None
    try:
        with conn.cursor() as cur:
            cur.execute(query, values)
            cur.execute("SELECT * FROM Users WHERE username = %s ;", (user['username'], ))
            registered_user = cur.fetchone()
            conn.commit()
            registered_user = get_user_dict(registered_user)
            if registered_user is not None:
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
    data = await fetch_db("SELECT * FROM Users WHERE username = %s ;", (username, ))
    print('[get_user_by_username]', user)
    if data is not None:
        user = get_user_dict(data)
    return user

async def get_user_by_id(id: str):
    user = None
    data = await fetch_db("SELECT * FROM Users WHERE id = %s ;", (id, ))
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
    query = f"UPDATE Users SET {field} = %s WHERE id = %s;"
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
    users = await fetch_db("SELECT * FROM Users WHERE username LIKE %s;", (f'{search_query.lower()}%', ), True)
    for user in users:
        user = get_user_dict(user)
    return users

# add movie
async def add_movie(movie_id: str, user_id: str, download_path: str):
    if not movie_id or not user_id:
        raise Exception("Missing data for movies table")
    pool = get_db()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Movies (id, download_path) VALUES (%s, %s);", (movie_id, download_path))
            conn.commit()
            cur.execute("INSERT INTO UserMovies (movie_id, user_id) VALUES (%s, %s);", (movie_id, user_id))
            cur.execute("SELECT id, last_watched::TEXT, watched, downloaded, download_path FROM Movies WHERE id = %s", (movie_id, ))
            movie = cur.fetchone()
            conn.commit()
            return get_movie_dict(movie)
    except psycopg.Error as e:
        raise Exception(f"Failed to add movie to the database: {e}")
    finally:
        pool.putconn(conn)

# get user movies with user/movie id
async def get_movie(movie_id):
    if not movie_id:
        raise Exception("Missing data for movies table")
    pool = get_db()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, last_watched::TEXT, watched, downloaded, download_path FROM Movies WHERE id = %s;
            """, (movie_id, ))
            movie = cur.fetchone()
            conn.commit()
            return get_movie_dict(movie)
    except psycopg.Error as e:
        raise Exception(f"Failed to get movie from the database: {e}")
    finally:
        pool.putconn(conn)

async def get_user_movies(movie_ids, user_id: str):
    if not movie_ids or not user_id:
        raise Exception("Missing data for UserMovies table")
    if len(movie_ids) == 0:
        return None
    pool = get_db()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT movie_id FROM UserMovies WHERE user_id = %s AND movie_id = ANY(%s);
            """, (user_id, movie_ids))
            movies = cur.fetchall()
            conn.commit()
            for movie in movies:
                movie = dict(zip(['id'], movie))
            return movies
    except psycopg.Error as e:
        raise Exception(f"Failed to get UserMovies from the database: {e}")
    finally:
        pool.putconn(conn)

# add comment
async def add_comment(movie_id: str, author_id: str, comment: str):
    if not movie_id or not author_id or not comment:
        raise Exception("Missing data for comments table")
    pool = get_db()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Comments (movie_id, author_id, comment) VALUES (%s, %s, %s);", (movie_id, author_id, comment))
            conn.commit()
            return
    except psycopg.Error as e:
        raise Exception(f"Failed to add comment to the database: {e}")
    finally:
        pool.putconn(conn)

# get comments with movie id
async def get_comments(movie_id: str):
    if not movie_id:
        raise Exception("Missing data for comments table")
    pool = get_db()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, author_id, movie_id, date::TEXT, comment FROM Comments WHERE movie_id = %s", (movie_id, ))
            comments = cur.fetchall()
            conn.commit()
            for comment in comments:
                comment = get_comment_dict(comment)
            return comments
    except psycopg.Error as e:
        raise Exception(f"Failed to add comment to the database: {e}")
    finally:
        pool.putconn(conn)
