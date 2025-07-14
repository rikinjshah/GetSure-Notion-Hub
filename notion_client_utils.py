import time
from typing import Optional, List, Dict, Any
from notion_client import Client

class NotionClientUtils:
    def __init__(self, token: str, settings: dict):
        self.notion = Client(auth=token)
        self.settings = settings

    def create_page(self, title: str, parent_id: str, icon: Optional[str] = None, cover: Optional[str] = None, content: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Create a Notion page with optional icon, cover, and content blocks.
        Returns the new page's ID.
        """
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {"title": [{"text": {"content": title}}]}
            }
        }
        if icon and self.settings.get("enable_icons", True):
            page_data["icon"] = {"emoji": icon}
        if cover and self.settings.get("enable_covers", True):
            page_data["cover"] = {"external": {"url": cover}}
        if content:
            max_blocks = self.settings.get("max_blocks_per_page", 50)
            page_data["children"] = content[:max_blocks]
        response = self.notion.pages.create(**page_data)
        return response["id"]

    def create_database(self, title: str, parent_id: str, properties: dict, icon: Optional[str] = None, cover: Optional[str] = None) -> str:
        """
        Create a Notion database with the given properties.
        Returns the new database's ID.
        """
        database_data = {
            "parent": {"page_id": parent_id},
            "title": [{"text": {"content": title}}],
            "properties": properties
        }
        if icon and self.settings.get("enable_icons", True):
            database_data["icon"] = {"emoji": icon}
        if cover and self.settings.get("enable_covers", True):
            database_data["cover"] = {"external": {"url": cover}}
        response = self.notion.databases.create(**database_data)
        return response["id"]

    def add_to_database(self, database_id: str, properties: dict, content: Optional[List[Dict[str, Any]]] = None, icon: Optional[str] = None, cover: Optional[str] = None) -> str:
        """
        Add an entry to a Notion database, with optional icon, cover, and content blocks.
        Returns the new page's ID.
        """
        page_data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        if icon and self.settings.get("enable_icons", True):
            page_data["icon"] = {"emoji": icon}
        if cover and self.settings.get("enable_covers", True):
            page_data["cover"] = {"external": {"url": cover}}
        if content:
            max_blocks = self.settings.get("max_blocks_per_page", 50)
            page_data["children"] = content[:max_blocks]
        response = self.notion.pages.create(**page_data)
        return response["id"]

    def parse_rich_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse text with markdown-style bold (**text**) into Notion rich text objects.
        """
        if not text:
            return [{"text": {"content": ""}}]
        rich_text = []
        parts = text.split("**")
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    rich_text.append({"text": {"content": part}})
            else:
                if part:
                    rich_text.append({"text": {"content": part}, "annotations": {"bold": True}})
        return rich_text if rich_text else [{"text": {"content": text}}]

    def convert_content_to_blocks(self, content_items: List[Dict[str, Any]], max_blocks: int = 50) -> List[Dict[str, Any]]:
        """
        Convert structured content (dicts) to Notion blocks.
        """
        blocks = []
        for item in content_items:
            if len(blocks) >= max_blocks:
                break
            if item["type"] == "paragraph":
                text = item["text"]
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": self.parse_rich_text(text)
                    }
                })
            elif item["type"] == "heading_2":
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"text": {"content": item["text"]}}]
                    }
                })
            elif item["type"] == "heading_3":
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": item["text"]}}]
                    }
                })
            elif item["type"] == "bulleted_list":
                for list_item in item["items"]:
                    if len(blocks) >= max_blocks:
                        break
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": self.parse_rich_text(list_item)
                        }
                    })
            elif item["type"] == "callout":
                blocks.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": self.parse_rich_text(item["text"]),
                        "icon": {"emoji": item.get("icon", "💡")}
                    }
                })
            elif item["type"] == "table":
                # For simplicity, convert table to heading + bulleted list
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": "📊 " + " | ".join(item["headers"])}}]
                    }
                })
                for row in item["rows"]:
                    if len(blocks) >= max_blocks:
                        break
                    row_text = " | ".join(str(cell) for cell in row)
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": self.parse_rich_text(row_text)
                        }
                    })
        return blocks