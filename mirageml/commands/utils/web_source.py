import logging
import subprocess
import tempfile
import urllib.parse
from urllib.parse import urlparse, urlunparse

import requests
import typer
from bs4 import BeautifulSoup
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import BeautifulSoupTransformer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from .custom_inputs import input_or_timeout

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


def crawl_with_playwright(live, start_url):
    visited_links = set()
    from playwright.sync_api import sync_playwright

    def get_all_play_links(page):
        # Execute script on the page to get all links
        links = page.eval_on_selector_all(
            "a",
            """(anchors) => {
            return anchors.map(anchor => anchor.href);
        }""",
        )
        for link in links:
            parsed_link = urlparse(link)
            cleaned_link = urlunparse((parsed_link.scheme, parsed_link.netloc, parsed_link.path, "", "", ""))
            yield cleaned_link

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(start_url)
        to_visit = [start_url]

        while to_visit:
            current_url = to_visit.pop(0)
            if current_url not in visited_links:
                visited_links.add(current_url)
                live.update(
                    Panel(
                        f"Scraping: {current_url}",
                        title="[bold green]Scraper[/bold green]",
                        border_style="green",
                    )
                )
                page.goto(current_url)
                links_on_page = get_all_play_links(page)
                for link in links_on_page:
                    if link.startswith(start_url):
                        to_visit.append(link)
        browser.close()
    return visited_links


def get_all_links(base_url, url, live=None):
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        },
    )
    soup = BeautifulSoup(response.text, "html.parser")
    a_tags = soup.find_all("a")
    if a_tags:
        for link in soup.find_all("a"):
            absolute_link = urllib.parse.urljoin(url, link.get("href"))
            parsed_link = urlparse(absolute_link)
            cleaned_link = urlunparse((parsed_link.scheme, parsed_link.netloc, parsed_link.path, "", "", ""))
            if cleaned_link.startswith(base_url):  # Only yield child URLs
                if live:
                    live.update(
                        Panel(
                            f"Scraping: {cleaned_link}",
                            title="[bold green]Scraper[/bold green]",
                            border_style="green",
                        )
                    )
                yield cleaned_link
    else:
        for link in crawl_with_playwright(live, url):
            yield link


def check_playwright_chromium():
    try:
        # Try to launch chromium and close immediately. This is just to check its presence.
        subprocess.run(
            ["python3", "-m", "playwright", "chromium", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Playwright Chromium required for webscraping.")
        print("Please run `python3 -m playwright install chromium`")
        return False


def crawl_website(start_url):
    if not start_url.endswith("/"):
        start_url += "/"
    urls = {start_url: set()}
    visited_links = set()
    to_visit = [start_url]
    base_url = start_url

    # Check if playwright is installed
    if not check_playwright_chromium():
        return

    while to_visit:
        with Live(
            Panel(
                "Preparing to Scrape...",
                title="[bold green]Scraper[/bold green]",
                border_style="green",
            ),
            console=console,
            transient=True,
            auto_refresh=True,
            vertical_overflow="visible",
        ) as live:
            with tempfile.TemporaryDirectory():
                # print(f"Created temporary directory: {tmp_dir}")
                while to_visit:
                    current_url = to_visit.pop(0)
                    if current_url not in visited_links:
                        visited_links.add(current_url)
                        for link in get_all_links(base_url, current_url, live):
                            to_visit.append(link)
        # pretty print all of the subpages that were indexed and ask the user if they want to continue
        typer.secho("Subpaths Per URL:", fg=typer.colors.GREEN, bold=True)
        print()

        # Process each link and add to tree
        for url in visited_links:
            # Check which key in urls the visited link is under
            url_key = ""
            for key in urls.keys():
                if key in url:
                    url_key = key

            if not url_key:
                continue

            try:
                url = url.replace(url_key, "").split("/")[0]
                if url:
                    urls[url_key].add(url)
            except Exception:
                continue

        # Print the results
        for domain, paths in urls.items():
            typer.secho(f"{domain}:", fg=typer.colors.BRIGHT_GREEN, bold=True)
            if len(paths) == 0:
                print("No subpaths found, you may have to manually add the url when prompted.")
                print()
                continue
            for path in sorted(paths):
                print(path)
            print()

        # Will timeout if user doesn't respond within 10 seconds
        user_input = input_or_timeout(
            "Do you want to index another URL? Enter a URL or leave empty (timeout: 10s) (default: no): ",
            default="no",
        )
        user_input = user_input.strip()
        if user_input and not user_input.lower().startswith("n"):
            if user_input.lower().startswith("https://"):
                link = user_input
                if not link.endswith("/"):
                    link += "/"
                to_visit = [link]
                urls[link] = set()
                base_url = link
            else:
                while True:
                    link = input("Link for the source (exit to skip): ")
                    if link.lower().strip() == "exit":
                        break
                    elif not link.startswith("https://"):
                        typer.echo("Please enter a valid link starting with https://")
                        continue
                    break
            if link.lower().strip() != "exit":
                if not link.endswith("/"):
                    link += "/"
                to_visit = [link]
                urls[link] = set()
            else:
                to_visit = []
        else:
            to_visit = []

    data, metadata = [], []
    with Live(
        Panel(
            "Preparing to Clean",
            title="[bold green]Cleaner[/bold green]",
            border_style="green",
        ),
        console=console,
        transient=True,
        auto_refresh=True,
        vertical_overflow="visible",
    ) as live:
        for link in visited_links:
            loader = AsyncChromiumLoader([link])
            live.update(
                Panel(
                    f"Cleaning: {link}",
                    title="[bold green]Cleaner[/bold green]",
                    border_style="green",
                )
            )
            html = loader.load()
            bs_transformer = BeautifulSoupTransformer()
            docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["p", "li", "div", "a", "code"])
            data.extend([x.page_content for x in docs_transformed])
            metadata.extend([dict({"data": x.page_content}, **x.metadata) for x in docs_transformed])
    return data, metadata


def extract_from_url(url, live=None):
    try:
        if not check_playwright_chromium():
            return
        from langchain.document_loaders import AsyncChromiumLoader
        from langchain.document_transformers import BeautifulSoupTransformer

        loader = AsyncChromiumLoader([url])
        html = loader.load()
        bs_transformer = BeautifulSoupTransformer()
        docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["p", "li", "div", "a", "code"])
        source, url_data = (
            docs_transformed[0].metadata["source"],
            docs_transformed[0].page_content,
        )
        if live:
            live.update(
                Panel(
                    f"Loaded webpage: {url}",
                    title="[bold blue]Assistant[/bold blue]",
                    border_style="blue",
                )
            )
        return source, url_data
    except Exception:
        if live:
            live.update(
                Panel(
                    f"Unable to read url make sure that the url starts with http: {url}",
                    title="[bold blue]Assistant[/bold blue]",
                    border_style="blue",
                )
            )


if __name__ == "__main__":
    import time

    start_time = time.time()
    crawl_website("https://www.nysenate.gov/legislation/laws/BNK")
    print(f"Time taken: {time.time() - start_time}")
