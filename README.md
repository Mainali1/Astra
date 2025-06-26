# Astra AI Assistant

Astra is a powerful, open-source AI assistant with extensive features and capabilities. It comes in two editions:

- **🏠 Home Edition**: Perfect for personal use, with a comprehensive set of features for individual productivity
- **🏢 Enterprise Edition**: Advanced features for business use, including team collaboration and enterprise security

## Features

### 🏠 Home Edition Features

#### Core Features
- 🧠 DeepSeek AI Integration
- 🗣️ Voice Recognition (Vosk)
- 🔊 Text-to-Speech (Piper)
- 🎯 Intent Recognition
- 🔄 Feature Management
- 🌐 API Server

#### Productivity
- ⛅ Weather Information (OpenWeatherMap)
- ⏰ Time & Date Utilities
- 🧮 Advanced Calculator
- 📝 Notes Management
- ⏲️ Timer & Stopwatch
- 📰 News Aggregation
- 📚 Dictionary & Thesaurus
- 🌍 Translation (50+ languages)
- 📅 Calendar Management
- 📧 Email Management
- 📁 File Management
- 🔍 Web Search (DuckDuckGo)
- 💻 System Monitoring
- 🎵 Music Player

#### Finance
- 💱 Currency Converter
- 📈 Crypto Price Tracking
- 📊 Basic Analytics

#### Automation
- 🤖 Basic Automation Rules
- 📋 Simple Workflows
- 📜 Script Management
- 📸 OCR Integration

### 🏢 Enterprise Edition Features
All Home Edition features, plus:

#### Team Features
- 📊 Project Management
- 👥 Team Collaboration
- 🔑 Role Management
- 📋 Task Assignment

#### Security & Compliance
- 📝 Audit Logging
- 🔒 Advanced Security
- ✅ Compliance Tools
- 🔐 E2E Encryption

#### Analytics & Monitoring
- 📈 Team Analytics
- 📊 Resource Monitoring
- 💳 License Management
- 📉 Usage Tracking

#### Administration
- 👤 User Management
- 🏢 Department Controls
- 💾 Enterprise Backup
- 🔄 System Recovery

#### Advanced Features
- 🔄 Custom Workflows
- 🔌 API Integration
- 🤖 Advanced Automation
- 🔗 Enterprise Integrations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/astra.git
cd astra
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy and configure environment variables:
```bash
cp env_example.txt .env
# Edit .env with your API keys and settings
```

5. Run Astra:
```bash
python main.py
```

## Configuration

### Home Edition Setup
1. Copy `env_example.txt` to `.env`
2. Set `ASTRA_EDITION=home`
3. Configure basic API keys:
   - `DEEPSEEK_API_KEY`: Your DeepSeek API key
   - `OPENWEATHER_API_KEY`: OpenWeatherMap API key
   - `NEWS_API_KEY`: NewsAPI key
   - Other API keys as needed

### Enterprise Edition Setup
1. Copy `env_example.txt` to `.env`
2. Set `ASTRA_EDITION=enterprise`
3. Obtain enterprise license file
4. Configure enterprise settings:
   - `ASTRA_LICENSE_KEY`: Your enterprise license key
   - `ASTRA_ENTERPRISE_DB_URL`: Database connection
   - `ASTRA_ENTERPRISE_REDIS_URL`: Redis connection
   - `ASTRA_ENTERPRISE_SMTP_*`: Email settings
   - Additional security settings

## Usage

### Voice Commands
1. Say "Hey Astra" to activate
2. Speak your command
3. Astra will process and respond

### Text Commands
1. Type your command in the input field
2. Press Enter or click Send
3. Astra will process and respond

## Development

### Project Structure
```
astra/
├── src/
│   ├── ai/
│   │   └── deepseek_client.py
│   ├── core/
│   │   ├── feature_manager.py
│   │   ├── intent_recognizer.py
│   │   └── voice_assistant.py
│   ├── features/
│   │   ├── calculator.py
│   │   ├── calendar.py
│   │   ├── crypto_prices.py
│   │   ├── currency_converter.py
│   │   ├── dictionary.py
│   │   ├── email_manager.py
│   │   ├── file_manager.py
│   │   ├── meeting_scheduler.py
│   │   ├── music.py
│   │   ├── news.py
│   │   ├── notes.py
│   │   ├── reminder.py
│   │   ├── system_monitor.py
│   │   ├── time.py
│   │   ├── timer.py
│   │   ├── translation.py
│   │   ├── weather.py
│   │   ├── web_search.py
│   │   └── wikipedia.py
│   ├── speech/
│   │   ├── speech_recognition.py
│   │   └── text_to_speech.py
│   └── server/
│       └── api_server.py
├── main.py
└── requirements.txt
```

### Adding New Features
1. Create feature module in `src/features/`
2. Implement feature class with required methods
3. Register feature in `feature_manager.py`
4. Add intent patterns in `intent_recognizer.py`
5. Update documentation

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is licensed under a proprietary license. See LICENSE.md for details.
- Home Edition: Free for personal use
- Enterprise Edition: Requires paid license

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/astra/issues)
- Email: 
  - Home Edition: support@astra-ai.com
  - Enterprise Edition: enterprise@astra-ai.com

## Acknowledgments

- DeepSeek AI for the language model
- Vosk for speech recognition
- Piper for text-to-speech
- All other open-source contributors

---

**Astra Technologies**  
**COPYRIGHT © 2024. ALL RIGHTS RESERVED.** 