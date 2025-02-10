import os
from pathlib import Path
import re
from typing import List
import agents_tasks




def remove_template_text(content: str) -> str:
    """Remove template text and language identifiers while preserving actual code"""
    # List of common programming language identifiers
    language_identifiers = [
        'python', 'javascript', 'java', 'typescript', 'cpp', 'c++', 
        'csharp', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin',
        'scala', 'r', 'matlab', 'sql', 'bash', 'shell', 'powershell'
    ]
    
    # Find code block markers
    first_index = content.find('```')
    second_index = content.find('```', first_index + 1)

    if first_index != -1 and second_index != -1:
        # Extract content between backticks
        content_between = content[first_index + 3:second_index].strip()
        
        # Remove language identifier from the beginning
        for lang in language_identifiers:
            if content_between.lower().startswith(lang):
                content_between = content_between[len(lang):].strip()
                break
        
        return content_between
    
    return content

def clean_file(file_path: str) -> bool:
    """Clean a single file while preserving actual code"""
    try:
        print(f"\n🧹 Cleaning: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        
        # Clean content
        cleaned_content = remove_template_text(content)
        
        # Don't write if cleaning resulted in empty content
        if not cleaned_content.strip():
            print(f"⚠️ Warning: Cleaning would result in empty file, skipping {file_path}")
            return False
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
            
        print(f"✨ Cleaned: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")
        return False

def main(directory: str = "generated_files") -> bool:
    """Clean all files in the directory"""
    try:
        # Create base directory if it doesn't exist
        base_dir = Path(directory)
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all files with their full paths
        files = []
        for file_info in agents_tasks.main():
            # Get the file path from agents_tasks
            relative_path = file_info[0]
            # Join with base directory to get full path
            full_path = base_dir.joinpath(Path(relative_path))
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            files.append(full_path)

        if not files:
            print("No files found to clean")
            return True
            
        print(f"\n🧹 Starting cleanup of {len(files)} files...")
        
        cleaned_files = []
        failed_files = []
        
        # Process each file
        for file_path in files:
            if clean_file(str(file_path)):
                cleaned_files.append(str(file_path))
            else:
                failed_files.append(str(file_path))
        
        # Print summary
        print("\n=== Cleanup Summary ===")
        print(f"✅ Successfully cleaned: {len(cleaned_files)}/{len(files)}")
        print(f"❌ Failed to clean: {len(failed_files)}/{len(files)}")
        
        if failed_files:
            print("\nFailed files:")
            for file in failed_files:
                print(f"- {file}")
        
        return len(failed_files) == 0
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return False

if __name__ == "__main__":
    main()





























































