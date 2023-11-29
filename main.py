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
    if name is None:
        stores = datastore.get_all_db_stores()
        print(stores)
    else:
        store = datastore.get_db_store(name)
        print(store)


@click.group()
def store():
    pass

store.add_command(add)
store.add_command(get)



if __name__ == "__main__":
    cli.add_command(store)
    cli()
