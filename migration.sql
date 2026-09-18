BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> ac38f3e2fe13

CREATE TABLE users (
    id SERIAL NOT NULL, 
    full_name VARCHAR(100) NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    role VARCHAR(50) NOT NULL, 
    is_active BOOLEAN NOT NULL, 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_id ON users (id);

INSERT INTO alembic_version (version_num) VALUES ('ac38f3e2fe13') RETURNING alembic_version.version_num;

-- Running upgrade ac38f3e2fe13 -> a86d3f36280f

ALTER TABLE users ADD COLUMN password VARCHAR(255);

UPDATE alembic_version SET version_num='a86d3f36280f' WHERE alembic_version.version_num = 'ac38f3e2fe13';

-- Running upgrade a86d3f36280f -> 6d48fbdb8a9e

CREATE TABLE audit_logs (
    id SERIAL NOT NULL, 
    user_id INTEGER, 
    action VARCHAR(255), 
    table_name VARCHAR(100), 
    record_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_audit_logs_id ON audit_logs (id);

CREATE TABLE contracts (
    id SERIAL NOT NULL, 
    contract_number VARCHAR(100), 
    vendor_name VARCHAR(255), 
    start_date DATE, 
    end_date DATE, 
    contract_value FLOAT, 
    status VARCHAR(50), 
    created_by INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(created_by) REFERENCES users (id)
);

CREATE INDEX ix_contracts_id ON contracts (id);

CREATE TABLE reports (
    id SERIAL NOT NULL, 
    generated_by INTEGER, 
    report_name VARCHAR(255), 
    report_type VARCHAR(100), 
    file_path VARCHAR(255), 
    PRIMARY KEY (id), 
    FOREIGN KEY(generated_by) REFERENCES users (id)
);

CREATE INDEX ix_reports_id ON reports (id);

CREATE TABLE activities (
    id SERIAL NOT NULL, 
    user_id INTEGER, 
    contract_id INTEGER, 
    activity VARCHAR(500), 
    PRIMARY KEY (id), 
    FOREIGN KEY(contract_id) REFERENCES contracts (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_activities_id ON activities (id);

CREATE TABLE contract_versions (
    id SERIAL NOT NULL, 
    contract_id INTEGER, 
    version_number INTEGER, 
    file_path VARCHAR(255), 
    uploaded_by INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(contract_id) REFERENCES contracts (id), 
    FOREIGN KEY(uploaded_by) REFERENCES users (id)
);

CREATE INDEX ix_contract_versions_id ON contract_versions (id);

CREATE TABLE notifications (
    id SERIAL NOT NULL, 
    user_id INTEGER, 
    contract_id INTEGER, 
    message VARCHAR(500), 
    notification_type VARCHAR(50), 
    is_read BOOLEAN, 
    PRIMARY KEY (id), 
    FOREIGN KEY(contract_id) REFERENCES contracts (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_notifications_id ON notifications (id);

CREATE TABLE obligations (
    id SERIAL NOT NULL, 
    contract_id INTEGER, 
    title VARCHAR(255), 
    description VARCHAR(500), 
    due_date DATE, 
    priority VARCHAR(20), 
    status VARCHAR(50), 
    assigned_to INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(assigned_to) REFERENCES users (id), 
    FOREIGN KEY(contract_id) REFERENCES contracts (id)
);

CREATE INDEX ix_obligations_id ON obligations (id);

CREATE TABLE renewals (
    id SERIAL NOT NULL, 
    contract_id INTEGER, 
    renewal_date DATE, 
    reminder_days INTEGER, 
    status VARCHAR(50), 
    PRIMARY KEY (id), 
    FOREIGN KEY(contract_id) REFERENCES contracts (id), 
    UNIQUE (contract_id)
);

CREATE INDEX ix_renewals_id ON renewals (id);

UPDATE alembic_version SET version_num='6d48fbdb8a9e' WHERE alembic_version.version_num = 'a86d3f36280f';

-- Running upgrade 6d48fbdb8a9e -> 29d9a70bf213

ALTER TABLE activities DROP CONSTRAINT activities_user_id_fkey;

ALTER TABLE activities ADD FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL;

ALTER TABLE audit_logs DROP CONSTRAINT audit_logs_user_id_fkey;

ALTER TABLE audit_logs ADD FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL;

ALTER TABLE contract_versions DROP CONSTRAINT contract_versions_uploaded_by_fkey;

ALTER TABLE contract_versions ADD FOREIGN KEY(uploaded_by) REFERENCES users (id) ON DELETE SET NULL;

ALTER TABLE contracts ADD COLUMN title VARCHAR(255) NOT NULL;

ALTER TABLE contracts ADD COLUMN category VARCHAR(100) NOT NULL;

ALTER TABLE contracts ADD COLUMN description VARCHAR(500);

ALTER TABLE contracts ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE contracts ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE contracts ALTER COLUMN contract_number SET NOT NULL;

ALTER TABLE contracts ALTER COLUMN start_date SET NOT NULL;

ALTER TABLE contracts ALTER COLUMN end_date SET NOT NULL;

ALTER TABLE contracts ALTER COLUMN status SET NOT NULL;

ALTER TABLE contracts ADD UNIQUE (contract_number);

ALTER TABLE contracts DROP CONSTRAINT contracts_created_by_fkey;

ALTER TABLE contracts ADD FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL;

ALTER TABLE contracts DROP COLUMN vendor_name;

ALTER TABLE contracts DROP COLUMN contract_value;

ALTER TABLE notifications DROP CONSTRAINT notifications_user_id_fkey;

ALTER TABLE notifications ADD FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL;

ALTER TABLE obligations DROP CONSTRAINT obligations_assigned_to_fkey;

ALTER TABLE obligations ADD FOREIGN KEY(assigned_to) REFERENCES users (id) ON DELETE SET NULL;

ALTER TABLE reports DROP CONSTRAINT reports_generated_by_fkey;

ALTER TABLE reports ADD FOREIGN KEY(generated_by) REFERENCES users (id) ON DELETE SET NULL;

ALTER TABLE users ALTER COLUMN password SET NOT NULL;

UPDATE alembic_version SET version_num='29d9a70bf213' WHERE alembic_version.version_num = '6d48fbdb8a9e';

-- Running upgrade 29d9a70bf213 -> 33f88fc04dd8

UPDATE alembic_version SET version_num='33f88fc04dd8' WHERE alembic_version.version_num = '29d9a70bf213';

-- Running upgrade 33f88fc04dd8 -> 4b7c8d1e2f90

ALTER TABLE contracts ADD COLUMN assigned_to INTEGER;

ALTER TABLE contracts ADD COLUMN reviewed_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE contracts ADD COLUMN approved_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE contracts ADD CONSTRAINT contracts_assigned_to_fkey FOREIGN KEY(assigned_to) REFERENCES users (id) ON DELETE SET NULL;

UPDATE alembic_version SET version_num='4b7c8d1e2f90' WHERE alembic_version.version_num = '33f88fc04dd8';

-- Running upgrade 4b7c8d1e2f90 -> cd16da5fa19f

ALTER TABLE obligations ADD COLUMN obligation_type VARCHAR(100) NOT NULL;

ALTER TABLE obligations ADD COLUMN completion_date DATE;

ALTER TABLE obligations ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE obligations ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE obligations ALTER COLUMN contract_id SET NOT NULL;

ALTER TABLE obligations ALTER COLUMN title SET NOT NULL;

ALTER TABLE obligations ALTER COLUMN due_date SET NOT NULL;

ALTER TABLE obligations ALTER COLUMN status SET NOT NULL;

ALTER TABLE obligations DROP CONSTRAINT obligations_contract_id_fkey;

ALTER TABLE obligations ADD FOREIGN KEY(contract_id) REFERENCES contracts (id) ON DELETE CASCADE;

ALTER TABLE obligations DROP COLUMN priority;

UPDATE alembic_version SET version_num='cd16da5fa19f' WHERE alembic_version.version_num = '4b7c8d1e2f90';

-- Running upgrade cd16da5fa19f -> eb05b207e97e

ALTER TABLE renewals ADD COLUMN previous_expiry_date DATE NOT NULL;

ALTER TABLE renewals ADD COLUMN new_expiry_date DATE NOT NULL;

ALTER TABLE renewals ADD COLUMN assigned_to INTEGER;

ALTER TABLE renewals ADD COLUMN notes VARCHAR(500);

ALTER TABLE renewals ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE renewals ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE renewals ALTER COLUMN contract_id SET NOT NULL;

ALTER TABLE renewals ALTER COLUMN renewal_date SET NOT NULL;

ALTER TABLE renewals ALTER COLUMN status SET NOT NULL;

ALTER TABLE renewals DROP CONSTRAINT renewals_contract_id_key;

ALTER TABLE renewals DROP CONSTRAINT renewals_contract_id_fkey;

ALTER TABLE renewals ADD FOREIGN KEY(assigned_to) REFERENCES users (id) ON DELETE SET NULL;

ALTER TABLE renewals ADD FOREIGN KEY(contract_id) REFERENCES contracts (id) ON DELETE CASCADE;

ALTER TABLE renewals DROP COLUMN reminder_days;

UPDATE alembic_version SET version_num='eb05b207e97e' WHERE alembic_version.version_num = 'cd16da5fa19f';

-- Running upgrade eb05b207e97e -> 02402fa124f7

ALTER TABLE notifications ADD COLUMN obligation_id INTEGER;

ALTER TABLE notifications ADD COLUMN title VARCHAR(255) NOT NULL;

ALTER TABLE notifications ADD COLUMN status VARCHAR(20);

ALTER TABLE notifications ADD COLUMN scheduled_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE notifications ADD COLUMN sent_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE notifications ADD COLUMN read_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE notifications ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE notifications ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE notifications ALTER COLUMN notification_type TYPE VARCHAR(100);

ALTER TABLE notifications ALTER COLUMN notification_type SET NOT NULL;

ALTER TABLE notifications ALTER COLUMN message TYPE TEXT;

ALTER TABLE notifications ALTER COLUMN message SET NOT NULL;

ALTER TABLE notifications DROP CONSTRAINT notifications_contract_id_fkey;

ALTER TABLE notifications ADD FOREIGN KEY(contract_id) REFERENCES contracts (id) ON DELETE SET NULL;

ALTER TABLE notifications ADD FOREIGN KEY(obligation_id) REFERENCES obligations (id) ON DELETE SET NULL;

ALTER TABLE notifications DROP COLUMN is_read;

UPDATE alembic_version SET version_num='02402fa124f7' WHERE alembic_version.version_num = 'eb05b207e97e';

-- Running upgrade 02402fa124f7 -> c7f1d6a4b2e8

ALTER TABLE contracts ADD COLUMN department VARCHAR(100);

ALTER TABLE contract_versions ADD COLUMN notes VARCHAR(500);

ALTER TABLE contract_versions ADD COLUMN uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT now();

UPDATE alembic_version SET version_num='c7f1d6a4b2e8' WHERE alembic_version.version_num = '02402fa124f7';

-- Running upgrade c7f1d6a4b2e8 -> d8e2f7b5c3a9

ALTER TABLE obligations ADD COLUMN priority VARCHAR(20);

UPDATE alembic_version SET version_num='d8e2f7b5c3a9' WHERE alembic_version.version_num = 'c7f1d6a4b2e8';

-- Running upgrade d8e2f7b5c3a9 -> e9f3a8c6d1b0

ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);

ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;

ALTER TABLE users ADD COLUMN preferences JSON;

ALTER TABLE users ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE users ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT now();

UPDATE alembic_version SET version_num='e9f3a8c6d1b0' WHERE alembic_version.version_num = 'd8e2f7b5c3a9';

-- Running upgrade e9f3a8c6d1b0 -> f0a4b9d7e2c1

ALTER TABLE activities ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT now();

UPDATE alembic_version SET version_num='f0a4b9d7e2c1' WHERE alembic_version.version_num = 'e9f3a8c6d1b0';

-- Running upgrade 02402fa124f7, f0a4b9d7e2c1 -> f13c2d9e4a67

DROP TABLE contract_versions;

UPDATE alembic_version SET version_num='f13c2d9e4a67' WHERE alembic_version.version_num = 'f0a4b9d7e2c1';

COMMIT;

