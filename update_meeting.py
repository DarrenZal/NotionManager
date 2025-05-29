#!/usr/bin/env python3
"""
Update Meeting Script - Updates an existing Notion meeting page with transcript processing
"""

import os
import sys
import re
import glob
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from transcript_processor import TranscriptProcessor
from notion_manager import NotionManager

# Load environment variables
load_dotenv()

def extract_page_id_from_url(url: str) -> Optional[str]:
    """
    Extract the page ID from a Notion URL.
    
    Args:
        url: Notion page URL
        
    Returns:
        Page ID or None if not found
    """
    # Pattern for URLs like:
    # https://www.notion.so/Page-Title-{page_id}?p={page_id}&pm=c
    # or
    # https://www.notion.so/Page-Title-2028b92ddc2f811ca933e7be5a1e00ee
    
    patterns = [
        # URL with ?p= parameter
        r'[?&]p=([a-f0-9]{32})',
        # URL with page ID at the end
        r'/([a-f0-9]{32})(?:\?|$)',
        # URL with dashed page ID
        r'-([a-f0-9]{8}[a-f0-9]{4}[a-f0-9]{4}[a-f0-9]{4}[a-f0-9]{12})(?:\?|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            page_id = match.group(1)
            # Remove dashes if present and format properly
            page_id = page_id.replace('-', '')
            # Insert dashes in the correct positions for Notion API
            formatted_id = f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
            return formatted_id
    
    return None

def find_transcript_file(transcript_dir: str = "./transcript", specific_file: Optional[str] = None) -> Optional[str]:
    """
    Find a transcript file in the transcript directory.
    
    Args:
        transcript_dir: Directory containing transcript files
        specific_file: Specific filename to use (optional)
        
    Returns:
        Path to transcript file or None if not found
    """
    from datetime import datetime
    
    if not os.path.exists(transcript_dir):
        print(f"❌ Transcript directory not found: {transcript_dir}")
        return None
    
    # Look for .txt files
    txt_files = glob.glob(os.path.join(transcript_dir, "*.txt"))
    
    if not txt_files:
        print(f"❌ No .txt files found in {transcript_dir}")
        return None
    
    # If specific file requested, try to find it
    if specific_file:
        specific_path = os.path.join(transcript_dir, specific_file)
        if os.path.exists(specific_path):
            print(f"📄 Using specified transcript file: {specific_path}")
            return specific_path
        else:
            print(f"❌ Specified file not found: {specific_path}")
            return None
    
    # If multiple files, let user choose
    if len(txt_files) > 1:
        print(f"\n📁 Found {len(txt_files)} transcript files:")
        for i, file_path in enumerate(txt_files, 1):
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            mod_time = os.path.getmtime(file_path)
            mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M')
            print(f"  {i}. {filename} ({file_size:,} bytes, modified: {mod_date})")
        
        while True:
            try:
                choice = input(f"\nSelect a file (1-{len(txt_files)}): ").strip()
                if choice.lower() in ['q', 'quit', 'exit']:
                    print("❌ Operation cancelled")
                    return None
                
                file_index = int(choice) - 1
                if 0 <= file_index < len(txt_files):
                    selected_file = txt_files[file_index]
                    print(f"📄 Selected transcript file: {selected_file}")
                    return selected_file
                else:
                    print(f"❌ Invalid choice. Please enter a number between 1 and {len(txt_files)}")
            except ValueError:
                print("❌ Invalid input. Please enter a number or 'q' to quit")
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled")
                return None
    
    # Only one file, use it
    selected_file = txt_files[0]
    print(f"📄 Found transcript file: {selected_file}")
    return selected_file

def read_transcript_file(file_path: str) -> Optional[str]:
    """
    Read the transcript content from file.
    
    Args:
        file_path: Path to transcript file
        
    Returns:
        Transcript content or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print(f"❌ Transcript file is empty: {file_path}")
            return None
        
        print(f"✅ Read transcript ({len(content)} characters)")
        return content
    
    except Exception as e:
        print(f"❌ Error reading transcript file: {e}")
        return None

def upload_file_to_notion(page_id: str, file_path: str) -> bool:
    """
    Upload a file to a Notion page's Files & media property.
    
    Args:
        page_id: Notion page ID
        file_path: Path to the file to upload
        
    Returns:
        True if successful, False otherwise
    """
    notion_token = os.getenv('NOTION_TOKEN')
    if not notion_token:
        print("❌ NOTION_TOKEN not found in environment")
        return False
    
    import requests
    import json
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # First, get the page to find the Files & media property
        page_url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()
        page_data = response.json()
        
        properties = page_data.get('properties', {})
        files_property = None
        
        # Look for Files & media property
        for prop_name, prop_data in properties.items():
            if prop_data.get('type') == 'files':
                files_property = prop_name
                break
        
        if not files_property:
            print("⚠️  No 'Files & media' property found on the page")
            print("Available properties:", list(properties.keys()))
            return False
        
        # Upload the file
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'text/plain')
            }
            
            # Upload to Notion's file storage
            upload_headers = {
                "Authorization": f"Bearer {notion_token}",
                "Notion-Version": "2022-06-28"
            }
            
            # Note: Notion API doesn't support direct file uploads to pages
            # We'll need to use a different approach
            print("ℹ️  File upload to Notion requires manual attachment")
            print(f"📎 Please manually attach the transcript file: {file_path}")
            print(f"📎 File name: {os.path.basename(file_path)}")
            return True
            
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return False

def create_rich_text_with_entity_links(text: str) -> list:
    """
    Create rich text array with people and project names linked to their Notion pages.
    
    Args:
        text: Text content that may contain people and project names
        
    Returns:
        List of rich text objects with linked entity names
    """
    notion_token = os.getenv('NOTION_TOKEN')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    projects_db_id = os.getenv('PROJECTS_DATABASE_ID')
    
    if not notion_token:
        # No token, return plain text
        return [{"type": "text", "text": {"content": text}}]
    
    # Get all entities (people and projects)
    entities = []
    
    # Add people
    if people_db_id:
        people_names = get_all_people_names()
        for name in people_names:
            entities.append({
                'name': name,
                'type': 'person',
                'variations': [name, f"{name} project"]  # Include "Name project" variation
            })
    
    # Add projects
    if projects_db_id:
        project_names = get_all_project_names()
        for name in project_names:
            entities.append({
                'name': name,
                'type': 'project',
                'variations': [name, f"{name} project", f"the {name} project"]
            })
    
    if not entities:
        return [{"type": "text", "text": {"content": text}}]
    
    # Sort entities by length (longest first) to avoid partial matches
    all_variations = []
    for entity in entities:
        for variation in entity['variations']:
            all_variations.append({
                'text': variation,
                'entity': entity
            })
    
    all_variations.sort(key=lambda x: len(x['text']), reverse=True)
    
    rich_text_parts = []
    remaining_text = text
    
    while remaining_text:
        # Find the earliest mention of any entity
        earliest_match = None
        earliest_pos = len(remaining_text)
        
        for variation in all_variations:
            # Look for case-insensitive matches
            import re
            pattern = re.compile(re.escape(variation['text']), re.IGNORECASE)
            match = pattern.search(remaining_text)
            
            if match and match.start() < earliest_pos:
                earliest_pos = match.start()
                earliest_match = {
                    'entity': variation['entity'],
                    'start': match.start(),
                    'end': match.end(),
                    'matched_text': match.group()
                }
        
        if earliest_match:
            # Add text before the entity name
            if earliest_match['start'] > 0:
                rich_text_parts.append({
                    "type": "text",
                    "text": {"content": remaining_text[:earliest_match['start']]}
                })
            
            # Add the linked entity name
            entity = earliest_match['entity']
            if entity['type'] == 'person':
                entity_link = get_person_link(entity['name'])
            else:  # project
                entity_link = get_project_link(entity['name'])
            
            if entity_link:
                rich_text_parts.append({
                    "type": "text",
                    "text": {
                        "content": earliest_match['matched_text'],
                        "link": {"url": entity_link}
                    }
                })
            else:
                rich_text_parts.append({
                    "type": "text",
                    "text": {"content": earliest_match['matched_text']}
                })
            
            # Continue with remaining text
            remaining_text = remaining_text[earliest_match['end']:]
        else:
            # No more entities found, add remaining text
            rich_text_parts.append({
                "type": "text",
                "text": {"content": remaining_text}
            })
            break
    
    return rich_text_parts

def create_rich_text_with_people_links(text: str) -> list:
    """
    Create rich text array with people names linked to their Notion pages.
    
    Args:
        text: Text content that may contain people names
        
    Returns:
        List of rich text objects with linked people names
    """
    notion_token = os.getenv('NOTION_TOKEN')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    
    if not notion_token or not people_db_id:
        # No people database, return plain text
        return [{"type": "text", "text": {"content": text}}]
    
    # Get all people from database
    people_names = get_all_people_names()
    if not people_names:
        return [{"type": "text", "text": {"content": text}}]
    
    # Sort people names by length (longest first) to avoid partial matches
    people_names.sort(key=len, reverse=True)
    
    rich_text_parts = []
    remaining_text = text
    
    while remaining_text:
        # Find the earliest mention of any person
        earliest_match = None
        earliest_pos = len(remaining_text)
        
        for person_name in people_names:
            # Look for case-insensitive matches
            import re
            pattern = re.compile(re.escape(person_name), re.IGNORECASE)
            match = pattern.search(remaining_text)
            
            if match and match.start() < earliest_pos:
                earliest_pos = match.start()
                earliest_match = {
                    'name': person_name,
                    'start': match.start(),
                    'end': match.end(),
                    'matched_text': match.group()
                }
        
        if earliest_match:
            # Add text before the person name
            if earliest_match['start'] > 0:
                rich_text_parts.append({
                    "type": "text",
                    "text": {"content": remaining_text[:earliest_match['start']]}
                })
            
            # Add the linked person name
            person_link = get_person_link(earliest_match['name'])
            if person_link:
                rich_text_parts.append({
                    "type": "text",
                    "text": {
                        "content": earliest_match['matched_text'],
                        "link": {"url": person_link}
                    }
                })
            else:
                rich_text_parts.append({
                    "type": "text",
                    "text": {"content": earliest_match['matched_text']}
                })
            
            # Continue with remaining text
            remaining_text = remaining_text[earliest_match['end']:]
        else:
            # No more people found, add remaining text
            rich_text_parts.append({
                "type": "text",
                "text": {"content": remaining_text}
            })
            break
    
    return rich_text_parts

def get_all_people_names() -> list:
    """
    Get all people names from the People database.
    
    Returns:
        List of people names
    """
    notion_token = os.getenv('NOTION_TOKEN')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    
    if not notion_token or not people_db_id:
        return []
    
    import requests
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Query the People database
        url = f"https://api.notion.com/v1/databases/{people_db_id}/query"
        response = requests.post(url, headers=headers, json={})
        response.raise_for_status()
        
        people_data = response.json()
        people_names = []
        
        for person in people_data.get('results', []):
            # Get the person's name
            name_prop = person.get('properties', {}).get('Name', {})
            if name_prop.get('title'):
                person_name = name_prop['title'][0]['text']['content']
                people_names.append(person_name)
        
        return people_names
        
    except Exception as e:
        print(f"⚠️  Error fetching people names: {e}")
        return []

def get_all_project_names() -> list:
    """
    Get all project names from the Projects database.
    
    Returns:
        List of project names
    """
    notion_token = os.getenv('NOTION_TOKEN')
    projects_db_id = os.getenv('PROJECTS_DATABASE_ID')
    
    if not notion_token or not projects_db_id:
        return []
    
    import requests
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Query the Projects database
        url = f"https://api.notion.com/v1/databases/{projects_db_id}/query"
        response = requests.post(url, headers=headers, json={})
        response.raise_for_status()
        
        projects_data = response.json()
        project_names = []
        
        for project in projects_data.get('results', []):
            # Get the project's name (try different property names)
            name_prop = None
            properties = project.get('properties', {})
            
            # Try common property names for project titles
            for prop_name in ['Name', 'Title', 'Project Name', 'Project']:
                if prop_name in properties:
                    name_prop = properties[prop_name]
                    break
            
            if name_prop and name_prop.get('title'):
                project_name = name_prop['title'][0]['text']['content']
                project_names.append(project_name)
        
        return project_names
        
    except Exception as e:
        print(f"⚠️  Error fetching project names: {e}")
        return []

def get_project_link(project_name: str) -> Optional[str]:
    """
    Get the Notion page URL for a project based on its name.
    
    Args:
        project_name: Name of the project to find
        
    Returns:
        Notion page URL or None if not found
    """
    notion_token = os.getenv('NOTION_TOKEN')
    projects_db_id = os.getenv('PROJECTS_DATABASE_ID')
    
    if not notion_token or not projects_db_id:
        return None
    
    import requests
    from difflib import SequenceMatcher
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Query the Projects database
        url = f"https://api.notion.com/v1/databases/{projects_db_id}/query"
        response = requests.post(url, headers=headers, json={})
        response.raise_for_status()
        
        projects_data = response.json()
        best_match = None
        best_score = 0.0
        
        for project in projects_data.get('results', []):
            # Get the project's name
            name_prop = None
            properties = project.get('properties', {})
            
            # Try common property names for project titles
            for prop_name in ['Name', 'Title', 'Project Name', 'Project']:
                if prop_name in properties:
                    name_prop = properties[prop_name]
                    break
            
            if not name_prop or not name_prop.get('title'):
                continue
            
            project_title = name_prop['title'][0]['text']['content']
            
            # Calculate similarity
            score = SequenceMatcher(None, project_name.lower(), project_title.lower()).ratio()
            
            if score > best_score and score >= 0.8:  # 80% similarity threshold
                best_score = score
                best_match = project
        
        if best_match:
            # Return the Notion page URL
            page_id = best_match['id']
            return f"https://www.notion.so/{page_id.replace('-', '')}"
        
        return None
        
    except Exception as e:
        print(f"⚠️  Error looking up project link for {project_name}: {e}")
        return None

def get_person_link(attendee_name: str) -> Optional[str]:
    """
    Get the Notion page URL for a person based on their name.
    
    Args:
        attendee_name: Name of the person to find
        
    Returns:
        Notion page URL or None if not found
    """
    notion_token = os.getenv('NOTION_TOKEN')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    
    if not notion_token or not people_db_id:
        return None
    
    import requests
    from difflib import SequenceMatcher
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        # Query the People database
        url = f"https://api.notion.com/v1/databases/{people_db_id}/query"
        response = requests.post(url, headers=headers, json={})
        response.raise_for_status()
        
        people_data = response.json()
        best_match = None
        best_score = 0.0
        
        for person in people_data.get('results', []):
            # Get the person's name
            name_prop = person.get('properties', {}).get('Name', {})
            if not name_prop.get('title'):
                continue
            
            person_name = name_prop['title'][0]['text']['content']
            
            # Calculate similarity
            score = SequenceMatcher(None, attendee_name.lower(), person_name.lower()).ratio()
            
            if score > best_score and score >= 0.8:  # 80% similarity threshold
                best_score = score
                best_match = person
        
        if best_match:
            # Return the Notion page URL
            page_id = best_match['id']
            return f"https://www.notion.so/{page_id.replace('-', '')}"
        
        return None
        
    except Exception as e:
        print(f"⚠️  Error looking up person link for {attendee_name}: {e}")
        return None

def add_blocks_to_notion_page(page_id: str, extracted_data: Dict[str, Any]) -> bool:
    """
    Add AI-processed content as blocks to a Notion page.
    
    Args:
        page_id: Notion page ID
        extracted_data: Processed data from transcript
        
    Returns:
        True if successful, False otherwise
    """
    notion_token = os.getenv('NOTION_TOKEN')
    if not notion_token:
        print("❌ NOTION_TOKEN not found in environment")
        return False
    
    import requests
    import json
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Create blocks for the content
    blocks = []
    
    # Add separator
    blocks.append({
        "object": "block",
        "type": "divider",
        "divider": {}
    })
    
    # Add header
    blocks.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "AI-Processed Meeting Summary"}
            }]
        }
    })
    
    # Add attendees with links
    attendees = extracted_data.get('attendees', [])
    if attendees:
        # Create rich text with linked attendees
        attendee_rich_text = [{"type": "text", "text": {"content": "**Attendees:** "}}]
        
        for i, attendee in enumerate(attendees):
            if i > 0:
                attendee_rich_text.append({"type": "text", "text": {"content": ", "}})
            
            # Try to find person page and create link
            person_link = get_person_link(attendee)
            if person_link:
                attendee_rich_text.append({
                    "type": "text",
                    "text": {"content": attendee, "link": {"url": person_link}}
                })
            else:
                attendee_rich_text.append({"type": "text", "text": {"content": attendee}})
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": attendee_rich_text
            }
        })
    
    # Add summary
    summary = extracted_data.get('summary', '')
    if summary:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "Summary"}
                }]
            }
        })
        
        # Split summary into chunks if too long and add entity links
        summary_chunks = [summary[i:i+2000] for i in range(0, len(summary), 2000)]
        for chunk in summary_chunks:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": create_rich_text_with_entity_links(chunk)
                }
            })
    
    # Add key decisions
    decisions = extracted_data.get('key_decisions', [])
    if decisions:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "Key Decisions"}
                }]
            }
        })
        
        for decision in decisions:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": decision}
                    }]
                }
            })
    
    # Add action items
    action_items = extracted_data.get('action_items', [])
    if action_items:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "Action Items"}
                }]
            }
        })
        
        for item in action_items:
            task = item.get('task', '')
            assignee = item.get('assignee', '')
            due_date = item.get('due_date', '')
            
            # Build rich text with people links
            rich_text_parts = []
            
            # Add task text with potential people links
            rich_text_parts.extend(create_rich_text_with_people_links(task))
            
            # Add assignee with link if present
            if assignee:
                rich_text_parts.append({"type": "text", "text": {"content": " (Assigned to: "}})
                rich_text_parts.extend(create_rich_text_with_people_links(assignee))
                rich_text_parts.append({"type": "text", "text": {"content": ")"}})
            
            # Add due date
            if due_date:
                rich_text_parts.append({"type": "text", "text": {"content": f" (Due: {due_date})"}})
            
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": rich_text_parts
                }
            })
    
    # Add next steps
    next_steps = extracted_data.get('next_steps', [])
    if next_steps:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "Next Steps"}
                }]
            }
        })
        
        for step in next_steps:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": step}
                    }]
                }
            })
    
    # Add note about transcript file
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "Original Transcript"}
            }]
        }
    })
    
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "See attached transcript file for full meeting recording."}
            }]
        }
    })
    
    # Add blocks to the page (in chunks of 100 - Notion's limit)
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    
    try:
        # Split blocks into chunks of 100
        chunk_size = 100
        for i in range(0, len(blocks), chunk_size):
            chunk = blocks[i:i+chunk_size]
            
            data = {
                "children": chunk
            }
            
            response = requests.patch(url, headers=headers, json=data)
            response.raise_for_status()
            
            print(f"✅ Added {len(chunk)} blocks to page (chunk {i//chunk_size + 1})")
        
        print(f"✅ Successfully added all {len(blocks)} blocks to page")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error adding blocks to Notion page: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                print(f"Error details: {json.dumps(error_details, indent=2)}")
            except:
                print(f"Response text: {e.response.text}")
        return False

def update_notion_page(page_id: str, extracted_data: Dict[str, Any], original_transcript: str) -> bool:
    """
    Update the Notion page with processed transcript data.
    
    Args:
        page_id: Notion page ID
        extracted_data: Processed data from transcript
        original_transcript: Original transcript text
        
    Returns:
        True if successful, False otherwise
    """
    notion_token = os.getenv('NOTION_TOKEN')
    if not notion_token:
        print("❌ NOTION_TOKEN not found in environment")
        return False
    
    import requests
    import json
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Format the content
    content_parts = []
    
    # Add attendees
    attendees = extracted_data.get('attendees', [])
    if attendees:
        content_parts.append(f"**Attendees:** {', '.join(attendees)}")
    
    # Add summary
    summary = extracted_data.get('summary', '')
    if summary:
        content_parts.append(f"## Summary\n{summary}")
    
    # Add key decisions
    decisions = extracted_data.get('key_decisions', [])
    if decisions:
        decisions_text = '\n'.join([f"• {decision}" for decision in decisions])
        content_parts.append(f"## Key Decisions\n{decisions_text}")
    
    # Add action items
    action_items = extracted_data.get('action_items', [])
    if action_items:
        action_text = []
        for item in action_items:
            task = item.get('task', '')
            assignee = item.get('assignee', '')
            due_date = item.get('due_date', '')
            
            item_text = f"• {task}"
            if assignee:
                item_text += f" (Assigned to: {assignee})"
            if due_date:
                item_text += f" (Due: {due_date})"
            
            action_text.append(item_text)
        
        content_parts.append(f"## Action Items\n" + '\n'.join(action_text))
    
    # Add next steps
    next_steps = extracted_data.get('next_steps', [])
    if next_steps:
        steps_text = '\n'.join([f"• {step}" for step in next_steps])
        content_parts.append(f"## Next Steps\n{steps_text}")
    
    # Note about transcript file attachment
    content_parts.append(f"## Original Transcript\nSee attached transcript file for full meeting recording.")
    
    formatted_content = '\n\n'.join(content_parts)
    
    # Update the page content
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    # First, get the current page to understand its structure
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        page_data = response.json()
        
        # Update the Text property if it exists
        properties = page_data.get('properties', {})
        
        # Look for a text property to update
        text_property = None
        for prop_name, prop_data in properties.items():
            if prop_data.get('type') == 'rich_text':
                text_property = prop_name
                break
        
        if text_property:
            # Get existing content first
            existing_content = ""
            existing_rich_text = properties[text_property].get('rich_text', [])
            
            if existing_rich_text:
                # Concatenate existing text content
                existing_parts = []
                for text_obj in existing_rich_text:
                    if text_obj.get('text', {}).get('content'):
                        existing_parts.append(text_obj['text']['content'])
                existing_content = ''.join(existing_parts)
            
            # Combine existing content with new AI-processed content
            if existing_content.strip():
                # Add separator and new content
                combined_content = existing_content + "\n\n" + "="*50 + "\n" + "# AI-Processed Meeting Summary\n" + "="*50 + "\n\n" + formatted_content
            else:
                # No existing content, just use the new content
                combined_content = formatted_content
            
            # Update the text property with combined content
            update_data = {
                "properties": {
                    text_property: {
                        "rich_text": [
                            {
                                "text": {
                                    "content": combined_content
                                }
                            }
                        ]
                    }
                }
            }
            
            response = requests.patch(url, headers=headers, json=update_data)
            response.raise_for_status()
            
            print(f"✅ Successfully updated page: {page_id}")
            print(f"📝 Preserved existing content and added AI summary")
            return True
        else:
            print("⚠️  No rich text property found to update")
            print("Available properties:", list(properties.keys()))
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating Notion page: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                print(f"Error details: {json.dumps(error_details, indent=2)}")
            except:
                print(f"Response text: {e.response.text}")
        return False

def main():
    """
    Main function to update a meeting page with transcript processing.
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python update_meeting.py <notion_page_url> [transcript_filename]")
        print("")
        print("Examples:")
        print("  python update_meeting.py 'https://www.notion.so/Page-Title-{page_id}?p={page_id}&pm=c'")
        print("  python update_meeting.py 'https://www.notion.so/Page-Title-{page_id}?p={page_id}&pm=c' my_meeting.txt")
        print("")
        print("If no transcript filename is provided, you'll be prompted to choose from available files.")
        sys.exit(1)
    
    page_url = sys.argv[1]
    specific_filename = sys.argv[2] if len(sys.argv) == 3 else None
    
    print("🔄 Updating Notion meeting page with transcript processing")
    print("=" * 60)
    
    # Extract page ID from URL
    page_id = extract_page_id_from_url(page_url)
    if not page_id:
        print(f"❌ Could not extract page ID from URL: {page_url}")
        sys.exit(1)
    
    print(f"📄 Page ID: {page_id}")
    
    # Find transcript file
    transcript_file = find_transcript_file(specific_file=specific_filename)
    if not transcript_file:
        sys.exit(1)
    
    # Read transcript content
    transcript_content = read_transcript_file(transcript_file)
    if not transcript_content:
        sys.exit(1)
    
    # Check required environment variables
    required_vars = ['NOTION_TOKEN', 'DATABASE_ID', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Initialize transcript processor
    try:
        processor = TranscriptProcessor(
            os.getenv('NOTION_TOKEN'),
            os.getenv('DATABASE_ID'),
            os.getenv('PEOPLE_DATABASE_ID'),
            os.getenv('OPENAI_API_KEY')
        )
        print("✅ Transcript processor initialized")
    except Exception as e:
        print(f"❌ Failed to initialize transcript processor: {e}")
        sys.exit(1)
    
    # Process the transcript
    print("\n🤖 Processing transcript with AI...")
    extracted_data = processor.process_transcript(transcript_content)
    
    if not extracted_data:
        print("❌ Failed to process transcript")
        sys.exit(1)
    
    print("✅ Transcript processed successfully")
    
    # Show what was extracted
    attendees = extracted_data.get('attendees', [])
    if attendees:
        print(f"👥 Attendees: {', '.join(attendees)}")
    
    action_items = extracted_data.get('action_items', [])
    if action_items:
        print(f"📋 Action items: {len(action_items)} items extracted")
    
    decisions = extracted_data.get('key_decisions', [])
    if decisions:
        print(f"🎯 Key decisions: {len(decisions)} decisions recorded")
    
    # Add content as blocks to the Notion page
    print(f"\n📝 Adding AI summary as blocks to Notion page...")
    success = add_blocks_to_notion_page(page_id, extracted_data)
    
    if success:
        # Try to upload the transcript file
        print(f"\n📎 Attempting to upload transcript file...")
        upload_success = upload_file_to_notion(page_id, transcript_file)
        
        print(f"\n🎉 Successfully updated meeting page!")
        print(f"Page URL: {page_url}")
        
        if not upload_success:
            print(f"\n📋 Manual step required:")
            print(f"Please manually attach the transcript file to the 'Files & media' property:")
            print(f"File location: {transcript_file}")
    else:
        print(f"\n❌ Failed to update meeting page")
        sys.exit(1)

if __name__ == "__main__":
    main()
