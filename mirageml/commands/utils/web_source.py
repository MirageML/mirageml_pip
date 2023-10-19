import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urlparse, urlunparse
import os
import tempfile
import subprocess
import shutil
import os
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import BeautifulSoupTransformer

import typer
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import track

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.CRITICAL)
logging.disable(logging.CRITICAL)
logging.getLogger("langchain").setLevel(logging.CRITICAL)

console = Console()

def tree_to_paths(node, path=None):
    path = path or []
    for child in node.children:
        yield from tree_to_paths(child, path + [child.label])
    if path:
        yield path

def get_all_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        absolute_link = urllib.parse.urljoin(url, link.get('href'))
        parsed_link = urlparse(absolute_link)
        cleaned_link = urlunparse((parsed_link.scheme, parsed_link.netloc, parsed_link.path, "", "", ""))
        if cleaned_link.startswith(url):  # Only yield child URLs
            yield cleaned_link

def check_playwright_chromium():
    try:
        # Try to launch chromium and close immediately. This is just to check its presence.
        subprocess.run(['python3', '-m', 'playwright', 'chromium', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def crawl_website(start_url):
    if not start_url.endswith("/"): start_url += "/"
    urls = {start_url: set()}
    visited_links = set()
    to_visit = [start_url]

    # Check if playwright is installed
    if not check_playwright_chromium():
        print("Playwright Chromium required for webscraping.")
        print("Please run `python3 -m playwright install chromium`")
        return

    while to_visit:
        with Live(Panel("Preparing to Index", title="[bold green]Indexer[/bold green]", border_style="green"),
                    console=console, transient=True, auto_refresh=True, vertical_overflow="visible") as live:
            with tempfile.TemporaryDirectory() as tmp_dir:
                # print(f"Created temporary directory: {tmp_dir}")
                while to_visit:
                    current_url = to_visit.pop(0)
                    if current_url not in visited_links:
                        visited_links.add(current_url)
                        live.update(Panel(f"Indexing: {current_url}", title="[bold green]Indexer[/bold green]", border_style="green"))
                        for link in get_all_links(current_url):
                            to_visit.append(link)
        # pretty print all of the subpages that were indexed and ask the user if they want to continue
        typer.secho("These are the subpaths we visited:", fg=typer.colors.BRIGHT_GREEN, bold=True)

        # Process each link and add to tree
        for url in visited_links:
            # Check which key in urls the visited link is under
            url_key = ""
            for key in urls.keys():
                if key in url: url_key = key

            if not url_key: continue

            try:
                url = url.replace(url_key, "").split("/")[0]
                urls[url_key].add(url)
            except: continue

        # Print the results
        for domain, paths in urls.items():
            print(f"{domain}:")
            for path in sorted(paths):
                print(path)
            print()


        user_input = input("Do you want to index another URL? [yes/no] (default: no): ")
        user_input = user_input.strip()
        if user_input and not user_input.lower().startswith('n'):
            while True:
                link = input("Link for the source (exit to skip): ")
                if link.lower().strip() == 'exit': break
                elif not link.startswith("https://"):
                    typer.echo("Please enter a valid link starting with https://")
                    continue
                break
            if link.lower().strip() != 'exit':
                if not user_input.endswith("/"): user_input += "/"
                to_visit = [user_input]
                urls[user_input] = set()
            else: to_visit = []
        else:
            to_visit = []

    # with Live(progress, console=console, transient=True, auto_refresh=True, vertical_overflow="visible") as live2:
    data, metadata = [], []
    for link in track(visited_links, transient=True, description="[cyan]Scraping Pages & Cleaning HTML..."):
        loader = AsyncChromiumLoader([link])
        # live2.update(Panel("Scraping Pages...", title="[bold green]Indexer[/bold green]", border_style="green"))
        html = loader.load()
        bs_transformer = BeautifulSoupTransformer()
        # live2.update(Panel("Cleaning HTML...", title="[bold green]Indexer[/bold green]", border_style="green"))
        docs_transformed = bs_transformer.transform_documents(html)
        data.extend([x.page_content for x in docs_transformed])
        metadata.extend([dict({"data": x.page_content}, **x.metadata) for x in docs_transformed])
    return data, metadata

if __name__ == "__main__":
    import time
    start_time = time.time()
    crawl_website("https://rich.readthedocs.io/en/stable")
    print(f"Time taken: {time.time() - start_time}")