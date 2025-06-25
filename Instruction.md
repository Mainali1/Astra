
**Project Specification: "Astra" - Cross-Platform Local-First Voice Assistant**

**Objective:** Develop a commercial-ready, native voice assistant named "Astra" that runs as a local home server on Windows (packaged as a single-click .exe installer) with an Android client for remote access. The system must support both offline and online operation with >50 modular features, context-aware interactions, and multi-device sync via local server. All components must use free APIs/libraries with paid services only as a last resort. Heavy processing occurs on the server with Windows/Android clients acting as thin clients.

**Core Requirements:**
1. **Deployment Architecture:**
   - Windows server packaged as single .exe installer (Inno Setup) with embedded DLLs
   - Android client as self-contained APK
   - Thin-client design (clients handle I/O, server handles processing)
   - Basic LAN client-server architecture (single-user focus, scalable design)

2. **Offline Operation:**
   - Online-first with seamless fallback to offline dependencies
   - DeepSeek as default unremovable NLU engine
   - Vosk fallback for offline ASR when DeepSeek unavailable
   - Piper TTS for all voice output

3. **Feature Handling:**
   - Built-in features (time, date, etc.) handled by server-hosted code
   - External queries (movie trivia, etc.) delegated to DeepSeek
   - MVP Support: Web search, music playback, reminders

4. **Performance Constraints:**
   - ≤3GB storage footprint
   - Desktop: 8GB RAM minimum
   - Android: 4GB RAM with swap optimization

5. **Natural Interaction:**
   - Context-aware responses with learning capability
   - Female TTS voice (Piper's en_GB-amy)
   - Sassy, humorous personality profile

6. **Cross-Platform:**
   - Unified codebase with platform-specific optimizations
   - Windows (EXE), Android (APK/AAB), Linux (AppImage)

7. **Security:**
   - End-to-end encryption for all data
   - Secure local storage
   - Privacy-focused design
   - .env file for API key management

**Technical Stack:**
- **Backend Core:** Rust (Actix for server, PyO3 bindings)
- **Machine Learning:** DeepSeek (via OpenRouter API) primary, Vosk fallback
- **Speech Recognition:** Vosk (offline ASR)
- **Text-to-Speech:** Piper TTS
- **Frontend UI:** Flutter (Material 3)
- **Database:** SQLite + Automerge CRDTs
- **Packaging:**
  - Windows: Inno Setup (embedded DLLs)
  - Android: Flutter-generated APK
  - Linux: AppImage
- **APIs:** Free services only (https://free-apis.github.io)

**Implementation Guidance:**
1. Server-client communication via WebSockets
2. Thin clients send voice/text → Server processes → Returns voice/text
3. Modular architecture with lazy loading
4. Free API integration with .env toggle
5. Platform-specific code isolation when unavoidable
6. DeepSeek as default NLU (unremovable)
7. Commercial-ready code (no mock logic)

**Critical Path MVP:**
1. Windows server executable with:
   - Vosk ASR / Piper TTS integration
   - DeepSeek NLU via OpenRouter
   - Reminder system
   - Local music playback
   - Web search (DuckDuckGo API)

2. Android client with:
   - Voice I/O pipeline
   - Server connection manager
   - Basic response UI

3. LAN synchronization:
   - Device discovery (mDNS)
   - Encrypted communication (Rustls)

**Packaging Specifications:**
- Windows: Single EXE installer (Inno Setup) with:
  - Embedded server executable
  - Required DLLs
  - Auto-start service configuration
- Android: Single APK with:
  - Minimal permissions
  - LAN discovery
  - Voice I/O components
- Configuration: .env file for API keys with off switches

**DeepSeek Integration:**
- Primary NLU through OpenRouter API
- Automatic fallback to Vosk when offline
- Personality injection layer for responses
- Unremovable core component
- Free-tier usage optimization

**Free Service Matrix:**
| Function         | Service                  |
|------------------|--------------------------|
| Web Search       | DuckDuckGo API           |
| Weather          | OpenWeatherMap Free Tier |
| Translations     | LibreTranslate           |
| News             | RSS Feeds                |
| TTS              | Piper (offline)          |
| ASR              | Vosk (offline)           |

**Security Implementation:**
1. Data at rest: AES-256 encryption
2. Network: TLS 1.3 (Rustls)
3. Authentication: Voiceprint + PIN
4. Sandboxed plugin execution
5. Regular audit schedule