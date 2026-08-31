from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.utils.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="OAuth2PasswordBearer",
    auto_error=False,
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print("TOKEN RECEIVED:", token)

    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    email = payload.get("sub")
    user_id = payload.get("user_id")

    if email is None and user_id is None:
        raise credentials_exception

    user = None

    if user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()

    if user is None and email is not None:
        user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise credentials_exception

    return user