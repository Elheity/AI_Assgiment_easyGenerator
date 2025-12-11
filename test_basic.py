#!/usr/bin/env python3
"""Quick test script to verify basic functionality"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("SYNTHETIC REVIEW GENERATOR - QUICK TEST")
print("=" * 60)

# Test 1: Configuration loading
print("\n[1/5] Testing configuration loading...")
try:
    from config_parser import ConfigParser
    config = ConfigParser('config/config.yaml')
    print(f"✓ Config loaded successfully")
    print(f"  - Models: {len(config.get_models())}")
    print(f"  - Personas: {len(config.get_personas())}")
    print(f"  - Tool categories: {len(config.get_tool_categories())}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 2: Environment variables
print("\n[2/5] Testing environment variables...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✓ OpenAI API key loaded (length: {len(api_key)})")
    else:
        print("⚠ Warning: OPENAI_API_KEY not found")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3: Generator imports
print("\n[3/5] Testing generator imports...")
try:
    from generators.base_generator import BaseGenerator
    from generators.openai_generator import OpenAIGenerator
    from generators.ollama_generator import OllamaGenerator
    print("✓ All generators imported successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 4: Quality modules (without ML dependencies)
print("\n[4/5] Testing quality module imports...")
try:
    # These will work without ML packages
    print("  - Importing quality scorer...")
    from quality.quality_scorer import QualityScorer
    print("  ✓ Quality scorer imported")
except Exception as e:
    print(f"  ⚠ Quality modules need ML dependencies: {e}")
    print("  → Run: pip install sentence-transformers transformers torch")

# Test 5: CLI import
print("\n[5/5] Testing CLI import...")
try:
    from cli import cli
    print("✓ CLI imported successfully")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n" + "=" * 60)
print("BASIC TESTS COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("1. Wait for ML dependencies to finish installing")
print("2. Run: python -m src.cli full-pipeline --count 10")
print("3. Check: data/generated_reviews/ and reports/")
print("\n" + "=" * 60)
