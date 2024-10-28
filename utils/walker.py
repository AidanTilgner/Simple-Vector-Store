"""
A module dedicated to utilities around walking directories.
"""

import os


class Walker:
    """
    A class for handling walking tasks.
    """

    directory: str
    followLinks: bool

    def __init__(self, directory: str, followLinks=True) -> None:
        self.directory = directory
        self.followLinks = followLinks

    def walk_files(self) -> list[str]:
        """
        Returns all of the files in a given directory as a list.
        """
        try:
            files = []
            for dirpath, _, filename in os.walk(
                top=self.directory, followlinks=self.followLinks
            ):
                for file in filename:
                    file_path = os.path.join(dirpath, file)
                    files.append(file_path)
            return files
        except Exception as e:
            print(f"Error walking directory: {e}")
            raise e
