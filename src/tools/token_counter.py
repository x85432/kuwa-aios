#!/usr/local/bin/python

import sys
import fileinput
import argparse
import tiktoken

SUPPORTED_TOKENIZER = ('openai',)

def openai_num_tokens_from_messages(messages):
    """
    Return the number of tokens used by a list of messages.
    Reference: https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    
    # Fixed value for nowadays GPT-3.5/4
    tokens_per_message = 3
    tokens_per_name = 1
    
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def count_token(tokenizer, messages):

    if args.tokenizer not in SUPPORTED_TOKENIZER:
        raise ValueError(f"Tokenizer {args.tokenizer} not supported. Supported value are {SUPPORTED_TOKENIZER}")

    tokenizer_map = {
        'openai': openai_num_tokens_from_messages,
    }
    num_tokens = tokenizer_map[tokenizer](messages)
    return num_tokens

if __name__ == "__main__":
    # sys.tracebacklimit = -1
    parser = argparse.ArgumentParser(description='Charter converter based-on OpenCC.')
    parser.add_argument('--tokenizer', default='openai', help='The tokenizer to use.')
    args = parser.parse_args()
    sys.argv = []

    content = '\n'.join(list(fileinput.input())).strip()
    messages = [{'role': 'user', 'content': content}]
    num_tokens = count_token(tokenizer=args.tokenizer, messages=messages)
    print(f"{num_tokens} tokens")