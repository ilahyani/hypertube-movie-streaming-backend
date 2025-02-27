import psycopg
import bcrypt
from src.database.db_pool import DatabasePool
from datetime import datetime

def get_conn_pool():
    try:
        pool = DatabasePool().get_pool()
        return pool
    except psycopg.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def _convert_to_user_dict(data):
    user = None
    if data is not None:
        keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture', 'oauth_id']
        user = dict(zip(keys, data))
    return user

def _convert_to_movie_dict(data):
    movie = None
    if data is not None:
        keys = ['id', 'last_watched', 'watched', 'downloaded', 'download_path', 'file_size']
        movie = dict(zip(keys, data))
    return movie

def _convert_to_comment_dict(data):
    comment = None
    if data is not None:
        keys = ['id', 'author_id', 'movie_id', 'date', 'comment']
        comment = dict(zip(keys, data))
    return comment

async def fetch_db(query: str, params=None, fetchMany=False):
    pool = get_conn_pool()
    if pool is None:
        print("Database connection pool is not available.")
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    raw_data = None
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            raw_data = cur.fetchall() if fetchMany else cur.fetchone()
            return raw_data
    except psycopg.Error as e:
        print(f"fetch_db() failed: {e}")
        raise Exception(f"Database Failed to fetch data: {e}")
    finally:
        pool.putconn(conn)

async def add_user_to_db(user, oauth_id: str = None):
    pool = get_conn_pool()
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
    data = (user['email'], user['username'], user['first_name'], user['last_name'], user['passwd'], user['picture'], user['oauth_id'])
    registered_user = None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Users(email, username, first_name, last_name, passwd, picture, oauth_id)
                VALUES(%s, %s, %s, %s, %s, %s, %s);
            """, data)
            cur.execute("SELECT * FROM Users WHERE username = %s ;", (user['username'], ))
            registered_user = cur.fetchone()
            conn.commit()
            registered_user = _convert_to_user_dict(registered_user)
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
        user = _convert_to_user_dict(data)
    return user

async def get_user_by_id(id: str):
    user = None
    data = await fetch_db("SELECT * FROM Users WHERE id = %s ;", (id, ))
    if data is None:
        return data
    user = _convert_to_user_dict(data)
    if user:
        del user['passwd']
    return user

async def update_user_data(id: str, field: str, value: str):
    user = await get_user_by_id(id)
    if not user:
        return None
    pool = get_conn_pool()
    if pool is None:
        print("Database connection pool is not available.")
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE Users SET {field} = %s WHERE id = %s;", (value.lower(), id))
            conn.commit()
    except psycopg.Error as e:
        if e.sqlstate == '23505':
            unique_key = ''
            if 'email' in str(e):
                unique_key = 'email'
            else:
                unique_key = 'username'
            raise Exception(f"An account with this {unique_key} already exists")
        raise Exception("Database Failed")
    return await get_user_by_id(id)

async def update_username(id: str, username: str):
    return await update_user_data(id, 'username', username)

async def update_email(id: str, email: str):
    return await update_user_data(id, 'email', email)

async def update_firstname(id: str, first_name: str):
    return await update_user_data(id, 'first_name', first_name)

async def update_lastname(id: str, last_name: str):
    return await update_user_data(id, 'last_name', last_name)

async def update_picture(id: str, picture: str):
    return await update_user_data(id, 'picture', picture)

async def update_password(id: str, old_password: str, new_password: str):
    data = await fetch_db("SELECT * FROM Users WHERE id = %s ;", (id, ))
    if data is None:
        return data
    user = _convert_to_user_dict(data)
    if user is None:
        return user
    if bcrypt.checkpw(old_password.encode(), user['passwd'].encode()) is False:
        raise Exception("Old Password invalid")
    pool = get_conn_pool()
    if pool is None:
        print("Database connection pool is not available.")
        raise Exception("Database Failed: Connection Pool Error")
    passwd = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    passwd = passwd.decode('utf-8')
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE Users SET passwd = %s WHERE id = %s;", (passwd, id))
            conn.commit()
    except psycopg.Error as e:
        raise Exception("Database Failed")
    del user['passwd']
    return user

async def search_users(search_query: str):
    users = await fetch_db("SELECT * FROM Users WHERE username LIKE %s;", (f'{search_query.lower()}%', ), True)
    for user in users:
        user = _convert_to_user_dict(user)
    return users

async def add_movie(movie_id: str, user_id: str, download_path: str, file_size: int):
    if not movie_id or not user_id or not file_size:
        raise Exception("Missing data for movies table")
    pool = get_conn_pool()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Movies (id, download_path, file_size) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING;
            """, (movie_id, download_path, file_size))
            conn.commit()
            cur.execute("""
                INSERT INTO UserMovies (movie_id, user_id) VALUES (%s, %s) ON CONFLICT (movie_id, user_id) DO NOTHING;
            """, (movie_id, user_id))
            conn.commit()
            cur.execute("""
                SELECT id, last_watched::TEXT, watched, downloaded, download_path, file_size FROM Movies WHERE id = %s
            """, (movie_id, ))
            movie = cur.fetchone()
            return _convert_to_movie_dict(movie)
    except psycopg.Error as e:
        raise Exception(f"Failed to add movie to the database: {e}")
    finally:
        pool.putconn(conn)

