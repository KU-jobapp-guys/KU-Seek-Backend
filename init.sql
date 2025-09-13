CREATE TABLE IF NOT EXISTS User (
    id INT NOT NULL AUTO_INCREMENT,
    google_uid VARCHAR(100),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS Profile (
    user_id INT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    about TEXT,
    location VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    contact_email VARCHAR(255),
    gender VARCHAR(1),
    age INT,
    user_type VARCHAR(20) COMMENT 'student, company, professor, admin',
    profile_img VARCHAR(100),
    banner_img VARCHAR(100),
    phone_number VARCHAR(20),
    is_verified BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Education (
    id INT NOT NULL AUTO_INCREMENT,
    curriculum_name VARCHAR(255),
    university VARCHAR(255),
    major VARCHAR(100),
    year_of_study DATE,
    graduate_year DATE,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS Student (
    user_id INT NOT NULL,
    nisit_id VARCHAR(10) UNIQUE,
    education INT,
    gpa DECIMAL(3,2),
    interests TEXT,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (education) REFERENCES Education(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Professor (
    user_id INT NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    office_location VARCHAR(255),
    research_interests TEXT,
    description TEXT,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Company (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    company_name VARCHAR(255),
    company_type VARCHAR(50),
    company_industry VARCHAR(100),
    company_size VARCHAR(50),
    company_website VARCHAR(255),
    full_location VARCHAR(255),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Job (
    id INT NOT NULL AUTO_INCREMENT,
    company_id INT,
    description TEXT,
    title VARCHAR(50),
    salary_min FLOAT,
    salary_max FLOAT,
    location VARCHAR(255),
    work_hours VARCHAR(20),
    job_type VARCHAR(40),
    job_level VARCHAR(40),
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, approved, rejected',
    visibility BOOLEAN,
    capacity INT,
    end_date DATETIME,
    created_at DATETIME DEFAULT NOW(),
    approved_by INT,
    PRIMARY KEY (id),
    FOREIGN KEY (company_id) REFERENCES Company(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES User(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Terms (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(40),
    type VARCHAR(40),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS Tags (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(40),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS Job_skills (
    job_id INT,
    skill_id INT,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES Terms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Profile_skills (
    user_id INT,
    skill_id INT,
    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES Terms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Job_Tag (
    job_id INT,
    tag_id INT,
    PRIMARY KEY (job_id, tag_id),
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES Tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS JobApplication (
    id INT NOT NULL AUTO_INCREMENT,
    job_id INT,
    student_id INT,
    resume VARCHAR(500),
    letter_of_application VARCHAR(500),
    additional_document VARCHAR(500),
    phone_number VARCHAR(12),
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, reviewed, accepted, rejected',
    applied_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Bookmark (
    id INT NOT NULL AUTO_INCREMENT,
    job_id INT,
    student_id INT,
    created_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES User(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_job (student_id, job_id)
);

CREATE TABLE IF NOT EXISTS StudentDocument (
    id INT NOT NULL AUTO_INCREMENT,
    student_id INT,
    file_path VARCHAR(500),
    original_filename VARCHAR(255),
    uploaded_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY (student_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS StudentHistory (
    job_id INT,
    student_id INT,
    viewed_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (job_id, student_id),
    FOREIGN KEY (job_id) REFERENCES Job(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ProfessorConnection (
    id INT NOT NULL AUTO_INCREMENT,
    professor_id INT,
    company_id INT,
    created_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY (professor_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Announcement (
    id INT NOT NULL AUTO_INCREMENT,
    professor_id INT,
    title VARCHAR(255),
    content TEXT,
    created_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY (professor_id) REFERENCES User(id) ON DELETE CASCADE
);