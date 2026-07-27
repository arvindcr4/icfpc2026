#!/usr/bin/env python3
"""Reproducibly build the baseline Triangle Littleman program."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


OUTPUT = Path(__file__).with_name("triangle.man")
INSTRUCTIONS = "@rM1+*M2W/sH"


def render() -> str:
    room = f"+{'-' * len(INSTRUCTIONS)}+"
    return "\n".join(
        [
            f"+-+   {room}   +-+",
            f"|I|>->|{INSTRUCTIONS}|>->|O|",
            f"+-+   {room}   +-+",
        ]
    ) + "\n"


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args(arguments)
    expected = render()
    if options.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="ascii") != expected:
            print(f"{OUTPUT} is stale; run {Path(__file__)}", file=sys.stderr)
            return 1
        print(f"checked {OUTPUT}")
        return 0
    temporary = OUTPUT.with_suffix(".man.tmp")
    temporary.write_text(expected, encoding="ascii")
    temporary.replace(OUTPUT)
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
