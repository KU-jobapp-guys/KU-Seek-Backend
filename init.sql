CREATE TABLE IF NOT EXISTS users (
id INT NOT NULL AUTO_INCREMENT,
username  VARCHAR(255) NOT NULL,
password  VARCHAR(255) NOT NULL,
user_type VARCHAR(50) NOT NULL,
PRIMARY KEY (id, username)
);

CREATE TABLE IF NOT EXISTS user_google_auth_info (
  user_id INT NOT NULL,
  google_uid VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  picture VARCHAR(255) NOT NULL,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  PRIMARY KEY (google_uid),
  FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS Company (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    company_name VARCHAR(255),
    company_about TEXT,
    company_type VARCHAR(50),
    company_industry VARCHAR(100),
    contact_email VARCHAR(255),
    company_size VARCHAR(50),
    company_website VARCHAR(255),
    location VARCHAR(100),
    full_location VARCHAR(255),
    PRIMARY KEY (id)
);

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