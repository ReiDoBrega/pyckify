
from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Generic, List,
    Optional, Sequence, Set, Tuple, TypeVar, Union,
)

from rich.live import Live
from rich.style import Style
from rich.text import Text

from pyckify.constants import (
    KEYS_COPY, KEYS_DOWN, KEYS_END, KEYS_ENTER, KEYS_ESC, KEYS_HELP,
    KEYS_HOME, KEYS_INVERT, KEYS_LEFT, KEYS_PAGE_DOWN, KEYS_PAGE_UP,
    KEYS_RIGHT, KEYS_SEARCH, KEYS_SELECT, KEYS_SELECT_ALL, KEYS_SORT,
    KEYS_TAG, KEYS_THEME, KEYS_UP, SYMBOL_ARROW, SYMBOL_CHECKED,
    SYMBOL_CIRCLE_EMPTY, SYMBOL_CIRCLE_FILLED, SYMBOL_COLLAPSE, SYMBOL_COPY,
    SYMBOL_DOWN, SYMBOL_EXPAND, SYMBOL_LOCK, SYMBOL_PREVIEW, SYMBOL_RADIO_OFF,
    SYMBOL_RADIO_ON, SYMBOL_SEARCH, SYMBOL_STAR, SYMBOL_TAG, SYMBOL_UNCHECKED,
    SYMBOL_UP, THEMES, custom_theme, set_theme,
)
from pyckify.options import Option, Separator
from pyckify.result import PickResult
from pyckify.utils import KeyReader, copy_to_clipboard, get_terminal_size

OPTION_T = TypeVar("OPTION_T", str, Option)
PICK_RETURN_T = Tuple[OPTION_T, int]

SORT_MODES = ("original", "a-z", "z-a", "selected-first")

INDICATOR_STYLES: Dict[str, Tuple[str, str]] = {
    "circle":   (SYMBOL_CIRCLE_FILLED,  SYMBOL_CIRCLE_EMPTY),
    "check":    (SYMBOL_CHECKED,        SYMBOL_UNCHECKED),
    "star":     (SYMBOL_STAR,           " "),
    "radio":    (SYMBOL_RADIO_ON,       SYMBOL_RADIO_OFF),
}

# Keys that are reserved for global actions and must NOT be passed to shortcut
# lookup when the user explicitly presses them (they have global handlers).
# However, if an option has that shortcut AND the key would otherwise be global,
# the option shortcut wins.
_GLOBAL_KEYS_BYTES: Set[bytes] = {
    b"a",  # select-all
    b"i",  # invert
    b"s",  # sort
    b"t",  # theme
    b"c",  # copy
    b"?",  # help
    b"/",  # search
    b"#",  # tag-filter
    b" ",  # space / select
}

