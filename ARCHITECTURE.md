# Mental Wellness AI Agent - Architecture & Getting Started Guide

## 🏗️ System Architecture

### Multi-Agent Design

This system implements a **2-agent collaborative architecture** where specialized agents work together to provide comprehensive mental wellness support.

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Telegram)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  AGENT ORCHESTRATOR                         │
│         Coordinates collaboration between agents             │
└───────────┬─────────────────────────┬───────────────────────┘
            │                         │
            ▼                         ▼
┌───────────────────────┐  ┌─────────────────────────────────┐
│   ANALYSIS AGENT      │  │    MESSAGING AGENT              │
│ (Gemini 2.0 Flash     │  │  (Gemini 2.0 Flash)             │
│      Thinking)        │  │                                 │
├───────────────────────┤  ├─────────────────────────────────┤
│ Responsibilities:     │  │ Responsibilities:               │
│ • Emotional Analysis  │  │ • User Communication            │
│ • Crisis Detection    │  │ • Daily Check-ins (4x/day)      │
│ • Wellness Planning   │  │ • Crisis Intervention           │
│ • Progress Tracking   │  │ • Empathetic Responses          │
│ • Calendar Scheduling │  │ • Task Reminders                │
│ • Music Curation      │  │ • Safety Monitoring             │
└───────┬───────────────┘  └─────────┬───────────────────────┘
        │                            │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  SHARED RESOURCES          │
        ├────────────────────────────┤
        │ • Vertex AI Memory Store   │
        │ • Telegram MCP Server      │
        │ • Google Calendar Server   │
        │ • Spotify Server           │
        │ • Task Scheduler           │
        └────────────────────────────┘
```

### Agent Specialization

#### 1️⃣ Analysis Agent
**Model**: Gemini 2.0 Flash Thinking (Deep reasoning)

**Core Functions**:
- **Emotional Analysis**: Identifies primary and secondary mental states (sadness, anxiety, loneliness, etc.)
- **Intensity Assessment**: Categorizes severity (low → moderate → high → severe)
- **Crisis Detection**: Identifies high-risk situations requiring immediate intervention
- **Wellness Plan Generation**: Creates personalized 7-day programs with:
  - Daily themes and goals
  - Therapeutic activities
  - Coping strategies (CBT, DBT, MBSR)
  - Progressive task scheduling
- **Resource Coordination**:
  - Schedules tasks in Google Calendar
  - Curates therapeutic Spotify playlists
  - Tracks progress and adjusts plans

**Example Analysis Output**:
```json
{
  "primary_state": "sadness",
  "secondary_states": ["loneliness", "anxiety"],
  "intensity": "moderate",
  "triggers": ["recent breakup", "social isolation"],
  "risk_level": "low",
  "wellness_plan": {
    "duration_days": 7,
    "daily_themes": [...],
    "tasks": [...],
    "coping_strategies": [...]
  }
}
```

#### 2️⃣ Messaging Agent
**Model**: Gemini 2.0 Flash (Fast, empathetic communication)

**Core Functions**:
- **Initial Report Delivery**: Communicates analysis results warmly and clearly
- **Daily Check-ins**: Conducts 4 check-ins per day at:
  - 09:00 - Morning energy assessment
  - 13:00 - Midday reflection
  - 17:00 - Evening stress check
  - 21:00 - Night review
- **Crisis Monitoring**: Continuously scans for crisis indicators:
  - Self-harm mentions
  - Suicidal ideation
  - Severe hopelessness
  - **Action**: Immediate intervention with emergency resources
- **Empathetic Communication**: 
  - Warm, non-judgmental tone
  - Active listening patterns
  - Validation and encouragement
- **Task Reminders**: Sends motivational reminders for wellness activities
- **Progress Updates**: Shares insights on user's journey

**Example Check-in Flow**:
```
Messaging Agent: "Good morning! 🌅 How did you sleep last night? 
                  On a scale of 1-10, how's your energy level?"

