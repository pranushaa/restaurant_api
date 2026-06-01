from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from passlib.context import CryptContext
import sqlite3
import jwt
import datetime
from typing import List

app = FastAPI()

# --- Security Configuration ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

# --- Database Setup ---
def call_database():
    connection = sqlite3.connect("restaurant.db", check_same_thread=False)
    
    # Automatically build the backend tables on startup if they do not exist
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        item_price INTEGER NOT NULL,
        category TEXT NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS userinformation (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        order_status TEXT DEFAULT 'Pending'
    );
    """)
    connection.commit()
    return connection

# Helper utility to mimic MySQL's dictionary=True functionality smoothly
def get_dict_cursor(connection):
    connection.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return connection.cursor()


# PYDANTIC REQUEST / RESPONSE MODELS

class MenuResponse(BaseModel):
    item_id: int
    item_name: str
    item_price: int
    category: str

class UserRegister(BaseModel):
    user_name: str
    email: str
    password: str

class RegisterResponse(BaseModel):
    status: str
    message: str

class UserLogin(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    status: str

class placeorder(BaseModel):
    user_id: int
    item_id: int
    quantity: int

class OrderResponse(BaseModel):
    status: str
    total_bill: float


# ENDPOINTS 

@app.get("/", tags=["System Vitals"], summary="Root system check")
def home():
    """
    Returns a simple welcome message to check if server is live.
    """
    return {"message": "welcome to happy kitchen"}


@app.get("/menu", response_model=List[MenuResponse], tags=["Menu Management"], summary="Fetch entire food menu")
def get_menu():
    """
    Fetches all available food items from the menu database table.
    """
    try:
        connection = call_database()
        cursor = get_dict_cursor(connection)
        cursor.execute("SELECT * FROM menu")
        menu = cursor.fetchall()
        cursor.close()
        connection.close()
        return menu
    except sqlite3.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))


@app.post("/menu", tags=["Menu Management"], summary="Add a new dish to the menu")
def add_menu_item(item_name: str, item_price: int, category: str):
    """
    Inserts a completely new food item details into the menu table.
    """
    try:
        connection = call_database()
        cursor = connection.cursor()
        query = "INSERT INTO menu (item_name, item_price, category) VALUES (?, ?, ?)"
        cursor.execute(query, (item_name, item_price, category))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "success", "message": "Item added successfully"}
    except sqlite3.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))


@app.put("/menu/{item_id}", tags=["Menu Management"], summary="Update an existing menu item")
def update_menu_items(item_id: int, item_name: str, item_price: int, category: str):
    """
    Modifies an existing food item matching the provided item_id parameter.
    """
    try:
        connection = call_database()
        cursor = connection.cursor()
        query = "UPDATE menu SET item_name=?, item_price=?, category=? WHERE item_id=?"
        cursor.execute(query, (item_name, item_price, category, item_id))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "updated successfully"}
    except sqlite3.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))


@app.delete("/menu/{item_id}", tags=["Menu Management"], summary="Remove a dish from the menu")
def delete_menu_item(item_id: int):
    """
    Deletes a food item completely from the database using its item_id.
    """
    try:
        connection = call_database()
        cursor = connection.cursor()
        query = "DELETE FROM menu WHERE item_id=?"
        cursor.execute(query, (item_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "deleted successfully"}
    except sqlite3.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))


@app.post("/register", response_model=RegisterResponse, tags=["Identity & Security"], summary="Register a new customer account")
def register_user(user: UserRegister = Body(...)):
    """
    Hashes the user password and creates a new profile entry in the database.
    """
    try:
        connection = call_database()
        cursor = connection.cursor()
        hashed_password = pwd_context.hash(user.password)
        query = "INSERT INTO userinformation (user_name, email, password) VALUES (?, ?, ?)"
        cursor.execute(query, (user.user_name, user.email, hashed_password))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "success", "message": "Registration successful"}
    except sqlite3.Error as dbrrr:
        raise HTTPException(status_code=400, detail=str(dbrrr))


@app.post("/login", response_model=LoginResponse, tags=["Identity & Security"], summary="Authenticate user and issue JWT token")
def login_user(user_data: UserLogin = Body(...)):
    """
    Verifies user credentials and generates a secure, timed JSON Web Token.
    """
    try:
        connection = call_database()
        cursor = get_dict_cursor(connection)
        query = "SELECT * FROM userinformation WHERE email = ?"
        cursor.execute(query, (user_data.email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if not user or not pwd_context.verify(user_data.password, user['password']):
            raise HTTPException(status_code=400, detail="Invalid Credentials")
            
        payload = {
            "user_id": user['user_id'],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer", "status": "Login successful"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/orders", response_model=OrderResponse, tags=["Transactional Orders"], summary="Place a live food order")
def place_new_order(order_data: placeorder = Body(...)):
    """
    Fetches base food price, calculates total bill, and logs the final order.
    """
    try:
        connection = call_database()
        cursor = get_dict_cursor(connection)
        query = "SELECT item_price FROM menu WHERE item_id = ?"
        cursor.execute(query, (order_data.item_id,))
        menu = cursor.fetchone()
        
        if not menu:
            cursor.close()
            connection.close()
            raise HTTPException(status_code=404, detail="Food item not found in menu")
            
        item_price = menu['item_price']
        calculated_total = item_price * order_data.quantity
        
        insert_query = "INSERT INTO orders (user_id, item_id, quantity, total_price) VALUES (?, ?, ?, ?)"
        cursor.execute(insert_query, (order_data.user_id, order_data.item_id, order_data.quantity, calculated_total))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "Order Placed Successfully!", "total_bill": float(calculated_total)}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/{user_id}", tags=["Order History"], summary="Fetch historical paginated order history")
def get_order_history(user_id: int, page: int = 1, limit: int = 5, order_status: str = None):
    """
    Retrieves previous checkout records using mathematical offset pagination.
    """
    try:
        connection = call_database()
        cursor = get_dict_cursor(connection)
        offset = (page - 1) * limit
        
        if order_status:
            query = "SELECT * FROM orders WHERE user_id = ? AND order_status = ? LIMIT ? OFFSET ?"
            params = (user_id, order_status, limit, offset)
        else:
            query = "SELECT * FROM orders WHERE user_id = ? LIMIT ? OFFSET ?"
            params = (user_id, limit, offset)
            
        cursor.execute(query, params)
        history = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"page": page, "limit": limit, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/report", tags=["Business Intelligence Analytics"], summary="Get order counts grouped by status")
def get_business_report(status: str = None):
    """
    Uses database grouping options to count orders sorted by fulfillment status.
    """
    try:
        connection = call_database()
        cursor = get_dict_cursor(connection)
        if status:
            query = "SELECT order_status, COUNT(*) as count FROM orders WHERE order_status = ? GROUP BY order_status"
            cursor.execute(query, (status,))
        else:
            query = "SELECT order_status, COUNT(*) as count FROM orders GROUP BY order_status"
            cursor.execute(query)
            
        report = cursor.fetchall()
        cursor.close()
        connection.close()
        return report
    except sqlite3.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))


@app.get("/analytics/basic-report", tags=["Business Intelligence Analytics"], summary="Get gross revenue metrics")
def get_basic_financial_report():
    """
    Runs native SQL aggregations to calculate total revenue metrics and customer volumes.
    """
    try:
        connection = call_database()
        cursor = get_dict_cursor(connection)
        query = """
            SELECT 
                SUM(total_price) as gross_revenue, 
                COUNT(*) as total_orders, 
                COUNT(DISTINCT user_id) as unique_customers 
            FROM orders
        """
        cursor.execute(query)
        report = cursor.fetchone()
        cursor.close()
        connection.close()
        return report
    except sqlite3.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))