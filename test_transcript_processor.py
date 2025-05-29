#!/usr/bin/env python3
"""
Test script for the Transcript Processor functionality.
"""

import os
from transcript_processor import TranscriptProcessor

def test_transcript_processing():
    """
    Test the transcript processing functionality with various transcript formats.
    """
    # Load environment variables
    notion_token = os.getenv('NOTION_TOKEN')
    meetings_db_id = os.getenv('DATABASE_ID')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not all([notion_token, meetings_db_id, openai_api_key]):
        print("❌ Missing required environment variables:")
        print("Please set NOTION_TOKEN, DATABASE_ID, and OPENAI_API_KEY")
        return False
    
    print("🧪 Testing Transcript Processor")
    print("=" * 50)
    
    # Initialize processor
    try:
        processor = TranscriptProcessor(notion_token, meetings_db_id, people_db_id, openai_api_key)
        print("✅ Transcript Processor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Transcript Processor: {e}")
        return False
    
    # Test 1: Simple meeting transcript
    print("\n1️⃣ Testing simple meeting transcript...")
    simple_transcript = """
Meeting: Product Planning Session
Date: May 28, 2025
Time: 2:00 PM

Alice: Welcome everyone to our product planning session. Let's discuss the Q3 roadmap.

Bob: I think we should prioritize the mobile app features. Our users have been requesting this for months.

Charlie: Agreed. I can lead the mobile development. We'll need about 6 weeks for the initial version.

Alice: Great. What about the API improvements, David?

David: The API refactoring is almost complete. Should be done by next Friday. After that, I can help with mobile backend integration.

Alice: Perfect. Action items: Charlie will lead mobile development with 6-week timeline, David will complete API refactoring by Friday and then support mobile backend. Let's reconvene in two weeks to check progress.

Bob: Should we also consider the analytics dashboard?

Alice: Yes, but let's make that a Q4 priority. Mobile comes first.

Meeting ended at 2:45 PM.
"""
    
    result1 = processor.create_meeting_from_transcript(simple_transcript)
    if result1:
        print("✅ Simple transcript processed successfully")
    else:
        print("❌ Failed to process simple transcript")
    
    # Test 2: Complex meeting with multiple speakers and detailed action items
    print("\n2️⃣ Testing complex meeting transcript...")
    complex_transcript = """
TRANSCRIPT: Engineering All-Hands Meeting
Date: May 28, 2025, 3:00 PM - 4:30 PM
Attendees: Sarah Chen (Engineering Manager), Mike Rodriguez (Backend Lead), 
          Jessica Wong (Frontend Lead), Alex Kumar (DevOps), Tom Wilson (QA Lead)

Sarah Chen: Good afternoon everyone. Today we're discussing the upcoming release and some critical infrastructure decisions.

Mike Rodriguez: The backend services are ready for the v2.1 release. We've implemented the new authentication system and improved the database query performance by 40%.

Jessica Wong: Frontend is mostly ready too. We have one blocker though - the new user dashboard is causing memory leaks in older browsers. I need another week to fix this.

Sarah Chen: That's concerning. Tom, what's the testing status?

Tom Wilson: We've completed 85% of our test cases. The memory leak Jessica mentioned is confirmed. It affects Chrome versions below 90 and Firefox below 88. We should either fix it or drop support for older browsers.

Alex Kumar: From an infrastructure perspective, we're seeing increased load on our staging environment. We might need to upgrade our servers before the release.

Sarah Chen: Let's make some decisions. Jessica, you have one week to fix the memory leak. If it's not resolved, we'll drop support for older browsers. Alex, please prepare a cost estimate for the server upgrade.

Mike Rodriguez: I can help Jessica with the memory leak investigation. I've dealt with similar issues before.

Jessica Wong: That would be great, Mike. Let's sync up tomorrow morning.

Sarah Chen: Excellent. Tom, can you prepare a compatibility report showing which browser versions we'll support?

Tom Wilson: Absolutely. I'll have that ready by Wednesday.

Alex Kumar: For the server upgrade, I'm looking at about $2000/month additional cost. Should I proceed with the procurement process?

Sarah Chen: Yes, but let's get approval from finance first. I'll talk to them tomorrow.

Sarah Chen: Action items summary: Jessica has one week to fix memory leak with Mike's help, Tom will prepare browser compatibility report by Wednesday, Alex will get finance approval for server upgrade, and I'll schedule a follow-up meeting for next Friday to review progress.

Mike Rodriguez: One more thing - we should consider implementing automated performance testing to catch these issues earlier.

Sarah Chen: Good point. Let's add that to our Q3 planning. Tom, can you research some tools?

Tom Wilson: Sure, I'll look into it.

Meeting concluded at 4:25 PM.
"""
    
    result2 = processor.create_meeting_from_transcript(complex_transcript)
    if result2:
        print("✅ Complex transcript processed successfully")
    else:
        print("❌ Failed to process complex transcript")
    
    # Test 3: Strategy meeting transcript
    print("\n3️⃣ Testing strategy meeting transcript...")
    strategy_transcript = """
BOARD MEETING TRANSCRIPT
Strategic Planning Session - Q3 2025
Date: May 28, 2025
Time: 10:00 AM - 12:00 PM

CEO John Smith: Welcome to our quarterly strategic planning session. We need to make some important decisions about our market expansion.

CFO Maria Garcia: Our Q2 numbers are strong. Revenue is up 25% compared to last quarter. We have the budget to pursue either the European expansion or the enterprise product line.

CTO David Lee: From a technical standpoint, the European expansion would require significant infrastructure investment. GDPR compliance alone would take 3-4 months.

VP Sales Rachel Brown: The enterprise market is very promising. We've had 15 inbound inquiries this month alone. I think we could close $2M in enterprise deals by end of Q3.

CEO John Smith: Those are compelling numbers. What about the competitive landscape?

VP Marketing Lisa Chen: In Europe, we'd be competing with three established players. In enterprise, we have a unique positioning with our AI features.

CTO David Lee: I agree with focusing on enterprise first. We can leverage our existing infrastructure and the technical lift is much smaller.

CFO Maria Garcia: Enterprise also has better margins. 40% vs 25% for our current consumer product.

CEO John Smith: It sounds like we're leaning toward enterprise. Let's make it official. Decision: We'll prioritize enterprise product development for Q3. Rachel, I need a detailed sales plan by next week.

VP Sales Rachel Brown: I'll have a comprehensive plan ready. Should include pricing strategy, target customer profiles, and sales process.

CTO David Lee: I'll need to hire two senior engineers for the enterprise features. Can we approve those positions?

CEO John Smith: Yes, approved. Maria, please work with David on the hiring budget.

CFO Maria Garcia: Will do. I'll also prepare a financial projection for the enterprise revenue.

CEO John Smith: Excellent. Next steps: Rachel prepares sales plan, David starts hiring process, Maria creates financial projections. Let's reconvene in two weeks to review progress.

VP Marketing Lisa Chen: Should I start working on enterprise marketing materials?

CEO John Smith: Yes, coordinate with Rachel on messaging and target audience.

Meeting adjourned at 11:45 AM.
"""
    
    result3 = processor.create_meeting_from_transcript(strategy_transcript)
    if result3:
        print("✅ Strategy transcript processed successfully")
    else:
        print("❌ Failed to process strategy transcript")
    
    # Summary
    success_count = sum([1 for result in [result1, result2, result3] if result])
    print(f"\n📊 Test Results: {success_count}/3 transcripts processed successfully")
    
    if success_count == 3:
        print("🎉 All transcript processing tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

def test_extraction_only():
    """
    Test just the data extraction without creating Notion pages.
    """
    # Load environment variables
    notion_token = os.getenv('NOTION_TOKEN')
    meetings_db_id = os.getenv('DATABASE_ID')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not all([notion_token, meetings_db_id, openai_api_key]):
        print("❌ Missing required environment variables")
        return False
    
    print("\n🔍 Testing Data Extraction Only")
    print("=" * 50)
    
    # Initialize processor
    processor = TranscriptProcessor(notion_token, meetings_db_id, people_db_id, openai_api_key)
    
    # Test transcript
    test_transcript = """
Daily Standup - Development Team
May 28, 2025, 9:00 AM

John: Good morning team. Let's go around and share updates.

Sarah: I finished the user authentication module yesterday. Today I'm working on the password reset functionality. No blockers.

Mike: I'm still working on the database optimization. Found a performance issue with the user queries. Should have it fixed by tomorrow.

Emma: I completed the UI mockups for the new dashboard. The client approved them. I'll start implementing the frontend components today.

John: Great progress everyone. Action items: Mike will fix the database performance issue by tomorrow, Emma will start dashboard implementation. Any questions?

Sarah: Should I coordinate with Emma on the authentication UI components?

Emma: Yes, let's sync up after this meeting.

John: Perfect. Meeting ends at 9:15 AM.
"""
    
    # Extract data without creating Notion page
    extracted_data = processor.process_transcript(test_transcript)
    
    if extracted_data:
        print("✅ Data extraction successful!")
        print("\n📋 Extracted Data:")
        print(f"Meeting Name: {extracted_data.get('meeting_name', 'N/A')}")
        print(f"Meeting Type: {extracted_data.get('meeting_type', 'N/A')}")
        print(f"Attendees: {', '.join(extracted_data.get('attendees', []))}")
        print(f"Action Items: {len(extracted_data.get('action_items', []))}")
        print(f"Key Decisions: {len(extracted_data.get('key_decisions', []))}")
        
        # Show action items in detail
        action_items = extracted_data.get('action_items', [])
        if action_items:
            print("\n📝 Action Items:")
            for i, item in enumerate(action_items, 1):
                print(f"  {i}. {item.get('task', 'N/A')}")
                if item.get('assignee'):
                    print(f"     Assigned to: {item['assignee']}")
                if item.get('due_date'):
                    print(f"     Due: {item['due_date']}")
        
        return True
    else:
        print("❌ Data extraction failed")
        return False

def main():
    """
    Main test function.
    """
    print("🚀 Transcript Processor Test Suite")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['NOTION_TOKEN', 'DATABASE_ID', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following in your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return
    
    # Run tests
    print("Testing data extraction only first...")
    extraction_success = test_extraction_only()
    
    if extraction_success:
        print("\n" + "=" * 50)
        print("Now testing full transcript processing with Notion integration...")
        processing_success = test_transcript_processing()
        
        if processing_success:
            print("\n🎉 All tests completed successfully!")
            print("Your transcript processor is ready to use!")
        else:
            print("\n⚠️  Some integration tests failed.")
    else:
        print("\n❌ Basic extraction test failed. Please check your OpenAI API key and try again.")

if __name__ == "__main__":
    main()
