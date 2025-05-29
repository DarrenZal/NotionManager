#!/usr/bin/env python3
"""
People Manager for Notion - Handles named entity resolution and linking
"""

import requests
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class PeopleManager:
    def __init__(self, token: str, people_database_id: str):
        """
        Initialize the People Manager for entity resolution and linking.
        
        Args:
            token: Your Notion integration token
            people_database_id: The ID of your People database
        """
        self.token = token
        self.people_database_id = people_database_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"
        self._people_cache = None
    
    def get_people_database_schema(self) -> Dict[str, Any]:
        """
        Retrieve the People database schema.
        
        Returns:
            Dictionary containing database information and properties
        """
        url = f"{self.base_url}/databases/{self.people_database_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching People database schema: {e}")
            return {}
    
    def get_all_people(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve all people from the People database with caching.
        
        Args:
            force_refresh: Force refresh of the cache
            
        Returns:
            List of people records
        """
        if self._people_cache is None or force_refresh:
            url = f"{self.base_url}/databases/{self.people_database_id}/query"
            
            all_people = []
            has_more = True
            start_cursor = None
            
            try:
                while has_more:
                    data = {}
                    if start_cursor:
                        data["start_cursor"] = start_cursor
                    
                    response = requests.post(url, headers=self.headers, json=data)
                    response.raise_for_status()
                    result = response.json()
                    
                    all_people.extend(result.get('results', []))
                    has_more = result.get('has_more', False)
                    start_cursor = result.get('next_cursor')
                
                self._people_cache = all_people
                print(f"📋 Loaded {len(all_people)} people from database")
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching people: {e}")
                return []
        
        return self._people_cache
    
    def extract_person_names(self, text: str) -> List[str]:
        """
        Extract potential person names from text using simple heuristics.
        
        Args:
            text: Text to extract names from
            
        Returns:
            List of potential person names
        """
        # Simple name extraction patterns - more conservative
        patterns = [
            # Names in "Attendees: Name1, Name2" format
            r'(?:attendees?|participants?|people):\s*([^.!?\n]+)',
            # Names after speaker labels like "John:" or "Sarah:"
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?):\s',
            # Names in simple lists
            r'\b([A-Z][a-z]+)(?:\s+and\s+([A-Z][a-z]+))?\b',
        ]
        
        potential_names = set()
        
        # First, try to extract from speaker labels (most reliable)
        speaker_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?):\s'
        for line in text.split('\n'):
            match = re.match(speaker_pattern, line.strip())
            if match:
                name = match.group(1).strip()
                if self._is_likely_person_name(name):
                    potential_names.add(name)
        
        # Then try other patterns
        for pattern in patterns[:-1]:  # Skip the last pattern as it's too broad
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                name_text = match.group(1).strip()
                
                # Split on common separators
                names = re.split(r'[,;&]+', name_text)
                
                for name in names:
                    name = name.strip()
                    # Filter out common non-names
                    if self._is_likely_person_name(name) and len(name.split()) <= 3:
                        potential_names.add(name)
        
        return list(potential_names)
    
    def _is_likely_person_name(self, name: str) -> bool:
        """
        Check if a string is likely to be a person's name.
        
        Args:
            name: String to check
            
        Returns:
            True if likely a person name
        """
        # Basic filters
        if len(name) < 2 or len(name) > 50:
            return False
        
        # Must start with capital letter
        if not name[0].isupper():
            return False
        
        # Filter out common non-names
        non_names = {
            'Team', 'Meeting', 'Call', 'Discussion', 'Review', 'Update',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December',
            'AM', 'PM', 'EST', 'PST', 'UTC', 'GMT'
        }
        
        if name in non_names:
            return False
        
        # Should contain only letters, spaces, hyphens, apostrophes
        if not re.match(r"^[A-Za-z\s\-']+$", name):
            return False
        
        return True
    
    def find_matching_person(self, name: str, threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """
        Find a matching person in the database using fuzzy matching.
        
        Args:
            name: Name to search for
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            Matching person record or None
        """
        people = self.get_all_people()
        best_match = None
        best_score = 0.0
        
        for person in people:
            # Get the person's name from the title property
            name_prop = person.get('properties', {}).get('Name', {})
            if not name_prop.get('title'):
                continue
            
            person_name = name_prop['title'][0]['text']['content']
            
            # Calculate similarity
            score = SequenceMatcher(None, name.lower(), person_name.lower()).ratio()
            
            if score > best_score and score >= threshold:
                best_score = score
                best_match = person
        
        if best_match:
            print(f"🔗 Matched '{name}' to existing person (similarity: {best_score:.2f})")
        
        return best_match
    
    def create_person(self, name: str, additional_properties: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new person in the People database.
        
        Args:
            name: Person's name
            additional_properties: Optional additional properties
            
        Returns:
            Created person record or None
        """
        url = f"{self.base_url}/pages"
        
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            }
        }
        
        # Add any additional properties
        if additional_properties:
            properties.update(additional_properties)
        
        data = {
            "parent": {"database_id": self.people_database_id},
            "properties": properties
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Created new person: {name}")
            
            # Refresh cache to include new person
            self._people_cache = None
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating person '{name}': {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    print(f"Error details: {json.dumps(error_details, indent=2)}")
                except:
                    print(f"Response text: {e.response.text}")
            return None
    
    def resolve_people_in_text(self, text: str, create_missing: bool = True) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Extract and resolve all people mentioned in text.
        
        Args:
            text: Text to process
            create_missing: Whether to create new people if not found
            
        Returns:
            Tuple of (resolved_people, unresolved_names)
        """
        # Extract potential names
        potential_names = self.extract_person_names(text)
        print(f"🔍 Extracted potential names: {potential_names}")
        
        resolved_people = []
        unresolved_names = []
        
        for name in potential_names:
            # Try to find existing person
            existing_person = self.find_matching_person(name)
            
            if existing_person:
                resolved_people.append(existing_person)
            elif create_missing:
                # Create new person
                new_person = self.create_person(name)
                if new_person:
                    resolved_people.append(new_person)
                else:
                    unresolved_names.append(name)
            else:
                unresolved_names.append(name)
        
        return resolved_people, unresolved_names
    
    def get_person_ids(self, people: List[Dict[str, Any]]) -> List[str]:
        """
        Extract person IDs from person records.
        
        Args:
            people: List of person records
            
        Returns:
            List of person IDs
        """
        return [person['id'] for person in people]
    
    def create_people_relation_property(self, people: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a relation property for linking people to meetings.
        
        Args:
            people: List of person records
            
        Returns:
            Relation property structure for Notion API
        """
        person_ids = self.get_person_ids(people)
        
        return {
            "relation": [
                {"id": person_id} for person_id in person_ids
            ]
        }


def main():
    """
    Test the People Manager functionality.
    """
    # Load environment variables
    token = os.getenv('NOTION_TOKEN')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    
    if not token or not people_db_id:
        print("❌ Missing required environment variables:")
        print("Please set NOTION_TOKEN and PEOPLE_DATABASE_ID")
        print("\nExample:")
        print("export PEOPLE_DATABASE_ID='your_people_database_id'")
        return
    
    # Initialize People Manager
    people_mgr = PeopleManager(token, people_db_id)
    
    # Test text with names
    test_text = "Meeting with Gaia Team. Attendees: Aaron, Darren, Susanna, John Smith"
    
    print("🧪 Testing People Manager")
    print("=" * 50)
    print(f"Test text: {test_text}")
    print()
    
    # Resolve people
    resolved, unresolved = people_mgr.resolve_people_in_text(test_text)
    
    print(f"\n📊 Results:")
    print(f"Resolved people: {len(resolved)}")
    print(f"Unresolved names: {len(unresolved)}")
    
    if resolved:
        print("\n✅ Resolved People:")
        for person in resolved:
            name = person['properties']['Name']['title'][0]['text']['content']
            print(f"  - {name} (ID: {person['id']})")
    
    if unresolved:
        print(f"\n❌ Unresolved Names: {unresolved}")


if __name__ == "__main__":
    main()
