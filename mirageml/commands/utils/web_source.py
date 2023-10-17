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

import logging
logging.basicConfig(level=logging.WARNING)

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
        subprocess.run(['playwright', 'chromium', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def crawl_website(start_url):
    visited_links = set()
    to_visit = [start_url]

    # Check if playwright is installed
    if not check_playwright_chromium():
        print("Playwright Chromium required for webscraping.")
        print("Please run `python3 -m playwright install chromium`")
        return
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # print(f"Created temporary directory: {tmp_dir}")
        while to_visit:
            current_url = to_visit.pop(0)
            if current_url not in visited_links:
                visited_links.add(current_url)
                print(f"Indexing: {current_url}")
                for link in get_all_links(current_url):
                    to_visit.append(link)

        loader = AsyncChromiumLoader(visited_links)
        html = loader.load()
        bs_transformer = BeautifulSoupTransformer()
        docs_transformed = bs_transformer.transform_documents(html)
        data = [x.page_content for x in docs_transformed]
        metadata = [dict({"data": x.page_content}, **x.metadata) for x in docs_transformed]
        return data, metadata
