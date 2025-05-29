#!/usr/bin/env python3
"""
Transcript Processor for Notion - Uses LLM to convert meeting transcripts into structured Notion data
"""

import json
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
import openai
from notion_manager import NotionManager
from people_manager import PeopleManager

# Load environment variables
load_dotenv()

class TranscriptProcessor:
    def __init__(self, notion_token: str, meetings_db_id: str, people_db_id: Optional[str] = None, openai_api_key: Optional[str] = None):
        """
        Initialize the Transcript Processor.
        
        Args:
            notion_token: Notion API token
            meetings_db_id: Meetings database ID
            people_db_id: People database ID (optional)
            openai_api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.notion_manager = NotionManager(notion_token, meetings_db_id, people_db_id)
        
        # Initialize People Manager if people database ID is provided
        self.people_manager = None
        if people_db_id:
            try:
                self.people_manager = PeopleManager(notion_token, people_db_id)
                # Test access to the People database
                schema = self.people_manager.get_people_database_schema()
                if not schema:
                    print("⚠️  People database not accessible - people linking will be disabled")
                    self.people_manager = None
            except Exception as e:
                print(f"⚠️  Could not initialize People Manager: {e}")
                print("People linking will be disabled")
                self.people_manager = None
        
        # Set up OpenAI client
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        self.openai_client = openai.OpenAI(api_key=api_key)
        
        # Get database schemas for prompt engineering
        self.meetings_schema = self.notion_manager.get_database_schema()
        self.people_list = self._get_people_list() if self.people_manager else []
    
    def _get_people_list(self) -> List[Dict[str, str]]:
        """
        Get a simplified list of people from the People database for LLM context.
        
        Returns:
            List of people with names and IDs
        """
        if not self.people_manager:
            return []
        
        people = self.people_manager.get_all_people()
        people_list = []
        
        for person in people:
            name_prop = person.get('properties', {}).get('Name', {})
            if name_prop.get('title'):
                name = name_prop['title'][0]['text']['content']
                people_list.append({
                    'name': name,
                    'id': person['id']
                })
        
        return people_list
    
    def _create_extraction_prompt(self, transcript: str) -> str:
        """
        Create a detailed prompt for the LLM to extract structured data from the transcript.
        
        Args:
            transcript: Raw meeting transcript
            
        Returns:
            Formatted prompt string
        """
        # Get meeting types from schema
        meeting_types = []
        properties = self.meetings_schema.get('properties', {})
        type_prop = properties.get('Type', {})
        if type_prop.get('type') == 'select':
            options = type_prop.get('select', {}).get('options', [])
            meeting_types = [opt['name'] for opt in options]
        
        # Format people list for prompt
        people_context = ""
        if self.people_list:
            people_names = [p['name'] for p in self.people_list]
            people_context = f"""
EXISTING PEOPLE IN DATABASE:
{', '.join(people_names)}

When extracting attendees, try to match names to these existing people. If you find variations (e.g., "John" vs "John Smith"), use the full name from the database.
"""
        
        # Get current date for context
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        prompt = f"""Extract key information from this meeting transcript and return ONLY valid JSON.

{people_context}

MEETING TYPES AVAILABLE: {', '.join(meeting_types) if meeting_types else 'Standard Meeting, Strategy Call, Discovery Call, Technical Consultation'}

TRANSCRIPT:
{transcript}

