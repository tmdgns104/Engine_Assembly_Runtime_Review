CREATE TABLE calibrations (calibration_id TEXT PRIMARY KEY, package_sha256 TEXT NOT NULL,
 station_id TEXT NOT NULL, payload_json TEXT NOT NULL, confirmed_at TEXT NOT NULL);

CREATE TABLE cycles (
 cell_id TEXT NOT NULL CHECK(length(trim(cell_id))>0),
 plc_session_id INTEGER NOT NULL CHECK(plc_session_id BETWEEN 1 AND 4294967295),
 cycle_id INTEGER NOT NULL CHECK(cycle_id BETWEEN 1 AND 4294967295),
 started_at TEXT NOT NULL, terminal TEXT,
 PRIMARY KEY(cell_id,plc_session_id,cycle_id));

CREATE TABLE defects (defect_id TEXT PRIMARY KEY, inspection_id TEXT NOT NULL REFERENCES inspections,
 code TEXT NOT NULL, slot TEXT, payload_json TEXT NOT NULL);

CREATE TABLE dispositions (disposition_id TEXT PRIMARY KEY, inspection_id TEXT NOT NULL REFERENCES inspections,
 disposition TEXT NOT NULL CHECK(disposition IN ('PENDING','RELEASED','QUARANTINED','REMOVED','ABORTED')),
 actor TEXT NOT NULL, reason TEXT NOT NULL, occurred_at TEXT NOT NULL);

CREATE TABLE events (event_id TEXT PRIMARY KEY, producer_id TEXT NOT NULL, producer_session TEXT NOT NULL,
 producer_seq INTEGER NOT NULL, occurred_at TEXT NOT NULL, received_at TEXT NOT NULL,
 event_type TEXT NOT NULL, payload_json TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
 UNIQUE(producer_id,producer_session,producer_seq));

CREATE TABLE frame_assets (asset_id TEXT PRIMARY KEY, inspection_id TEXT NOT NULL REFERENCES inspections,
 kind TEXT NOT NULL, relative_path TEXT NOT NULL UNIQUE, sha256 TEXT NOT NULL, width INTEGER NOT NULL CHECK(width>0),
 height INTEGER NOT NULL CHECK(height>0), bytes INTEGER NOT NULL CHECK(bytes>0), capture_at TEXT, view TEXT NOT NULL,
 sync_state TEXT NOT NULL DEFAULT 'PENDING');

CREATE TABLE inspections (
 inspection_id TEXT PRIMARY KEY, cell_id TEXT NOT NULL, plc_session_id INTEGER NOT NULL,
 request_id INTEGER NOT NULL CHECK(request_id BETWEEN 1 AND 4294967295), cycle_id INTEGER NOT NULL,
 attempt INTEGER NOT NULL CHECK(attempt>=1), fingerprint TEXT NOT NULL, request_json TEXT NOT NULL,
 package_json TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('ACCEPTED','COMPLETE','CANCELLED')),
 decision TEXT CHECK(decision IN ('PASS','FAIL','REVIEW','ERROR')), result_json TEXT,
 accepted_at TEXT NOT NULL, completed_at TEXT,
 UNIQUE(cell_id,plc_session_id,request_id),
 FOREIGN KEY(cell_id,plc_session_id,cycle_id) REFERENCES cycles(cell_id,plc_session_id,cycle_id));

CREATE TABLE outbox (event_id TEXT PRIMARY KEY REFERENCES events, state TEXT NOT NULL DEFAULT 'PENDING',
 attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT, acknowledged_at TEXT);

CREATE TABLE quarantine (quarantine_id TEXT PRIMARY KEY, event_id TEXT, reason TEXT NOT NULL,
 payload_json TEXT NOT NULL, received_at TEXT NOT NULL);

CREATE TABLE service_state (key TEXT PRIMARY KEY, value TEXT NOT NULL);