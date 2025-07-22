from __future__ import annotations

from typing import Callable

from SPPCompiler.SemanticAnalysis.Utils.AstPrinter import AstPrinter


class SequenceUtils:
    @staticmethod
    def duplicates[T](seq: list[T]) -> list[T]:
        """
        Create a list of elements that are duplicates of the first element that has duplicates. For example, if the
        input is [1, 1, 2, 3, 3, 1], the output will be [1, 1, 1]. Note 3 isn't included, because 1 is the first element
        that has duplicates.

        :param seq: The sequence to check for duplicates.
        :return: The list of duplicates of the first element to have duplicates.
        """

        for elem in seq:
            if seq.count(elem) > 1:
                return [e for e in seq if e == elem]
        return []

    @staticmethod
    def remove_if[T](seq: list[T], func: Callable[[T], bool]) -> None:
        """
        Remove all elements from the sequence that match the predicate function.

        :param seq: The sequence to remove elements from.
        :param func: The predicate function to match against.
        :return: The modified sequence.
        """

        for element in seq.copy():
            if func(element):
                seq.remove(element)

    @staticmethod
    def print[T](printer: AstPrinter, seq: list[T], *, sep: str) -> str:
        output = ""
        for i, item in enumerate(seq):
            output += item.print(printer)
            if i != len(seq) - 1:
                output += sep
        return output

    @staticmethod
    def flatten[T](seq: list[list[T]]) -> list[T]:
        """
        Flatten a sequence of sequences into a single sequence.

        :param seq: The sequence of sequences to flatten.
        :return: The flattened sequence.
        """

        flat = []
        for item in seq:
            flat.extend(item) if isinstance(item, list) else flat.append(item)
        return flat
