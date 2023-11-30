"""
The processing module is responsible for providing utilities which help process files.
"""
from time import sleep
import os
import frontmatter
from rich.progress import track
import click
from utils.walker import Walker
from utils.store import Store

default_file_limit = int(os.environ["DEFAULT_FILE_LIMIT"])
default_delay_per_request = float(os.environ["DEFAULT_DELAY_PER_REQUEST"])
typeformat = {"txt": "text", "md": "markdown"}


class Processor:
    """
    The Processor class is responsible for processing files and inserting them into the datastore.
    """

    def __init__(
        self,
        directory: str,
        store: Store,
        file_types_to_process: list[str] = [],
        file_limit: int = default_file_limit,
        delay_per_request: float = default_delay_per_request,
    ) -> None:
        self.dir = directory
        self.store = store
        if len(file_types_to_process) == 0:
            self.file_types_to_process = [".txt", ".md"]
        self.file_limit = file_limit
        self.delay_per_request = delay_per_request

        self.walker = Walker(dir)

        self.files_to_process: list[str] = []
        self.files_processed: list[str] = []
        self.unprocessed_files: list[str] = []
        self.files_to_delete: list[str] = []
        self.files_to_update: list[str] = []

    def run_build(self):
        """
        Run the build process for the processing directory.
        """
        print(f"Running build on store {self.store.get_name()}")
        self.store.reset_db()
        print("Getting files to process.")
        self.get_all_directory_processable_files()
        print(f"Found {len(self.files_to_process)} files to process. Processing...")
        print("\n\n")
        self.process_files()

    def run_sync(self):
        """
        Run the sync process for the processing directory.
        """
        print(f"Running sync on store {self.store.get_name()}")
        self.identify_files_out_of_sync()

    def flush_context(self):
        """
        Flush the context of the processor.
        """
        self.files_to_process = []
        self.files_processed = []
        self.files_to_process = []
        self.files_to_delete = []
        self.files_to_update = []

    def file_is_private(self, file: str) -> bool:
        """
        Checks if a file is private.
        """
        if "_private" in file:
            return True

        with open(file, "r", encoding="utf-8") as f:
            fm = frontmatter.load(f)
            if "private" in fm and (fm["private"] == "true" or fm["private"] == True):
                return True
            return False

    def file_is_type_to_process(self, file: str) -> bool:
        """
        Checks if a file is the right type to process.
        """
        file_type = os.path.splitext(file)[1]
        if file_type in self.file_types_to_process:
            return True
        return False

    def get_all_directory_processable_files(self):
        """
        Gets all the files to process.
        """
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

        return self.files_to_process

    def process_files(self) -> None:
        """
        Process all files in the files_to_process list.
        """
        for file in track(self.files_to_process, description="[green]Processing files"):
            sleep(self.delay_per_request)
            self.process_file(file)

    def process_file(self, file: str) -> None:
        """
        Process an individual file, inserting it into the datastore.
        """
        file_type = os.path.splitext(file)[1]
        formatted_type = typeformat[file_type[1:]]
        formatted_path = os.path.relpath(file, self.dir)
        formatted_title = os.path.splitext(os.path.basename(file))[0]

        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            if content == "":
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

        self.files_processed.append(file)

    def identify_files_out_of_sync(self):
        """
        Identify files which meet the following criteria:
        - File content in datastore does not match file content on disk
        - File is on datastore but doesn't exist on disk
        - File is on disk but doesn't exist in datastore
        """
        self.flush_context()
        self.identify_deleted_files()
        self.identify_new_files()
        self.identify_updated_files()

        click.echo(f"Found {len(self.files_to_delete)} files to delete.")
        click.echo(f"Found {len(self.files_to_update)} files to update.")
        click.echo(f"Found {len(self.files_to_process)} files to process.")

    def identify_new_files(self):
        """
        Identify files which meet the following criteria:
        - File exists on disk but not in datastore
        """
        processable_files = self.get_all_directory_processable_files()
        db_files = self.store.get_all_titles()

        new_files = []

        for file in processable_files:
            if file not in db_files:
                new_files.append(file)
                self.files_to_process.append(file)

        return new_files

    def identify_deleted_files(self):
        """
        Identify files which meet the following criteria:
        - File exists in datastore but not on disk
        """
        processable_files = self.get_all_directory_processable_files()
        db_files = self.store.get_all_titles()

        deleted_files = []

        for file in db_files:
            if file not in processable_files:
                deleted_files.append(file)
                self.files_to_delete.append(file)

        return deleted_files

    def identify_updated_files(self):
        """
        Identify files which meet the following criteria:
        - File exists in datastore and on disk
        - File content in datastore does not match file content on disk
        """
        db_files = self.store.get_all()

        updated_files = []

        for file in db_files:
            with open(file[1], "r", encoding="utf-8") as f:
                content = f.read()
                if content != file[2]:
                    updated_files.append(file)
                    self.files_to_update.append(file)

        return updated_files
