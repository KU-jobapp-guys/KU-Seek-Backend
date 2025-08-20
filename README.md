## Generating the Swagger Server
If the `swagger server` does not exist, you must generate one by using [Swagger Codegen](https://editor.swagger.io/) or [openapi-generator-cli](https://www.npmjs.com/package/@openapitools/openapi-generator-cli).

When using openapi-generator-cli use the follwing command to generate the server
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
```

## Running the backend (API service)
1. docker compose up -d db
or to run manually (ensure your database is running)
1. create a virtual env. <br>```python -m venv env```
2. Activate the virtual environment.<br>
    ```
    # on Mac/Linux use
    .env/bin/activate
    
    # on Windows use
    .\env\scripts\activate
    ```
3. Run the backend using:<br>
   ```python app.py```