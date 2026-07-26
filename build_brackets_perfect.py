import sim, subprocess, sys, json

def build_grid(rooms_dict):
    # Determine canvas bounds
    max_w = 0
    max_h = 0
    for (x0, y0), lines in rooms_dict.items():
        w = len(lines[0])
        h = len(lines)
        max_w = max(max_w, x0 + w)
        max_h = max(max_h, y0 + h)

    canvas = [[' ' for _ in range(max_w)] for _ in range(max_h)]

    for (x0, y0), lines in rooms_dict.items():
        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                if ch != ' ':
                    canvas[y0 + r][x0 + c] = ch

    return "\n".join("".join(row) for row in canvas)

# Test helper
print("Builder helper defined")
