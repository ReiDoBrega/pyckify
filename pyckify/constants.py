import sys
import platform
from rich.style import Style


THEMES: dict = {
    "default": {
        "title":            Style(bold=True,   color="dark_orange"),
        "subtitle":         Style(italic=True, color="cyan"),
        "indicator":        Style(bold=True,   color="bright_yellow"),
        "selected":         Style(bold=True,   color="green"),
        "active":           Style(bold=True,   color="white",  bgcolor="blue"),
        "active_selected":  Style(bold=True,   color="green",  bgcolor="blue"),
        "disabled":         Style(dim=True,    color="grey70"),
        "description":      Style(italic=True, color="bright_blue"),
        "scroll_indicator": Style(bold=True,   color="dark_orange"),
        "controls":         Style(italic=True, color="bright_black"),
        "search":           Style(bold=True,   color="yellow"),
        "search_match":     Style(bold=True,   color="white",  bgcolor="dark_orange"),
        "group_header":     Style(bold=True,   color="dark_orange"),
        "shortcut":         Style(bold=True,   color="red"),
        "border":           Style(color="bright_black"),
        "tag":              Style(italic=True, color="magenta"),
        "counter":          Style(bold=True,   color="cyan"),
        "help":             Style(italic=True, color="bright_black"),
        "error":            Style(bold=True,   color="red"),
        "warning":          Style(bold=True,   color="yellow"),
        "success":          Style(bold=True,   color="green"),
        "fuzzy_score":      Style(italic=True, color="bright_black"),
        "preview_border":   Style(color="blue"),
        "preview_text":     Style(color="white"),
    },
    "dracula": {
        "title":            Style(bold=True,   color="#ff79c6"),
        "subtitle":         Style(italic=True, color="#8be9fd"),
        "indicator":        Style(bold=True,   color="#f1fa8c"),
        "selected":         Style(bold=True,   color="#50fa7b"),
        "active":           Style(bold=True,   color="#f8f8f2", bgcolor="#44475a"),
        "active_selected":  Style(bold=True,   color="#50fa7b", bgcolor="#44475a"),
        "disabled":         Style(dim=True,    color="#6272a4"),
        "description":      Style(italic=True, color="#bd93f9"),
        "scroll_indicator": Style(bold=True,   color="#ff5555"),
        "controls":         Style(italic=True, color="#6272a4"),
        "search":           Style(bold=True,   color="#f1fa8c"),
        "search_match":     Style(bold=True,   color="#282a36", bgcolor="#f1fa8c"),
        "group_header":     Style(bold=True,   color="#ff79c6"),
        "shortcut":         Style(bold=True,   color="#ff5555"),
        "border":           Style(color="#44475a"),
        "tag":              Style(italic=True, color="#bd93f9"),
        "counter":          Style(bold=True,   color="#8be9fd"),
        "help":             Style(italic=True, color="#6272a4"),
        "error":            Style(bold=True,   color="#ff5555"),
        "warning":          Style(bold=True,   color="#ffb86c"),
        "success":          Style(bold=True,   color="#50fa7b"),
        "fuzzy_score":      Style(italic=True, color="#6272a4"),
        "preview_border":   Style(color="#bd93f9"),
        "preview_text":     Style(color="#f8f8f2"),
    },
    "nord": {
        "title":            Style(bold=True,   color="#88c0d0"),
        "subtitle":         Style(italic=True, color="#81a1c1"),
        "indicator":        Style(bold=True,   color="#ebcb8b"),
        "selected":         Style(bold=True,   color="#a3be8c"),
        "active":           Style(bold=True,   color="#eceff4", bgcolor="#3b4252"),
        "active_selected":  Style(bold=True,   color="#a3be8c", bgcolor="#3b4252"),
        "disabled":         Style(dim=True,    color="#4c566a"),
        "description":      Style(italic=True, color="#81a1c1"),
        "scroll_indicator": Style(bold=True,   color="#bf616a"),
        "controls":         Style(italic=True, color="#4c566a"),
        "search":           Style(bold=True,   color="#ebcb8b"),
        "search_match":     Style(bold=True,   color="#2e3440", bgcolor="#ebcb8b"),
        "group_header":     Style(bold=True,   color="#88c0d0"),
        "shortcut":         Style(bold=True,   color="#bf616a"),
        "border":           Style(color="#4c566a"),
        "tag":              Style(italic=True, color="#b48ead"),
        "counter":          Style(bold=True,   color="#88c0d0"),
        "help":             Style(italic=True, color="#4c566a"),
        "error":            Style(bold=True,   color="#bf616a"),
        "warning":          Style(bold=True,   color="#ebcb8b"),
        "success":          Style(bold=True,   color="#a3be8c"),
        "fuzzy_score":      Style(italic=True, color="#4c566a"),
        "preview_border":   Style(color="#81a1c1"),
        "preview_text":     Style(color="#eceff4"),
    },
    "monokai": {
        "title":            Style(bold=True,   color="#fd971f"),
        "subtitle":         Style(italic=True, color="#66d9e8"),
        "indicator":        Style(bold=True,   color="#e6db74"),
        "selected":         Style(bold=True,   color="#a6e22e"),
        "active":           Style(bold=True,   color="#f8f8f2", bgcolor="#3e3d32"),
        "active_selected":  Style(bold=True,   color="#a6e22e", bgcolor="#3e3d32"),
        "disabled":         Style(dim=True,    color="#75715e"),
        "description":      Style(italic=True, color="#66d9e8"),
        "scroll_indicator": Style(bold=True,   color="#f92672"),
        "controls":         Style(italic=True, color="#75715e"),
        "search":           Style(bold=True,   color="#e6db74"),
        "search_match":     Style(bold=True,   color="#272822", bgcolor="#e6db74"),
        "group_header":     Style(bold=True,   color="#fd971f"),
        "shortcut":         Style(bold=True,   color="#f92672"),
        "border":           Style(color="#49483e"),
        "tag":              Style(italic=True, color="#ae81ff"),
        "counter":          Style(bold=True,   color="#66d9e8"),
        "help":             Style(italic=True, color="#75715e"),
        "error":            Style(bold=True,   color="#f92672"),
        "warning":          Style(bold=True,   color="#fd971f"),
        "success":          Style(bold=True,   color="#a6e22e"),
        "fuzzy_score":      Style(italic=True, color="#75715e"),
        "preview_border":   Style(color="#ae81ff"),
        "preview_text":     Style(color="#f8f8f2"),
    },
    "catppuccin": {
        "title":            Style(bold=True,   color="#cba6f7"),   # mauve
        "subtitle":         Style(italic=True, color="#89dceb"),   # sky
        "indicator":        Style(bold=True,   color="#f9e2af"),   # yellow
        "selected":         Style(bold=True,   color="#a6e3a1"),   # green
        "active":           Style(bold=True,   color="#cdd6f4", bgcolor="#313244"),
        "active_selected":  Style(bold=True,   color="#a6e3a1", bgcolor="#313244"),
        "disabled":         Style(dim=True,    color="#6c7086"),   # overlay0
        "description":      Style(italic=True, color="#89b4fa"),   # blue
        "scroll_indicator": Style(bold=True,   color="#f38ba8"),   # red
        "controls":         Style(italic=True, color="#6c7086"),
        "search":           Style(bold=True,   color="#f9e2af"),
        "search_match":     Style(bold=True,   color="#1e1e2e", bgcolor="#f9e2af"),
        "group_header":     Style(bold=True,   color="#cba6f7"),
        "shortcut":         Style(bold=True,   color="#fab387"),   # peach
        "border":           Style(color="#45475a"),
        "tag":              Style(italic=True, color="#f5c2e7"),   # pink
        "counter":          Style(bold=True,   color="#89dceb"),
        "help":             Style(italic=True, color="#6c7086"),
        "error":            Style(bold=True,   color="#f38ba8"),
        "warning":          Style(bold=True,   color="#fab387"),
        "success":          Style(bold=True,   color="#a6e3a1"),
        "fuzzy_score":      Style(italic=True, color="#6c7086"),
        "preview_border":   Style(color="#89b4fa"),
        "preview_text":     Style(color="#cdd6f4"),
    },
    "solarized": {
        "title":            Style(bold=True,   color="#268bd2"),   # blue
        "subtitle":         Style(italic=True, color="#2aa198"),   # cyan
        "indicator":        Style(bold=True,   color="#b58900"),   # yellow
        "selected":         Style(bold=True,   color="#859900"),   # green
        "active":           Style(bold=True,   color="#fdf6e3", bgcolor="#073642"),
        "active_selected":  Style(bold=True,   color="#859900", bgcolor="#073642"),
        "disabled":         Style(dim=True,    color="#586e75"),
        "description":      Style(italic=True, color="#657b83"),
        "scroll_indicator": Style(bold=True,   color="#dc322f"),   # red
        "controls":         Style(italic=True, color="#586e75"),
        "search":           Style(bold=True,   color="#b58900"),
        "search_match":     Style(bold=True,   color="#002b36", bgcolor="#b58900"),
        "group_header":     Style(bold=True,   color="#268bd2"),
        "shortcut":         Style(bold=True,   color="#cb4b16"),   # orange
        "border":           Style(color="#073642"),
        "tag":              Style(italic=True, color="#6c71c4"),   # violet
        "counter":          Style(bold=True,   color="#2aa198"),
        "help":             Style(italic=True, color="#586e75"),
        "error":            Style(bold=True,   color="#dc322f"),
        "warning":          Style(bold=True,   color="#b58900"),
        "success":          Style(bold=True,   color="#859900"),
        "fuzzy_score":      Style(italic=True, color="#586e75"),
        "preview_border":   Style(color="#268bd2"),
        "preview_text":     Style(color="#839496"),
    },
    "one_dark": {
        "title":            Style(bold=True,   color="#61afef"),   # blue
        "subtitle":         Style(italic=True, color="#56b6c2"),   # cyan
        "indicator":        Style(bold=True,   color="#e5c07b"),   # yellow
        "selected":         Style(bold=True,   color="#98c379"),   # green
        "active":           Style(bold=True,   color="#abb2bf", bgcolor="#3e4452"),
        "active_selected":  Style(bold=True,   color="#98c379", bgcolor="#3e4452"),
        "disabled":         Style(dim=True,    color="#5c6370"),
        "description":      Style(italic=True, color="#61afef"),
        "scroll_indicator": Style(bold=True,   color="#e06c75"),   # red
        "controls":         Style(italic=True, color="#5c6370"),
        "search":           Style(bold=True,   color="#e5c07b"),
        "search_match":     Style(bold=True,   color="#282c34", bgcolor="#e5c07b"),
        "group_header":     Style(bold=True,   color="#c678dd"),   # purple
        "shortcut":         Style(bold=True,   color="#e06c75"),
        "border":           Style(color="#3e4452"),
        "tag":              Style(italic=True, color="#c678dd"),
        "counter":          Style(bold=True,   color="#56b6c2"),
        "help":             Style(italic=True, color="#5c6370"),
        "error":            Style(bold=True,   color="#e06c75"),
        "warning":          Style(bold=True,   color="#e5c07b"),
        "success":          Style(bold=True,   color="#98c379"),
        "fuzzy_score":      Style(italic=True, color="#5c6370"),
        "preview_border":   Style(color="#61afef"),
        "preview_text":     Style(color="#abb2bf"),
    },
    "gruvbox": {
        "title":            Style(bold=True,   color="#fabd2f"),   # yellow
        "subtitle":         Style(italic=True, color="#83a598"),   # blue
        "indicator":        Style(bold=True,   color="#fe8019"),   # orange
        "selected":         Style(bold=True,   color="#b8bb26"),   # green
        "active":           Style(bold=True,   color="#ebdbb2", bgcolor="#3c3836"),
        "active_selected":  Style(bold=True,   color="#b8bb26", bgcolor="#3c3836"),
        "disabled":         Style(dim=True,    color="#928374"),   # gray
        "description":      Style(italic=True, color="#83a598"),
        "scroll_indicator": Style(bold=True,   color="#fb4934"),   # red
        "controls":         Style(italic=True, color="#928374"),
        "search":           Style(bold=True,   color="#fabd2f"),
        "search_match":     Style(bold=True,   color="#282828", bgcolor="#fabd2f"),
        "group_header":     Style(bold=True,   color="#d3869b"),   # purple
        "shortcut":         Style(bold=True,   color="#fb4934"),
        "border":           Style(color="#504945"),
        "tag":              Style(italic=True, color="#d3869b"),
        "counter":          Style(bold=True,   color="#8ec07c"),   # aqua
        "help":             Style(italic=True, color="#928374"),
        "error":            Style(bold=True,   color="#fb4934"),
        "warning":          Style(bold=True,   color="#fe8019"),
        "success":          Style(bold=True,   color="#b8bb26"),
        "fuzzy_score":      Style(italic=True, color="#928374"),
        "preview_border":   Style(color="#83a598"),
        "preview_text":     Style(color="#ebdbb2"),
    },
}

