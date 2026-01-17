from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import users, categories, records, status, admin
from app.utils.database import engine, Base, init_db

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize database with default groups and permissions
init_db()

# Create FastAPI app
app = FastAPI(
    title="DuckPay",
    description="Where My Duck Goes?",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(records.router, prefix="/api/records", tags=["records"])
app.include_router(status.router, prefix="/api", tags=["status"])
app.include_router(admin.router, prefix="/api", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "欢迎使用记账系统 API"}
