from db import DB
import time
import argparse
from typing import Any

db = DB("db.sqlite")

def search_on(query: str, on: str) -> list[Any]:
    """Searches the knowledge base for a query."""
    results = db.search_and_map_similar_items(query, search_in=on)
    return results

def get_content_summary(content: str, length: int) -> str:
    """Returns a summary of the content."""
    return content[:length] + ("..." if len(content) > length else "")


if __name__ == "__main__":
    start_time = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Query to search for.")
    parser.add_argument("--on", help="Search in the title or the content of the note.", choices={'title', 'content'})


    args = parser.parse_args()

    query = args.query
    on = args.on or 'content'

    print(f"Searching for {query} in {on}\n")

    results = search_on(query, on)

    print(f"Found {len(results)} results\n")

    for result in results:
        print('-' * 80)
        print(f"({result[0]}) {result[1]}:\n\n {get_content_summary(result[2], 256)}\n\n\n")

    end_time = time.time()
    time_diff = end_time - start_time
    time_ms = time_diff * 1000
    print(f"Finished in {round(time_ms, 2)} ms")
