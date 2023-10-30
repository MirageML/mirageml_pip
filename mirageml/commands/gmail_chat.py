import requests
import pyperclip
import keyring
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import VSplit, Dimension, Layout
from prompt_toolkit.widgets import Box, TextArea, VerticalLine, SearchToolbar, RadioList, HorizontalLine

from rich.console import Console
from .config import load_config
from ..constants import get_headers, GMAIL_DATA_ENDPOINT, SERVICE_ID, GMAIL_THREAD_FORMAT_ENDPOINT, LLM_GPT_ENDPOINT


def worker(q):
    while True:
        item = q.get()
        if item is None: break
        thread_id, g = item
        generate_response(thread_id, g)

def llm_call(headers, user_id, model, messages, temperature):
    generated_response = requests.post(LLM_GPT_ENDPOINT, headers=headers, json={
        "user_id": user_id,
        "temperature": temperature,
        "messages": messages,
        "model": model,
    })
    generated_message = generated_response.json()
    return generated_message

def generate_response(thread_id, g):
    formatted_email_response = requests.post(GMAIL_THREAD_FORMAT_ENDPOINT, headers=g.headers, json={"thread_id": thread_id})
    formatted_email = formatted_email_response.json()
    g_messages = []
    messages = [{"role": "system", "content": 'You are an email assistant designed to help users compose emails in their own unique voice.'}, {"role": "user", "content": f"{formatted_email}"}]
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(llm_call, g.headers, g.user_id, g.model, messages, 0.8 - 0.1 * i) for i in range(3)]
        for future in futures:
            g_messages.append(future.result())

    g.third_box_text_area.text = "Generated Response. Use `1`, `2`, `3` to copy the response to your clipboard."
    g.third_box_text_area.text += "\n----------------------------------------\n"
    g.third_box_text_area.text += "\n----------------------------------------\n".join(g_messages)
    g.generated_responses = g_messages

def fetch_initial_gmail_data():
    gmail_data_response = requests.post(GMAIL_DATA_ENDPOINT, headers=get_headers(), json={"page_token": None, "query": ""})
    data = gmail_data_response.json()
    return data

class GmailChat:
    threads = []
    page_token = None
    generated_responses = []

    def __init__(self, queue, threads, page_token):
        self.queue = queue
        self.threads = threads
        self.page_token = page_token
        self.headers = get_headers()
        self.user_id = keyring.get_password(SERVICE_ID, "user_id")

        config = load_config()
        self.model = config["model"]

        self.kb = KeyBindings()

        self.kb.add("tab")(focus_next)
        self.kb.add("s-tab")(focus_previous)

        @self.kb.add("c-c")
        @self.kb.add("c-d")
        def _(event): event.app.exit()

        @self.kb.add("g")
        def _(event):
            self.third_box_text_area.text = "Generating response..."
            current_thread_id = self.radios.current_value
            self.queue.put((current_thread_id, self))

        @self.kb.add("1")
        def _(event):
            if len(self.generated_responses) > 0:
                pyperclip.copy(self.generated_responses[0])

        @self.kb.add("2")
        def _(event):
            if len(self.generated_responses) > 1:
                pyperclip.copy(self.generated_responses[1])

        @self.kb.add("3")
        def _(event):
            if len(self.generated_responses) > 2:
                pyperclip.copy(self.generated_responses[2])

        @self.kb.add("4")
        def _(event):
            if len(self.generated_responses) > 3:
                pyperclip.copy(self.generated_responses[3])

        self.create_radio(threads)
        self.create_first_box()
        self.create_second_box()
        self.create_third_box()

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
        self.second_box_text_area.text = self.fetch_thread_messages(new_threads, new_threads[0]["id"])
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
            self.second_box_text_area.text = self.fetch_thread_messages(threads, new_value)
            self.third_box_text_area.text = "Use `g` to generate a response"
            self.generated_responses = []
            self.third_box.body = self.third_box_text_area
        self.radios._handle_enter = handle_enter

    def create_first_box(self):
        self.first_box = Box(body=self.radios, padding=0, width=Dimension(weight=24), height=Dimension(weight=90))

    def create_second_box(self):
        self.second_box_text_area = TextArea(self.fetch_thread_messages(self.threads, self.threads[0]["id"]), read_only=True)
        self.second_box = Box(body=self.second_box_text_area, padding_top=0, padding_bottom=0, padding_left=1, padding_right=1, width=Dimension(weight=38), height=Dimension(weight=90))

    def create_third_box(self):
        self.third_box_text_area = TextArea("Use `g` to generate a response", read_only=True)
        self.third_box = Box(body=self.third_box_text_area, padding_top=0, padding_bottom=0, padding_left=1, padding_right=1, width=Dimension(weight=38), height=Dimension(weight=90))

    def accept(self, buff: Buffer):
        current_buff_text = buff.text
        self.fetch_gmail_data(page_token=None, query=current_buff_text)
        return False

    def create_application(self):
        top = VSplit([
                self.first_box,
                VerticalLine(),
                self.second_box,
                VerticalLine(),
                self.third_box
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

    q = queue.Queue()
    t = threading.Thread(target=worker, args=(q,))
    t.start()
    q.join()

    g = GmailChat(q, data["threads"], data["next_page_token"])
    g.create_application()
    g.app.run()

    q.put(None)
    t.join()