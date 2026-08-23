from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return payload


def role_required(
    allowed_roles: list[str],
):
    def wrapper(
        current_user=Depends(get_current_user),
    ):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

        return current_user

    return wrapper
