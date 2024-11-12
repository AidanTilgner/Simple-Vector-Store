import os
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils.datastore import Datastore
from utils.processing import Processor

load_dotenv()

PORT = (
    int(os.environ["SERVER_PORT"])
    if "SERVER_PORT" in os.environ and isinstance(os.environ["SERVER_PORT"], int)
    else 8000
)
ENV = os.environ.get("SERVER_ENV", "production")  # default to 'production'

app = Flask(__name__)


def get_datastore():
    """
    Gets the global datastore for the given thread.
    """
    return Datastore("datastore")


@app.route("/stores", methods=["GET"])
def get_stores():
    """
    Retrieves all stores.
    """
    try:
        datastore = get_datastore()
        stores = datastore.get_all_db_stores()
        store_details = [{"name": store[0], "location": store[1]} for store in stores]

        return jsonify(
            {
                "message": f"Successfully retrieved {len(stores)} store(s).",
                "data": store_details,
            }
        )
    except Exception as e:
        return jsonify({"message": f"Error retrieving stores: {e}"}), 500


@app.route("/stores/<name>", methods=["GET"])
def get_store(name: str):
    """
    Retrieves a store by name.
    """
    try:
        datastore = get_datastore()
        store_exists = datastore.check_store_exists(name)
        if not store_exists:
            return jsonify({"message": f"Store '{name}' does not exist."}), 404

        store = datastore.get_db_store(name)
        store_details = {
            "name": store[0],
            "path": store[1],
        }

        return jsonify(
            {
                "message": f"Successfully retrieved store '{name}'.",
                "data": store_details,
            }
        )
    except Exception as e:
        return jsonify({"message": f"Error retrieving store: {e}"}), 500


@app.route("/stores", methods=["POST"])
def create_store():
    """
    Creates a new store with the given name and path.
    """
    try:
        data = request.get_json()
        if not data or "name" not in data or "path" not in data:
            return jsonify({"message": "Name and path are required."}), 400

        name = data["name"]
        path = data["path"]

        datastore = get_datastore()
        store_exists = datastore.check_store_exists(name)
        if store_exists:
            return jsonify({"message": f"Store '{name}' already exists."}), 400

        path_exists = datastore.check_store_with_path_exists(path)
        print("Store already exists: ", path_exists, path)
        if path_exists:
            return jsonify(
                {"message": f"Store with path '{path}' already exists."}
            ), 400

        datastore.add_new_store(name, path)
        return jsonify({"message": f"Store '{name}' created successfully."}), 201

    except Exception as e:
        return jsonify({"message": f"Error creating store: {e}"}), 500


@app.route("/stores/<name>/search", methods=["GET"])
def search_store(name: str):
    """
    Searches a store by name.
    """
    try:
        start_time = time.time()

        datastore = get_datastore()
        store_exists = datastore.check_store_exists(name)
        if not store_exists:
            return jsonify({"message": f"Store '{name}' does not exist."}), 404

        store = datastore.get_store(name)
        query = request.args.get("query")
        if query is None:
            return jsonify({"message": "No query provided."}), 400
        column = request.args.get("column")
        if column is None:
            column = "content"
        limit = request.args.get("limit")
        if limit is None:
            limit = 10
        else:
            limit = int(limit)
        threshold = request.args.get("threshold")
        if threshold is None:
            threshold = 0.5
        else:
            threshold = float(threshold)

        results = store.search_and_map_similar_items(
            query=query, search_in=column, limit=limit
        )
        results_list = []
        for result in results:
            results_list.append(
                {
                    "id": result[0],
                    "title": result[1],
                    "content": result[2],
                    "path": result[3],
                    "type": result[4],
                    "distance": result[5],
                }
            )

        end_time = time.time()
        time_taken = end_time - start_time
        time_taken_ms = round(time_taken * 1000, 2)

        return jsonify(
            {
                "message": f"Successfully searched store '{name}' for query '{query}' in column '{column}', in {time_taken_ms}ms",
                "data": results_list,
            }
        )
    except Exception as e:
        return jsonify({"message": f"Error searching store: {e}"}), 500


