# Detailed Usage of Hive Agent Server Endpoints

After starting the Hive Agent server with `agent.run()`, the following endpoints become available:

## Chat Endpoint

### **POST /api/chat**
  
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
    --url http://localhost:8000/api/chat \
    --header 'Content-Type: application/json' \
    --data '{"messages": [{"role": "user", "content": "What is the capital of France?"}]}'
  ```

## Entry Endpoint

### **POST /api/entry/{namespace}**
  
  This endpoint allows you to create an entry in a specified namespace.

  **Request Body:**
  ```json
  {
    "key": "value"
  }
  ```

  **Response:**
  - Status of the operation and entry details.

  **Usage Example:**
  ```bash
  curl --request POST \
    --url http://localhost:8000/api/entry/my_namespace \
    --header 'Content-Type: application/json' \
    --data '{"key": "value"}'
  ```

### **WebSocket /api/entry/{namespace}/stream**
  
  This endpoint establishes a WebSocket connection for real-time data streaming into the specified namespace.

  **Usage:**
  - Connect via WebSocket client and stream data as JSON messages.
  - Each sent message triggers an addition to the namespace and returns a confirmation.

### **GET /api/entry/{namespace}**
  
  Fetches all entries within a specific namespace.

  **Response:**
  - A list of all entries in the namespace.

  **Usage Example:**
  ```bash
  curl --request GET \
    --url http://localhost:8000/api/entry/my_namespace
  ```

### **GET /api/entry/{namespace}/{entry_id}**
  
  Retrieves a specific entry by its ID within the namespace.

  **Response:**
  - Details of the specified entry.

  **Usage Example:**
  ```bash
  curl --request GET \
    --url http://localhost:8000/api/entry/my_namespace/1
  ```

### **PUT /api/entry/{namespace}/{entry_id}**
  
  Updates a specific entry by its ID within the namespace.

  **Request Body:**
  ```json
  {
    "updated_key": "updated_value"
  }
  ```

  **Response:**
  - Status of the update operation.

  **Usage Example:**
  ```bash
  curl --request PUT \
    --url http://localhost:8000/api/entry/my_namespace/1 \
    --header 'Content-Type: application/json' \
    --data '{"updated_key": "updated_value"}'
  ```

### **DELETE /api/entry/{namespace}/{entry_id}**
  
  Removes a specific entry by its ID within the namespace.

  **Response:**
  - Status of the removal operation.

  **Usage Example:**
  ```bash
  curl --request DELETE \
    --url http://localhost:8000/api/entry/my_namespace/1
  ```

These endpoints provide the foundation for interacting with the Hive Agent, allowing for both real-time and persistent data handling, as well as dynamic interaction via chat.