custom_theme = THEMES["default"].copy()


def set_theme(name: str) -> None:
    """Switch the active theme by name."""
    if name not in THEMES:
        raise ValueError(f"Unknown theme '{name}'. Available: {list(THEMES)}")
    global custom_theme
    custom_theme.clear()
    custom_theme.update(THEMES[name])


IS_WINDOWS = platform.system() == "Windows"

KEYS_ENTER      = (b"\r",)
KEYS_UP         = (b"H",)
KEYS_DOWN       = (b"P",)
KEYS_LEFT       = (b"K",)
KEYS_RIGHT      = (b"M",)
KEYS_SELECT     = (b" ",)
KEYS_SEARCH     = (b"/",)
KEYS_ESC        = (b"\x1b",)
KEYS_SELECT_ALL = (b"a",)
KEYS_INVERT     = (b"i",)
KEYS_HELP       = (b"?",)
KEYS_PAGE_UP    = (b"I",)
KEYS_PAGE_DOWN  = (b"Q",)
KEYS_HOME       = (b"G",)
KEYS_END        = (b"O",)
KEYS_COPY       = (b"c",)
KEYS_SORT       = (b"s",)
KEYS_THEME      = (b"t",)
KEYS_TAG        = (b"#",)


def _pick(*candidates: str) -> str:
    enc = sys.stdout.encoding or "ascii"
    for sym in candidates:
        try:
            sym.encode(enc)
            return sym
        except (UnicodeEncodeError, LookupError):
            pass
    return candidates[-1]


SYMBOL_CIRCLE_FILLED = _pick("●", "*")
SYMBOL_CIRCLE_EMPTY  = _pick("○", "o")
SYMBOL_ARROW         = _pick("→", ">")
SYMBOL_UP            = _pick("↑", "^")
SYMBOL_DOWN          = _pick("↓", "v")
SYMBOL_SEARCH        = _pick("🔍", "/")
SYMBOL_CHECKED       = _pick("✔", "x")
SYMBOL_UNCHECKED     = _pick("☐", " ")
SYMBOL_SEPARATOR     = _pick("─", "-")
SYMBOL_EXPAND        = _pick("▶", ">")
SYMBOL_COLLAPSE      = _pick("▼", "v")
SYMBOL_STAR          = _pick("★", "*")
SYMBOL_LOCK          = _pick("🔒", "[locked]")
SYMBOL_PREVIEW       = _pick("👁", "[preview]")
SYMBOL_COPY          = _pick("📋", "[copy]")
SYMBOL_TAG           = _pick("🏷", "#")
SYMBOL_RADIO_ON      = _pick("◉", "(x)")
SYMBOL_RADIO_OFF     = _pick("◯", "( )")
