# Simple Vector Store REST API
You can use the Simple Vector Store REST API to interact with your stores. This is useful for integrating the SVS into other applications, or for automating tasks.

# Setting it up
First, define the `SERVER_PORT` environment variable in your `.env` file. This will be where the server will listen for requests. By default, the server will listen on port `8000`.

Next, run the server script:
```bash
python server.py
```

> [!note]
> You'll notice a warning about running the server in development mode. I just haven't gotten around to making it production yet. It's on the list!

# Endpoints
The server has a few endpoints that you can use to interact with your stores. Here's a list of them:

- **GET /stores**: Retrieve store by name or path.
- **GET /stores/<name>**: Retrieve store by name.
- **POST /stores**: Create a new store.
- **GET /stores/<name>/search**: Search store by name using query parameters.
- **POST /stores/<name>/search**: Search store by name using JSON request body.
- **POST /stores/<name>/sync**: Sync store by name.
- **POST /stores/<name>/build**: Build store by name.

## Documentation
1. **GET /stores**
   - **Description:** Retrieves a store by name or path from query parameters.
   - **Query Parameters:**
     - `name` (optional): The name of the store.
     - `path` (optional): The path of the store.
   - **Responses:**
     - 200: Successfully retrieved store.
     - 400: Name or path query parameters are required.
     - 404: Store does not exist.
     - 500: Error retrieving store.

2. **GET /stores/<name>**
   - **Description:** Retrieves a store by name.
   - **Path Parameters:**
     - `name`: The name of the store.
   - **Responses:**
     - 200: Successfully retrieved store.
     - 404: Store does not exist.
     - 500: Error retrieving store.

3. **POST /stores**
   - **Description:** Creates a new store with the given name and path.
   - **Request Body:**
     - `name`: The name of the store.
     - `path`: The path of the store.
   - **Responses:**
     - 201: Store created successfully.
     - 400: Name and path are required, or store already exists.
     - 500: Error creating store.

4. **GET /stores/<name>/search**
   - **Description:** Searches a store by name using query parameters.
   - **Path Parameters:**
     - `name`: The name of the store.
   - **Query Parameters:**
     - `query`: The search query.
     - `column` (optional): The column to search in (default is "content").
     - `limit` (optional): The maximum number of results to return (default is 10).
   - **Responses:**
     - 200: Successfully searched store.
     - 400: No query provided.
     - 404: Store does not exist.
     - 500: Error searching store.

5. **POST /stores/<name>/search**
   - **Description:** Searches a store by name using a JSON request body.
   - **Path Parameters:**
     - `name`: The name of the store.
   - **Request Body:**
     - `query`: The search query.
     - `column` (optional): The column to search in (default is "content").
     - `limit` (optional): The maximum number of results to return (default is 10).
   - **Responses:**
     - 200: Successfully searched store.
     - 400: No query provided.
     - 404: Store does not exist.
     - 500: Error searching store.

6. **POST /stores/<name>/sync**
   - **Description:** Syncs a store by name.
   - **Path Parameters:**
     - `name`: The name of the store.
   - **Responses:**
     - 200: Successfully synced store.
     - 500: Error syncing store.

7. **POST /stores/<name>/build**
   - **Description:** Builds a store by name.
   - **Path Parameters:**
     - `name`: The name of the store.
   - **Responses:**
     - 200: Successfully built store.
     - 500: Error building store.

## Examples
Here are some examples of how you can use the Simple Vector Store REST API:

**Perform a search on a store:**
```bash
curl -X POST http://localhost:8000/stores/my_store/search -d '{"query": "hello"}'
```

**Create a new store:**
```bash
curl -X POST http://localhost:8000/stores -d '{"name": "new_store", "path": "/path/to/store"}'
```

**Sync a store:**
```bash
curl -X POST http://localhost:8000/stores/my_store/sync
```

**Build a store:**
```bash
curl -X POST http://localhost:8000/stores/my_store/build
```

That's it! You can now interact with your stores using the Simple Vector Store REST API.
