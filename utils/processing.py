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
        self.directory = directory
        self.store = store
        if len(file_types_to_process) == 0:
            self.file_types_to_process = [".txt", ".md"]
        else:
            self.file_types_to_process = file_types_to_process
        self.file_limit = file_limit
        self.delay_per_request = delay_per_request

        self.walker = Walker(self.directory)

    def run_build(self):
        """
        Run the build process for the processing directory.
        """
        print(f"Running build on store {self.store.get_name()}")
        self.store.reset_db()
        print("Getting files to process.")
        files_to_process = self.get_all_directory_processable_files()
        print(f"Found {len(files_to_process)} files to process. Processing...")
        print("\n\n")
        self.process_files(files=files_to_process)

    def run_sync(self):
        """
        Run the sync process for the processing directory.
        """
        print(f"Running sync on store {self.store.get_name()}, {self.directory}")
        self.identify_files_out_of_sync()

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
        new_files = []

        for file in self.walker.walk_files():
            if len(new_files) >= self.file_limit:
                return
            if self.file_is_private(file):
                continue
            if not self.file_is_type_to_process(file):
                continue
            new_files.append(file)

        return new_files

    def process_files(self, files: list[str]) -> None:
        """
        Process all files in the files_to_process list.
        """
        for file in track(files, description="[green]Processing files"):
            sleep(self.delay_per_request)
            self.process_file(file)

    def process_file(self, file: str) -> None:
        """
        Process an individual file, inserting it into the datastore.
        """
        file_type = os.path.splitext(file)[1]
        formatted_type = typeformat[file_type[1:]]
        formatted_path = os.path.relpath(file, self.directory)
        formatted_title = self.get_file_name_from_path(file)

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

    def identify_files_out_of_sync(self):
        """
        Identify files which meet the following criteria:
        - File content in datastore does not match file content on disk
        - File is on datastore but doesn't exist on disk
        - File is on disk but doesn't exist in datastore
        """
        click.echo("Identifying files which were deleted...")
        deleted_files = self.identify_deleted_files()
        click.echo("Identifying new files...")
        new_files = self.identify_new_files()
        click.echo("Identifying files which were updated...")
        updated_files = self.identify_updated_files()

        click.echo(f"Found {len(deleted_files)} files to delete.")
        click.echo(f"Found {len(new_files)} files to add.")
        click.echo(f"Found {len(updated_files)} files to update.")

        click.echo("Deleting files...")
        for file in track(deleted_files, description="[green]Deleting files"):
            print(f"Deleting file {file}")

        click.echo("Adding files...")
        for file in track(new_files, description="[green]Adding files"):
            print(f"Adding file {file}")

        click.echo("Updating files...")
        for file in track(updated_files, description="[green]Updating files"):
            print(f"Updating file {file}")

    def identify_new_files(self):
        """
        Identify files which meet the following criteria:
        - File exists on disk but not in datastore
        """
        processable_files = self.get_all_directory_processable_files()
        db_files = [item[0] for item in self.store.get_all_titles()]

        new_files = []

        for file in processable_files:
            filename = self.get_file_name_from_path(file)
            if filename not in db_files:
                new_files.append(file)

        return new_files

    def identify_deleted_files(self):
        """
        Identify files which meet the following criteria:
        - File exists in datastore but not on disk
        """
        processable_files = self.get_all_directory_processable_files()
        db_files = [item[0] for item in self.store.get_all_titles()]

        deleted_files = []

        for file in db_files:
            if file not in [self.get_file_name_from_path(f) for f in processable_files]:
                deleted_files.append(file)

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
            filepath = os.path.join(self.directory, file[2])
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if content != file[3]:
                    updated_files.append(file[2])

        return updated_files

    @staticmethod
    def get_file_name_from_path(path: str) -> str:
        """
        Get the file name from a path.
        """
        return os.path.splitext(os.path.basename(path))[0]
