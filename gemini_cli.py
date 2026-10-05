#!/usr/bin/env python3
import sys
from gemini_client import generate_text


def main():
    prompt = " ".join(sys.argv[1:])
    if not prompt:
        prompt = "Give me a brief summary of arbitrage betting math."
    print(generate_text(prompt))


if __name__ == "__main__":
    main()
