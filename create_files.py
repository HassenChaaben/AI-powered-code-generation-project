import json
import os
from pathlib import Path
from glob import glob

def get_latest_blueprint():
    """Get the most recently created blueprint file from outputs directory."""
    output_dir = Path('outputs')
    if not output_dir.exists():
        raise FileNotFoundError("outputs directory not found")
    
    # Get all JSON files in the outputs directory
    blueprint_files = glob(str(output_dir / '*_blueprint.json'))
    
    if not blueprint_files:
        raise FileNotFoundError("No blueprint files found in outputs directory")
    
    # Get the most recently modified file
    latest_file = max(blueprint_files, key=os.path.getmtime)
    return latest_file

def read_blueprint(blueprint_path):
    """Read the JSON blueprint file."""
    with open(blueprint_path, 'r') as f:
        return json.load(f)

def create_file_content(file_info):
    """Create initial content for each file with documentation."""
    content = []
    
    # Add file description as comment
    content.append('"""')
    content.append(file_info['description'])
    content.append('\nDependencies:')
    for dep in file_info['dependencies']:
        content.append(f'- {dep}')
    content.append('\nKey Functions:')
    for func in file_info['key_functions']:
        content.append(f'- {func}')
    content.append('"""')
    
    return '\n'.join(content)

def generate_files(blueprint):
    """Generate all files from the blueprint."""
    service_name = blueprint['service_name']
    base_dir = Path('generated_files')  # Changed from f'generated_{service_name}'
    
    # Create base directory
    base_dir.mkdir(exist_ok=True)
    
    # Create files
    for filename, file_info in blueprint['files'].items():
        # Create subdirectories if needed
        file_path = base_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate file content
        content = create_file_content(file_info)
        
        # Write file
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f'Created: {file_path}')

def main():
    try:
        blueprint_path = get_latest_blueprint()
        print(f"Using blueprint: {blueprint_path}")
        
        blueprint = read_blueprint(blueprint_path)
        generate_files(blueprint)
        print(f"\nSuccessfully generated files for {blueprint['service_name']} microservice")
        print(f"Total files created: {blueprint['total_files']}")
        
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON in blueprint file")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