def _shortcut_exists(options: Sequence, char: str) -> bool:
    """Return True if any *enabled* Option has shortcut == char."""
    for opt in options:
        if isinstance(opt, Option) and opt.enabled and opt.shortcut == char:
            return True
    return False

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
    filter_fn: Optional[Callable[[OPTION_T], bool]] = None
    show_shortcuts: bool = True
    group_by: Optional[str] = None
    theme: str = "default"
    fuzzy: bool = True
    show_preview: bool = False
    preview_position: str = "bottom"        # "bottom" or "right"
    show_border: bool = False
    multiselect_indicator: str = "circle"   # "circle" | "check" | "star" | "radio"
    confirm_on_single: bool = False
    allow_empty: bool = False
    show_tags: bool = True
    show_fuzzy_score: bool = False
    max_visible: Optional[int] = None
    page_size: Optional[int] = None
    jump_on_shortcut_select: bool = False
    selectedIndexes: List[int]  = field(init=False, default_factory=list)
    index: int                  = field(init=False, default=0)
    shouldExit: bool            = field(init=False, default=False)
    scrollPosition: int         = field(init=False, default=0)
    maxVisibleOptions: int      = field(init=False, default=10)
    total_lines: int            = field(init=False, default=0)
    search_string: str          = field(init=False, default="")
    is_searching: bool          = field(init=False, default=False)
    tag_filter: str             = field(init=False, default="")
    is_tag_filtering: bool      = field(init=False, default=False)
    selection_message: str      = field(init=False, default="")
    filtered_options: List[Tuple[int, OPTION_T]] = field(init=False, default_factory=list)
    sort_mode_index: int        = field(init=False, default=0)
    theme_index: int            = field(init=False, default=0)
    show_help: bool             = field(init=False, default=False)
    clipboard_message: str      = field(init=False, default="")
    _key_reader: KeyReader      = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if len(self.options) == 0:
            raise ValueError("options must not be empty")
        if self.defaultIndex >= len(self.options):
            raise ValueError("defaultIndex out of range")
        if self.multiselect_indicator not in INDICATOR_STYLES:
            raise ValueError(
                f"multiselect_indicator must be one of {list(INDICATOR_STYLES)}"
            )

        set_theme(self.theme)
        self.theme_index = list(THEMES).index(self.theme)

        cols, lines = get_terminal_size()
        if self.max_visible is not None:
            self.maxVisibleOptions = self.max_visible
        else:
            self.maxVisibleOptions = max(3, min(lines - 8, 15))

        if self.page_size is None:
            self.page_size = max(1, self.maxVisibleOptions - 1)

        self._key_reader = KeyReader()
        self.index = self.defaultIndex
        option = self.options[self.index]
        if isinstance(option, Option) and not option.enabled:
            self.moveDownInitial()

    def moveDownInitial(self) -> None:
        """Find the first enabled option at startup."""
        for i, opt in enumerate(self.options):
            if not isinstance(opt, Option) or opt.enabled:
                self.index = i
                return

    @property
    def _theme(self):
        return custom_theme

    def msIndicator(self, selected: bool) -> str:
        filled, empty = INDICATOR_STYLES[self.multiselect_indicator]
        return filled if selected else empty

    def _option_label(self, option: Any) -> str:
        if isinstance(option, Option):
            return option.label
        return str(option)

    def formatOption(self, idx: int, option: Any) -> Text:  # noqa: C901
        t = custom_theme
        text = Text()
        is_current   = idx == self.index
        is_selected  = idx in self.selectedIndexes
        is_disabled  = isinstance(option, Option) and not option.enabled
        is_separator = isinstance(option, Separator)

        if isinstance(option, Option) and option.style:
            try:
                base_style = Style.parse(option.style)
            except Exception:
                base_style = Style()
        elif is_disabled:
            base_style = t["disabled"]
        elif is_current and is_selected:
            base_style = t["active_selected"]
        elif is_current:
            base_style = t["active"]
        elif is_selected:
            base_style = t["selected"]
        else:
            base_style = Style()

        if is_separator:
            text.append(f"  {option.label}\n", style=t["disabled"])
            return text

        if is_current:
            text.append(f"{self.indicator} ", style=t["indicator"])
        else:
            text.append("  " + " " * len(self.indicator), style="")

        if self.multiselect:
            badge = self.msIndicator(is_selected)
            badge_style = t["selected"] if is_selected else t["disabled"]
            text.append(f"{badge} ", style=badge_style)

        if is_disabled:
            text.append(f"{SYMBOL_LOCK} ", style=t["disabled"])

        if isinstance(option, Option) and option.icon:
            text.append(f"{option.icon} ", style=base_style)

        label = self._option_label(option)
        query = self.search_string.lower()
        if query and query in label.lower() and not self.fuzzy:
            start = label.lower().index(query)
            end   = start + len(query)
            text.append(label[:start],    style=base_style)
            text.append(label[start:end], style=t["search_match"])
            text.append(label[end:],      style=base_style)
        else:
            text.append(label, style=base_style)

        if self.show_shortcuts and isinstance(option, Option) and option.shortcut:
            text.append(f" [{option.shortcut}]", style=t["shortcut"])

        if isinstance(option, Option) and option.description:
            text.append(f"  {option.description}", style=t["description"])

        if self.show_tags and isinstance(option, Option) and option.tags:
            tag_str = " ".join(f"{SYMBOL_TAG}{tag}" for tag in option.tags)
            text.append(f"  {tag_str}", style=t["tag"])

        if self.show_fuzzy_score and self.search_string and isinstance(option, Option):
            score = option.fuzzy_score(self.search_string)
            if score:
                text.append(f"  [{score}]", style=t["fuzzy_score"])

        if not self.show_preview and isinstance(option, Option) and option.preview:
            text.append(f" {SYMBOL_PREVIEW}", style=t["fuzzy_score"])

        return text

    def helpOverlay(self) -> Text:
        t = custom_theme
        text = Text()
        text.append("─── Keyboard Help ───\n", style=t["title"])
        bindings = [
            ("↑ / k",         "Move up"),
            ("↓ / j",         "Move down"),
            ("PgUp / PgDn",   "Scroll page"),
            ("Home / End",    "Jump to top / bottom"),
            ("Enter",         "Confirm selection"),
            ("Space",         "Toggle selection (multiselect)"),
            ("a",             "Select / deselect all  [overridden by shortcut]"),
            ("i",             "Invert selection       [overridden by shortcut]"),
            ("/",             "Search"),
            ("#",             "Filter by tag"),
            ("s",             "Cycle sort mode        [overridden by shortcut]"),
            ("t",             "Cycle theme            [overridden by shortcut]"),
            ("c",             "Copy label to clipboard[overridden by shortcut]"),
            ("?",             "Toggle this help"),
            ("Esc",           "Clear filter / quit"),
        ]
        for key, desc in bindings:
            text.append(f"  {key:<22}", style=t["shortcut"])
            text.append(f"{desc}\n",   style=t["controls"])
        text.append(
            "\n  Note: option shortcuts always take priority over global keys.\n",
            style=t["warning"],
        )
        return text

    def previewText(self) -> Optional[Text]:
        if not self.show_preview:
            return None
        try:
            option = self.options[self.index]
        except IndexError:
            return None
        if not isinstance(option, Option) or not option.preview:
            return None
        t = custom_theme
        text = Text()
        text.append(option.preview, style=t["preview_text"])
        return text

    def generateOutput(self) -> Text:  # noqa: C901
        t = custom_theme
        output = Text()

        if self.show_help:
            output.append_text(self.helpOverlay())
            output.append("\n[?] or [Esc] to close help", style=t["controls"])
            return output

        if self.title:
            output.append(f"{self.title}\n", style=t["title"])
            if self.subtitle:
                output.append(f"{self.subtitle}\n", style=t["subtitle"])

        sort_label  = f"sort:{SORT_MODES[self.sort_mode_index]}"
        theme_label = f"theme:{list(THEMES)[self.theme_index]}"
        output.append(f"  {sort_label}  {theme_label}\n", style=t["help"])

        if self.multiselect:
            ctrl = (
                "↑↓ nav • spc sel • a all • i invert • enter confirm"
                " • / search • # tag • s sort • t theme • ? help • esc quit"
            )
        else:
            ctrl = (
                "↑↓ nav • enter confirm • / search • # tag"
                " • s sort • t theme • c copy • ? help • esc quit"
            )
        output.append(ctrl + "\n\n", style=t["controls"])

        if self.clipboard_message:
            output.append(f"{self.clipboard_message}\n", style=t["success"])
        if self.selection_message:
            msg_style = t["error"] if "⚠" in self.selection_message else t["warning"]
            output.append(f"{self.selection_message}\n", style=msg_style)

        if self.is_searching:
            output.append(f"{SYMBOL_SEARCH} ", style=t["search"])
            output.append(f"search: {self.search_string}█\n", style=t["search"])
        elif self.is_tag_filtering:
            output.append(f"{SYMBOL_TAG} ", style=t["search"])
            output.append(f"tag: {self.tag_filter}█\n", style=t["search"])

        if self.search_string:
            mode = "fuzzy" if self.fuzzy else "exact"
            output.append(
                f"  [{mode}] '{self.search_string}'  [esc to clear]\n",
                style=t["description"],
            )
        if self.tag_filter:
            output.append(
                f"  [tag] #{self.tag_filter}  [esc to clear]\n",
                style=t["tag"],
            )

        filtered = self.getFilteredOptions()

        if self.scrollPosition > 0:
            output.append(
                f"{SYMBOL_UP} More options above\n", style=t["scroll_indicator"]
            )

        visible = filtered[self.scrollPosition : self.scrollPosition + self.maxVisibleOptions]

        if self.group_by:
            current_group: Optional[str] = None
            for idx, option in visible:
                if isinstance(option, Option) and option.group != current_group:
                    current_group = option.group
                    if current_group:
                        output.append(
                            f"\n{SYMBOL_EXPAND} {current_group}\n",
                            style=t["group_header"],
                        )
                output.append_text(self.formatOption(idx, option))
                output.append("\n")
        else:
            for idx, option in visible:
                output.append_text(self.formatOption(idx, option))
                output.append("\n")

        if self.scrollPosition + self.maxVisibleOptions < len(filtered):
            output.append(
                f"{SYMBOL_DOWN} More options below\n", style=t["scroll_indicator"]
            )

        if self.search_string or self.tag_filter or self.filter_fn:
            output.append(
                f"  {len(filtered)} / {len(self.options)} options\n",
                style=t["description"],
            )

        if self.multiselect:
            count = len(self.selectedIndexes)
            parts = [f"Selected: {count}"]
            if self.maxSelectionCount:
                parts.append(f"/ {self.maxSelectionCount}")
            if self.minSelectionCount:
                parts.append(f"  (min {self.minSelectionCount})")
            output.append("\n" + " ".join(parts) + "\n", style=t["counter"])

        if self.show_preview and self.preview_position == "bottom":
            pv = self.previewText()
            if pv:
                output.append("\n─── Preview ───\n", style=t["preview_border"])
                output.append_text(pv)
                output.append("\n")

        return output

    def getFilteredOptions(self) -> List[Tuple[int, OPTION_T]]:
        filtered: List[Tuple[int, OPTION_T]] = []
        fuzzy_scores: Dict[int, int] = {}

        for i, opt in enumerate(self.options):
            if self.filter_fn and not self.filter_fn(opt):
                continue

            if self.tag_filter:
                if not isinstance(opt, Option) or not any(
                    self.tag_filter.lower() in tag.lower() for tag in opt.tags
                ):
                    continue

            if self.search_string:
                if self.fuzzy and isinstance(opt, Option):
                    score = opt.fuzzy_score(self.search_string)
                    if score == 0:
                        continue
                    fuzzy_scores[i] = score
                else:
                    label = self._option_label(opt).lower()
                    if self.search_string.lower() not in label:
                        continue

            filtered.append((i, opt))

        mode = SORT_MODES[self.sort_mode_index]
        if mode == "a-z":
            filtered.sort(key=lambda x: self._option_label(x[1]).lower())
        elif mode == "z-a":
            filtered.sort(key=lambda x: self._option_label(x[1]).lower(), reverse=True)
        elif mode == "selected-first":
            filtered.sort(key=lambda x: (0 if x[0] in self.selectedIndexes else 1))
        elif self.fuzzy and self.search_string and fuzzy_scores:
            filtered.sort(key=lambda x: fuzzy_scores.get(x[0], 0), reverse=True)

        self.filtered_options = filtered

        if filtered and not any(i == self.index for i, _ in filtered):
            self.index = filtered[0][0]
            self.scrollPosition = 0

        if filtered:
            max_scroll = max(0, len(filtered) - self.maxVisibleOptions)
            self.scrollPosition = min(self.scrollPosition, max_scroll)

        return filtered
    
    def _filtered_pos(self) -> int:
        return next(
            (i for i, (idx, _) in enumerate(self.filtered_options) if idx == self.index),
            -1,
        )

    def moveDown(self) -> None:
        if not self.filtered_options:
            return
        pos = self._filtered_pos()
        if pos == -1:
            self.index = self.filtered_options[0][0]
            self.scrollPosition = 0
            return
        next_pos = (pos + 1) % len(self.filtered_options)
        self.index = self.filtered_options[next_pos][0]
        self.syncScroll(next_pos)
        if isinstance(self.options[self.index], Option) and not self.options[self.index].enabled:
            self.moveDown()

    def moveUp(self) -> None:
        if not self.filtered_options:
            return
        pos = self._filtered_pos()
        if pos == -1:
            self.index = self.filtered_options[-1][0]
            self.scrollPosition = max(0, len(self.filtered_options) - self.maxVisibleOptions)
            return
        prev_pos = (pos - 1) % len(self.filtered_options)
        self.index = self.filtered_options[prev_pos][0]
        self.syncScroll(prev_pos)
        if isinstance(self.options[self.index], Option) and not self.options[self.index].enabled:
            self.moveUp()

    def pageDown(self) -> None:
        if not self.filtered_options:
            return
        pos = self._filtered_pos()
        new_pos = min(pos + self.page_size, len(self.filtered_options) - 1)
        self.index = self.filtered_options[new_pos][0]
        self.syncScroll(new_pos)

    def pageUp(self) -> None:
        if not self.filtered_options:
            return
        pos = self._filtered_pos()
        new_pos = max(pos - self.page_size, 0)
        self.index = self.filtered_options[new_pos][0]
        self.syncScroll(new_pos)

    def jumpHome(self) -> None:
        if self.filtered_options:
            self.index = self.filtered_options[0][0]
            self.scrollPosition = 0

    def jumpEnd(self) -> None:
        if self.filtered_options:
            self.index = self.filtered_options[-1][0]
            self.scrollPosition = max(0, len(self.filtered_options) - self.maxVisibleOptions)

    def syncScroll(self, pos: int) -> None:
        if pos >= self.scrollPosition + self.maxVisibleOptions:
            self.scrollPosition = pos - self.maxVisibleOptions + 1
        elif pos < self.scrollPosition:
            self.scrollPosition = pos

    def markIndex(self) -> None:
        if not self.filtered_options or not self.multiselect:
            return
        opt = self.options[self.index]
        if isinstance(opt, Separator):
            return
        if self.index in self.selectedIndexes:
            self.selectedIndexes.remove(self.index)
            self.selection_message = ""
        else:
            if self.maxSelectionCount and len(self.selectedIndexes) >= self.maxSelectionCount:
                self.selection_message = f"⚠️ Max {self.maxSelectionCount} selections allowed"
                return
            self.selectedIndexes.append(self.index)
            self.selection_message = ""

    def selectAll(self) -> None:
        """Toggle select-all among currently *filtered* enabled options."""
        enabled_in_filter = [
            i for i, opt in self.filtered_options
            if not isinstance(opt, Option) or opt.enabled
        ]
        if self.maxSelectionCount:
            enabled_in_filter = enabled_in_filter[: self.maxSelectionCount]
        if set(self.selectedIndexes) >= set(enabled_in_filter):
            # Deselect all filtered options
            self.selectedIndexes = [
                i for i in self.selectedIndexes if i not in set(enabled_in_filter)
            ]
        else:
            # Select all filtered options (merge, respect max)
            merged = list(
                dict.fromkeys(self.selectedIndexes + enabled_in_filter)
            )
            if self.maxSelectionCount:
                merged = merged[: self.maxSelectionCount]
            self.selectedIndexes = merged

    def invertSelection(self) -> None:
        """Invert selection among currently *filtered* enabled options only.

        Previously this operated on the full options list which felt wrong when
        a search/tag filter was active — you'd suddenly have hidden items selected.
        """
        enabled_in_filter = [
            i for i, opt in self.filtered_options
            if not isinstance(opt, Option) or opt.enabled
        ]
        currently_selected_in_filter = set(self.selectedIndexes) & set(enabled_in_filter)
        not_selected_in_filter = [i for i in enabled_in_filter if i not in currently_selected_in_filter]

        # Keep selections outside the current filter unchanged, invert within filter
        outside_filter = [i for i in self.selectedIndexes if i not in set(enabled_in_filter)]
        new_selection = outside_filter + not_selected_in_filter

        if self.maxSelectionCount:
            new_selection = new_selection[: self.maxSelectionCount]

        self.selectedIndexes = new_selection

    def jumpToShortcut(self, char: str) -> bool:
        """Jump cursor to option with given shortcut.

        Returns True if a matching shortcut was found (consumed the keypress).
        """
        for i, opt in enumerate(self.options):
            if isinstance(opt, Option) and opt.shortcut == char and opt.enabled:
                self.index = i
                pos = next(
                    (p for p, (idx, _) in enumerate(self.filtered_options) if idx == i),
                    0,
                )
                self.syncScroll(pos)
                return True
        return False

    def resetFilter(self) -> None:
        self.search_string = ""
        self.tag_filter = ""
        self.scrollPosition = 0
        for i, opt in enumerate(self.options):
            if not isinstance(opt, Option) or opt.enabled:
                self.index = i
                break

    def handleSearchInput(self, key: bytes) -> None:
        if key == b"\r":
            self.is_searching = False
        elif key == b"\x1b":
            self.search_string = ""
            self.is_searching = False
        elif key in (b"\x08", b"\x7f"):
            self.search_string = self.search_string[:-1]
        else:
            try:
                self.search_string += key.decode("utf-8")
            except (UnicodeDecodeError, AttributeError):
                pass

    def handleTagInput(self, key: bytes) -> None:
        if key == b"\r":
            self.is_tag_filtering = False
        elif key == b"\x1b":
            self.tag_filter = ""
            self.is_tag_filtering = False
        elif key in (b"\x08", b"\x7f"):
            self.tag_filter = self.tag_filter[:-1]
        else:
            try:
                self.tag_filter += key.decode("utf-8")
            except (UnicodeDecodeError, AttributeError):
                pass

    def getSelected(self) -> Union[List[PICK_RETURN_T], PICK_RETURN_T]:
        if self.multiselect:
            return [(self.options[i], i) for i in self.selectedIndexes]
        return self.options[self.index], self.index

    def start(self):  # noqa: C901
        self._key_reader.flush()

        with Live(
            self.generateOutput(),
            refresh_per_second=20,
            auto_refresh=True,
        ) as live:
            while not self.shouldExit:
                live.update(self.generateOutput())

                # auto-confirm when exactly 1 match
                if (
                    self.confirm_on_single
                    and self.search_string
                    and len(self.filtered_options) == 1
                ):
                    self.index = self.filtered_options[0][0]
                    live.stop()
                    return self.getSelected()

                key = self._key_reader.getch()

                if self.is_searching:
                    self.handleSearchInput(key)
                    self.clipboard_message = ""
                    continue

                if self.is_tag_filtering:
                    self.handleTagInput(key)
                    self.clipboard_message = ""
                    continue

                self.clipboard_message = ""
                self.selection_message = ""

                if self.show_help:
                    if key in KEYS_HELP or key in KEYS_ESC:
                        self.show_help = False
                    continue

                if key in KEYS_ESC:
                    if self.search_string or self.tag_filter:
                        self.resetFilter()
                        self.selection_message = "ℹ️  Filters cleared"
                    else:
                        self.shouldExit = True
                        live.stop()
                        return None
                    continue

                if key in KEYS_UP:
                    self.moveUp()
                elif key in KEYS_DOWN:
                    self.moveDown()
                elif key in KEYS_PAGE_UP:
                    self.pageUp()
                elif key in KEYS_PAGE_DOWN:
                    self.pageDown()
                elif key in KEYS_HOME:
                    self.jumpHome()
                elif key in KEYS_END:
                    self.jumpEnd()

                elif key in KEYS_ENTER:
                    if self.multiselect:
                        if (
                            not self.allow_empty
                            and len(self.selectedIndexes) < self.minSelectionCount
                        ):
                            self.selection_message = (
                                f"⚠️ Select at least {self.minSelectionCount} option(s)"
                            )
                            continue
                    live.stop()
                    return self.getSelected()

                elif key in KEYS_SELECT and self.multiselect:
                    self.markIndex()

                elif key in KEYS_SEARCH:
                    self.is_searching = True

                elif key in KEYS_TAG:
                    self.is_tag_filtering = True

                elif key in KEYS_HELP:
                    self.show_help = True

                else:
                    try:
                        char = key.decode("utf-8")
                    except (UnicodeDecodeError, AttributeError):
                        continue

                    # Check whether any enabled option claims this shortcut
                    has_shortcut = self.show_shortcuts and _shortcut_exists(
                        self.options, char
                    )

                    if has_shortcut:
                        # Option shortcut wins — jump (and optionally select)
                        jumped = self.jumpToShortcut(char)
                        if jumped and self.jump_on_shortcut_select and self.multiselect:
                            self.markIndex()
                    else:
                        if key in KEYS_SELECT_ALL and self.multiselect:
                            if (
                                self.maxSelectionCount
                                and len(self.filtered_options) > self.maxSelectionCount
                            ):
                                self.selection_message = (
                                    f"⚠️ Max selection is {self.maxSelectionCount}"
                                )
                            else:
                                self.selectAll()

                        elif key in KEYS_INVERT and self.multiselect:
                            self.invertSelection()

                        elif key in KEYS_SORT:
                            self.sort_mode_index = (
                                self.sort_mode_index + 1
                            ) % len(SORT_MODES)

                        elif key in KEYS_THEME:
                            self.theme_index = (self.theme_index + 1) % len(THEMES)
                            set_theme(list(THEMES)[self.theme_index])

                        elif key in KEYS_COPY:
                            label = self._option_label(self.options[self.index])
                            ok = copy_to_clipboard(label)
                            self.clipboard_message = (
                                f"{SYMBOL_COPY} Copied to clipboard"
                                if ok
                                else f"{SYMBOL_COPY} Clipboard unavailable"
                            )

        return None

