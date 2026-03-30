from __future__ import annotations
from dataclasses import dataclass
from typing import List

from pyckify import Option, Pyck, Separator, set_theme
from pyckify.constants import SYMBOL_ARROW
from pyckify.options import from_dict, make_options


def showcase_basic():
    """Plain strings, single select."""
    options = ["Red", "Blue", "Green", "Yellow", "Purple", "Cyan", "Magenta"]
    result = Pyck(
        options=options,
        title="Basic Color Selection",
        subtitle="Choose your favourite colour",
        indicator=SYMBOL_ARROW,
    )
    if result:
        print(f"Selected: {result[0]}")


def showcase_multiselect():
    """Multiselect with constraints and circle indicators."""
    options = [
        Option("🍎 Apple",      description="Fresh from the garden", tags=["sweet"]),
        Option("🍌 Banana",     description="Rich in potassium",     tags=["sweet"]),
        Option("🍊 Orange",     description="Vitamin C boost",       tags=["citrus"]),
        Option("🍇 Grapes",     description="Sweet and juicy",       tags=["sweet"]),
        Option("🥝 Kiwi",       description="Tropical delight",      tags=["exotic"]),
        Option("🍓 Strawberry", description="Summer favourite",      tags=["sweet"]),
        Option("🍋 Lemon",      description="Sour but useful",       tags=["citrus"]),
    ]
    result = Pyck(
        options=options,
        title="Fruit Basket",
        subtitle="Choose 2–4 fruits  (# to filter by tag)",
        multiselect=True,
        minSelectionCount=2,
        maxSelectionCount=4,
        multiselect_indicator="circle",   # NEW
        show_tags=True,                   # NEW
        separateValues=True,
    )
    if result:
        print("\nYour basket:")
        for fruit in result.values:
            print(f"  {fruit.label}")

def showcase_grouped():
    """Groups, shortcuts, and check-style multiselect indicators."""
    options = [
        Option("📝 VS Code",      description="Popular code editor",       group="Development",    shortcut="v", tags=["editor","free"]),
        Option("⚡ PyCharm",      description="Python IDE",                 group="Development",    shortcut="p", tags=["ide","paid"]),
        Option("🎨 Neovim",       description="Blazing-fast terminal edit", group="Development",    shortcut="n", tags=["editor","free"]),
        Option("😺 GitHub",       description="Code hosting platform",      group="Version Control",shortcut="g", tags=["git","cloud"]),
        Option("🦊 GitLab",       description="DevOps platform",            group="Version Control",shortcut="l", tags=["git","cloud"]),
        Option("🪣 Bitbucket",    description="Enterprise git",             group="Version Control",shortcut="b", tags=["git","cloud"]),
        Option("☁️ AWS",          description="Cloud platform",             group="Deployment",     shortcut="a", tags=["cloud","paid"]),
        Option("🐳 Docker",       description="Containerisation",           group="Deployment",     shortcut="d", tags=["container","free"]),
        Option("🚀 Fly.io",       description="Edge deployment",            group="Deployment",     shortcut="f", tags=["cloud","paid"]),
    ]
    result = Pyck(
        options=options,
        title="Development Stack",
        subtitle="Select your tools  (s to sort, t to switch theme)",
        multiselect=True,
        group_by="group",
        show_shortcuts=True,
        multiselect_indicator="check",   # NEW – checkboxes
        separateValues=True,
    )
    if result:
        print("\nSelected tools:")
        for tool in result.values:
            print(f"  {tool.label}  [{', '.join(tool.tags)}]")


def showcase_fuzzy_and_sort():
    """Fuzzy search with ranked results and sort-mode cycling."""

    @dataclass
    class Language:
        name: str
        lang_type: str
        year: int
        popularity: int

    langs = [
        Language("Python",     "interpreted", 1991, 10),
        Language("JavaScript", "interpreted", 1995,  9),
        Language("Java",       "compiled",    1995,  8),
        Language("C++",        "compiled",    1985,  7),
        Language("Ruby",       "interpreted", 1995,  6),
        Language("Go",         "compiled",    2009,  7),
        Language("Rust",       "compiled",    2010,  7),
        Language("Swift",      "compiled",    2014,  6),
        Language("Kotlin",     "compiled",    2011,  6),
        Language("TypeScript", "transpiled",  2012,  8),
        Language("Zig",        "compiled",    2016,  5),
        Language("Elixir",     "interpreted", 2011,  5),
    ]
    options = [
        Option(
            label=f"{'★' * lang.popularity:<10} {lang.name}",
            description=f"{lang.lang_type} · {lang.year}",
            value=lang,
            tags=[lang.lang_type],
            group=f"Popularity {lang.popularity}/10",
        )
        for lang in langs
    ]

    def modern_only(opt: Option) -> bool:
        return opt.value.year >= 2009

    result = Pyck(
        options=options,
        title="Language Picker",
        subtitle="/ fuzzy-search • s sort • # tag-filter • modern langs only",
        multiselect=True,
        filter_fn=modern_only,
        group_by="group",
        fuzzy=True,              # NEW
        show_fuzzy_score=True,   # NEW
        separateValues=True,
    )
    if result:
        print("\nSelected:")
        for opt in result.values:
            print(f"  {opt.value.name} ({opt.value.year})")


