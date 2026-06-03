from database import call_database

def db_create_user(user_name, email, hashed_password):
    connection = call_database()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO userinformation (user_name, email, password) VALUES (%s, %s, %s)", (user_name, email, hashed_password))
    connection.commit()
    cursor.close()
    connection.close()

def db_get_user_by_email(email):
    connection = call_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM userinformation WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user