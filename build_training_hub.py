#!/usr/bin/env python3
"""
Life Insurance Agent Training Hub Builder
Creates a comprehensive training workspace entirely from external content files.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from notion_client import Client

class TrainingHubBuilder:
    def __init__(self, config_path: str = "content/config.json"):
        self.content_dir = Path("content")
        self.config = self.load_config(config_path)
        
        # Initialize Notion client
        self.notion = Client(auth=self.config["notion"]["token"])
        self.parent_page_id = self.config["notion"]["parent_page_id"]
        
        # Load all schemas and data
        self.main_hub_config = self.load_json("main_hub.json")
        self.database_schemas = self.load_json("database_schemas.json")
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_json(self, filename: str) -> Dict:
        """Load JSON content from content directory"""
        file_path = self.content_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Warning: {filename} not found")
            return {}
    
    def load_markdown_file(self, filepath: str) -> Dict:
        """Load and parse markdown content with frontmatter"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_text = parts[1].strip()
                    body = parts[2].strip()
                    
                    frontmatter = {}
                    for line in frontmatter_text.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            frontmatter[key.strip()] = value.strip().strip('"')
                    
                    return {'frontmatter': frontmatter, 'body': body}
            
            return {'frontmatter': {}, 'body': content}
        except FileNotFoundError:
            print(f"⚠️  Warning: {filepath} not found")
            return {'frontmatter': {}, 'body': ''}
    
    def create_page(self, title: str, parent_id: str, icon: str = None, 
                   cover: str = None, content: List[Dict] = None) -> str:
        """Create a Notion page with properties"""
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {"title": [{"text": {"content": title}}]}
            }
        }
        
        if icon and self.config["settings"]["enable_icons"]:
            page_data["icon"] = {"emoji": icon}
        
        if cover and self.config["settings"]["enable_covers"]:
            page_data["cover"] = {"external": {"url": cover}}
        
        if content:
            max_blocks = self.config["settings"]["max_blocks_per_page"]
            page_data["children"] = content[:max_blocks]
            
        response = self.notion.pages.create(**page_data)
        return response["id"]
    
    def create_database(self, title: str, parent_id: str, properties: Dict, 
                       icon: str = None, cover: str = None) -> str:
        """Create a Notion database"""
        database_data = {
            "parent": {"page_id": parent_id},
            "title": [{"text": {"content": title}}],
            "properties": properties
        }
        
        if icon and self.config["settings"]["enable_icons"]:
            database_data["icon"] = {"emoji": icon}
        
        if cover and self.config["settings"]["enable_covers"]:
            database_data["cover"] = {"external": {"url": cover}}
            
        response = self.notion.databases.create(**database_data)
        return response["id"]
    
    def add_to_database(self, database_id: str, properties: Dict, 
                       content: List[Dict] = None, icon: str = None, 
                       cover: str = None) -> str:
        """Add entry to database"""
        page_data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        
        if icon and self.config["settings"]["enable_icons"]:
            page_data["icon"] = {"emoji": icon}
        
        if cover and self.config["settings"]["enable_covers"]:
            page_data["cover"] = {"external": {"url": cover}}
        
        if content:
            max_blocks = self.config["settings"]["max_blocks_per_page"]
            page_data["children"] = content[:max_blocks]
            
        response = self.notion.pages.create(**page_data)
        return response["id"]
    
    def parse_rich_text(self, text: str) -> List[Dict]:
        """Parse text with markdown-style formatting"""
        if not text:
            return [{"text": {"content": ""}}]
            
        rich_text = []
        parts = text.split("**")
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Regular text
                if part:
                    rich_text.append({"text": {"content": part}})
            else:  # Bold text
                if part:
                    rich_text.append({
                        "text": {"content": part},
                        "annotations": {"bold": True}
                    })
        
        return rich_text if rich_text else [{"text": {"content": text}}]
    
    def convert_content_to_blocks(self, content_items: List[Dict], 
                                 max_blocks: int = None) -> List[Dict]:
        """Convert structured content to Notion blocks"""
        if max_blocks is None:
            max_blocks = self.config["settings"]["max_blocks_per_page"]
            
        blocks = []
        
        for item in content_items:
            if len(blocks) >= max_blocks:
                break
                
            if item["type"] == "paragraph":
                text = item["text"]
                max_length = self.config["content_limits"]["max_paragraph_length"]
                if len(text) > max_length:
                    text = text[:max_length] + "..."
                    
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": self.parse_rich_text(text)
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
            
            elif item["type"] == "heading_2":
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"text": {"content": item["text"]}}]
                    }
                })
            
            elif item["type"] == "bulleted_list":
                max_items = self.config["content_limits"]["max_list_items"]
                for list_item in item["items"][:max_items]:
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
            
            elif item["type"] == "table" and not self.config["settings"]["skip_tables"]:
                # Handle tables with limits
                max_rows = self.config["content_limits"]["max_table_rows"]
                limited_rows = item["rows"][:max_rows]
                
                # Convert to bulleted list format instead of table for reliability
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": "📊 " + " | ".join(item["headers"])}}]
                    }
                })
                
                for row in limited_rows:
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
    
    def convert_markdown_to_blocks(self, markdown_content: str, 
                                  max_blocks: int = None) -> List[Dict]:
        """Convert markdown to Notion blocks"""
        if max_blocks is None:
            max_blocks = self.config["settings"]["max_blocks_per_page"]
            
        blocks = []
        lines = markdown_content.split('\n')
        
        i = 0
        while i < len(lines) and len(blocks) < max_blocks:
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Handle headings
            if line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": line[4:]}}]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"text": {"content": line[3:]}}]
                    }
                })
            # Handle callouts
            elif line.startswith('> **'):
                callout_text = line[2:]
                icon = "💡"
                if "🎯" in callout_text: icon = "🎯"
                elif "💭" in callout_text: icon = "💭"
                elif "🧠" in callout_text: icon = "🧠"
                
                blocks.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": self.parse_rich_text(callout_text),
                        "icon": {"emoji": icon}
                    }
                })
            # Handle bullet lists
            elif line.startswith('- ') or line.startswith('* '):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": self.parse_rich_text(line[2:])
                    }
                })
            # Skip tables if configured to do so
            elif '|' in line and self.config["settings"]["skip_tables"]:
                i += 1
                continue
            # Handle regular paragraphs
            else:
                paragraph_lines = [line]
                j = i + 1
                while (j < len(lines) and lines[j].strip() and 
                       not lines[j].startswith('#') and 
                       not lines[j].startswith('>') and 
                       not lines[j].startswith('-') and 
                       not lines[j].startswith('*')):
                    paragraph_lines.append(lines[j].strip())
                    j += 1
                
                paragraph_text = ' '.join(paragraph_lines)
                if paragraph_text:
                    max_length = self.config["content_limits"]["max_paragraph_length"]
                    if len(paragraph_text) > max_length:
                        paragraph_text = paragraph_text[:max_length] + "..."
                    
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": self.parse_rich_text(paragraph_text)
                        }
                    })
                
                i = j - 1
            
            i += 1
        
        return blocks
    
    def create_main_hub(self) -> str:
        """Create the main training hub page from config"""
        hub_config = self.main_hub_config
        
        content = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"text": {"content": f"{hub_config['icon']} {hub_config['title']}"}}]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"text": {"content": hub_config["description"]}}],
                    "icon": {"emoji": "💡"}
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ]
        
        # Add sections from config
        for section in hub_config["sections"]:
            content.extend([
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"text": {"content": section["title"]}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": section["description"]}}]
                    }
                }
            ])
        
        hub_id = self.create_page(
            hub_config["title"],
            self.parent_page_id,
            icon=hub_config["icon"],
            cover=hub_config["cover"],
            content=content
        )
        
        print(f"✅ Created Training Hub: {hub_id}")
        return hub_id
    
    def create_faq_database(self, parent_id: str) -> str:
        """Create FAQ database from schema and populate from file"""
        schema = self.database_schemas["faq_database"]
        
        db_id = self.create_database(
            schema["title"],
            parent_id,
            schema["properties"],
            icon=schema["icon"],
            cover=schema["cover"]
        )
        
        # Load FAQ data
        faqs = self.load_json("faqs.json")
        if isinstance(faqs, list):
            faq_data = faqs
        else:
            faq_data = [faqs] if faqs else []
        
        for faq in faq_data:
            properties = {
                "Title": {"title": [{"text": {"content": faq["title"]}}]},
                "Description": {"rich_text": [{"text": {"content": faq["description"]}}]},
                "Tags": {"multi_select": [{"name": tag} for tag in faq["tags"]]},
                "Priority": {"select": {"name": "High"}}
            }
            
            # Build content
            max_blocks = self.config["content_limits"]["max_faq_content_blocks"]
            content = [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"text": {"content": faq["title"]}}]
                    }
                },
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"text": {"content": faq["callout"]}}],
                        "icon": {"emoji": "💡"}
                    }
                }
            ]
            
            # Add rich content if available
            if "content" in faq:
                content.extend(self.convert_content_to_blocks(faq["content"], max_blocks - len(content)))
            
            # Add variations if space allows
            if len(content) < max_blocks - 5:
                content.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": "🔄 Variations of this question:"}}]
                    }
                })
                
                for variation in faq["variations"][:3]:
                    if len(content) >= max_blocks:
                        break
                    content.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": variation}}]
                        }
                    })
            
            self.add_to_database(
                db_id,
                properties,
                content,
                icon=faq.get("icon", "❓"),
                cover=faq.get("cover")
            )
            
            print(f"✅ Added FAQ: {faq['title']}")
            time.sleep(self.config["settings"]["rate_limit_delay"])
        
        return db_id
    
    def create_sales_training(self, parent_id: str) -> str:
        """Create sales training section from markdown files"""
        schema = self.database_schemas["sales_training"]
        
        # Create main training page
        main_content = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"text": {"content": f"{schema['icon']} {schema['title']}"}}]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"text": {"content": schema["description"]}}],
                    "icon": {"emoji": "🎯"}
                }
            }
        ]
        
        training_id = self.create_page(
            schema["title"],
            parent_id,
            icon=schema["icon"],
            cover=schema["cover"],
            content=main_content
        )
        
        # Load training phase files
        phase_files = [
            "intro_rapport.md",
            "needs_discovery.md",
            "product_presentation.md",
            "pricing_discussion.md",
            "closing_next_steps.md",
            "follow_up_cadence.md"
        ]
        
        for phase_file in phase_files:
            file_path = self.content_dir / "sales_call_pages" / phase_file
            page_data = self.load_markdown_file(file_path)
            
            if page_data["body"]:
                frontmatter = page_data["frontmatter"]
                max_blocks = self.config["content_limits"]["max_training_content_blocks"]
                content_blocks = self.convert_markdown_to_blocks(page_data["body"], max_blocks)
                
                page_id = self.create_page(
                    frontmatter.get("title", phase_file),
                    training_id,
                    icon=frontmatter.get("icon", "📋"),
                    cover=frontmatter.get("cover_image"),
                    content=content_blocks
                )
                print(f"✅ Created training phase: {frontmatter.get('title', phase_file)}")
        
        return training_id
    
    def create_objections_database(self, parent_id: str) -> str:
        """Create objections database from schema and file"""
        schema = self.database_schemas["objections_database"]
        
        db_id = self.create_database(
            schema["title"],
            parent_id,
            schema["properties"],
            icon=schema["icon"],
            cover=schema["cover"]
        )
        
        # Load objections data
        objections = self.load_json("objections.json")
        if isinstance(objections, list):
            objections_data = objections
        else:
            objections_data = [objections] if objections else []
        
        for objection in objections_data:
            properties = {
                "Title": {"title": [{"text": {"content": objection["title"]}}]},
                "Description": {"rich_text": [{"text": {"content": objection["description"]}}]},
                "Tags": {"multi_select": [{"name": tag} for tag in objection["tags"]]},
                "Difficulty": {"select": {"name": "Medium"}}
            }
            
            # Build content
            max_blocks = self.config["content_limits"]["max_objection_content_blocks"]
            content = [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"text": {"content": objection["title"]}}]
                    }
                },
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"text": {"content": f"What they're really saying: {objection['what_they_mean']}"}}],
                        "icon": {"emoji": "🤔"}
                    }
                }
            ]
            
            # Add content sections with limits
            if "emotional_drivers" in objection:
                content.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": "🧠 Emotional Drivers"}}]
                    }
                })
                
                max_items = self.config["content_limits"]["max_list_items"]
                for driver in objection["emotional_drivers"][:max_items]:
                    if len(content) >= max_blocks:
                        break
                    content.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": driver}}]
                        }
                    })
            
            # Add strategies
            if "rebuttal_strategies" in objection and len(content) < max_blocks - 10:
                content.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": "🛡️ Rebuttal Strategies"}}]
                    }
                })
                
                max_items = self.config["content_limits"]["max_list_items"]
                for strategy in objection["rebuttal_strategies"][:max_items]:
                    if len(content) >= max_blocks:
                        break
                    content.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": strategy}}]
                        }
                    })
            
            # Add sample responses
            if "sample_responses" in objection and len(content) < max_blocks - 5:
                content.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": "💬 Sample Responses"}}]
                    }
                })
                
                for response in objection["sample_responses"][:2]:
                    if len(content) >= max_blocks - 2:
                        break
                    content.extend([
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"text": {"content": f"**{response['situation']}:**"}, "annotations": {"bold": True}}]
                            }
                        },
                        {
                            "object": "block",
                            "type": "quote",
                            "quote": {
                                "rich_text": self.parse_rich_text(response["response"])
                            }
                        }
                    ])
            
            self.add_to_database(
                db_id,
                properties,
                content,
                icon=objection.get("icon", "🛡️"),
                cover=objection.get("cover")
            )
            
            print(f"✅ Added objection: {objection['title']}")
            time.sleep(self.config["settings"]["rate_limit_delay"])
        
        return db_id
    
    def create_scripts_database(self, parent_id: str) -> str:
        """Create scripts database from schema and file"""
        schema = self.database_schemas["scripts_database"]
        
        db_id = self.create_database(
            schema["title"],
            parent_id,
            schema["properties"],
            icon=schema["icon"],
            cover=schema["cover"]
        )
        
        # Load scripts data
        scripts = self.load_json("scripts.json")
        if isinstance(scripts, list):
            scripts_data = scripts
        else:
            scripts_data = [scripts] if scripts else []
        
        for script in scripts_data:
            properties = {
                "Title": {"title": [{"text": {"content": script["title"]}}]},
                "Description": {"rich_text": [{"text": {"content": script["description"]}}]},
                "Tags": {"multi_select": [{"name": tag} for tag in script["tags"]]},
                "Skill Level": {"select": {"name": "Beginner"}}
            }
            
            # Build content
            max_blocks = self.config["content_limits"]["max_script_content_blocks"]
            content = [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"text": {"content": script["title"]}}]
                    }
                },
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"text": {"content": f"When to use: {script['when_to_use']}"}}],
                        "icon": {"emoji": "⏰"}
                    }
                }
            ]
            
            # Add script blocks
            if "script_blocks" in script:
                content.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": "📝 Script Components"}}]
                    }
                })
                
                for block in script["script_blocks"][:3]:
                    if len(content) >= max_blocks - 5:
                        break
                    content.extend([
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"text": {"content": f"**{block['label']}:**"}, "annotations": {"bold": True}}]
                            }
                        },
                        {
                            "object": "block",
                            "type": "code",
                            "code": {
                                "rich_text": [{"text": {"content": block["content"][:1500]}}],
                                "language": "plain text"
                            }
                        }
                    ])
            
            # Add tips
            if "tips" in script and len(content) < max_blocks - 8:
                content.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"text": {"content": "💡 Tips for Success"}}]
                    }
                })
                
                max_items = self.config["content_limits"]["max_list_items"]
                for tip in script["tips"][:max_items]:
                    if len(content) >= max_blocks:
                        break
                    content.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": tip}}]
                        }
                    })
            
            self.add_to_database(
                db_id,
                properties,
                content,
                icon=script.get("icon", "📝"),
                cover=script.get("cover")
            )
            
            print(f"✅ Added script: {script['title']}")
            time.sleep(self.config["settings"]["rate_limit_delay"])
        
        return db_id
    
    def build(self):
        """Build the complete training hub from external files"""
        print("🚀 Building Life Insurance Agent Training Hub from external files...")
        
        try:
            # Create main hub
            hub_id = self.create_main_hub()
            
            # Create all components
            faq_db_id = self.create_faq_database(hub_id)
            training_id = self.create_sales_training(hub_id)
            objections_db_id = self.create_objections_database(hub_id)
            scripts_db_id = self.create_scripts_database(hub_id)
            
            print(f"\n✅ Training Hub built successfully!")
            print(f"📍 Hub ID: {hub_id}")
            print(f"📊 FAQ Database: {faq_db_id}")
            print(f"🎯 Sales Training: {training_id}")
            print(f"🛡️ Objections Database: {objections_db_id}")
            print(f"📝 Scripts Database: {scripts_db_id}")
            
            return {
                "hub_id": hub_id,
                "faq_database": faq_db_id,
                "sales_training": training_id,
                "objections_database": objections_db_id,
                "scripts_database": scripts_db_id
            }
            
        except Exception as e:
            print(f"❌ Error building training hub: {str(e)}")
            raise

if __name__ == "__main__":
    builder = TrainingHubBuilder()
    builder.build()