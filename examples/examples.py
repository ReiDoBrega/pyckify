from typing import List, Optional
from dataclasses import dataclass
from pyckify import Pyck, Option
from pyckify.constants import SYMBOL_ARROW

def showcase_basic():
    """Basic usage with simple string options"""
    options = ["Red", "Blue", "Green", "Yellow", "Purple"]
    result = Pyck(
        options=options,
        title="Basic Color Selection",
        subtitle="Choose your favorite color",
        indicator=SYMBOL_ARROW
    )
    print(f"Selected color: {result[0]}")

def showcase_multiselect():
    """Demonstrate multiselect with min/max limits"""
    options = [
        Option("🍎 Apple", description="Fresh from the garden"),
        Option("🍌 Banana", description="Rich in potassium"),
        Option("🍊 Orange", description="Vitamin C boost"),
        Option("🍇 Grapes", description="Sweet and juicy"),
        Option("🥝 Kiwi", description="Tropical delight")
    ]
    
    result = Pyck(
        options=options,
        title="Fruit Selection",
        subtitle="Choose 2-4 fruits for your basket",
        multiselect=True,
        minSelectionCount=2,
        maxSelectionCount=4,
        separateValues=True
    )
    
    if result:
        print("\nYour fruit basket:")
        for fruit in result.values:
            print(f"- {fruit.label}")

def showcase_grouped_options():
    """Demonstrate grouped options with icons and shortcuts"""
    options = [
        # Development Tools
        Option("📝 VS Code", description="Popular code editor", 
               group="📼 Development Tools", shortcut="v", tags=["editor", "free"]),
        Option("🎨 Sublime Text", description="Fast and lightweight", 
               group="📼 Development Tools", shortcut="s", tags=["editor", "paid"]),
        Option("⚡ PyCharm", description="Python IDE", 
               group="📼 Development Tools", shortcut="p", tags=["ide", "paid"]),
        
        # Version Control
        Option("😺 GitHub", description="Code hosting platform", 
               group="Version Control", shortcut="g", tags=["git", "cloud"]),
        Option("🦊 GitLab", description="DevOps platform", 
               group="Version Control", shortcut="l", tags=["git", "cloud"]),
        Option("🪣 Bitbucket", description="Enterprise git solution", 
               group="Version Control", shortcut="b", tags=["git", "cloud"]),
        
        # Deployment
        Option("☁️ AWS", description="Cloud platform", 
               group="Deployment", shortcut="a", tags=["cloud", "paid"]),
        Option("🚀 Heroku", description="PaaS solution", 
               group="Deployment", shortcut="h", tags=["cloud", "paas"]),
        Option("📦 Docker", description="Containerization", 
               group="Deployment", shortcut="d", tags=["container", "free"]),
    ]
    
    result = Pyck(
        options=options,
        title="Development Stack",
        subtitle="Select your preferred tools",
        multiselect=True,
        group_by="group",
        show_shortcuts=True,
        separateValues=True
    )
    
    if result:
        print("\nSelected tools:")
        for tool in result.values:
            print(f"- {tool.label} [{', '.join(tool.tags)}]")

def showcase_filtered_selection():
    """Demonstrate custom filtering and search"""
    @dataclass
    class Language:
        name: str
        type: str
        year: int
        popularity: int  # 1-10 scale
        
    options = [
        Option(f"🌟 {lang.name}", 
               description=f"Created in {lang.year}", 
               value=lang,
               tags=[lang.type],
               group=f"Popularity: {lang.popularity}/10")
        for lang in [
            Language("Python", "interpreted", 1991, 10),
            Language("JavaScript", "interpreted", 1995, 9),
            Language("Java", "compiled", 1995, 8),
            Language("C++", "compiled", 1985, 7),
            Language("Ruby", "interpreted", 1995, 6),
            Language("Go", "compiled", 2009, 7),
            Language("Rust", "compiled", 2010, 7),
            Language("Swift", "compiled", 2014, 6),
            Language("Kotlin", "compiled", 2011, 6),
            Language("TypeScript", "transpiled", 2012, 8)
        ]
    ]
    
    # Custom filter for modern languages
    def modern_languages(option: Option) -> bool:
        lang: Language = option.value  # type: ignore
        return lang.year >= 2010
    
    result = Pyck(
        options=options,
        title="Programming Language Selection",
        subtitle="Use '/' to search, filtered to show modern languages",
        multiselect=True,
        filter_fn=modern_languages,
        group_by="group",
        separateValues=True
    )
    
    if result:
        print("\nSelected languages:")
        for option in result.values:
            lang = option.value
            print(f"- {lang.name} ({lang.type}, {lang.year})")

def showcase_disabled_options():
    """Demonstrate disabled options"""
    options = [
        Option("✨ Premium Plan", description="All features included", enabled=True),
        Option("💎 Enterprise Plan", description="Custom solutions", enabled=True),
        Option("🔒 Legacy Plan", description="No longer available", enabled=False),
        Option("⭐ Basic Plan", description="Limited features", enabled=True),
    ]
    
    result = Pyck(
        options=options,
        title="Subscription Plans",
        subtitle="Select an available plan",
        separateValues=True
    )
    
    if result:
        print(f"\nSelected plan: {result.values.label}")

def main():
    """Run all showcases"""
    showcases = [
        ("Basic Selection", showcase_basic),
        ("Multiselect with Limits", showcase_multiselect),
        ("Grouped Options", showcase_grouped_options),
        ("Filtered Selection", showcase_filtered_selection),
        ("Disabled Options", showcase_disabled_options)
    ]
    
    # Let user choose which showcase to run
    options = [Option(title, description=f"Showcase {title}")
               for title, _ in showcases]
    
    while True:
        result = Pyck(
            options=options,
            title="Picker Showcase",
            subtitle="Choose a showcase to run (ESC to exit)",
            separateValues=True
        )
        
        if not result:
            break
            
        print("\n" + "="*50)
        print(f"Running showcase: {result.values.label}")
        print("="*50 + "\n")
        
        showcase_func = next(func for title, func in showcases 
                           if title == result.values.label)
        showcase_func()
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()