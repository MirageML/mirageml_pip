from prompt_toolkit.filters import in_paste_mode
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

bindings = KeyBindings()

@bindings.add(Keys.Enter, Keys.Escape)
def _(event):
    event.current_buffer.validate_and_handle()

@bindings.add(Keys.Enter)
def _(event):
    event.current_buffer.newline(copy_margin=not in_paste_mode())