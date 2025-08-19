import enum

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"

TABLE_DEPARTMENTS = "departments"
TABLE_USERS = "users"

DEPT_COL_ID = "id"
DEPT_COL_NAME = "name"

USER_COL_ID = "id"
USER_COL_NAME = "name"
USER_COL_EMAIL = "email"
USER_COL_PASSWORD = "password"
USER_COL_ROL = "rol"
USER_COL_DEPARTMENT_ID = "department_id"
USER_COL_FAILED_ATTEMPTS = "failed_attempts"
USER_COL_LOCKED_UNTIL = "locked_until"
USER_COL_CREATED_AT = "created_at"

def get_create_table_statements() -> list:
    stmts = []

    stmts.append(f"""
    CREATE TABLE IF NOT EXISTS `{TABLE_DEPARTMENTS}` (
      `{DEPT_COL_ID}` INT NOT NULL AUTO_INCREMENT,
      `{DEPT_COL_NAME}` VARCHAR(150) NOT NULL,
      PRIMARY KEY (`{DEPT_COL_ID}`),
      UNIQUE KEY `uq_{TABLE_DEPARTMENTS}_{DEPT_COL_NAME}` (`{DEPT_COL_NAME}`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """.strip())

    stmts.append(f"""
    CREATE TABLE IF NOT EXISTS `{TABLE_USERS}` (
      `{USER_COL_ID}` BIGINT NOT NULL AUTO_INCREMENT,
      `{USER_COL_NAME}` VARCHAR(150) NOT NULL,
      `{USER_COL_EMAIL}` VARCHAR(200) NOT NULL,
      `{USER_COL_PASSWORD}` VARCHAR(255) NOT NULL,
      `{USER_COL_ROL}` ENUM('user','admin') NOT NULL DEFAULT 'user',
      `{USER_COL_DEPARTMENT_ID}` INT NULL,
      `{USER_COL_FAILED_ATTEMPTS}` INT NOT NULL DEFAULT 0,
      `{USER_COL_LOCKED_UNTIL}` DATETIME NULL,
      `{USER_COL_CREATED_AT}` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (`{USER_COL_ID}`),
      UNIQUE KEY `uq_{TABLE_USERS}_{USER_COL_EMAIL}` (`{USER_COL_EMAIL}`),
      INDEX `idx_{TABLE_USERS}_{USER_COL_EMAIL}` (`{USER_COL_EMAIL}`),
      CONSTRAINT `fk_{TABLE_USERS}_{TABLE_DEPARTMENTS}` FOREIGN KEY (`{USER_COL_DEPARTMENT_ID}`)
        REFERENCES `{TABLE_DEPARTMENTS}` (`{DEPT_COL_ID}`) ON DELETE SET NULL ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """.strip())

    stmts.append(f"""
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    uploaded_by INT,
    department INT,
    upload_date DATETIME
);

""")
    
    stmts.append(f"""
    CREATE TABLE IF NOT EXISTS extracted_tables (
      id INT AUTO_INCREMENT PRIMARY KEY,
      document_id INT,
      page_number INT,
      description VARCHAR(255),
      table_data TEXT, -- JSON string
      FOREIGN KEY (document_id) REFERENCES documents(id)
    );
""")
    
    stmts.append(f"""
    CREATE TABLE IF NOT EXISTS password_resets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        token_hash VARCHAR(255) NOT NULL UNIQUE,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
""")
    return stmts
