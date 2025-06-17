# FastAPI Event Management Backend

This is a FastAPI backend for managing events, categories, and bookings with PostgreSQL support.

---

## Project Structure

├── app/
│ ├── auth / # Authentication logic, jwt logic
│ ├── routes / # API routers
│ ├── core / # Config and constants
│ ├── db/ # SQLAlchemy models & DB connection
│ ├── schemas/ # Pydantic schemas
│ └── exceptions/ # Exceptions
├── main.py # FastAPI entrypoint
├── docker-compose.yml # Docker setup
└── README.md


---

## 🛠️ Prerequisites

Before running this project, make sure you have:

- Python 3.10+
- PostgreSQL installed or Docker installed
- `pip` to install packages
- Docker & Docker Compose (for containerized setup)

---

## Running Manually (Python Environment)

### Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows use .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the App

```bash
uvicorn app.main:app --reload
```
- The app will be available at http://localhost:8000

## Running with Docker Compose

Before starting the server, follow these steps:
- Create a postgres_data folder inside the root of the app directory.
- Get the absloute path of the postgres_data folder.
- Replace <postgres_data> with the absolute path in the docker-compose.yml file at line number 15  

### Start the service


```bash
docker-compose up --build
```
This will:
- start the FastAPI app
- Start PostgreSQL DB
- Mount your code for live reloading

### API Available at

```bash
http://0.0.0.0:8000
```

### Stop the services

```bash
docker-compose down
```


# By default login details available in DB 

### postgres DB login
For local server
```bhash
user: postgres
host: localhost or 127.0.0.1
password: postgres
```

For docker server
```bhash
user: postgres
host: 0.0.0.0
password: postgres
```

### Admin Logins details

```bhash

// Admin 1
username: admin@example.com
passowrd: admin123

// Admin 2
username: admin1@example.com
password: admin123
```

### Non Admin Login details
```bhash

// user
username: user@example.com
passowrd: user23

// Test
username: test@example.com
password: test123
```

## API DOCS

- Swagger UI: http://0.0.0.0:8000/docs
- ReDoc: https://0.0.0.0:8000/redoc

