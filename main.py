from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from passlib.context import CryptContext
import mysql.connector
import jwt
import datetime
from typing import List
import os
import json
import redis

app = FastAPI()

# --- Security Configuration ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

# --- Redis Initialization ---
# Setup connection to your local Memurai / Redis engine running on port 6379
redis_client = redis.Redis(
    host='localhost', 
    port=6379, 
    db=0, 
    decode_responses=True  # Important: Ensures cache returns clean strings instead of bytes
)

def call_database():
    ca_path = os.path.join(os.path.dirname(__file__), 'ca.pem')

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 13080)),
        ssl_ca=ca_path if os.path.exists(ca_path) else None,
        ssl_verify_cert=True if os.path.exists(ca_path) else False
    )


# PYDANTIC REQUEST / RESPONSE MODELS
class MenuResponse(BaseModel):
    item_id: int
    item_name: str
    item_price: int
    category: str
    calories: int
    health_score: int

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

class HealthRequest(BaseModel):
    item_id: int

class HealthResponse(BaseModel):
    selected_item: str
    healthier_alternative: str
    selected_calories: int
    alternative_calories: int
    reason: str


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
    Uses Redis cache storage to bypass heavy database disk reads on consecutive requests.
    """
    cache_key = "restaurant_food_menu"
    
    # STEP A: Check Redis Cache First (RAM Read)
    try:
        cached_menu = redis_client.get(cache_key)
        if cached_menu:
            # Cache Hit: Convert JSON string back to a Python list and return instantly
            return json.loads(cached_menu)
    except Exception:
        pass  # Fallback safety: If Redis server has issues, silently skip and fall back to MySQL
        
    # STEP B: Cache Miss - Fetch from your MySQL Database
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM menu")
        menu = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # STEP C: Save the fresh data into Redis for the next customer
        if menu:
            try:
                # Convert list to JSON string and store it for 10 minutes (600 seconds)
                redis_client.setex(cache_key, 600, json.dumps(menu))
            except Exception:
                pass  # Safety: If saving to Redis fails, protect endpoint and return data anyway
                
        return menu
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))






@app.post("/menu", tags=["Menu Management"], summary="Add a new dish to the menu")
def add_menu_item(item_name: str, item_price: int, category: str):
    """
    Inserts a completely new food item details into the menu table.
    Evicts out-of-date cache to ensure data transparency.
    """
    if item_price <= 0: raise HTTPException(status_code=400, detail="Price must be positive")
    try:
        connection = call_database()
        cursor = connection.cursor()
        query = "INSERT INTO menu (item_name, item_price, category) VALUES (%s, %s, %s)"
        cursor.execute(query, (item_name, item_price, category))
        connection.commit()
        cursor.close()
        connection.close()
        try:
            redis_client.delete("restaurant_food_menu")
        except Exception:
            pass
            
        return {"status": "success", "message": "Item added successfully"}
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))





@app.put("/menu/{item_id}", tags=["Menu Management"], summary="Update an existing menu item")
def update_menu_items(item_id: int, item_name: str, item_price: int, category: str):
    """
    Modifies an existing food item matching the provided item_id parameter.
    Evicts out-of-date cache to prevent display errors.
    """
    try:
        connection = call_database()
        cursor = connection.cursor()
        query = "UPDATE menu SET item_name=%s, item_price=%s, category=%s WHERE item_id=%s"
        cursor.execute(query, (item_name, item_price, category, item_id))
        connection.commit()
        cursor.close()
        connection.close()
        
        # CRITICAL CACHE EVICTION: Clear out stale cache values on change tracking rules
        try:
            redis_client.delete("restaurant_food_menu")
        except Exception:
            pass
            
        return {"status": "updated successfully"}
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))





@app.delete("/menu/{item_id}", tags=["Menu Management"], summary="Remove a dish from the menu")
def delete_menu_item(item_id: int):
    """
    Deletes a food item completely from the database using its item_id.
    Evicts deleted metrics from storage.
    """
    try:
        connection = call_database()
        cursor = connection.cursor()
        query = "DELETE FROM menu WHERE item_id=%s"
        cursor.execute(query, (item_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        # CRITICAL CACHE EVICTION: Ensure deleted item disappears from memory layer immediately
        try:
            redis_client.delete("restaurant_food_menu")
        except Exception:
            pass
            
        return {"status": "deleted successfully"}
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))





@app.post("/register", response_model=RegisterResponse, tags=["Identity & Security"], summary="Register a new customer account")
def register_user(user: UserRegister = Body(...)):
    """
    Hashes the user password and creates a new profile entry in the database.
    """
    connection=None
    try:
        hashed_password = pwd_context.hash(user.password)
        connection = call_database()
        cursor = connection.cursor()
        query = "INSERT INTO userinformation (user_name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (user.user_name, user.email,hashed_password))
        connection.commit()
        cursor.close()
        connection.close()
        return {"status": "success", "message": "Registration successful"}
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=400, detail=str(dbrrr))
    finally:
        if connection and connection.is_connected():
            connection.close()





@app.post("/login", response_model=LoginResponse, tags=["Identity & Security"], summary="Authenticate user and issue JWT token")
def login_user(user_data: UserLogin = Body(...)):
    """
    Verifies user credentials and generates a secure, timed JSON Web Token.
    """
    connection=None
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM userinformation WHERE email = %s"
        cursor.execute(user_data.email) # Safe execution tracking setup
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid email or password")
        password_matches = pwd_context.verify(user_data.password,user["password"])
            
        if not password_matches:
            raise HTTPException(status_code=400, detail="Invalid email or password")
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        token_payload = {
            "email": user['email'],
            "exp": expire
        }
        
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer", "status": "Login Successful!"}
        
    except mysql.connector.Error as db_err:
        raise HTTPException(status_code=500, detail=f"Database verification error: {db_err.msg}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            
            




@app.post("/orders", response_model=OrderResponse, tags=["Transactional Orders"], summary="Place a live food order")
def place_new_order(order_data: placeorder = Body(...)):
    """
    Fetches base food price, calculates total bill, and logs the final order.
    Utilizes ACID transaction processing to rollback changes on failure.
    """
    if order_data.quantity <= 0: 
        raise HTTPException(status_code=400, detail="Quantity must be > 0")
    connection = None
    cursor = None
    try:
        connection = call_database()
        # START TRANSACTION (Turn off autocommit to control the transaction manually)
        connection.autocommit = False
        cursor = connection.cursor(dictionary=True)
        # Step A: Fetch food item price
        query = "SELECT item_price FROM menu WHERE item_id = %s"
        cursor.execute(query, (order_data.item_id,))
        menu = cursor.fetchone()
        if not menu:
            raise HTTPException(status_code=404, detail="Food item not found in menu")
        item_price = menu['item_price']
        calculated_total = item_price * order_data.quantity
        # Step B: Log the final order record
        insert_query = "INSERT INTO orders (user_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (order_data.user_id, order_data.item_id, order_data.quantity, calculated_total))
        # COMMIT TRANSACTION (Permanently save changes on logical completion)
        connection.commit()
        return {"status": "Order Placed Successfully!", "total_bill": float(calculated_total)}
    except Exception as e:
        # ROLLBACK ON FAILURE (Wipe changes clean if any execution fails mid-transit)
        if connection and connection.is_connected():
            connection.rollback()
        if isinstance(e, HTTPException): 
            raise e
        raise HTTPException(status_code=500, detail=f"Transaction failed. Order rolled back: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()




@app.get("/orders/{user_id}", tags=["Order History"], summary="Fetch historical paginated order history")
def get_order_history(user_id: int, page: int = 1, limit: int = 5, order_status: str = None):
    """
    Retrieves previous checkout records using mathematical offset pagination.
    """
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        offset = (page - 1) * limit
        if order_status:
            query = "SELECT * FROM orders WHERE user_id = %s AND order_status = %s LIMIT %s OFFSET %s"
            params = (user_id, order_status, limit, offset)
        else:
            query = "SELECT * FROM orders WHERE user_id = %s LIMIT %s OFFSET %s"
            params = (user_id, limit, offset)
        cursor.execute(query, params)
        history = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"page": page, "limit": limit, "data": history}
    except Exception as e:
         print("ORDER ERROR:", str(e))
         raise HTTPException(status_code=500, detail=str(e))





@app.get("/analytics/report", tags=["Business Intelligence Analytics"], summary="Get order counts grouped by status")
def get_business_report(status: str = None):
    """
    Uses database grouping options to count orders sorted by fulfillment status.
    """
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        if status:
            query = "SELECT order_status, COUNT(*) as count FROM orders WHERE order_status = %s GROUP BY order_status"
            cursor.execute(query, (status,))
        else:
            query = "SELECT order_status, COUNT(*) as count FROM orders GROUP BY order_status"
            cursor.execute(query)
        report = cursor.fetchall()
        cursor.close()
        connection.close()
        return report
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))





@app.get("/analytics/basic-report", tags=["Business Intelligence Analytics"], summary="Get gross revenue metrics")
def get_basic_financial_report():
    """
    Runs native SQL aggregations to calculate total revenue metrics and customer volumes.
    """
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT SUM(total_price) as gross_revenue, COUNT(*) as total_orders, COUNT(DISTINCT user_id) as unique_customers FROM orders"
        cursor.execute(query)
        report = cursor.fetchone()
        cursor.close()
        connection.close()
        return report
    except mysql.connector.Error as dbrrr:
        raise HTTPException(status_code=500, detail=str(dbrrr))





@app.post("/healthier-alternative", response_model=HealthResponse, tags=["Smart Recommendations"], summary="Suggest a healthier alternative food item")
def healthier_alternative(data: HealthRequest = Body(...)):
    """
    providing option to choice healthier version for calorie dense food
    """
    try:
        connection = call_database()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM menu WHERE item_id = %s", (data.item_id,))
        selected_item = cursor.fetchone()
        if not selected_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        cursor.execute(
            """SELECT * FROM menu WHERE category = %s AND health_score > %s
            ORDER BY health_score DESC, calories ASC LIMIT 1""",
            (selected_item["category"], selected_item["health_score"])
        )
        alternative = cursor.fetchone()
        cursor.close()
        connection.close()
        if not alternative:
            return {
                "selected_item": selected_item["item_name"],
                "healthier_alternative": selected_item["item_name"],
                "selected_calories": selected_item["calories"],
                "alternative_calories": selected_item["calories"],
                "reason": "No healthier alternative available"
            }
        return {
            "selected_item": selected_item["item_name"],
            "healthier_alternative": alternative["item_name"],
            "selected_calories": selected_item["calories"],
            "alternative_calories": alternative["calories"],
            "reason": "Higher health score and lower calories"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