def Pyck(
    options: Sequence[OPTION_T],
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    indicator: str = SYMBOL_ARROW,
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
) -> Union[PickResult, List[PICK_RETURN_T], PICK_RETURN_T, None]:
    """Create and run an interactive CLI picker.

    Parameters
    ----------
    options                 : Items to display (strings or :class:`Option` objects).
    title                   : Header text.
    subtitle                : Subheader text.
    indicator               : Cursor symbol (default ``→``).
    defaultIndex            : Pre-selected cursor position.
    multiselect             : Allow multiple selections.
    minSelectionCount       : Minimum required selections (multiselect).
    maxSelectionCount       : Maximum allowed selections (multiselect).
    filter_fn               : Custom predicate to hide options programmatically.
    show_shortcuts          : Render ``[key]`` shortcut badges.
    group_by                : ``Option`` attribute name to group by (e.g. ``'group'``).
    separateValues          : Return a :class:`PickResult` instead of raw tuples.
    theme                   : Built-in theme name — ``'default'``, ``'dracula'``,
                              ``'nord'``, ``'monokai'``, ``'catppuccin'``,
                              ``'solarized'``, ``'one_dark'``, ``'gruvbox'``.
    fuzzy                   : Enable fuzzy (ranked) search (default ``True``).
    show_preview            : Display the ``Option.preview`` field in a pane.
    preview_position        : ``'bottom'`` or ``'right'``.
    show_border             : Wrap the picker in a Rich panel border.
    multiselect_indicator   : ``'circle'``, ``'check'``, ``'star'``, or ``'radio'``.
    confirm_on_single       : Auto-confirm when the search yields exactly one result.
    allow_empty             : Allow confirming with zero selections in multiselect.
    show_tags               : Render option tags inline.
    show_fuzzy_score        : Show fuzzy match score next to each option.
    max_visible             : Override auto-detected visible row count.
    page_size               : Rows scrolled per PgUp / PgDn (default: page height - 1).
    jump_on_shortcut_select : When True, pressing a shortcut in multiselect mode
                              also toggles that option's selection in addition to
                              jumping the cursor to it.

    Returns
    -------
    ``None`` on Esc, a :class:`PickResult` when ``separateValues=True``,
    otherwise a ``(value, index)`` tuple or list of tuples.
    """
    picker = Pyckify(
        options=options,
        title=title,
        subtitle=subtitle,
        indicator=indicator,
        defaultIndex=defaultIndex,
        multiselect=multiselect,
        minSelectionCount=minSelectionCount,
        maxSelectionCount=maxSelectionCount,
        filter_fn=filter_fn,
        show_shortcuts=show_shortcuts,
        group_by=group_by,
        theme=theme,
        fuzzy=fuzzy,
        show_preview=show_preview,
        preview_position=preview_position,
        show_border=show_border,
        multiselect_indicator=multiselect_indicator,
        confirm_on_single=confirm_on_single,
        allow_empty=allow_empty,
        show_tags=show_tags,
        show_fuzzy_score=show_fuzzy_score,
        max_visible=max_visible,
        page_size=page_size,
        jump_on_shortcut_select=jump_on_shortcut_select,
    )
    result = picker.start()

    if result is None:
        return None

    if separateValues:
        if isinstance(result, list):
            return PickResult(
                [item[0] for item in result],
                [item[1] for item in result],
            )
        else:
            value, index = result
            return PickResult(value, index)

    return result


__all__ = [
    "Pyck",
    "Pyckify",
    "Option",
    "Separator",
    "PickResult",
    "set_theme",
    "THEMES",
]
