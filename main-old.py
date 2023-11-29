import argparse
import os
import time
import frontmatter
from tenacity import sleep
from dotenv import load_dotenv
from db import DB
from ui import update_progress

load_dotenv()

db = DB("db.sqlite")

file_types_to_process = [".txt", ".md"]
files_to_process = []
files_processed = []
file_limit = int(os.environ["DEFAULT_FILE_LIMIT"])
delay_per_request = int(os.environ["DEFAULT_DELAY_PER_REQUEST"])
location = ""
typeformat = {"txt": "text", "md": "markdown"}


def process_file(file: str) -> None:
    """Processes a file."""
    global files_processed
    file_name = os.path.basename(file)
    update_progress(len(files_processed) / len(files_to_process), message=f'Processing file "{file_name}"')

    file_type = os.path.splitext(file)[1]
    formatted_type = typeformat[file_type[1:]]
    formatted_path = os.path.relpath(file, location)
    formatted_title = os.path.splitext(os.path.basename(file))[0]

    with open(file, "r") as f:
        content = f.read()
        if (content == ""):
            return
        try:
            db.insert_into_knowledge_base(
                path=formatted_path,
                title=formatted_title,
                content=content,
                filetype=formatted_type,
            )
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
            raise e

    files_processed.append(file)
    update_progress(len(files_processed) / len(files_to_process), message=f'Processed file "{file_name}"')


def process_all_files() -> None:
    """Processes all the files."""
    for file in files_to_process:
        # sleep to avoid rate-limiting
        sleep(delay_per_request)
        process_file(file)


def walk_location(location: str) -> None:
    """Walks a location and all files in it."""
    for dirpath, _, filename in os.walk(location):
        if '_private' in dirpath:
            continue
        for file in filename:
            file_type = os.path.splitext(file)[1]
            if file_type in file_types_to_process:
                try:
                    with open(os.path.join(dirpath, file), "r") as f:
                        fm = frontmatter.load(f)
                        if 'private' in fm and (fm["private"] == "true" or fm["private"] == True):
                            continue
                        if len(files_to_process) >= file_limit:
                            return
                        files_to_process.append(os.path.join(dirpath, file))
                except Exception as e:
                    print(f"Error walking file {file}: {e}")
                    raise e



if __name__ == "__main__":
    start_time = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument("location", help="Location of knowledge base.")
    parser.add_argument("-l", "--limit", type=int, help="Limit the number of files to process.", default=500)
    parser.add_argument("-d", "--delay", type=float, help="Delay between requests to OpenAI API.", default=0.5)
    parser.add_argument("--no-delay", action="store_true", help="Disable delay between requests to OpenAI API.")

    args = parser.parse_args()

    location = args.location
    delay_per_request = args.delay
    no_delay = args.no_delay
    limit = args.limit

    if no_delay:
        delay = 0

    delay_per_request = max(0, delay_per_request)

    print(f"Walking location {location}\n")
    walk_location(location)

    print(f"Resetting database...\n")
    db.reset_db()

    print(f"Found {len(files_to_process)} files to process\n")
    print("Processing files...\n")
    process_all_files()

    end_time = time.time()
    time_diff = end_time - start_time
    time_ms = time_diff * 1000
    print(f"\n\n\nFinished in {round(time_ms, 2)} ms")
