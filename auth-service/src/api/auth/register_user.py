from src.database.db import add_user_to_db, fetch_db

async def register_user(email: str, first_name: str, last_name: str, username: str, picture: str):
    query = "SELECT * FROM users WHERE username = %s AND email = %s ;"
    params = (username.replace(" ", "_"), email)
    user_data = await fetch_db(query, params)
    user = None
    if user_data is not None:
        keys = ['id', 'email', 'username', 'first_name', 'last_name', 'passwd', 'picture']
        user = dict(zip(keys, user_data))
    if user is None:
        user = await add_user_to_db({
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'picture': picture
        }, True)
    return user