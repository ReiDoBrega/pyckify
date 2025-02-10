from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, Optional, Sequence, Tuple, TypeVar, Union
import msvcrt
import shutil
from rich.text import Text
from rich.style import Style
from rich.live import Live
from pyckify.options import Option, Separator
from pyckify.constants import (
    KEYS_ENTER, KEYS_UP, KEYS_DOWN, KEYS_SELECT, KEYS_SEARCH, KEYS_ESC, KEYS_SELECT_ALL,
    custom_theme, SYMBOL_ARROW, SYMBOL_UP, SYMBOL_DOWN, SYMBOL_SEARCH
)
from pyckify.result import PickResult
from pyckify.utils import clear_previous_lines

OPTION_T = TypeVar("OPTION_T", str, Option)
PICK_RETURN_T = Tuple[OPTION_T, int]

@dataclass
class Pyckify(Generic[OPTION_T]):
    options: Sequence[OPTION_T]
    title: Optional[str] = None
    subtitle: Optional[str] = None
    indicator: str = SYMBOL_ARROW
    defaultIndex: int = 0
    multiselect: bool = False
    minSelectionCount: int = 0
    maxSelectionCount: Optional[int] = None
    selectedIndexes: List[int] = field(init=False, default_factory=list)
    index: int = field(init=False, default=0)
    shouldExit: bool = field(init=False, default=False)
    scrollPosition: int = field(init=False, default=0)
    maxVisibleOptions: int = field(init=False, default=10)
    total_lines: int = field(init=False, default=0)
    last_move: str = field(init=False, default="none")
    search_string: str = field(init=False, default="")
    is_searching: bool = field(init=False, default=False)
    filter_fn: Optional[Callable[[OPTION_T], bool]] = None
    show_shortcuts: bool = True
    group_by: Optional[str] = None
    selection_message: str = field(init=False, default="")
    filtered_options: List[Tuple[int, OPTION_T]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        if len(self.options) == 0:
            raise ValueError("options should not be an empty list")
        
        if self.defaultIndex >= len(self.options):
            raise ValueError("defaultIndex should be less than the length of options")
        
        terminal_height = shutil.get_terminal_size().lines
        self.maxVisibleOptions = min(terminal_height - 4, 10)
        
        self.index = self.defaultIndex
        option = self.options[self.index]
        if isinstance(option, Option) and not option.enabled:
            self.moveDown()

    def formatOption(self, index: int, option: Any) -> Text:
        text = Text()
        
        # Add cursor indicator
        if index == self.index:
            text.append(f"{self.indicator} ", style=custom_theme["indicator"])
        else:
            text.append("  " + " " * len(self.indicator), style="")

        if isinstance(option, Option):
            # Add icon if present
            if option.icon:
                text.append(f"{option.icon} ", style="")

            if not option.enabled:
                base_style = custom_theme["disabled"]
            else:
                is_selected = index in self.selectedIndexes
                is_current = index == self.index
                
                if is_current and is_selected:
                    base_style = custom_theme["active_selected"]
                elif is_current:
                    base_style = custom_theme["active"]
                elif is_selected:
                    base_style = custom_theme["selected"]
                else:
                    base_style = Style()

            # Highlight search matches
            if self.search_string and self.search_string.lower() in option.label.lower():
                start = option.label.lower().index(self.search_string.lower())
                end = start + len(self.search_string)
                
                text.append(option.label[:start], style=base_style)
                text.append(option.label[start:end], style=custom_theme["search_match"])
                text.append(option.label[end:], style=base_style)
            else:
                text.append(option.label, style=base_style)
            
            # Add shortcut if present
            if self.show_shortcuts and option.shortcut:
                text.append(f" [{option.shortcut}]", style=custom_theme["shortcut"])
            
            # Add description if present
            if option.description:
                text.append(" ", style=base_style)
                text.append(f"- {option.description}", style=custom_theme["description"])
            
            # Add tags if present
            if option.tags:
                text.append(" [", style=custom_theme["description"])
                text.append(", ".join(option.tags), style=custom_theme["description"])
                text.append("]", style=custom_theme["description"])
        else:
            # Handle string options
            is_selected = index in self.selectedIndexes
            is_current = index == self.index
                
            if is_current and is_selected:
                base_style = custom_theme["active_selected"]
            elif is_current:
                base_style = custom_theme["active"]
            elif is_selected:
                base_style = custom_theme["selected"]
            else:
                base_style = Style()
                
            text.append(str(option), style=base_style)

        return text

    def generateOutput(self) -> Text:
        output = Text()
        line_count = 0
        
        # Title and subtitle
        if self.title:
            output.append(f"{self.title}\n", style=custom_theme["title"])
            line_count += 1
            
            if self.subtitle:
                output.append(f"{self.subtitle}\n", style=custom_theme["subtitle"])
                line_count += 1

        # Controls
        controls = []
        if self.multiselect:
            controls.extend(["↑↓ navigate", "space select", "a select all", "enter confirm"])
        else:
            controls.extend(["↑↓ navigate", "enter confirm"])
        controls.append("/ search")
        controls.append("esc clear filters/quit")
        
        output.append(" • ".join(controls) + "\n\n", style=custom_theme["controls"])
        line_count += 2

        # Selection message if present
        if self.selection_message:
            output.append(f"{self.selection_message}\n", style=custom_theme["description"])
            line_count += 1

        # Search bar if active
        if self.is_searching:
            output.append(f"{SYMBOL_SEARCH} ", style=custom_theme["search"])
            output.append(f"{self.search_string}█\n", style=custom_theme["search"])
            line_count += 1

        # Add filter indicator if filters are active
        if self.search_string or self.filter_fn:
            if self.search_string and self.filter_fn:
                filter_text = "Search and custom filters active"
            elif self.search_string:
                filter_text = f"Search filter: '{self.search_string}'"
            else:
                filter_text = "Custom filter active"
            output.append(f"🔍 {filter_text} (ESC to clear)\n", style=custom_theme["description"])
            line_count += 1

        # Get all filtered options
        filtered_options = self.getFilteredOptions()

        # Scroll indicator (top)
        if self.scrollPosition > 0:
            output.append(f"{SYMBOL_UP} More options above\n", style=custom_theme["scroll_indicator"])
            line_count += 1

        # Display visible options
        visible_options = filtered_options[self.scrollPosition:self.scrollPosition + self.maxVisibleOptions]
        
        # Group options if grouping is enabled
        if self.group_by:
            current_group = None
            for index, option in visible_options:
                if isinstance(option, Option) and option.group != current_group:
                    current_group = option.group
                    if current_group:
                        output.append(f"\n{current_group}\n", style=custom_theme["group_header"])
                        line_count += 2
                
                output.append(self.formatOption(index, option))
                output.append("\n")
                line_count += 1
        else:
            for index, option in visible_options:
                output.append(self.formatOption(index, option))
                output.append("\n")
                line_count += 1

        # Scroll indicator (bottom)
        if self.scrollPosition + self.maxVisibleOptions < len(filtered_options):
            output.append(f"{SYMBOL_DOWN} More options below\n", style=custom_theme["scroll_indicator"])
            line_count += 1

        # Show filtered results count if filtering is active
        if self.search_string or self.filter_fn:
            total_options = len(self.options)
            filtered_count = len(filtered_options)
            if filtered_count < total_options:
                output.append(f"Showing {filtered_count} of {total_options} options\n", 
                            style=custom_theme["description"])
                line_count += 1

        # Selection count for multiselect with enhanced feedback
        if self.multiselect:
            count_text = f"Selected: {len(self.selectedIndexes)}"
            if self.maxSelectionCount:
                count_text += f" / {self.maxSelectionCount}"
            if self.minSelectionCount > 0:
                count_text += f" (minimum: {self.minSelectionCount})"
            output.append(f"\n{count_text}", style=custom_theme["description"])
            line_count += 2

        self.total_lines = line_count
        return output
    
    def getFilteredOptions(self) -> List[Tuple[int, OPTION_T]]:
        filtered = []
        for index, option in enumerate(self.options):
            # Apply search filter
            if self.search_string:
                if isinstance(option, Option):
                    if self.search_string.lower() not in option.label.lower():
                        continue
                elif self.search_string.lower() not in str(option).lower():
                    continue
            
            # Apply custom filter
            if self.filter_fn and not self.filter_fn(option):
                continue
                
            filtered.append((index, option))  # Keep track of the original index
        
        # Update the filtered_options attribute
        self.filtered_options = filtered
        
        # If the current index is not in filtered options, select the first available option
        if not any(index == self.index for index, _ in filtered):
            if filtered:
                self.index = filtered[0][0]
                self.scrollPosition = 0

        # Ensure scroll position is valid
        if filtered:
            max_scroll = max(0, len(filtered) - self.maxVisibleOptions)
            self.scrollPosition = min(self.scrollPosition, max_scroll)
        
        # Return all filtered options, not just visible ones
        return filtered

    def handleSearchInput(self, key: bytes) -> None:
        if key == b"\r":  # Enter
            self.is_searching = False
        elif key == b"\x1b":  # Escape
            self.search_string = ""  # Clear search
            self.is_searching = False
            self.resetFilter()  # Reset any custom filters
        elif key == b"\x08":  # Backspace
            self.search_string = self.search_string[:-1]
        else:
            try:
                char = key.decode('utf-8')
                self.search_string += char
            except UnicodeDecodeError:
                pass

    def selectAll(self) -> None:
        if self.multiselect:
            if len(self.selectedIndexes) == len([opt for opt in self.options if not isinstance(opt, Option) or opt.enabled]):
                # If all options are already selected, unselect all
                self.selectedIndexes = []
            else:
                # Otherwise, select all enabled options
                self.selectedIndexes = [
                    i for i, opt in enumerate(self.options)
                    if not isinstance(opt, Option) or opt.enabled
                ]
                if self.maxSelectionCount:
                    self.selectedIndexes = self.selectedIndexes[:self.maxSelectionCount]

    def resetFilter(self) -> None:
        """Reset all filtering and restore original options view"""
        self.search_string = ""
        self.filter_fn = None
        self.scrollPosition = 0
        # Reset index to first enabled option
        for i, option in enumerate(self.options):
            if not isinstance(option, Option) or option.enabled:
                self.index = i
                break

    def runLoop(self) -> Union[List[PICK_RETURN_T], PICK_RETURN_T]:
        self.clearInputBuffer()
        
        with Live(self.generateOutput(), refresh_per_second=10, auto_refresh=True) as live:
            while not self.shouldExit:
                current_output = self.generateOutput()
                live.update(current_output)
                
                key = self.getKey()

                if self.is_searching:
                    self.handleSearchInput(key)
                    continue

                if key in KEYS_UP:
                    self.moveUp()
                elif key in KEYS_DOWN:
                    self.moveDown()
                elif key in KEYS_ENTER:
                    if self.multiselect:
                        if len(self.selectedIndexes) < self.minSelectionCount:
                            self.selection_message = f"⚠️ Please select at least {self.minSelectionCount} options"
                            continue
                        else:
                            self.selection_message = ""
                    
                    live.stop()
                    actual_lines = len(str(current_output).split('\n'))
                    clear_previous_lines(actual_lines)
                    return self.getSelected()
                elif key in KEYS_SELECT and self.multiselect:
                    self.markIndex()
                elif key in KEYS_SEARCH:
                    self.is_searching = True
                    self.selection_message = ""
                elif key in KEYS_ESC:
                    # If filtering is active, clear it instead of exiting
                    if self.search_string or self.filter_fn:
                        self.resetFilter()
                        self.selection_message = "Filters cleared"
                    else:
                        self.shouldExit = True
                        live.stop()
                        actual_lines = len(str(current_output).split('\n'))
                        clear_previous_lines(actual_lines)
                        return None
                elif key in KEYS_SELECT_ALL and self.multiselect:
                    if self.maxSelectionCount and len(self.options) > self.maxSelectionCount:
                        self.selection_message = f"⚠️ Cannot select all: maximum is {self.maxSelectionCount}"
                    else:
                        self.selectAll()
                        self.selection_message = ""

    def moveDown(self) -> None:
        self.last_move = "down"
        if not self.filtered_options:
            return  # No filtered options to navigate

        # Find current position in filtered options
        current_filtered_index = next((i for i, (idx, _) in enumerate(self.filtered_options) if idx == self.index), -1)
        
        if current_filtered_index == -1:
            # If current index not found, start from beginning
            if self.filtered_options:
                self.index = self.filtered_options[0][0]
                self.scrollPosition = 0
            return

        # Calculate next index
        next_filtered_index = (current_filtered_index + 1) % len(self.filtered_options)
        self.index = self.filtered_options[next_filtered_index][0]

        # Adjust scroll position if necessary
        if next_filtered_index >= self.scrollPosition + self.maxVisibleOptions:
            self.scrollPosition = min(
                next_filtered_index - self.maxVisibleOptions + 1,
                len(self.filtered_options) - self.maxVisibleOptions
            )
        elif next_filtered_index < self.scrollPosition:
            self.scrollPosition = 0

        # Skip disabled options
        option = self.options[self.index]
        if isinstance(option, Option) and not option.enabled:
            self.moveDown()

    def moveUp(self) -> None:
        self.last_move = "up"
        if not self.filtered_options:
            return  # No filtered options to navigate

        # Find current position in filtered options
        current_filtered_index = next((i for i, (idx, _) in enumerate(self.filtered_options) if idx == self.index), -1)
        
        if current_filtered_index == -1:
            # If current index not found, start from end
            if self.filtered_options:
                self.index = self.filtered_options[-1][0]
                self.scrollPosition = max(0, len(self.filtered_options) - self.maxVisibleOptions)
            return

        # Calculate previous index
        prev_filtered_index = (current_filtered_index - 1) % len(self.filtered_options)
        self.index = self.filtered_options[prev_filtered_index][0]

        # Adjust scroll position if necessary
        if prev_filtered_index < self.scrollPosition:
            self.scrollPosition = prev_filtered_index
        elif prev_filtered_index >= self.scrollPosition + self.maxVisibleOptions:
            self.scrollPosition = max(0, len(self.filtered_options) - self.maxVisibleOptions)

        # Skip disabled options
        option = self.options[self.index]
        if isinstance(option, Option) and not option.enabled:
            self.moveUp()

    def markIndex(self) -> None:
        if not self.filtered_options:
            return  # No filtered options to select

        # Find the current option in filtered options
        try:
            visible_options = self.filtered_options[self.scrollPosition:self.scrollPosition + self.maxVisibleOptions]
            current_visible_index = next((i for i, (idx, _) in enumerate(visible_options) if idx == self.index), None)
            
            if current_visible_index is None:
                return  # Current index not found in visible options
                
            original_index = visible_options[current_visible_index][0]
            option = self.options[original_index]
            
            if self.multiselect and not isinstance(option, Separator):
                if original_index in self.selectedIndexes:
                    self.selectedIndexes.remove(original_index)
                    self.selection_message = ""
                else:
                    if self.maxSelectionCount and len(self.selectedIndexes) >= self.maxSelectionCount:
                        self.selection_message = f"⚠️ Cannot select more than {self.maxSelectionCount} options"
                        return
                    self.selectedIndexes.append(original_index)
                    self.selection_message = ""
                    
        except IndexError:
            return  # Handle any remaining index errors gracefully

    def updateScrollPosition(self) -> None:
        filtered_indices = [index for index, _ in self.filtered_options]
        if self.index not in filtered_indices:
            return

        current_position = filtered_indices.index(self.index)
        
        # Adjust scroll position if current selection is out of view
        if current_position >= self.scrollPosition + self.maxVisibleOptions:
            self.scrollPosition = max(0, current_position - self.maxVisibleOptions + 1)
        elif current_position < self.scrollPosition:
            self.scrollPosition = current_position

    def getSelected(self) -> Union[List[PICK_RETURN_T], PICK_RETURN_T]:
        if self.multiselect:
            returnTuples = []
            for selected in self.selectedIndexes:
                returnTuples.append((self.options[selected], selected))
            return returnTuples
        else:
            return self.options[self.index], self.index

    def start(self):
        return self.runLoop()

    def clearInputBuffer(self):
        while msvcrt.kbhit():
            msvcrt.getch()

    def getKey(self):
        key = msvcrt.getch()
        if key == b"\xe0":
            key = msvcrt.getch()
        return key

def separatePickResult(result: Union[List[PICK_RETURN_T], PICK_RETURN_T]) -> PickResult:
    if isinstance(result, list):
        values = [item[0] for item in result]
        indices = [item[1] for item in result]
        return PickResult(values, indices)
    else:
        value, index = result
        return PickResult(value, index)
    
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
) -> Union[PickResult, Union[List[PICK_RETURN_T], PICK_RETURN_T]]:
    picker = Pyckify(
        options,
        title,
        subtitle,
        indicator,
        defaultIndex,
        multiselect,
        minSelectionCount,
        maxSelectionCount,
        filter_fn=filter_fn,
        show_shortcuts=show_shortcuts,
        group_by=group_by,
    )
    result = picker.start()
    
    if result is None:
        return None
        
    if separateValues:
        if isinstance(result, list):
            values = [item[0] for item in result]
            indices = [item[1] for item in result]
            return PickResult(values, indices)
        else:
            value, index = result
            return PickResult(value, index)
    return result