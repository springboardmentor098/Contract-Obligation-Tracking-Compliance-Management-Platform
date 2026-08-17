from sqlalchemy.orm import Session

from app.repositories import user_repository
from app.schemas.user import UserCreate, UserUpdate


class DuplicateUserError(Exception):
    """Raised when a username or email already exists."""


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate):
        if user_repository.get_user_by_username(self.db, user.username):
            raise DuplicateUserError(f"Username '{user.username}' already exists.")
        if user_repository.get_user_by_email(self.db, user.email):
            raise DuplicateUserError(f"Email '{user.email}' already exists.")
        return user_repository.create_user(self.db, user)

    def get_user(self, user_id: int):
        return user_repository.get_user(self.db, user_id)

    def list_users(self, skip: int = 0, limit: int = 100):
        return user_repository.get_users(self.db, skip, limit)

    def update_user(self, user_id: int, user_update: UserUpdate):
        if user_update.username and user_repository.get_user_by_username(
            self.db, user_update.username
        ):
            existing = user_repository.get_user_by_username(self.db, user_update.username)
            if existing and existing.id != user_id:
                raise DuplicateUserError(
                    f"Username '{user_update.username}' already exists."
                )
        if user_update.email and user_repository.get_user_by_email(
            self.db, user_update.email
        ):
            existing = user_repository.get_user_by_email(self.db, user_update.email)
            if existing and existing.id != user_id:
                raise DuplicateUserError(f"Email '{user_update.email}' already exists.")
        return user_repository.update_user(self.db, user_id, user_update)

    def delete_user(self, user_id: int):
        return user_repository.delete_user(self.db, user_id)
