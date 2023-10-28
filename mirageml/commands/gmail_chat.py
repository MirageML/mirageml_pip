import requests
import pyperclip
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import VSplit, HSplit, Dimension, Layout, ScrollablePane
from prompt_toolkit.widgets import Label, Box, Frame, TextArea, HorizontalLine, VerticalLine, SearchToolbar, RadioList

from rich.console import Console
from ..constants import get_headers, GMAIL_DATA_ENDPOINT

def fetch_initial_gmail_data():
    gmail_data_response = requests.post(GMAIL_DATA_ENDPOINT, headers=get_headers(), json={"page_token": None, "query": ""})
    data = gmail_data_response.json()
    return data

class GmailChat:
    threads = []
    page_token = None
    def __init__(self, threads, page_token):
        self.threads = threads
        self.page_token = page_token

        self.kb = KeyBindings()

        self.kb.add("tab")(focus_next)
        self.kb.add("s-tab")(focus_previous)

        @self.kb.add("c-c")
        @self.kb.add("c-d")
        def _(event): event.app.exit()

        @self.kb.add("g")
        def _(event):
            pass

        @self.kb.add("c")
        def _(event):
            pyperclip.copy(self.text_area.text)

        self.create_radio(threads)
        self.create_left_box()
        self.create_right_box()

    def fetch_gmail_data(self, page_token=None, query=""):
        gmail_data_response = requests.post(GMAIL_DATA_ENDPOINT, headers=get_headers(), json={"page_token": page_token, query: query})
        data = gmail_data_response.json()
        self.threads = data["threads"]
        self.page_token = data["next_page_token"]
        self.update_data(data["threads"])

    def fetch_thread_messages(self, threads, thread_id):
        thread = list(filter(lambda x: x["id"] == thread_id, threads))[0]
        return thread["text"]

    def update_data(self, new_threads):
        filtered_threads = list(filter(lambda x: len(x["messages"]) > 0, new_threads))
        radio_values = [(thread["id"], thread["messages"][0]["subject"]) for thread in filtered_threads]
        self.radios.values = radio_values
        self.radios.current_values = radio_values
        self.radios.current_value = radio_values[0][0]
        self.text_area.text = self.fetch_thread_messages(new_threads, new_threads[0]["id"])
        self.app.invalidate()

    def create_radio(self, threads):
        filtered_threads = list(filter(lambda x: len(x["messages"]) > 0, threads))
        radio_values = [(thread["id"], thread["messages"][0]["subject"]) for thread in filtered_threads]
        self.radios = RadioList(values=radio_values)
        self.radios.open_character = "["
        self.radios.close_character = "]"
        self.radios.show_scrollbar = False
        def handle_enter():
            new_value = self.radios.values[self.radios._selected_index][0]
            self.radios.current_value = new_value
            self.text_area.text = self.fetch_thread_messages(threads, new_value)
        self.radios._handle_enter = handle_enter

    def create_left_box(self):
        self.left_box = Box(body=self.radios, padding=0, width=Dimension(weight=33), height=Dimension(weight=90))

    def create_right_box(self):
        self.text_area = TextArea(self.fetch_thread_messages(self.threads, self.threads[0]["id"]), read_only=True)
        self.right_box = Box(body=self.text_area, padding_left=1, padding_right=1, width=Dimension(weight=66), height=Dimension(weight=90))

    def accept(self, buff: Buffer):
        current_buff_text = buff.text
        self.fetch_gmail_data(page_token=None, query=current_buff_text)
        return False

    def create_application(self):
        top = VSplit([
                self.left_box,
                VerticalLine(),
                self.right_box
            ])
        search_field = SearchToolbar()
        input_field = TextArea(
            height=1,
            prompt="Search: ",
            multiline=False,
            wrap_lines=False,
            search_field=search_field,
        )
        input_field.accept_handler = self.accept

        # container = HSplit([
        #     top,
        #     HorizontalLine(),
        #     input_field,
        # ])
        self.app = Application(layout=Layout(top), full_screen=True, key_bindings=self.kb)

    def get_application(self):
        return self.app

def gmail_chat():
    data = {}
    console = Console()
    with console.status("[blue]Loading Gmail data...[/blue]", spinner="dots", spinner_style="blue"):
        data = fetch_initial_gmail_data()

    g = GmailChat(data["threads"], data["next_page_token"])
    g.create_application()
    g.app.run()