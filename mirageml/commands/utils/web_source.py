import json

import requests
import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel

from ...constants import WEB_SCRAPE_EXTRACT_ENDPOINT, WEB_SCRAPE_LINKS_ENDPOINT, get_headers
from .custom_inputs import input_or_timeout

console = Console()


def validate_all_scraped(visited_links, urls):
    # pretty print all of the subpages that were indexed and ask the user if they want to continue
    typer.secho("Subpaths Per URL:", fg=typer.colors.GREEN, bold=True)
    print()

    # Process each link and add to tree
    for url in visited_links:
        # Find the key in urls that the visited link is under
        url_key = next((key for key in urls.keys() if key in url), None)

        if url_key:
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
            print("No subpaths found, you may have to manually add the url when prompted.\n")
            continue
        for path in sorted(paths):
            print(path)
        print()

    # Will timeout if user doesn't respond within 10 seconds
    user_input = input_or_timeout(
        "Do you want to index another URL? Enter a URL or leave empty (timeout: 10s) (default: no): ",
        default="no",
        timeout=10,
    )
    user_input = user_input.strip()
    if user_input and not user_input.lower().startswith("n"):
        link = (
            user_input if user_input.lower().startswith("https://") else input("Link for the source (exit to skip): ")
        )

        while not link.lower().startswith("https://") and link.lower().strip() != "exit":
            link = input("Please enter a valid link starting with https:// or type 'exit' to skip: ")

        to_visit = [link + "/" if not link.endswith("/") else link] if link.lower().strip() != "exit" else []
        if to_visit:
            urls[to_visit[0]] = set()
            start_url = to_visit[0]
    else:
        to_visit = []
        start_url = ""
    return start_url, to_visit, urls


def crawl_website(start_url):
    if not start_url.endswith("/"):
        start_url += "/"
    urls = {start_url: set()}
    visited_links = set()
    to_visit = [start_url]

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
            response = requests.post(
                WEB_SCRAPE_LINKS_ENDPOINT, json={"urls": [start_url]}, headers=get_headers(), stream=True
            )
            if response.status_code == 200:
                for chunk in response.iter_lines():
                    # process line here
                    link = chunk.decode("utf-8")
                    if live:
                        live.update(
                            Panel(
                                f"Scraping: {link}",
                                title="[bold green]Scraper[/bold green]",
                                border_style="green",
                            )
                        )
                    visited_links.add(link.strip())

        # Skip for now, assume that the scraper can find all paths
        # start_url, to_visit, urls = validate_all_scraped(visited_links, urls)
        start_url, to_visit, urls = "", [], urls

    data, metadata = [], []
    with Live(
        Panel(
            "Preparing to Clean...",
            title="[bold green]Cleaner[/bold green]",
            border_style="green",
        ),
        console=console,
        transient=True,
        auto_refresh=True,
        vertical_overflow="visible",
    ) as live:
        response = requests.post(
            WEB_SCRAPE_EXTRACT_ENDPOINT, json={"urls": list(visited_links)}, headers=get_headers(), stream=True
        )
        if response.status_code == 200:
            for chunk in response.iter_lines():
                # process line here
                decoded_chunk = chunk.decode("utf-8")
                json_data = json.loads(decoded_chunk)

                source = json_data["source"]
                data.extend([json_data["data"]])
                metadata.extend([json_data["metadata"]])

                if live:
                    live.update(
                        Panel(
                            f"Cleaning: {source}",
                            title="[bold green]Cleaner[/bold green]",
                            border_style="green",
                        )
                    )

    return data, metadata


def extract_from_url(url, live=None):
    if live:
        live.update(
            Panel(
                f"Loading: {url}",
                title="[bold blue]Assistant[/bold blue]",
                border_style="blue",
            )
        )

    response = requests.post(WEB_SCRAPE_EXTRACT_ENDPOINT, json={"urls": [url]}, headers=get_headers())
    json_data = response.json()

    source, url_data = (
        json_data["source"],
        json_data["data"],
    )
    data = [url_data]
    metadata = [{"data": url_data, "source": source}]

    return data, metadata


if __name__ == "__main__":
    import time

    start_time = time.time()
    crawl_website("https://modal.com/docs/guide/")
    print(f"Time taken: {time.time() - start_time}")
