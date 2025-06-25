# Astra Voice Assistant - Flutter Client

A beautiful, production-ready Flutter client for the Astra Voice Assistant with an ocean and night sky theme.

## Features

### 🎨 Beautiful UI/UX
- **Ocean & Night Sky Theme**: Stunning gradient backgrounds and color schemes
- **Material 3 Design**: Modern, accessible interface components
- **Responsive Layout**: Works perfectly on all screen sizes
- **Dark Mode**: Optimized for low-light environments
- **Smooth Animations**: Fluid transitions and micro-interactions

### 🎤 Voice Assistant Integration
- **Real-time Communication**: WebSocket connection for instant responses
- **Voice Waveform Visualization**: Beautiful animated voice indicators
- **Status Monitoring**: Live connection and assistant status
- **Text Input**: Type commands when voice isn't available
- **Message History**: Complete conversation tracking

### 📊 Dashboard & Analytics
- **System Status Overview**: Connection, assistant, and feature status
- **Quick Actions**: One-tap access to common commands
- **Activity Tracking**: Message counts and session statistics
- **Feature Management**: Enable/disable assistant capabilities

### ⚙️ Settings & Configuration
- **Server Configuration**: Easy IP and port setup
- **Voice Settings**: Speed, pitch, and voice selection
- **Appearance Options**: Theme and language preferences
- **Notification Controls**: Sound, vibration, and push notifications

## Screenshots

### Home Screen
- Voice waveform visualization
- Real-time status indicators
- Message conversation interface
- Quick command input

### Dashboard
- System status cards
- Quick action buttons
- Activity statistics
- Feature overview

### Features Management
- Toggle feature enable/disable
- Feature descriptions and keywords
- Visual status indicators
- Search and filter capabilities

### Settings
- Server connection settings
- Voice customization
- Appearance preferences
- Notification controls

## Architecture

### Project Structure
```
lib/
├── main.dart                 # App entry point
├── theme/
│   └── app_theme.dart        # Theme configuration
├── services/
│   └── astra_service.dart    # Backend communication
├── models/
│   └── astra_message.dart    # Data models
├── screens/
│   ├── home_screen.dart      # Main voice interface
│   ├── dashboard_screen.dart # System overview
│   ├── features_screen.dart  # Feature management
│   └── settings_screen.dart  # App configuration
└── widgets/
    ├── voice_waveform.dart   # Voice visualization
    └── feature_card.dart     # Reusable components
```

### Key Components

#### AstraService
- WebSocket connection management
- REST API communication
- Message handling and parsing
- Error handling and reconnection

#### Theme System
- Ocean and night sky color palette
- Material 3 design tokens
- Light and dark theme support
- Consistent styling across the app

#### Voice Waveform
- Animated voice visualization
- Circular and linear waveform options
- Real-time audio level display
- Processing state indicators

## Getting Started

### Prerequisites
- Flutter SDK 3.0.0 or higher
- Dart SDK 3.0.0 or higher
- Android Studio / VS Code
- Running Astra Python backend

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd astra_client
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure server connection**
   - Update `lib/services/astra_service.dart`
   - Set your server IP and port:
   ```dart
   static const String baseUrl = 'http://YOUR_SERVER_IP:8000';
   static const String wsUrl = 'ws://YOUR_SERVER_IP:8000/ws';
   ```

4. **Run the app**
   ```bash
   flutter run
   ```

### Configuration

#### Server Settings
The app connects to the Python backend via:
- **REST API**: HTTP requests for status and control
- **WebSocket**: Real-time communication for voice and text

#### Network Requirements
- Both devices must be on the same network
- Port 8000 must be accessible
- Firewall should allow WebSocket connections

## Usage

### Connecting to Server
1. Ensure the Python backend is running
2. Update server IP in settings if needed
3. The app will automatically connect on startup
4. Connection status is shown in the top bar

### Voice Commands
1. Tap "Start Assistant" to begin listening
2. Speak your command clearly
3. Wait for the response
4. Tap "Stop Assistant" when done

### Text Commands
1. Type your message in the input field
2. Press send or tap the send button
3. View the response in the conversation

### Managing Features
1. Navigate to the Features screen
2. Toggle features on/off as needed
3. View feature descriptions and keywords
4. Changes take effect immediately

## Customization

### Theme Colors
Edit `lib/theme/app_theme.dart` to customize:
- Primary colors (ocean blues)
- Accent colors (coral, seaweed green)
- Background gradients
- Text colors and styles

### Voice Settings
Configure in the Settings screen:
- Voice selection (Amy, Emma, Sarah, Lisa)
- Speed adjustment (0.5x - 2.0x)
- Pitch adjustment (0.5x - 2.0x)

### Server Configuration
Update connection settings:
- Server IP address
- Port number
- Auto-connect behavior
- Connection timeout

## Development

### Adding New Features
1. Create feature model in `models/`
2. Add API methods in `services/astra_service.dart`
3. Create UI components in `widgets/`
4. Add screens in `screens/`
5. Update navigation in `main.dart`

### Styling Guidelines
- Use `AstraTheme` colors consistently
- Follow Material 3 design principles
- Maintain ocean/night sky aesthetic
- Ensure accessibility compliance

### Testing
```bash
# Run unit tests
flutter test

# Run integration tests
flutter test integration_test/

# Run with coverage
flutter test --coverage
```

## Troubleshooting

### Connection Issues
- Verify server IP and port
- Check network connectivity
- Ensure firewall allows connections
- Restart both client and server

### Voice Problems
- Check microphone permissions
- Verify audio device selection
- Test with text input first
- Check server audio configuration

### Performance Issues
- Close other apps using audio
- Check available memory
- Update Flutter and dependencies
- Restart the app

## Dependencies

### Core Dependencies
- `http`: REST API communication
- `web_socket_channel`: Real-time messaging
- `provider`: State management
- `shared_preferences`: Local storage

### UI Dependencies
- `google_fonts`: Typography
- `cupertino_icons`: Icons
- `flutter_lints`: Code quality

### Audio Dependencies
- `audioplayers`: Audio playback
- `permission_handler`: Microphone access

### Network Dependencies
- `connectivity_plus`: Network status
- `url_launcher`: External links

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review troubleshooting guide
- Contact the development team

---

**Astra Voice Assistant** - Bringing the ocean's depth and the night sky's wonder to your voice interactions. 