## Project Overview
This is the backend API service for **KU-Seek**, a job-seeking platform for KU Computer Engineering students.  


## Requirements
- Python 3.11+
- MySQL 8.0+
- Docker & Docker Compose (optional, for local DB)
- Node.js (for generating the Swagger server)


## Generating the Swagger Server
If the `swagger server` does not exist, you must generate one by using [Swagger Codegen](https://editor.swagger.io/) or [openapi-generator-cli](https://www.npmjs.com/package/@openapitools/openapi-generator-cli).

When using openapi-generator-cli use the following command to generate the server
```
openapi-generator-cli generate -i openapi/ku-seek-api.yml -g python-flask -o swagger_server
```

## Setting up the environment file
You will need a MySQL database for this application, to setup the credentials in `.env` include:
```
OPENAPI_STUB_DIR = "swagger_server"
DB_USER     = {your database user}
DB_PASSWORD = {your user password}
DB_HOST     = {database host IP}
DB_PORT     = {port of the database} # must be int
DB_NAME     = {your database}
ALLOWED_ORIGINS =  {the frontend host or http://localhost:5173 for default configuration}
CLIENT_SECRETS_FILE = {the file path to your client secrets}
CLIENT_ID = {Your google cloud console client ID}
SECRET_KEY = {A secure secret key for JWT signing - see below}
```

## Generating a Secure SECRET_KEY

**DO NOT use a random text string for production!** The SECRET_KEY is used for signing JWTs and should be cryptographically secure.

**For Development:**
## Generate a secure random key using Python
```
python -c "import secrets; print(secrets.token_hex(32))"
```

## Running the backend (API service)
1. docker compose up -d db
or to run manually (ensure your database is running)
1. create a virtual env. <br>```python -m venv env```
2. Activate the virtual environment.<br>
    ```
    # on Mac/Linux use
    source env/bin/activate
    
    # on Windows use
    .\env\scripts\activate
    ```
3. Create the MySQL table by using<br>
    ```alembic upgrade head```

4. Run the backend using:<br>
   ```python app.py```

## Running Tests
To run the unit tests, execute:
```python -m unittest discover tests```
