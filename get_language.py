import json
from pathlib import Path
from typing import Dict, Union, List
from create_files import get_latest_blueprint  


def extract_language_info(json_file_path: str) -> Dict[str, Union[str, List[str]]]:
    """
    Extract language and technology information from a service blueprint JSON file.
    
    Args:
        json_file_path (str): Path to the JSON blueprint file
        
    Returns:
        Dict[str, Union[str, List[str]]]: Dictionary containing language and technology info
        
    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is invalid
        KeyError: If required fields are missing
    """
    # Read and parse JSON file
    json_path = Path(json_file_path)
    with json_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract technology information
    tech_info = data.get('technologies', {})
    
    return {
        'language': tech_info.get('language', 'Unknown'),
        'framework': tech_info.get('framework', 'None'),
        'database': tech_info.get('database', 'None'),
        'tools': tech_info.get('tools', []),
        'total_files': data.get('total_files', 0)
    }
    
def main():
    file_path = get_latest_blueprint()
    language_info = extract_language_info(file_path)
    return language_info



if __name__ == "__main__":
    main()