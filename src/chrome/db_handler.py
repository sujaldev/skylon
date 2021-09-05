import mysql.connector as sql
import pickle

connection = sql.connect(
    user="admin",
    password="skylonUserDB",
    host="skylon-users.ctq2ehobzwiu.ap-south-1.rds.amazonaws.com",
    database="skylon_users",
    autocommit=True
)
cursor = connection.cursor()


# noinspection SqlResolve
def create_user(first_name, last_name, email, engine_choice):
    # CREATE NEW USER ON MYSQL SERVER THEN CACHE USER
    query = f'INSERT INTO users VALUES("{first_name}", "{last_name}", "{email}", "{engine_choice}")'
    cursor.execute(query)


# noinspection SqlResolve
def user_exists(first_name, last_name, email):
    query = f'SELECT * FROM users WHERE first_name="{first_name}" AND last_name="{last_name}" and email = "{email}";'
    cursor.execute(query)

    user_existence = len(cursor.fetchall()) == 1
    return user_existence


# noinspection SqlResolve
def update_preference(email, new_preference):
    if new_preference in ["skylon", "chromium"]:
        query = f'UPDATE users SET engine_choice="{new_preference}" WHERE email="{email}";'
        cursor.execute(query)
    else:
        raise ValueError


# noinspection SqlResolve
def delete_user(email):
    query = f'DELETE FROM users WHERE email="{email}";'
    cursor.execute(query)


# noinspection SqlResolve
def cache_user(email):
    # LOCALLY STORES USER PREFERENCES FOR QUICKER ACCESS
    query = f'SELECT * FROM users WHERE email="{email}";'
    cursor.execute(query)

    user_data = cursor.fetchall()[0]
    cache_file = open("user.cache", "wb")
    pickle.dump(user_data, cache_file)
    cache_file.close()


