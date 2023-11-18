#!/usr/bin/env python

import os
import sys
import argparse
import json
from typing import Dict, Tuple, Optional

import openai
# weird imports 'cause of pyinstaller bug
from tiktoken_ext import openai_public
import tiktoken_ext
import tiktoken


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-dir", "--input_path",
        metavar="<file or dir>",
        help="file or directory path containing input file(s)",
        type=str,
        default=None
    )
    parser.add_argument("-fe", "--file_endings", 
        metavar="file endings", 
        type=str, nargs="*",
        help="Files with specified endings are not ignored", 
        default=[]
    )
    parser.add_argument("-m", "--model",
        metavar="gpt-<model>",
        help="GPT model to be used via the OpenAI API, e.g.: 3.5-turbo-1106, 4, 4-32k, 4-1106-preview",
        type=str,
        default="3.5-turbo-1106"
    )
    parser.add_argument("--temperature",
        metavar="<float>",
        help="sampling temperature to use, value between 0-2",
        type=float,
        default=1
    )
    parser.add_argument("--max_tokens",
        metavar="<int>",
        help="maximum number of tokens to generate in the chat completion. Value should be greater than 0",
        type=int,
        default=None
    )
    parser.add_argument("-s", "--system",
        metavar="<system>",
        help="set the behavior of the assistant",
        type=str,
        default="You are a helpful assistant!"
    )
    return parser


class GptClient:
    def __init__(
        self,
        input_path: str,
        file_endings: list[str],
        model: str,
        temperature: float,
        max_tokens: int,
        system: str,
    ) -> None:
        self.input_path = input_path
        self.file_endings = file_endings
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system = system
        self.input_pricing = {
            "3.5-turbo-1106": 0.0010,
            "4": 0.03,
            "4-32k": 0.06,
            "4-1106-preview": 0.01,
        }
        self.output_pricing = {
            "3.5-turbo-1106": 0.0020,
            "4": 0.06,
            "4-32k": 0.12,
            "4-1106-preview": 0.03,
        }
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def costs(self, string: str, price_table: Dict[str, float]) -> [int, float]:
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(string))
        return num_tokens, num_tokens / 1000 * price_table[self.model]
    
    def _concatenate_files(self, path: str, file_endings: list[str]) -> str:
        # This function reads the contents of a file
        def read_file(file_path):
            with open(file_path, "r") as file:
                return file.read()

        # Check if the path is a file
        if os.path.isfile(path):
            return read_file(path)

        concat = ""
        # Walk through the directory
        for root, dirs, files in os.walk(path):
            # Filter out directories that start with "."
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for file in files:
                # Skip files that start with "."
                if file.startswith("."):
                    continue
                _, file_extension = os.path.splitext(file)
                if file_extension not in file_endings:
                    continue
                file_path = os.path.join(root, file)
                concat += f"File: {file_path}\n"
                concat += read_file(file_path) + "\n\n"
        return concat

    def _confirm(self, conversation: list[dict]) -> None:
        tokens, prompt_costs = self.costs(str(conversation), self.input_pricing)
        if prompt_costs > 0.05 or tokens > 8000:
            cost_string = "{:.5f}".format(prompt_costs)
            user_choice = input(
                f"Tokens: {tokens} -> Input costs: {cost_string}, proceed? [Y/n]\n"
            )
            if not user_choice.lower() in ["", "y"]:
                sys.exit()

    def _user_prompt(self, conversation: list[dict]) -> list[dict]:
        # Prompt user message
        user_input = input("User: ")
        conversation.append({"role": "user", "content": json.dumps(user_input)})
        return conversation

    def run_chat(self) -> None:
        # Init conversation with input file(s)
        conversation = [{"role": "system", "content": self.system}]
        if self.input_path:
            file_contents = self._concatenate_files(self.input_path, self.file_endings)
            conversation.append({"role": "user", "content": file_contents})

        # Main loop
        while True:
            # Last message from AI or system role?
            if (conversation[-1]["role"] in ["assistant", "system"]):
                # Get user prompt
                conversation = self._user_prompt(conversation)

            self._confirm(conversation)
            # Send conversation
            stream = openai.chat.completions.create(
                model="gpt-" + self.model,
                messages=conversation,
                temperature=self.temperature,
                stream=True,
            )

            # Answer stream
            messages = []
            print("Assistant: ", end="")
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta:
                    message = delta.content
                    if message:
                        messages.append(message)
                        print(message, end="")

            # Add full answer to conversation
            full_message = "".join(messages)
            conversation.append({"role": "assistant", "content": full_message})
            # Print costs to user
            _, conversation_cost = self.costs(str(conversation), self.input_pricing)
            _, answer_cost = self.costs(full_message, self.output_pricing)
            full_cost_string = "{:.5f}".format(conversation_cost + answer_cost)
            print(f"\nTotal Costs: {full_cost_string}\n")


def main():
    args = create_parser().parse_args()
    client = GptClient(*vars(args).values())
    client.run_chat()


if __name__ == "__main__":
    main()