def showcase_preview():
    """Long-form preview text shown in a pane below the list."""
    options = [
        Option(
            "🐍 Python",
            description="General-purpose scripting",
            tags=["interpreted"],
            preview=(
                "Python is a high-level, dynamically typed language prized for\n"
                "its readability and vast ecosystem. Ideal for data science,\n"
                "web backends (Django/Flask), automation, and AI/ML workloads.\n"
                "Creator: Guido van Rossum, 1991."
            ),
        ),
        Option(
            "🦀 Rust",
            description="Systems programming without GC",
            tags=["compiled"],
            preview=(
                "Rust gives you memory safety without a garbage collector via\n"
                "its ownership system. Used in browsers (Firefox), OS kernels,\n"
                "WebAssembly, and game engines. Creator: Graydon Hoare, 2010."
            ),
        ),
        Option(
            "🐹 Go",
            description="Concurrency-first cloud language",
            tags=["compiled"],
            preview=(
                "Go (Golang) was designed at Google for large-scale networked\n"
                "services. Simple syntax, first-class goroutines, and a fat\n"
                "standard library make it the go-to for CLIs and microservices.\n"
                "Creators: Pike, Thompson, Griesemer, 2009."
            ),
        ),
    ]
    result = Pyck(
        options=options,
        title="Language Deep-Dive",
        subtitle="Navigate to read the preview pane",
        show_preview=True,        # NEW
        preview_position="bottom", # NEW
        separateValues=True,
    )
    if result:
        print(f"\nChose: {result.values.label}")

def showcase_themes():
    """Switch between built-in themes with the t key."""
    options = [
        Option("Option Alpha",   description="First choice",  tags=["a"]),
        Option("Option Beta",    description="Second choice", tags=["b"]),
        Option("Option Gamma",   description="Third choice",  tags=["c"]),
        Option("Option Delta",   description="Fourth choice", tags=["d"]),
    ]
    for theme_name in ("default", "dracula", "nord", "monokai",
                       "catppuccin", "solarized", "one_dark", "gruvbox"):
        print(f"\n  → Theme: {theme_name}  (press Enter to proceed)")
        Pyck(
            options=options,
            title=f"Theme: {theme_name}",
            subtitle="Press t to cycle themes live, Enter to confirm",
            theme=theme_name,     # NEW
            show_tags=True,
        )


def showcase_advanced_options():
    """Separators, disabled items, and per-option Rich style overrides."""
    options = [
        Separator("── Recommended ──────────────────"),
        Option("✨ Premium Plan",    description="All features",       enabled=True,  style="bold green",   tags=["paid"]),
        Option("💎 Enterprise Plan", description="Custom SLA + SSO",   enabled=True,  style="bold cyan",    tags=["paid"]),
        Separator("── Legacy (unavailable) ─────────"),
        Option("🔒 Pro v1",          description="Discontinued",       enabled=False, tags=["legacy"]),
        Option("🔒 Starter v1",      description="Discontinued",       enabled=False, tags=["legacy"]),
        Separator("── Free tiers ────────────────────"),
        Option("⭐ Hobbyist",         description="500 req/day",        enabled=True,  tags=["free"]),
        Option("⭐ Open-Source",      description="Unlimited, OSS only",enabled=True,  tags=["free"]),
    ]
    result = Pyck(
        options=options,
        title="Subscription Plans",
        subtitle="Disabled options are shown but not selectable",
        separateValues=True,
    )
    if result:
        print(f"\nChosen plan: {result.values.label}")


def showcase_helpers():
    """Build Option lists from plain dicts or any iterable."""
    # from_dict
    raw = [
        {"label": "AWS S3",     "description": "Object storage",     "tags": ["storage"]},
        {"label": "GCS",        "description": "Google Cloud Storage","tags": ["storage"]},
        {"label": "Cloudflare R2","description": "Zero-egress S3",   "tags": ["storage"]},
    ]
    options = from_dict(raw)

    result = Pyck(
        options=options,
        title="Built from dicts",
        subtitle="Options loaded via from_dict()",
        separateValues=True,
    )
    if result:
        print(f"\nSelected: {result.values.label}")

def showcase_confirm_on_single():
    """Auto-confirm when the search yields exactly one visible option."""
    options = [
        Option("apple",  tags=["fruit"]),
        Option("apricot",tags=["fruit"]),
        Option("avocado",tags=["fruit"]),
        Option("banana", tags=["fruit"]),
        Option("cherry", tags=["fruit"]),
    ]
    result = Pyck(
        options=options,
        title="Confirm-on-single demo",
        subtitle="Type until only one match remains – it confirms automatically",
        confirm_on_single=True,   # NEW
        separateValues=True,
    )
    if result:
        print(f"\nAuto-confirmed: {result.values.label}")


def main():
    showcases = [
        ("1 · Basic single-select",       showcase_basic),
        ("2 · Multiselect + min/max",      showcase_multiselect),
        ("3 · Grouped + shortcuts",        showcase_grouped),
        ("4 · Fuzzy search + sort",        showcase_fuzzy_and_sort),
        ("5 · Preview pane",               showcase_preview),
        ("6 · Theme showcase",             showcase_themes),
        ("7 · Separators + per-opt style", showcase_advanced_options),
        ("8 · from_dict / make_options",   showcase_helpers),
        ("9 · confirm_on_single",          showcase_confirm_on_single),
    ]

    menu_options = [
        Option(label=title, description=f"Run showcase #{i+1}")
        for i, (title, _) in enumerate(showcases)
    ]

    while True:
        result = Pyck(
            options=menu_options,
            title="🎯 Pyckify Feature Showcase",
            subtitle="Choose a showcase  (Esc to quit)",
            theme="dracula",
            separateValues=True,
        )
        if not result:
            break

        chosen_label = result.values.label
        _, fn = next((t, f) for t, f in showcases if t == chosen_label)

        print("\n" + "═" * 56)
        print(f"  {chosen_label}")
        print("═" * 56 + "\n")

        fn()
        input("\nPress Enter to return to menu…")


if __name__ == "__main__":
    main()
