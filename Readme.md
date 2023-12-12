# Simple Vector Store
Simple Vector Store (SVS) is a lightweight, **simple** vector store for your files. Simply point it at a directory, and it will create a vectorized version of that directory in the store of your choice, which can be easily searched semantically. Manage multiple stores, and use the REST API feature to connect your stores with other systems. Perfect for simple RAG Chatbots, knowledge base search, and plenty of other use-cases.

The synchronization feature allows you to easily maintain a vector representation of your directory over time, as it evolves. The SVS automatically detects differences between your source material and the vector store, and updates itself accordingly so that you never have to rebuild from scratch.

## Early Release and Contributing
This repository is in its early stages, so **don't hesitate to reach out and/or report bugs**. I wan't this repository to be simple but reliable. Therefore, new bug reports are encouraged and will be addressed if reproduced. New features will be considered, but they won't be added unless they fit the scope of the project. If you still think the feature should be developed, feel free to fork the repository and let us know about it here.

If you would like to contribute, go ahead and reach out to me, you can find my contact info on [my website](https://www.aidantilgner.dev).

## Features
The SVS provides multiple utilities to suit your vector store needs.

### Current Features
- Vectorize a directory as a store
- Manage multiple stores
- Synchronize stores with their source
- Easily query a store
- REST API script

### Planned Features
- Increased store management features
- Additional redundancy and edge-case checks

### Proposed Features
These aren't "planned" per-se, but if people show interest then I'd be willing to build them:
- Support for multiple embeddings models

## Getting Setup
The simplest way to get started is to clone this repo:

```bash
git clone https://github.com/AidanTilgner/Simple-Vector-Store.git
```

Then, navigate to the new directory:

```
cd Simple-Vector-Store
```

Then, install requirements with pip. I'd **also recommend using a virtual environment, with at least Python 3.9**.:

```bash
pip install -r requirements.txt
```

Then, copy the `.env.example` file into a new file called `.env`:

Macos/Linux:
```bash
cp .env.example .env
```

Windows:
```bash
copy .env.example .env
```

And make sure to fill out the fields in the new .env file, especially your `OPENAI_API_KEY` for embeddings.

## CLI Usage
The script is fairly simple, and uses a click CLI to make things more intuitive. The CLI functionality all happens in the `main.py` script, so all the commands will start by running the `main.py`:

```bash
python main.py <command> <subcommand> [...ARGUMENTS] [...OPTIONS]
```
You can always alias this as well, however that's up to you unless people want it to be a part of the program directly.

### Your First Store
Creating a `store` is essentially creating a vectorization of a certain location. You can create a store like so:

```bash
python main.py stores add <store_name> <location_of_directory>
```

Here you'll want to replace `<store_name>` with the name you want to give your store, and `<location_of_direcory>` with the directory of files that you want to vectorize. Now that you have a store, verify that it's there with the `stores get` command:

```bash
python main.py stores get
```

The result should be a list of stores. Now, you can build that store by running the build command:

```bash
python main.py store build <store_name>
```

You should see a progress bar, and if everything is set up correctly, this should work accross the board. Keep in mind, this step uses the OpenAI Embeddings, and you may see [issues related to them](#openai-rate-limits).

Now that you've built your store, you can search it like so:

```bash
python main.py store search <store_name> <query>
```

Where your `<query>` is the text string that you want to find related documents to. The result of this command should be a list of results with the beginnings of each document.

Now, say you've made some changes to your knowledge base or directory which was previously vectorized, and you'd like to see those changes reflected. Simply run the `store sync` command to update your store without having to rebuild from scratch:

```bash
python main.py store sync <store_name>
```

This will find all the differences between your current store and the source directory, and update the store accordingly.

### Commands
There are two base commands as of now, each with a few subcommands:

- `stores`: manage the different stores
    - `add <name> <path_to_directory>`: add a new store, of a given name and path
    - `get [name]`: get all the stores, or if you provide the optional `--name` flag, you can fetch information about an individual store
    - `reset`: | <mark>DANGEROUS</mark> | This will reset your entire datastore to its initial state
- `store`: work with an individual store
    - `build <name>`: builds the store based on the files in the given path
    - `search <name> <query> [column (title | content)]`: performs semantic search on the given store, add a `--column` flag with either "title" or "content" to search the respective column
    - `sync <name>`: run synchronization for a given store, any changes made to the source will be reflected after synchronization 
    - `rename <name> <new_name>`: rename a store from one name to another
    - `remove <name>`: remove a given store from the datastore

## REST API Usage
You can set up a little server to return results from a given store, by running the `server.py` script:

```bash
python server.py
```

> You can provide a SERVER_PORT variable in your `.env` file to override the default of `8000`

This will expose a `search` endpoint, which will return results of the search: `GET /stores/<name>/search`

You can make a GET request to this endpoint, while providing the following query paramters:
- `query`: the query to search
- `column`: "content" or "title", "content" is the default
- `limit`: the amount of results which the query should return, default is 10

So, an example request would look like this:

```
http://localhost:8000/stores/test_store/search?query="test query"&limit=10&column=content
```

## Troubleshooting
There are a few gotchas that you should be aware of.

### OpenAI Rate Limits
You can learn more about OpenAI's rate-limiting on [their site](https://platform.openai.com/docs/guides/rate-limits?context=tier-free). These will apply since this script uses the [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings). The script has ways to account for this, such as the `DEFAULT_FILE_LIMIT` and `DEFAULT_DELAY_PER_REQUEST` environment variables, which are set up for the "free" tier of the OpenAI API.

If you fall under the free tier you may see fairly severe rate limits, such as only 200 requests per day and 3 per minute. Fortunately however, the bar for reaching tier 1 is fairly low (around 5 dollars paid), and the RPM and RPD increase substantially.
