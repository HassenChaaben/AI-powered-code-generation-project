# AI-Powered Code Generation Project

An intelligent code generation system that uses LangChain and LLMs to create production-ready code with documentation and best practices.

## Features

- Automated code generation from requirements
- Knowledge retrieval from documentation
- Code cleaning and formatting
- Error detection and fixing
- Project structure generation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the main script:
```bash
python main.py
```

## Project Structure

- `main.py`: Entry point and orchestration
- `developper_agents.py`: Code generation agents
- `cleaning.py`: Code cleaning utilities
- `debugger.py`: Error detection and fixing
- `github_search.py`: Documentation retrieval
- `analyse_fix.py`: Code analysis and improvement

## License

MIT
