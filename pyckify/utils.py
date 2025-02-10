import sys

def clear_previous_lines(num_lines: int):
    """Clear previous lines more reliably by moving cursor up and clearing each line"""
    sys.stdout.write(f'\033[{num_lines}F')  # Move cursor up n lines
    for _ in range(num_lines):
        sys.stdout.write('\033[K')  # Clear current line
        sys.stdout.write('\033[1E')  # Move to next line
    sys.stdout.write(f'\033[{num_lines}F')  # Move cursor back up