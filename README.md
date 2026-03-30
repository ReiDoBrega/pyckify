# Pyckify 🎯

A modern, feature-rich Python library for creating interactive command-line selection interfaces. Pyckify (pick-it-for-you) offers an enhanced selection experience with support for multiselect, grouping, filtering, search, and rich styling.

[![PyPI version](https://badge.fury.io/py/pyckify.svg)](https://badge.fury.io/py/pyckify)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyckify.svg)](https://pypi.org/project/pyckify/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features 🚀

- 🎨 Rich terminal UI with 8 built-in themes, live-switchable with `t`
- ✨ Single and multi-selection modes
- 🔍 Fuzzy search with ranked results and optional score display
- 🏷️ Option grouping, tagging, and tag-filter mode (`#` key)
- ⌨️ Keyboard shortcuts with smart conflict resolution
- 🎯 Custom filtering and 4 sort modes (`s` key cycles)
- 📝 Option descriptions, icons, per-option Rich style overrides
- 👁️ Preview pane (bottom or right) for long-form option detail
- 📋 Clipboard copy (`c` key)
- ⚡ Smooth scrolling, Page Up/Down, Home/End navigation
- 🎭 Disabled options and visual `Separator` support
- 🎪 Windows/Unix compatible
- 📻 Multiple multiselect indicator styles: `circle`, `check`, `star`, `radio`
- 🧰 Helper utilities: `make_options()`, `from_dict()`

## Installation 📦

```bash
pip install pyckify
```

## Quick Start 🎮

### Basic Usage

```python
from pyckify import Pyck, Option

# Simple string options
options = ["Red", "Blue", "Green", "Yellow"]
selected, index = Pyck(options, title="Choose a color")
print(f"Selected color: {selected}")

# Using Option objects
options = [
    Option("🍎 Apple", description="Fresh from the garden"),
    Option("🍌 Banana", description="Rich in potassium"),
    Option("🍊 Orange", description="Vitamin C boost")
]
selected, index = Pyck(options, title="Choose a fruit")
print(f"Selected fruit: {selected.label}")
```

## Advanced Usage 🔧

### Multi-select with Constraints

```python
from pyckify import Pyck, Option

options = [
    Option("Python", description="General-purpose language"),
    Option("JavaScript", description="Web development"),
    Option("Rust", description="Systems programming"),
    Option("Go", description="Cloud infrastructure")
]

result = Pyck(
    options=options,
    title="Select Programming Languages",
    subtitle="Choose 2-3 languages for your project",
    multiselect=True,
    minSelectionCount=2,
    maxSelectionCount=3,
    separateValues=True  # Returns a PickResult object
)

if result:
    print("\nSelected languages:")
    for lang in result.values:
        print(f"- {lang.label}: {lang.description}")
```

### Grouped Options with Icons and Shortcuts

```python
options = [
    # Development Tools
    Option("📝 VS Code",
           description="Popular code editor",
           group="Development Tools",
           shortcut="v",
           tags=["editor", "free"]),
    Option("⚡ PyCharm",
           description="Python IDE",
           group="Development Tools",
           shortcut="p",
           tags=["ide", "paid"]),

    # Version Control
    Option("😺 GitHub",
           description="Code hosting platform",
           group="Version Control",
           shortcut="g",
           tags=["git", "cloud"]),
    Option("🦊 GitLab",
           description="DevOps platform",
           group="Version Control",
           shortcut="l",
           tags=["git", "cloud"])
]

result = Pyck(
    options=options,
    title="Development Stack",
    subtitle="Select your tools",
    multiselect=True,
    group_by="group",
    show_shortcuts=True
)
```

### Advanced Grouped Options with Objects

```python
options = (
    [Option(f" 🎞️ {video}", group="🎞️ Video Tracks", value=video) for video in videos] +
    [Option(f" 🔊 {audio}", group="🔊 Audio Tracks", value=audio) for audio in audios] +
    [Option(f" 💬 {subtitle}", group="💬 Subtitle Tracks", value=subtitle) for subtitle in subtitles]
)
result = Pyck(
    options=options,
    group_by="group",
    multiselect=True,
    minSelectionCount=1,
    separateValues=True,
)
results = [value.value for option in result for value in option if isinstance(value, Option)]
```

Output:
```
↑↓ navigate • space select • a select all • enter confirm • / search • esc clear filters/quit

↑ More options above

🎞️ Video Tracks
    🎞️ VIDEO: BnGFobSd | avc1.4d401f | SDR | 480x360 | 901 kbps | 29.970 FPS
    🎞️ VIDEO: 6EFRMq5M | avc1.4d401f | SDR | 480x360 | 494 kbps | 29.970 FPS

🔊 Audio Tracks
    🔊 AUDIO: KuHayhsL | AAC | 2.0 | 128 kbps | yue
    🔊 AUDIO: eXSUTLgz | AAC | 2.0 | 128 kbps | en
→  🔊 AUDIO: QyEd8Mp6 | AAC | 2.0 | 128 kbps | el
↓ More options below

Selected: 0 (minimum: 1)
```

### Fuzzy Search with Ranked Results

```python
result = Pyck(
    options=options,
    title="Language Picker",
    fuzzy=True,             # Enable fuzzy (ranked) search — default True
    show_fuzzy_score=True,  # Show match score next to each option
    separateValues=True,
)
```

Press `/` to enter search mode. Results are automatically ranked by match quality. Set `confirm_on_single=True` to auto-confirm when the search narrows to a single match.

### Preview Pane

```python
options = [
    Option(
        "🐍 Python",
        description="General-purpose scripting",
        preview=(
            "Python is a high-level, dynamically typed language prized for\n"
            "its readability and vast ecosystem. Ideal for data science,\n"
            "web backends, automation, and AI/ML workloads."
        ),
    ),
]

result = Pyck(
    options=options,
    title="Language Deep-Dive",
    show_preview=True,
    preview_position="bottom",  # or "right"
    separateValues=True,
)
```

### Themes

```python
result = Pyck(
    options=options,
    title="Themed Picker",
    theme="dracula",  # Set a theme at creation time
)
```

Press `t` at runtime to cycle through all available themes live. Available themes: `default`, `dracula`, `nord`, `monokai`, `catppuccin`, `solarized`, `one_dark`, `gruvbox`.

You can also switch themes programmatically:

```python
from pyckify import set_theme
set_theme("catppuccin")
```

### Multiselect Indicator Styles

```python
result = Pyck(
    options=options,
    multiselect=True,
    multiselect_indicator="radio",  # "circle" | "check" | "star" | "radio"
)
```

### Sort Modes

Press `s` to cycle through sort modes at runtime: `original → a→z → z→a → selected-first`.

### Tag Filtering

Press `#` to enter tag-filter mode and narrow options by tag. Tags are displayed inline when `show_tags=True` (default).

```python
options = [
    Option("Apple",  tags=["fruit", "sweet"]),
    Option("Lemon",  tags=["fruit", "citrus"]),
    Option("Carrot", tags=["vegetable"]),
]
result = Pyck(options=options, show_tags=True)
# Press # then type "citrus" to filter
```

### Custom Filtering

```python
from dataclasses import dataclass
from pyckify import Pyck, Option

@dataclass
class Language:
    name: str
    type: str
    year: int

options = [
    Option(f"🌟 {lang.name}",
           description=f"Created in {lang.year}",
           value=lang,
           tags=[lang.type])
    for lang in [
        Language("Go",   "compiled",    2009),
        Language("Rust", "compiled",    2010),
        Language("Zig",  "compiled",    2016),
    ]
]

def modern_languages(option: Option) -> bool:
    return option.value.year >= 2010

result = Pyck(
    options=options,
    title="Modern Languages",
    multiselect=True,
    filter_fn=modern_languages,
)
```

### Disabled Options and Separators

```python
from pyckify import Pyck, Option, Separator

options = [
    Separator("── Recommended ──────────────────"),
    Option("✨ Premium Plan",    description="All features",  style="bold green", tags=["paid"]),
    Option("💎 Enterprise Plan", description="Custom SLA",    style="bold cyan",  tags=["paid"]),
    Separator("── Legacy (unavailable) ─────────"),
    Option("🔒 Pro v1",          description="Discontinued",  enabled=False,      tags=["legacy"]),
    Separator("── Free tiers ────────────────────"),
    Option("⭐ Hobbyist",         description="500 req/day",                       tags=["free"]),
]

result = Pyck(
    options=options,
    title="Subscription Plans",
    subtitle="Disabled options are shown but not selectable"
)
```

### Helper Utilities

Build `Option` lists from plain dicts or any iterable:

```python
from pyckify.options import from_dict, make_options

# From a list of dicts
options = from_dict([
    {"label": "AWS S3",       "description": "Object storage",      "tags": ["storage"]},
    {"label": "GCS",          "description": "Google Cloud Storage", "tags": ["storage"]},
    {"label": "Cloudflare R2","description": "Zero-egress S3",       "tags": ["storage"]},
])

# From any iterable
options = make_options([1, 2, 3], label_fn=lambda x: f"Item {x}")
```

### Per-Option Rich Style Overrides

```python
Option("✨ Premium", style="bold green")
Option("💎 Enterprise", style="bold cyan")
```

Any valid [Rich style string](https://rich.readthedocs.io/en/stable/style.html) is accepted, overriding the active theme for that row only.

### Clipboard Copy

Press `c` to copy the currently focused option's label to the system clipboard. Works on Windows, macOS, and Linux (requires `xclip`, `xsel`, or `wl-copy`).

## API Reference 📚

### Pyck() Function

The main function for creating selection interfaces.

```python
def Pyck(
    options: Sequence[OPTION_T],
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    indicator: str = "→",
    defaultIndex: int = 0,
    multiselect: bool = False,
    minSelectionCount: int = 0,
    maxSelectionCount: Optional[int] = None,
    filter_fn: Optional[Callable[[OPTION_T], bool]] = None,
    show_shortcuts: bool = True,
    group_by: Optional[str] = None,
    separateValues: bool = False,
    theme: str = "default",
    fuzzy: bool = True,
    show_preview: bool = False,
    preview_position: str = "bottom",
    show_border: bool = False,
    multiselect_indicator: str = "circle",
    confirm_on_single: bool = False,
    allow_empty: bool = False,
    show_tags: bool = True,
    show_fuzzy_score: bool = False,
    max_visible: Optional[int] = None,
    page_size: Optional[int] = None,
    jump_on_shortcut_select: bool = False,
) -> Union[PickResult, List[PICK_RETURN_T], PICK_RETURN_T, None]
```

#### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `options` | `Sequence` | — | Items to display (strings or `Option` objects) |
| `title` | `str` | `None` | Header text |
| `subtitle` | `str` | `None` | Subheader text |
| `indicator` | `str` | `"→"` | Cursor indicator symbol |
| `defaultIndex` | `int` | `0` | Starting cursor position |
| `multiselect` | `bool` | `False` | Allow multiple selections |
| `minSelectionCount` | `int` | `0` | Minimum required selections (multiselect) |
| `maxSelectionCount` | `int` | `None` | Maximum allowed selections (multiselect) |
| `filter_fn` | `Callable` | `None` | Custom predicate to hide options |
| `show_shortcuts` | `bool` | `True` | Render `[key]` shortcut badges |
| `group_by` | `str` | `None` | `Option` attribute to group by (e.g. `"group"`) |
| `separateValues` | `bool` | `False` | Return a `PickResult` instead of raw tuples |
| `theme` | `str` | `"default"` | Built-in theme name |
| `fuzzy` | `bool` | `True` | Enable fuzzy (ranked) search |
| `show_preview` | `bool` | `False` | Display `Option.preview` in a pane |
| `preview_position` | `str` | `"bottom"` | `"bottom"` or `"right"` |
| `show_border` | `bool` | `False` | Wrap the picker in a Rich panel border |
| `multiselect_indicator` | `str` | `"circle"` | `"circle"`, `"check"`, `"star"`, or `"radio"` |
| `confirm_on_single` | `bool` | `False` | Auto-confirm when search yields exactly one result |
| `allow_empty` | `bool` | `False` | Allow confirming with zero selections in multiselect |
| `show_tags` | `bool` | `True` | Render option tags inline |
| `show_fuzzy_score` | `bool` | `False` | Show fuzzy match score next to each option |
| `max_visible` | `int` | `None` | Override auto-detected visible row count |
| `page_size` | `int` | `None` | Rows scrolled per PgUp/PgDn (default: page height − 1) |
| `jump_on_shortcut_select` | `bool` | `False` | Also toggle selection when jumping via shortcut in multiselect mode |

Returns `None` on Esc, a `PickResult` when `separateValues=True`, otherwise a `(value, index)` tuple or list of tuples.

### Option Class

```python
@dataclass
class Option:
    label: str
    value: Union[object, str, Any] = None
    description: Optional[str] = None
    enabled: bool = True
    shortcut: Optional[str] = None
    icon: Optional[str] = None
    group: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    preview: Optional[str] = None       # Long-form text shown in preview pane
    style: Optional[str] = None         # Per-row Rich style string override
    metadata: Dict[str, Any] = field(default_factory=dict)  # App data bag
```

#### Attributes

| Attribute | Description |
|---|---|
| `label` | Display text shown in the list |
| `value` | Arbitrary payload returned on selection (defaults to `label`) |
| `description` | Short helper text rendered beside the label |
| `enabled` | When `False`, shown but cannot be selected |
| `shortcut` | Single character that jumps to this option |
| `icon` | Emoji or ASCII prefix prepended to the label |
| `group` | Group name used when `group_by` is set |
| `tags` | Free-form tags for display and tag-filter mode |
| `preview` | Long-form text shown in the optional preview pane |
| `style` | Rich style string to override the active theme for this row |
| `metadata` | Arbitrary dict for application-specific data |

### Separator Class

```python
@dataclass
class Separator(Option):
    def __init__(self, label: str = "─" * 30, description: Optional[str] = None):
        super().__init__(label, description=description, enabled=False)
```

A non-selectable visual divider. Can be placed anywhere in the options list.

### PickResult

```python
class PickResult(NamedTuple):
    values: Union[List[Any], Any]
    indices: Union[List[int], int]
```

Returned when `separateValues=True`. Provides `is_multi`, `as_list`, and `index_list` convenience properties.

### Helper Functions

```python
from pyckify.options import from_dict, make_options

# Build Options from a list of dicts (keys match Option fields)
options = from_dict([{"label": "Alpha", "tags": ["a"]}, {"label": "Beta"}])

# Wrap any iterable in Option instances
options = make_options([1, 2, 3], label_fn=lambda x: f"Item {x}")
```

## Keyboard Controls ⌨️

| Key | Action |
|---|---|
| `↑` / `↓` | Navigate options |
| `PgUp` / `PgDn` | Scroll one page |
| `Home` / `End` | Jump to top / bottom |
| `Enter` | Confirm selection |
| `Space` | Toggle selection (multiselect) |
| `a` | Select / deselect all visible options |
| `i` | Invert selection among visible options |
| `/` | Enable search |
| `#` | Filter by tag |
| `s` | Cycle sort mode (original → a→z → z→a → selected-first) |
| `t` | Cycle theme live |
| `c` | Copy focused label to clipboard |
| `?` | Toggle help overlay |
| `Esc` | Clear active filter, or quit |

> **Shortcut priority:** Option shortcuts always take precedence over global keys. For example, if an option has `shortcut="a"`, pressing `a` jumps to it rather than triggering select-all.

## Theming 🎨

Eight built-in themes are available. Pass `theme=` to `Pyck()` or press `t` at runtime to cycle live.

```python
# Available theme names
"default" | "dracula" | "nord" | "monokai" | "catppuccin" | "solarized" | "one_dark" | "gruvbox"
```

Each theme defines styles for every UI element:

```python
custom_theme = {
    "title":            Style(bold=True,   color="dark_orange"),
    "subtitle":         Style(italic=True, color="cyan"),
    "indicator":        Style(bold=True,   color="bright_yellow"),
    "selected":         Style(bold=True,   color="green"),
    "active":           Style(bold=True,   color="white", bgcolor="blue"),
    "active_selected":  Style(bold=True,   color="green", bgcolor="blue"),
    "disabled":         Style(dim=True,    color="grey70"),
    "description":      Style(italic=True, color="bright_blue"),
    "group_header":     Style(bold=True,   color="dark_orange"),
    "shortcut":         Style(bold=True,   color="red"),
    "tag":              Style(italic=True, color="magenta"),
    "search_match":     Style(bold=True,   color="white", bgcolor="dark_orange"),
    # ... and more
}
```

Switch themes programmatically at any time:

```python
from pyckify import set_theme
set_theme("gruvbox")
```

## Examples 📝

Run the full feature showcase interactively:

```bash
python examples.py
```

The showcase covers: basic single-select, multiselect with min/max constraints, grouped options with shortcuts, fuzzy search and sort, preview pane, theme switching, separators with per-option styles, `from_dict`/`make_options` helpers, and `confirm_on_single`.

## What's New

- **`radio` indicator style** — new `multiselect_indicator` value using `◉`/`◯` symbols
- **`jump_on_shortcut_select`** — in multiselect mode, pressing a shortcut key now optionally toggles that option's selection in addition to jumping the cursor
- **4 new themes** — `catppuccin`, `solarized`, `one_dark`, `gruvbox`
- **`confirm_on_single`** — auto-confirms when a search narrows to exactly one visible result
- **`allow_empty`** — permits confirming with zero selections in multiselect mode
- **`show_preview` / `preview_position`** — side or bottom preview pane using `Option.preview`
- **`fuzzy` / `show_fuzzy_score`** — ranked fuzzy search with optional score display
- **`show_tags` / tag-filter mode** — display tags inline and filter by tag with `#`
- **`show_border`** — wrap the picker in a Rich panel border
- **`multiselect_indicator`** — choose between `circle`, `check`, `star`, `radio`
- **`page_size` / `max_visible`** — fine-grained control over scroll behaviour
- **`s` / `t` / `c` keys** — sort cycling, live theme switching, clipboard copy
- **`from_dict()` / `make_options()`** — convenience helpers in `pyckify.options`
- **`Option.preview`** — long-form text for the preview pane
- **`Option.style`** — per-row Rich style string override
- **`Option.metadata`** — arbitrary app data bag on each option
- **`invertSelection`** — now inverts only among currently visible (filtered) options
- **Shortcut conflict resolution** — option shortcuts always take priority over global keys

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Inspired by [pick](https://github.com/aisk/pick)
- Built with [rich](https://github.com/Textualize/rich) for terminal formatting

## Author ✍️

ReiDoBrega ([@ReiDoBrega](https://github.com/ReiDoBrega))

---

Made with ❤️ using Python