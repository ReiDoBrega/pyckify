from __future__ import annotations
import os
import sys
import platform
import shutil
from typing import Optional

_IS_WINDOWS = platform.system() == "Windows"

def clear_previous_lines(num_lines: int) -> None:
    """Erase *num_lines* previously printed lines from the terminal.

    Works on Windows (10+ with VTP and legacy fallback), macOS, and Linux.
    """
    if num_lines <= 0:
        return

    if _IS_WINDOWS:
        _clear_windows(num_lines)
    else:
        _clear_unix(num_lines)


def _clear_windows(num_lines: int) -> None:
    # Enable Virtual Terminal Processing so ANSI codes work on Win 10+
    _enable_win_vtp()
    try:
        for _ in range(num_lines):
            sys.stdout.write("\033[1A\033[2K")
        sys.stdout.flush()
    except Exception:
        os.system("cls")


def _clear_unix(num_lines: int) -> None:
    sys.stdout.write(f"\033[{num_lines}A")
    for _ in range(num_lines):
        sys.stdout.write("\033[2K\033[1B")
    sys.stdout.write(f"\033[{num_lines}A")
    sys.stdout.flush()


def _enable_win_vtp() -> None:
    """Enable ANSI / VTP on Windows 10+. Silent no-op on older versions."""
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        # ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

def get_terminal_size() -> tuple[int, int]:
    """Return (columns, lines) with safe fallback."""
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines

def copy_to_clipboard(text: str) -> bool:
    """Attempt to copy *text* to the system clipboard.

    Returns True on success, False when no clipboard mechanism is available.
    """
    try:
        if _IS_WINDOWS:
            import subprocess
            p = subprocess.Popen(["clip"], stdin=subprocess.PIPE, close_fds=True)
            p.communicate(input=text.encode("utf-16"))
            return True
        elif platform.system() == "Darwin":
            import subprocess
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, close_fds=True)
            p.communicate(input=text.encode("utf-8"))
            return True
        else:
            # Linux – try xclip then xsel then wl-copy
            import subprocess
            for cmd in (["xclip", "-selection", "clipboard"],
                        ["xsel", "--clipboard", "--input"],
                        ["wl-copy"]):
                try:
                    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, close_fds=True)
                    p.communicate(input=text.encode("utf-8"))
                    return True
                except FileNotFoundError:
                    continue
    except Exception:
        pass
    return False


class KeyReader:
    """Unified, cross-platform single-keypress reader.

    On Windows uses ``msvcrt``; on Unix uses ``tty`` + ``termios``.
    Normalises arrow / special keys to the same byte codes as the
    Windows msvcrt extended-key convention so the rest of the code
    sees a consistent API regardless of OS.
    """

    def __init__(self) -> None:
        self._windows = _IS_WINDOWS

    # Windows extended-key second-byte → normalised bytes mapping
    _WIN_EXT: dict[bytes, bytes] = {
        b"H": b"H",  # Up
        b"P": b"P",  # Down
        b"K": b"K",  # Left
        b"M": b"M",  # Right
        b"I": b"I",  # Page Up
        b"Q": b"Q",  # Page Down
        b"G": b"G",  # Home
        b"O": b"O",  # End
    }

    # Unix escape sequences → normalised bytes
    _UNIX_MAP: dict[bytes, bytes] = {
        b"[A": b"H",   # Up
        b"[B": b"P",   # Down
        b"[D": b"K",   # Left
        b"[C": b"M",   # Right
        b"[5~": b"I",  # Page Up
        b"[6~": b"Q",  # Page Down
        b"[H": b"G",   # Home
        b"[F": b"O",   # End
        b"OH": b"G",   # Home (alt)
        b"OF": b"O",   # End  (alt)
    }

    def flush(self) -> None:
        """Discard any pending keystrokes."""
        if self._windows:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        # On Unix there is no reliable non-blocking flush without raw mode;
        # we simply skip (input is already consumed char-by-char in raw mode).

    def getch(self) -> bytes:
        """Block until a key is pressed and return a normalised byte string."""
        if self._windows:
            return self._getch_windows()
        else:
            return self._getch_unix()

    def _getch_windows(self) -> bytes:
        import msvcrt
        key = msvcrt.getch()
        if key in (b"\x00", b"\xe0"):      # extended key prefix
            key = msvcrt.getch()
            return self._WIN_EXT.get(key, key)
        return key

    def _getch_unix(self) -> bytes:
        import tty, termios, select
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            first = os.read(fd, 1)
            if first == b"\x1b":
                # Check for more bytes (non-blocking)
                ready, _, _ = select.select([fd], [], [], 0.05)
                if ready:
                    rest = os.read(fd, 8)
                    return self._UNIX_MAP.get(rest, first + rest)
                return b"\x1b"
            return first
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