@app.route("/stores/<name>/search", methods=["POST"])
def search_store_post(name: str):
    """
    Searches a store by name.
    """
    try:
        start_time = time.time()

        datastore = get_datastore()
        store_exists = datastore.check_store_exists(name)
        if not store_exists:
            return jsonify({"message": f"Store '{name}' does not exist."}), 404

        store = datastore.get_store(name)
        data = request.get_json()
        if data is None:
            return jsonify({"message": "No data provided."}), 400
        query = data.get("query")
        if query is None:
            return jsonify({"message": "No query provided."}), 400
        column = data.get("column")
        if column is None:
            column = "content"
        limit = data.get("limit")
        if limit is None:
            limit = 10
        else:
            limit = int(limit)
        threshold = data.get("threshold")
        if threshold is None:
            threshold = 0.5
        else:
            threshold = float(threshold)

        results = store.search_and_map_similar_items(
            query=query, search_in=column, limit=limit, threshold=threshold
        )
        results_list = []
        for result in results:
            results_list.append(
                {
                    "id": result[0],
                    "title": result[1],
                    "content": result[2],
                    "path": result[3],
                    "type": result[4],
                    "distance": result[5],
                }
            )

        end_time = time.time()
        time_taken = end_time - start_time
        time_taken_ms = round(time_taken * 1000, 2)

        return jsonify(
            {
                "message": f"Successfully searched store '{name}' for query '{query}' in column '{column}', in {time_taken_ms}ms",
                "data": results_list,
            }
        )
    except Exception as e:
        return jsonify({"message": f"Error searching store: {e}"}), 500


@app.route("/stores/<name>/sync", methods=["POST"])
def sync_store(name: str):
    """
    Syncs a store by name.
    """
    try:
        start_time = time.time()
        datastore = get_datastore()
        s = datastore.get_store(name)
        store_data = datastore.get_db_store(name)
        processor = Processor(
            directory=store_data[1],
            store=s,
        )
        processor.run_sync()
        end_time = time.time()
        time_taken = end_time - start_time
        time_taken_ms = round(time_taken * 1000, 2)

        return jsonify(
            {
                "message": f"Successfully synced store '{name}' in {time_taken_ms}ms",
            }
        )
    except ValueError as e:
        return jsonify({"message": f"Error syncing store: {e}"}), 500


@app.route("/stores/<name>/build", methods=["POST"])
def build_store(name: str):
    """
    Builds a store by name.
    """
    try:
        start_time = time.time()
        datastore = get_datastore()
        s = datastore.get_store(name)
        store_data = datastore.get_db_store(name)
        processor = Processor(
            directory=store_data[1],
            store=s,
        )
        processor.run_build()
        end_time = time.time()
        time_taken = end_time - start_time
        time_taken_ms = round(time_taken * 1000, 2)

        return jsonify(
            {
                "message": f"Successfully built store '{name}' in {time_taken_ms}ms",
            }
        )
    except ValueError as e:
        return jsonify({"message": f"Error building store: {e}"}), 500


if __name__ == "__main__":
    if ENV == "development":
        # Run in development mode with Flask's built-in server
        app.run(port=PORT, debug=True)
    else:
        # Run in production mode with Gunicorn
        from gunicorn.app.base import BaseApplication

        class GunicornApp(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                if self.cfg is not None:
                    config = {
                        key: value
                        for key, value in self.options.items()
                        if key in self.cfg.settings and value is not None
                    }
                    for key, value in config.items():
                        self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = {
            "bind": f"0.0.0.0:{PORT}",
            "workers": 4,  # Adjust the number of workers as per your server's resources
        }

        GunicornApp(app, options).run()
