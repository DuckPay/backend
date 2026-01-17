from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Hash password
def get_password_hash(password):
    # bcrypt only supports passwords up to 72 bytes
    safe_password = password[:72] if isinstance(password, str) else password
    # Convert to bytes if it's a string
    password_bytes = safe_password.encode('utf-8') if isinstance(safe_password, str) else safe_password
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed_bytes.decode('utf-8')

# Verify password
def verify_password(plain_password, hashed_password):
    # bcrypt only supports passwords up to 72 bytes
    safe_password = plain_password[:72] if isinstance(plain_password, str) else plain_password
    # Convert to bytes
    password_bytes = safe_password.encode('utf-8') if isinstance(safe_password, str) else safe_password
    hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
    # Verify
    return bcrypt.checkpw(password_bytes, hashed_bytes)

# Create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Decode access token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
