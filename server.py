import os
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils.datastore import Datastore

load_dotenv()

PORT = os.environ["SERVER_PORT"] if "SERVER_PORT" in os.environ else 8000

app = Flask(__name__)


def get_datastore():
    """
    Gets the global datastore for the given thread.
    """
    return Datastore("datastore")


@app.route("/stores", methods=["GET"])
def get_store_by_query_params():
    """
    Retrieves a store by name and path from query parameters.
    """
    try:
        name = request.args.get("name")
        path = request.args.get("path")

        if not name and not path:
            return jsonify(
                {"message": "Name or path query parameters are required."}
            ), 400

        datastore = get_datastore()

        if path:
            store_with_path = datastore.get_store_by_absolute_path(path)
            if not store_with_path:
                store_with_path = datastore.get_store_by_relative_path(path)
            if not store_with_path:
                return jsonify(
                    {"message": f"Store with path '{path}' does not exist."}
                ), 404

            store_details = {
                "name": store_with_path.get_name(),
                "path": store_with_path.get_db_path(),
            }

            return jsonify(
                {
                    "message": f"Successfully retrieved store with path '{path}'.",
                    "data": store_details,
                }
            )

        if name:
            datastore = get_datastore()
            store_exists = datastore.check_store_exists(name)
            if not store_exists:
                return jsonify({"message": f"Store '{name}' does not exist."}), 404

            store = datastore.get_store(name)
            store_details = {
                "name": store.get_name(),
                "path": path,  # Assuming you want to include the path in the response
            }

            return jsonify(
                {
                    "message": f"Successfully retrieved store '{name}'.",
                    "data": store_details,
                }
            )
    except Exception as e:
        return jsonify({"message": f"Error retrieving store: {e}"}), 500


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

        store = datastore.get_store(name)
        store_details = {
            "name": store.get_name(),
            "path": store.get_db_path(),
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
                    "distance": result[3],
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


if __name__ == "__main__":
    app.run(port=PORT, debug=True)
