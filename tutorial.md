# Detailed Usage of Hive Agent Server Endpoints

After starting the Hive Agent server with `agent.run()`, the following endpoints become available:

## Chat Endpoint

### **POST /api/v1/chat**

This endpoint processes natural language queries and returns responses from the configured OpenAI model.

**Request Body:**

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Your query here"
    }
  ]
}
```

**Response:**
- A streaming response that returns the conversation or information from the agent.

**Usage Example:**

```bash
curl --request POST \
  --url http://localhost:8000/api/v1/chat \
  --header 'Content-Type: application/json' \
  --data '{"messages": [{"role": "user", "content": "What is the capital of France?"}]}'
```

## Database Endpoints

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
