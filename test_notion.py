#!/usr/bin/env python3
"""
Test script for Notion API functionality with example usage patterns.
"""

import os
from datetime import datetime, timedelta
from notion_manager import NotionManager

def test_basic_functionality():
    """
    Test basic Notion API functionality.
    """
    # Load environment variables
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('DATABASE_ID')
    
    if not token or not database_id:
        print("❌ Please set up your environment variables first:")
        print("Run: python setup_env.py")
        return False
    
    print("🧪 Testing Notion API Integration")
    print("=" * 50)
    
    # Initialize Notion Manager
    notion = NotionManager(token, database_id)
    
    # Test 1: Get database schema
    print("1️⃣ Testing database schema retrieval...")
    schema = notion.get_database_schema()
    if schema:
        print("✅ Successfully retrieved database schema")
        notion.print_database_properties()
    else:
        print("❌ Failed to retrieve database schema")
        return False
    
    print("\n" + "=" * 50)
    
    # Test 2: Add a test meeting
    print("2️⃣ Testing page creation...")
    test_meeting_name = f"Test Meeting - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    test_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.000-07:00')
    test_type = "Standard Meeting"
    test_text = "Test attendees: Test User 1, Test User 2"
    
    result = notion.add_meeting_page(test_meeting_name, test_date, test_type, test_text)
    if result:
        print("✅ Successfully created test page")
        page_id = result.get('id', 'Unknown')
        print(f"Page ID: {page_id}")
    else:
        print("❌ Failed to create test page")
        return False
    
    print("\n" + "=" * 50)
    
    # Test 3: Query database
    print("3️⃣ Testing database query...")
    query_result = notion.query_database()
    if query_result and 'results' in query_result:
        print(f"✅ Successfully queried database")
        print(f"Found {len(query_result['results'])} total pages")
        
        # Show recent pages
        print("\nRecent pages:")
        for i, page in enumerate(query_result['results'][:5]):
            title_prop = page.get('properties', {}).get('Name', {})
            if title_prop.get('title'):
                title = title_prop['title'][0]['text']['content']
                created_time = page.get('created_time', 'Unknown')
                print(f"  {i+1}. {title} (Created: {created_time[:10]})")
    else:
        print("❌ Failed to query database")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your Notion integration is working correctly.")
    return True

def test_advanced_features():
    """
    Test advanced features like custom properties and filters.
    """
    token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('DATABASE_ID')
    
    if not token or not database_id:
        print("❌ Environment variables not set")
        return False
    
    print("\n🔬 Testing Advanced Features")
    print("=" * 50)
    
    notion = NotionManager(token, database_id)
    
    # Test with additional properties (if they exist in your database)
    print("4️⃣ Testing advanced page creation with custom properties...")
    
    # Get schema to see what properties are available
    schema = notion.get_database_schema()
    properties = schema.get('properties', {})
    
    additional_props = {}
    
    # Check for common property types and add them if they exist
    for prop_name, prop_info in properties.items():
        prop_type = prop_info.get('type')
        
        if prop_type == 'select' and prop_name.lower() in ['status', 'priority', 'type']:
            options = prop_info.get('select', {}).get('options', [])
            if options:
                # Use the first available option
                additional_props[prop_name] = {
                    "select": {
                        "name": options[0]['name']
                    }
                }
                print(f"  Adding {prop_name}: {options[0]['name']}")
    
    if additional_props:
        advanced_meeting_name = f"Advanced Test Meeting - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        advanced_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%S.000-07:00')
        
        result = notion.add_meeting_page(
            advanced_meeting_name, 
            advanced_date, 
            "Technical Consultation",
            "Advanced test with custom properties",
            additional_props
        )
        
        if result:
            print("✅ Successfully created advanced page with custom properties")
        else:
            print("❌ Failed to create advanced page")
    else:
        print("ℹ️  No additional select properties found for testing")
    
    # Test filtered query
    print("\n5️⃣ Testing filtered database query...")
    
    # Query for pages created today
    today = datetime.now().strftime('%Y-%m-%d')
    filter_conditions = {
        "property": "Created time",
        "created_time": {
            "on_or_after": f"{today}T00:00:00.000Z"
        }
    }
    
    filtered_result = notion.query_database(filter_conditions)
    if filtered_result and 'results' in filtered_result:
        print(f"✅ Successfully executed filtered query")
        print(f"Found {len(filtered_result['results'])} pages created today")
    else:
        print("❌ Filtered query failed")
    
    print("\n🎉 Advanced testing completed!")

def main():
    """
    Main test function.
    """
    print("🚀 Notion API Test Suite")
    print("=" * 50)
    
    # Run basic tests
    basic_success = test_basic_functionality()
    
    if basic_success:
        # Run advanced tests
        test_advanced_features()
    else:
        print("\n❌ Basic tests failed. Please check your setup and try again.")
        print("\nTroubleshooting steps:")
        print("1. Run: python setup_env.py")
        print("2. Verify your Notion integration has access to the database")
        print("3. Check that your database ID is correct")

if __name__ == "__main__":
    main()
