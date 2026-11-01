CREATE DATABASE IF NOT EXISTS people_append_only
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE people_append_only;

-- A complete snapshot per version. Existing rows never change.
CREATE TABLE IF NOT EXISTS person_events (
  person_id CHAR(36) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  version INT UNSIGNED NOT NULL,
  operation ENUM('created', 'updated', 'deleted') NOT NULL,
  full_name VARCHAR(150) NOT NULL,
  dob DATE NOT NULL,
  recorded_at TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (person_id, version),
  CONSTRAINT valid_version CHECK (
    (version = 1 AND operation = 'created') OR
    (version > 1 AND operation IN ('updated', 'deleted'))
  )
) ENGINE=InnoDB;
