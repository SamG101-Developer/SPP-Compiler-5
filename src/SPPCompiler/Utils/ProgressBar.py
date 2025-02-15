import math
import os
import time

import colorama

SHOW_PROGRESS_BARS = os.getenv("SHOW_PROGRESS_BARS", "1") == "1"


class ProgressBar:
    _title: str
    _max_value: int
    _current_value: int
    _current_label: str
    _characters: list[str]
    _start_time: float

    def __init__(self, title: str, max_value: int) -> None:
        self._title = title
        self._max_value = max_value
        self._current_value = 0
        self._current_label = ""
        self._character = "—"
        self._start_time = -1

    def next(self, label: str) -> None:
        if self._start_time == -1:
            self._start_time = time.time()

        self._current_value += 1
        self._current_label = label.split(os.path.sep)[-1]
        self._print()

    def _print(self) -> None:
        if not SHOW_PROGRESS_BARS:
            return

        # Calculate the percentage done, and the number of characters to print.
        percentage = self._current_value / self._max_value * 100
        bar = self._character * math.floor(percentage)

        # Create the title label, describing the progress bar.
        color = colorama.Fore.LIGHTWHITE_EX
        reset = colorama.Fore.RESET
        title = f"{color}{self._title}{reset} "

        # Create the subtext label, describing the current step, and pad it to the end of the bar.
        pad_to_label = " " * (100 - len(bar))
        if self._current_value == self._max_value:
            label = f"[{time.time() - self._start_time:.3f}s | 100.00% | ✔️]"
        else:
            label = f"{pad_to_label}[{time.time() - self._start_time:.3f}s | 0{percentage:.2f}% | {self._current_label}]"
        label = f"{color}{label}{reset}"

        # Create the colour of the progress bar depending on the percentage complete.
        color = colorama.Fore.LIGHTRED_EX if percentage < 25 else colorama.Fore.LIGHTYELLOW_EX if percentage < 75 else colorama.Fore.LIGHTGREEN_EX

        # Print the progress bar
        print(f"\r{title}{color}{bar}{reset} {label}", end="")

        # Print a newline if the progress bar is complete.
        if self._current_value == self._max_value:
            print("")
