# DuckPay Backend

DuckPay is a modern payment management system with a robust and scalable backend API.

## Tech Stack

- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database
- **JWT** - Secure token authentication
- **SSE (Server-Sent Events)** - Real-time event streaming
- **Pydantic** - Data validation and serialization

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database
- pip or poetry package manager

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on the `.env.example` template:

```bash
cp .env.example .env
```

3. Configure the database connection in the `.env` file:

```
DATABASE_URL="postgresql://username:password@localhost:5432/duckpay"
```

4. Run database migrations (if using Alembic):

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Running the Application

#### Development Mode

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

#### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
app/
├── api/              # API routes
│   ├── admin.py      # Admin endpoints
│   ├── categories.py # Category endpoints
│   ├── records.py    # Record endpoints
│   ├── status.py     # Status endpoints
│   └── users.py      # User endpoints
├── crud/             # CRUD operations
├── models/           # Database models
├── schemas/          # Pydantic schemas
├── utils/            # Utility functions
│   ├── auth.py       # Authentication utilities
│   ├── database.py   # Database connection
│   └── jwt.py        # JWT token handling
└── main.py           # Application entry point
```

## Features

- **User Management** - Registration, authentication, and profile management
- **Payment Records** - Create, read, update, and delete payment records
- **Categories** - Manage payment categories
- **Real-time Updates** - SSE for live data updates
- **Admin Dashboard** - Administrative functions
- **Secure Authentication** - JWT-based authentication with password hashing

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions and variables
- Write comprehensive docstrings
- Implement proper error handling
- Use dependency injection for shared resources

### Testing

```bash
# Run tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=app
```

### Linting

```bash
# Install linting tools
pip install flake8 black isort

# Run flake8
flake8 app

# Run black formatter
black app

# Run isort for import sorting
isort app
```

## License

MIT
