"""
A module dedicated to utilities around walking directories.
"""
import os


class Walker:
    """
    A class for handling walking tasks.
    """

    def __init__(self, directory: str) -> None:
        self.directory = directory

    def walk_files(self) -> list[str]:
        """
        Returns all of the files in a given directory as a list.
        """
        files = []
        for dirpath, _, filename in os.walk(self.directory):
            for file in filename:
                file_path = os.path.join(dirpath, file)
                files.append(file_path)
        return files
