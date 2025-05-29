# Transcript Directory

This directory is where you should place your meeting transcript files for processing.

## 📁 File Requirements

- **File format**: `.txt` files only
- **Encoding**: UTF-8 text files
- **Content**: Raw meeting transcripts or conversation logs

## 📝 How to Add Transcripts

1. **Save your transcript** as a `.txt` file in this directory
2. **Name the file** descriptively (e.g., `team-standup-2025-05-28.txt`)
3. **Run the processing script**:
   ```bash
   # Option 1: Let the script help you choose from available files
   python update_meeting.py "<notion_page_url>"
   
   # Option 2: Specify the exact filename
   python update_meeting.py "<notion_page_url>" "your_transcript.txt"
   ```

## 🔄 Processing Workflow

1. **Place transcript file** in this directory
2. **The script automatically finds** the most recent `.txt` file
3. **AI processes the transcript** to extract:
   - Meeting attendees
   - Summary
   - Key decisions
   - Action items
   - Next steps
4. **Updates your Notion page** with structured content

## 📋 Example Transcript Format

Your transcript can be in any format, but here are some examples that work well:

### Format 1: Speaker Labels
```
John: Good morning everyone. Let's start with our weekly standup.
Sarah: I've completed the dashboard wireframes. The client feedback was positive.
Mike: I can have the analytics API ready by Friday.
```

### Format 2: Meeting Notes
```
Meeting: Weekly Team Standup
Date: 2025-05-28
Attendees: John, Sarah, Mike

- Sarah completed dashboard wireframes
- Client feedback was positive
- Mike will deliver analytics API by Friday
```

### Format 3: Raw Conversation
```
The meeting started at 10 AM with John, Sarah, and Mike present.
Sarah reported that she had finished the dashboard wireframes and received positive feedback from the client.
Mike committed to delivering the analytics API by Friday.
```

## 🔒 Security Note

- **Transcript files are excluded from git** (see `.gitignore`)
- **Your transcripts remain private** and are not uploaded to the repository
- **Only place transcripts you're comfortable processing** with AI

## 🧪 Testing

A sample transcript file is provided for testing:
- `sample_meeting.txt` - Use this to test the system before processing real transcripts

## 📞 Support

If you encounter issues with transcript processing:
1. Check that your file is saved as `.txt` with UTF-8 encoding
2. Ensure the file contains actual text content
3. Verify your OpenAI API key is configured correctly
4. Review the troubleshooting section in the main README
