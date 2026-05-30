# 🍕 Restaurant Management API

A robust backend REST API built to manage restaurant operations, handle menu items, track customer orders, and generate financial reports.

## 🛠️ Tech Stack
* **Language:** Python
* **Framework:** FastAPI
* **Database:** MySQL
* **Core Libraries:** Uvicorn, Pydantic, MySQL Connector Python, Passlib, PyJWT

## 🚀 Features
* **User Authentication & Security:** Secure user registration and login endpoints utilizing      password hashing via `passlib` (bcrypt) and encrypted stateless token generation via `PyJWT`.
* **Menu Management (CRUD):** Complete database control system supporting actions to view the full food menu, add new items, modify pricing/details, and delete existing menu records.
* **Order Processing Engine:** Automated route that accepts user orders, cross-checks real-time item prices from the MySQL menu table, processes multi-item billing math, and locks records down.
* **Advanced History Pagination:** Optimized history route for users that utilizes query parameters (`page`, `limit`, `offset`) to pull chunked database segments, avoiding system lag.
* **Business Intelligence Reports:** Advanced analytics endpoints that run complex SQL aggregation functions (`SUM`, `COUNT`, `DISTINCT`) and `GROUP BY` groupings to output operational revenue metrics.

## 🏃‍♂️ How to Run Locally
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: (`uvicorn main:app --reload`)
