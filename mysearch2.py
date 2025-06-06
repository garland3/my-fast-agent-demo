import os
import time
import inspect
from typing import get_origin, get_args
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()



def tavily_search_and_scrape(
    query: str, 
    max_results: int = 3,
    search_depth: str = "basic",
    include_raw_content: bool = True,
    include_answer: bool = False,
    include_images: bool = False,
    topic: str = "general",
    time_range: str = None,
    include_domains: list = None,
    exclude_domains: list = None
):
    """
    Search using Tavily AI and extract content from results.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of search results to return (0-20, default: 3)
        search_depth (str): Search depth - "basic" (1 credit) or "advanced" (2 credits, default: "basic")
        include_raw_content (bool): Include cleaned HTML content of each result (default: True)
        include_answer (bool): Include LLM-generated answer to query (default: False)
        include_images (bool): Include image search results (default: False)
        topic (str): Search category - "general" or "news" (default: "general")
        time_range (str): Time filter - "day", "week", "month", "year" or None (default: None)
        include_domains (list): List of domains to specifically include (default: None)
        exclude_domains (list): List of domains to specifically exclude (default: None)
    
    Returns:
        dict: Dictionary containing search results, answer (if requested), and metadata
    """
    
    # Get API key from environment variable
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable not found. Please add it to your .env file.")
    
    # Initialize Tavily client
    try:
        tavily_client = TavilyClient(api_key=api_key)
    except Exception as e:
        return {"error": f"Failed to initialize Tavily client: {str(e)}"}
    
    # Prepare search parameters
    search_params = {
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_raw_content": include_raw_content,
        "include_answer": include_answer,
        "include_images": include_images,
        "topic": topic
    }
    
    # Add optional parameters if provided
    if time_range:
        search_params["time_range"] = time_range
    if include_domains:
        search_params["include_domains"] = include_domains
    if exclude_domains:
        search_params["exclude_domains"] = exclude_domains
    
    try:
        # Execute search
        response = tavily_client.search(**search_params)
        
        # Process results for easier consumption
        processed_results = []
        
        if "results" in response:
            for result in response["results"]:
                processed_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0)
                }
                
                # Include raw content if available and requested
                if include_raw_content and "raw_content" in result:
                    processed_result["raw_content"] = result["raw_content"]
                
                processed_results.append(processed_result)
        
        # Prepare final response
        final_response = {
            "query": response.get("query", query),
            "results": processed_results,
            "results_count": len(processed_results),
            "response_time": response.get("response_time", "N/A")
        }
        
        # Include answer if requested
        if include_answer and "answer" in response:
            final_response["answer"] = response["answer"]
        
        # Include images if requested
        if include_images and "images" in response:
            final_response["images"] = response["images"]
        
        return final_response
        
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

def tavily_context_search(query: str, max_results: int = 5):
    """
    Get search context optimized for RAG applications using Tavily.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to include in context
    
    Returns:
        str: Formatted context string ready for RAG applications
    """
    
    # Get API key from environment variable
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable not found. Please add it to your .env file.")
    
    try:
        # Initialize Tavily client
        tavily_client = TavilyClient(api_key=api_key)
        
        # Get search context (this is a specialized Tavily method for RAG)
        context = tavily_client.get_search_context(
            query=query,
            max_results=max_results
        )
        
        return context
        
    except Exception as e:
        return f"Context search failed: {str(e)}"

def tavily_qna_search(query: str):
    """
    Get a direct answer to a question using Tavily's Q&A search.
    
    Args:
        query (str): Question to answer
    
    Returns:
        str: Direct answer to the question
    """
    
    # Get API key from environment variable
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable not found. Please add it to your .env file.")
    
    try:
        # Initialize Tavily client
        tavily_client = TavilyClient(api_key=api_key)
        
        # Get direct answer
        answer = tavily_client.qna_search(query=query)
        
        return answer
        
    except Exception as e:
        return f"Q&A search failed: {str(e)}"

# Example usage and testing
if __name__ == "__main__":
    # Test basic search
    print("=== Testing Tavily Search ===")
    results = tavily_search_and_scrape(
        query="artificial intelligence recent developments",
        max_results=3,
        search_depth="basic",
        include_answer=True,
        topic="general"
    )
    
    if "error" not in results:
        print(f"Query: {results['query']}")
        print(f"Results found: {results['results_count']}")
        print(f"Response time: {results['response_time']} seconds")
        
        if "answer" in results:
            print(f"\nGenerated Answer:\n{results['answer']}\n")
        
        print("Search Results:")
        for i, result in enumerate(results['results'], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Score: {result['score']}")
            print(f"   Content: {result['content'][:200]}...")
    else:
        print(f"Error: {results['error']}")
    
    print("\n" + "="*50)
    
    # Test context search
    print("=== Testing Context Search ===")
    context = tavily_context_search("machine learning applications in healthcare")
    print(f"Context (first 300 chars): {context[:300]}...")
    
    print("\n" + "="*50)
    
    # Test Q&A search
    print("=== Testing Q&A Search ===")
    answer = tavily_qna_search("What is the capital of France?")
    print(f"Answer: {answer}")
    
    print("\n" + "="*50)
  