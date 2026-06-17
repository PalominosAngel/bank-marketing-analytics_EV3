CREATE TABLE IF NOT EXISTS contact_channel_reference (
    contact VARCHAR(30) PRIMARY KEY,
    channel_label VARCHAR(80) NOT NULL,
    channel_group VARCHAR(40) NOT NULL,
    priority_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS etl_runs (
    run_id VARCHAR(50) PRIMARY KEY,
    started_at VARCHAR(40) NOT NULL,
    finished_at VARCHAR(40),
    status VARCHAR(20) NOT NULL,
    rows_extracted INTEGER DEFAULT 0,
    rows_loaded INTEGER DEFAULT 0,
    api_source_status VARCHAR(40),
    error_message TEXT
);
