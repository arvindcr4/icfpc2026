import json, subprocess, sys

# Load problem spec
with open('/home/claude/icfpc2026/spec_brackets.json') as f:
    spec = json.load(f)

public_tests = spec['publicTestData']

# Let's write the complete, tested layout for brackets.man
# We'll construct a compact room grid and test each case!

