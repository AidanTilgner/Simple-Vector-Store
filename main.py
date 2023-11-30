import os
from typing import Optional
import click
from utils.datastore import Datastore

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
    except Exception as e:
        print("Error building store: ", e)

store.add_command(build)


if __name__ == "__main__":
    cli.add_command(stores)
    cli.add_command(store)
    cli()
