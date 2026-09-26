from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone

from app.core.roles import UserRole

# Secret key and algorithm for JWT (Keep this safe!)
SECRET_KEY = "contractiq_super_secret_key"
ALGORITHM = "HS256"

# This creates the "Authorize" button in Swagger and tells it where to login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Set up the bcrypt hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def normalize_role_name(role_value: str | None) -> str | None:
    if role_value is None:
        return None
    if hasattr(role_value, "value"):
        role_value = role_value.value

    normalized = str(role_value).strip()
    aliases = {
        "admin": "Admin",
        "administrator": "Admin",
        "legal manager": "Legal Manager",
        "legal_manager": "Legal Manager",
        "employee": "Employee",
        "contract manager": "Contract Manager",
        "contract_manager": "Contract Manager",
        "manager": "Manager",
        "compliance officer": "Compliance Officer",
        "compliance_officer": "Compliance Officer",
        "department head": "Department Head",
        "department_head": "Department Head",
    }
    return aliases.get(normalized.lower(), normalized)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates the JWT token and returns the user payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_role(required_roles: list):
    """Protect routes with a list of allowed roles."""

    allowed_roles = {
        normalize_role_name(str(role))
        for role in required_roles
        if normalize_role_name(str(role))
    }

    def role_dependency(current_user: dict = Depends(get_current_user)):
        user_role = normalize_role_name(current_user.get("role"))
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. User role is missing from token.",
            )

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(sorted(allowed_roles))}",
            )
        return current_user

    return role_dependency


ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    """Creates a new JWT token valid for 30 minutes."""
    to_encode = data.copy()
    normalize = normalize_role_name(data.get("role"))
    if normalize:
        to_encode["role"] = normalize

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt