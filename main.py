import sys
import requests
import os
import json
import numpy as np
import inspect
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.json import JSON
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

# load dotenv
from dotenv import load_dotenv
load_dotenv(override=True)

console = Console()
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:0.6b")
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "http://localhost:11434/v1/models")
MODEL_API_KEY = os.getenv("OPENAI_API_KEY", "")

MAX_LOOP_COUNT = int(os.getenv("MAX_LOOP_COUNT", 15))

print(f"Using model: {MODEL_NAME} from {MODEL_BASE_URL}")
# print the first 10 characters of the API key if it exists
if MODEL_API_KEY:
    print(f"Using API key: {MODEL_API_KEY[:10]}... (truncated for security)")

# from help import generate_schema, search_and_scrape
from help import generate_schema
from mysearch2 import tavily_context_search

def my_super_cool_function(x_int, y_int) -> float:
    """Does some cool math and returns a number."""
    # convert to float. 
    x_int = float(x_int)
    y_int = float(y_int)
    r = np.sin(x_int) * np.cos(y_int)
    return r

def encode_a_secret(secret_to_encode: str) -> str:
    """Encodes a secret string with a simple transformation."""
    code = [f"xx{a}" for a in secret_to_encode]
    return "".join(code)

def all_work_is_finished(is_finished: bool):
    """A function to call when all work is sufficiently finished. This will exit the program."""
    if is_finished:
        console.print(Panel("🎉 Work completed! Exiting...", style="green"))
        sys.exit(0)
        
# function for writing to a file. 
def write_to_file(filename: str, content: str):
    """Writes content to a file."""
    try:
        with open(filename, 'w') as f:
            f.write(content)
    except Exception as e:
        console.print(Panel(f"❌ Error writing to file {filename}: {e}", style="red"))

# Setup tools
tool_list = [my_super_cool_function, encode_a_secret, all_work_is_finished, tavily_context_search, write_to_file]
tool_list_schema = [generate_schema(t) for t in tool_list]
tool_map = {t.__name__: t for t in tool_list}

# API setup
headers = {"Content-Type": "application/json"}
if MODEL_API_KEY:
    headers["Authorization"] = f"Bearer {MODEL_API_KEY}"

def call_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool and return the result message."""
    if tool_name not in tool_map:
        return f"Tool '{tool_name}' not found in available tools."
    
    try:
        fn = tool_map[tool_name]
        result = fn(**arguments)
        return f"✅ Called {tool_name} with {arguments}. Result: {result}"
    except Exception as e:
        return f"❌ Error calling {tool_name}: {str(e)}"

def make_api_call(payload: dict) -> dict:
    """Make API call to Ollama with progress indicator."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("🤖 Thinking...", total=None)
        response = requests.post(MODEL_BASE_URL, headers=headers, json=payload)
        return response.json()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="AI Tool Assistant")
    parser.add_argument("-p", "--prompt", type=str, help="Initial prompt to send to the AI assistant")
    args = parser.parse_args()
    
    console.print(Panel("🤖 AI Tool Assistant", style="bold blue"))
    console.print("Available tools:", style="bold")
    for tool in tool_list:
        console.print(f"  • {tool.__name__}: {tool.__doc__}")
    
    # Use provided prompt or ask user for input
    if args.prompt:
        user_input = args.prompt
        console.print(f"\n[bold cyan]Using provided prompt:[/bold cyan] {user_input}")
    else:
        user_input = Prompt.ask("\n[bold cyan]What would you like me to help you with?[/bold cyan]")
    
    messages = [
        {"role": "system", "content": "You are helpful AI assistent that works in a loop. You can call tools when necessary. After thinking, return in valid tool calling format. Call 'all_work_is_finished' with is_finished=true when the task is complete.\n\nOnly call one tool per response/iteration of the loop."},
        {"role": "user", "content": user_input}
    ]
    
    max_loops = MAX_LOOP_COUNT
    for loop_count in range(max_loops):
        console.print(f"\n[dim]--- Loop {loop_count + 1}/{max_loops} ---[/dim]")
        
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "tools": tool_list_schema,
            "tool_choice": "auto"
        }
        
        # Make API call
        resp_json = make_api_call(payload)
        
        # Show raw response in debug mode
        if os.getenv("DEBUG"):
            console.print(Panel(JSON.from_data(resp_json), title="Raw Response"))
        
        # Parse response
        choice = resp_json.get("choices", [{}])[0]
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls", [])
        
        # only allow 1 tool call per response
        if len(tool_calls) > 1:
            console.print("[red]⚠️ Multiple tool calls detected! Only the first will be processed.[/red]")
            tool_calls = [tool_calls[0]]
        
        # Process tool calls or handle no tool call scenario
        tool_results = []
        
        if not tool_calls:
            # No tool call - show assistant response and add to context
            content = message.get("content", "No response content")
            console.print(Panel(content, title="🤖 Assistant Response", style="blue"))
            
            # Add descriptive message about no tool call to context
            no_tool_message = (
                f"💭 Assistant provided a text response without calling any tools. "
                f"Response: '{content}'. If you need to use tools to complete the task, "
                f"please call the appropriate function. If the task is complete, "
                f"call 'all_work_is_finished' with is_finished=true.  When calling this tool make sure to use the 'tool_calls' format."
            )
            tool_results.append(no_tool_message)
            console.print(f"[dim]{no_tool_message}[/dim]")
        else:
            # Process tool calls
            for tool_call in tool_calls:
                try:
                    func_info = tool_call['function']
                    tool_name = func_info['name']
                    arguments = func_info['arguments']
                    
                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)
                    
                    console.print(f"🔧 Calling tool: [bold]{tool_name}[/bold] with {arguments}")
                    result = call_tool(tool_name, arguments)
                    tool_results.append(result)
                    console.print(result)
                    
                except Exception as e:
                    error_msg = f"❌ Error processing tool call: {str(e)}"
                    tool_results.append(error_msg)
                    console.print(error_msg, style="red")
        
        # Add results back to conversation
        tool_response = "\n".join(tool_results)
        messages.append({
            "role": "user", 
            "content": f"{tool_response}\n\nGiven this information, decide what to do next or call 'all_work_is_finished' if the task is complete."
        })
    
    console.print(Panel("⚠️ Maximum loops reached. Exiting.", style="yellow"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted by user. Goodbye![/red]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
