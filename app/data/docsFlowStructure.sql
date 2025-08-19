CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    uploaded_by INT,
    department VARCHAR(100),
    upload_date DATETIME
);

CREATE TABLE extracted_tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT,
    page_number INT,
    description VARCHAR(255),
    table_data TEXT, -- JSON string
    FOREIGN KEY (document_id) REFERENCES documents(id)
);