import os
import json
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
load_dotenv()
import create_files
import agents_tasks
import developper_agents
import time
import cleaning 
import debugger



# Define state properly
class GraphState(TypedDict):
    messages: Annotated[List, add_messages]

# Create the graph
builder = StateGraph(GraphState)

# Create the LLM
# llm = AzureChatOpenAI(
#     azure_deployment=os.environ.get("AZURE_OPENAI_API_DEPLOYMENT_NAME"),
#     api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
#     temperature=0,
#     max_tokens=1000,
#     timeout=None,
#     max_retries=2,
# )

# Create the LLM
os.environ["GROQ_API_KEY"] = 
llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",  # High-quality code generation model
    temperature=0.1,                         # Slight randomness for creativity
    max_tokens=4000,                         # Increased token limit for complex code
    top_p=0.95,                             # Nucleus sampling for better quality
    frequency_penalty=0.5,                   # Reduce repetition
    presence_penalty=0.5,                    # Encourage diversity
    timeout=120,                            # Longer timeout for complex generations
    max_retries=5,                          # More retries for reliability                         # Enable streaming for long responses
    request_timeout=120,
    verbose = True,
)

def create_node(state, system_prompt):
    human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    ai_messages = [msg for msg in state["messages"] if isinstance(msg, AIMessage)]
    system_message = [SystemMessage(content=system_prompt)]
    messages = system_message + human_messages + ai_messages
    message = llm.invoke(messages)
    return {"messages": [message]}

pm_agent = lambda state: create_node(state, """
You are a technical project manager specializing in minimal, efficient software architectures. 
For any given application request, generate a JSON structure focusing on essential files only.
Always include the appropriate main/entry point file for the specified language.

Generate the following JSON structure:
{
 "service_name": "",
 "files": {
   "entry_point": {
     "description": "Main entry point file that runs the application",
     "dependencies": ["list of core dependencies"],
     "key_functions": ["main()", "run()", "start()", or language-specific entry point]
   },
   "filename.ext": {
     "description": "Essential component with clear single responsibility",
     "dependencies": ["only necessary dependencies"],
     "key_functions": ["core functionalities"]
   }
 },
 "total_files": 0,
 "technologies": {
   "language": "programming language to use",
   "framework": "minimal framework if needed",
   "database": "lightweight database if required",
   "tools": ["essential development tools only"]
 }
}

Language-Specific Entry Points:
- Python: main.py with if __name__ == '__main__':
- JavaScript: index.js with module.exports or export default
- Java: Main.java with public static void main(String[] args)
- C++: main.cpp with int main()
- Go: main.go with func main()
- TypeScript: index.ts with export default
- Ruby: main.rb
- C#: Program.cs with static void Main(string[] args)

Requirements:
1. Create minimal, executable architecture (max 5-7 files)
2. Always include appropriate entry point for chosen language
3. Each file must have a single responsibility
4. Dependencies must be standard or easily installable
5. Ensure the entry point can execute the complete application
6. Focus on core functionality without overengineering
7. Include clear build/run instructions

Entry Point Structure by Language:
{
  "Python": {
    "file": "main.py",
    "structure": ["imports", "config", "main()", "__main__ block"]
  },
  "JavaScript": {
    "file": "index.js",
    "structure": ["imports", "config", "main()", "export"]
  },
  "Java": {
    "file": "Main.java",
    "structure": ["package", "imports", "class Main", "main method"]
  },
  "C++": {
    "file": "main.cpp",
    "structure": ["includes", "namespace", "main()"]
  },
  "Go": {
    "file": "main.go",
    "structure": ["package main", "imports", "main()"]
  }
}

Include for each language:
1. Entry point file (main.*, index.*, etc.)
2. Core business logic file
3. Configuration (if needed)
4. Utility functions (if needed)
5. Dependencies list (package.json, requirements.txt, pom.xml, etc.)
""")



# Add nodes to the graph
builder.add_node("pm_agent", pm_agent)


# Set entry point and edges
builder.add_edge(START, "pm_agent")
builder.add_edge("pm_agent", END)

# Compile and run the builder
graph = builder.compile()

# Draw the graph
try:
    graph.get_graph(xray=True).draw_mermaid_png(output_file_path="graph.png")
except Exception:
    pass

def clean_json_string(content):
    """Clean and extract JSON from the response string."""
    try:
        # Find the first '{' and last '}'
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = content[start:end]
            # Parse to validate and format
            return json.loads(json_str)
        return None
    except Exception as e:
        print(f"Error cleaning JSON: {e}")
        return None

def save_json_output(content, service_name=None):
    try:
        # First try to clean and parse the JSON
        json_data = clean_json_string(content)
        if json_data is None:
            print("Warning: Could not extract valid JSON from response")
            print("Raw response:", content)
            return None
            
        if service_name is None:
            service_name = json_data.get('service_name', 'microservice')
        
        # Create outputs directory if it doesn't exist
        os.makedirs('outputs', exist_ok=True)
        
        # Save JSON file
        filename = f'outputs/{service_name}_blueprint.json'
        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=2)
        return filename
    except Exception as e:
        print(f"Error saving JSON: {e}")
        print("Raw response:", content)
        return None

def main_loop():
    try:
        user_input = input(">> ")
        response = graph.invoke({"messages": [HumanMessage(content=user_input)]})
        pm_response = response["messages"][-1].content
        print("\nAnalyst Response:", pm_response)
        
        # Save the JSON output
        saved_file = save_json_output(pm_response)
        if saved_file:
            print(f"\nBlueprint saved to: {saved_file}")
        else:
            print("\nFailed to save blueprint. Please check the response format.")
        
        create_files.main()
        agents_task = agents_tasks.main()
        print("number of files: ", len(agents_task))
        
        # Initialize developer agent and generate code
        developer = developper_agents.DeveloperAgent(llm)
        developer.process_files(agents_task)
        print("\nCode generation completed.")
        cleaning.main()

        # Initialize debugger agent and correct code
        debug_agent = debugger.DebuggerAgent(llm)
        debug_agent.debugging_files(agents_task)
        print("\nCode correction completed.")
        
    except Exception as e:
        print(f"Error in main loop: {str(e)}")
        return False
    
    return True

# Run the main loop once
if __name__ == "__main__":
    main_loop()