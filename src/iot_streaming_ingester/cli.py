# src/base_python_project/cli.py
import argparse
import sys
import asyncio

from .main import run


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Base Python Project CLI")
    return parser.parse_args(args)


def main() -> None:
    _ = parse_args(sys.argv[1:])
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting cleanly.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
