# Update Meeting Script

This script updates an existing Notion meeting page with AI-processed transcript data.

## Usage

```bash
python update_meeting.py "<notion_page_url>"
```

## Example

```bash
python update_meeting.py "https://www.notion.so/AWP-OS-1fd8b92ddc2f800a8fdcf8b771eeec11?p=2028b92ddc2f811ca933e7be5a1e00ee&pm=c"
```

## What it does

1. **Extracts page ID** from the Notion URL
2. **Finds transcript file** in `/Users/darrenzal/AWP/transcript/` (uses most recent .txt file)
3. **Processes transcript** with AI to extract:
   - Attendees
   - Summary
   - Key decisions
   - Action items with assignees and due dates
   - Next steps
4. **Appends to the Notion page** (preserves existing content) with structured content including original transcript

## Requirements

- Transcript file must be in `/Users/darrenzal/AWP/transcript/` as a .txt file
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

A sample transcript has been created at `/Users/darrenzal/AWP/transcript/sample_meeting.txt` for testing.

## Troubleshooting

- **"Could not extract page ID"**: Check the URL format
- **"No .txt files found"**: Ensure transcript file exists in the correct directory
- **"No rich text property found"**: The Notion page needs a Text/rich text property to update
- **"404 Not Found"**: Check that your integration has access to the page
