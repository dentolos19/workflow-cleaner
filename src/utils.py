def clear_previous_lines(lines: int = 1):
    LINE_UP = "\x1b[1A"
    LINE_CLEAR = "\x1b[2K"
    for i in range(lines):
        print(LINE_UP, end=LINE_CLEAR)
