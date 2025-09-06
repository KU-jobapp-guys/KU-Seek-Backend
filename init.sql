CREATE TABLE IF NOT EXISTS Job (
    id INT NOT NULL AUTO_INCREMENT,
    company_id INT,
    description TEXT,
    role VARCHAR(50),
    location VARCHAR(255),
    work_hours VARCHAR(20),
    job_type VARCHAR(40),
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT NOW(),
    approved_by INT,
    PRIMARY KEY (id),
    FOREIGN KEY (company_id) REFERENCES Company(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Skills (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(40),
    job_id INT,
    PRIMARY KEY (id),
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Tags (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(40),
    job_id INT,
    PRIMARY KEY (id),
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS JobApplication (
    id INT NOT NULL AUTO_INCREMENT,
    job_id INT,
    student_id INT,
    resume VARCHAR(500),
    letter_of_application VARCHAR(500),
    additional_document VARCHAR(500),
    phone_number VARCHAR(12),
    status VARCHAR(20) DEFAULT 'pending',
    applied_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Bookmark (
    id INT NOT NULL AUTO_INCREMENT,
    job_id INT,
    student_id INT,
    created_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_job (student_id, job_id)
);