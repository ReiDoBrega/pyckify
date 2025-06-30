import sys
import os
import platform

def clear_previous_lines(num_lines: int):
    """Clear previous lines with Windows CMD compatibility"""
    if platform.system() == "Windows":
        # For Windows, use a more compatible approach
        try:
            # Enable ANSI escape sequences on Windows 10+
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            
            # Move cursor up and clear lines
            for i in range(num_lines):
                sys.stdout.write('\033[1A')  # Move cursor up one line
                sys.stdout.write('\033[2K')  # Clear entire line
            sys.stdout.flush()
            
        except:
            # Fallback for older Windows or if ctypes fails
            # Simply print enough newlines to push content up
            os.system('cls' if os.name == 'nt' else 'clear')
    else:
        # Unix/Linux/Mac - original approach should work
        sys.stdout.write(f'\033[{num_lines}A')  # Move cursor up n lines
        for _ in range(num_lines):
            sys.stdout.write('\033[2K')  # Clear entire line
            sys.stdout.write('\033[1B')  # Move cursor down one line
        sys.stdout.write(f'\033[{num_lines}A')  # Move cursor back up
        sys.stdout.flush()