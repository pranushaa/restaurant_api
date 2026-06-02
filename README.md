# 🍽️ Restaurant Management API

A cloud-deployed backend application built with FastAPI and MySQL that manages restaurant operations including customer authentication, menu administration, order processing, order history management, and business analytics reporting.

The project demonstrates REST API development, secure authentication, database integration, cloud deployment, pagination, reporting, transaction handling, and performance optimization techniques used in modern backend systems.

## 🔗 Live API Documentation

https://restaurant-api-xj8w.onrender.com/docs

## 📂 Source Code

https://github.com/pranushaa/restaurant_api

---

# 🚀 Core Capabilities

### Authentication & Security

* Secure customer registration
* Password hashing using BCrypt
* JWT-based authentication
* Protected business reporting endpoints
* Credential verification and access control

### Menu Management

* Create menu items
* Retrieve menu catalog
* Update existing menu items
* Delete menu items
* Real-time database synchronization

### Order Processing

* Food order placement
* Dynamic bill calculation
* Quantity validation
* Order tracking
* Database-backed transaction processing

### Order History

* User-specific order retrieval
* Pagination support
* Status-based filtering
* Optimized query execution

### Business Analytics

* Revenue reporting
* Order aggregation reports
* Customer activity insights
* Operational status summaries

---

# 🏗️ System Architecture

```text
Client
   │
   ▼
Swagger UI / REST Client
   │
   ▼
FastAPI Application
   │
   ├── Authentication Layer
   ├── Business Logic Layer
   ├── Validation Layer
   └── Reporting Layer
   │
   ▼
MySQL Connector
   │
   ▼
Cloud MySQL Database
```

---

# 📊 Entity Relationship Diagram

```text
+----------------------+
| User Information     |
+----------------------+
| user_id (PK)         |
| user_name            |
| email                |
| password             |
+----------------------+
           │
           │ 1
           │
           │ M
+----------------------+
| Orders               |
+----------------------+
| order_id (PK)        |
| user_id (FK)         |
| item_id (FK)         |
| quantity             |
| total_price          |
| order_status         |
+----------------------+
           │
           │ M
           │
           │ 1
+----------------------+
| Menu                 |
+----------------------+
| item_id (PK)         |
| item_name            |
| item_price           |
| category             |
+----------------------+
```

---

# ⚡ Database Optimization

The system incorporates indexing strategies to improve query performance for:

* Authentication lookups
* Order history retrieval
* Analytics generation
* Status-based filtering

Benefits include:

* Reduced query execution time
* Faster report generation
* Improved scalability
* Better database efficiency

---

# 🔒 Transaction Management

The order processing workflow utilizes transaction handling principles to ensure database consistency.

Features include:

* Atomic order creation
* Commit on successful execution
* Rollback on failure
* Protection against partial writes
* Data integrity preservation

---

# 🧩 ACID Compliance

The application follows core ACID database principles:

### Atomicity

Operations complete entirely or not at all.

### Consistency

Database rules remain valid before and after transactions.

### Isolation

Concurrent operations do not interfere with each other.

### Durability

Committed data remains permanently stored.

---

# 🛠️ Technology Stack

| Category          | Technology |
| ----------------- | ---------- |
| Language          | Python     |
| Framework         | FastAPI    |
| Database          | MySQL      |
| Authentication    | JWT        |
| Password Security | BCrypt     |
| Validation        | Pydantic   |
| Deployment        | Render     |
| Cloud Database    | Aiven      |
| API Documentation | Swagger UI |

---

# 📖 API Endpoints

## Authentication

* POST /register
* POST /login

## Menu

* GET /menu
* POST /menu
* PUT /menu/{item_id}
* DELETE /menu/{item_id}

## Orders

* POST /orders
* GET /orders/{user_id}

## Analytics

* GET /analytics/report
* GET /analytics/basic-report

---

# 🌐 Deployment

The application is deployed as a publicly accessible cloud service with integrated API documentation and remote database connectivity.

Live Documentation:

https://restaurant-api-xj8w.onrender.com/docs

---

# 🎯 Backend Concepts Demonstrated

* REST API Design
* Authentication & Authorization
* Password Hashing
* JWT Token Management
* CRUD Operations
* Pagination
* SQL Aggregations
* Database Indexing
* Transaction Management
* ACID Properties
* Cloud Deployment
* API Documentation
* Data Validation
* Error Handling

---

# 👩‍💻 Author

Pranusha V

Backend Developer | Python | FastAPI | MySQL | REST APIs

