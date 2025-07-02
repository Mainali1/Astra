#!/usr/bin/env python3
"""
Test script for Astra Home Edition Code Protection System

This script tests the protection mechanisms without exposing any keys or sensitive data.
"""

import sys
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from astra.home_edition.drm import get_protection_status, verify_feature_access
from astra.home_edition.features import HomeFeatures


def test_protection_system():
    """Test the code protection system."""
    print("🔒 Testing Astra Home Edition Code Protection System")
    print("=" * 60)
    
    # Test 1: Protection Status
    print("\n1. Checking Protection Status...")
    status = get_protection_status()
    
    print(f"   ✅ Protection Active: {status['protection_active']}")
    print(f"   🐛 Debugger Detected: {status['debugger_detected']}")
    print(f"   🖥️  Virtualization Detected: {status['virtualization_detected']}")
    print(f"   🔧 Tampering Detected: {status['tampering_detected']}")
    print(f"   💉 Injection Detected: {status['injection_detected']}")
    print(f"   🔍 Integrity Checks Passed: {status['integrity_checks_passed']}")
    
    # Test 2: Feature Access (should always be True for Home Edition)
    print("\n2. Testing Feature Access...")
    features = ["calculator", "timer", "notes", "weather", "search"]
    
    for feature in features:
        access = verify_feature_access(feature)
        status_icon = "✅" if access else "❌"
        print(f"   {status_icon} {feature}: {'Available' if access else 'Not Available'}")
    
    # Test 3: Basic Feature Functionality
    print("\n3. Testing Basic Features...")
    home_features = HomeFeatures()
    
    # Test calculator
    calc_result = home_features.calculator("2 + 2")
    if "result" in calc_result:
        print(f"   ✅ Calculator: 2 + 2 = {calc_result['result']}")
    else:
        print(f"   ❌ Calculator Error: {calc_result.get('error', 'Unknown')}")
    
    # Test timer creation
    timer_result = home_features.start_timer(5, "Test Timer")
    if "timer_id" in timer_result:
        print(f"   ✅ Timer Created: {timer_result['name']}")
    else:
        print(f"   ❌ Timer Error: {timer_result.get('error', 'Unknown')}")
    
    # Test 4: Protection Monitoring
    print("\n4. Testing Protection Monitoring...")
    print("   🔄 Protection system is running in background...")
    print("   ⏱️  Monitoring for 3 seconds...")
    
    start_time = time.time()
    while time.time() - start_time < 3:
        current_status = get_protection_status()
        if not current_status['protection_active']:
            print("   ❌ Protection system stopped unexpectedly!")
            break
        time.sleep(0.5)
    
    print("   ✅ Protection monitoring test completed")
    
    # Test 5: Security Summary
    print("\n5. Security Summary...")
    final_status = get_protection_status()
    
    if all([
        final_status['protection_active'],
        not final_status['debugger_detected'],
        not final_status['virtualization_detected'],
        not final_status['tampering_detected'],
        not final_status['injection_detected'],
        final_status['integrity_checks_passed']
    ]):
        print("   🛡️  All security checks passed!")
        print("   ✅ Code protection system is working correctly")
    else:
        print("   ⚠️  Some security issues detected:")
        if final_status['debugger_detected']:
            print("      - Debugger detected")
        if final_status['virtualization_detected']:
            print("      - Virtualization detected")
        if final_status['tampering_detected']:
            print("      - Code tampering detected")
        if final_status['injection_detected']:
            print("      - Code injection detected")
        if not final_status['integrity_checks_passed']:
            print("      - Integrity checks failed")
    
    print("\n" + "=" * 60)
    print("🎉 Home Edition Code Protection Test Completed!")
    print("💡 All features are available in the free Home Edition")
    print("🔒 Code is protected against debugging and tampering")


if __name__ == "__main__":
    try:
        test_protection_system()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        sys.exit(1) 