INSTRUCTIONS:
1. Extract the meeting name/title (if not explicit, create a descriptive one)
2. Extract or infer the meeting date and time (if not found, use today's date: {current_date})
3. Determine the meeting type from the available options
4. Extract all attendee names mentioned in the transcript
5. Create a summary of key discussion points, decisions, and action items
6. If speaker labels are present (e.g., John:, Speaker 1:), preserve attribution for important points
7. Extract any action items or tasks mentioned, noting who they're assigned to

Return JSON with this exact structure:
{{
    "meeting_name": "string - descriptive meeting title",
    "meeting_date": "string - ISO format YYYY-MM-DDTHH:MM:SS.000-07:00",
    "meeting_type": "string - one of the available meeting types",
    "attendees": ["array of attendee names"],
    "summary": "string - comprehensive summary including key points, decisions, and action items with speaker attribution where relevant",
    "action_items": [
        {{
            "task": "string - description of the task",
            "assignee": "string - person assigned (if mentioned)",
            "due_date": "string - ONLY if explicitly mentioned in transcript, otherwise null"
        }}
    ],
    "key_decisions": ["array of key decisions made"],
    "next_steps": ["array of next steps or follow-up actions"]
}}

CRITICAL RULES:
- Return ONLY the JSON object, no additional text
- Use ISO 8601 format for dates with timezone offset
- If date/time is not in transcript, use {current_date} as the date
- NEVER invent or hallucinate due dates - only use dates explicitly mentioned in the transcript
- If no due date is mentioned for an action item, set due_date to null
- Be comprehensive in the summary but concise
- Preserve speaker attribution for action items and decisions
- Only include attendees who are actually mentioned or speak in the transcript
- If meeting type is unclear, default to Standard Meeting
- Do NOT make up information that is not in the transcript"""
        
        return prompt
    
    def process_transcript(self, transcript: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """
        Process a meeting transcript using OpenAI's LLM.
        
        Args:
            transcript: Raw meeting transcript text
            model: OpenAI model to use
            
        Returns:
            Extracted structured data
        """
        print("🤖 Processing transcript with OpenAI...")
        
        prompt = self._create_extraction_prompt(transcript)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert meeting analyst. Extract structured information from transcripts accurately and comprehensively. Always respond with valid JSON only."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=4000,  # Sufficient for detailed extraction
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON from the response
            try:
                # Look for JSON in the response (sometimes LLMs add extra text)
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    extracted_data = json.loads(json_match.group())
                else:
                    # If no JSON found, try parsing the whole response
                    extracted_data = json.loads(content)
                
                print("✅ Successfully extracted structured data from transcript")
                return extracted_data
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON from LLM response: {e}")
                print(f"Raw response: {content}")
                return {}
                
        except Exception as e:
            print(f"❌ Error calling OpenAI API: {e}")
            return {}
    
    def create_meeting_from_transcript(self, transcript: str, auto_link_people: bool = True) -> Optional[Dict[str, Any]]:
        """
        Process a transcript and create a meeting page in Notion.
        
        Args:
            transcript: Raw meeting transcript
            auto_link_people: Whether to automatically link people
            
        Returns:
            Created Notion page data or None if failed
        """
        print("📝 Creating meeting from transcript...")
        
        # Extract structured data using LLM
        extracted_data = self.process_transcript(transcript)
        
        if not extracted_data:
            print("❌ Failed to extract data from transcript")
            return None
        
        # Prepare the meeting data
        meeting_name = extracted_data.get('meeting_name', 'Untitled Meeting')
        meeting_date = extracted_data.get('meeting_date', datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000-07:00'))
        meeting_type = extracted_data.get('meeting_type', 'Standard Meeting')
        
        # Create comprehensive text content
        text_content = self._format_meeting_content(extracted_data)
        
        # Create additional properties for action items and decisions
        additional_properties = {}
        
        # Add action items if there's a rich text field for them
        action_items = extracted_data.get('action_items', [])
        if action_items:
            action_text = self._format_action_items(action_items)
            # You might want to add this to a specific property if it exists in your schema
            text_content += f"\n\n## Action Items\n{action_text}"
        
        # Create the meeting page
        result = self.notion_manager.add_meeting_page(
            meeting_name=meeting_name,
            meeting_date=meeting_date,
            meeting_type=meeting_type,
            text_content=text_content,
            auto_link_people=auto_link_people,
            additional_properties=additional_properties
        )
        
        if result:
            print(f"✅ Successfully created meeting: {meeting_name}")
            
            # Print summary of what was extracted
            attendees = extracted_data.get('attendees', [])
            if attendees:
                print(f"👥 Attendees: {', '.join(attendees)}")
            
            action_items = extracted_data.get('action_items', [])
            if action_items:
                print(f"📋 Action items: {len(action_items)} items extracted")
            
            decisions = extracted_data.get('key_decisions', [])
            if decisions:
                print(f"🎯 Key decisions: {len(decisions)} decisions recorded")
        
        return result
    
    def _format_meeting_content(self, extracted_data: Dict[str, Any]) -> str:
        """
        Format the extracted data into comprehensive meeting content.
        
        Args:
            extracted_data: Data extracted by LLM
            
        Returns:
            Formatted text content
        """
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
        
        # Add next steps
        next_steps = extracted_data.get('next_steps', [])
        if next_steps:
            steps_text = '\n'.join([f"• {step}" for step in next_steps])
            content_parts.append(f"## Next Steps\n{steps_text}")
        
        return '\n\n'.join(content_parts)
    
    def _format_action_items(self, action_items: List[Dict[str, Any]]) -> str:
        """
        Format action items into readable text.
        
        Args:
            action_items: List of action item dictionaries
            
        Returns:
            Formatted action items text
        """
        if not action_items:
            return ""
        
        formatted_items = []
        for item in action_items:
            task = item.get('task', '')
            assignee = item.get('assignee', '')
            due_date = item.get('due_date', '')
            
            item_text = f"• {task}"
            if assignee:
                item_text += f" (Assigned to: {assignee})"
            if due_date:
                item_text += f" (Due: {due_date})"
            
            formatted_items.append(item_text)
        
        return '\n'.join(formatted_items)


def main():
    """
    Test the transcript processor with a sample transcript.
    """
    # Load environment variables
    notion_token = os.getenv('NOTION_TOKEN')
    meetings_db_id = os.getenv('DATABASE_ID')
    people_db_id = os.getenv('PEOPLE_DATABASE_ID')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not all([notion_token, meetings_db_id, openai_api_key]):
        print("❌ Missing required environment variables:")
        print("Please set NOTION_TOKEN, DATABASE_ID, and OPENAI_API_KEY")
        return
    
    # Initialize processor
    processor = TranscriptProcessor(notion_token, meetings_db_id, people_db_id, openai_api_key)
    
    # Sample transcript for testing
    sample_transcript = """
Meeting: Weekly Team Standup
Date: 2025-05-28
Time: 10:00 AM

John: Good morning everyone. Let's start with our weekly standup. Sarah, can you give us an update on the client project?

Sarah: Sure! I've completed the initial wireframes for the dashboard. The client feedback was positive, but they want us to add a new analytics section. I'll need to coordinate with Mike on the backend API for that.

Mike: I can have the analytics API ready by Friday. Sarah, let's sync up tomorrow to go over the data structure.

John: Great. What about the mobile app, Alex?

Alex: The iOS version is almost done. Just fixing some UI bugs. Android version should be ready for testing next week. I'll need someone to help with QA testing.

Sarah: I can help with QA testing on Thursday and Friday.

John: Perfect. Any blockers or concerns?

Mike: The database migration is taking longer than expected. Might need to push the deployment to next Monday instead of Friday.

John: Okay, let's plan for Monday deployment then. Action items: Sarah will coordinate with Mike on analytics API, Alex will finish mobile app bugs, and Sarah will help with QA testing. Mike, keep us posted on the database migration progress.

Sarah: Sounds good. Should we schedule a deployment review meeting for Monday morning?

John: Yes, let's do 9 AM Monday. I'll send out the calendar invite.

Meeting ended at 10:25 AM.
"""
    
    print("🧪 Testing Transcript Processor")
    print("=" * 50)
    
    # Process the transcript
    result = processor.create_meeting_from_transcript(sample_transcript)
    
    if result:
        print(f"\n✅ Meeting created successfully!")
        print(f"Page URL: {result.get('url', 'N/A')}")
    else:
        print("\n❌ Failed to create meeting from transcript")


if __name__ == "__main__":
    main()
