import os
from typing import Callable

class Walker:
    def __init__(self, dir: str) -> None:
        self.dir = dir
        pass

    def walk_files(self) -> list[str]:
        files = []
        for dirpath, _, filename in os.walk(self.dir):
            for file in filename:
                file_path = os.path.join(dirpath, file)
                files.append(file_path)
        return files
