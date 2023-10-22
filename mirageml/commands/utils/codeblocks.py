def add_indices_to_code_blocks(markdown):
    """Add indices with enhanced formatting before each code block."""
    import re

    code_blocks = re.findall(r"```(.*?)```", markdown, re.DOTALL)
    for index, block in enumerate(code_blocks, start=1):
        markdown = markdown.replace(f"```{block}```", f"\n_**Block {index}**_:\n```{block}```", 1)
    return markdown


def extract_code_from_markdown(markdown):
    """Extract code blocks from markdown without the language specifier."""
    import re

    # Capture everything between triple backticks
    code_blocks = re.findall(r"```(.*?)```", markdown, re.DOTALL)

    # Remove potential language specifiers (e.g., "python") from the start of each block
    cleaned_code_blocks = []
    for block in code_blocks:
        cleaned_block = "\n".join(block.split("\n")[1:]) if block.split("\n")[0].isalpha() else block
        cleaned_code_blocks.append(cleaned_block.strip())

    return cleaned_code_blocks


def copy_code_to_clipboard(code_blocks, selected_indices):
    import pyperclip
    import typer

    selected_code = "\n\n".join([code_blocks[i - 1] for i in selected_indices if 1 <= i <= len(code_blocks)])

    if selected_code:
        pyperclip.copy(selected_code)
        typer.secho(
            "Selected code blocks copied to clipboard!",
            fg=typer.colors.BRIGHT_GREEN,
            bold=True,
        )
