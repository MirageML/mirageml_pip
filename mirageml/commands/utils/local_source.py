import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import typer
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern


def load_gitignore_patterns(gitignore_path):
    with open(gitignore_path, "r") as f:
        lines = f.readlines()

    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def is_ignored(path, spec):
    return spec.match_file(path)


def get_unignored_files(start_dir):
    gitignore_path = Path(start_dir) / ".gitignore"
    if not gitignore_path.exists():
        return [f for f in Path(start_dir).rglob("*") if f.is_file()]

    patterns = load_gitignore_patterns(gitignore_path)
    spec = PathSpec.from_lines(GitWildMatchPattern, patterns)

    unignored_files = []
    for root, dirs, files in os.walk(start_dir):
        # Remove dirs that are ignored to avoid traversing them
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), spec)]

        for file in files:
            filepath = os.path.join(root, file)
            if not is_ignored(filepath, spec) and not filepath.split("/")[1].startswith(".") and ".git" not in filepath:
                unignored_files.append(filepath)

    final_files = [os.path.abspath(f) for f in unignored_files]
    return final_files


def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read(), str(filepath)
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
        all_files = get_unignored_files(start_dir)

        with ThreadPoolExecutor() as executor:
            file_data = list(executor.map(read_file, all_files))

        file_data = [x for x in file_data if x is not None]

    data = [x[1] + ": " + x[0] for x in file_data]
    metadata = [dict({"data": x[0]}, **{"source": x[1]}) for x in file_data]
    return data, metadata
