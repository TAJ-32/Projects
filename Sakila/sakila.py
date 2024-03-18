import mysql.connector
from mysql.connector import Error

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

connection = create_db_connection("localhost", "root", "BobbyB123(!)", "sakila")

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def execute_list_query(connection, sql, val):
    cursor = connection.cursor()
    try:
        cursor.executemany(sql, val)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def main():

    cursor = connection.cursor()

    print("Hello!\n")

    stop = False

    favorite_actors = []


    while (not stop):
        favorite_actor = input("Who are your favorite actors (type nothing if you are done)")

        if (favorite_actor == ""):
            stop = True
            break

        first_last = favorite_actor.split()

        cursor.execute("SELECT COUNT(*) FROM actor WHERE first_name = %s AND last_name = %s", [first_last[0], first_last[1]])
        actor_exists = cursor.fetchone()

        if (actor_exists[0] == 1):
            favorite_actors.append(favorite_actor)
        else:
            print("This actor is not in our database.")

        
    for i in favorite_actors:
        print(i)


if __name__ == "__main__":
    main()