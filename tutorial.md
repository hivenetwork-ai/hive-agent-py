# Detailed Usage of Hive Agent Server Endpoints

After starting the Hive Agent server with `agent.run()`, the following endpoints become available:

## Chat Endpoint

### **POST /api/v1/chat**

This endpoint processes natural language queries and returns responses from the configured OpenAI model. This also supports a reference to a previously uploaded file. This endpoint also has the ability to processes natural language queries with documents.

**Request Body:**

The request body should be sent as multipart/form-data and include the following fields:

* user_id (string): The ID of the user.
* session_id (string): The ID of the session.
* chat_data (string): A JSON string representing the chat messages. The JSON should include an array of message objects, each with a role ('user', 'assistant', etc.) and content.
* files (file): One or more files that the query refers to.

**Response:**

- A streaming response that returns the conversation or information from the agent.

**Usage Example:**

```bash
curl --request POST \
  --url http://localhost:8000/api/v1/chat \
  --header 'Content-Type: multipart/form-data' \
  --form 'user_id="test"' \
  --form 'session_id="test"' \
  --form 'chat_data={ "messages": [ { "role": "user", "content": "What is in these images?" } ] }' \
  --form 'files=@/path/to/your/image1.png' \
  --form 'files=@/path/to/your/image2.png'
```

### **GET /api/v1/chat_history**

This endpoint retrieves the chat history for a specified user and session.

**Query Parameters:**

- `user_id`: The user ID.
- `session_id`: The session ID.

**Response:**

- A JSON array of the chat history.

**Usage Example:**

```bash
curl --request GET \
  --url 'http://localhost:8000/api/v1/chat_history?user_id=user123&session_id=session123'
```

### **GET /api/v1/all_chats**

This endpoint retrieves all chats for a specified user, organized by session ID.

**Query Parameters:**

- `user_id`: The user ID.

**Response:**

- A JSON object where each key is a `session_id` and the value is an array of chat messages for that session.

**Usage Example:**

```bash
curl --request GET \
  --url 'http://localhost:8000/api/v1/all_chats?user_id=user123'
```

## Database Endpoints

Ensure you set the `HIVE_AGENT_DATABASE_URL` environment variable.

### **POST /api/v1/database/create-table**

This endpoint creates a new table in the database.

**Request Body:**

```json
{
  "table_name": "your_table_name",
  "columns": {
    "column1": "type1",
    "column2": "type2"
  }
}
```

**Response:**

- A JSON object indicating the success of the table creation.

**Usage Example:**

```bash
curl --request POST \
  --url http://localhost:8000/api/v1/database/create-table \
  --header 'Content-Type: application/json' \
  --data '{"table_name": "example_table", "columns": {"id": "INTEGER PRIMARY KEY", "name": "TEXT"}}'
```

### **POST /api/v1/database/insert-data**

This endpoint inserts data into a specified table.

**Request Body:**

```json
{
  "table_name": "your_table_name",
  "data": {
    "column1": "value1",
    "column2": "value2"
  }
}
```

**Response:**

- A JSON object indicating the success of the data insertion and the ID of the inserted record.

**Usage Example:**

```bash
curl --request POST \
  --url http://localhost:8000/api/v1/database/insert-data \
  --header 'Content-Type: application/json' \
  --data '{"table_name": "example_table", "data": {"name": "John Doe"}}'
```

### **POST /api/v1/database/read-data**

This endpoint reads data from a specified table based on given filters.

**Request Body:**

```json
{
  "table_name": "your_table_name",
  "filters": {
    "column": "value"
  }
}
```

**Response:**

- A JSON array of the matching records.

**Usage Example:**

```bash
curl --request POST \
  --url http://localhost:8000/api/v1/database/read-data \
  --header 'Content-Type: application/json' \
  --data '{"table_name": "example_table", "filters": {"name": "John Doe"}}'
```

### **PUT /api/v1/database/update-data**

This endpoint updates data in a specified table.

**Request Body:**

```json
{
  "table_name": "your_table_name",
  "id": "record_id",
  "data": {
    "column": "new_value"
  }
}
```

**Response:**

- A JSON object indicating the success of the data update.

**Usage Example:**

```bash
curl --request PUT \
  --url http://localhost:8000/api/v1/database/update-data \
  --header 'Content-Type: application/json' \
  --data '{"table_name": "example_table", "id": 1, "data": {"name": "Jane Doe"}}'
```

### **DELETE /api/v1/database/delete-data**

This endpoint deletes data from a specified table.

**Request Body:**

```json
{
  "table_name": "your_table_name",
  "id": "record_id"
}
```

**Response:**

- A JSON object indicating the success of the data deletion.

**Usage Example:**

```bash
curl --request DELETE \
  --url http://localhost:8000/api/v1/database/delete-data \
  --header 'Content-Type: application/json' \
  --data '{"table_name": "example_table", "id": 1}'
```

These endpoints provide the foundation for interacting with the Hive Agent, allowing for both real-time and persistent data handling, as well as dynamic interaction via chat and database operations.

## File Management Endpoints

### **POST /api/v1/uploadfiles/**

This endpoint allows you to upload one or more files to the server.

**Request:**

- Multipart form data containing files.

**Response:**

- A JSON object with the names of the uploaded files.

**Usage Example:**

```bash
curl --request POST \
  --url http://localhost:8000/api/v1/uploadfiles/ \
  --header 'Content-Type: multipart/form-data' \
  --form 'files=@path/to/your/file1.txt' \
  --form 'files=@path/to/your/file2.txt'
```

