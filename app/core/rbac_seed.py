import logging
import os
from pathlib import Path
import sys

# Ensure root directory is on sys.path when executed directly as a script
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password, verify_password

logger = logging.getLogger("contractiq.rbac_seed")

DEFAULT_RBAC_USERS = [
    {
        "full_name": "System Administrator",
        "email": "admin@contractiq.com",
        "password": "Admin@123",
        "role": "Admin",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Admin",
    },
    {
        "full_name": "Legal Manager",
        "email": "legal@contractiq.com",
        "password": "Legal@123",
        "role": "Legal Manager",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Legal",
    },
    {
        "full_name": "Contract Manager",
        "email": "contract@contractiq.com",
        "password": "Contract@123",
        "role": "Contract Manager",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Contract",
    },
    {
        "full_name": "Compliance Officer",
        "email": "compliance@contractiq.com",
        "password": "Compliance@123",
        "role": "Compliance Officer",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Compliance",
    },
    {
        "full_name": "Contract Viewer",
        "email": "viewer@contractiq.com",
        "password": "Viewer@123",
        "role": "Viewer",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Viewer",
    },
]


def ensure_default_rbac_users(db: Session = None):
    """
    Ensures that the 5 default RBAC users exist with bcrypt-hashed passwords,
    active status, and exact roles as specified in the platform requirements.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        updated_count = 0
        created_count = 0

        for user_data in DEFAULT_RBAC_USERS:
            email_clean = user_data["email"].strip().lower()
            user = db.query(User).filter(func.lower(User.email) == email_clean).first()

            if user:
                # Check if password matches the required default
                password_valid = False
                try:
                    password_valid = verify_password(user_data["password"], user.password)
                except Exception:
                    password_valid = False

                needs_update = False
                if not password_valid:
                    user.password = hash_password(user_data["password"])
                    needs_update = True

                if user.role != user_data["role"]:
                    user.role = user_data["role"]
                    needs_update = True

                if not user.is_active:
                    user.is_active = True
                    needs_update = True

                if not user.avatar_url:
                    user.avatar_url = user_data["avatar_url"]
                    needs_update = True

                if needs_update:
                    updated_count += 1
            else:
                new_user = User(
                    full_name=user_data["full_name"],
                    email=email_clean,
                    password=hash_password(user_data["password"]),
                    role=user_data["role"],
                    is_active=True,
                    avatar_url=user_data["avatar_url"],
                    preferences={"theme": "light", "notifications_enabled": True},
                )
                db.add(new_user)
                created_count += 1

        db.commit()
        logger.info(
            f"RBAC Seed complete: {created_count} created, {updated_count} updated default users."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding default RBAC users: {e}")
        raise
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    ensure_default_rbac_users()
    print("Default RBAC users successfully seeded.")
