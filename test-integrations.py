#!/usr/bin/env python3
"""
Test script to verify Ollama and Lexoffice connectivity
"""
import os
import sys
import requests

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from api.ollama_classifier import OllamaClassifier
from api.lexoffice_client import LexofficeClient

def test_ollama():
    """Test Ollama connectivity"""
    print("\n=== Testing Ollama Connection ===")
    classifier = OllamaClassifier()
    
    if classifier.health_check():
        print("✅ Ollama is reachable!")
        print(f"   API URL: {classifier.api_url}")
        print(f"   Model: {classifier.model}")
        
        # Test classification with sample text
        sample_text = """
        RECHNUNG
        
        Rechnung-Nr.: RE-2024-001
        Datum: 15.01.2024
        
        Von: Baumarkt Hornbach GmbH
        An: Musterfirma GmbH
        
        Position: Schrauben Set
        Betrag: 119,00 EUR inkl. MwSt.
        """
        
        print("\n   Testing classification...")
        result = classifier.classify_document(sample_text)
        print(f"   Result: {result}")
        return True
    else:
        print("❌ Ollama is NOT reachable!")
        print(f"   Make sure Ollama is running on {classifier.api_url}")
        print("   Install: https://ollama.ai")
        print("   Or run: docker run -d -p 11434:11434 ollama/ollama")
        return False

def test_lexoffice():
    """Test Lexoffice connectivity"""
    print("\n=== Testing Lexoffice Connection ===")
    client = LexofficeClient()
    
    if not client.api_key:
        print("❌ Lexoffice API Key not configured!")
        print("   Set LEXOFFICE_API_KEY in .env file")
        return False
    
    print(f"✅ API Key configured (length: {len(client.api_key)})")
    
    if client.health_check():
        print("✅ Lexoffice API is reachable!")
        print(f"   API URL: {client.api_url}")
        
        # Get profile
        profile = client.get_profile()
        if profile:
            print(f"\n   Profile Info:")
            print(f"   - Organization: {profile.get('companyName', 'N/A')}")
            print(f"   - User: {profile.get('created', {}).get('userName', 'N/A')}")
            print(f"   - Email: {profile.get('created', {}).get('userEmail', 'N/A')}")
        return True
    else:
        print("❌ Lexoffice API is NOT reachable!")
        print("   Check API key and internet connection")
        return False

def main():
    print("="*50)
    print("Ollama + Lexoffice Integration Test")
    print("="*50)
    
    ollama_ok = test_ollama()
    lexoffice_ok = test_lexoffice()
    
    print("\n=== Summary ===")
    print(f"Ollama:    {'✅ OK' if ollama_ok else '❌ FAILED'}")
    print(f"Lexoffice: {'✅ OK' if lexoffice_ok else '❌ FAILED'}")
    
    if ollama_ok and lexoffice_ok:
        print("\n🎉 All systems operational!")
        return 0
    else:
        print("\n⚠️  Some systems need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