### **GET /api/v1/files/**

This endpoint lists all files stored on the server.

**Response:**

- A JSON object containing a list of file names.

**Usage Example:**

```bash
curl --request GET \
  --url http://localhost:8000/api/v1/files/
```

### **PUT /api/v1/files/{old_filename}/{new_filename}**

This endpoint renames a specified file on the server.

**URL Parameters:**

- old_filename: The current name of the file.
- new_filename: The new name for the file.

**Response:**

- A JSON object indicating the success of the file renaming.

**Usage Example:**

```bash
curl --request PUT \
  --url http://localhost:8000/api/v1/files/old_name.txt/new_name.txt
```

### **DELETE /api/v1/files/{filename}**

This endpoint deletes a specified file from the server.

**URL Parameters:**

- filename: The name of the file to be deleted.

**Response:**

- A JSON object indicating the success of the file deletion.

**Usage Example:**

```bash
curl --request DELETE \
  --url http://localhost:8000/api/v1/files/test_delete.txt
```

## Index Endpoints

### **POST /api/v1/create_index/?{index_name}&{index_type}'**

This endpoint create an index

**URL Parameters:**

- index_name: The name of the index.
- index_type: You can choose one of them 'basic', 'chroma', 'pinecone-serverless', 'pinecone-pod'

**Request Body:**

```json
[
  "hive-agent-data/files/user/{yourfilename1}",
  "hive-agent-data/files/user/{yourfilename2}"
]
```

**Response:**

- A JSON object indicating the success of the index creation.

**Usage Example:**

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/v1/create_index/?index_name=test&index_type=chroma' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  "hive-agent-data/files/user/pdf-sample.pdf"
]'
```

### **POST /api/v1/insert_documents/?{index_name}**

This endpoint inserts documents into an existing index.

**URL Parameters:**

- index_name: The name of the index to insert documents into.

**Request Body:**

```json
[
  "hive-agent-data/files/user/{yourfilename1}",
  "hive-agent-data/files/user/{yourfilename2}"
]
```

**Response:**

- A JSON object indicating the success of the document insertion.

**Usage Example:**

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/v1/insert_documents/?index_name=test' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  "hive-agent-data/files/user/uniswap-protocol.md"
]'
```

### **PUT /api/v1/update_documents/?{index_name}**

This endpoint updates documents in an existing index.

**URL Parameters:**

- index_name: The name of the index to update documents in.

**Request Body:**

```json
[
  "hive-agent-data/files/user/{yourfilename1}",
  "hive-agent-data/files/user/{yourfilename2}"
]
```

**Response:**

- A JSON object indicating the success of the document update.

**Usage Example:**

```bash
curl -X 'PUT' \
  'http://0.0.0.0:8000/api/v1/update_documents/?index_name=test' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  "hive-agent-data/files/user/uniswap-protocol.md"
]'
```

### **DELETE /api/v1/delete_documents/?{index_name}**

This endpoint deletes documents from an existing index.

**URL Parameters:**

- index_name: The name of the index to delete documents from.

**Request Body:**

```json
[
  "hive-agent-data/files/user/{yourfilename1}",
  "hive-agent-data/files/user/{yourfilename2}"
]
```

**Response:**

- A JSON object indicating the success of the document deletion.

**Usage Example:**

```bash
curl -X 'DELETE' \
  'http://0.0.0.0:8000/api/v1/delete_documents/?index_name=test' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  "hive-agent-data/files/user/pdf-sample.pdf"
]'
```


## Tools Endpoints

### **POST /api/v1/install_tools**

This endpoint installs tools into the agent by sending a list of tools with their GitHub URLs, function paths, and an optional GitHub token for private repositories.

**Request Body:**

```json
{
  "tools": [
    {
      "github_url": "https://github.com/example/tool1",
      "functions": [
        "module1.function1",
        "module2.function2"
      ],
      "install_path": "/app/tools/tool1/",
      "github_token": "your_private_repo_token"
    },
    {
      "github_url": "https://github.com/example/tool2",
      "functions": [
        "module1.functionA"
      ],
      "install_path": "/app/tools/tool2/"
    },
    {
      "github_url": "https://github.com/example/tool3",
      "functions": [
        "module1.functionA"
      ],
      "install_path": "/app/tools/tool3/",
      "env_vars": {
        "EXAMPLE_API_KEY": "api-key-123"
      }
    }
  ]
}
```

**Request Parameters:**

- **github_url**: The GitHub URL of the tool repository.
- **functions**: A list of functions (in `module.function` format) to be installed from the tool.
- **install_path** (optional): The installation path on the server. Defaults to `/tmp` if not provided.
- **github_token** (optional): A token for accessing private GitHub repositories.
- **env_vars** (optional): The environment variables required for the tool to run.

**Response:**

- A JSON object indicating whether the tools were installed successfully.

**Usage Example:**

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/api/v1/install_tools' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "tools": [
    {
      "github_url": "https://github.com/example/tool1",
      "functions": ["module1.function1", "module2.function2"],
      "install_path": "/app/tools/tool1/",
      "github_token": "your_private_repo_token"
    },
    {
      "github_url": "https://github.com/example/tool2",
      "functions": ["module1.functionA"],
      "install_path": "/app/tools/tool2/"
    },
    {
      "github_url": "https://github.com/example/tool3",
      "functions": [
        "module1.functionA"
      ],
      "install_path": "/app/tools/tool3/",
      "env_vars": {
        "EXAMPLE_API_KEY": "api-key-123"
      }
    }
  ]
}'
```
