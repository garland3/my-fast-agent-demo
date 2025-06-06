import inspect
def my_unique_addition(x:int, y:int)->int:
    return x**2+y

# r = inspect.getsource(my_unique_addition)
# print(r)
# inspect.get
print(my_unique_addition.__name__)

# sig = inspect.signature(my_unique_addition)
# print("--- SIG --------")
# print(sig)
# params = sig.parameters
# for p in params:
#     print(p)

# docstring = inspect.get_annotations(my_unique_addition)
# print(docstring)


import inspect
from typing import get_origin, get_args

def python_type_to_json_schema_type(python_type) -> str:
    """Convert Python type annotations to JSON Schema type strings."""
    if python_type is None or python_type == type(None):
        return "null"
    elif python_type == int:
        return "integer"
    elif python_type == float:
        return "number"
    elif python_type == str:
        return "string"
    elif python_type == bool:
        return "boolean"
    elif python_type == list or get_origin(python_type) == list:
        return "array"
    elif python_type == dict or get_origin(python_type) == dict:
        return "object"
    else:
        # For complex types or unknown types, default to string
        return "string"

def generate_schema(function: callable) -> dict:
    """Generates a JSON Schema representing a Python function's structure.

    Args:
        function: The Python function to be analyzed for schema generation.

    Returns:
        A dictionary representing the JSON Schema of the function. 
    """

    schema = {
        "type": "function",
        "function": {
            "name": function.__name__,
            "description": inspect.getdoc(function) if inspect.getdoc(function) else "",
        }
    }

    # Extract parameters from the function signature
    signature = inspect.signature(function)
    properties = {}
    required_params = []
    
    for param_name, param in signature.parameters.items():
        param_type = param.annotation
        if param_type != inspect.Parameter.empty:
            # Convert Python type to JSON Schema type
            json_type = python_type_to_json_schema_type(param_type)
            properties[param_name] = {"type": json_type}
        else:
            # No type annotation available - use string as default valid type
            properties[param_name] = {"type": "string"}
        
        # Check if parameter is required (no default value)
        if param.default == inspect.Parameter.empty:
            required_params.append(param_name)
    
    schema["function"]["parameters"] = {
        "type": "object",  
        "properties": properties,
        "required": required_params
    }

    return schema

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import time

def search_and_scrape(query, n=3):
    """
    Search DuckDuckGo and scrape text from top N results.
    
    Args:
        query (str): Search query
        n (int): Number of top results to scrape (default: 3)
    
    Returns:
        list: List of dictionaries with 'url' and 'text' keys
    """
    results = []
    
    try:
        # Search DuckDuckGo
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=n))
        
        # Scrape each URL
        for result in search_results:
            url = result['href']
            try:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                results.append({'url': url, 'text': text})
                time.sleep(1)  # Be respectful to servers
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                results.append({'url': url, 'text': f"Error: {str(e)}"})
                
    except Exception as e:
        print(f"Search error: {e}")
        
    return results

# Example usage:
# results = search_and_scrape("artificial intelligence", 3)
# for i, result in enumerate(results, 1):
#     print(f"\n{i}. {result['url']}")
#     print(f"Text preview: {result['text'][:200]}...")


if __name__ == "__main__":
    r = generate_schema(my_unique_addition)
    import json
    print(json.dumps(r, indent=2))

# print(r)
