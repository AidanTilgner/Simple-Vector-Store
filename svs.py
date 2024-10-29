#!/usr/bin/env python3
"""
The entrypoint for the CLI.
"""

import os
import sys
from typing import Optional
import click
from dotenv import load_dotenv
from utils.datastore import Datastore
from utils.processing import Processor
from utils.store import Store
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

console = Console()
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
    console.print(f'Adding "{name}" to store with location {abs_path}')
    datastore.add_new_store(name, abs_path)


@click.command()
@click.option("--name", default=None)
def get(name: Optional[str]):
    """
    Gets a store by name, or all the stores if no name is provided.
    """
    console.print("\n\n")
    if name is None:
        ss = datastore.get_all_db_stores()
        console.print("All stores:\n")
        for s in ss:
            console.print(f"- {s[0]} {s[1]}\n")
    else:
        s = datastore.get_db_store(name)
        console.print(f"Store {s[0]}:\n")


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
            console.print("Datastore reset successfully.")
        except ValueError as e:
            console.print("Error resetting datastore: ", e)
        except Exception as e:
            console.print(
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
    console.print(f"Attempting to build store {name}")
    try:
        s = datastore.get_store(name)
        store_data = datastore.get_db_store(name)
        processor = Processor(
            directory=store_data[1],
            store=s,
        )
        processor.run_build()
    except ValueError as e:
        console.print("Error building store: ", e)


@click.command()
@click.argument("name")
@click.argument("query")
@click.option(
    "--column", help="The column to search in (title or content).", default="content"
)
def search(name, query, column):
    """
    Searches a given store based on a query.
    """
    console.print(f"Searching store {name} for query '{query}' in column {column}")
    try:
        if column not in ["title", "content"]:
            raise Exception("Invalid column, must be either 'title' or 'content'")
        if column is None:
            column = "content"
        s = datastore.get_store(name)
        results = s.search_and_map_similar_items(query, column)

        for result in results:
            console.print(
                Markdown(
                    f"({result[0]}) {result[1]}:\n\n {Store.get_content_summary(result[2], 256)}\n\n\n"
                )
            )
    except Exception as e:
        console.print("Error searching store: ", e)


@click.command()
@click.argument("name")
def sync(name):
    """
    Sync a store.
    """
    console.print(f"Attempting to sync store {name}")
    try:
        s = datastore.get_store(name)
        store_data = datastore.get_db_store(name)
        processor = Processor(
            directory=store_data[1],
            store=s,
        )
        processor.run_sync()
    except ValueError as e:
        console.print("Error syncing store: ", e)


@click.command()
@click.argument("name")
@click.argument("new_name")
def rename(name, new_name):
    """
    Rename a store.
    """
    console.print(f"Attempting to rename store {name} to {new_name}")
    try:
        datastore.rename_store(name, new_name)
        console.print(f"Store {name} renamed to {new_name}")
    except ValueError as e:
        console.print("Error renaming store: ", e)


@click.command()
@click.argument("name")
def remove(name):
    """
    Remove a store.
    """
    console.print(f"Attempting to remove store {name}")
    try:
        datastore.remove_store(name)
        console.print(f"Store {name} removed")
    except ValueError as e:
        console.print("Error removing store: ", e)


store.add_command(build)
store.add_command(search)
store.add_command(sync)
store.add_command(rename)
store.add_command(remove)


if __name__ == "__main__":
    cli.add_command(stores)
    cli.add_command(store)
    cli()
