from database import call_database

def db_get_business_report(status=None):
    connection = call_database()
    cursor = connection.cursor(dictionary=True)
    if status:
        cursor.execute("SELECT order_status, COUNT(*) as count FROM orders WHERE order_status = %s GROUP BY order_status", (status,))
    else:
        cursor.execute("SELECT order_status, COUNT(*) as count FROM orders GROUP BY order_status")
    report = cursor.fetchall()
    cursor.close()
    connection.close()
    return report

def db_get_basic_financial_report():
    connection = call_database()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT SUM(total_price) as gross_revenue, COUNT(*) as total_orders, COUNT(DISTINCT user_id) as unique_customers FROM orders")
    report = cursor.fetchone()
    cursor.close()
    connection.close()
    return report