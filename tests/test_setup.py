"""
Example test script to verify the system works
Run this after setting up your API key
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_basic_import():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from root_agent import create_root_agent
        from agents.search_agent import create_search_agent
        from agents.summarize_agent import create_summarizer_agent
        from agents.synthesize_agent import create_synthesizer_agent
        from agents.gap_finder_agent import create_gap_finder_agent
        from agents.idea_generator_agent import create_idea_generator_agent
        from agents.technique_agent import create_technique_agent
        from evaluation.evaluator import create_evaluator
        from utils.logger import get_logger
        from utils.timer import Timer
        from utils.helpers import chunk_text, count_tokens
        
        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False


def test_api_key():
    """Test that API key is configured"""
    print("\nTesting API key configuration...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ API key not configured")
        print("   Please set OPENAI_API_KEY in .env file")
        return False
    
    print("✅ API key is configured")
    return True


def test_utilities():
    """Test utility functions"""
    print("\nTesting utilities...")
    
    try:
        from utils.helpers import chunk_text, count_tokens
        
        # Test chunking
        text = "This is a test. " * 100
        chunks = chunk_text(text, max_tokens=50)
        print(f"   Chunking works: {len(chunks)} chunks created")
        
        # Test token counting
        tokens = count_tokens("Hello world")
        print(f"   Token counting works: {tokens} tokens in 'Hello world'")
        
        print("✅ Utilities working!")
        return True
    except Exception as e:
        print(f"❌ Utility test failed: {str(e)}")
        return False


def test_logger():
    """Test logging system"""
    print("\nTesting logger...")
    
    try:
        from utils.logger import reset_logger
        logger = reset_logger()
        logger.log_query("Test query")
        logger.log_papers_found(5)
        print("✅ Logger working!")
        return True
    except Exception as e:
        print(f"❌ Logger test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Research Intelligence Engine - System Verification")
    print("=" * 60)
    
    tests = [
        test_basic_import,
        test_api_key,
        test_utilities,
        test_logger
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Or: streamlit run streamlit_app.py")
    else:
        print("❌ Some tests failed. Please fix issues above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
