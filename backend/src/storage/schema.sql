-- ================================
-- 1. Users Table
-- Tracks internal users interacting with the system.
-- Includes role, contact info, and audit timestamps.
-- ================================
CREATE TABLE users (
    user_id        VARCHAR(50) PRIMARY KEY,
    name           VARCHAR(100),
    email          VARCHAR(100) UNIQUE,
    role           VARCHAR(50), -- Finance / IT / Admin / MSP
    created_at     TIMESTAMP DEFAULT NOW(),
    updated_at     TIMESTAMP DEFAULT NOW()
);

-- ================================
-- 2. Accounts Table
-- Represents customer accounts or cloud/SaaS products.
-- Supports multiple product types (AWS, GCP, Zoom, Slack, etc.)
-- ================================
CREATE TABLE accounts (
    account_id      VARCHAR(50) PRIMARY KEY,
    account_name    VARCHAR(100),
    product_type    VARCHAR(50), -- AWS, GCP, Azure, Zoom, Slack, etc.
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ================================
-- 3. Services Table
-- Defines services/resources associated with accounts.
-- Allows multi-product support with product_type column.
-- ================================
CREATE TABLE services (
    service_id      SERIAL PRIMARY KEY,
    product_type    VARCHAR(50), -- e.g., EC2, S3, Zoom Meetings
    service_name    VARCHAR(100),
    description     TEXT,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ================================
-- 4. Daily Usage Table
-- Stores daily aggregated usage and cost metrics per account/service.
-- Includes anomaly flags and resource metadata for analysis.
-- ================================
CREATE TABLE daily_usage (
    id                  SERIAL PRIMARY KEY,
    account_id          VARCHAR(50) REFERENCES accounts(account_id),
    service_id          INT REFERENCES services(service_id),
    usage_date          DATE NOT NULL,
    usage_quantity      NUMERIC(20,4),
    cost                NUMERIC(20,4),
    currency            VARCHAR(10) DEFAULT 'USD',
    region              VARCHAR(50),
    resource_id         VARCHAR(100),
    tags                JSONB,
    billing_period      VARCHAR(20),
    anomaly_flag        BOOLEAN DEFAULT FALSE,
    anomaly_score       NUMERIC(5,2),
    ingestion_timestamp TIMESTAMP DEFAULT NOW(),
    last_updated        TIMESTAMP DEFAULT NOW(),
    UNIQUE(account_id, service_id, usage_date)
);

-- ================================
-- 5. Recommendations Table
-- Stores AI-generated cost optimization or resource recommendations.
-- Tracks ROI, confidence, and status of each recommendation.
-- ================================
CREATE TABLE recommendations (
    id                  SERIAL PRIMARY KEY,
    daily_usage_id      INT REFERENCES daily_usage(id),
    recommendation_text TEXT,
    action_type         VARCHAR(50), -- Terminate / Downgrade / Consolidate / Ignore
    roi_estimate        NUMERIC(20,4),
    confidence_score    NUMERIC(5,2),
    status              VARCHAR(20) DEFAULT 'Pending', -- Pending / Applied / Rejected
    created_at          TIMESTAMP DEFAULT NOW(),
    applied_at          TIMESTAMP
);

-- ================================
-- 6. Usage Anomalies Table
-- Tracks anomalies detected in daily usage data.
-- Includes severity, predicted savings, and linked recommendation.
-- ================================
CREATE TABLE usage_anomalies (
    id                  SERIAL PRIMARY KEY,
    daily_usage_id      INT REFERENCES daily_usage(id),
    anomaly_type        VARCHAR(50),
    description         TEXT,
    severity            VARCHAR(10), -- Low / Medium / High
    predicted_savings   NUMERIC(20,4),
    recommendation_id   INT REFERENCES recommendations(id),
    context_snapshot    JSONB,
    status              VARCHAR(20) DEFAULT 'New', -- New / Acknowledged / Resolved
    detected_at         TIMESTAMP DEFAULT NOW()
);

-- ================================
-- 7. User Feedback Table
-- Captures feedback on AI recommendations from internal users.
-- Tracks actions taken, actual savings, and notes for continuous improvement.
-- ================================
CREATE TABLE user_feedback (
    id                  SERIAL PRIMARY KEY,
    recommendation_id   INT REFERENCES recommendations(id),
    user_id             VARCHAR(50) REFERENCES users(user_id),
    action_taken        VARCHAR(20), -- Accept / Reject / Simulate
    actual_savings      NUMERIC(20,4),
    feedback_timestamp  TIMESTAMP DEFAULT NOW(),
    notes               TEXT
);

