"""
The entrypoint for the CLI.
"""
import os
import sys
from typing import Optional
import click
from utils.datastore import Datastore
from utils.processing import Processor
from utils.store import Store

datastore = Datastore("datastore")


def get_absolute_path(path: str):
    """
    A util to get the proper absolute path of a given path.
    """
    joined_path = os.path.join(os.path.dirname(__file__), path)
    return os.path.abspath(joined_path)


@click.group()
def cli():
    """
    The entrypoint for the CLI.
    """


@click.command()
@click.argument("name")
@click.argument("path")
def add(name: str, path: str):
    """
    Add a
    """
    abs_path = get_absolute_path(path)
    print(f'Adding "{name}" to store with location {abs_path}')
    datastore.add_new_store(name, abs_path)


@click.command()
@click.option("--name", default=None)
def get(name: Optional[str]):
    """
    Gets a store by name, or all the stores if no name is provided.
    """
    print("\n\n")
    if name is None:
        ss = datastore.get_all_db_stores()
        print("All stores:\n")
        for s in ss:
            print(f"- {s[0]} {s[1]}\n")
    else:
        s = datastore.get_db_store(name)
        print(f"Store {s[0]}:\n")


@click.command()
def reset():
    """
    Resets the datastore.
    """
    answer = input(
        "Are you sure you want to reset the datastore, all data will be lost and this cannot be undone?\nIf you are sure please type 'RESET': "
    )
    if answer == "RESET":
        try:
            datastore.hard_reset()
            print("Datastore reset successfully.")
        except ValueError as e:
            print("Error resetting datastore: ", e, file=sys.stderr)
        except Exception as e:
            print(
                "An error occurred while resetting the datastore: ", e, file=sys.stderr
            )


@click.group()
def stores():
    """
    Get and add stores.
    """


stores.add_command(add)
stores.add_command(get)
stores.add_command(reset)


@click.group()
def store():
    """
    Manage individual stores.
    """


@click.command()
@click.argument("name")
def build(name):
    """
    Build a store.
    """
    print(f"Attempting to build store {name}")
    try:
        s = datastore.get_store(name)
        store_data = datastore.get_db_store(name)
        processor = Processor(
            directory=store_data[1],
            store=s,
            file_types_to_process=[".md", ".txt", ".html"],
        )
        processor.run_build()
    except ValueError as e:
        print("Error building store: ", e)


@click.command()
@click.argument("name")
@click.argument("query")
@click.option(
    "--column", help="The column to search in (title or content).", default="title"
)
def search(name, query, column):
    """
    Searches a given store based on a query.
    """
    print(f"Searching store {name} for query '{query}' in column {column}")
    try:
        if column not in ["title", "content"]:
            raise Exception("Invalid column, must be either 'title' or 'content'")
        if column is None:
            column = "content"
        s = datastore.get_store(name)
        results = s.search_and_map_similar_items(query, column)

        for result in results:
            print(
                f"({result[0]}) {result[1]}:\n\n {Store.get_content_summary(result[2], 256)}\n\n\n"
            )
    except Exception as e:
        print("Error searching store: ", e)


@click.command()
@click.argument("name")
def sync(name):
    """
    Sync a store.
    """
    print(f"Attempting to sync store {name}")
    try:
        s = datastore.get_store(name)
        store_data = datastore.get_db_store(name)
        processor = Processor(
            directory=store_data[1],
            store=s,
            file_types_to_process=[".md", ".txt", ".html"],
        )
        processor.run_sync()
    except ValueError as e:
        print("Error syncing store: ", e)


store.add_command(build)
store.add_command(search)
store.add_command(sync)


if __name__ == "__main__":
    cli.add_command(stores)
    cli.add_command(store)
    cli()
