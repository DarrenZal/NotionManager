# Update Meeting Script

This script updates an existing Notion meeting page with AI-processed transcript data.

## Usage

```bash
# Option 1: Interactive file selection (if multiple transcripts exist)
python update_meeting.py "<notion_page_url>"

# Option 2: Specify exact transcript filename
python update_meeting.py "<notion_page_url>" "transcript_filename.txt"
```

## Examples

```bash
# Let the script help you choose from available transcript files
python update_meeting.py "https://www.notion.so/Page-Title-{page_id}?p={page_id}&pm=c"

# Use a specific transcript file
python update_meeting.py "https://www.notion.so/Page-Title-{page_id}?p={page_id}&pm=c" "team-meeting-2025-05-28.txt"
```

## What it does

1. **Extracts page ID** from the Notion URL
2. **Finds transcript file** in `./transcript/` directory (interactive selection or specified filename)
3. **Processes transcript** with AI to extract:
   - Attendees
   - Summary
   - Key decisions
   - Action items with assignees and due dates
   - Next steps
4. **Appends to the Notion page** (preserves existing content) with structured content including original transcript

## Requirements

- Transcript file must be in `./transcript/` directory as a .txt file
- Environment variables must be set (NOTION_TOKEN, DATABASE_ID, OPENAI_API_KEY)
- The Notion page must have a "Text" property (rich text field) to update

## Supported URL Formats

The script can extract page IDs from various Notion URL formats:

- `https://www.notion.so/Page-Title-{page_id}`
- `https://www.notion.so/workspace/{page_id}`
- `https://www.notion.so/workspace/page?p={page_id}&pm=c`

## Output

The script will **append** to the Notion page (preserving existing content) with:

```
[Existing content preserved]

==================================================
# AI-Processed Meeting Summary
==================================================
```

```
**Attendees:** Graham Boyd, Steve Keen, Sarah, Mike

## Summary
[AI-generated summary of the meeting]

## Key Decisions
• Decision 1
• Decision 2

## Action Items
• Task 1 (Assigned to: Person) (Due: Date)
• Task 2 (Assigned to: Person)

## Next Steps
• Next step 1
• Next step 2

## Original Transcript
```
[Full original transcript in code block]
```
```

## Testing

A sample transcript has been created at `./transcript/sample_meeting.txt` for testing.

## Troubleshooting

- **"Could not extract page ID"**: Check the URL format
- **"No .txt files found"**: Ensure transcript file exists in the correct directory
- **"No rich text property found"**: The Notion page needs a Text/rich text property to update
- **"404 Not Found"**: Check that your integration has access to the page
