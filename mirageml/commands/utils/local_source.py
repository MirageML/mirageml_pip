import os


def crawl_files(start_dir="."):
    file_data = []

    # Walk through the directory structure
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


def extract_from_file(filepath, live=None):
    from rich.panel import Panel

    if not filepath.startswith("http"):
        try:
            # Read the file content
            with open(filepath, "r", encoding="utf-8") as file:
                file_content = file.read()
                source, file_data = filepath, file_content
                if live:
                    live.update(
                        Panel(
                            f"Loaded file: {filepath}",
                            title="[bold blue]Assistant[/bold blue]",
                            border_style="blue",
                        )
                    )
            return source, file_data
        except Exception:
            if live:
                live.update(
                    Panel(
                        f"Unable to read file: {filepath}",
                        title="[bold blue]Assistant[/bold blue]",
                        border_style="blue",
                    )
                )
