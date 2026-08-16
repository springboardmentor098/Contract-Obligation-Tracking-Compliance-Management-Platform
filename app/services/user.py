from sqlalchemy.orm import Session

from app.models.contracts import Contract
from app.models.activities import Activity

from app.models.user import User
from app.repositories.user import (
    get_user_by_email,
    create_user,
)
from app.schemas.user import UserCreate
from app.utils.security import hash_password


def register_user(db: Session, user_data: UserCreate):
    existing_user = get_user_by_email(db, user_data.email)

    if existing_user:
        raise ValueError("Email already registered")

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role
    )

    return create_user(db, new_user)


def get_all_users(db: Session):
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user_service(
    db: Session,
    user_id: int,
    user_data: UserCreate
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.password = hash_password(user_data.password)
    user.role = user_data.role

    db.commit()
    db.refresh(user)

    return user


def delete_user_service(
    db: Session,
    user_id: int
    ):
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError("User not found")

        contracts = db.query(Contract).filter(
            Contract.user_id == user_id
        ).all()

        for contract in contracts:
            db.query(Activity).filter(
                Activity.contract_id == contract.id
            ).delete()

        db.query(Contract).filter(
            Contract.user_id == user_id
        ).delete()

        db.delete(user)
        db.commit()

        return {
            "message": "User deleted successfully"
        }