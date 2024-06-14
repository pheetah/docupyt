import os
from typing import Optional

import typer

from client import DocupytClient, FileFormat

app = typer.Typer()

client = DocupytClient()


def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    return file_paths


@app.command()
def docupyt(path: Optional[str] = None, out_path: Optional[str] = "_outputs"):
    if not path:
        raise ValueError("Path is required")

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    formats = []

    for filepath in get_filepaths(path):
        formats.append(
            FileFormat(
                input_path=filepath,
            )
        )

    client.draw_epc(out_path=out_path, file_format=formats)


if __name__ == "__main__":
    app()
