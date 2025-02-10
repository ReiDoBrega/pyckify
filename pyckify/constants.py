import curses
from rich.style import Style

# Enhanced theme with new styles
custom_theme = {
    "title": Style(bold=True, color="dark_orange"),
    "subtitle": Style(italic=True, color="cyan"),
    "indicator": Style(bold=True, color="bright_yellow"),
    "selected": Style(bold=True, color="green"),
    "active": Style(bold=True, color="white", bgcolor="blue"),
    "active_selected": Style(bold=True, color="green", bgcolor="blue"),
    "disabled": Style(dim=True, color="grey70"),
    "description": Style(italic=True, color="bright_blue"),
    "scroll_indicator": Style(bold=True, color="dark_orange"),
    "controls": Style(italic=True, color="bright_black"),
    "search": Style(bold=True, color="yellow"),
    "search_match": Style(bold=True, color="white", bgcolor="yellow"),
    "group_header": Style(bold=True, color="dark_orange"),
    "shortcut": Style(bold=True, color="red"),
}

# Curses specific constants
CURSES_KEYS_ENTER = (curses.KEY_ENTER, ord("\n"), ord("\r"))
CURSES_KEYS_UP = (curses.KEY_UP, ord("k"))
CURSES_KEYS_DOWN = (curses.KEY_DOWN, ord("j"))
CURSES_KEYS_SELECT = (curses.KEY_RIGHT, ord(" "))
CURSES_KEYS_ESC = (27,)

# Rich console specific keys
KEYS_ENTER = (b"\r",)
KEYS_UP = (b"H",)
KEYS_DOWN = (b"P",)
KEYS_SELECT = (b"M", b" ")
KEYS_SEARCH = (b"/",)
KEYS_ESC = (b"\x1b",)
KEYS_SELECT_ALL = (b"a",)

# Symbols
SYMBOL_CIRCLE_FILLED = "●"
SYMBOL_CIRCLE_EMPTY = "○"
SYMBOL_ARROW = "→"
SYMBOL_UP = "↑"
SYMBOL_DOWN = "↓"
SYMBOL_SEARCH = "🔍"
