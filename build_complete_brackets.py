import sim, subprocess, sys, json

# Build complete working brackets.man

# Algorithm summary:
# Read n from input pipe:
#   if n == 0: output 0 to O pipe, halt!
# Set BP = n.
# stack = 0, pos = 1.
# Loop BP times:
#   send pos to M pipe (which bounces pos back).
#   read character c from input pipe.
#   classify c:
#     if c < 50: btype = 1, diff = c - 40
#     elif c < 110: btype = 2, diff = c - 91
#     else: btype = 3, diff = c - 123
#   if diff == 0: (opener)
#     stack = stack * 4 + btype
#     read pos from M pipe.
#     pos = pos + 1.
#     BP -= 1, loop back if BP > 0.
#   else: (closer)
#     top = stack % 4
#     stack = stack // 4
#     if top != btype: (mismatch!)
#       read pos from M pipe.
#       send -1 to M pipe (to halt M man).
#       send pos to O pipe, halt!
#     read pos from M pipe.
#     pos = pos + 1.
#     BP -= 1, loop back if BP > 0.
# After loop:
#   if stack == 0:
#     send -1 to M pipe.
#     send 0 to O pipe, halt!
#   else: (unclosed openers)
#     read pos from M pipe.
#     send -1 to M pipe.
#     send pos to O pipe, halt!

print("Algorithm definition complete.")
