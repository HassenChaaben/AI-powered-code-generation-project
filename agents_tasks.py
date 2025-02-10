import json
from typing import Dict, Any, List

from create_files import get_latest_blueprint 

def extract_file_info(json_data: Dict[str, Any]) -> Dict[str, List]:
    """Extract all file information into categorized lists"""
    files_info = {
        'entities': [],
        'services': [],
        'repositories': [],
        'controllers': [],
        'configs': [],
        'tests': [],
        'other': []
    }
    
    for filename, info in json_data.get('files', {}).items():
        file_data = {
            'name': filename,
            'description': info.get('description', ''),
            'dependencies': info.get('dependencies', []),
            'key_functions': info.get('key_functions', [])
        }
        
        if filename.startswith('entities/'):
            files_info['entities'].append(file_data)
        elif filename.startswith('services/'):
            files_info['services'].append(file_data)
        elif filename.startswith('repositories/'):
            files_info['repositories'].append(file_data)
        elif filename.startswith('controllers/'):
            files_info['controllers'].append(file_data)
        elif filename.startswith('config/'):
            files_info['configs'].append(file_data)
        elif filename.startswith('tests/'):
            files_info['tests'].append(file_data)
        else:
            files_info['other'].append(file_data)
            
    return files_info


# ...existing imports and extract_file_info function...

def main():
    try:
        file_path = get_latest_blueprint()
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            files_info = extract_file_info(json_data)
            files = []
            descriptions = []
            dependencies = []
            key_functions = []

            # Safely collect data from all non-empty categories
            for category, items in files_info.items():
                for item in items:
                    files.append(item['name'])
                    descriptions.append(item['description'])
                    dependencies.append(item['dependencies'])
                    key_functions.append(item['key_functions'])

            # Create the file data tuple list
            file_data = list(zip(files, descriptions, dependencies, key_functions))
            return file_data
            
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        return []

if __name__ == "__main__":
    main()