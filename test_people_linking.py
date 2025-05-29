#!/usr/bin/env python3
"""
Test script for People Manager and automatic people linking functionality.
"""

import os
from datetime import datetime, timedelta
from notion_manager import NotionManager
from people_manager import PeopleManager

def test_people_manager_standalone():
    """
    Test the People Manager functionality independently.
    """
    token = os.getenv('NOTION_TOKEN')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    
    if not token or not people_db_id:
        print("❌ Missing PEOPLE_DATABASE_ID environment variable")
        print("Please set PEOPLE_DATABASE_ID to test people linking")
        return False
    
    print("🧪 Testing People Manager (Standalone)")
    print("=" * 50)
    
    # Initialize People Manager
    people_mgr = PeopleManager(token, people_db_id)
    
    # Test 1: Get People database schema
    print("1️⃣ Testing People database schema retrieval...")
    schema = people_mgr.get_people_database_schema()
    if schema:
        print("✅ Successfully retrieved People database schema")
        title = schema.get('title', [{}])[0].get('plain_text', 'Unknown')
        print(f"Database Title: {title}")
    else:
        print("❌ Failed to retrieve People database schema")
        return False
    
    # Test 2: Load existing people
    print("\n2️⃣ Testing people loading...")
    people = people_mgr.get_all_people()
    print(f"✅ Loaded {len(people)} people from database")
    
    if people:
        print("Sample people:")
        for i, person in enumerate(people[:3]):
            name_prop = person.get('properties', {}).get('Name', {})
            if name_prop.get('title'):
                name = name_prop['title'][0]['text']['content']
                print(f"  {i+1}. {name}")
    
    # Test 3: Name extraction
    print("\n3️⃣ Testing name extraction...")
    test_texts = [
        "Meeting with Gaia Team. Attendees: Aaron, Darren, Susanna",
        "Call with John Smith and Jane Doe about the project",
        "Strategy session with Alice Johnson, Bob Wilson, and Charlie Brown"
    ]
    
    for text in test_texts:
        print(f"\nText: '{text}'")
        names = people_mgr.extract_person_names(text)
        print(f"Extracted names: {names}")
    
    # Test 4: People resolution
    print("\n4️⃣ Testing people resolution...")
    test_text = "Meeting with Gaia Team. Attendees: Aaron, Darren, Susanna, John Smith"
    print(f"Test text: {test_text}")
    
    resolved, unresolved = people_mgr.resolve_people_in_text(test_text, create_missing=False)
    
    print(f"\n📊 Resolution Results:")
    print(f"Resolved people: {len(resolved)}")
    print(f"Unresolved names: {len(unresolved)}")
    
    if resolved:
        print("\n✅ Resolved People:")
        for person in resolved:
            name = person['properties']['Name']['title'][0]['text']['content']
            print(f"  - {name} (ID: {person['id']})")
    
    if unresolved:
        print(f"\n❌ Unresolved Names: {unresolved}")
    
    return True

def test_integrated_people_linking():
    """
    Test the integrated people linking functionality with NotionManager.
    """
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('DATABASE_ID')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    
    if not all([token, database_id, people_db_id]):
        print("❌ Missing required environment variables for integrated testing")
        print("Need: NOTION_TOKEN, DATABASE_ID, PEOPLE_DATABASE_ID")
        return False
    
    print("\n🔗 Testing Integrated People Linking")
    print("=" * 50)
    
    # Initialize Notion Manager with People database
    notion = NotionManager(token, database_id, people_db_id)
    
    # Test 1: Check if People Manager is initialized
    print("1️⃣ Testing People Manager initialization...")
    if notion.people_manager:
        print("✅ People Manager successfully initialized")
    else:
        print("❌ People Manager not initialized")
        return False
    
    # Test 2: Check for relation properties
    print("\n2️⃣ Checking for people relation properties...")
    schema = notion.get_database_schema()
    people_relation_props = []
    
    for prop_name, prop_info in schema.get('properties', {}).items():
        if prop_info.get('type') == 'relation':
            relation_db_id = prop_info.get('relation', {}).get('database_id')
            if relation_db_id == people_db_id:
                people_relation_props.append(prop_name)
    
    if people_relation_props:
        print(f"✅ Found people relation properties: {', '.join(people_relation_props)}")
    else:
        print("⚠️  No people relation properties found - people won't be linked")
        print("   Consider adding a relation property to your Meetings database that links to People")
    
    # Test 3: Create meeting with people linking
    print("\n3️⃣ Testing meeting creation with people linking...")
    
    meeting_name = f"Test People Linking - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    meeting_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.000-07:00')
    meeting_type = "Standard Meeting"
    text_content = "Attendees: Aaron, Darren, Susanna, John Smith, Alice Johnson"
    
    print(f"Creating meeting: {meeting_name}")
    print(f"Text content: {text_content}")
    
    result = notion.add_meeting_page(
        meeting_name=meeting_name,
        meeting_date=meeting_date,
        meeting_type=meeting_type,
        text_content=text_content,
        auto_link_people=True
    )
    
    if result:
        print("✅ Successfully created meeting with people linking")
        print(f"Meeting URL: {result.get('url', 'N/A')}")
        return True
    else:
        print("❌ Failed to create meeting")
        return False

def test_people_creation():
    """
    Test creating new people when they don't exist.
    """
    token = os.getenv('NOTION_TOKEN')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    
    if not token or not people_db_id:
        print("❌ Missing PEOPLE_DATABASE_ID for people creation test")
        return False
    
    print("\n👥 Testing People Creation")
    print("=" * 50)
    
    people_mgr = PeopleManager(token, people_db_id)
    
    # Test creating a new person with a unique name
    test_name = f"Test Person {datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print(f"Creating new person: {test_name}")
    new_person = people_mgr.create_person(test_name)
    
    if new_person:
        print("✅ Successfully created new person")
        print(f"Person ID: {new_person['id']}")
        
        # Test that we can now find this person
        found_person = people_mgr.find_matching_person(test_name)
        if found_person:
            print("✅ Successfully found newly created person")
            return True
        else:
            print("❌ Could not find newly created person")
            return False
    else:
        print("❌ Failed to create new person")
        return False

def main():
    """
    Main test function for people linking functionality.
    """
    print("🚀 People Linking Test Suite")
    print("=" * 50)
    
    # Check environment variables
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('DATABASE_ID')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    
    if not token:
        print("❌ NOTION_TOKEN not set")
        return
    
    if not database_id:
        print("❌ DATABASE_ID not set")
        return
    
    if not people_db_id:
        print("⚠️  PEOPLE_DATABASE_ID not set - some tests will be skipped")
        print("   To enable people linking, set PEOPLE_DATABASE_ID to your People database ID")
        return
    
    # Run tests
    success_count = 0
    total_tests = 3
    
    # Test 1: People Manager standalone
    if test_people_manager_standalone():
        success_count += 1
    
    # Test 2: Integrated people linking
    if test_integrated_people_linking():
        success_count += 1
    
    # Test 3: People creation
    if test_people_creation():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All people linking tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
