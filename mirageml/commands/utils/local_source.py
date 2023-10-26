import os
from concurrent.futures import ThreadPoolExecutor

import pathspec
import typer


def read_file(args):
    dirpath, filename = args
    filepath = os.path.join(dirpath, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read(), filepath
    except Exception:
        pass


def crawl_files(start_dir="."):
    file_data = []

    # Walk through the directory structure
    if os.path.isfile(start_dir):
        try:
            # Read the file content
            with open(start_dir, "r", encoding="utf-8") as file:
                file_content = file.read()
                file_data.append((file_content, start_dir))
        except Exception:
            # If unable to read a file, you can print an error or continue to the next file
            typer.secho(f"Unable to read file: {start_dir}", fg=typer.colors.BRIGHT_RED, bold=True)
            return None, None
    elif not os.path.isdir(start_dir):
        typer.secho(f"Unable to read dir: {start_dir}", fg=typer.colors.BRIGHT_RED, bold=True)
        return None, None
    else:
        # Get .gitignore file content in all directories within the root directory.
        start_dir = os.path.abspath(start_dir)
        gitignore_specs = []
        for dirpath, dirnames, filenames in os.walk(start_dir):
            if ".gitignore" in filenames:
                with open(os.path.join(dirpath, ".gitignore"), "r") as f:
                    gitignore = f.readlines()
                    # Compile the list of rules into a single PathSpec which can be called upon later
                    spec = pathspec.PathSpec.from_lines("gitwildmatch", gitignore)
                    gitignore_specs.append(spec)

        all_files = [
            (dirpath, filename)
            for dirpath, _, filenames in os.walk(start_dir)
            for filename in filenames
            if not (filename.startswith(".") or dirpath.split("/")[-1].startswith(".") or ".git" in dirpath)
            # Check the files against all gitignore rules
            and all(not spec.match_file(os.path.join(dirpath, filename)) for spec in gitignore_specs)
        ]

        with ThreadPoolExecutor() as executor:
            file_data = list(executor.map(read_file, all_files))

        file_data = [x for x in file_data if x is not None]

    data = [x[1] + ": " + x[0] for x in file_data]
    metadata = [dict({"data": x[0]}, **{"source": x[1]}) for x in file_data]
    return data, metadata
