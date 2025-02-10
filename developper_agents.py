from typing import List, Tuple
from pathlib import Path
import os
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime


class DeveloperAgent:
    def __init__(self, llm, output_dir: str = "generated_files"):
        self.llm = llm
        self.output_dir = Path(output_dir)
        self.system_prompt = """You are an expert software developer.
Create production-ready code that:
1. Uses best practices and design patterns
2. Implements all required functionality
3. Includes proper error handling
4. Follows language-specific conventions
5. Is well-documented and maintainable
Generate clean, efficient, and well-structured code."""

        self.memory =[]

    def read_file(self, file_path: str) -> str:
        """Read existing file content if it exists"""
        full_path = self.output_dir / file_path
        if (full_path.exists()):
            return full_path.read_text(encoding='utf-8')
        return ""

    def write_file(self, file_path: str, content: str):
        """Write content to file, creating directories if needed"""
        full_path = self.output_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        print(f"Generated: {file_path}")

    def generate_code(self, file_info: Tuple[str, str, List[str], List[str]], context: dict[str, str] = None) -> str:
        """
        Generate code based on file information and project context.

        Args:
            file_info: Tuple containing (file_path, description, dependencies, key_functions)
            context: Optional dictionary of previously generated files and their content

        Returns:
            str: Generated code content

        Raises:
            ValueError: If file_info is invalid
            Exception: If code generation fails
        """
        file_path, description, dependencies, key_functions = file_info

        # Build context from memory and previously generated files
        context_str = "\nProject Context:"
        if self.memory:
            # Get last 3 generated files for immediate context
            recent_context = self.memory[-3:]
            context_str += "\nRecent Generated Files:\n"
            for code in recent_context:
                context_str += f"\n{code}\n---\n"

        # Add dependency implementations if available
        if context:
            context_str += "\nDependency Implementations:\n"
            for dep in dependencies:
                for fname, content in context.items():
                    if dep.lower() in fname.lower():
                        context_str += f"\n--- {fname} ---\n{content}\n"

        # Enhanced prompt with better structure and guidance
        prompt = f"""Create implementation for: {file_path}

    Technical Requirements:
    - Description: {description}
    - Dependencies: {', '.join(dependencies)}
    - Required Functions: {', '.join(key_functions)}

    Implementation Guidelines:
    1. Follow the project's existing code style and patterns
    2. Implement all specified functions: {', '.join(key_functions)}
    3. Handle dependencies correctly: {', '.join(dependencies)}
    4. Include proper error handling and input validation
    5. Add comprehensive docstrings and comments
    6. Ensure consistent naming conventions
    7. Include type hints for Python files
    8. Add logging for important operations

    Existing Content:
    {self.read_file(file_path)}

    {context_str}

    Generate production-ready, well-structured code that integrates with the existing codebase."""

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            generated_code = response.content

            # Store in memory with metadata
            self.memory.append({
                'file': file_path,
                'code': generated_code,
                'dependencies': dependencies,
                'functions': key_functions,
                'timestamp': datetime.now().isoformat()
            })

            return generated_code
        except Exception as e:
            print(f"❌ Error generating code for {file_path}: {str(e)}")
            raise
        


    def process_files(self, agents_task: List[Tuple[str, str, List[str], List[str]]]):
        """Process all files in the agents task"""
        print("\nStarting code generation...")
        
        for file_info in agents_task:
            file_path = file_info[0]
            print(f"\nProcessing: {file_path}")
            
            try:
                code = self.generate_code(file_info , agents_task[3])
                self.write_file(file_path, code)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue

        print("\nCode generation completed.")