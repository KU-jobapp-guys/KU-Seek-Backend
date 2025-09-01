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