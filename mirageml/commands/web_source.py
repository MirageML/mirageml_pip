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

from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm.auto import tqdm
import hashlib
import json
import tiktoken
tokenizer = tiktoken.get_encoding('cl100k_base')

def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)

def process_html_files(folder_path):
    # Get all files in the folder
    all_files = os.listdir(folder_path)

    # Filter out HTML files
    html_files = [file for file in all_files if file.endswith('.html')]

    # Initialize tokenizer and text_splitter
    tokenizer = tiktoken.get_encoding('cl100k_base')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=20,
        length_function=tiktoken_len,
        separators=['\n\n', '\n', ' ', '']
    )

    documents = []

    # Process each HTML file
    for html_file in tqdm(html_files):
        try:
            file_path = os.path.join(folder_path, html_file)

            # Load the HTML content
            with open(file_path, 'r') as f:
                content = f.read()

            # Generate a unique ID based on the file path
            m = hashlib.md5()
            m.update(file_path.encode('utf-8'))
            uid = m.hexdigest()[:12]

            # Split the content into chunks
            chunks = text_splitter.split_text(content)

            # Create document data
            for i, chunk in enumerate(chunks):
                base_name = os.path.basename(file_path)
                url_with_extension = urllib.parse.unquote(base_name)
                url, extension = os.path.splitext(url_with_extension)

                documents.append({
                    'id': f'{uid}-{i}',
                    'text': chunk,
                    'source': url
                })

            # Delete the HTML file after processing
            os.remove(file_path)

        except Exception as e:
            print(f"Error processing file {html_file}: {e}")

    return documents

def get_all_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        absolute_link = urllib.parse.urljoin(url, link.get('href'))
        parsed_link = urlparse(absolute_link)
        cleaned_link = urlunparse((parsed_link.scheme, parsed_link.netloc, parsed_link.path, "", "", ""))
        if cleaned_link.startswith(url):  # Only yield child URLs
            yield cleaned_link

def download_html(url, folder):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    cleaned_html = soup.prettify()
    file_name = os.path.join(folder, urllib.parse.quote_plus(url) + '.html')
    with open(file_name, 'w') as file:
        file.write(cleaned_html)

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
        print(f"Created temporary directory: {tmp_dir}")
        while to_visit:
            current_url = to_visit.pop(0)
            if current_url not in visited_links:
                visited_links.add(current_url)
                print(f"Visiting: {current_url}")
                # download_html(current_url, tmp_dir)
                for link in get_all_links(current_url):
                    to_visit.append(link)

        loader = AsyncChromiumLoader(visited_links)
        html = loader.load()
        bs_transformer = BeautifulSoupTransformer()
        docs_transformed = bs_transformer.transform_documents(html)
        breakpoint()
        # process_html_files(tmp_dir)
        while True: continue

# Start crawling from a specific URL
crawl_website('http://modal.com/docs')


# Call the function with the folder path "websites"
# folder_path = "websites"
# documents = process_html_files(folder_path)