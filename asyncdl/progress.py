import dataclasses
import os
import sys
from typing import Any, List, Optional, TextIO


@dataclasses.dataclass
class Progress:
    value: int
    total: Optional[int] = None
    unit: Optional[str] = None
    status: Optional[str] = None

    def update(self, value: Optional[int] = None) -> None:
        if value is None:
            self.value += 1
        else:
            total = self.total or (self.value + value)
            self.value = min(self.value + value, total)

    def reset(self, value: int) -> None:
        self.value = value

    def __str__(self) -> str:
        if self.total is not None:
            if self.unit:
                maxlen = len(str(self.total))
                return f"{self.value:{maxlen}d}/{self.total} {self.unit}"
            else:
                ratio = self.value / self.total if self.total else 0.0
                percentage = f"{100 * ratio:.1f}"
                return f"{percentage:<5s} %s"
        else:
            if self.unit:
                return f"{self.value} {self.unit}"
            else:
                return f" {self.unit}"


class ProgressBar:
    def __init__(
        self,
        progress: Progress,
        title: Optional[str] = None,
        max_title_length: Optional[int] = None,
        max_bar_length: Optional[int] = None,
        max_progress_length: Optional[int] = None,
        output: Optional[TextIO] = None,
    ) -> None:
        self._title = title
        self._progress = progress
        self._max_title_length = max_title_length
        self._max_bar_length = max_bar_length
        self._max_progress_length = max_progress_length
        self._output = output or sys.stderr

    def set_properties(
        self,
        max_title_length: Optional[int] = None,
        max_progress_length: Optional[int] = None,
        output: Optional[TextIO] = None,
    ) -> None:
        self._max_title_length = max_title_length or self._max_title_length
        self._max_progress_length = max_progress_length or self._max_progress_length
        self._output = output or sys.stderr

    def get_title(self) -> str:
        title = self._title or ""
        max_title_length = self._max_title_length or len(title)
        if max_title_length < 1:
            return ""
        return f"{title:<{max_title_length}s}"

    def get_progress(self) -> str:
        progress = str(self._progress)
        max_progress_length = self._max_progress_length or len(progress)
        if max_progress_length < 1:
            return ""
        return f"{progress:>{max_progress_length}s}"

    def get_bar(self, terminal_width: int, *others: str) -> str:
        others_length = sum(len(x) for x in others)
        padding_length = len(others) + 2  # (num of others) + (num chars of bar frame)

        bar_maxlen = terminal_width - others_length - padding_length
        if bar_maxlen <= 1:
            return ""

        if self._progress.total:
            ratio = self._progress.value / self._progress.total
            bar_length = int(bar_maxlen * ratio)
            bar = f"[{'=' * bar_length:<{bar_maxlen}s}]"
        else:
            bar = ""

        max_bar_length = self._max_bar_length or len(bar)
        if max_bar_length < 1:
            return ""
        return f"{bar:<{max_bar_length}s}"

    def update(self, end: str = "\n", flush: bool = True) -> None:
        terminal_width, _ = os.get_terminal_size()

        title = self.get_title()
        progress = self.get_progress()
        bar = self.get_bar(terminal_width, title, progress)

        components = [title, bar, progress]

        self._output.write("\x1b[2K\r")  # clear line
        self._output.write(" ".join(components).strip())
        if end:
            self._output.write(end)
        if flush:
            self._output.flush()


class MultiProgressBar:
    def __init__(
        self,
        bars: List[ProgressBar],
        output: Optional[TextIO] = None,
    ) -> None:
        self._bars = bars
        self._output = output or sys.stderr
        self._with_context = False
        for bar in self._bars:
            bar.set_properties(
                max_title_length=max(len(b.get_title()) for b in bars),
                max_progress_length=max(len(b.get_progress()) for b in bars),
                output=output,
            )

    def __enter__(self) -> "MultiProgressBar":
        self._with_context = True
        self._output.write("\n" * len(self._bars))
        self._output.write("\x1b[?25l")  # hide cursor
        self._output.flush()
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self._with_context = False
        self._output.write("\x1b[?25h")  # show cursor
        self._output.flush()

    def update(self) -> None:
        if not self._with_context:
            raise RuntimeError("MultiProgressBar.update must be used in with context.")

        self._output.write(f"\x1b[{len(self._bars)}A")
        for bar in self._bars:
            bar.update(flush=False)
        self._output.flush()
