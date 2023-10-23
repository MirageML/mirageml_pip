import os
import typer


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
    elif not os.path.isdir(start_dir):
        typer.secho(f"Unable to read dir: {start_dir}", fg=typer.colors.BRIGHT_RED, bold=True)
    else:
        for dirpath, dirnames, filenames in os.walk(os.path.abspath(start_dir)):
            for filename in filenames:
                # Skip hidden files
                if filename.startswith(".") or dirpath.split("/")[-1].startswith("."):
                    continue
                filepath = os.path.join(dirpath, filename)

                try:
                    # Read the file content
                    with open(filepath, "r", encoding="utf-8") as file:
                        file_content = file.read()
                        file_data.append((file_content, filepath))
                except Exception:
                    # If unable to read a file, you can print an error or continue to the next file
                    pass

    data = [x[1] + ": " + x[0] for x in file_data]
    metadata = [dict({"data": x[0]}, **{"source": x[1]}) for x in file_data]
    return data, metadata
