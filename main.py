import os
from typing import Optional
import click
from utils.datastore import Datastore
import time

from utils.processing import Processor
from utils.store import Store

datastore = Datastore("datastore")

def get_absolute_path(path: str):
    joined_path = os.path.join(os.path.dirname(__file__), path)
    return os.path.abspath(joined_path)


@click.group()
def cli():
    pass

@click.command()
@click.argument("name")
@click.argument("path")
def add(name: str, path: str):
    abs_path = get_absolute_path(path)
    print(f'Adding "{name}" to store with location {abs_path}')
    datastore.add_new_store(name, abs_path)

@click.command()
@click.option("--name", default=None)
def get(name: Optional[str]):
    print("\n\n")
    if name is None:
        stores = datastore.get_all_db_stores()
        print("All stores:\n")
        for s in stores:
            print(f'- {s[0]} {s[1]}\n')
    else:
        store = datastore.get_db_store(name)
        print(store)

@click.command()
def reset():
    answer = input("Are you sure you want to reset the datastore, all data will be lost and this cannot be undone?\nIf you are sure please type 'RESET': ")
    if answer == "RESET":
        try:
            datastore.hard_reset()
            print("Datastore reset successfully.")
        except Exception as e:
            print("Error resetting datastore: ", e)
        


@click.group()
def stores():
    pass

stores.add_command(add)
stores.add_command(get)
stores.add_command(reset)


@click.group()
def store():
    pass


@click.command()
@click.argument("name")
def build(name):
    print(f"Attempting to build store {name}")
    try:
        store = datastore.get_store(name)
        store_data = datastore.get_db_store(name)
        processor = Processor(
            dir=store_data[1],
            store=store,
        )
        processor.run_build()
    except Exception as e:
        print("Error building store: ", e)


@click.command()
@click.argument("name")
@click.argument("query")
@click.option("--column", help="The column to search in (title or content).", default="title")
def search(name, query, column):
    print(f"Searching store {name} for query '{query}' in column {column}")
    try:
        if column not in ["title", "content"]:
            raise Exception("Invalid column, must be either 'title' or 'content'")
        if column is None:
            column = "content"
        store = datastore.get_store(name)
        results = store.search_and_map_similar_items(query, column)
        
        for result in results:
            print(f"({result[0]}) {result[1]}:\n\n {Store.get_content_summary(result[2], 256)}\n\n\n")
    except Exception as e:
        print("Error searching store: ", e)


store.add_command(build)
store.add_command(search)



if __name__ == "__main__":
    start_time = time.time()

    cli.add_command(stores)
    cli.add_command(store)
    cli()

    end_time = time.time()
    time_diff = end_time - start_time
    time_ms = time_diff * 1000
    print(f"\n\n\nFinished in {round(time_ms, 2)} ms")

