#!/usr/bin/env python3
"""
Test script for Astra Voice Assistant
Verifies core functionality without requiring voice input
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import config
from src.ai.deepseek_client import deepseek_client
from src.core.voice_assistant import voice_assistant
from src.core.feature_manager import FeatureManager
from src.core.intent_recognizer import IntentRecognizer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    try:
        assert config.server_host == "0.0.0.0"
        assert config.server_port == 8000
        assert config.wake_word == "astra"
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_intent_recognition():
    """Test intent recognition"""
    print("\n🎯 Testing intent recognition...")
    try:
        recognizer = IntentRecognizer()
        
        # Test weather intent
        intent = recognizer.recognize_intent("What's the weather like?")
        assert intent is not None
        assert intent["feature"] == "weather"
        print("✅ Weather intent recognized")
        
        # Test time intent
        intent = recognizer.recognize_intent("What time is it?")
        assert intent is not None
        assert intent["feature"] == "time"
        print("✅ Time intent recognized")
        
        # Test calculator intent
        intent = recognizer.recognize_intent("Calculate 5 plus 3")
        assert intent is not None
        assert intent["feature"] == "calculator"
        print("✅ Calculator intent recognized")
        
        print("✅ Intent recognition working")
        return True
    except Exception as e:
        print(f"❌ Intent recognition test failed: {e}")
        return False

def test_feature_manager():
    """Test feature manager"""
    print("\n⚙️ Testing feature manager...")
    try:
        manager = FeatureManager()
        
        # Check available features
        features = manager.get_available_features()
        assert len(features) > 0
        print(f"✅ Found {len(features)} features")
        
        # Check enabled features
        enabled = manager.get_enabled_features()
        print(f"✅ {len(enabled)} features enabled")
        
        # Test feature info
        if "weather" in features:
            info = manager.get_feature_info("weather")
            assert info is not None
            print("✅ Feature info retrieval working")
        
        print("✅ Feature manager working")
        return True
    except Exception as e:
        print(f"❌ Feature manager test failed: {e}")
        return False

async def test_deepseek_client():
    """Test DeepSeek client"""
    print("\n🤖 Testing DeepSeek client...")
    try:
        # Test greeting
        greeting = deepseek_client.get_greeting()
        assert len(greeting) > 0
        print(f"✅ Greeting: {greeting}")
        
        # Test joke
        joke = deepseek_client.get_joke()
        assert len(joke) > 0
        print(f"✅ Joke: {joke}")
        
        # Test conversation summary
        summary = deepseek_client.get_conversation_summary()
        assert summary is not None
        print("✅ Conversation summary working")
        
        print("✅ DeepSeek client working")
        return True
    except Exception as e:
        print(f"❌ DeepSeek client test failed: {e}")
        return False

def test_voice_assistant():
    """Test voice assistant core"""
    print("\n🎤 Testing voice assistant core...")
    try:
        # Test status
        status = voice_assistant.get_status()
        assert status is not None
        assert "is_running" in status
        print("✅ Status retrieval working")
        
        # Test text processing
        response = voice_assistant.process_text_command("What time is it?")
        assert response is not None
        print(f"✅ Text processing: {response}")
        
        print("✅ Voice assistant core working")
        return True
    except Exception as e:
        print(f"❌ Voice assistant test failed: {e}")
        return False

async def test_features():
    """Test individual features"""
    print("\n🔧 Testing individual features...")
    try:
        # Test time feature
        from src.features.time import TimeFeature
        time_feature = TimeFeature()
        result = await time_feature.execute({}, "What time is it?")
        assert result["success"]
        print(f"✅ Time feature: {result['response']}")
        
        # Test calculator feature
        from src.features.calculator import CalculatorFeature
        calc_feature = CalculatorFeature()
        result = await calc_feature.execute({"expression": "5+3"}, "Calculate 5 plus 3")
        assert result["success"]
        print(f"✅ Calculator feature: {result['response']}")
        
        print("✅ Individual features working")
        return True
    except Exception as e:
        print(f"❌ Features test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Astra Voice Assistant Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Intent Recognition", test_intent_recognition),
        ("Feature Manager", test_feature_manager),
        ("DeepSeek Client", test_deepseek_client),
        ("Voice Assistant", test_voice_assistant),
        ("Features", test_features),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Astra is ready to use.")
        print("\nTo start Astra:")
        print("  python main.py")
        print("\nTo start with API server:")
        print("  python main.py --server-only")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 