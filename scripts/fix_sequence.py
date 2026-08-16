import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.database.database import engine

def fix_sequences():
    with engine.begin() as conn:
        conn.execute(text("""
            SELECT setval(
                pg_get_serial_sequence('contracts', 'id'),
                COALESCE((SELECT MAX(id) FROM contracts), 0) + 1,
                false
            );
        """))
    print("PostgreSQL contracts sequence reset successfully!")

if __name__ == "__main__":
    fix_sequences()
