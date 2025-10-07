from .zen_of_python import get_zen_of_python


class Dummy:
    """Simple dummy class serving as example."""

    def __init__(self) -> None:
        self.name = "Dummy"

    def addition(self, a: int, b: int) -> int:
        """Add two integer.

        :param a: First integer.
        :param b: Second integer.
        :return: Sum of the two integers.
        """
        return a + b

    def zen(self) -> str:
        """Return The Zen of Python."""
        return get_zen_of_python()
