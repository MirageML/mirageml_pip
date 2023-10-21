from prompt_toolkit import prompt
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

# Create custom key bindings
kb = KeyBindings()

# You can put your custom finish conditon function here
@kb.add(Keys.Escape, Keys.Enter)
def _(event):
    buffer = event.current_buffer
    buffer.insert_text('\n')

@kb.add(Keys.Enter)
def _(event):
    event.current_buffer.validate_and_handle()

def multiline_input(message):
    import typer
    typer.secho(f'{message} (Use Option+Enter for newline):', fg=typer.colors.BRIGHT_GREEN, bold=True)
    user_input = prompt("> ", multiline=True, key_bindings=kb)
    return user_input

if __name__ == '__main__':
    user_input = multiline_input("test_file")
    print(user_input)