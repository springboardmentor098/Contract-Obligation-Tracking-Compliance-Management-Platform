-- ============================================================
-- ContractIQ
-- Sprint 3 - Database Design
-- Contract Obligation Tracking & Compliance Management Platform
-- ============================================================


-- ============================================================
-- 1. USERS
-- ============================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. CONTRACTS
-- ============================================================

CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    contract_number VARCHAR(100) UNIQUE,
    description TEXT,
    party_name VARCHAR(255),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50),
    owner_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_contract_owner
        FOREIGN KEY (owner_id)
        REFERENCES users(id)
);


-- ============================================================
-- 3. CONTRACT VERSIONS
-- ============================================================

CREATE TABLE contract_versions (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    document_path VARCHAR(500),
    change_summary TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_version_contract
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id),

    CONSTRAINT fk_version_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(id)
);


-- ============================================================
-- 4. OBLIGATIONS
-- ============================================================

CREATE TABLE obligations (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(50),
    priority VARCHAR(50),
    assigned_to INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_obligation_contract
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id),

    CONSTRAINT fk_obligation_assigned_to
        FOREIGN KEY (assigned_to)
        REFERENCES users(id)
);


-- ============================================================
-- 5. RENEWALS
-- ============================================================

CREATE TABLE renewals (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    renewal_date DATE,
    status VARCHAR(50),
    renewal_period INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_renewal_contract
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id)
);


-- ============================================================
-- 6. NOTIFICATIONS
-- ============================================================

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    contract_id INTEGER,
    title VARCHAR(255),
    message TEXT,
    notification_type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notification_user
        FOREIGN KEY (user_id)
        REFERENCES users(id),

    CONSTRAINT fk_notification_contract
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id)
);


-- ============================================================
-- 7. REPORTS
-- ============================================================

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    generated_by INTEGER NOT NULL,
    report_type VARCHAR(100),
    report_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_report_contract
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id),

    CONSTRAINT fk_report_generated_by
        FOREIGN KEY (generated_by)
        REFERENCES users(id)
);


-- ============================================================
-- 8. AUDIT LOGS
-- ============================================================

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    contract_id INTEGER,
    action VARCHAR(100),
    entity_type VARCHAR(100),
    entity_id INTEGER,
    old_value JSON,
    new_value JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id)
        REFERENCES users(id),

    CONSTRAINT fk_audit_contract
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id)
);


-- ============================================================
-- 9. ACTIVITIES
-- ============================================================

CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    contract_id INTEGER,
    activity_type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_activity_user
        FOREIGN KEY (user_id)
        REFERENCES users(id),

    CONSTRAINT fk_activity_contract
        FOREIGN KEY (contract_id)
        REFERENCES contracts(id)
);