async def get_movie(movie_id):
    if not movie_id:
        raise Exception("Missing data for movies table")
    pool = get_conn_pool()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, last_watched::TEXT, watched, downloaded, download_path, file_size FROM Movies WHERE id = %s;
            """, (movie_id, ))
            movie = cur.fetchone()
            return _convert_to_movie_dict(movie)
    except psycopg.Error as e:
        raise Exception(f"Failed to get movie from the database: {e}")
    finally:
        pool.putconn(conn)

async def get_user_movies(movie_ids, user_id: str):
    if not movie_ids or not user_id:
        raise Exception("Missing data for UserMovies table")
    if len(movie_ids) == 0:
        return None
    pool = get_conn_pool()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT movie_id FROM UserMovies WHERE user_id = %s AND movie_id = ANY(%s);
            """, (user_id, movie_ids))
            movies = cur.fetchall()
            for movie in movies:
                movie = dict(zip(['id'], movie))
            return movies
    except psycopg.Error as e:
        raise Exception(f"Failed to get UserMovies from the database: {e}")
    finally:
        pool.putconn(conn)

async def get_movies():
    pool = get_conn_pool()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, last_watched::TEXT, watched, downloaded, download_path, file_size FROM Movies;
            """, ())
            movies = cur.fetchall()
            for movie in movies:
                movie = _convert_to_movie_dict(movie)
            return movies
    except psycopg.Error as e:
        raise Exception(f"Failed to get UserMovies from the database: {e}")
    finally:
        pool.putconn(conn)


async def update_movie(movie_id, downloaded, last_watched):
    if not movie_id:
        raise Exception("Can't update movie: Missing ID")
    pool = get_conn_pool()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            if downloaded is not None:
                cur.execute("""
                    UPDATE Movies SET downloaded = %s WHERE id = %s;
                """, (downloaded, movie_id))
            else:
                current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cur.execute("""
                    UPDATE Movies SET last_watched = %s WHERE id = %s;
                """, (current_timestamp, movie_id))
            conn.commit()
            cur.execute("""
                SELECT id, last_watched::TEXT, watched, downloaded, download_path, file_size FROM Movies WHERE id = %s;
            """, (movie_id, ))
            movie = cur.fetchone()
            return _convert_to_movie_dict(movie)
    except pyscopg.Error as e:
        raise Exception(f"Failed to update Movies table: {e}")
    finally:
        pool.putconn(conn)

async def delete_movie(movie_id):
    if not movie_id:
        raise Exception("Can't delete movie: Missing ID")
    pool = get_conn_pool()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Movies WHERE id = %s;", (movie_id, ))
            conn.commit()
            return
    except pyscopg.Error as e:
        raise Exception(f"Failed to delete Movies table: {e}")
    finally:
        pool.putconn(conn)

async def add_comment(movie_id: str, author_id: str, comment: str):
    if not movie_id or not author_id or not comment:
        raise Exception("Missing data for comments table")
    pool = get_conn_pool()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Comments (movie_id, author_id, comment) VALUES (%s, %s, %s);
            """, (movie_id, author_id, comment))
            conn.commit()
            return
    except psycopg.Error as e:
        raise Exception(f"Failed to add comment to the database: {e}")
    finally:
        pool.putconn(conn)

async def get_comments(movie_id: str):
    if not movie_id:
        raise Exception("Missing data for comments table")
    pool = get_conn_pool()
    if not pool:
        raise Exception("Database Failed: Connection Pool Error")
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, author_id, movie_id, date::TEXT, comment FROM Comments WHERE movie_id = %s
            """, (movie_id, ))
            comments = cur.fetchall()
            for comment in comments:
                comment = _convert_to_comment_dict(comment)
            return comments
    except psycopg.Error as e:
        raise Exception(f"Failed to add comment to the database: {e}")
    finally:
        pool.putconn(conn)
