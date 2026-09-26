import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in environment (.env).")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE contracts ADD COLUMN IF NOT EXISTS document_url VARCHAR;")
    conn.commit()
    print("Database fix applied: contracts.document_url added successfully.")
finally:
    cur.close()
    conn.close()
