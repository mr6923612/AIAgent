#!/usr/bin/env python3
"""
Ollama Model Verification Script
Verify if Ollama service is running normally and contains required models
"""

import requests
import json
import time
import sys

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Ollama service response abnormal: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Unable to connect to Ollama service (http://localhost:11434)")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama service: {str(e)}")
        return False

def get_installed_models():
    """Get list of installed models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models
        else:
            print(f"❌ Failed to get model list: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting model list: {str(e)}")
        return []

def verify_required_models():
    """Verify if required models are installed"""
    required_models = ['bge-m3', 'llama3.2:3b']
    
    print("Checking Ollama service status...")
    if not check_ollama_service():
        print("Ollama service is not running, please check service status")
        return False
    
    print("Getting installed models list...")
    installed_models = get_installed_models()
    
    if not installed_models:
        print("No installed models found")
        return False
    
    print(f"Installed models: {', '.join(installed_models)}")
    
    missing_models = []
    for model in required_models:
        if model not in installed_models:
            missing_models.append(model)
    
    if missing_models:
        print(f"Missing required models: {', '.join(missing_models)}")
        return False
    
    print("All required models are installed")
    return True

def test_model_inference():
    """Test model inference functionality"""
    print("Testing model inference...")
    
    try:
        # Test bge-m3 model
        test_data = {
            "model": "bge-m3",
            "prompt": "Hello, world!",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("bge-m3 model inference test successful")
            return True
        else:
            print(f"Model inference test failed: {response.status_code}")
            return False
                
    except Exception as e:
        print(f"Error during model inference test: {str(e)}")
        return False

def main():
    """Main function"""
    print("Starting Ollama model verification...")
    print("=" * 50)
    
    # Wait for service to start
    print("Waiting for Ollama service to start...")
    time.sleep(5)
    
    # Verify models
    if not verify_required_models():
        print("Model verification failed")
        sys.exit(1)
    
    # Test inference
    if not test_model_inference():
        print("Model inference test failed")
        sys.exit(1)
    
    print("=" * 50)
    print("All verifications passed! Ollama model configuration is correct")
    sys.exit(0)

if __name__ == "__main__":
    main()
