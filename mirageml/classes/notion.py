import requests
from rich.progress import track

from mirageml.constants import NOTION_API_URL, NOTION_VERSION
from mirageml.commands.utils.vectordb import delete_qdrant_db, create_qdrant_db

class Notion:
    roots = []

    def __init__(self, provider_token):
        self.provider_token = provider_token
        self.headers = {
            "Authorization": f"Bearer {provider_token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        }

    def _delete_notion_collection(self):
        delete_qdrant_db("notion")

    def _fetch_blocks(self, block_id):
        cursor = None
        has_more = True
        blocks = []
        while has_more:
            endpoint = f"{NOTION_API_URL}/blocks/{block_id}/children" if not cursor else f"{NOTION_API_URL}/blocks/{block_id}/children?start_cursor={cursor}"
            response = requests.get(endpoint, headers=self.headers)
            data = response.json()
            has_more = data.get("has_more", False)
            cursor = data.get("next_cursor", None)
            blocks.extend(data["results"])
        return blocks

    def _extract_text(self, block):
        all_text = []
        if block["type"] == "bulleted_list_item" and len(block["bulleted_list_item"]["rich_text"]) > 0:
            all_text = [text["text"]["content"] for text in block["bulleted_list_item"]["rich_text"]]
        elif block["type"] == "callout" and len(block["callout"]["rich_text"]) > 0:
            all_text = [text["text"]["content"] for text in block["callout"]["rich_text"]]
        elif block["type"] == "code" and len(block["code"]["rich_text"]) > 0:
            all_text = [text["text"]["content"] for text in block["code"]["rich_text"]]
        elif block["type"] == "equation":
            all_text = [block["equation"]["expression"]]
        elif "heading" in block["type"] and len(block[block["type"]]["rich_text"]) > 0:
            all_text = [text["text"]["content"] for text in block[block["type"]]["rich_text"]]
        elif block["type"] == "numbered_list_item" and len(block["numbered_list_item"]["rich_text"]) > 0:
            all_text = [text["text"]["content"] for text in block["numbered_list_item"]["rich_text"]]
        elif block["type"] == "paragraph" and len(block["paragraph"]["rich_text"]) > 0:
            all_text = [text["text"]["content"] for text in block["paragraph"]["rich_text"]]
        elif block["type"] == "quote" and len(block["quote"]["rich_text"]) > 0:
            all_text = [text["text"]["content"] for text in block["quote"]["rich_text"]]
        elif block["type"] == "to_do" and len(block["to_do"]["rich_text"]) > 0:
            all_text = [text["text"]["content"] for text in block["to_do"]["rich_text"]]
        elif block["type"] == "toggle" and len(block["toggle"]["rich_text"]) > 0:
            all_text = [text["text"]["content"] for text in block["toggle"]["rich_text"]]
        return all_text

    def _process_block(self, block):
        content = []
        if "type" in block:
            all_text = self._extract_text(block)
            content.append(all_text)
        children = self._fetch_blocks(block["id"])
        for child in children:
            if "type" in child and child["type"] != "child_page" and child["type"] != "child_database":
                content.extend(self._process_block(child))
        return content

    def _extract_title(self, page):
        if page["object"] == "page":
            return page["properties"]["title"]["title"][0]["plain_text"] if len(page["properties"]["title"]["title"]) > 0 else ""
        elif page["object"] == "database":
            return page["title"][0]["plain_text"] if len(page["title"]) > 0 else ""

    def _process_page(self, page):
        content = self._process_block(page)
        flattened_list = [string for sublist in content for string in sublist]

        page_title = self._extract_title(page)
        flattened_list.insert(0, page_title)

        result_string = "\n".join(flattened_list)
        return result_string

    def parse_pages(self):
        has_more = True
        cursor = None
        pages = []
        page_data = []
        while has_more:
            params = { "start_cursor": cursor } if cursor else {}
            response = requests.post(f"{NOTION_API_URL}/search", json=params, headers=self.headers)
            data = response.json()
            pages.extend(data["results"])
            has_more = data.get("has_more", False)
            cursor = data.get("next_cursor", None)
        for page in track(pages, description="Processing pages..."):
            processed_page_data = self._process_page(page)
            page_data.append({
                "id": page["id"],
                "data": processed_page_data,
                "source": page["url"]
            })
        text_data = [x["data"] for x in page_data]
        create_qdrant_db(text_data, page_data, "notion")


    def sync(self):
        print("Starting notion sync...")
        self._delete_notion_collection()
        self.parse_pages()
        print("Done syncing notion")