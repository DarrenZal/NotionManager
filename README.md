# NotionManager

A comprehensive Python toolkit for managing Notion databases with AI-powered transcript processing, automatic entity linking, and intelligent meeting management.

## 🚀 Features

### Core Functionality
- **Notion Database Management**: Create, query, and manage Notion databases
- **AI-Powered Transcript Processing**: Convert meeting transcripts into structured summaries using OpenAI
- **Automatic Entity Linking**: Smart linking of people and projects mentioned in content
- **Meeting Page Updates**: Update existing Notion pages with AI-processed content
- **People & Project Management**: Automatic detection and linking to existing database entries

### Advanced Capabilities
- **Dynamic Date Handling**: No hardcoded dates - works on any date
- **Unlimited Content Length**: Block-based approach handles large transcripts
- **Fuzzy Matching**: 80% similarity threshold for entity recognition
- **Content Preservation**: Non-destructive updates that preserve existing content
- **Rich Text Formatting**: Professional formatting with headers, lists, and links

## 📋 Requirements

- Python 3.8+
- Notion API integration token
- OpenAI API key
- Required Python packages (see `requirements.txt`)

## 🛠 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DarrenZal/NotionManager.git
   cd NotionManager
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv notion-env
   source notion-env/bin/activate  # On Windows: notion-env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and database IDs
   ```

## ⚙️ Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

```bash
# Notion API Configuration
NOTION_TOKEN=secret_your_token_here
DATABASE_ID=your_meetings_database_id_here
OPENAI_API_KEY=sk-your_openai_api_key_here

# Optional: For automatic entity linking
PEOPLE_DATABASE_ID=your_people_database_id_here
PROJECTS_DATABASE_ID=your_projects_database_id_here
```

### Getting Your API Keys

#### Notion API Token
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the "Internal Integration Token" (starts with `secret_`)
4. Share your databases with the integration

#### Database IDs
Extract from your Notion database URLs:
- URL: `https://www.notion.so/workspace/database?v=view_id`
- Database ID is the part between `/workspace/` and `?v=`

#### OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

## 🎯 Usage

### 1. Basic Notion Database Management

```bash
# Test your Notion connection and explore database schema
python notion_manager.py
```

### 2. Add Your Transcript Files

```bash
# Place your meeting transcript (.txt files) in the transcript directory
# The directory structure will be:
# transcript/
# ├── README.md              # Instructions and examples
# ├── sample_meeting.txt     # Sample file for testing
# └── your_meeting.txt       # Your actual transcript files
```

### 3. Process Transcripts into Meeting Pages

```bash
# Create a new meeting page from transcript
python transcript_processor.py
```

### 4. Update Existing Meeting Pages

```bash
# Option 1: Interactive file selection (if multiple transcripts exist)
python update_meeting.py "https://www.notion.so/Page-Title-{page_id}?p={page_id}&pm=c"

# Option 2: Specify exact transcript filename
python update_meeting.py "https://www.notion.so/Page-Title-{page_id}?p={page_id}&pm=c" "your_meeting.txt"
```

### 5. Test People Linking

```bash
# Test automatic people detection and linking
python test_people_linking.py
```

## 📁 File Structure

```
NotionManager/
├── notion_manager.py          # Core Notion API management
├── transcript_processor.py    # AI transcript processing
├── people_manager.py         # People database management
├── update_meeting.py         # Update existing meeting pages
├── setup_env.py             # Interactive environment setup
├── test_*.py                # Test scripts
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🔧 Core Components

### NotionManager
- Database schema exploration
- Page creation and updates
- Query functionality
- Automatic people linking

### TranscriptProcessor
- AI-powered transcript analysis
- Structured data extraction
- Meeting summary generation
- Action item identification

### PeopleManager
- People database integration
- Fuzzy name matching
- Automatic entity resolution
- Relation property management

## 🤖 AI Processing Features

### Transcript Analysis
The AI extracts:
- **Meeting attendees** (with automatic linking)
- **Meeting summary** (comprehensive overview)
- **Key decisions** (important outcomes)
- **Action items** (with assignees and due dates)
- **Next steps** (follow-up actions)

### Entity Linking
Automatically creates clickable links for:
- **People mentions** → Links to People database pages
- **Project references** → Links to Projects database pages
- **Smart variations** (e.g., "Steve Keen project" → Steve Keen project page)

### Content Formatting
- **Rich text formatting** with headers and lists
- **Clickable entity links** throughout content
- **Professional structure** with clear sections
- **Content preservation** (existing notes remain intact)

## 📝 Example Workflows

### Workflow 1: New Meeting from Transcript
1. Place transcript file in `transcript/` directory
2. Run `python transcript_processor.py`
3. AI processes transcript and creates structured meeting page
4. People and projects automatically linked

### Workflow 2: Update Existing Meeting
1. Place transcript file in `transcript/` directory
2. Get Notion page URL from existing meeting page
3. Run `python update_meeting.py "<page_url>"`
4. AI summary appended to existing content with entity links

### Workflow 3: Batch Processing
1. Set up multiple transcript files
2. Use the core classes in your own scripts
3. Process multiple meetings programmatically

## 🧪 Testing

### Test Scripts
- `test_notion.py` - Test basic Notion connectivity
- `test_people_linking.py` - Test people detection and linking
- `test_transcript_processor.py` - Test AI transcript processing

### Running Tests
```bash
# Test individual components
python test_notion.py
python test_people_linking.py
python test_transcript_processor.py

# Test full workflow
python transcript_processor.py
```

## 🔍 Troubleshooting

### Common Issues

#### "Missing required environment variables"
- Ensure `.env` file exists with all required variables
- Check that API keys are valid and not expired

#### "Database not accessible"
- Verify your Notion integration has access to the databases
- Check that database IDs are correct

#### "No transcript files found"
- Place `.txt` transcript files in the `transcript/` directory
- Ensure files have `.txt` extension

#### "Could not extract page ID"
- Verify the Notion page URL format
- Try copying the URL directly from your browser

### Debug Mode
Add debug prints to any script:
```python
import os
print("Environment variables:")
for key in ['NOTION_TOKEN', 'DATABASE_ID', 'OPENAI_API_KEY']:
    value = os.getenv(key)
    print(f"{key}: {'✅ Set' if value else '❌ Missing'}")
```

## 🔒 Security

### Data Protection
- API keys stored in `.env` (excluded from git)
- Transcript files excluded from repository
- No hardcoded sensitive information

### Best Practices
- Use environment variables for all secrets
- Regularly rotate API keys
- Review transcript content before processing
- Backup important Notion data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed information

## 🔄 Updates

### Recent Features
- ✅ Universal entity linking (people + projects)
- ✅ Block-based content handling (unlimited length)
- ✅ Dynamic date processing
- ✅ Content preservation
- ✅ Rich text formatting

### Roadmap
- [ ] Batch transcript processing
- [ ] Custom entity types
- [ ] Meeting templates
- [ ] Calendar integration
- [ ] Export functionality

---

**Made with ❤️ for better meeting management**
