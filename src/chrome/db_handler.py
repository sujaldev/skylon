import mysql.connector as sql
import pickle
server_down = True
local_data = {}

if not server_down:
    connection = sql.connect(
        user="admin",
        password="skylonUserDB",
        host="skylon-users.ctq2ehobzwiu.ap-south-1.rds.amazonaws.com",
        database="skylon_users",
        autocommit=True
    )
    cursor = connection.cursor()


def create_user(first_name, last_name, email, engine_choice):
    # CREATE NEW USER ON MYSQL SERVER THEN CACHE USER
    if server_down:
        local_data["first_name"] = first_name
        local_data["last_name"] = last_name
        local_data["email"] = email 
        local_data["engine_choice"] = engine_choice 
        return
    query = f'INSERT INTO users VALUES("{first_name}", "{last_name}", "{email}", "{engine_choice}")'
    cursor.execute(query)


def user_exists(first_name, last_name, email):
    if server_down:
        return
    query = f'SELECT * FROM users WHERE first_name="{first_name}" AND last_name="{last_name}" and email = "{email}";'
    cursor.execute(query)

    user_existence = len(cursor.fetchall()) == 1
    return user_existence


def update_preference(email, new_preference):
    if server_down:
        if new_preference in ["skylon", "chromium"]:
            local_data["email"] = new_preference
        else:
            raise ValueError
        return
    if new_preference in ["skylon", "chromium"]:
        query = f'UPDATE users SET engine_choice="{new_preference}" WHERE email="{email}";'
        cursor.execute(query)
    else:
        raise ValueError


def delete_user(email):
    if server_down:
        return
    query = f'DELETE FROM users WHERE email="{email}";'
    cursor.execute(query)


def cache_user(email):
    # LOCALLY STORES USER PREFERENCES FOR QUICKER ACCESS
    if server_down:
        cache_file = open("user.cache", "wb")
        pickle.dump(local_data, cache_file)
        cache_file.close()
        return
    query = f'SELECT * FROM users WHERE email="{email}";'
    cursor.execute(query)

    user_data = cursor.fetchall()[0]
    cache_file = open("user.cache", "wb")
    pickle.dump(user_data, cache_file)
    cache_file.close()
