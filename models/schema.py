TABLES = {
    "users": '''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            password TEXT,
            role VARCHAR(50),
            full_name VARCHAR(255),
            grade VARCHAR(50),
            section VARCHAR(50),
            voted TINYINT(1) DEFAULT 0,
            session_token VARCHAR(255),
            last_active DATETIME
        ) ENGINE=InnoDB;
    ''',
    "candidates": '''
        CREATE TABLE IF NOT EXISTS candidates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            position VARCHAR(255),
            grade VARCHAR(50),
            votes INT DEFAULT 0,
            image LONGBLOB
        ) ENGINE=InnoDB;
    ''',
    "votes": '''
        CREATE TABLE IF NOT EXISTS votes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            voter_id INT,
            candidate_id INT,
            position VARCHAR(255),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
    ''',
    "audit_trail": '''
        CREATE TABLE IF NOT EXISTS audit_trail (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user VARCHAR(255),
            module VARCHAR(100),
            action VARCHAR(255),
            description TEXT
        ) ENGINE=InnoDB;
    ''',
    "system_config": '''
        CREATE TABLE IF NOT EXISTS system_config (
            `key` VARCHAR(100) PRIMARY KEY,
            value TEXT
        ) ENGINE=InnoDB;
    ''',
    "deleted_users": '''
        CREATE TABLE IF NOT EXISTS deleted_users (
            id INT, username VARCHAR(255), full_name VARCHAR(255), role VARCHAR(50), 
            grade VARCHAR(50), section VARCHAR(50), deleted_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
    ''',
    "deleted_candidates": '''
        CREATE TABLE IF NOT EXISTS deleted_candidates (
            id INT, name VARCHAR(255), position VARCHAR(255), grade VARCHAR(50), 
            image LONGBLOB, deleted_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
    '''
}