# Pyckify 🎯

A modern, feature-rich Python library for creating interactive command-line selection interfaces. Pyckify (pick-it-for-you) offers an enhanced selection experience with support for multiselect, grouping, filtering, search, and rich styling.

[![PyPI version](https://badge.fury.io/py/pyckify.svg)](https://badge.fury.io/py/pyckify)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyckify.svg)](https://pypi.org/project/pyckify/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features 🚀

- 🎨 Rich terminal UI with customizable themes
- ✨ Single and multi-selection modes
- 🔍 Built-in search functionality
- 🏷️ Option grouping and tagging
- ⌨️ Keyboard shortcuts
- 🎯 Custom filtering
- 📝 Option descriptions and icons
- ⚡ Smooth scrolling for large lists
- 🎭 Disabled options support
- 🎪 Windows/Unix compatible

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

if any(isinstance(value, VideoTrack) for value in results):
    videos = [value for value in results if isinstance(value, VideoTrack)]
elif any(isinstance(value, AudioTrack) for value in results):
    audios = [value for value in results if isinstance(value, AudioTrack)]
elif any(isinstance(value, SubtitleTrack) for value in results):
    subtitles = [value for value in results if isinstance(value, SubtitleTrack)]

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
    🔊 AUDIO: 4r83sM8H | AAC | 2.0 | 128 kbps | da
    🔊 AUDIO: BpZJpQs8 | AAC | 2.0 | 128 kbps | de
    🔊 AUDIO: eXSUTLgz | AAC | 2.0 | 128 kbps | en
    🔊 AUDIO: kZ9xNLh5 | AAC | 2.0 | 128 kbps | es-ES
    🔊 AUDIO: RRZLJ5Lj | AAC | 2.0 | 128 kbps | es-419
    🔊 AUDIO: 9ciYXZEy | AAC | 2.0 | 128 kbps | fr-FR
→  🔊 AUDIO: QyEd8Mp6 | AAC | 2.0 | 128 kbps | el
↓ More options below

Selected: 0 (minimum: 1)

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
    popularity: int

options = [
    Option(f"🌟 {lang.name}", 
           description=f"Created in {lang.year}",
           value=lang,
           tags=[lang.type],
           group=f"Popularity: {lang.popularity}/10")
    for lang in [
        Language("Python", "interpreted", 1991, 10),
        Language("JavaScript", "interpreted", 1995, 9),
        Language("Rust", "compiled", 2010, 7),
        Language("Go", "compiled", 2009, 7)
    ]
]

# Custom filter for modern languages
def modern_languages(option: Option) -> bool:
    return option.value.year >= 2010

result = Pyck(
    options=options,
    title="Programming Language Selection",
    subtitle="Modern languages only (2010+)",
    multiselect=True,
    filter_fn=modern_languages,
    group_by="group"
)
```

### Disabled Options

```python
options = [
    Option("✨ Premium Plan", 
           description="All features included", 
           enabled=True),
    Option("💎 Enterprise Plan", 
           description="Custom solutions", 
           enabled=True),
    Option("🔒 Legacy Plan", 
           description="No longer available", 
           enabled=False)
]

result = Pyck(
    options=options,
    title="Subscription Plans",
    subtitle="Select an available plan"
)
```

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
) -> Union[PickResult, Union[List[PICK_RETURN_T], PICK_RETURN_T]]
```

#### Parameters:

- `options`: List of options to choose from (strings or Option objects)
- `title`: Title displayed at the top
- `subtitle`: Subtitle displayed below the title
- `indicator`: Cursor indicator symbol
- `defaultIndex`: Starting selection index
- `multiselect`: Enable multiple selections
- `minSelectionCount`: Minimum required selections (multiselect mode)
- `maxSelectionCount`: Maximum allowed selections (multiselect mode)
- `filter_fn`: Custom filtering function
- `show_shortcuts`: Show keyboard shortcuts
- `group_by`: Group options by attribute
- `separateValues`: Return separated values and indices

### Option Class

Class for creating rich options with metadata.

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
```

#### Attributes:

- `label`: Display text
- `value`: Associated value (optional)
- `description`: Additional description
- `enabled`: Whether the option can be selected
- `shortcut`: Keyboard shortcut key
- `icon`: Display icon
- `group`: Group name for grouping
- `tags`: List of tags for categorization

### Separator Class

Class for creating visual separators in the option list.

```python
@dataclass
class Separator(Option):
    def __init__(self, label: str, description: Optional[str] = None):
        super().__init__(label, description=description, enabled=False)
```

## Keyboard Controls ⌨️

- `↑/↓`: Navigate options
- `Enter`: Confirm selection
- `Space`: Toggle selection (multiselect mode)
- `a`: Select/deselect all (multiselect mode)
- `/`: Enable search
- `Esc`: Clear filters/exit

## Theming 🎨

Pyckify uses a custom theme system for consistent styling:

```python
custom_theme = {
    "title": Style(bold=True, color="dark_orange"),
    "subtitle": Style(italic=True, color="cyan"),
    "indicator": Style(bold=True, color="bright_yellow"),
    "selected": Style(bold=True, color="green"),
    "active": Style(bold=True, color="white", bgcolor="blue"),
    "disabled": Style(dim=True, color="grey70"),
    "description": Style(italic=True, color="bright_blue"),
    "shortcut": Style(bold=True, color="red"),
}
```

## Examples 📝

Check out the [examples](examples/) directory for more usage scenarios:

- Basic selection
- Multi-select with constraints
- Grouped options
- Custom filtering
- Disabled options
- Rich formatting
- Search functionality
- Keyboard shortcuts

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
