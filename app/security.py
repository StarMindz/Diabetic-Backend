from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

# Constants
SECRET_KEY = "51e10bb3aaad8bea49197e824a9d77339da6a38542fda8460f40d8c0ba5d78d5"  # Use a strong, secret value for JWT encoding/decoding
ALGORITHM = "HS256"  # Algorithm used for JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiry time

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Hashing Passwords
def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a hashed password against an input password."""
    return pwd_context.verify(plain_password, hashed_password)

# JWT Handling
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT token that stores user data and has an expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decode JWT token and return the payload or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload if payload.get('exp') > datetime.utcnow() else None
    except JWTError:
        return None

# Password Reset Tokens
def generate_password_reset_token(email: str) -> str:
    """Generate a token for resetting password, valid for 1 hour."""
    delta = timedelta(hours=1)
    data = {"sub": email, "exp": datetime.utcnow() + delta}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_password_reset_token(token: str) -> str:
    """Verify the reset token and return the email if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['exp'] < datetime.utcnow():
            return None
        return payload['sub']
    except JWTError:
        return None

# Authentication Middleware
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Extract the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    payload = decode_access_token(token)
    if payload is None or (email := payload.get('sub')) is None:
        raise credentials_exception
    # Implementation to retrieve user from database goes here
    return {"email": email}  # Dummy user object
