from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

# Create custom key bindings
kb = KeyBindings()


# You can put your custom finish conditon function here
@kb.add(Keys.ControlJ)
def _(event):
    buffer = event.current_buffer
    buffer.insert_text("\n")


@kb.add(Keys.Enter)
def _(event):
    event.current_buffer.validate_and_handle()


def multiline_input(message):
    import typer

    typer.secho(
        f"{message} (Use Control+J' for newline):",
        fg=typer.colors.BRIGHT_GREEN,
        bold=True,
    )
    user_input = prompt("> ", multiline=True, key_bindings=kb)
    return user_input


# if __name__ == '__main__':
#     user_input = multiline_input("test_file")
#     print(user_input)


def interrupted(signum, frame):
    # when receive a timeout signal,
    raise Exception("end of time")


def input_or_timeout(prompt, default="no", timeout=10):
    import signal

    # set the signal function handler
    # set the alarm after timeout seconds
    signal.signal(signal.SIGALRM, interrupted)
    signal.alarm(timeout)

    try:
        answer = input(prompt)
        signal.alarm(0)
        return answer
    except Exception:
        return default
