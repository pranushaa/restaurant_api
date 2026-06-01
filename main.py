from fastapi import FastAPI,HTTPException,Body
from pydantic import BaseModel
from passlib.context import CryptContext
import mysql.connector
import jwt
import datetime

app = FastAPI()
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"
def call_database():
    connection=mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pranu@2001",
        database="eleven"
        )
    return connection

@app.get("/")
def home():
    return{"message": "welcome to happy kitchen"}


@app.get("/menu")
def get_menu():
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT item_id, item_name, item_price, category FROM eleven.menu")
        menu_items = cursor.fetchall()
        cursor.close()
        connection.close()
        return menu_items
    except mysql.connector.Error as db_err:
        raise HTTPException(status_code=500, detail=f"database error: {db_err.msg}")



@app.post("/menu")
def add_menu_item(item_name: str, item_price: int, category: str):
    try:
        connection = call_database()
        cursor = connection.cursor()
        query = "INSERT INTO eleven.menu (item_name, item_price, category) VALUES (%s, %s, %s)"
        values = (item_name, item_price, category)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return {"message": f"successfully added {item_name} to the menu"}
    except mysql.connector.Error as db_err:
        raise HTTPException(status_code=400, detail=f"database insertion failed: {db_err.msg}")
                   


@app.put("/menu/{item_id}")
def update_menu_items(item_id: int,item_name: str,item_price: int,category: str):
    connection=call_database()
    cursor=connection.cursor()
    query="UPDATE eleven.menu SET item_name= %s,item_price= %s,category= %s WHERE item_id= %s"
    values=(item_name, item_price, category, item_id)
    cursor.execute(query,values)
    connection.commit()
    cursor.close()
    connection.close()
    return{"message":f"item_id{item_id} updated successfully!"}

@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int):
    connection=call_database()
    cursor=connection.cursor()
    query="DELETE FROM eleven.menu WHERE item_id=%s"
    values=(item_id,)
    cursor.execute(query,values)
    connection.commit()
    cursor.close()
    connection.close()
    return{"message:" f"item_id {item_id}updated successfully"}

class UserRegister(BaseModel):
    user_name:str
    email:str
    password:str
class UserLogin(BaseModel):
    email:str
    password:str
@app.post("/register")
def register_user(user: UserRegister=Body(...)):
    try:
        connection=call_database()
        cursor=connection.cursor()
        hashed_password = pwd_context.hash(user.password)
        query="INSERT INTO eleven.userinformation(user_name,email,password) VALUES (%s,%s,%s)"
        values=(user.user_name,user.email,hashed_password)
        cursor.execute(query,values)
        connection.commit()
        cursor.close()
        connection.close()
        return{"status":"success","message":f"user{user.user_name} registered successfully!"}
    except mysql.connector.Error as db_err:
        raise HTTPException(status_code=400,detail=f"Registration failed:{db_err.msg}")
    
    
@app.post("/login")
def login_user(user_data: UserLogin = Body(...)):
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM eleven.userinformation WHERE email = %s"
        cursor.execute(query, (user_data.email,))
        db_user = cursor.fetchone()
        cursor.close()
        connection.close()
        if db_user is None:
            raise HTTPException(status_code=400, detail="Invalid email or password")
        password_matches =pwd_context.verify(user_data.password,db_user['password'])
        if not password_matches:
            raise HTTPException(status_code=400, detail="Invalid email or password")
        expire = datetime.datetime.now( datetime.timezone.utc)+datetime.timedelta(minutes=30)
        token_payload = {
            "email": db_user['email'],
            "exp": expire
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer", "status": "Login Successful!"}
    except mysql.connector.Error as db_err:
        raise HTTPException(status_code=500, detail=f"Database verification error: {db_err.msg}")
    
    
class placeorder(BaseModel): 
    user_id: int
    item_id: int
    quantity: int
@app.post("/orders")
def place_new_order(order_data: placeorder = Body(...)):
    try:  
        connection = call_database()
        cursor = connection.cursor(dictionary=True) 
        query = "SELECT item_price FROM eleven.menu WHERE item_id = %s"
        cursor.execute(query, (order_data.item_id,))  
        menu = cursor.fetchone()
        if not menu:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Food item not found in menu")
        item_price = menu['item_price']
        calculated_total = item_price * order_data.quantity
        insert_query = "INSERT INTO eleven.orders (user_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (order_data.user_id, order_data.item_id, order_data.quantity, calculated_total))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "Order Placed Successfully!", "total_bill": float(calculated_total)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/orders/{user_id}")
def get_order_history(user_id: int, page: int = 1, limit: int = 5, order_status: str = None):
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        offset = (page - 1) * limit
        query = "SELECT * FROM eleven.orders WHERE user_id = %s"
        query_params = [user_id]
        if order_status:
            query += " AND order_status = %s"
            query_params.append(order_status)
        query += " LIMIT %s OFFSET %s"
        query_params.extend([limit, offset])
        cursor.execute(query, tuple(query_params))
        orders = cursor.fetchall()
        cursor.close()
        connection.close()
        return {
            "user_id": user_id,
            "current_page": page,
            "items_per_page": limit,
            "order_history": orders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/analytics/report")
def get_business_report(status: str = None):
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
         # Scenario 1: User wants to see ALL statuses (status is None or "all")
        if not status or status.lower() == "all":
            query = """
                SELECT order_status, COUNT(order_id) as total_orders 
                FROM eleven.orders 
                GROUP BY order_status
            """
            cursor.execute(query)
            # Scenario 2: User wants to filter for a single specific status
        else:
            query = """
                SELECT order_status, COUNT(order_id) as total_orders 
                FROM eleven.orders 
                WHERE order_status = %s 
                GROUP BY order_status
            """
            cursor.execute(query, (status,))
        report = cursor.fetchall()
        cursor.close()
        connection.close()
        return {
            "status": "success",
            "viewing_mode": status if status else "all_status",
            "data": report if report else []
        }
    except mysql.connector.Error as db_err:
        raise HTTPException(status_code=500, detail=f"data_base error: {str(db_err)}")
    
    
    
@app.get("/analytics/basic-report")
def get_basic_financial_report():
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        # 1. Grab overall revenue and total orders count
        cursor.execute("SELECT SUM(total_price) as total_revenue, COUNT(order_id) as total_orders FROM eleven.orders")
        financials = cursor.fetchone()
        # 2. Get total count of unique active customers
        cursor.execute("SELECT COUNT(DISTINCT user_id) as unique_customers FROM eleven.orders")
        customers = cursor.fetchone()
        cursor.close()
        connection.close()
        return {
            "status": "success",
            "total_business_revenue": financials["total_revenue"] if financials["total_revenue"] else 0,
            "total_orders_placed": financials["total_orders"],
            "total_active_customers": customers["unique_customers"]
        }
    except mysql.connector.Error as db_err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_err)}")