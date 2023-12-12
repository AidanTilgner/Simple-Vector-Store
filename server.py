"""
This file provides a simple Flask REST API for interacting with stores.
"""

import os
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils.datastore import Datastore

load_dotenv()

PORT = os.environ["SERVER_PORT"] if "SERVER_PORT" in os.environ else 8000

datastore = Datastore("datastore")

app = Flask(__name__)


@app.route("/stores/<name>/search", methods=["GET"])
def search_store(name: str):
    """
    Searches a store by name.
    """
    start_time = time.time()
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


if __name__ == "__main__":
    app.run(port=PORT)