User: "I slept okay, maybe 6 hours. Energy is about a 4/10."

Messaging Agent: "Thanks for sharing. A 4/10 is understandable given 
                  what you're going through. Let's focus on small wins 
                  today. Have you tried the breathing exercise from 
                  your plan? Even 5 minutes can help. 💙"
```

#### 🎭 Orchestrator
**Coordinates Agent Collaboration**:

**New User Flow**:
1. User sends initial message
2. Orchestrator → Analysis Agent: Analyze condition
3. Analysis Agent → Returns: Mental state + wellness plan
4. Analysis Agent → Coordinates: Calendar events + music playlist
5. Orchestrator → Messaging Agent: Deliver comprehensive report
6. Messaging Agent → User: Personalized welcome + plan overview

**Daily Check-in Flow**:
1. Scheduler triggers check-in
2. Orchestrator → Messaging Agent: Conduct check-in
3. Messaging Agent → User: Check-in questions
4. User responds
5. Messaging Agent → Processes response (crisis check)
6. If crisis: Immediate intervention
7. If normal: Empathetic response + encouragement

**Progress Tracking Flow**:
1. Every 7 check-ins (~2 days)
2. Orchestrator → Analysis Agent: Analyze progress
3. Analysis Agent → Returns: Progress insights
4. Orchestrator → Messaging Agent: Send update
5. Messaging Agent → User: Encouraging progress report

---

## 🛠️ Technology Stack

### AI/ML
- **Google Gemini 2.0 Flash Thinking**: Analysis Agent (deep reasoning)
- **Google Gemini 2.0 Flash**: Messaging Agent (fast responses)
- **Google Vertex AI**: Memory storage and RAG-based retrieval

### Communication
- **Telegram Bot API**: Primary messaging platform
- **MCP (Model Context Protocol)**: Service integration layer

### Services
- **Google Calendar API**: Wellness task scheduling
- **Spotify API**: Therapeutic music recommendations

### Infrastructure
- **APScheduler**: Task and check-in scheduling
- **Loguru**: Advanced logging
- **Pydantic**: Data validation

---

## 📦 Project Structure

```
c:\program zero\
│
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── .env                            # Configuration (create from .env.example)
├── ARCHITECTURE.md                 # This file
│
├── config/                         # Configuration
│   ├── __init__.py
│   ├── settings.py                # Environment settings
│   └── mental_states.py           # Mental state definitions
│
├── core/                          # Core system
│   ├── memory.py                  # Vertex AI memory manager
│   ├── scheduler.py               # Check-in & task scheduler
│   │
│   └── agents/                    # Multi-agent system
│       ├── __init__.py
│       ├── analysis_agent.py      # Analysis Agent
│       ├── messaging_agent.py     # Messaging Agent
│       └── orchestrator.py        # Agent coordinator
│
├── mcp/                           # MCP Servers
│   ├── __init__.py
│   ├── telegram_server.py         # Telegram integration
│   ├── calendar_server.py         # Google Calendar
│   └── spotify_server.py          # Spotify integration
│
├── models/                        # Data models
│   ├── __init__.py
│   ├── user.py                    # User profiles & sessions
│   └── task.py                    # Wellness tasks
│
└── utils/                         # Utilities
    ├── __init__.py
    ├── prompts.py                 # AI prompt templates
    └── coping_strategies.py       # Evidence-based strategies
```

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**
2. **Google Cloud Account** (for Vertex AI)
3. **Telegram Bot Token** (from @BotFather)
4. **Google AI API Key** (from Google AI Studio)

### Step 1: Install Dependencies

```powershell
# Install all required packages
pip install -r requirements.txt
```

### Step 2: Set Up Google Cloud

1. **Create a Google Cloud Project**:
   - Go to https://console.cloud.google.com
   - Create new project: "mental-wellness-agent"

2. **Enable Required APIs**:
   ```
   - Vertex AI API
   - Google Calendar API (optional)
   - Cloud Storage API
   ```

3. **Create Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Create service account: "wellness-agent"
   - Grant roles:
     - Vertex AI User
     - Cloud Storage Admin
   - Create JSON key → Download as `service-account.json`

4. **Set Up Vertex AI Memory**:
   - The system will auto-create RAG corpus on first run

### Step 3: Get API Keys

#### Google AI API Key
1. Visit https://makersuite.google.com/app/apikey
2. Create API key
3. Copy key for `.env` file

#### Telegram Bot Token
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Follow instructions:
   - Bot name: "Mental Wellness Assistant"
   - Username: "your_wellness_bot"
4. Copy the token provided

#### Google Calendar (Optional)
1. Go to https://console.cloud.google.com
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials
4. Download as `credentials.json` in project root

#### Spotify (Optional)
1. Go to https://developer.spotify.com/dashboard
2. Create app: "Mental Wellness Music"
3. Copy Client ID and Client Secret

### Step 4: Configure Environment

```powershell
# Copy example configuration
Copy-Item .env.example .env

# Edit .env with your credentials
notepad .env
```

**Required Configuration** (`.env`):
```env
# Google AI
GOOGLE_API_KEY=your_google_api_key_from_makersuite
GEMINI_MODEL=gemini-2.0-flash-thinking-exp

# Google Cloud / Vertex AI
GOOGLE_PROJECT_ID=your-gcp-project-id
GOOGLE_LOCATION=us-central1
GOOGLE_CREDENTIALS_PATH=service-account.json

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather

# Application
CHECK_IN_TIMES=09:00,13:00,17:00,21:00
PROGRAM_DURATION_DAYS=7
LOG_LEVEL=INFO
```

**Optional Configuration**:
```env
# Google Calendar (optional)
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json
GOOGLE_CALENDAR_TOKEN_PATH=token.json

# Spotify (optional)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

### Step 5: Run the System

```powershell
# Start the multi-agent system
python main.py
```

**Expected Output**:
```
======================================================================
Initializing Mental Wellness Multi-Agent System
======================================================================
✓ Configuration validated
Initializing Vertex AI Memory Store...
✓ Memory system initialized
Initializing MCP Servers...
✓ Telegram server initialized
✓ Google Calendar server initialized
✓ Spotify server initialized
Initializing Multi-Agent Orchestrator...
✓ Agent orchestrator initialized
  → Analysis Agent: Ready (Gemini 2.0 Flash Thinking)
  → Messaging Agent: Ready (Gemini 2.0 Flash)
✓ Scheduler initialized
======================================================================
Mental Wellness Multi-Agent System Ready!
======================================================================
🚀 Starting Mental Wellness Multi-Agent System
======================================================================
✓ Telegram bot running
✓ Scheduler running
======================================================================
✅ System is now ACTIVE and monitoring for users
======================================================================

Active Components:
  • Analysis Agent (Gemini 2.0 Flash Thinking)
  • Messaging Agent (Gemini 2.0 Flash)
  • Telegram Bot
  • Google Calendar: ✓
  • Spotify: ✓
  • Vertex AI Memory Store
  • Task Scheduler

Press Ctrl+C to stop the system
======================================================================
```

---

## 🧪 Testing Your Agent

### Test 1: Basic Functionality

1. **Find your bot on Telegram**:
   - Search for your bot username
   - Click "Start" or send `/start`

2. **Send initial message**:
   ```
   I'm feeling really sad and lonely. I just broke up with my 
   boyfriend yesterday and I don't have anyone to talk to about it.
   ```

3. **Expected Response**:
   - Analysis Agent analyzes: sadness + loneliness (moderate)
   - Generates 7-day wellness plan
   - Messaging Agent delivers warm, comprehensive report
   - Calendar events created (if configured)
   - Spotify playlist suggested (if configured)

### Test 2: Check-in System

1. **Wait for scheduled time** (09:00, 13:00, 17:00, or 21:00)
2. **Bot sends check-in**:
   ```
   Good morning! 🌅 How did you sleep? On a scale of 1-10, 
   how would you rate your energy level right now?
   ```
3. **Respond naturally**:
   ```
   I slept okay, about 6 hours. Energy is maybe a 5/10.
   ```
4. **Bot provides empathetic response** and tracks progress

### Test 3: Crisis Detection

**⚠️ Test Carefully** - This triggers emergency response

1. **Send crisis indicator**:
   ```
   I don't think I can go on anymore. I feel hopeless.
   ```

2. **Expected Response**:
   - Messaging Agent **immediately** detects crisis
   - Sends emergency resources (988, Crisis Text Line)
   - Marks session as high-risk
   - Logs critical event

### Test 4: Progress Tracking

1. **Complete several check-ins** (at least 7)
2. **After 2 days**, system automatically:
   - Analysis Agent analyzes progress
   - Messaging Agent sends encouraging update
   - Shows improvements and areas of focus

---

## 📊 Understanding System Behavior

### Mental State Detection

**Supported States** (10 total):
```python
- Sadness         - Depression
- Loneliness      - Overwhelm
- Anxiety         - Fear
- Anger           - Hopelessness
- Grief           - Stress
```

**Intensity Levels**:
- **Low**: Mild discomfort, manageable
- **Moderate**: Noticeable impact on daily life
- **High**: Significant distress, affecting function
- **Severe**: Crisis-level, requires immediate support

### Wellness Plan Generation

**Analysis Agent creates**:
- **Day 1-2**: Stabilization & grounding
- **Day 3-4**: Building coping skills
- **Day 5-6**: Social connection & meaning
- **Day 7**: Integration & reflection

**Task Types**:
- Breathing exercises (5-10 min)
- Physical activity (20-30 min)
- Journaling prompts (15 min)
- Social connection activities
- Mindfulness practices
- Creative expression

### Check-in Schedule

**4 Daily Check-ins**:
```
09:00 → Morning Assessment
        - Sleep quality
        - Energy level
        - Morning intentions

13:00 → Midday Reflection
        - Morning task completion
        - Stress check
        - Afternoon planning

17:00 → Evening Check
        - Day review
        - Emotional state
        - Evening wind-down

21:00 → Night Review
        - Day summary
        - Gratitude practice
        - Sleep preparation
```

---

## 🔒 Safety & Privacy

### Crisis Intervention

**Automatic Detection**:
- Keywords: "suicide", "self-harm", "want to die", etc.
- Risk level from AI analysis
- Sudden mood deterioration

**Immediate Actions**:
1. Messaging Agent sends crisis resources
2. Session marked as high-risk
3. Critical event logged
4. Continuous monitoring enabled

**Emergency Resources**:
```
988 - Suicide & Crisis Lifeline (US)
Crisis Text Line - Text HOME to 741741
International Hotlines provided
```

### Data Privacy

**What's Stored**:
- User ID (Telegram chat_id)
- Conversation history (30 days)
- Session data & progress
- Mood scores & completed tasks

**What's NOT Stored**:
- Real names (unless user provides)
- Personal identifying information
- Third-party data

**Storage**:
- Google Vertex AI (encrypted at rest)
- 30-day retention policy
- Auto-cleanup of old data

---

## 🛠️ Troubleshooting

### Common Issues

#### "Configuration validation failed"
**Solution**:
```powershell
# Check .env file exists
Get-Content .env

# Verify required variables
$env:GOOGLE_API_KEY
$env:TELEGRAM_BOT_TOKEN
$env:GOOGLE_PROJECT_ID
```

#### "Vertex AI connection error"
**Solution**:
1. Verify `service-account.json` exists
2. Check Google Cloud project ID is correct
3. Ensure Vertex AI API is enabled
4. Verify service account has correct permissions

#### "Telegram bot not responding"
**Solution**:
1. Check bot token is correct
2. Verify bot is not running elsewhere
3. Test with `/start` command
4. Check logs: `logs/wellness_agent_*.log`

#### "Google Calendar not working"
**Solution**:
1. Ensure `credentials.json` exists
2. Run OAuth flow (will open browser)
3. Grant calendar permissions
4. Check `token.json` is created

---

## 📈 Monitoring & Logs

### Log Files

**Location**: `logs/wellness_agent_YYYY-MM-DD.log`

**Log Levels**:
- `INFO`: Normal operations
- `WARNING`: Non-critical issues
- `ERROR`: Errors (handled)
- `CRITICAL`: Crisis detections

**Example Log Entry**:
```
2025-11-30 14:23:15 | INFO     | orchestrator:handle_new_user_input - → Analysis Agent: Analyzing user condition...
2025-11-30 14:23:18 | INFO     | analysis_agent:analyze_initial_input - Analysis complete: sadness (moderate)
2025-11-30 14:23:20 | INFO     | messaging_agent:deliver_analysis_report - Analysis report delivered to user 123456789
```

### Monitoring Metrics

**Track in Logs**:
- Total users onboarded
- Crisis interventions triggered
- Check-ins completed
- Tasks scheduled
- Average session duration
- Agent response times

---

## 🎯 Next Steps

### Enhancements You Can Add

1. **Voice Support**:
   - Integrate Telegram voice messages
   - Speech-to-text analysis

2. **Wearable Integration**:
   - Heart rate monitoring
   - Sleep tracking data
   - Activity levels

3. **Group Sessions**:
   - Peer support groups
   - Moderated discussions

4. **Multilingual Support**:
   - Gemini supports 100+ languages
   - Add language detection

5. **Professional Referral**:
   - Therapist matching
   - Appointment booking
   - Progress reports for clinicians

### Customization Options

**Modify Check-in Times** (`.env`):
```env
CHECK_IN_TIMES=08:00,12:00,16:00,20:00
```

**Change Program Duration** (`.env`):
```env
PROGRAM_DURATION_DAYS=14  # 2 weeks instead of 7 days
```

**Add Mental States** (`config/mental_states.py`):
```python
class MentalState(str, Enum):
    # ... existing states ...
    BURNOUT = "burnout"
    CONFUSION = "confusion"
```

**Customize Coping Strategies** (`utils/coping_strategies.py`):
```python
COPING_STRATEGIES = {
    MentalState.SADNESS: {
        # Add your custom strategies
    }
}
```

---

## ⚖️ Ethical Considerations

### System Boundaries

**This System IS**:
✅ A supportive companion
✅ A wellness coach
✅ A crisis detector
✅ A resource provider

**This System IS NOT**:
❌ A replacement for therapy
❌ A medical diagnosis tool
❌ A prescription provider
❌ A legal advisor

### User Safety

**Always Recommended**:
- Professional therapy for moderate+ intensity
- Psychiatrist for severe depression/anxiety
- Emergency services for immediate danger
- Support groups for ongoing care

### Disclaimers

The system provides these disclaimers:
- "Supportive tool, not professional therapy"
- "Crisis resources for emergencies"
- "Consult healthcare provider for medical advice"

---

## 📞 Support

### Issues?

1. Check `ARCHITECTURE.md` (this file)
2. Review logs in `logs/` directory
3. Verify configuration in `.env`
4. Test with simple message

### Resources

- **Google Gemini**: https://ai.google.dev
- **Vertex AI**: https://cloud.google.com/vertex-ai
- **Telegram Bots**: https://core.telegram.org/bots
- **Mental Health Resources**: 988lifeline.org

---

## 📜 License & Disclaimer

**Important**: This is a supportive wellness tool, not a medical device. Always seek professional help for mental health concerns. In crisis, contact emergency services or crisis hotlines immediately.

**License**: MIT License (or your chosen license)

**Disclaimer**: Not FDA approved. Not for clinical diagnosis or treatment. Use at your own risk. Consult mental health professionals for medical advice.

---

**Built with ❤️ for mental wellness support**