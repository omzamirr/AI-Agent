# DISCLAIMER

This is not perfect by any means you may need to debug the main.py file to get it to do what you want it to do. This is usually because of how gemini reads and understands text and not necessarily because a lack of error handling in the code.

# AI Agent Calculator

This project is an **AI-powered coding agent** that can interact with a codebase, execute code, read and write files, and answer questions about the project using the Gemini LLM API. It is designed to operate in a secure, sandboxed environment and can be extended to support additional tools and workflows.

## Features

- **Conversational AI Agent:** Interact with the agent using natural language prompts.
- **Function Calling:** The agent can:
  - List files and directories in the working directory.
  - Read the contents of files.
  - Write or overwrite files.
  - Execute Python scripts (including running tests).
- **Secure Execution:** All file and code operations are restricted to a specified working directory.
- **Verbose Mode:** See detailed logs of the agent’s reasoning and actions.
- **Extensible:** Easily add new tools and function schemas.

## Usage

### Prerequisites

- Python 3.12+
- [Gemini API key](https://ai.google.dev/)
- (Recommended) A virtual environment

### Setup

1. **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd ai-agent
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up your environment variables:**
    - Create a `.env` file in the project root:
      ```
      GEMINI_API_KEY=your_gemini_api_key_here
      ```

### Running the Agent

You can interact with the agent using natural language prompts. For example:

```sh
python main.py "what files are in the root?"
python main.py "get the contents of lorem.txt"
python main.py "create a new README.md file with the contents '# calculator'"
python main.py "run tests.py" --verbose
```

- Use `--verbose` to see detailed logs of the agent’s actions.

### Project Structure

```
ai-agent/
├── calculator/           # Calculator app and tests
│   └── tests.py
├── functions/            # Tool implementations
│   ├── get_files_info.py
│   ├── get_files_content.py
│   ├── run_python.py
│   └── write_files.py
├── config.py             # Configuration (e.g., WORKING_DIR)
├── main.py               # Main agent script
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (not committed)
```

### How It Works

- The agent receives your prompt and builds a conversation history.
- It uses Gemini’s function calling to decide which tool(s) to invoke.
- Each tool is securely sandboxed to the working directory.
- The agent loops, calling functions and updating the conversation, until it produces a final answer.

### Adding New Tools

To add a new tool:
1. Implement the function in `functions/`.
2. Define its schema in `main.py`.
3. Add it to the `function_map` and `available_functions`.

### Security

- All file and code operations are restricted to the `WORKING_DIR` (default: `./calculator`).
- The agent will not execute or modify files outside this directory.

### License

MIT License

---

**Enjoy your AI-powered coding agent!**
