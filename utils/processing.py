import os
from time import sleep
from utils.store import Store
from utils.walker import Walker
import frontmatter
from utils.ui import update_progress

file_types_to_process = [".txt", ".md"]
files_to_process = []
files_processed = []
file_limit = int(os.environ["DEFAULT_FILE_LIMIT"])
delay_per_request = float(os.environ["DEFAULT_DELAY_PER_REQUEST"])
location = ""
typeformat = {"txt": "text", "md": "markdown"}


class Processor:
    def __init__(
            self,
            dir: str,
            store: Store,
            file_types_to_process: list[str]=file_types_to_process,
            file_limit: int = file_limit,
            delay_per_request: float = delay_per_request,
        ) -> None:
        self.dir = dir
        self.store = store
        self.file_types_to_process = file_types_to_process
        self.files_to_process = []
        self.files_processed = []
        self.file_limit = file_limit
        self.delay_per_request = delay_per_request
        self.walker = Walker(dir)

    def run_build(self):
        print(f"Running build on store {self.store.get_name()}")
        self.store.reset_db()
        print(f"Getting files to process.")
        self.get_files_to_process()
        print(f"Found {len(self.files_to_process)} files to process. Processing...")
        print("\n\n")
        self.process_files()


    def file_is_private(self, file: str) -> bool:
        if '_private' in file:
            return True

        with open(file, "r") as f:
            fm = frontmatter.load(f)
            if 'private' in fm and (fm["private"] == "true" or fm["private"] == True):
                return True
            return False

    def file_is_type_to_process(self, file: str) -> bool:
        file_type = os.path.splitext(file)[1]
        if file_type in self.file_types_to_process:
            return True
        return False

    def get_files_to_process(self):
        if len(self.files_to_process) >= self.file_limit:
            return
        
        for file in self.walker.walk_files():
            if len(self.files_to_process) >= self.file_limit:
                return
            if self.file_is_private(file):
                continue
            if not self.file_is_type_to_process(file):
                continue
            self.files_to_process.append(file)


    def process_files(self):
        for file in self.files_to_process:
            sleep(self.delay_per_request)
            self.process_file(file)

    def process_file(self, file: str):
        progress = len(files_processed) / len(files_to_process) if len(files_to_process) else 0
        update_progress(progress, message=f'Processing file "{file}"')

        file_type = os.path.splitext(file)[1]
        formatted_type = typeformat[file_type[1:]]
        formatted_path = os.path.relpath(file, location)
        formatted_title = os.path.splitext(os.path.basename(file))[0]

        with open(file, "r") as f:
            content = f.read()
            if (content == ""):
                return
            try:
                self.store.insert_into_knowledge_base(
                    path=formatted_path,
                    title=formatted_title,
                    content=content,
                    filetype=formatted_type,
                )
            except Exception as e:
                print(f"Error processing file {file}: {e}")
                raise e


