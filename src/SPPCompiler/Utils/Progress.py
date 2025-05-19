import os
import time

import colorama

SHOW_PROGRESS_BARS = os.getenv("SHOW_PROGRESS_BARS", "1") == "1"


class Progress:
    _title: str
    _max_value: int
    _current_value: int
    _current_label: str
    _start_time: float
    _scale: float
    _bar_char: str
    _finished: bool

    def __init__(self, title: str, max_value: int) -> None:
        self._title = title.upper()
        self._max_value = max_value
        self._current_value = 0
        self._current_label = ""
        self._start_time = -1
        self._scale = 0.5
        self._bar_char = "—"
        self._finished = False

    def next(self, label: str) -> None:
        if self._start_time == -1:
            self._start_time = time.time()

        self._current_value += 1
        self._current_label = label.split(os.path.sep)[-1]
        self._print()

    def finish(self) -> None:
        self._current_value = self._max_value
        self._finished = True
        self._print()

    def set_max(self, max_value: int) -> None:
        # Set the maximum value of the progress bar.
        self._max_value = max_value

    def _print(self) -> None:
        if not SHOW_PROGRESS_BARS:
            return

        # Calculate the percentage done, and the number of characters to print.
        percentage = self._current_value / self._max_value * 100

        # Create the title label, describing the progress bar.
        color = colorama.Fore.LIGHTWHITE_EX
        reset = colorama.Fore.RESET
        title = f"{color}[{self._title}]{reset} "

        # Create the subtext label, describing the current step, and pad it to the end of the bar.
        if self._current_value == self._max_value:
            label = f"100%  ({time.time() - self._start_time:.3f}s)"
        else:
            pad_0 = " " * (3 - len(str(int(percentage))))
            label = f"{pad_0}{int(percentage)}%  ({self._current_label})"
        label = f"{color}{label}{reset}"

        # Create the colour of the progress bar depending on the percentage complete.
        color = colorama.Fore.LIGHTRED_EX if percentage < 25 else colorama.Fore.LIGHTYELLOW_EX if percentage < 75 else colorama.Fore.LIGHTGREEN_EX
        self._final_print(title, color, reset, label)

    def _final_print(self, title, color, reset, label) -> None:
        # Print the progress bar
        print(f"\r{title}{color}{reset} {label}", end="")

        # Print a newline if the progress bar is complete.
        if self._finished:
            print("")
