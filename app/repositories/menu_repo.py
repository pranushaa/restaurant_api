from database import call_database

def db_get_menu():
    connection = call_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()
    cursor.close()
    connection.close()
    return menu

def db_add_menu_item(item_name, item_price, category):
    connection = call_database()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO menu (item_name, item_price, category) VALUES (%s, %s, %s)", (item_name, item_price, category))
    connection.commit()
    cursor.close()
    connection.close()

def db_update_menu_item(item_id, item_name, item_price, category):
    connection = call_database()
    cursor = connection.cursor()
    cursor.execute("UPDATE menu SET item_name=%s, item_price=%s, category=%s WHERE item_id=%s", (item_name, item_price, category, item_id))
    connection.commit()
    cursor.close()
    connection.close()

def db_delete_menu_item(item_id):
    connection = call_database()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM menu WHERE item_id=%s", (item_id,))
    connection.commit()
    cursor.close()
    connection.close()

def db_get_menu_item_by_id(item_id):
    connection = call_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu WHERE item_id = %s", (item_id,))
    item = cursor.fetchone()
    cursor.close()
    connection.close()
    return item

def db_get_healthier_alternative(category, health_score):
    connection = call_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM menu WHERE category = %s AND health_score > %s ORDER BY health_score DESC, calories ASC LIMIT 1",
        (category, health_score)
    )
    alternative = cursor.fetchone()
    cursor.close()
    connection.close()
    return alternative