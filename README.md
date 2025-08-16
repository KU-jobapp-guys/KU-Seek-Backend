## Generating the Swagger Server
If the `swagger server` does not exist, you must generate one by using [Swagger Codegen](https://editor.swagger.io/) or [openapi-generator-cli](https://www.npmjs.com/package/@openapitools/openapi-generator-cli).

When using openapi-generator-cli use the follwing command to generate the server
```
openapi-generator-cli generate -i openapi/ku-seek-api.yml -g python-flask -o swagger_server
```

## Running the backend (API service)
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