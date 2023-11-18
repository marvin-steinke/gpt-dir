# GPT Directory Assistant

A Python script that utilizes the OpenAI API to generate chat completions based
on the GPT model. The script takes input from a file or directory (recursive!)
containing files and interacts with the OpenAI GPT model to provide
conversational responses. It is designed to facilitate easy and interactive
communication with the GPT model using specific input file(s) or directory
content.

## Usage

1. Clone this repository to your local machine.
2. Build and install the pip wheel:
   ```bash
   python setup.py sdist bdist_wheel
   pip install .
   ```
3. Obtain your OpenAI API key and set it as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

## Options

- `-dir, --input_path`: The file or directory path containing input file(s).
- `-fe, --file_endings`: Files with specified endings are not ignored (e.g., `.txt`, `.md`).
- `-m, --model`: The GPT model to be used via the OpenAI API (e.g., 3.5-turbo-1106, 4, 4-32k, 4-1106-preview).
- `--temperature`: The sampling temperature to use, with a value between 0-2.
- `--max_tokens`: The maximum number of tokens to generate in the chat completion.
- `-s, --system`: Set the behavior of the assistant.

## Example

```bash
gpt-dir -dir example_dir -fe ".txt" -m "3.5-turbo-1106" -s "Summarize the following files" --temperature "1" --max_tokens "100" 
