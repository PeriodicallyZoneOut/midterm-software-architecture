USE hello;

CREATE TABLE IF NOT EXISTS greetings (
    id TINYINT UNSIGNED PRIMARY KEY,
    message VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO greetings (id, message) VALUES (1, 'Hello world!');

-- The runtime service can read its table but cannot change the greeting or schema.
REVOKE ALL PRIVILEGES ON hello.* FROM 'hello'@'%';
GRANT SELECT ON hello.greetings TO 'hello'@'%';
