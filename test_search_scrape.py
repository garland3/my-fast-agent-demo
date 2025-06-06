import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from help import search_and_scrape
import json

def test_search_and_scrape():
    """Test the search_and_scrape function with various queries."""
    
    print("Testing search_and_scrape function...")
    print("=" * 50)
    
    # Test 1: Simple search query
    print("\nTest 1: Searching for 'Python programming'")
    try:
        results = search_and_scrape("Python programming", n=2)
        print(f"Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. URL: {result['url']}")
            print(f"   Text preview: {result['text'][:150]}...")
            if result['text'].startswith('Error:'):
                print(f"   ⚠️  Error occurred: {result['text']}")
            else:
                print(f"   ✅ Successfully scraped {len(result['text'])} characters")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Technical search query
    print("\nTest 2: Searching for 'JSON Schema validation'")
    try:
        results = search_and_scrape("JSON Schema validation", n=1)
        print(f"Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. URL: {result['url']}")
            print(f"   Text preview: {result['text'][:150]}...")
            if result['text'].startswith('Error:'):
                print(f"   ⚠️  Error occurred: {result['text']}")
            else:
                print(f"   ✅ Successfully scraped {len(result['text'])} characters")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 3: Edge case - empty query
    print("\nTest 3: Testing with empty query")
    try:
        results = search_and_scrape("", n=1)
        print(f"Found {len(results)} results")
        if len(results) == 0:
            print("✅ Correctly handled empty query")
        else:
            print("⚠️  Unexpected results for empty query")
    except Exception as e:
        print(f"⚠️  Expected behavior - empty query caused: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 4: Test with n=0
    print("\nTest 4: Testing with n=0")
    try:
        results = search_and_scrape("test query", n=0)
        print(f"Found {len(results)} results")
        if len(results) == 0:
            print("✅ Correctly handled n=0")
        else:
            print("⚠️  Unexpected results for n=0")
    except Exception as e:
        print(f"⚠️  Error with n=0: {e}")

def test_search_and_scrape_detailed():
    """More detailed test showing the structure of returned data."""
    
    print("\n" + "=" * 60)
    print("DETAILED TEST - Data Structure Analysis")
    print("=" * 60)
    
    try:
        results = search_and_scrape("artificial intelligence basics", n=1)
        
        if results:
            print(f"\nReturned data type: {type(results)}")
            print(f"Number of results: {len(results)}")
            
            for i, result in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  Type: {type(result)}")
                print(f"  Keys: {list(result.keys())}")
                print(f"  URL type: {type(result.get('url'))}")
                print(f"  Text type: {type(result.get('text'))}")
                print(f"  URL: {result.get('url', 'N/A')}")
                print(f"  Text length: {len(result.get('text', ''))}")
                print(f"  Text sample: {result.get('text', '')[:100]}...")
                
                # Validate expected structure
                if 'url' in result and 'text' in result:
                    print("  ✅ Structure is correct")
                else:
                    print("  ❌ Structure is incorrect")
        else:
            print("No results returned")
            
    except Exception as e:
        print(f"❌ Detailed test failed: {e}")

if __name__ == "__main__":
    print("🔍 Starting search_and_scrape function tests...")
    
    # Run basic tests
    test_search_and_scrape()
    
    # Run detailed test
    test_search_and_scrape_detailed()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)
