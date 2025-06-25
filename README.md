# Astra AI Assistant

Astra is a powerful, open-source AI assistant with extensive features and capabilities. It comes in two editions: Single Edition (free for individual users) and Industry Edition (for enterprise use).

## Features

### Core Features
- 🧠 DeepSeek AI Integration
- 🗣️ Voice Recognition (Vosk)
- 🔊 Text-to-Speech (Piper)
- 🎯 Intent Recognition
- 🔄 Feature Management
- 🌐 API Server

### Productivity Features
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
- 🔍 Wikipedia Integration
- 💻 System Monitoring
- 🎵 Music Player

### Coming Soon
- 🎙️ Voice Commands
- 📊 Data Analysis
- 🤖 Automation Tools
- 🔒 Security Features
- 📱 Mobile Integration

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

Astra uses environment variables for configuration. Copy `env_example.txt` to `.env` and configure:

- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `OPENWEATHERMAP_API_KEY`: OpenWeatherMap API key
- `NEWS_API_KEY`: NewsAPI key
- Other API keys as needed

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
│   │   ├── dictionary.py
│   │   ├── email_manager.py
│   │   ├── file_manager.py
│   │   ├── music.py
│   │   ├── news.py
│   │   ├── notes.py
│   │   ├── reminder.py
│   │   ├── system_monitor.py
│   │   ├── time.py
│   │   ├── timer.py
│   │   ├── translation.py
│   │   ├── weather.py
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

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/astra/issues)
- Email: support@astra-ai.com

## Acknowledgments

- DeepSeek AI for the language model
- Vosk for speech recognition
- Piper for text-to-speech
- All other open-source contributors

---

**Astra Technologies**  
**COPYRIGHT © 2024. ALL RIGHTS RESERVED.** 