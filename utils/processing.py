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
import fnmatch
from rich.console import Console

console = Console()

default_file_limit = int(os.environ["DEFAULT_FILE_LIMIT"])
default_delay_per_request = float(os.environ["DEFAULT_DELAY_PER_REQUEST"])
typeformat = {"txt": "text", "md": "markdown"}


class Processor:
    """
    The Processor class is responsible for processing files and inserting them into the datastore.
    """

    directory: str
    store: Store
    file_limit: int
    delay_per_request: float
    walker: Walker
    ignore_patterns: list[str]

    def __init__(
        self,
        directory: str,
        store: Store,
        file_limit: int = default_file_limit,
        delay_per_request: float = default_delay_per_request,
    ) -> None:
        self.directory = directory
        self.store = store
        self.file_limit = file_limit
        self.delay_per_request = delay_per_request
        self.walker = Walker(self.directory)

        self.load_svs_ignore()

    def load_default_ignore_patterns(self):
        # just text files, no images or special files for now
        # ignore all files that start with a dot
        default_ignore_patterns = [".*"]

        self.ignore_patterns.extend(default_ignore_patterns)

    def is_supported_file_type(self, file: str) -> bool:
        # only process text files for now
        text_types = [
            ".txt",
            ".md",
            ".markdown",
        ]
        code_types = [
            ".ts",
            ".js",
            ".py",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
            ".ps1",
            ".psm1",
            ".psd1",
            ".ps1xml",
            ".psc1",
            ".pssc",
            ".ksh",
            ".html",
        ]

        for type in text_types:
            if file.endswith(type):
                return True
        for type in code_types:
            if file.endswith(type):
                return True
        return False

    def run_build(self):
        """
        Run the build process for the processing directory.
        """
        console.print(f"Running build on store {self.store.get_name()}")
        self.store.reset_db()
        console.print("Getting files to process.")
        files_to_process = self.get_all_directory_processable_files()
        if not files_to_process:
            console.print("No files to process.")
            return
        console.print(f"Found {len(files_to_process)} files to process. Processing...")
        console.print("\n\n")
        self.process_files(files=files_to_process)

    def run_sync(self):
        """
        Run the sync process for the processing directory.
        """
        console.print(
            f"Running sync on store {self.store.get_name()}, {self.directory}"
        )
        self.identify_files_out_of_sync()

    def file_is_private(self, file: str) -> bool:
        """
        Checks if a file is private.
        """
        if "_private" in file:
            return True

        with open(file, "r") as f:
            fm = frontmatter.load(f)
            if "private" in fm and (
                str(fm["private"]).lower() == "true" or fm["private"]
            ):
                return True
            return False

    def load_svs_ignore(self):
        """
        Reads the .svsignore file.
        """
        found_ignore_files = []
        with os.scandir(self.directory) as entries:
            for entry in entries:
                if entry.name == ".svsignore":
                    found_ignore_files.append(entry.path)

        ignore_patterns = []
        for ignore_file in found_ignore_files:
            with open(ignore_file, "r") as f:
                for line in f:
                    if line.strip() == "":
                        continue
                    ignore_patterns.append(line.strip())
        self.ignore_patterns = ignore_patterns
        return ignore_patterns

    def should_ignore_file(self, file: str) -> bool:
        """
        Checks if a given file should be ignored based on .svsignore patterns.

        Args:
            file (str): The path to the file being checked.

        Returns:
            bool: True if the file should be ignored, False otherwise.
        """
        if file.endswith(".svsignore"):
            return True

        # Get the relative path of the file from the root directory
        rel_file = os.path.relpath(file, self.directory)

        for pattern in self.ignore_patterns:
            # Handle directory patterns (e.g., 'dir/' to ignore everything in a directory)
            if pattern.endswith("/"):
                if rel_file.startswith(pattern.rstrip("/")):
                    return True
            # Handle wildcard patterns and exact matches
            elif fnmatch.fnmatch(rel_file, pattern):
                return True

        return False

    def get_all_directory_processable_files(self) -> list[str]:
        """
        Gets all the files to process.
        """
        try:
            new_files = []

            for file in self.walker.walk_files():
                if len(new_files) >= self.file_limit:
                    return new_files
                if not self.is_supported_file_type(file):
                    continue
                if self.file_is_private(file):
                    continue
                if self.should_ignore_file(file):
                    continue
                new_files.append(file)

            return new_files
        except Exception as e:
            console.print(f"Error getting files to process: {e}")
            return []

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
                console.print(f"Error processing file {file}: {e}")
                raise e

    def identify_files_out_of_sync(self):
        """
        Identify files which meet the following criteria:
        - File content in datastore does not match file content on disk
        - File is on datastore but doesn't exist on disk
        - File is on disk but doesn't exist in datastore
        """
        # edge case where the db has no files and the directory has no files, nothing to do
        deleted_files = self.identify_deleted_files()
        click.echo(f"\nFound {len(deleted_files)} files to delete.")

        new_files = self.identify_new_files()
        click.echo(f"Found {len(new_files)} files to add.")

        updated_files = self.identify_updated_files()
        click.echo(f"Found {len(updated_files)} files to update.\n\n")

        if len(deleted_files) > 0:
            click.echo("Deleting files...")
            for file in track(deleted_files, description="[green]Deleting files"):
                db_file = self.store.get_entry_from_path(file[2])
                self.store.delete_item(db_file[0])

        if len(new_files) > 0:
            click.echo("Adding files...")
            for file in track(new_files, description="[green]Adding files"):
                self.process_file(file)

        if len(updated_files) > 0:
            click.echo("Updating files...")
            for file in track(updated_files, description="[green]Updating files"):
                path = file[2]
                identifier = file[0]
                full_path = os.path.join(self.directory, path)
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.store.update_item(
                        identifier=identifier,
                        title=self.get_file_name_from_path(path),
                        content=content,
                    )

    def identify_new_files(self):
        """
        Identify files which meet the following criteria:
        - File exists on disk but not in datastore
        """
        processable_files = self.get_all_directory_processable_files()
        db_files = [item[0] for item in self.store.get_all_titles()]

        if len(processable_files) == 0:
            return []

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
        db_files = [(item[0], item[1], item[2]) for item in self.store.get_all()]

        if len(db_files) == 0:
            return []

        deleted_files = []

        for file in db_files:
            if file[1] not in [
                self.get_file_name_from_path(f) for f in processable_files
            ]:
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
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content != file[3]:
                        updated_files.append(file)
            except FileNotFoundError:
                continue

        return updated_files

    @staticmethod
    def get_file_name_from_path(path: str) -> str:
        """
        Get the file name from a path.
        """
        return os.path.splitext(os.path.basename(path))[0]

    @staticmethod
    def get_formatted_file_path(path: str) -> str:
        """
        Get the formatted file path.
        """
        return os.path.relpath(path, os.getcwd())
