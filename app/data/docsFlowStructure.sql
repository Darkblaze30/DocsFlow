CREATE DATABASE docsflow;

use docsflow;

CREATE TABLE IF NOT EXISTS `departments` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_departments_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(150) NOT NULL,
  `email` VARCHAR(200) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `rol` ENUM('user','admin') NOT NULL DEFAULT 'user',
  `department_id` INT NULL,
  `failed_attempts` INT NOT NULL DEFAULT 0,
  `locked_until` DATETIME NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_email` (`email`),
  INDEX `idx_users_email` (`email`),
  CONSTRAINT `fk_users_departments` FOREIGN KEY (`department_id`)
    REFERENCES `departments` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    uploaded_by INT,
    department INT,
    upload_date DATETIME
);

CREATE TABLE IF NOT EXISTS extracted_tables (
      id INT AUTO_INCREMENT PRIMARY KEY,
      document_id INT,
      page_number INT,
      description VARCHAR(255),
      table_data TEXT, -- JSON string
      FOREIGN KEY (document_id) REFERENCES documents(id)
    );

CREATE TABLE IF NOT EXISTS password_resets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        token_hash VARCHAR(255) NOT NULL UNIQUE,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

-- Departamentos
INSERT INTO departments (name) VALUES
  ('Recursos Humanos'),
  ('Finanzas'),
  ('Tecnología'),
  ('Legal'),
  ('Marketing');

-- Usuarios
INSERT INTO users (name, email, password, rol, department_id, failed_attempts, locked_until) VALUES
  ('Ana Torres', 'ana@empresa.com', 'hashed_pw_ana', 'admin', 3, 0, NULL),
  ('Carlos Ruiz', 'carlos@empresa.com', 'hashed_pw_carlos', 'user', 1, 2, '2025-08-19 10:00:00'),
  ('Laura Gómez', 'laura@empresa.com', 'hashed_pw_laura', 'user', 2, 0, NULL),
  ('Diego Martínez', 'diego@empresa.com', 'hashed_pw_diego', 'admin', 4, 1, NULL),
  ('Sofía López', 'sofia@empresa.com', 'hashed_pw_sofia', 'user', NULL, 0, NULL);

-- Documentos
INSERT INTO documents (filename, uploaded_by, department, upload_date) VALUES
  ('contrato_rrhh.pdf', 2, 1, '2025-08-18 09:30:00'),
  ('balance_financiero.xlsx', 3, 2, '2025-08-17 14:20:00'),
  ('manual_tecnico.docx', 1, 3, '2025-08-16 11:45:00'),
  ('politicas_legales.pdf', 4, 4, '2025-08-15 16:00:00');

-- Tablas extraídas
INSERT INTO extracted_tables (document_id, page_number, description, table_data) VALUES
  (1, 5, 'Costos directos por sector y año',
   '[["Año", "Agrícola y Forestal", "Pecuario y Pesquero", "Comercialización", "Total Costos Directos"], ["2023", "$120,000", "$80,000", "$50,000", "$250,000"], ["2024", "$130,000", "$82,000", "$53,000", "$265,000"], ["2025", "$140,000", "$85,000", "$55,000", "$280,000"]]'),
  (2, 3, 'Inventario de equipos tecnológicos',
   '[["Equipo", "Cantidad", "Estado"], ["Laptop", "25", "Operativo"], ["Proyector", "4", "En reparación"], ["Router", "10", "Operativo"]]'),
  (3, 2, 'Ventas por trimestre',
   '[["Trimestre", "Producto A", "Producto B", "Total"], ["Q1", "$12,000", "$8,000", "$20,000"], ["Q2", "$15,000", "$9,500", "$24,500"], ["Q3", "$13,500", "$10,000", "$23,500"]]'),
  (4, 7, 'Resultados de análisis clínicos',
   '[["Paciente", "Glucosa", "Colesterol", "Fecha"], ["Juan Pérez", "95 mg/dL", "180 mg/dL", "2025-08-01"], ["Ana Gómez", "88 mg/dL", "170 mg/dL", "2025-08-02"]]'),
  (1, 4, 'Asistencia mensual por departamento',
   '[["Departamento", "Julio", "Agosto", "Septiembre"], ["Recursos Humanos", "95%", "97%", "96%"], ["Tecnología", "92%", "90%", "93%"], ["Marketing", "88%", "85%", "87%"]]');

INSERT INTO users 
    (name, email, password, rol, department_id, failed_attempts, locked_until, created_at)
VALUES
    ('Jonathan Romero', 'ola@s.com', '$2b$12$xP1hwHIgfgB9dFA.u518p.yeYofCYqxpGcj44akSFouVovhRLyVUe', 'admin', 1, 0, NULL, NOW());
    