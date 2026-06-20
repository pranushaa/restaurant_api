# 🍽️ Happy Kitchen — Restaurant Management API

> Built this to understand how real backend systems work — menu management, order processing, caching, and analytics all in one place.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-Aiven_Cloud-orange?style=flat-square&logo=mysql)](https://aiven.io)
[![Redis](https://img.shields.io/badge/Redis-Caching-red?style=flat-square&logo=redis)](https://redis.io)
[![Render](https://img.shields.io/badge/Deployed-Render-purple?style=flat-square)](https://render.com)
[![Docker](https://img.shields.io/badge/Docker-Containerization-blue?style=flat-square&logo=docker)](https://www.docker.com)

**Live API →** https://restaurant-api-xj8w.onrender.com/docs  
**GitHub →** https://github.com/pranushaa/restaurant_api

---

## Why I built this

I wanted to go beyond tutorials and build something that actually handles real problems — what happens when two users order at the same time? How do you stop reading from the database on every single request? What happens if an order fails halfway through saving?

This project is my answer to those questions.

---

## What it does

A REST API that handles the backend of a restaurant:
- Customers can browse the menu, register, log in, and place orders
- Staff can add, update, or remove menu items
- Business can pull revenue reports and order analytics
- A smart feature suggests a healthier food alternative based on calories and health score

---

## 🛠️ Tech Stack
* **Backend:** Python
* **Database:** MySQL
* **DevOps:** Docker (Containerization & local development)


## 🏗️ Architecture

I separated the code into three clear layers so each part has one job:

```
HTTP Request
     │
     ▼
 Routes Layer          → receives the request, calls service
     │
     ▼
 Services Layer        → business logic, calculations, decisions
     │
     ▼
 Repository Layer      → only place that talks to the database
     │
     ▼
MySQL (Aiven) + Redis
```

```
RESTAURANT_API/
├── main.py                        # registers all routers
├── database.py                    # MySQL connection with SSL
├── app/
│   ├── models.py                  # Pydantic request/response models
│   ├── cache.py                   # Redis client
│   ├── routes/                    # HTTP endpoints
│   │   ├── menu.py
│   │   ├── auth.py
│   │   ├── orders.py
│   │   ├── analytics.py
│   │   └── health.py
│   ├── services/                  # Business logic
│   │   ├── menu_services.py
│   │   ├── auth_service.py
│   │   ├── order_service.py
│   │   ├── analytics_service.py
│   │   └── health_service.py
│   └── repositories/              # All SQL queries
│       ├── menu_repo.py
│       ├── user_repo.py
│       ├── order_repo.py
│       └── analytics_repo.py
```

---



## 🗃️ Database Design

```
┌──────────────────────┐        ┌──────────────────────┐
│   userinformation    │        │        menu           │
├──────────────────────┤        ├──────────────────────┤
│ PK user_id     INT   │        │ PK item_id      INT   │
│    user_name   STR   │        │    item_name    STR   │
│    email       STR   │        │    item_price   INT   │
│    password    STR   │        │    category     STR   │
└────────┬─────────────┘        │    calories     INT   │
         │                      │    health_score INT   │
         │ 1                    └──────────┬────────────┘
         │                                 │
         │ places                          │ referenced in
         ▼ N                               ▼ N
┌──────────────────────────────────────────────────────┐
│                        orders                         │
├──────────────────────────────────────────────────────┤
│ PK  order_id     INT   AUTO INCREMENT                 │
│ FK  user_id      INT   → userinformation.user_id      │
│ FK  item_id      INT   → menu.item_id                 │
│     quantity     INT                                  │
│     total_price  FLOAT                                │
│     order_status STR   DEFAULT 'pending'              │
│     created_at   DATETIME                             │
└──────────────────────────────────────────────────────┘
```

**Relationships:**
- One user → many orders (1:N)
- One menu item → many orders (1:N)


### Indexes Applied

| Table | Column | Reason |
|---|---|---|
| orders | user_id | Fast order history fetch per user |
| orders | item_id | Quick item lookup in orders |
| orders | order_status | Fast filtering in analytics queries |
| menu | category | Speeds up healthier alternative search |

Indexes added on columns used in WHERE clauses to avoid full table scans.

---



## 📌 API Endpoints

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Server health check |

### Menu Management
| Method | Endpoint | Description |
|---|---|---|
| GET | `/menu` | Fetch all items (Redis cached, 10 min TTL) |
| POST | `/menu` | Add new food item |
| PUT | `/menu/{item_id}` | Update existing item |
| DELETE | `/menu/{item_id}` | Remove item from menu |

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register new user (bcrypt hashed password) |
| POST | `/login` | Login and receive JWT token (30 min expiry) |

### Orders
| Method | Endpoint | Description |
|---|---|---|
| POST | `/orders` | Place order (ACID transaction) |
| GET | `/orders/{user_id}` | Paginated order history with status filter |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/report` | Order counts grouped by status |
| GET | `/analytics/basic-report` | Gross revenue, total orders, unique customers |

### Smart Feature
| Method | Endpoint | Description |
|---|---|---|
| POST | `/healthier-alternative` | Suggest healthier option in same category |

---



## 🧠 Technical Decisions & How They Work

### Redis Caching
The menu doesn't change every second, so reading from MySQL on every request is wasteful. I cache the menu in Redis for 10 minutes. On any write operation (add/update/delete), the cache is cleared immediately so the next request gets fresh data.

```
GET /menu
  ├── Redis has it? → return instantly
  └── Redis empty?  → query MySQL → store in Redis → return
```

### ACID Transactions with Rollback
An order involves two steps: fetch the price, then insert the order record. If step 2 fails after step 1, you'd have corrupted data. I use transactions so either both steps succeed or neither saves.

```python
connection.autocommit = False
try:
    fetch item price        # step 1
    insert order record     # step 2
    connection.commit()     # saves only if both succeed
except:
    connection.rollback()   # wipes everything on failure
```

### Race Condition Prevention
Under concurrent load, two requests hitting the order endpoint at the same time could both read the same data and both proceed. Transaction isolation at the database level prevents this.

### Healthier Alternative Logic
Queries items in the same category with a strictly higher health score, sorted by health score descending and calories ascending — returns the single best option.

```sql
SELECT * FROM menu
WHERE category = ? AND health_score > ?
ORDER BY health_score DESC, calories ASC
LIMIT 1
```

### Pagination
Order history uses offset-based pagination to avoid loading all records at once.

```
GET /orders/1?page=2&limit=5
offset = (2-1) * 5 = 5  →  fetches records 6 to 10
```

### Database Indexing Strategy
Indexes added on columns used frequently in WHERE clauses:
- `orders.user_id` — speeds up order history queries
- `orders.order_status` — speeds up analytics report grouping
- `menu.category` — speeds up healthier alternative search

Result: Avoids full table scans on large datasets.

### JWT Authentication
Passwords hashed with bcrypt on register. On login, hash is verified and a signed JWT token is returned with a 30-minute expiry.

### JWT Protected Route Authorization
POST /orders requires a valid JWT token.

Pass token in request header:
Authorization: Bearer <your_token>

Get token by calling POST /login first.
Token expires in 30 minutes.

---

### Rate Limiting
Brute-force protection on sensitive endpoints using slowapi.

- `POST /login` → limited to 5 requests/minute per IP
- `GET /` → limited to 100 requests/minute per IP

Exceeding the limit returns `429 Too Many Requests`. Rate limiting is automatically disabled during automated tests (via `conftest.py`) so the test suite isn't blocked by its own requests.


## 🔒 Security

- Passwords hashed with bcrypt — plain text never stored
- JWT tokens with 30-minute expiry
- All credentials in environment variables — nothing hardcoded
- SSL/TLS on all MySQL connections via ca.pem
- Parameterized queries throughout — no SQL injection possible

---

### Logging
Structured logging added to order processing using Python's 
built-in logging module.

- INFO  → successful order placed, history fetched
- WARNING → invalid input, item not found  
- ERROR → transaction failures, unexpected errors

Logs include user_id and item details for easy debugging.


## 📊 Sample Requests

**Register**
```json
POST /register
{ "user_name": "pranu", "email": "pranushav69@gmail.com", "password": "pass123" }

→ { "status": "success", "message": "Registration successful" }
```

**Place Order**
```json
POST /orders
{ "user_id": 1, "item_id": 3, "quantity": 2 }

→ { "status": "Order Placed Successfully!", "total_bill": 340.0 }
```

**Healthier Alternative**
```json
POST /healthier-alternative
{ "item_id": 5 }

→ {
    "selected_item": "Chicken Burger",
    "healthier_alternative": "Grilled Chicken Wrap",
    "selected_calories": 650,
    "alternative_calories": 420,
    "reason": "Higher health score and lower calories"
  }
```

---

## 🧪 Testing

Automated tests using pytest and FastAPI's TestClient cover core functionality:

- Server health check (`/`)
- Menu retrieval (`/menu`)
- Invalid login rejection (`/login`)

Run tests:
```bash
python -m pytest -v


## ⚙️ Local Setup

```bash
# Clone
git clone https://github.com/pranushaa/restaurant_api
cd restaurant_api

# Install
pip install -r requirements.txt

# Environment variables — create a .env file
DB_HOST=your_aiven_host
DB_USER=your_user
DB_PASS=your_password
DB_NAME=your_dbname
DB_PORT=13080
SECRET_KEY=your_secret_key

# Run
uvicorn main:app --reload

# Docs
http://localhost:8000/docs
```

---


## 📦 Dependencies

```
fastapi
uvicorn
mysql-connector-python
redis
passlib[bcrypt]
PyJWT
python-dotenv
slowapi
pytest
```

---

## 🎯 Backend Concepts Demonstrated

- REST API Design
- JWT Authentication
- Password Hashing (bcrypt)
- Redis Caching with Cache Invalidation
- ACID Transactions with Rollback
- Race Condition Prevention
- Database Indexing
- Pagination
- Proper logging
- SQL Aggregations
- Cloud Deployment
- Environment Variable Management
- Parameterized Queries (SQL Injection Prevention)
- Clean Architecture (Routes → Services → Repository)
- Docker 
- Rate Limiting (Brute-force Protection)
- Automated Testing (pytest)

---


## 🌐 Deployment

### Local Development with Docker
```bash
docker-compose up --build
```
Starts API + Redis together in containers.
Test at: http://localhost:8000/docs

### Production Deployment
- Hosted on **Render** — auto-deploys on every git push
- Database on **Aiven MySQL** — cloud-hosted with SSL
- Environment variables set in Render dashboard
- Live docs: https://restaurant-api-xj8w.onrender.com/docs

## 👤 Author

**Pranusha Velugubantla**  
📧 pranushav69@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/pranusha-velugubantla/) 
    [GitHub](https://github.com/pranushaa)