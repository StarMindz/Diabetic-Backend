from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.user_model import User as UserModel
from app.database import get_db

# Constants
SECRET_KEY = "51e10bb3aaad8bea49197e824a9d77339da6a38542fda8460f40d8c0ba5d78d5"  # Use a strong, secret value for JWT encoding/decoding
ALGORITHM = "HS256"  # Algorithm used for JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 2800  # Token expiry time

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")

# Hashing Passwords
def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a hashed password against an input password."""
    return pwd_context.verify(plain_password, hashed_password)

# JWT Handling
def create_access_token(data: UserModel) -> str:
    """Create a JWT token that stores user data and has an expiry."""
    userClaims = {
        "email": data.email,
        "user_id": data.id,
        "username": data.full_name,
        "email": data.email
    }
    expire = datetime.utcnow() + (timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    userClaims.update({"exp": expire})
    encoded_jwt = jwt.encode(userClaims, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
def decode_access_token(token: str):
    """Decode JWT token and check if it's still valid (not expired)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('exp') < datetime.utcnow().timestamp():
            raise JWTError("Token has expired")
        return payload
    except JWTError:
        return None

# Password Reset Tokens
def generate_password_reset_token(email: str) -> str:
    """Generate a token for resetting password, valid for 1 hour."""
    delta = timedelta(hours=1)
    data = {"email": email, "exp": datetime.utcnow() + delta}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_password_reset_token(token: str) -> str:
    """Verify the reset token and return the email if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload['exp'] < datetime.utcnow():
            return None
        return payload['email']
    except JWTError:
        return None

# Authentication Middleware
def authenticate_user(db: Session, email: str, password: str):
    """Authenticate user by email and password."""
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def get_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Extract the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token)
        if payload is None or 'email' not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid or expired",
                headers={"WWW-Authenticate": "Bearer"}
            )

        email = payload['email']
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )