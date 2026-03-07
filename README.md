# Mental Wellness AI Agent

A compassionate, multi-agent AI system providing personalized mental wellness support through Telegram.

## 🌟 Features

- **Intelligent Analysis**: Deep emotional understanding using Gemini 2.0 Flash Thinking
- **Empathetic Communication**: Warm, supportive messaging via Gemini 2.0 Flash
- **Daily Check-ins**: 4 automated wellness check-ins per day
- **Personalized Plans**: 7-day therapeutic programs tailored to your needs
- **Crisis Detection**: Immediate intervention with emergency resources
- **Calendar Integration**: Automatic scheduling of wellness activities
- **Music Therapy**: Curated Spotify playlists for emotional regulation
- **Progress Tracking**: Continuous monitoring and plan adjustments

## 🏗️ Architecture

**Multi-Agent System**:
- **Analysis Agent**: Emotional analysis, wellness planning, resource coordination
- **Messaging Agent**: Communication, check-ins, crisis detection
- **Orchestrator**: Coordinates seamless agent collaboration

**Technology Stack**:
- Google Gemini 2.0 (Flash Thinking + Flash)
- Google Vertex AI Memory Store
- Telegram Bot API
- Google Calendar API (optional)
- Spotify API (optional)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Cloud Account
- Telegram Bot Token
- Google AI API Key

### Installation

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up configuration
Copy-Item .env.example .env
# Edit .env with your API keys

# 3. Set up Google Cloud
# - Create project
# - Enable Vertex AI API
# - Create service account
# - Download service-account.json

# 4. Run the system
python main.py
```

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture and getting started guide
- **[.env.example](.env.example)** - Configuration template

## 🧪 Testing

1. Find your bot on Telegram
2. Send `/start`
3. Share how you're feeling
4. Experience personalized support!

## 🔒 Safety

- **Crisis Detection**: Automatic identification of high-risk situations
- **Emergency Resources**: Immediate access to 988, Crisis Text Line, etc.
- **Privacy**: 30-day data retention, encrypted storage
- **Boundaries**: Clear disclaimers about professional therapy

## ⚠️ Disclaimer

This is a supportive wellness tool, **NOT** a replacement for professional mental health care. 

**In crisis, contact**:
- 988 (Suicide & Crisis Lifeline)
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911

## 📊 Supported Mental States

Sadness • Loneliness • Anxiety • Anger • Grief • Stress • Depression • Overwhelm • Fear • Hopelessness

Each with 4 intensity levels and personalized coping strategies.

## 🛠️ Customization

- Modify check-in times in `.env`
- Adjust program duration (default 7 days)
- Add custom mental states
- Extend coping strategies database

## 📈 What Happens Behind the Scenes

1. **User shares feelings** → Analysis Agent evaluates condition
2. **Agent generates plan** → 7-day personalized program
3. **Calendar scheduling** → Tasks automatically added
4. **Music curation** → Therapeutic playlists suggested
5. **Daily check-ins** → 4 times/day progress monitoring
6. **Crisis monitoring** → Continuous safety surveillance
7. **Progress tracking** → Plan adjustments based on data

## 🎯 Use Cases

- **Breakup Recovery**: Coping with relationship loss
- **Loneliness**: Building social connections
- **Work Stress**: Managing overwhelm and burnout
- **Grief Support**: Processing loss
- **Anxiety Management**: Daily grounding techniques
- **Depression Support**: Encouraging small wins

## 📝 License

MIT License - See LICENSE file for details

## 💙 Support Mental Health

Remember:
- You are not alone
- Seeking help is strength
- Recovery is possible
- Professional support is available

---

**Built with compassion for mental wellness** 🌸
