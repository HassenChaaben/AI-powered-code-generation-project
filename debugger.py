import subprocess
from typing import List, Tuple, Dict
from pathlib import Path
import os
import ast
import pylint.lint
from langchain_core.messages import SystemMessage, HumanMessage
import get_language 
import cleaning

class DebuggerAgent:
    def __init__(self, llm, output_dir: str = "generated_files"):
        self.llm = llm
        self.output_dir = Path(output_dir)
        self.correction_attempts = {}  # Track attempts per file
        self.system_prompt = """You are an expert code debugger and software architect with deep knowledge of all programming languages.
Your task is to fix ANY code issue, no matter how complex.
You MUST return working code that:
1. Has zero syntax errors
2. Implements all required functionality
3. Handles edge cases and errors
4. Uses correct dependencies
5. Follows language-specific best practices

If the code has complex issues, break down the fix into steps:
1. First fix syntax and structural issues
2. Then implement missing functionality
3. Finally optimize and add error handling

You MUST return complete, working code that can be executed without errors."""

    def check_syntax(self, content: str) -> List[str]:
        """Check for syntax errors using ast"""
        try:
            ast.parse(content)
            return []
        except SyntaxError as e:
            return [f"Syntax error on line {e.lineno}: {e.msg}"]
        except Exception as e:
            return [str(e)]

    def check_linting(self, file_path: str) -> List[str]:
        """Run pylint on the file"""
        try:
            pylint_output = []
            pylint.lint.Run([str(file_path)], do_exit=False)
            return pylint_output
        except Exception:
            return []

    def analyze_code(self, file_path: str, content: str) -> Dict:
        """Comprehensive code analysis"""
        return {
            'syntax_errors': self.check_syntax(content),
            'lint_issues': self.check_linting(file_path),
            'ast_valid': len(self.check_syntax(content)) == 0
        }

    def correct_error(self, file_info: Tuple, error: str, content: str, analysis: Dict) -> str:
        """Enhanced error correction with multiple strategies"""
        _, description, dependencies, key_functions = file_info
        
        # Track complexity of the error
        has_syntax_errors = bool(analysis['syntax_errors'])
        has_runtime_errors = error is not True
        has_lint_issues = bool(analysis['lint_issues'])
        
        # Build progressive correction prompt
        correction_focus = "structural and syntax fixes"
        if not has_syntax_errors and has_runtime_errors:
            correction_focus = "runtime error fixes and functionality"
        elif not has_syntax_errors and not has_runtime_errors and has_lint_issues:
            correction_focus = "code quality and optimization"

        prompt = f"""Fix this code with focus on {correction_focus}:

File Context:
Description: {description}
Dependencies: {', '.join(dependencies)}
Key Functions: {', '.join(key_functions)}

Current Issues:
Syntax Errors: {', '.join(analysis['syntax_errors']) if has_syntax_errors else 'None'}
Runtime Error: {error if has_runtime_errors else 'None'}
Linting Issues: {', '.join(analysis['lint_issues']) if has_lint_issues else 'None'}

Code to Fix:
{content}

Requirements:
1. Code MUST be complete and executable
2. Fix ALL syntax and runtime errors
3. Implement ALL required functionality
4. Include proper error handling
5. Use correct imports and dependencies

Return ONLY the corrected code."""

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return cleaning.remove_template_text(response.content)

    def recursive_correction(self, file_info: Tuple, content: str, max_depth: int = 3) -> str:
        """Recursively attempt to fix code until it works"""
        file_path = file_info[0]
        
        for depth in range(max_depth):
            # Analyze current state
            analysis = self.analyze_code(file_path, content)
            result = self.execute_code(file_path)
            
            if analysis['ast_valid'] and result is True:
                print(f"✅ Code fixed after {depth + 1} attempts")
                return content
                
            print(f"🔄 Correction attempt {depth + 1}/{max_depth}")
            content = self.correct_error(file_info, result, content, analysis)
            
            # Write intermediate result
            self.write_file(file_path, content)
        
        # If we reach here, try one final comprehensive fix
        return self.final_attempt_fix(file_info, content)

    def final_attempt_fix(self, file_info: Tuple, content: str) -> str:
        """Last resort fix attempt with simplified code"""
        _, description, _, key_functions = file_info
        
        prompt = f"""Create a completely new implementation that:
1. Implements these core functions: {', '.join(key_functions)}
2. Fulfills this description: {description}
3. Uses minimal dependencies
4. Has basic error handling
5. Is guaranteed to run without errors

Return 100% working code """

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return cleaning.remove_template_text(response.content)

    def debugging_files(self, agents_task: List[Tuple[str, str, List[str], List[str]]]):
        """Improved file debugging process"""
        print("\nStarting comprehensive code correction...")
        
        for file_info in agents_task:
            file_path = file_info[0]
            print(f"\n🔍 Analyzing: {file_path}")
            
            try:
                current_code = self.read_file(file_path)
                if not current_code:
                    print(f"⚠️ Could not read file: {file_path}")
                    continue

                # Try recursive correction
                corrected_code = self.recursive_correction(file_info, current_code)
                self.write_file(file_path, corrected_code)
                print(f"✨ Successfully corrected: {file_path}")
                
            except Exception as e:
                print(f"⚠️ Error during correction: {str(e)}, attempting final fix...")
                try:
                    # Always try final attempt fix if anything fails
                    final_code = self.final_attempt_fix(file_info, current_code)
                    self.write_file(file_path, final_code)
                    print(f"✨ Applied final fix to: {file_path}")
                except Exception as e2:
                    print(f"⚠️ Final fix attempt error: {str(e2)}")

        print("\nCode correction completed.")

    def read_file(self, file_path: str) -> str:
        """Read existing file content if it exists"""
        full_path = self.output_dir / file_path
        if full_path.exists():
            return full_path.read_text(encoding='utf-8')
        return ""

    def write_file(self, file_path: str, content: str):
        """Write content to file, creating directories if needed"""
        full_path = self.output_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        print(f"Generated: {file_path}")

    def execute_code(self, file_path: str):
        """Execute the code and return True if successful, or the error message if not"""
        full_path = self.output_dir / file_path
        language_info = get_language.main()
        language = language_info['language']
        result = subprocess.run([language, full_path], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        return result.stderr
