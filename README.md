# Astra AI-Driven Productivity & Project Management Assistant

## 🚀 Overview

Astra is a sophisticated, industrial-ready voice assistant available in two distinct editions:

- **🏠 Home Edition**: Free for personal use with 5-user expansion packs ($10 per 5 additional users)
- **🏢 Enterprise Edition**: Commercial-grade solution for businesses with advanced security and collaboration features

## 📋 Features

### Home Edition Features
- Voice recognition and synthesis (offline-first)
- Personal productivity tools (calculator, timer, reminders, notes)
- Health and lifestyle tracking
- Learning assistance and educational tools
- Basic automation and workflow management
- File management and system monitoring
- Weather, translation, and web search capabilities

### Enterprise Edition Features
- All Home Edition features plus:
- Multi-user authentication and role-based access control
- Advanced security and compliance tools
- Team collaboration and project management
- Enterprise-grade encryption and audit logging
- Custom integrations and API access
- Advanced analytics and reporting

## 🛠️ Technical Stack

- **Backend**: Python with FastAPI, asyncio
- **Frontend**: Flutter with Material 3
- **AI Models**: DeepSeek V3 0324 (OpenRouter), Vosk (offline ASR), Piper (offline TTS)
- **Database**: SQLCipher-encrypted SQLite
- **Security**: AES-256 encryption, TLS 1.3, hardware fingerprinting
- **Deployment**: Inno Setup (Windows), APK/AAB (Android)

## 🏗️ Architecture

```
astra/
├── core/                 # Core backend services
├── home_edition/         # Home edition specific code
├── enterprise_edition/   # Enterprise edition specific code
├── shared/              # Shared utilities and components
├── frontend/            # Flutter application
├── models/              # AI models and weights
├── docs/                # Documentation
├── scripts/             # Build and deployment scripts
└── tests/               # Test suites
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Flutter 3.16+
- Windows 10/11 (for development)
- Android Studio (for mobile development)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/astra.git
cd astra
```

2. Set up Python environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up Flutter:
```bash
cd frontend
flutter pub get
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

### Development

1. Start the backend server:
```bash
python -m astra.core.server
```

2. Start the Flutter frontend:
```bash
cd frontend
flutter run
```

## 📦 Deployment

### Home Edition
- Windows: Single-click installer via Inno Setup
- Android: APK/AAB package
- Self-contained with all dependencies

### Enterprise Edition
- Windows: Enterprise installer with license validation
- Docker containers for server deployment
- Kubernetes charts for cloud deployment

## 🔒 Security

- AES-256 encryption for all data
- Hardware fingerprinting for license validation
- Anti-tampering and anti-debugging protection
- Role-based access control (Enterprise)
- Audit logging and compliance features

## 📄 License

- **Home Edition**: Free for personal use, expansion packs available
- **Enterprise Edition**: Commercial license required
- See [LICENSE.md](LICENSE.md) for details

## 🤝 Contributing

This is a commercial project. Please contact us for contribution guidelines.

## 📞 Support

- Home Edition: Community forums and documentation
- Enterprise Edition: 24/7 priority support with dedicated account management

---

**Astra Technologies**  
**Copyright © 2024. All Rights Reserved.** 