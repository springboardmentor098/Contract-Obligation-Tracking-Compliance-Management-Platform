import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.database.database import engine

def migrate():
    with engine.begin() as conn:
        # 1. Rename contract_id to id if contract_id column exists
        res = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'contracts' AND column_name = 'contract_id'
        """)).fetchone()
        if res:
            print("Renaming contract_id to id and updating FKs...")
            conn.execute(text('ALTER TABLE obligations DROP CONSTRAINT IF EXISTS obligations_contract_id_fkey;'))
            conn.execute(text('ALTER TABLE renewals DROP CONSTRAINT IF EXISTS renewals_contract_id_fkey;'))
            conn.execute(text('ALTER TABLE contracts RENAME COLUMN contract_id TO id;'))
            conn.execute(text('ALTER TABLE obligations ADD CONSTRAINT obligations_contract_id_fkey FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE;'))
            conn.execute(text('ALTER TABLE renewals ADD CONSTRAINT renewals_contract_id_fkey FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE;'))

        # 2. Add contract_number column if not exists
        res = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'contracts' AND column_name = 'contract_number'
        """)).fetchone()
        if not res:
            print("Adding contract_number column...")
            conn.execute(text('ALTER TABLE contracts ADD COLUMN contract_number VARCHAR(100);'))
            conn.execute(text("UPDATE contracts SET contract_number = CONCAT('CNT-', 1000 + id);"))
            conn.execute(text('ALTER TABLE contracts ALTER COLUMN contract_number SET NOT NULL;'))
            conn.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_contracts_contract_number ON contracts (contract_number);'))

        # 3. Add category column if not exists
        res = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'contracts' AND column_name = 'category'
        """)).fetchone()
        if not res:
            print("Adding category column...")
            conn.execute(text('ALTER TABLE contracts ADD COLUMN category VARCHAR(100);'))
            conn.execute(text("""
                UPDATE contracts SET category = CASE 
                    WHEN contract_type = 'Vendor' THEN 'Vendor Contract'
                    WHEN contract_type = 'Service' THEN 'Service Agreement'
                    WHEN contract_type = 'Employment' THEN 'Employment Contract'
                    WHEN contract_type = 'Software' THEN 'Service Agreement'
                    WHEN contract_type = 'Licensing' THEN 'Service Agreement'
                    WHEN contract_type = 'NDA' THEN 'Confidentiality Agreement'
                    ELSE 'Vendor Contract'
                END;
            """))
            conn.execute(text('ALTER TABLE contracts ALTER COLUMN category SET NOT NULL;'))

        # 4. Add description column if not exists
        res = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'contracts' AND column_name = 'description'
        """)).fetchone()
        if not res:
            print("Adding description column...")
            conn.execute(text('ALTER TABLE contracts ADD COLUMN description TEXT;'))

    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
