from database import call_database

def db_get_item_price(item_id):
    connection = call_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT item_price FROM menu WHERE item_id = %s", (item_id,))
    menu = cursor.fetchone()
    cursor.close()
    connection.close()
    return menu

def db_insert_order(user_id, item_id, quantity, calculated_total):
    connection = call_database()
    connection.autocommit = False
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO orders (user_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
            (user_id, item_id, quantity, calculated_total)
        )
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()

def db_get_order_history(user_id, limit, offset, order_status=None):
    connection = call_database()
    cursor = connection.cursor(dictionary=True)
    if order_status:
        cursor.execute("SELECT * FROM orders WHERE user_id = %s AND order_status = %s LIMIT %s OFFSET %s", (user_id, order_status, limit, offset))
    else:
        cursor.execute("SELECT * FROM orders WHERE user_id = %s LIMIT %s OFFSET %s", (user_id, limit, offset))
    history = cursor.fetchall()
    cursor.close()
    connection.close()
    return history