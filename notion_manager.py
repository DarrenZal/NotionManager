import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from people_manager import PeopleManager

# Load environment variables from .env file
load_dotenv()

class NotionManager:
    def __init__(self, token: str, database_id: str, people_database_id: Optional[str] = None):
        """
        Initialize the Notion Manager with API token and database ID.
        
        Args:
            token: Your Notion integration token (starts with 'secret_')
            database_id: The ID of your Notion database
            people_database_id: Optional ID of your People database for entity linking
        """
        self.token = token
        self.database_id = database_id
        self.people_database_id = people_database_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"
        
        # Initialize People Manager if people database ID is provided
        self.people_manager = None
        if people_database_id:
            self.people_manager = PeopleManager(token, people_database_id)
    
    def get_database_schema(self) -> Dict[str, Any]:
        """
        Retrieve the database schema to understand available properties.
        
        Returns:
            Dictionary containing database information and properties
        """
        url = f"{self.base_url}/databases/{self.database_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching database schema: {e}")
            return {}
    
    def print_database_properties(self):
        """
        Print the database properties in a readable format.
        """
        schema = self.get_database_schema()
        if not schema:
            print("Failed to retrieve database schema")
            return
        
        print(f"Database Title: {schema.get('title', [{}])[0].get('plain_text', 'Unknown')}")
        print(f"Database ID: {self.database_id}")
        print("\nAvailable Properties:")
        print("-" * 50)
        
        properties = schema.get('properties', {})
        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get('type', 'unknown')
            print(f"• {prop_name}: {prop_type}")
            
            # Show additional info for specific types
            if prop_type == 'select':
                options = prop_info.get('select', {}).get('options', [])
                if options:
                    option_names = [opt['name'] for opt in options]
                    print(f"  Options: {', '.join(option_names)}")
            elif prop_type == 'multi_select':
                options = prop_info.get('multi_select', {}).get('options', [])
                if options:
                    option_names = [opt['name'] for opt in options]
                    print(f"  Options: {', '.join(option_names)}")
    
    def add_meeting_page(self, 
                        meeting_name: str, 
                        meeting_date: str, 
                        meeting_type: str = "Standard Meeting",
                        text_content: str = "",
                        auto_link_people: bool = True,
                        additional_properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a new meeting page to the database with automatic people linking.
        
        Args:
            meeting_name: Name/title of the meeting
            meeting_date: Date in ISO format (e.g., "2025-06-01T10:00:00.000-07:00")
            meeting_type: Type of meeting (Strategy Call, Discovery Call, Standard Meeting, Technical Consultation)
            text_content: Text content for the meeting
            auto_link_people: Whether to automatically extract and link people mentioned
            additional_properties: Optional dict of additional properties to set
            
        Returns:
            Dictionary containing the API response
        """
        url = f"{self.base_url}/pages"
        
        # Base properties structure
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": meeting_name
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": meeting_date
                }
            },
            "Type": {
                "select": {
                    "name": meeting_type
                }
            }
        }
        
        # Add text content if provided
        if text_content:
            properties["Text"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": text_content
                        }
                    }
                ]
            }
        
        # Auto-link people if enabled and People Manager is available
        if auto_link_people and self.people_manager:
            print("🔍 Extracting and linking people...")
            
            # Combine meeting name and text content for people extraction
            full_text = f"{meeting_name} {text_content}"
            
            try:
                resolved_people, unresolved_names = self.people_manager.resolve_people_in_text(full_text)
                
                if resolved_people:
                    # Check if we have relation properties that could link to people
                    schema = self.get_database_schema()
                    people_relation_props = []
                    
                    for prop_name, prop_info in schema.get('properties', {}).items():
                        if prop_info.get('type') == 'relation':
                            # Check if this relation points to the People database
                            relation_db_id = prop_info.get('relation', {}).get('database_id')
                            if relation_db_id == self.people_database_id:
                                people_relation_props.append(prop_name)
                    
                    # Link people to the first available people relation property
                    if people_relation_props:
                        relation_prop = people_relation_props[0]
                        people_relation = self.people_manager.create_people_relation_property(resolved_people)
                        properties[relation_prop] = people_relation
                        
                        linked_names = [p['properties']['Name']['title'][0]['text']['content'] for p in resolved_people]
                        print(f"🔗 Linked {len(resolved_people)} people to '{relation_prop}': {', '.join(linked_names)}")
                    else:
                        print("ℹ️  No people relation properties found in database schema")
                
                if unresolved_names:
                    print(f"⚠️  Could not resolve: {', '.join(unresolved_names)}")
                    
            except Exception as e:
                print(f"⚠️  Error during people linking: {e}")
        
        # Add any additional properties
        if additional_properties:
            properties.update(additional_properties)
        
        data = {
            "parent": {"database_id": self.database_id},
            "properties": properties
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            print(f"✅ Successfully created page: {meeting_name}")
            print(f"Page URL: {result.get('url', 'N/A')}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating page: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    print(f"Error details: {json.dumps(error_details, indent=2)}")
                except:
                    print(f"Response text: {e.response.text}")
            return {}
    
    def query_database(self, filter_conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query the database with optional filters.
        
        Args:
            filter_conditions: Optional filter conditions for the query
            
        Returns:
            Dictionary containing query results
        """
        url = f"{self.base_url}/databases/{self.database_id}/query"
        
        data = {}
        if filter_conditions:
            data["filter"] = filter_conditions
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying database: {e}")
            return {}


def main():
    """
    Main function to demonstrate Notion API functionality.
    """
    # Load environment variables
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('DATABASE_ID')
    
    if not token or not database_id:
        print("❌ Missing required environment variables:")
        print("Please set NOTION_TOKEN and DATABASE_ID")
        print("\nExample:")
        print("export NOTION_TOKEN='secret_xxxxxxxxxxxxxxx'")
        print("export DATABASE_ID='your_database_id_here'")
        return
    
    # Initialize Notion Manager
    notion = NotionManager(token, database_id)
    
    print("🔍 Fetching database schema...")
    notion.print_database_properties()
    
    print("\n" + "="*60)
    print("📝 Testing page creation...")
    
    # Test adding a meeting
    meeting_name = "Meeting with Gaia Team"
    meeting_date = "2025-06-01T10:00:00.000-07:00"
    meeting_type = "Standard Meeting"
    text_content = "Attendees: Aaron, Darren, Susanna"
    
    result = notion.add_meeting_page(meeting_name, meeting_date, meeting_type, text_content)
    
    if result:
        print(f"\n✅ Page created successfully!")
        print(f"Page ID: {result.get('id', 'N/A')}")
    
    print("\n" + "="*60)
    print("📋 Querying recent pages...")
    
    # Query the database to see recent entries
    query_result = notion.query_database()
    if query_result and 'results' in query_result:
        print(f"Found {len(query_result['results'])} pages in the database")
        for i, page in enumerate(query_result['results'][:3]):  # Show first 3
            title_prop = page.get('properties', {}).get('Name', {})
            if title_prop.get('title'):
                title = title_prop['title'][0]['text']['content']
                print(f"{i+1}. {title}")


if __name__ == "__main__":
    main()
