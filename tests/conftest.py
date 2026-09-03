import os

# Keep automated tests independent from a developer's PostgreSQL instance.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_contractiq.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
